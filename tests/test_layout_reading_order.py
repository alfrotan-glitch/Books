"""
Unit tests for Column Detection, Semantic Regions, and Reading Order Engine.
"""

import pytest
from src.layout.detector import ColumnDetector
from src.layout.regions import SemanticRegionClassifier
from src.models import BoundingBox, RegionType, SemanticRegion, TextLine, TextSpan
from src.reading_order.sorter import ReadingOrderSorter


def test_column_detector_two_columns():
    detector = ColumnDetector()
    page_w = 600.0
    page_h = 800.0

    boxes = []
    # Left column: x = 50..260
    for y in range(100, 700, 40):
        boxes.append(BoundingBox(50, y, 260, y + 20))

    # Right column: x = 340..550
    for y in range(100, 700, 40):
        boxes.append(BoundingBox(340, y, 550, y + 20))

    layout = detector.detect_layout(boxes, page_w, page_h)
    assert layout.column_count == 2
    assert len(layout.columns) == 2
    assert layout.columns[0].x0 < layout.columns[1].x0


def test_reading_order_two_columns_ltr():
    sorter = ReadingOrderSorter()
    page_w = 600.0
    page_h = 800.0

    # Spanning Title at top
    title_reg = SemanticRegion(
        region_id="title",
        region_type=RegionType.TITLE,
        bbox=BoundingBox(50, 40, 550, 70),
        text="Spanning Chapter Title",
    )

    # Column 1 items (Left)
    col1_item1 = SemanticRegion(
        region_id="c1_1",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(50, 120, 260, 160),
        text="Left column top paragraph",
    )
    col1_item2 = SemanticRegion(
        region_id="c1_2",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(50, 180, 260, 220),
        text="Left column bottom paragraph",
    )

    # Column 2 items (Right)
    col2_item1 = SemanticRegion(
        region_id="c2_1",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(340, 120, 550, 160),
        text="Right column top paragraph",
    )
    col2_item2 = SemanticRegion(
        region_id="c2_2",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(340, 180, 550, 220),
        text="Right column bottom paragraph",
    )

    detector = ColumnDetector()
    all_boxes = [title_reg.bbox, col1_item1.bbox, col1_item2.bbox, col2_item1.bbox, col2_item2.bbox]
    layout = detector.detect_layout(all_boxes, page_w, page_h)

    # Pass in shuffled order
    shuffled = [col2_item1, col1_item2, title_reg, col2_item2, col1_item1]
    sorted_regs = sorter.sort_regions(shuffled, layout, page_w, page_h, is_rtl=False)

    ordered_texts = [r.text for r in sorted_regs]
    assert ordered_texts[0] == "Spanning Chapter Title"
    assert ordered_texts[1] == "Left column top paragraph"
    assert ordered_texts[2] == "Left column bottom paragraph"
    assert ordered_texts[3] == "Right column top paragraph"
    assert ordered_texts[4] == "Right column bottom paragraph"


def test_reading_order_two_columns_rtl():
    sorter = ReadingOrderSorter()
    page_w = 600.0
    page_h = 800.0

    # Column 1 in RTL should be on the RIGHT
    right_col_item = SemanticRegion(
        region_id="c_right",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(340, 120, 550, 160),
        text="متن ستون راست که باید اول خوانده شود",
    )
    left_col_item = SemanticRegion(
        region_id="c_left",
        region_type=RegionType.PARAGRAPH,
        bbox=BoundingBox(50, 120, 260, 160),
        text="متن ستون چپ که باید دوم خوانده شود",
    )

    detector = ColumnDetector()
    layout = detector.detect_layout([right_col_item.bbox, left_col_item.bbox], page_w, page_h)

    sorted_regs = sorter.sort_regions([left_col_item, right_col_item], layout, page_w, page_h, is_rtl=True)

    # In RTL, right column must be read before left column!
    assert sorted_regs[0].text == "متن ستون راست که باید اول خوانده شود"
    assert sorted_regs[1].text == "متن ستون چپ که باید دوم خوانده شود"
