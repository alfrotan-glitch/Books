"""
Unit tests for Cross-Page Verification and Anomaly Detection.
"""

from src.models import (
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
)
from src.validation.verifier import CrossPageVerifier


def test_missing_page_anomaly():
    verifier = CrossPageVerifier()

    # Total expected: 3 pages, but page 2 is missing
    pr1 = PageResult(page_num=1, classification=PageClassification.NATIVE_TEXT, extraction_method=ExtractionMethod.NATIVE, text="Page 1 text " * 10)
    pr3 = PageResult(page_num=3, classification=PageClassification.NATIVE_TEXT, extraction_method=ExtractionMethod.NATIVE, text="Page 3 text " * 10)

    summary = verifier.verify_document(3, [pr1, pr3])
    assert summary.is_valid is False
    assert 2 in summary.missing_pages
    assert any(a.anomaly_type == "MISSING_PAGE" and a.page_num == 2 for a in summary.anomalies)


def test_density_drop_anomaly():
    verifier = CrossPageVerifier()

    # Page 2 has only 5 chars while pages 1 and 3 have 500 chars
    pr1 = PageResult(page_num=1, classification=PageClassification.NATIVE_TEXT, extraction_method=ExtractionMethod.NATIVE, text="Standard text content. " * 30)
    pr2 = PageResult(page_num=2, classification=PageClassification.NATIVE_TEXT, extraction_method=ExtractionMethod.NATIVE, text="Tiny.")
    pr3 = PageResult(page_num=3, classification=PageClassification.NATIVE_TEXT, extraction_method=ExtractionMethod.NATIVE, text="Standard text content. " * 30)

    summary = verifier.verify_document(3, [pr1, pr2, pr3])
    assert any(a.anomaly_type == "DENSITY_DROP" and a.page_num == 2 for a in summary.anomalies)
