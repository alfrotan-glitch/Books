"""
OCR Error Detection and High-Confidence Correction Subsystem.
Detects common optical character recognition errors (digit/letter confusion, broken ligatures)
with full audit trail and strict confidence thresholds. Never alters text without high confidence.
"""

from dataclasses import dataclass
import re
from typing import List, Optional, Tuple


@dataclass
class OCRErrorCorrection:
    page_num: int
    original: str
    corrected: str
    confidence: float
    reason: str
    applied: bool


class OCRErrorDetector:
    def __init__(self, min_confidence_to_apply: float = 0.85):
        self.min_confidence_to_apply = min_confidence_to_apply

        # Embedded digit inside alphabetic word pattern: e.g. "med1cine", "b00k"
        self.digit_in_word_pattern = re.compile(r"\b([a-zA-Z]{2,})([0158])([a-zA-Z]{2,})\b")

        # Lexicon of common words with ambiguous OCR digit substitutions (1 -> i or l, 0 -> o)
        self.common_words = {
            "medicine", "medical", "clinical", "hospital", "patient", "treatment",
            "protocol", "individual", "prescription", "condition", "illness",
            "examination", "physician", "surgical", "diagnosis", "analysis",
            "circulation", "respiratory", "cardiovascular", "pharmacology",
            "information", "guideline", "definition", "position", "condition",
            "book", "blood", "good", "food", "look", "took", "room", "door",
        }

    def detect_and_clean(self, text: str, page_num: int = 0) -> Tuple[str, List[OCRErrorCorrection]]:
        """
        Scans text for OCR errors. Applies high-confidence fixes and logs all detected errors.
        """
        if not text:
            return text, []

        corrections: List[OCRErrorCorrection] = []
        cleaned_text = text

        # 1. Detect embedded digits in alphabetic words: e.g. med1cine -> medicine, c1inical -> clinical
        def replacer(match: re.Match) -> str:
            prefix = match.group(1)
            digit = match.group(2)
            suffix = match.group(3)
            orig_word = match.group(0)

            # Evaluate candidates for the digit
            candidate_chars = []
            if digit == "1":
                candidate_chars = ["i", "l"]
            elif digit == "0":
                candidate_chars = ["o"]
            elif digit == "5":
                candidate_chars = ["s"]
            elif digit == "8":
                candidate_chars = ["b"]
            else:
                candidate_chars = [digit]

            best_word = None
            # Check lexicon first
            for ch in candidate_chars:
                w_cand = prefix + ch + suffix
                if w_cand.lower() in self.common_words:
                    best_word = w_cand
                    break

            # Fallback heuristic
            if best_word is None:
                # If 1 is followed by 'c' or 't', often 'i' (e.g. med1cine, act1on)
                if digit == "1" and suffix.startswith(("c", "t", "n", "m")):
                    best_word = prefix + "i" + suffix
                else:
                    best_word = prefix + candidate_chars[0] + suffix

            conf = 0.92 if best_word.lower() in self.common_words else 0.75
            applied = conf >= self.min_confidence_to_apply

            corrections.append(
                OCRErrorCorrection(
                    page_num=page_num,
                    original=orig_word,
                    corrected=best_word if applied else orig_word,
                    confidence=conf,
                    reason=f"OCR digit-letter confusion: replaced '{digit}' in '{orig_word}' with '{best_word}'",
                    applied=applied,
                )
            )

            return best_word if applied else orig_word

        cleaned_text = self.digit_in_word_pattern.sub(replacer, cleaned_text)

        # 2. Detect vertical bar '|' misused as letter 'l' or 'I' inside words
        bar_in_word = re.findall(r"\b([a-zA-Z]+)\|([a-zA-Z]+)\b", cleaned_text)
        for pre, suf in bar_in_word:
            orig = f"{pre}|{suf}"
            cand = f"{pre}l{suf}"
            conf = 0.88
            applied = conf >= self.min_confidence_to_apply
            corrections.append(
                OCRErrorCorrection(
                    page_num=page_num,
                    original=orig,
                    corrected=cand if applied else orig,
                    confidence=conf,
                    reason="Vertical bar '|' recognized as letter 'l'",
                    applied=applied,
                )
            )
            if applied:
                cleaned_text = cleaned_text.replace(orig, cand)

        return cleaned_text, corrections
