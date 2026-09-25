"""
Native PDF Text Extraction Subsystem.
Extracts detailed spans, fonts, ligatures, and layout coordinates from native PDF text streams.
Integrates directly with layout analysis and reading order engines.
"""

import unicodedata
from typing import List, Optional, Tuple
import pymupdf

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
from src.reading_order.sorter import ReadingOrderSorter


class NativeTextExtractor:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config
        self.column_detector = ColumnDetector(self.config)
        self.region_classifier = SemanticRegionClassifier(self.config)
        self.reading_sorter = ReadingOrderSorter(self.config)
        self.table_detector = TableDetector(self.config.table_min_cells)

        # Standard ligature mapping
        self.ligature_map = {
            "\ufb00": "ff",
            "\ufb01": "fi",
            "\ufb02": "fl",
            "\ufb03": "ffi",
            "\ufb04": "ffl",
            "\ufb05": "ft",
            "\ufb06": "st",
        }

    def clean_text_ligatures(self, text: str) -> str:
        """Replaces Unicode typographic ligatures and cleans control characters."""
        for lig, repl in self.ligature_map.items():
            if lig in text:
                text = text.replace(lig, repl)
        # Normalize Unicode NFC
        text = unicodedata.normalize("NFC", text)
        # Strip zero-width spaces and non-printable control chars except newlines and tabs
        text = "".join(
            ch for ch in text
            if ch in "\n\r\t" or (ord(ch) >= 32 and ch != "\u200b")
        )
        return text

    def extract_page_lines(self, page: pymupdf.Page) -> List[TextLine]:
        """Extracts structured TextLine and TextSpan objects from PyMuPDF dict output."""
        page_dict = page.get_text("dict")
        lines_out: List[TextLine] = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # 0 indicates text block
                continue

            for line_data in block.get("lines", []):
                spans_out: List[TextSpan] = []
                line_text_parts = []
                l_bbox_raw = line_data.get("bbox", (0, 0, 0, 0))
                line_bbox = BoundingBox(
                    x0=l_bbox_raw[0],
                    y0=l_bbox_raw[1],
                    x1=l_bbox_raw[2],
                    y1=l_bbox_raw[3],
                )

                for span_data in line_data.get("spans", []):
                    raw_text = span_data.get("text", "")
                    clean_span_text = self.clean_text_ligatures(raw_text)
                    if not clean_span_text.strip():
                        continue

                    s_bbox_raw = span_data.get("bbox", (0, 0, 0, 0))
                    span_bbox = BoundingBox(
                        x0=s_bbox_raw[0],
                        y0=s_bbox_raw[1],
                        x1=s_bbox_raw[2],
                        y1=s_bbox_raw[3],
                    )

                    span = TextSpan(
                        text=clean_span_text,
                        bbox=span_bbox,
                        font_name=span_data.get("font", ""),
                        font_size=span_data.get("size", 10.0),
                        flags=span_data.get("flags", 0),
                        color=span_data.get("color", 0),
                        confidence=1.0,
                    )
                    spans_out.append(span)
                    line_text_parts.append(clean_span_text)

                if spans_out:
                    full_line_text = "".join(line_text_parts)
                    lines_out.append(
                        TextLine(
                            spans=spans_out,
                            bbox=line_bbox,
                            text=full_line_text,
                            baseline_y=line_bbox.y1,
                            confidence=1.0,
                        )
                    )

        return lines_out

    def process_page(
        self,
        page: pymupdf.Page,
        page_num: int,
        is_rtl: bool = False,
    ) -> List[SemanticRegion]:
        """
        Executes complete native text processing pipeline on a page:
        1. Extract lines and spans
        2. Extract tables
        3. Layout & column analysis
        4. Semantic region classification
        5. Reading order sorting
        """
        rect = page.rect
        page_width = rect.width
        page_height = rect.height

        # 1. Extract lines
        lines = self.extract_page_lines(page)
        if not lines:
            return []

        # 2. Extract tables
        native_tables = self.table_detector.extract_native_tables(page)
        table_boxes = [t[0] for t in native_tables]

        # Filter out lines that are inside detected tables
        non_table_lines = []
        for line in lines:
            # Check if line center or significant intersection is inside any table box
            in_table = False
            for t_box in table_boxes:
                # Expand table box slightly for text margin tolerance
                pad = 4.0
                cx, cy = line.bbox.center_x, line.bbox.center_y
                if (t_box.x0 - pad <= cx <= t_box.x1 + pad) and (t_box.y0 - pad <= cy <= t_box.y1 + pad):
                    in_table = True
                    break
                if t_box.intersects(line.bbox) and (t_box.contains(line.bbox) or t_box.iou(line.bbox) > 0.15):
                    in_table = True
                    break

            if not in_table:
                non_table_lines.append(line)

        # 3. Detect column layout
        line_boxes = [line.bbox for line in non_table_lines]
        layout = self.column_detector.detect_layout(line_boxes, page_width, page_height)

        # 4. Classify semantic regions
        regions = self.region_classifier.classify_regions(
            non_table_lines, page_width, page_height, layout
        )

        # Add table regions
        for idx, (t_box, t_md) in enumerate(native_tables):
            regions.append(
                SemanticRegion(
                    region_id=f"table_{idx}",
                    region_type=RegionType.TABLE,
                    bbox=t_box,
                    confidence=0.95,
                    lines=[],
                    text=t_md,
                )
            )

        # 5. Order regions into true reading sequence
        ordered_regions = self.reading_sorter.sort_regions(
            regions=regions,
            layout=layout,
            page_width=page_width,
            page_height=page_height,
            is_rtl=is_rtl,
        )

        return ordered_regions
