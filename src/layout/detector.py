"""
Layout and Column Detection Subsystem.
Analyzes bounding boxes, whitespace gutters, and geometry to determine page layout structure.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

from src.config import ExtractionConfig, default_config
from src.models import BoundingBox, SemanticRegion, TextBlock, TextLine


@dataclass
class ColumnBoundary:
    col_idx: int
    x0: float
    x1: float


@dataclass
class PageLayoutInfo:
    column_count: int
    columns: List[ColumnBoundary]
    gutters: List[Tuple[float, float]]
    spanning_blocks: List[BoundingBox]
    is_complex: bool = False


class ColumnDetector:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

    def detect_layout(
        self,
        boxes: List[BoundingBox],
        page_width: float,
        page_height: float,
    ) -> PageLayoutInfo:
        """
        Determines the number of columns and column boundaries using
        horizontal occupancy projection profiles and whitespace gutters.
        """
        if not boxes or page_width <= 0:
            return PageLayoutInfo(
                column_count=1,
                columns=[ColumnBoundary(0, 0.0, max(1.0, page_width))],
                gutters=[],
                spanning_blocks=[],
            )

        # Exclude headers and footers from column gutter analysis
        margin_top = page_height * self.config.header_margin_ratio
        margin_bottom = page_height * (1.0 - self.config.footer_margin_ratio)

        body_boxes = [
            b for b in boxes
            if b.y0 >= margin_top and b.y1 <= margin_bottom and b.width > 15
        ]

        if len(body_boxes) < 4:
            # Too few boxes to reliably assert multi-column
            return PageLayoutInfo(
                column_count=1,
                columns=[ColumnBoundary(0, 0.0, page_width)],
                gutters=[],
                spanning_blocks=[],
            )

        # Identify spanning blocks (e.g. wide titles or banners that cross columns)
        spanning_boxes = []
        regular_boxes = []
        wide_threshold = page_width * 0.65

        for b in body_boxes:
            if b.width >= wide_threshold:
                spanning_boxes.append(b)
            else:
                regular_boxes.append(b)

        if len(regular_boxes) < 3:
            return PageLayoutInfo(
                column_count=1,
                columns=[ColumnBoundary(0, 0.0, page_width)],
                gutters=[],
                spanning_blocks=spanning_boxes,
            )

        # Build horizontal occupancy histogram across 200 bins
        num_bins = 200
        bin_width = page_width / num_bins
        occupancy = np.zeros(num_bins, dtype=np.float32)

        for b in regular_boxes:
            start_bin = int(max(0, min(num_bins - 1, b.x0 / bin_width)))
            end_bin = int(max(0, min(num_bins - 1, b.x1 / bin_width)))
            # Accumulate box height as weight
            occupancy[start_bin : end_bin + 1] += b.height

        # Normalize occupancy
        max_occ = np.max(occupancy)
        if max_occ > 0:
            norm_occ = occupancy / max_occ
        else:
            norm_occ = occupancy

        # Find whitespace valleys (gutters) between 15% and 85% of page width
        min_gutter_bins = max(2, int((page_width * self.config.min_column_gutter_ratio) / bin_width))
        left_bound_bin = int(0.18 * num_bins)
        right_bound_bin = int(0.82 * num_bins)

        valleys = []
        current_valley_start = None

        for i in range(left_bound_bin, right_bound_bin):
            if norm_occ[i] < 0.08:  # gutter threshold
                if current_valley_start is None:
                    current_valley_start = i
            else:
                if current_valley_start is not None:
                    gutter_len = i - current_valley_start
                    if gutter_len >= min_gutter_bins:
                        valleys.append((current_valley_start, i))
                    current_valley_start = None

        if current_valley_start is not None:
            gutter_len = right_bound_bin - current_valley_start
            if gutter_len >= min_gutter_bins:
                valleys.append((current_valley_start, right_bound_bin))

        # Check valleys: verify significant text volume on both sides
        valid_gutters = []
        for v_start, v_end in valleys:
            gutter_x0 = v_start * bin_width
            gutter_x1 = v_end * bin_width
            left_text = sum(1 for b in regular_boxes if b.x1 <= gutter_x1 + 5.0)
            right_text = sum(1 for b in regular_boxes if b.x0 >= gutter_x0 - 5.0)

            # Require at least 2 text lines/boxes on each side
            if left_text >= 2 and right_text >= 2:
                valid_gutters.append((gutter_x0, gutter_x1))

        if len(valid_gutters) == 1:
            g_x0, g_x1 = valid_gutters[0]
            col1 = ColumnBoundary(0, 0.0, (g_x0 + g_x1) / 2.0)
            col2 = ColumnBoundary(1, (g_x0 + g_x1) / 2.0, page_width)
            return PageLayoutInfo(
                column_count=2,
                columns=[col1, col2],
                gutters=valid_gutters,
                spanning_blocks=spanning_boxes,
            )
        elif len(valid_gutters) == 2:
            g1_mid = (valid_gutters[0][0] + valid_gutters[0][1]) / 2.0
            g2_mid = (valid_gutters[1][0] + valid_gutters[1][1]) / 2.0
            col1 = ColumnBoundary(0, 0.0, g1_mid)
            col2 = ColumnBoundary(1, g1_mid, g2_mid)
            col3 = ColumnBoundary(2, g2_mid, page_width)
            return PageLayoutInfo(
                column_count=3,
                columns=[col1, col2, col3],
                gutters=valid_gutters,
                spanning_blocks=spanning_boxes,
            )

        # Default to single column
        return PageLayoutInfo(
            column_count=1,
            columns=[ColumnBoundary(0, 0.0, page_width)],
            gutters=[],
            spanning_blocks=spanning_boxes,
        )

    def assign_to_column(self, box: BoundingBox, layout: PageLayoutInfo) -> int:
        """Assigns a bounding box to its respective column index."""
        if layout.column_count == 1 or not layout.columns:
            return 0

        # If box spans across columns, mark as spanning (-1)
        if any(box.intersects(s) or box.iou(s) > 0.6 for s in layout.spanning_blocks):
            return -1

        # Check center_x alignment
        cx = box.center_x
        for col in layout.columns:
            if col.x0 <= cx <= col.x1:
                return col.col_idx

        # Fallback to closest column
        min_dist = float("inf")
        best_col = 0
        for col in layout.columns:
            col_mid = (col.x0 + col.x1) / 2.0
            dist = abs(cx - col_mid)
            if dist < min_dist:
                min_dist = dist
                best_col = col.col_idx
        return best_col
