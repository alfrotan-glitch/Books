"""
Reading Order Engine.
Determines the true logical reading sequence of document elements across single-column,
multi-column, spanning headers, sidebars, footnotes, and RTL/LTR languages.
"""

from typing import List, Optional
from src.config import ExtractionConfig, default_config
from src.layout.detector import PageLayoutInfo
from src.models import BoundingBox, RegionType, SemanticRegion


class ReadingOrderSorter:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

    def sort_regions(
        self,
        regions: List[SemanticRegion],
        layout: PageLayoutInfo,
        page_width: float,
        page_height: float,
        is_rtl: bool = False,
    ) -> List[SemanticRegion]:
        """
        Sorts semantic regions into strictly logical reading order.
        Handles:
        1. Top running headers & page numbers
        2. Spanning titles / headings across multiple columns
        3. Column 1 (top to bottom) -> Column 2 (top to bottom) [LTR or RTL aware]
        4. Embedded figures / tables in their logical vertical flow
        5. Sidebars
        6. Footnotes at the bottom
        7. Footers
        """
        if not regions:
            return []

        # 1. Categorize regions into structural layers
        headers: List[SemanticRegion] = []
        footers: List[SemanticRegion] = []
        footnotes: List[SemanticRegion] = []
        sidebars: List[SemanticRegion] = []
        body_regions: List[SemanticRegion] = []

        header_boundary = page_height * self.config.header_margin_ratio
        footer_boundary = page_height * (1.0 - self.config.footer_margin_ratio)

        for r in regions:
            if r.region_type in (RegionType.HEADER, RegionType.PAGE_NUMBER) and r.bbox.y1 <= header_boundary:
                headers.append(r)
            elif r.region_type in (RegionType.FOOTER, RegionType.PAGE_NUMBER) and r.bbox.y0 >= footer_boundary:
                footers.append(r)
            elif r.region_type == RegionType.FOOTNOTE:
                footnotes.append(r)
            elif r.region_type == RegionType.SIDEBAR:
                sidebars.append(r)
            else:
                body_regions.append(r)

        # Sort headers and footers by coordinates
        headers.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))
        footers.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))
        footnotes.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))

        # 2. Process Body Regions
        ordered_body: List[SemanticRegion] = []

        if layout.column_count <= 1 or not layout.columns:
            # Single Column: sort primarily by vertical y0, with small tolerance for horizontal jitter
            # Group lines that are on roughly the same horizontal band (tolerance: 4 points)
            ordered_body = self._sort_single_column(body_regions, is_rtl=is_rtl)
        else:
            # Multi-Column Layout (e.g. 2 or 3 columns)
            # Separate spanning titles/banners from column-bound content
            spanning_top: List[SemanticRegion] = []
            column_buckets: dict[int, List[SemanticRegion]] = {
                col.col_idx: [] for col in layout.columns
            }
            spanning_middle: List[SemanticRegion] = []

            spanning_width_threshold = page_width * 0.60
            top_cut_off = page_height * 0.35

            for r in body_regions:
                # Check if region is a spanning title or banner
                is_wide = r.bbox.width >= spanning_width_threshold
                is_title_heading = r.region_type in (RegionType.TITLE, RegionType.HEADING)

                if is_wide and is_title_heading and r.bbox.y0 < top_cut_off:
                    spanning_top.append(r)
                elif is_wide:
                    spanning_middle.append(r)
                else:
                    # Assign to column
                    col_idx = self._find_column_index(r.bbox, layout)
                    if col_idx in column_buckets:
                        r.column_index = col_idx
                        column_buckets[col_idx].append(r)
                    else:
                        spanning_middle.append(r)

            # Sort top spanning regions by y0
            spanning_top.sort(key=lambda r: r.bbox.y0)
            ordered_body.extend(spanning_top)

            # Determine column iteration order based on text direction (LTR vs RTL)
            # For LTR: Left column (lowest x0) -> Right column (highest x0)
            # For RTL: Right column (highest x0) -> Left column (lowest x0)
            sorted_cols = sorted(layout.columns, key=lambda c: c.x0, reverse=is_rtl)

            # Collect columns
            for col in sorted_cols:
                col_items = column_buckets.get(col.col_idx, [])
                col_sorted = self._sort_single_column(col_items, is_rtl=is_rtl)
                ordered_body.extend(col_sorted)

            # Append middle spanning blocks sorted by y0
            if spanning_middle:
                spanning_middle.sort(key=lambda r: r.bbox.y0)
                ordered_body.extend(spanning_middle)

        # 3. Assemble Complete Reading Sequence
        final_sequence: List[SemanticRegion] = []
        final_sequence.extend(headers)
        final_sequence.extend(ordered_body)
        final_sequence.extend(sidebars)
        final_sequence.extend(footnotes)
        final_sequence.extend(footers)

        # Assign 0-based reading order index to every region
        for idx, reg in enumerate(final_sequence):
            reg.reading_order_idx = idx

        return final_sequence

    def _sort_single_column(
        self, regions: List[SemanticRegion], is_rtl: bool = False
    ) -> List[SemanticRegion]:
        """
        Sorts regions in a single column:
        Groups items on nearly identical baseline (within 4 points) and sorts horizontally.
        """
        if not regions:
            return []

        # Sort with small vertical clustering tolerance
        sorted_regions = sorted(regions, key=lambda r: r.bbox.y0)
        clustered = []
        current_cluster = [sorted_regions[0]]

        for r in sorted_regions[1:]:
            prev_y0 = current_cluster[-1].bbox.y0
            if abs(r.bbox.y0 - prev_y0) <= 4.0:
                current_cluster.append(r)
            else:
                # Sort cluster horizontally
                current_cluster.sort(key=lambda x: x.bbox.x0, reverse=is_rtl)
                clustered.extend(current_cluster)
                current_cluster = [r]

        if current_cluster:
            current_cluster.sort(key=lambda x: x.bbox.x0, reverse=is_rtl)
            clustered.extend(current_cluster)

        return clustered

    def _find_column_index(self, bbox: BoundingBox, layout: PageLayoutInfo) -> int:
        """Determines which column best contains the bounding box."""
        cx = bbox.center_x
        for col in layout.columns:
            if col.x0 <= cx <= col.x1:
                return col.col_idx

        # Distance fallback
        best_col = layout.columns[0].col_idx
        min_dist = float("inf")
        for col in layout.columns:
            mid = (col.x0 + col.x1) / 2.0
            dist = abs(cx - mid)
            if dist < min_dist:
                min_dist = dist
                best_col = col.col_idx
        return best_col
