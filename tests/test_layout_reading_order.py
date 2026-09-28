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


def test_column_detector_two_columns_with_gutter_noise():
    """Scanned pages frequently have dust, fold shadows, or speckles in the central gutter."""
    detector = ColumnDetector()
    page_w = 1000.0
    page_h = 1400.0

    boxes = []
    # Left column: x = 80..460
    for y in range(150, 1100, 35):
        boxes.append(BoundingBox(80, y, 460, y + 22))

    # Right column: x = 540..920
    for y in range(150, 1100, 35):
        boxes.append(BoundingBox(540, y, 920, y + 22))

    # Scanner noise speckles in the central gutter (x = 480..520)
    speckles = [
        BoundingBox(485, 300, 515, 320),
        BoundingBox(490, 600, 510, 620),
        BoundingBox(480, 850, 520, 870),
    ]
    boxes.extend(speckles)

    layout = detector.detect_layout(boxes, page_w, page_h)
    assert layout.column_count == 2
    assert len(layout.columns) == 2


def test_conservative_ocr_heading_classification():
    """Verify that regular Persian sentences with ascenders are not falsely tagged as headings."""
    classifier = SemanticRegionClassifier()
    page_w = 1000.0
    page_h = 1400.0
    layout = ColumnDetector().detect_layout([], page_w, page_h)

    # Simulate OCR line with ascenders that makes its bbox height taller (32pt vs median 24pt)
    tall_body_line = TextLine(
        spans=[
            TextSpan(
                text="اگر سرفه همراه با مخاط باشد در آن صورت سرفه بلغم‌دار می‌باشد.",
                bbox=BoundingBox(540, 200, 920, 232),
                font_name="OCR_Generic",
                font_size=32.0 * 0.8, # ~25.6
                confidence=0.92,
            )
        ],
        bbox=BoundingBox(540, 200, 920, 232),
        text="اگر سرفه همراه با مخاط باشد در آن صورت سرفه بلغم‌دار می‌باشد.",
        baseline_y=230,
        confidence=0.92,
    )

    # Actual section title
    section_title_line = TextLine(
        spans=[
            TextSpan(
                text="اعراض معمول امراض تنفسی",
                bbox=BoundingBox(540, 150, 820, 185),
                font_name="OCR_Generic",
                font_size=35.0 * 0.8,
                confidence=0.95,
            )
        ],
        bbox=BoundingBox(540, 150, 820, 185),
        text="اعراض معمول امراض تنفسی",
        baseline_y=180,
        confidence=0.95,
    )

    regions = classifier.classify_regions([section_title_line, tall_body_line], page_w, page_h, layout)
    # The body line must NOT be a heading or title
    assert regions[1].region_type == RegionType.PARAGRAPH
    # The short section title is classified as heading
    assert regions[0].region_type in (RegionType.HEADING, RegionType.TITLE)

