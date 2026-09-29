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
        Enforces gutter-aware and gap-aware splitting to prevent multi-column interleaving.
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
            raw_words = []
            n_boxes = len(data["text"])
            img_h, img_w = image.shape[:2]

            for i in range(n_boxes):
                word = str(data["text"][i]).strip()
                conf = float(data["conf"][i])
                if not word or conf < 0:
                    continue
                x = float(data["left"][i])
                y = float(data["top"][i])
                w = float(data["width"][i])
                h = float(data["height"][i])
                raw_words.append({
                    "word": word,
                    "conf": conf / 100.0,
                    "x0": x,
                    "y0": y,
                    "x1": x + w,
                    "y1": y + h,
                    "orig_idx": i,
                    "block": data["block_num"][i],
                    "par": data["par_num"][i],
                    "line": data["line_num"][i],
                })

            if not raw_words:
                return []

            # 1. Detect vertical gutter cutoffs from raw words across central body region
            margin_top = img_h * 0.08
            margin_bottom = img_h * 0.92
            body_words = [w for w in raw_words if margin_top <= w["y0"] and w["y1"] <= margin_bottom]

            gutter_cutoffs: List[float] = []
            if len(body_words) >= 12:
                num_bins = 200
                bin_w = float(img_w) / num_bins
                hist = np.zeros(num_bins, dtype=np.float32)
                for w in body_words:
                    b0 = int(max(0, min(num_bins - 1, w["x0"] / bin_w)))
                    b1 = int(max(0, min(num_bins - 1, w["x1"] / bin_w)))
                    hist[b0 : b1 + 1] += 1.0

                mid_start = int(0.25 * num_bins)
                mid_end = int(0.75 * num_bins)
                max_occ = float(np.max(hist)) if np.max(hist) > 0 else 1.0
                norm_occ = hist / max_occ

                v_start = None
                for b_idx in range(mid_start, mid_end):
                    if norm_occ[b_idx] < 0.10:  # Gutter whitespace threshold
                        if v_start is None:
                            v_start = b_idx
                    else:
                        if v_start is not None:
                            if (b_idx - v_start) >= 3:
                                gutter_cutoffs.append(((v_start + b_idx) / 2.0) * bin_w)
                            v_start = None
                if v_start is not None and (mid_end - v_start) >= 3:
                    gutter_cutoffs.append(((v_start + mid_end) / 2.0) * bin_w)

            # 2. Group words by line_key = (block, par, line)
            lines_dict: Dict[Tuple[int, int, int], List[Dict[str, Any]]] = {}
            for w in raw_words:
                key = (w["block"], w["par"], w["line"])
                if key not in lines_dict:
                    lines_dict[key] = []
                lines_dict[key].append(w)

            # 3. For each line, split into independent segments if separated by gutters or wide gaps
            parsed = []
            for line_key, words in lines_dict.items():
                if len(words) == 1:
                    w = words[0]
                    parsed.append({
                        "bbox": BoundingBox(x0=w["x0"], y0=w["y0"], x1=w["x1"], y1=w["y1"]),
                        "text": w["word"],
                        "confidence": w["conf"],
                    })
                    continue

                # Sort words by x0 to inspect horizontal spacing
                x_sorted = sorted(words, key=lambda item: item["x0"])
                med_h = float(np.median([item["y1"] - item["y0"] for item in x_sorted]))
                gap_threshold = max(35.0, med_h * 1.5)

                # Segmenting by gap and gutter cutoffs
                segments: List[List[Dict[str, Any]]] = []
                current_seg = [x_sorted[0]]

                for item in x_sorted[1:]:
                    prev_x1 = current_seg[-1]["x1"]
                    curr_x0 = item["x0"]
                    gap = curr_x0 - prev_x1

                    # Check if a detected gutter lies strictly between the two words
                    crosses_gutter = any(prev_x1 < g_cut < curr_x0 for g_cut in gutter_cutoffs)

                    if crosses_gutter or gap > gap_threshold:
                        segments.append(current_seg)
                        current_seg = [item]
                    else:
                        current_seg.append(item)
                segments.append(current_seg)

                # Convert each segment to a TextLine candidate
                for seg in segments:
                    # Sort words within segment by their original Tesseract index to preserve word flow
                    seg_ordered = sorted(seg, key=lambda item: item["orig_idx"])
                    seg_text = " ".join(item["word"] for item in seg_ordered)
                    seg_conf = float(np.mean([item["conf"] for item in seg]))
                    seg_x0 = min(item["x0"] for item in seg)
                    seg_y0 = min(item["y0"] for item in seg)
                    seg_x1 = max(item["x1"] for item in seg)
                    seg_y1 = max(item["y1"] for item in seg)

                    parsed.append({
                        "bbox": BoundingBox(x0=seg_x0, y0=seg_y0, x1=seg_x1, y1=seg_y1),
                        "text": seg_text,
                        "confidence": seg_conf,
                    })

            return parsed
        except Exception:
            return []

    def slice_page_into_layout_crops(
        self,
        img: np.ndarray,
        is_rtl: bool = True,
    ) -> List[Tuple[str, Tuple[int, int, int, int], int]]:
        """
        Detects horizontal bands and column gutters directly on the image.
        Returns list of (crop_type, (x0, y0, x1, y1), band_index).
        crop_type: 'col_right', 'col_left', 'spanning'
        """
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()

        # Margins for header and footer (top 6%, bottom 6%)
        m_top = int(h * 0.06)
        m_bot = int(h * 0.94)

        # Morphological binarization to detect text distribution
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Bridge text lines vertically within paragraphs
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, h // 35)))
        dilated = cv2.dilate(thresh[m_top:m_bot, :], kernel)

        h_proj = np.sum(dilated > 0, axis=1)

        raw_bands = []
        in_b = False
        start_y = 0
        min_band_h = max(25, h // 40)
        for y in range(len(h_proj)):
            if h_proj[y] > 0 and not in_b:
                in_b = True
                start_y = y
            elif h_proj[y] == 0 and in_b:
                in_b = False
                if y - start_y >= min_band_h:
                    raw_bands.append((start_y + m_top, y + m_top))
        if in_b and len(h_proj) - start_y >= min_band_h:
            raw_bands.append((start_y + m_top, len(h_proj) + m_top))

        if not raw_bands:
            raw_bands = [(m_top, m_bot)]

        crops_info = []
        has_multi_col = False
        for band_idx, (b_y0, b_y1) in enumerate(raw_bands):
            band_thresh = thresh[b_y0:b_y1, :]

            # Neutralize vertical rule lines if present so they don't mask the gutter!
            v_rule_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(25, (b_y1 - b_y0) // 2)))
            v_rules = cv2.morphologyEx(band_thresh, cv2.MORPH_OPEN, v_rule_kernel)
            band_text_only = cv2.subtract(band_thresh, v_rules)

            v_proj = np.sum(band_text_only > 0, axis=0)

            # Central zone where gutters can occur (15% to 85% of page width)
            m_left = int(0.15 * w)
            m_right = int(0.85 * w)
            max_occ = float(np.max(v_proj[m_left:m_right])) if np.max(v_proj[m_left:m_right]) > 0 else 1.0
            norm_v = v_proj / max_occ

            valleys = []
            in_v = False
            v_start = 0
            gutter_min_w = max(10, int(w * 0.015))

            for x in range(m_left, m_right):
                if norm_v[x] < 0.12 and not in_v:
                    in_v = True
                    v_start = x
                elif norm_v[x] >= 0.12 and in_v:
                    in_v = False
                    if (x - v_start) >= gutter_min_w:
                        valleys.append((v_start, x))
            if in_v and (m_right - v_start) >= gutter_min_w:
                valleys.append((v_start, m_right))

            # Also check if vertical rule lines exist in band
            v_rule_proj = np.sum(v_rules > 0, axis=0)
            mid_rules = np.where(v_rule_proj[m_left:m_right] > (b_y1 - b_y0) * 0.35)[0]
            if len(mid_rules) > 0:
                rule_x = m_left + int(np.mean(mid_rules))
                if not any(v_s <= rule_x <= v_e for v_s, v_e in valleys):
                    valleys.append((rule_x - 3, rule_x + 3))

            # Filter valid gutters: must have text on both sides
            min_col_w = int(w * 0.10)
            valid_cutoffs = []
            for v_s, v_e in valleys:
                left_text = np.sum(v_proj[m_left:v_s] > 0)
                right_text = np.sum(v_proj[v_e:m_right] > 0)
                if left_text >= min_col_w * 0.3 and right_text >= min_col_w * 0.3:
                    valid_cutoffs.append((v_s + v_e) // 2)

            if not valid_cutoffs:
                crops_info.append(("spanning", (0, b_y0, w, b_y1), band_idx))
            else:
                has_multi_col = True
                intervals = []
                curr_x = 0
                for cut in sorted(valid_cutoffs):
                    intervals.append((curr_x, cut))
                    curr_x = cut
                intervals.append((curr_x, w))

                # Order intervals by reading direction
                if is_rtl:
                    ordered = list(reversed(intervals))
                    for idx_c, (cx0, cx1) in enumerate(ordered):
                        c_type = "col_right" if idx_c == 0 else "col_left"
                        crops_info.append((c_type, (cx0, b_y0, cx1, b_y1), band_idx))
                else:
                    for idx_c, (cx0, cx1) in enumerate(intervals):
                        c_type = "col_left" if idx_c == 0 else "col_right"
                        crops_info.append((c_type, (cx0, b_y0, cx1, b_y1), band_idx))

        if has_multi_col:
            return crops_info
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
                # 1. Try Layout-Aware Physical Column Slicing on multi-column scanned pages
                crops_info = self.slice_page_into_layout_crops(proc_img, is_rtl=is_rtl)
                if crops_info:
                    sliced_blocks = []
                    for crop_type, (cx0, cy0, cx1, cy1), band_idx in crops_info:
                        sub_img = proc_img[cy0:cy1, cx0:cx1]
                        if sub_img.shape[0] < 15 or sub_img.shape[1] < 20:
                            continue
                        sub_blocks = self.run_tesseract(sub_img)
                        for b in sub_blocks:
                            b_box = b["bbox"]
                            b["bbox"] = BoundingBox(
                                x0=b_box.x0 + cx0,
                                y0=b_box.y0 + cy0,
                                x1=b_box.x1 + cx0,
                                y1=b_box.y1 + cy0,
                            )
                            b["col_idx"] = 1 if crop_type == "col_right" else 0 if crop_type == "col_left" else -1
                            b["band_idx"] = band_idx
                            sliced_blocks.append(b)

                    if sliced_blocks:
                        ocr_blocks = sliced_blocks
                        method_used = ExtractionMethod.OCR_TESSERACT
                        warnings.append("Applied physical layout band & column slicing for zero-interleaving extraction.")

                # Fallback to full-page OCR if slicing found single-column or yielded no blocks
                if not ocr_blocks:
                    ocr_blocks = self.run_tesseract(proc_img)
                    if ocr_blocks:
                        method_used = ExtractionMethod.OCR_TESSERACT
                        avg_c = float(np.mean([b["confidence"] for b in ocr_blocks]))
                        # Universal Background Invariance Retry:
                        # If confidence is low or text blocks are sparse on an image page,
                        # automatically retry with Sauvola adaptive binarization!
                        if avg_c < 0.62 or len(ocr_blocks) < 6:
                            gray_proc = cv2.cvtColor(proc_img, cv2.COLOR_RGB2GRAY)
                            sauvola_img = self.preprocessor.sauvola_threshold(gray_proc)
                            sauvola_rgb = cv2.cvtColor(sauvola_img, cv2.COLOR_GRAY2RGB)
                            retry_blocks = self.run_tesseract(sauvola_rgb)
                            if retry_blocks:
                                retry_c = float(np.mean([b["confidence"] for b in retry_blocks]))
                                if retry_c > avg_c or len(retry_blocks) > len(ocr_blocks) * 1.25:
                                    ocr_blocks = retry_blocks
                                    warnings.append("Applied Sauvola adaptive thresholding retry for difficult background.")
                    else:
                        # If initial standard image produced 0 blocks, try Sauvola adaptive binarization directly!
                        gray_proc = cv2.cvtColor(proc_img, cv2.COLOR_RGB2GRAY)
                        sauvola_img = self.preprocessor.sauvola_threshold(gray_proc)
                        sauvola_rgb = cv2.cvtColor(sauvola_img, cv2.COLOR_GRAY2RGB)
                        ocr_blocks = self.run_tesseract(sauvola_rgb)
                        if ocr_blocks:
                            method_used = ExtractionMethod.OCR_TESSERACT
                            warnings.append("Extracted text via Sauvola binarization for stained/degraded document.")
            except Exception as e:
                warnings.append(f"Tesseract error: {e}")

        # CRITICAL FAILOVER: If Tesseract produced no blocks, try RapidOCR!
        if not ocr_blocks and RAPIDOCR_AVAILABLE:
            try:
                ocr_blocks = self.run_rapidocr(proc_img)
                if ocr_blocks:
                    method_used = ExtractionMethod.OCR_RAPIDOCR
                    if is_rtl:
                        warnings.append("Engaged secondary RapidOCR fallback engine.")
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

        # Detect visual table grids in image
        try:
            table_boxes = self.table_detector.detect_table_grid_in_image(prep_res.processed_image)
        except Exception:
            table_boxes = []

        # 6. Semantic Region Classification
        regions = self.region_classifier.classify_regions(
            lines, float(w), float(h), layout, table_boxes=table_boxes
        )

        # 7. Reading Order Sorting
        ordered_regions = self.reading_sorter.sort_regions(
            regions=regions,
            layout=layout,
            page_width=float(w),
            page_height=float(h),
            is_rtl=is_rtl,
        )

        return ordered_regions, prep_res, method_used, avg_conf, warnings
