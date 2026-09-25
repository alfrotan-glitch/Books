"""
Unit tests for Fault Tolerance and No-Silent-Loss Principle (Rules 13, 20, 33).
Verifies that individual page crashes do not halt execution,
that failed pages produce visible markers, and that no silent drops occur.
"""

from pathlib import Path
import pymupdf
import pytest

from src.config import ExtractionConfig
from src.models import (
    BoundingBox,
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
    RegionType,
    SemanticRegion,
)
from src.pipeline.book_pipeline import BookPipeline
from src.reconstruction.formatter import DocumentFormatter


def test_failed_page_marker_generation():
    formatter = DocumentFormatter()

    failed_page = PageResult(
        page_num=42,
        classification=PageClassification.UNKNOWN,
        extraction_method=ExtractionMethod.FALLBACK,
        text="",
        quality_status=QualityStatus.FAILED,
        confidence=0.0,
        error_message="Decompression error in raster stream",
    )

    page_text = formatter.format_page(failed_page)
    assert "[PAGE 42 — EXTRACTION FAILED: Decompression error in raster stream]" in page_text


def test_pipeline_fault_isolation(tmp_path, monkeypatch):
    """
    Simulates a multi-page book where Page 2 raises a severe unhandled exception.
    Verifies that Page 1 and Page 3 succeed, and Page 2 is captured as FAILED.
    """
    pdf_path = tmp_path / "fault_test_book.pdf"
    doc = pymupdf.open()
    for p in range(1, 4):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 100), f"Clinical Medicine Section {p}", fontsize=14)
    doc.save(str(pdf_path))
    doc.close()

    cfg = ExtractionConfig(
        workspace_root=tmp_path,
        inbox_dir=tmp_path / "inbox",
        output_dir=tmp_path / "output",
        debug_dir=tmp_path / "debug",
        logs_dir=tmp_path / "logs",
        checkpoints_dir=tmp_path / "checkpoints",
    )
    pipeline = BookPipeline(cfg)

    # Monkeypatch _process_single_page to throw exception specifically on Page 2
    original_process = pipeline._process_single_page

    def mock_process(reader, page, page_num):
        if page_num == 2:
            raise RuntimeError("Simulated synthetic engine crash on page 2")
        return original_process(reader, page, page_num)

    monkeypatch.setattr(pipeline, "_process_single_page", mock_process)

    report = pipeline.process_pdf(pdf_path, force_reprocess=True)

    assert report.total_pages == 3
    assert report.successful_pages == 2
    assert report.failed_pages == 1
    assert 2 in report.failed_pages_list

    # Check output TXT file contains the explicit failure marker
    with open(report.output_txt_path, "r", encoding="utf-8") as f:
        out_txt = f.read()

    assert "Clinical Medicine Section 1" in out_txt
    assert "Clinical Medicine Section 3" in out_txt
    assert "[PAGE 2 — EXTRACTION FAILED: Simulated synthetic engine crash on page 2]" in out_txt
