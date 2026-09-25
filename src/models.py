"""
Data models and enumeration definitions for the PDF book extraction pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class PageClassification(str, Enum):
    NATIVE_TEXT = "NATIVE_TEXT"
    SCANNED_IMAGE = "SCANNED_IMAGE"
    HYBRID = "HYBRID"
    OCR_EXISTING = "OCR_EXISTING"
    LOW_QUALITY_SCAN = "LOW_QUALITY_SCAN"
    ROTATED = "ROTATED"
    COMPLEX_LAYOUT = "COMPLEX_LAYOUT"
    UNKNOWN = "UNKNOWN"


class RegionType(str, Enum):
    TITLE = "TITLE"
    HEADING = "HEADING"
    SUBHEADING = "SUBHEADING"
    PARAGRAPH = "PARAGRAPH"
    COLUMN = "COLUMN"
    HEADER = "HEADER"
    FOOTER = "FOOTER"
    FOOTNOTE = "FOOTNOTE"
    TABLE = "TABLE"
    CAPTION = "CAPTION"
    LIST = "LIST"
    IMAGE = "IMAGE"
    FORMULA = "FORMULA"
    PAGE_NUMBER = "PAGE_NUMBER"
    SIDEBAR = "SIDEBAR"
    QUOTE = "QUOTE"


class QualityStatus(str, Enum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    GOOD = "GOOD"
    REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    FAILED = "FAILED"


class ExtractionMethod(str, Enum):
    NATIVE = "NATIVE"
    OCR_RAPIDOCR = "OCR_RAPIDOCR"
    OCR_TESSERACT = "OCR_TESSERACT"
    OCR_HYBRID = "OCR_HYBRID"
    FALLBACK = "FALLBACK"
    FAILED = "FAILED"


@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    @property
    def height(self) -> float:
        return max(0.0, self.y1 - self.y0)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2.0

    def contains(self, other: "BoundingBox") -> bool:
        return (
            self.x0 <= other.x0 + 1e-4
            and self.y0 <= other.y0 + 1e-4
            and self.x1 >= other.x1 - 1e-4
            and self.y1 >= other.y1 - 1e-4
        )

    def intersects(self, other: "BoundingBox") -> bool:
        return not (
            self.x1 <= other.x0
            or self.x0 >= other.x1
            or self.y1 <= other.y0
            or self.y0 >= other.y1
        )

    def union(self, other: "BoundingBox") -> "BoundingBox":
        return BoundingBox(
            x0=min(self.x0, other.x0),
            y0=min(self.y0, other.y0),
            x1=max(self.x1, other.x1),
            y1=max(self.y1, other.y1),
        )

    def iou(self, other: "BoundingBox") -> float:
        ix0 = max(self.x0, other.x0)
        iy0 = max(self.y0, other.y0)
        ix1 = min(self.x1, other.x1)
        iy1 = min(self.y1, other.y1)
        if ix1 <= ix0 or iy1 <= iy0:
            return 0.0
        intersection = (ix1 - ix0) * (iy1 - iy0)
        union = self.area + other.area - intersection
        return intersection / union if union > 0 else 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"x0": round(self.x0, 2), "y0": round(self.y0, 2), "x1": round(self.x1, 2), "y1": round(self.y1, 2)}


@dataclass
class TextSpan:
    text: str
    bbox: BoundingBox
    font_name: str = ""
    font_size: float = 10.0
    flags: int = 0  # 1=superscript, 2=italic, 4=serifed, 8=monospaced, 16=bold
    color: int = 0
    confidence: float = 1.0


@dataclass
class TextLine:
    spans: List[TextSpan] = field(default_factory=list)
    bbox: BoundingBox = field(default_factory=lambda: BoundingBox(0, 0, 0, 0))
    text: str = ""
    baseline_y: float = 0.0
    confidence: float = 1.0


@dataclass
class TextBlock:
    bbox: BoundingBox
    lines: List[TextLine] = field(default_factory=list)
    text: str = ""
    confidence: float = 1.0


@dataclass
class SemanticRegion:
    region_id: str
    region_type: RegionType
    bbox: BoundingBox
    confidence: float = 1.0
    lines: List[TextLine] = field(default_factory=list)
    text: str = ""
    column_index: int = 0
    reading_order_idx: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "region_type": self.region_type.value,
            "bbox": self.bbox.to_dict(),
            "confidence": round(self.confidence, 3),
            "column_index": self.column_index,
            "reading_order_idx": self.reading_order_idx,
            "text_snippet": (self.text[:80] + "...") if len(self.text) > 80 else self.text,
        }


@dataclass
class PageForensics:
    page_num: int
    width_pt: float
    height_pt: float
    rotation: int
    char_count: int
    word_count: int
    image_count: int
    fonts: List[str]
    corrupt_char_ratio: float
    printable_ratio: float
    has_native_text: bool
    classification: PageClassification
    estimated_dpi: float = 72.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "width_pt": round(self.width_pt, 2),
            "height_pt": round(self.height_pt, 2),
            "rotation": self.rotation,
            "char_count": self.char_count,
            "word_count": self.word_count,
            "image_count": self.image_count,
            "fonts": self.fonts,
            "corrupt_char_ratio": round(self.corrupt_char_ratio, 4),
            "printable_ratio": round(self.printable_ratio, 4),
            "has_native_text": self.has_native_text,
            "classification": self.classification.value,
            "estimated_dpi": round(self.estimated_dpi, 1),
            "notes": self.notes,
        }


@dataclass
class QualityMetrics:
    ocr_confidence: float = 1.0
    text_density: float = 0.0
    character_validity: float = 1.0
    layout_confidence: float = 1.0
    reading_order_confidence: float = 1.0
    image_quality_score: float = 1.0
    language: str = "eng"
    language_confidence: float = 1.0

    def overall_score(self) -> float:
        # Weighted harmonic or arithmetic average of core quality metrics
        score = (
            0.35 * self.ocr_confidence
            + 0.25 * self.character_validity
            + 0.20 * self.layout_confidence
            + 0.10 * self.reading_order_confidence
            + 0.10 * self.image_quality_score
        )
        return max(0.0, min(1.0, score))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ocr_confidence": round(self.ocr_confidence, 3),
            "text_density": round(self.text_density, 3),
            "character_validity": round(self.character_validity, 3),
            "layout_confidence": round(self.layout_confidence, 3),
            "reading_order_confidence": round(self.reading_order_confidence, 3),
            "image_quality_score": round(self.image_quality_score, 3),
            "language": self.language,
            "language_confidence": round(self.language_confidence, 3),
            "overall_score": round(self.overall_score(), 3),
        }


@dataclass
class PageResult:
    page_num: int
    classification: PageClassification
    extraction_method: ExtractionMethod
    text: str
    regions: List[SemanticRegion] = field(default_factory=list)
    quality_status: QualityStatus = QualityStatus.GOOD
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    column_count: int = 1
    confidence: float = 1.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    headers_detected: List[str] = field(default_factory=list)
    footers_detected: List[str] = field(default_factory=list)
    tables_count: int = 0
    footnotes_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "classification": self.classification.value,
            "extraction_method": self.extraction_method.value,
            "quality_status": self.quality_status.value,
            "quality_metrics": self.quality_metrics.to_dict(),
            "column_count": self.column_count,
            "confidence": round(self.confidence, 3),
            "error_message": self.error_message,
            "warnings": self.warnings,
            "char_count": len(self.text),
            "regions_count": len(self.regions),
            "tables_count": self.tables_count,
            "footnotes_count": self.footnotes_count,
        }


@dataclass
class BookReport:
    book_name: str
    pdf_path: str
    total_pages: int
    native_pages: int = 0
    ocr_pages: int = 0
    hybrid_pages: int = 0
    successful_pages: int = 0
    needs_review_pages: int = 0
    failed_pages: int = 0
    high_confidence_pages: int = 0
    ocr_engines_used: List[str] = field(default_factory=list)
    layout_types: Dict[str, int] = field(default_factory=dict)
    detected_languages: Dict[str, int] = field(default_factory=dict)
    processing_time_sec: float = 0.0
    output_txt_path: str = ""
    report_json_path: str = ""
    report_html_path: str = ""
    page_status_csv_path: str = ""
    errors_json_path: str = ""
    review_pages_list: List[int] = field(default_factory=list)
    failed_pages_list: List[int] = field(default_factory=list)
    page_results: List[PageResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_name": self.book_name,
            "pdf_path": self.pdf_path,
            "total_pages": self.total_pages,
            "native_pages": self.native_pages,
            "ocr_pages": self.ocr_pages,
            "hybrid_pages": self.hybrid_pages,
            "successful_pages": self.successful_pages,
            "needs_review_pages": self.needs_review_pages,
            "failed_pages": self.failed_pages,
            "high_confidence_pages": self.high_confidence_pages,
            "ocr_engines_used": self.ocr_engines_used,
            "layout_types": self.layout_types,
            "detected_languages": self.detected_languages,
            "processing_time_sec": round(self.processing_time_sec, 2),
            "output_txt_path": self.output_txt_path,
            "report_json_path": self.report_json_path,
            "report_html_path": self.report_html_path,
            "page_status_csv_path": self.page_status_csv_path,
            "errors_json_path": self.errors_json_path,
            "review_pages_list": self.review_pages_list,
            "failed_pages_list": self.failed_pages_list,
        }
