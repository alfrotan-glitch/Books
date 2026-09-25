"""
Unit tests for Table and Footnote handling.
"""

import pymupdf
import pytest
from src.layout.tables import TableDetector


def test_table_detector_with_lines(tmp_path):
    pdf_path = tmp_path / "table_test.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)

    # Draw table outline
    page.draw_rect(pymupdf.Rect(50, 100, 450, 200), color=(0, 0, 0), width=1)
    page.draw_line(pymupdf.Point(50, 140), pymupdf.Point(450, 140), color=(0, 0, 0), width=1)
    page.draw_line(pymupdf.Point(250, 100), pymupdf.Point(250, 200), color=(0, 0, 0), width=1)

    page.insert_text((60, 125), "Header 1", fontsize=11)
    page.insert_text((260, 125), "Header 2", fontsize=11)
    page.insert_text((60, 175), "Val 1", fontsize=11)
    page.insert_text((260, 175), "Val 2", fontsize=11)

    doc.save(str(pdf_path))
    doc.close()

    detector = TableDetector()
    doc_in = pymupdf.open(str(pdf_path))
    tables = detector.extract_native_tables(doc_in[0])
    doc_in.close()

    assert len(tables) >= 1
    bbox, md = tables[0]
    assert "|" in md
    assert "Header 1" in md
    assert "Val 1" in md
