"""
Unit tests for PDF Forensics and Page Classification.
"""

from pathlib import Path
import pymupdf
import pytest

from src.config import ExtractionConfig
from src.models import PageClassification
from src.pdf.forensics import PDFForensicsEngine


def test_native_page_forensics(tmp_path):
    pdf_path = tmp_path / "native.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "Chapter 1: The Circulatory System", fontsize=16)
    page.insert_text((50, 140), "Blood flows through arteries and veins across organs.", fontsize=11)
    doc.save(str(pdf_path))
    doc.close()

    engine = PDFForensicsEngine()
    doc_in = pymupdf.open(str(pdf_path))
    p_info = engine.analyze_page(doc_in[0], 1)

    assert p_info.has_native_text is True
    assert p_info.char_count > 30
    assert p_info.classification in (PageClassification.NATIVE_TEXT, PageClassification.COMPLEX_LAYOUT)
    assert p_info.corrupt_char_ratio < 0.05
    doc_in.close()


def test_scanned_image_forensics(tmp_path):
    import cv2
    import numpy as np

    pdf_path = tmp_path / "scanned.pdf"
    img = np.ones((600, 400, 3), dtype=np.uint8) * 200
    _, buf = cv2.imencode(".png", img)

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=buf.tobytes())
    doc.save(str(pdf_path))
    doc.close()

    engine = PDFForensicsEngine()
    doc_in = pymupdf.open(str(pdf_path))
    p_info = engine.analyze_page(doc_in[0], 1)

    assert p_info.has_native_text is False
    assert p_info.classification in (PageClassification.SCANNED_IMAGE, PageClassification.LOW_QUALITY_SCAN)
    assert p_info.image_count == 1
    doc_in.close()


def test_rotated_page_forensics(tmp_path):
    pdf_path = tmp_path / "rotated.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((100, 100), "Rotated Page Test", fontsize=12)
    page.set_rotation(90)
    doc.save(str(pdf_path))
    doc.close()

    engine = PDFForensicsEngine()
    doc_in = pymupdf.open(str(pdf_path))
    p_info = engine.analyze_page(doc_in[0], 1)

    assert p_info.rotation == 90
    assert p_info.classification == PageClassification.ROTATED
    doc_in.close()
