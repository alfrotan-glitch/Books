"""
Unit tests for OCR Error Detection and High-Confidence Correction.
"""

from src.validation.ocr_cleaner import OCRErrorDetector


def test_ocr_error_detector_digit_confusion():
    detector = OCRErrorDetector(min_confidence_to_apply=0.85)
    dirty_text = "The doctor prescribed modern med1cine to the patient."
    cleaned, corrections = detector.detect_and_clean(dirty_text, page_num=1)

    assert "medicine" in cleaned
    assert "med1cine" not in cleaned
    assert len(corrections) == 1
    assert corrections[0].original == "med1cine"
    assert corrections[0].corrected == "medicine"
    assert corrections[0].applied is True


def test_ocr_error_vertical_bar():
    detector = OCRErrorDetector(min_confidence_to_apply=0.85)
    dirty_text = "The c|inical trial showed improvement."
    cleaned, corrections = detector.detect_and_clean(dirty_text, page_num=2)

    assert "clinical" in cleaned
    assert len(corrections) == 1
    assert corrections[0].applied is True


def test_no_false_corrections_on_valid_numbers():
    detector = OCRErrorDetector(min_confidence_to_apply=0.85)
    clean_text = "Patient received 500mg of dose 1 on day 2."
    cleaned, corrections = detector.detect_and_clean(clean_text, page_num=3)

    assert cleaned == clean_text
    assert len(corrections) == 0
