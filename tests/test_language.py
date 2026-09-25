"""
Unit tests for Language Detection and RTL Direction.
"""

from src.validation.language import LanguageDetector


def test_english_detection():
    detector = LanguageDetector()
    text = "The cardiovascular examination begins with vital signs and inspection."
    profile = detector.analyze_text(text)
    assert profile.primary_language == "eng"
    assert profile.is_rtl is False
    assert profile.confidence > 0.8


def test_dari_persian_detection():
    detector = LanguageDetector()
    text = "معاینات کلینیکی مریض شامل گرفتن تاریخچه و معاینه فیزیکی دقیق است."
    profile = detector.analyze_text(text)
    assert profile.primary_language == "fas"
    assert profile.is_rtl is True
    assert profile.confidence > 0.7


def test_pashto_detection():
    detector = LanguageDetector()
    text = "د ناروغ د روغتیا او درملنې لپاره دقیق معاینات ترسره شول."
    profile = detector.analyze_text(text)
    assert profile.primary_language in ("pus", "fas")
    assert profile.is_rtl is True
