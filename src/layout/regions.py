"""
Semantic Region Classification.
Classifies text blocks into HEADER, FOOTER, TITLE, HEADING, PARAGRAPH,
FOOTNOTE, TABLE, CAPTION, PAGE_NUMBER, and SIDEBAR.
"""

import re
from typing import List, Optional
import numpy as np

from src.config import ExtractionConfig, default_config
from src.layout.detector import PageLayoutInfo
from src.models import BoundingBox, RegionType, SemanticRegion, TextLine


class SemanticRegionClassifier:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

        # Regex for page numbers
        self.page_num_regex = re.compile(
            r"^\s*(?:page\s+)?(?:[\-\—\–]\s*)?([0-9]{1,4}|[ivxlcdm]+)(?:\s*[\-\—\–])?\s*$",
            re.IGNORECASE,
        )

        # Regex for captions
        self.caption_regex = re.compile(
            r"^\s*(?:figure|fig\.|table|chart|graph|diagram|شکل|جدول|تصویر|نمودار)\s+[0-9\.\-]+",
            re.IGNORECASE,
        )

        # Regex for footnotes
        self.footnote_regex = re.compile(
            r"^\s*(?:\[\s*\d+\s*\]|\(\s*\d+\s*\)|\d+[\.\)]|\*+|\†|\‡)\s+[A-Z\u0600-\u06FF]",
            re.UNICODE,
        )

    def classify_regions(
        self,
        lines: List[TextLine],
        page_width: float,
        page_height: float,
        layout: PageLayoutInfo,
    ) -> List[SemanticRegion]:
        """Classify lines and group them into semantic regions."""
        if not lines:
            return []

        header_boundary = page_height * self.config.header_margin_ratio
        footer_boundary = page_height * (1.0 - self.config.footer_margin_ratio)
        footnote_top_limit = page_height * (1.0 - self.config.footnote_max_ratio_from_bottom)

        # Calculate median font size for body text reference
        font_sizes = []
        for line in lines:
            for span in line.spans:
                if span.font_size > 0:
                    font_sizes.append(span.font_size)
        median_font_size = float(np.median(font_sizes)) if font_sizes else 11.0

        regions: List[SemanticRegion] = []
        for idx, line in enumerate(lines):
            text = line.text.strip()
            if not text:
                continue

            bbox = line.bbox
            line_font_size = (
                max([s.font_size for s in line.spans], default=median_font_size)
                if line.spans
                else median_font_size
            )
            is_bold = any(bool(s.flags & 16) for s in line.spans) if line.spans else False

            # 1. Page Number check
            if self.page_num_regex.match(text) and (bbox.y1 <= header_boundary or bbox.y0 >= footer_boundary):
                regions.append(
                    SemanticRegion(
                        region_id=f"page_num_{idx}",
                        region_type=RegionType.PAGE_NUMBER,
                        bbox=bbox,
                        confidence=0.95,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 1B. Margin line numbers check (e.g. 5, 10, 15 printed along margins of reading passages)
            if (bbox.x1 <= page_width * 0.16 or bbox.x0 >= page_width * 0.88) and re.match(r"^[\·\.\s]*\d{1,3}[\s\.]*$", text):
                regions.append(
                    SemanticRegion(
                        region_id=f"margin_line_num_{idx}",
                        region_type=RegionType.PAGE_NUMBER,
                        bbox=bbox,
                        confidence=0.95,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 2. Header check (in top margin, short or distinct)
            if bbox.y1 <= header_boundary:
                regions.append(
                    SemanticRegion(
                        region_id=f"header_{idx}",
                        region_type=RegionType.HEADER,
                        bbox=bbox,
                        confidence=0.90,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 3. Footer check (in bottom margin)
            if bbox.y0 >= footer_boundary:
                regions.append(
                    SemanticRegion(
                        region_id=f"footer_{idx}",
                        region_type=RegionType.FOOTER,
                        bbox=bbox,
                        confidence=0.90,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 4. Caption check
            if self.caption_regex.match(text):
                regions.append(
                    SemanticRegion(
                        region_id=f"caption_{idx}",
                        region_type=RegionType.CAPTION,
                        bbox=bbox,
                        confidence=0.92,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 5. Footnote check (bottom portion of page, smaller font or footnote symbol)
            if bbox.y0 >= footnote_top_limit and (
                line_font_size < median_font_size * 0.90 or self.footnote_regex.match(text)
            ):
                regions.append(
                    SemanticRegion(
                        region_id=f"footnote_{idx}",
                        region_type=RegionType.FOOTNOTE,
                        bbox=bbox,
                        confidence=0.88,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 6. Title / Heading / Subheading check
            if line_font_size >= median_font_size * 1.50 or (is_bold and line_font_size >= median_font_size * 1.35):
                regions.append(
                    SemanticRegion(
                        region_id=f"title_{idx}",
                        region_type=RegionType.TITLE,
                        bbox=bbox,
                        confidence=0.92,
                        lines=[line],
                        text=text,
                    )
                )
                continue
            elif line_font_size >= median_font_size * 1.20 or (is_bold and len(text) < 70 and not text.endswith(".")):
                regions.append(
                    SemanticRegion(
                        region_id=f"heading_{idx}",
                        region_type=RegionType.HEADING,
                        bbox=bbox,
                        confidence=0.88,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 7. Sidebar check
            is_narrow = bbox.width < (page_width * 0.25)
            is_edge = (bbox.x0 < page_width * 0.15) or (bbox.x1 > page_width * 0.85)
            if is_narrow and is_edge and len(text) > 40:
                regions.append(
                    SemanticRegion(
                        region_id=f"sidebar_{idx}",
                        region_type=RegionType.SIDEBAR,
                        bbox=bbox,
                        confidence=0.75,
                        lines=[line],
                        text=text,
                    )
                )
                continue

            # 8. Standard Paragraph
            regions.append(
                SemanticRegion(
                    region_id=f"para_{idx}",
                    region_type=RegionType.PARAGRAPH,
                    bbox=bbox,
                    confidence=0.95,
                    lines=[line],
                    text=text,
                )
            )

        return regions
