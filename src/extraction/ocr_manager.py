"""
Multi-Engine OCR Architecture Subsystem.
Orchestrates RapidOCR and Tesseract, performs confidence scoring,
engine agreement analysis, and integrates with layout and reading order engines.
"""

import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
import pytesseract

try:
    from rapidocr_onnxruntime import RapidOCR
    RAPIDOCR_AVAILABLE = True
except ImportError:
    RapidOCR = None
    RAPIDOCR_AVAILABLE = False

from src.config import ExtractionConfig, default_config
from src.layout.detector import ColumnDetector
from src.layout.regions import SemanticRegionClassifier
from src.layout.tables import TableDetector
from src.models import (
    BoundingBox,
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
    RegionType,
    SemanticRegion,
    TextLine,
    TextSpan,
)
from src.preprocessing.cv_pipeline import ImagePreprocessor, PreprocessingResult
from src.reading_order.sorter import ReadingOrderSorter


class OCRManager:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config
        self.preprocessor = ImagePreprocessor(self.config)
        self.column_detector = ColumnDetector(self.config)
        self.region_classifier = SemanticRegionClassifier(self.config)
        self.reading_sorter = ReadingOrderSorter(self.config)
        self.table_detector = TableDetector(self.config.table_min_cells)

        # Initialize RapidOCR engine
        self._rapid_engine: Optional[RapidOCR] = None

        # Check Tesseract availability
        self._tesseract_available = self._check_tesseract()

    @property
    def is_ocr_available(self) -> bool:
        return bool(RAPIDOCR_AVAILABLE or self._tesseract_available)

    @property
    def rapid_engine(self) -> Optional[RapidOCR]:
        if not RAPIDOCR_AVAILABLE:
            return None
        if self._rapid_engine is None:
            self._rapid_engine = RapidOCR()
        return self._rapid_engine

    def _check_tesseract(self) -> bool:
        candidate_paths = [
            self.config.tesseract_cmd,
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe") if os.environ.get("LOCALAPPDATA") else None,
            str(Path(os.environ.get("PROGRAMFILES", "")) / "Tesseract-OCR" / "tesseract.exe") if os.environ.get("PROGRAMFILES") else None,
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]
        for p in candidate_paths:
            if p and os.path.isfile(p):
                try:
                    pytesseract.pytesseract.tesseract_cmd = str(p)
                    self.config.tesseract_cmd = str(p)
                    pytesseract.get_tesseract_version()
                    return True
                except Exception:
                    continue
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _get_tesseract_config_and_langs(self, requested_langs: Optional[str] = None) -> Tuple[str, str]:
        """
        Determines the safest, most compatible Tesseract configuration and language string.
        Guarantees that only actually existing traineddata files are requested.
        """
        target = requested_langs or self.config.tesseract_languages
        req_tokens = [t.strip() for t in target.split("+")]

        system_tessdata = None
        for candidate in [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
            "/usr/share/tesseract-ocr/5/tessdata",
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tesseract-ocr/tessdata",
        ]:
            if os.path.isdir(candidate):
                system_tessdata = Path(candidate)
                break

        local_tessdata = self.config.workspace_root / "tessdata"

        # Check if fas is in system tessdata
        if system_tessdata and (system_tessdata / "fas.traineddata").exists():
            try:
                avail = set(pytesseract.get_languages())
            except Exception:
                avail = {"fas", "eng"}
            active = [t for t in req_tokens if t in avail]
            if not active:
                active = ["fas", "eng"] if "fas" in avail and "eng" in avail else ["fas"] if "fas" in avail else ["eng"]
            return "--oem 1 --psm 3 --dpi 300", "+".join(active)

        # Check if fas is in local tessdata
        if local_tessdata.exists() and (local_tessdata / "fas.traineddata").exists():
            if system_tessdata and system_tessdata.exists():
                for needed in ["eng.traineddata", "osd.traineddata"]:
                    src = system_tessdata / needed
                    dst = local_tessdata / needed
                    if src.exists() and not dst.exists():
                        try:
                            shutil.copy2(src, dst)
                        except Exception:
                            pass

            local_avail = {f.stem for f in local_tessdata.glob("*.traineddata")}
            active = [t for t in req_tokens if t in local_avail]
            if not active:
                active = ["fas", "eng"] if "fas" in local_avail and "eng" in local_avail else ["fas"] if "fas" in local_avail else ["eng"]
            return f'--tessdata-dir "{local_tessdata}" --oem 1 --psm 3 --dpi 300', "+".join(active)

        # Fallback to system languages
        try:
            avail = set(pytesseract.get_languages())
        except Exception:
            avail = {"eng"}
        active = [t for t in req_tokens if t in avail]
        if not active:
            active = list(avail)[:2] if avail else ["eng"]
        return "--oem 1 --psm 3 --dpi 300", "+".join(active)

    def tesseract_has_language(self, lang: str = "fas") -> bool:
        if not self._tesseract_available:
            return False
        local_dir = self.config.workspace_root / "tessdata"
        if (local_dir / f"{lang}.traineddata").exists():
            return True
        for candidate in [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        ]:
            if os.path.isfile(os.path.join(candidate, f"{lang}.traineddata")):
                return True
        try:
            langs = pytesseract.get_languages()
            return lang in langs
        except Exception:
            return False

    def get_tesseract_languages(self) -> List[str]:
        if not self._tesseract_available:
            return []
        langs = set()
        local_dir = self.config.workspace_root / "tessdata"
        if local_dir.exists():
            for f in local_dir.glob("*.traineddata"):
                langs.add(f.stem)
        for candidate in [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        ]:
            p = Path(candidate)
            if p.is_dir():
                for f in p.glob("*.traineddata"):
                    langs.add(f.stem)
        try:
            for l in pytesseract.get_languages():
                langs.add(l)
        except Exception:
            pass
        return sorted(list(langs))

    def run_rapidocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs RapidOCR on an image.
        Returns a list of dicts: {"bbox": BoundingBox, "text": str, "confidence": float}
        """
        if not RAPIDOCR_AVAILABLE or self.rapid_engine is None:
            return []
        raw_results, _ = self.rapid_engine(image)
        if not raw_results:
            return []

        parsed = []
        for item in raw_results:
            quad, text, conf = item
            if not text or not str(text).strip():
                continue

            xs = [pt[0] for pt in quad]
            ys = [pt[1] for pt in quad]
            bbox = BoundingBox(
                x0=float(min(xs)),
                y0=float(min(ys)),
                x1=float(max(xs)),
                y1=float(max(ys)),
            )

            parsed.append({
                "bbox": bbox,
                "text": str(text).strip(),
                "confidence": float(conf),
            })

        return parsed

    def run_tesseract(self, image: np.ndarray, langs: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Runs Tesseract OCR if available.
        Groups words into natural coherent lines with bounding boxes and confidence.
        """
        if not self._tesseract_available:
            return []

        custom_config, active_langs = self._get_tesseract_config_and_langs(langs)

        try:
            data = pytesseract.image_to_data(
                image,
                lang=active_langs,
                config=custom_config,
                output_type=pytesseract.Output.DICT,
            )
            parsed = []
            lines_dict: Dict[Tuple[int, int, int], Dict[str, Any]] = {}
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                word = str(data["text"][i]).strip()
                conf = float(data["conf"][i])
                if not word or conf < 0:
                    continue
                line_key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
                x = float(data["left"][i])
                y = float(data["top"][i])
                w = float(data["width"][i])
                h = float(data["height"][i])

                if line_key not in lines_dict:
                    lines_dict[line_key] = {
                        "words": [word],
                        "confs": [conf / 100.0],
                        "x0": x,
                        "y0": y,
                        "x1": x + w,
                        "y1": y + h,
                    }
                else:
                    lines_dict[line_key]["words"].append(word)
                    lines_dict[line_key]["confs"].append(conf / 100.0)
                    lines_dict[line_key]["x0"] = min(lines_dict[line_key]["x0"], x)
                    lines_dict[line_key]["y0"] = min(lines_dict[line_key]["y0"], y)
                    lines_dict[line_key]["x1"] = max(lines_dict[line_key]["x1"], x + w)
                    lines_dict[line_key]["y1"] = max(lines_dict[line_key]["y1"], y + h)

            for line_info in lines_dict.values():
                line_text = " ".join(line_info["words"])
                avg_line_conf = float(np.mean(line_info["confs"])) if line_info["confs"] else 0.8
                bbox = BoundingBox(
                    x0=line_info["x0"],
                    y0=line_info["y0"],
                    x1=line_info["x1"],
                    y1=line_info["y1"],
                )
                parsed.append({
                    "bbox": bbox,
                    "text": line_text,
                    "confidence": avg_line_conf,
                })
            return parsed
        except Exception:
            return []

    def compute_agreement(self, text_a: str, text_b: str) -> float:
        """Computes word overlap agreement between two OCR engines."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a and not words_b:
            return 1.0
        if not words_a or not words_b:
            return 0.0
        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        return len(intersection) / len(union)

    def process_image(
        self,
        image: np.ndarray,
        page_num: int,
        is_rtl: bool = False,
    ) -> Tuple[List[SemanticRegion], PreprocessingResult, ExtractionMethod, float, List[str]]:
        """
        Preprocesses image and runs OCR engine with layout and reading order reconstruction.
        Guarantees automatic multi-engine failover: if primary engine produces no text,
        secondary engine is automatically engaged so no page is left empty.
        """
        warnings: List[str] = []

        # 1. Non-destructive Preprocessing
        prep_res = self.preprocessor.preprocess_for_ocr(image)
        proc_img = prep_res.processed_image
        h, w = proc_img.shape[:2]

        # 2. Multi-Engine Selection with Guaranteed Failover
        ocr_blocks: List[Dict[str, Any]] = []
        method_used = ExtractionMethod.FAILED
        tess_has_persian = self.tesseract_has_language("fas") or self.tesseract_has_language("ara")

        # Prioritize Tesseract if Persian language is needed/available
        prefer_tesseract = self._tesseract_available and (
            tess_has_persian
            or self.config.ocr_engine == "tesseract"
            or is_rtl
            or not RAPIDOCR_AVAILABLE
        )

        if prefer_tesseract:
            try:
                ocr_blocks = self.run_tesseract(proc_img)
                if ocr_blocks:
                    method_used = ExtractionMethod.OCR_TESSERACT
            except Exception as e:
                warnings.append(f"Tesseract error: {e}")

        # CRITICAL FAILOVER: If Tesseract produced no blocks, try RapidOCR!
        if not ocr_blocks and RAPIDOCR_AVAILABLE:
            try:
                ocr_blocks = self.run_rapidocr(proc_img)
                if ocr_blocks:
                    method_used = ExtractionMethod.OCR_RAPIDOCR
                    if is_rtl:
                        warnings.append("از موتور پشتیبان RapidOCR استفاده شد.")
            except Exception as e:
                warnings.append(f"RapidOCR error: {e}")

        # Secondary failover back to Tesseract if RapidOCR was attempted first and yielded nothing
        if not ocr_blocks and self._tesseract_available and not prefer_tesseract:
            try:
                ocr_blocks = self.run_tesseract(proc_img)
                if ocr_blocks:
                    method_used = ExtractionMethod.OCR_TESSERACT
            except Exception as e:
                warnings.append(f"Tesseract secondary fallback error: {e}")

        if not ocr_blocks:
            warnings.append("No text could be extracted by OCR engines.")
            return [], prep_res, method_used, 0.0, warnings

        # 3. Agreement analysis with secondary engine if hybrid mode or low confidence
        avg_conf = (
            float(np.mean([b["confidence"] for b in ocr_blocks]))
            if ocr_blocks
            else 0.0
        )

        if RAPIDOCR_AVAILABLE and self._tesseract_available and (
            self.config.ocr_engine == "hybrid" or avg_conf < self.config.min_ocr_confidence
        ):
            tess_blocks = self.run_tesseract(proc_img)
            if tess_blocks:
                tess_text = " ".join(b["text"] for b in tess_blocks)
                rapid_text = " ".join(b["text"] for b in ocr_blocks)
                agreement = self.compute_agreement(rapid_text, tess_text)

                if agreement < self.config.ocr_agreement_threshold:
                    warnings.append(
                        f"Engine agreement divergence detected (agreement={round(agreement, 2)}). Flagged for review."
                    )

                # Select best engine or merge
                tess_conf = float(np.mean([b["confidence"] for b in tess_blocks]))
                if tess_conf > avg_conf:
                    ocr_blocks = tess_blocks
                    avg_conf = tess_conf
                    method_used = ExtractionMethod.OCR_TESSERACT
                else:
                    method_used = ExtractionMethod.OCR_HYBRID

        if not ocr_blocks:
            warnings.append("No text could be extracted by OCR engines.")
            return [], prep_res, method_used, 0.0, warnings

        # 4. Convert OCR boxes into structured TextLines
        lines: List[TextLine] = []
        for b in ocr_blocks:
            span = TextSpan(
                text=b["text"],
                bbox=b["bbox"],
                font_name="OCR_Generic",
                font_size=max(8.0, b["bbox"].height * 0.8),
                confidence=b["confidence"],
            )
            line = TextLine(
                spans=[span],
                bbox=b["bbox"],
                text=b["text"],
                baseline_y=b["bbox"].y1,
                confidence=b["confidence"],
            )
            lines.append(line)

        # 5. Layout & Column Detection
        line_boxes = [l.bbox for l in lines]
        layout = self.column_detector.detect_layout(line_boxes, float(w), float(h))

        # 6. Semantic Region Classification
        regions = self.region_classifier.classify_regions(lines, float(w), float(h), layout)

        # 7. Reading Order Sorting
        ordered_regions = self.reading_sorter.sort_regions(
            regions=regions,
            layout=layout,
            page_width=float(w),
            page_height=float(h),
            is_rtl=is_rtl,
        )

        return ordered_regions, prep_res, method_used, avg_conf, warnings
