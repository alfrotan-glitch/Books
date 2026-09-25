"""
Reading Order Engine (Hardened Band-Based Slicing).
Determines the true logical reading sequence across single-column, multi-column,
spanning headers, middle section banners, sidebars, footnotes, and RTL/LTR languages.
Uses Vertical Band Slicing to guarantee middle banners never get pushed out of sequence.
"""

from typing import Dict, List, Optional
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
        Employs Vertical Band Slicing:
        1. Top running headers & page numbers
        2. Spanning elements partition the body into vertical bands
        3. Within each band: Column 1 (top to bottom) -> Column 2 (top to bottom)
        4. Sidebars placed contextually
        5. Footnotes at the bottom
        6. Footers
        """
        if not regions:
            return []

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

        # Sort headers, footers, and footnotes by geometry
        headers.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))
        footers.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))
        footnotes.sort(key=lambda r: (r.bbox.y0, r.bbox.x0))

        # 2. Process Body Regions using Vertical Band Slicing
        ordered_body: List[SemanticRegion] = []

        if layout.column_count <= 1 or not layout.columns:
            # Single-column page
            ordered_body = self._sort_single_column(body_regions, is_rtl=is_rtl)
        else:
            # Multi-column layout with potential spanning elements
            spanning_width_threshold = page_width * 0.55

            spanning_elements: List[SemanticRegion] = []
            columnar_elements: List[SemanticRegion] = []

            for r in body_regions:
                # Wide titles, headings, tables or figures spanning across columns
                is_wide = r.bbox.width >= spanning_width_threshold
                is_heading_or_table = r.region_type in (RegionType.TITLE, RegionType.HEADING, RegionType.TABLE)
                if is_wide or (is_heading_or_table and r.bbox.width >= page_width * 0.45):
                    spanning_elements.append(r)
                else:
                    columnar_elements.append(r)

            if not spanning_elements:
                # No spanning elements, single multi-column band
                ordered_body = self._sort_multicolumn_band(columnar_elements, layout, is_rtl)
            else:
                # Sort spanning elements strictly by vertical position
                spanning_elements.sort(key=lambda r: r.bbox.y0)

                # Partition into vertical slices (bands)
                # Band 0: above first spanning element
                # Band i: between spanning element i and i+1
                # Band last: below last spanning element
                current_y = 0.0

                for span in spanning_elements:
                    band_items = [
                        item for item in columnar_elements
                        if current_y <= item.bbox.center_y < span.bbox.y0
                    ]
                    if band_items:
                        ordered_body.extend(self._sort_multicolumn_band(band_items, layout, is_rtl))

                    # Append the spanning element itself
                    span.column_index = -1
                    ordered_body.append(span)
                    current_y = span.bbox.y1

                # Remaining items below the last spanning element
                trailing_items = [
                    item for item in columnar_elements
                    if item.bbox.center_y >= current_y
                ]
                if trailing_items:
                    ordered_body.extend(self._sort_multicolumn_band(trailing_items, layout, is_rtl))

        # 3. Assemble Complete Sequence
        final_sequence: List[SemanticRegion] = []
        final_sequence.extend(headers)
        final_sequence.extend(ordered_body)
        final_sequence.extend(sidebars)
        final_sequence.extend(footnotes)
        final_sequence.extend(footers)

        for idx, reg in enumerate(final_sequence):
            reg.reading_order_idx = idx

        return final_sequence

    def _sort_multicolumn_band(
        self,
        band_items: List[SemanticRegion],
        layout: PageLayoutInfo,
        is_rtl: bool,
    ) -> List[SemanticRegion]:
        """Sorts columnar items within a vertical slice/band from left to right (or right to left in RTL)."""
        if not band_items:
            return []

        column_buckets: Dict[int, List[SemanticRegion]] = {
            col.col_idx: [] for col in layout.columns
        }

        for item in band_items:
            col_idx = self._find_column_index(item.bbox, layout)
            if col_idx in column_buckets:
                item.column_index = col_idx
                column_buckets[col_idx].append(item)
            else:
                # Fallback to nearest column
                best = layout.columns[0].col_idx
                item.column_index = best
                column_buckets[best].append(item)

        ordered_band: List[SemanticRegion] = []
        # In LTR: lowest x0 (left) -> highest x0 (right)
        # In RTL: highest x0 (right) -> lowest x0 (left)
        sorted_cols = sorted(layout.columns, key=lambda c: c.x0, reverse=is_rtl)

        for col in sorted_cols:
            col_items = column_buckets.get(col.col_idx, [])
            col_sorted = self._sort_single_column(col_items, is_rtl=is_rtl)
            ordered_band.extend(col_sorted)

        return ordered_band

    def _sort_single_column(
        self, regions: List[SemanticRegion], is_rtl: bool = False
    ) -> List[SemanticRegion]:
        """
        Sorts regions in a single column:
        Groups items on nearly identical baseline (within 4 points) and sorts horizontally.
        """
        if not regions:
            return []

        sorted_regions = sorted(regions, key=lambda r: r.bbox.y0)
        clustered = []
        current_cluster = [sorted_regions[0]]

        for r in sorted_regions[1:]:
            prev_y0 = current_cluster[-1].bbox.y0
            if abs(r.bbox.y0 - prev_y0) <= 4.0:
                current_cluster.append(r)
            else:
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
