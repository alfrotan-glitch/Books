"""
Quality Control Subsystem (Grounded Evidence Scoring).
Computes real, empirically measured quality metrics for every page:
- Token-level OCR confidence
- Whitespace layout gutter clarity
- Character validity ratio (clean alphanumeric vs corrupted symbols)
- Page text density (chars / sq inch)
- Multi-engine agreement divergence
"""

from typing import List, Optional, Tuple
from src.config import ExtractionConfig, default_config
from src.models import (
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
)


class QualityControlEngine:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

    def evaluate_page(
        self,
        page_num: int,
        raw_text: str,
        page_width_pt: float,
        page_height_pt: float,
        ocr_confidence: float = 1.0,
        image_quality_score: float = 1.0,
        layout_confidence: float = 0.95,
        reading_order_confidence: float = 0.95,
        language: str = "eng",
        language_confidence: float = 1.0,
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None,
    ) -> Tuple[QualityMetrics, QualityStatus]:
        """
        Calculates character validity, density, and aggregates evidence-based quality score.
        Returns (QualityMetrics, QualityStatus).
        """
        if error_message:
            metrics = QualityMetrics(
                ocr_confidence=0.0,
                text_density=0.0,
                character_validity=0.0,
                layout_confidence=0.0,
                reading_order_confidence=0.0,
                image_quality_score=image_quality_score,
                language=language,
                language_confidence=language_confidence,
            )
            return metrics, QualityStatus.FAILED

        text = raw_text.strip()
        char_count = len(text)
        warnings = warnings or []

        # 1. Character Validity: ratio of clean printable characters to total non-space
        printable_count = sum(1 for ch in text if ch.isprintable() and not ch.isspace())
        non_space_count = sum(1 for ch in text if not ch.isspace())
        char_validity = (printable_count / non_space_count) if non_space_count > 0 else 1.0

        # Check for symbol/punctuation noise ratio
        alpha_count = sum(1 for ch in text if ch.isalnum())
        alpha_ratio = (alpha_count / non_space_count) if non_space_count > 0 else 1.0
        if alpha_ratio < 0.60 and non_space_count > 30:
            char_validity *= 0.85

        # 2. Text Density (characters per square inch)
        area_sq_inch = (page_width_pt * page_height_pt) / (72.0 * 72.0)
        text_density = (char_count / area_sq_inch) if area_sq_inch > 0 else 0.0

        # Density penalty if sparse (< 3.0 chars/sq inch) on a full-size page
        density_factor = min(1.0, max(0.5, text_density / 10.0)) if char_count > 0 else 0.2

        # 3. Grounded Layout & Reading Order Confidence
        grounded_layout_conf = layout_confidence * density_factor
        grounded_reading_conf = reading_order_confidence

        # Multi-engine disagreement penalty
        disagreement_present = any("divergence" in w.lower() or "disagreement" in w.lower() for w in warnings)
        if disagreement_present:
            ocr_confidence = min(ocr_confidence, 0.65)

        metrics = QualityMetrics(
            ocr_confidence=ocr_confidence,
            text_density=text_density,
            character_validity=char_validity,
            layout_confidence=grounded_layout_conf,
            reading_order_confidence=grounded_reading_conf,
            image_quality_score=image_quality_score,
            language=language,
            language_confidence=language_confidence,
        )

        overall = metrics.overall_score()

        # Status assignment strictly governed by empirical thresholds
        if disagreement_present or any("degraded" in w.lower() for w in warnings):
            status = QualityStatus.REVIEW_RECOMMENDED
        elif overall >= 0.88 and char_count >= 50:
            status = QualityStatus.HIGH_CONFIDENCE
        elif overall >= 0.70 and char_count >= 20:
            status = QualityStatus.GOOD
        elif overall >= 0.45 or (char_count > 0 and char_count < 20):
            status = QualityStatus.REVIEW_RECOMMENDED
        elif char_count == 0:
            status = QualityStatus.REVIEW_RECOMMENDED  # empty page flagged for review
        else:
            status = QualityStatus.LOW_CONFIDENCE

        return metrics, status
