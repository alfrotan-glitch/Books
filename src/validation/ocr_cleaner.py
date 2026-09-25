"""
OCR Error Detection and Highly Conservative Correction Subsystem.
Strict Principle: "A visible OCR error is better than a false correction."
Every correction is strictly logged and audited: (page, original, corrected, confidence, reason).
Only applies replacements when the candidate word is verified in a validated lexicon.
"""

from dataclasses import dataclass
import re
from typing import List, Optional, Set, Tuple


@dataclass
class OCRErrorCorrection:
    page_num: int
    original: str
    corrected: str
    confidence: float
    reason: str
    applied: bool

    def to_dict(self):
        return {
            "page_num": self.page_num,
            "original": self.original,
            "corrected": self.corrected,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "applied": self.applied,
        }


class OCRErrorDetector:
    def __init__(self, min_confidence_to_apply: float = 0.90):
        self.min_confidence_to_apply = min_confidence_to_apply

        # Pattern for letters with a single embedded digit: e.g. "med1cine", "c1inical"
        self.digit_in_word_pattern = re.compile(r"\b([a-zA-Z]{2,})([0158])([a-zA-Z]{2,})\b")

        # Scientific/chemical/model identifiers that should NEVER be touched
        self.protected_identifiers: Set[str] = {
            "covid19", "sars", "h1n1", "h5n1", "co2", "h2o", "b12", "d3", "t3", "t4",
            "cd4", "cd8", "il6", "il1", "tnf", "p53", "brca1", "brca2", "page1", "fig1", "table1"
        }

        # Validated lexicon of high-frequency words prone to OCR digit substitution
        self.verified_lexicon: Set[str] = {
            "medicine", "medical", "clinical", "hospital", "patient", "treatment",
            "protocol", "individual", "prescription", "condition", "illness",
            "examination", "physician", "surgical", "diagnosis", "analysis",
            "circulation", "respiratory", "cardiovascular", "pharmacology",
            "information", "guideline", "definition", "position", "condition",
            "education", "educational", "institution", "measurement", "temperature",
            "concentration", "investigation", "reconstruction", "communication",
            "book", "blood", "good", "food", "look", "took", "room", "door", "school",
            "action", "motion", "option", "section", "fraction", "reaction", "traction",
            "critical", "optical", "physical", "typical", "practical", "chemical"
        }

    def detect_and_clean(self, text: str, page_num: int = 0) -> Tuple[str, List[OCRErrorCorrection]]:
        """
        Scans text for OCR errors. Applies ONLY high-confidence, verified fixes.
        Never alters text without lexical verification.
        """
        if not text:
            return text, []

        corrections: List[OCRErrorCorrection] = []
        cleaned_text = text

        def replacer(match: re.Match) -> str:
            prefix = match.group(1)
            digit = match.group(2)
            suffix = match.group(3)
            orig_word = match.group(0)

            # Never touch scientific identifiers
            if orig_word.lower() in self.protected_identifiers:
                return orig_word

            # Determine substitution candidates
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
            for ch in candidate_chars:
                candidate = prefix + ch + suffix
                if candidate.lower() in self.verified_lexicon:
                    best_word = candidate
                    break

            if best_word is not None:
                # Verified in dictionary -> high confidence
                conf = 0.94
                applied = conf >= self.min_confidence_to_apply
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig_word,
                        corrected=best_word,
                        confidence=conf,
                        reason=f"OCR digit-letter confusion: verified '{orig_word}' -> '{best_word}' in lexicon",
                        applied=applied,
                    )
                )
                return best_word if applied else orig_word
            else:
                # UNVERIFIED: preserve original text without guessing!
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig_word,
                        corrected=orig_word,
                        confidence=0.40,
                        reason=f"Potential OCR anomaly '{orig_word}' not found in verified lexicon; preserved original",
                        applied=False,
                    )
                )
                return orig_word

        cleaned_text = self.digit_in_word_pattern.sub(replacer, cleaned_text)

        # 2. Vertical bar '|' inside words: e.g. "c|inical" -> "clinical"
        bar_matches = re.findall(r"\b([a-zA-Z]+)\|([a-zA-Z]+)\b", cleaned_text)
        for pre, suf in bar_matches:
            orig = f"{pre}|{suf}"
            cand_l = f"{pre}l{suf}"
            cand_i = f"{pre}i{suf}"

            chosen = None
            if cand_l.lower() in self.verified_lexicon:
                chosen = cand_l
            elif cand_i.lower() in self.verified_lexicon:
                chosen = cand_i

            if chosen is not None:
                conf = 0.92
                applied = conf >= self.min_confidence_to_apply
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig,
                        corrected=chosen,
                        confidence=conf,
                        reason=f"Vertical bar misrecognized as letter: verified '{orig}' -> '{chosen}'",
                        applied=applied,
                    )
                )
                if applied:
                    cleaned_text = cleaned_text.replace(orig, chosen)
            else:
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig,
                        corrected=orig,
                        confidence=0.45,
                        reason=f"Unverified vertical bar pattern '{orig}'; preserved original",
                        applied=False,
                    )
                )

        return cleaned_text, corrections
