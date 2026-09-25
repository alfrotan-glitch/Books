"""
Unit tests for SQLite Resumable Checkpoint Manager.
"""

from pathlib import Path
from src.models import (
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
)
from src.pipeline.checkpoint import CheckpointManager


def test_checkpoint_save_and_retrieve(tmp_path):
    mgr = CheckpointManager(tmp_path, "test_book")

    pr1 = PageResult(
        page_num=1,
        classification=PageClassification.NATIVE_TEXT,
        extraction_method=ExtractionMethod.NATIVE,
        text="Sample page 1 text",
        quality_status=QualityStatus.HIGH_CONFIDENCE,
        confidence=0.98,
    )
    pr2 = PageResult(
        page_num=2,
        classification=PageClassification.SCANNED_IMAGE,
        extraction_method=ExtractionMethod.OCR_RAPIDOCR,
        text="Sample page 2 OCR text",
        quality_status=QualityStatus.GOOD,
        confidence=0.88,
    )

    mgr.save_page(pr1)
    mgr.save_page(pr2)

    completed = mgr.get_completed_pages()
    assert 1 in completed
    assert 2 in completed

    results = mgr.get_all_results()
    assert len(results) == 2
    assert results[0].page_num == 1
    assert results[0].text == "Sample page 1 text"
    assert results[1].page_num == 2
    assert results[1].text == "Sample page 2 OCR text"


def test_checkpoint_isolation_on_failure(tmp_path):
    mgr = CheckpointManager(tmp_path, "test_fail_book")

    pr_failed = PageResult(
        page_num=3,
        classification=PageClassification.UNKNOWN,
        extraction_method=ExtractionMethod.FALLBACK,
        text="",
        quality_status=QualityStatus.FAILED,
        confidence=0.0,
        error_message="Corrupted image stream",
    )
    mgr.save_page(pr_failed)

    # Failed pages should NOT be considered completed for resume
    completed = mgr.get_completed_pages()
    assert 3 not in completed
