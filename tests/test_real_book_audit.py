"""
Independent Quality Audit & Real-Book Validation Test Suite.
Verifies real-world extraction, degraded OCR detection, vertical band reading order,
conservative OCR error cleaning, strict dehyphenation, and complete page provenance.
"""

from pathlib import Path
import pymupdf
import pytest

from src.config import ExtractionConfig
from src.layout.detector import ColumnDetector
from src.models import (
    BoundingBox,
    ExtractionMethod,
    PageClassification,
    QualityStatus,
    RegionType,
    SemanticRegion,
)
from src.pdf.forensics import PDFForensicsEngine
from src.pdf.reader import PDFReader
from src.pipeline.book_pipeline import BookPipeline
from src.pipeline.provenance import ProvenanceAuditor
from src.reading_order.sorter import ReadingOrderSorter
from src.reconstruction.paragraphs import ParagraphReconstructor
from src.validation.language import LanguageDetector
from src.validation.ocr_cleaner import OCRErrorDetector


def test_real_book_forensic_audit():
    """Audits forensics on the real textbook: Active_Skills_for_Reading_2."""
    real_pdf = Path("Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf")
    if not real_pdf.exists():
        pytest.skip("Real PDF not found in repository root")

    engine = PDFForensicsEngine()
    with PDFReader(real_pdf) as reader:
        assert reader.page_count == 179

        # Page 1: Cover image
        p1 = reader.get_page(1)
        f1 = engine.analyze_page(p1, 1)
        assert f1.has_native_text is False
        assert f1.classification in (PageClassification.SCANNED_IMAGE, PageClassification.LOW_QUALITY_SCAN)

        # Page 2: Native text intro
        p2 = reader.get_page(2)
        f2 = engine.analyze_page(p2, 2)
        assert f2.has_native_text is True
        assert f2.char_count > 2000

        # Page 18: Degraded OCR layer with accented corruption (Àethods, cÁntinue)
        p18 = reader.get_page(18)
        f18 = engine.analyze_page(p18, 18)
        # Must be flagged as OCR_EXISTING with degraded note, and NOT trusted as clean native text!
        assert f18.classification == PageClassification.OCR_EXISTING
        assert f18.has_native_text is False
        assert any("degraded" in n.lower() or "corrupted" in n.lower() for n in f18.notes)


def test_vertical_band_reading_order_with_middle_banner():
    """
    Validates that middle section banners are placed between bands,
    NOT pushed to the very end of the page!
    """
    sorter = ReadingOrderSorter()
    page_w = 600.0
    page_h = 800.0

    # Layout structure:
    # 1. Top Spanning Title (y: 40-70)
    title = SemanticRegion("title", RegionType.TITLE, BoundingBox(50, 40, 550, 70), text="Chapter 3: Cardiology")

    # 2. Band 1: Two Columns (y: 100-300)
    b1_c1 = SemanticRegion("b1_c1", RegionType.PARAGRAPH, BoundingBox(50, 100, 260, 280), text="Band 1 Left Column Text")
    b1_c2 = SemanticRegion("b1_c2", RegionType.PARAGRAPH, BoundingBox(340, 100, 550, 280), text="Band 1 Right Column Text")

    # 3. Middle Spanning Banner (y: 340-380)
    mid_banner = SemanticRegion("mid_banner", RegionType.HEADING, BoundingBox(50, 340, 550, 380), text="SECTION B: CLINICAL PROTOCOLS")

    # 4. Band 2: Two Columns (y: 400-650)
    b2_c1 = SemanticRegion("b2_c1", RegionType.PARAGRAPH, BoundingBox(50, 400, 260, 640), text="Band 2 Left Column Text")
    b2_c2 = SemanticRegion("b2_c2", RegionType.PARAGRAPH, BoundingBox(340, 400, 550, 640), text="Band 2 Right Column Text")

    # 5. Bottom Footnote (y: 720-750)
    fn = SemanticRegion("fn", RegionType.FOOTNOTE, BoundingBox(50, 720, 550, 750), text="[1] Reference note details.")

    detector = ColumnDetector()
    all_boxes = [title.bbox, b1_c1.bbox, b1_c2.bbox, mid_banner.bbox, b2_c1.bbox, b2_c2.bbox, fn.bbox]
    layout = detector.detect_layout(all_boxes, page_w, page_h)

    shuffled = [b2_c2, fn, b1_c2, mid_banner, title, b1_c1, b2_c1]
    sorted_regs = sorter.sort_regions(shuffled, layout, page_w, page_h, is_rtl=False)
    ordered_texts = [r.text for r in sorted_regs]

    # Verify exact sequential band order:
    assert ordered_texts[0] == "Chapter 3: Cardiology"
    assert ordered_texts[1] == "Band 1 Left Column Text"
    assert ordered_texts[2] == "Band 1 Right Column Text"
    assert ordered_texts[3] == "SECTION B: CLINICAL PROTOCOLS"  # MUST be in the middle!
    assert ordered_texts[4] == "Band 2 Left Column Text"
    assert ordered_texts[5] == "Band 2 Right Column Text"
    assert ordered_texts[6] == "[1] Reference note details."


def test_strict_dehyphenation_accuracy():
    """
    Verifies that authentic hyphenated compounds are preserved,
    while broken line wraps are merged.
    """
    pr = ParagraphReconstructor(dehyphenate=True, preserve_true_hyphens=True)

    # Broken line wraps -> must dehyphenate
    assert pr.is_line_break_hyphen("infor-", "mation") is True
    assert pr.is_line_break_hyphen("adminis-", "tration") is True
    assert pr.is_line_break_hyphen("circu-", "lation") is True
    assert pr.is_line_break_hyphen("physi-", "ology") is True

    # Authentic hyphenated compounds -> MUST preserve hyphen
    assert pr.is_line_break_hyphen("well-", "known") is False
    assert pr.is_line_break_hyphen("evidence-", "based") is False
    assert pr.is_line_break_hyphen("peer-", "reviewed") is False
    assert pr.is_line_break_hyphen("decision-", "making") is False
    assert pr.is_line_break_hyphen("high-", "risk") is False
    assert pr.is_line_break_hyphen("follow-", "up") is False
    assert pr.is_line_break_hyphen("first-", "line") is False
    assert pr.is_line_break_hyphen("cost-", "effective") is False


def test_conservative_ocr_cleaner_audit():
    """
    Verifies that OCR error cleaner is strictly conservative:
    Only verified dictionary matches are replaced; scientific/unverified are preserved.
    """
    cleaner = OCRErrorDetector(min_confidence_to_apply=0.90)

    # 1. Verified dictionary match -> clean with high confidence
    txt1, corr1 = cleaner.detect_and_clean("The hospital provided modern med1cine.", page_num=1)
    assert "medicine" in txt1
    assert len(corr1) == 1
    assert corr1[0].applied is True

    # 2. Scientific identifiers -> MUST NOT be altered
    txt2, corr2 = cleaner.detect_and_clean("Patient tested positive for COVID19 and took vitamin B12.", page_num=2)
    assert "COVID19" in txt2
    assert "B12" in txt2

    # 3. Arbitrary/unverified token -> MUST preserve original text
    txt3, corr3 = cleaner.detect_and_clean("System recorded code ab1cd in the database.", page_num=3)
    assert "ab1cd" in txt3  # NOT changed to abicd or ablcd!
    assert len(corr3) == 1
    assert corr3[0].applied is False


def test_real_dari_persian_manuscript_validation():
    """Validates language and RTL processing on the real Dari Manuscript."""
    manuscript_file = Path("Manuscript")
    if not manuscript_file.exists():
        pytest.skip("Manuscript file not found")

    with open(manuscript_file, "r", encoding="utf-8") as f:
        content = f.read(2000)

    detector = LanguageDetector()
    prof = detector.analyze_text(content)

    assert prof.is_rtl is True
    assert prof.primary_language in ("fas", "pus", "ara")
    assert prof.confidence > 0.80
    assert prof.script_distribution["arabic"] > 0.90


def test_page_provenance_and_completeness_audit(tmp_path):
    """
    Validates that ProvenanceAuditor creates a complete, zero-loss mathematical audit manifest.
    """
    pdf_path = tmp_path / "provenance_test.pdf"
    doc = pymupdf.open()
    for p in range(1, 4):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 100), f"Clinical Medicine Section {p}", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()

    cfg = ExtractionConfig(
        workspace_root=tmp_path,
        inbox_dir=tmp_path / "inbox",
        output_dir=tmp_path / "output",
        checkpoints_dir=tmp_path / "checkpoints",
    )
    pipeline = BookPipeline(cfg)
    report = pipeline.process_pdf(pdf_path, force_reprocess=True)

    provenance_file = tmp_path / "output" / f"{pdf_path.stem}_provenance.json"
    assert provenance_file.exists()

    import json
    with open(provenance_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    audit = data["completeness_audit"]
    assert audit["total_pages_input"] == 3
    assert audit["total_pages_processed"] == 3
    assert audit["is_complete_zero_loss"] is True
    assert len(audit["missing_pages"]) == 0
    assert len(data["pages"]) == 3
    assert data["pages"][0]["text_sha256"] != ""
