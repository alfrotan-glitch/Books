"""
Multi-Engine OCR Architecture Subsystem.
Orchestrates RapidOCR and Tesseract, performs confidence scoring,
engine agreement analysis, and integrates with layout and reading order engines.
"""

import shutil
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
import pytesseract
from rapidocr_onnxruntime import RapidOCR

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
    def rapid_engine(self) -> RapidOCR:
        if self._rapid_engine is None:
            self._rapid_engine = RapidOCR()
        return self._rapid_engine

    def _check_tesseract(self) -> bool:
        if self.config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd
        return bool(shutil.which("tesseract") or shutil.which(pytesseract.pytesseract.tesseract_cmd))

    def run_rapidocr(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs RapidOCR on an image.
        Returns a list of dicts: {"bbox": BoundingBox, "text": str, "confidence": float}
        """
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

    def run_tesseract(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs Tesseract OCR if available.
        Returns word/line-level bounding boxes and confidence.
        """
        if not self._tesseract_available:
            return []

        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.config.tesseract_languages,
                output_type=pytesseract.Output.DICT,
            )
            parsed = []
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf = float(data["conf"][i])
                if text and conf > 0:
                    x = float(data["left"][i])
                    y = float(data["top"][i])
                    w = float(data["width"][i])
                    h = float(data["height"][i])
                    bbox = BoundingBox(x0=x, y0=y, x1=x + w, y1=y + h)
                    parsed.append({
                        "bbox": bbox,
                        "text": text,
                        "confidence": conf / 100.0,
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
        """
        warnings: List[str] = []

        # 1. Non-destructive Preprocessing
        prep_res = self.preprocessor.preprocess_for_ocr(image)
        proc_img = prep_res.processed_image
        h, w = proc_img.shape[:2]

        # 2. Run Primary Engine (RapidOCR)
        ocr_blocks = self.run_rapidocr(proc_img)
        method_used = ExtractionMethod.OCR_RAPIDOCR

        # 3. Agreement analysis with secondary engine if hybrid mode or low confidence
        avg_conf = (
            float(np.mean([b["confidence"] for b in ocr_blocks]))
            if ocr_blocks
            else 0.0
        )

        if self._tesseract_available and (
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
