"""
Quality Control Subsystem.
Computes comprehensive quality metrics for every page and assigns overall extraction status.
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
        Calculates character validity, density, and aggregates quality score.
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

        # 1. Character Validity
        printable_count = sum(1 for ch in text if ch.isprintable() and not ch.isspace())
        non_space_count = sum(1 for ch in text if not ch.isspace())
        char_validity = (printable_count / non_space_count) if non_space_count > 0 else 1.0

        # 2. Text Density (characters per square inch)
        area_sq_inch = (page_width_pt * page_height_pt) / (72.0 * 72.0)
        text_density = (char_count / area_sq_inch) if area_sq_inch > 0 else 0.0

        metrics = QualityMetrics(
            ocr_confidence=ocr_confidence,
            text_density=text_density,
            character_validity=char_validity,
            layout_confidence=layout_confidence,
            reading_order_confidence=reading_order_confidence,
            image_quality_score=image_quality_score,
            language=language,
            language_confidence=language_confidence,
        )

        overall = metrics.overall_score()

        # Determine status
        if warnings and len(warnings) > 0 and overall < 0.80:
            status = QualityStatus.REVIEW_RECOMMENDED
        elif overall >= 0.88 and char_count > 20:
            status = QualityStatus.HIGH_CONFIDENCE
        elif overall >= 0.72 and char_count > 10:
            status = QualityStatus.GOOD
        elif overall >= 0.45:
            status = QualityStatus.REVIEW_RECOMMENDED
        else:
            status = QualityStatus.LOW_CONFIDENCE

        return metrics, status
