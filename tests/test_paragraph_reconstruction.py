"""
Unit tests for Paragraph Reconstruction and Hyphenation.
"""

from src.reconstruction.paragraphs import ParagraphReconstructor


def test_merge_lines_into_paragraph():
    pr = ParagraphReconstructor()
    lines = [
        "This is the first line of a continuing sentence",
        "and here is the second line continuing without a break.",
        "Here begins a new paragraph following a period.",
    ]
    paras = pr.merge_lines_into_paragraphs(lines)
    assert len(paras) == 2
    assert paras[0] == "This is the first line of a continuing sentence and here is the second line continuing without a break."
    assert paras[1] == "Here begins a new paragraph following a period."


def test_dehyphenation_rules():
    pr = ParagraphReconstructor(dehyphenate=True, preserve_true_hyphens=True)

    # Line break hyphen should be merged
    assert pr.is_line_break_hyphen("infor-", "mation") is True
    assert pr.is_line_break_hyphen("exami-", "nation") is True

    # True hyphenated words with prefixes should be preserved
    assert pr.is_line_break_hyphen("well-", "known") is False
    assert pr.is_line_break_hyphen("self-", "esteem") is False


def test_paragraph_reconstruct_text_with_hyphen():
    pr = ParagraphReconstructor(dehyphenate=True, preserve_true_hyphens=True)
    lines = [
        "The clinician gathered the infor-",
        "mation regarding previous interventions.",
    ]
    merged = pr.merge_lines_into_paragraphs(lines)
    assert len(merged) == 1
    assert "information" in merged[0]
    assert "infor- mation" not in merged[0]
