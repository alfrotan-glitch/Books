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


def test_medical_terminology_corrections():
    detector = OCRErrorDetector(min_confidence_to_apply=0.85)
    dirty_medical = "غسرث نفس همراه با إکس حری صدری و پاوریزی و نومونورگس و قیخی بلغم"
    cleaned, corrections = detector.detect_and_clean(dirty_medical, page_num=4)

    assert "عسرت تنفس" in cleaned
    assert "اکسری صدر" in cleaned
    assert "پلوریزی" in cleaned
    assert "نوموتوراکس" in cleaned
    assert "قیحی" in cleaned
    assert len(corrections) >= 5


def test_unintelligible_smudge_rejection():
    detector = OCRErrorDetector()
    assert detector.is_unintelligible_smudge("بیذ مت کد اج") is True
    assert detector.is_unintelligible_smudge("gs ۳3 نی اکن قر") is True
    assert detector.is_unintelligible_smudge("ae") is True
    assert detector.is_unintelligible_smudge("oe]") is True
    assert detector.is_unintelligible_smudge("بیوپسی پلورا با سوزن بیوپسی پلورای Abrams انجام می‌شود") is False
    assert detector.is_unintelligible_smudge("AP View PA") is False
    assert detector.is_unintelligible_smudge("سایه قلب بزرگتر معلوم می‌شود.") is False


def test_latin_hallucinations_purging():
    detector = OCRErrorDetector()
    corrupted_line = (
        "pe وی اسکن انداژه و cays یک توئول Wis) spy MS را لنتکه Ul درآ تکلس ا "
        "spss lal است Ghats! yp قد ۵ مسر نی ادن dows بندی کارسینومای برانشیل و برای نشان"
    )
    cleaned, _ = detector.detect_and_clean(corrupted_line, page_num=2)

    # Hallucinated junk must be purged
    for junk in ["pe", "cays", "Wis", "spy", "MS", "Ul", "spss", "lal", "Ghats", "yp", "dows"]:
        assert junk not in cleaned

    # Valid Persian text and corrections must remain intact
    assert "اندازه" in cleaned
    assert "نودول" in cleaned
    assert "سی تی اسکن" in cleaned

