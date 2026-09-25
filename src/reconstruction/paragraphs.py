"""
Paragraph Reconstruction and Strict Dehyphenation Subsystem.
Merges broken OCR/PDF lines into coherent paragraphs and strictly differentiates
between line-break word splits (infor-mation -> information)
and genuine compound words (well-known, evidence-based, decision-making).
"""

import re
from typing import List, Set


class ParagraphReconstructor:
    def __init__(self, dehyphenate: bool = True, preserve_true_hyphens: bool = True):
        self.dehyphenate = dehyphenate
        self.preserve_true_hyphens = preserve_true_hyphens

        # Common compound words & prefix modifiers that MUST retain their hyphen
        self.compound_halves: Set[str] = {
            "well", "self", "cross", "peer", "evidence", "high", "low", "short",
            "long", "first", "second", "third", "decision", "rate", "cost",
            "state", "follow", "user", "blood", "case", "open", "closed", "full",
            "part", "broad", "narrow", "large", "small", "hard", "soft", "fast",
            "slow", "cold", "warm", "up", "out", "in", "off", "on", "quasi", "semi"
        }

        # Common compound suffixes that retain hyphens (e.g. -based, -related, -free, -like)
        self.compound_suffixes: Set[str] = {
            "based", "related", "induced", "associated", "free", "like", "type",
            "dependent", "resistant", "sensitive", "specific", "driven", "centered",
            "proven", "oriented", "bound", "borne", "led", "making", "seeking", "looking"
        }

        # Dictionary of standard English words frequently broken by line wraps
        self.valid_merged_lexicon: Set[str] = {
            "information", "examination", "administration", "distribution", "circulation",
            "respiratory", "cardiovascular", "pharmacology", "physiology", "pathology",
            "management", "alternative", "international", "individual", "development",
            "understanding", "significant", "comprehension", "vocabulary", "education",
            "educational", "institution", "measurement", "temperature", "concentration",
            "treatment", "prescription", "diagnostic", "investigation", "reconstruction",
            "communication", "recommendation", "responsibility", "characterization",
            "classification", "differentiation", "specialization", "organization",
            "transcription", "intervention", "interaction", "identification", "evaluation"
        }

        # Terminal punctuation regex (Western + Arabic/Persian)
        self.terminal_punct = re.compile(r"[\.\!\?؟؛\:\。\！\？]$")

        # Bullet or list item prefix regex
        self.bullet_regex = re.compile(r"^(?:[\-\*•–—]|(?:\d+|[a-zA-Z])[\.\)])\s+")

    def is_line_break_hyphen(self, word1: str, word2: str) -> bool:
        """
        Strictly determines whether word1 ending with '-' followed by word2
        was split solely by line wrapping, or represents an authentic hyphenated compound.
        """
        w1 = word1.rstrip("-").lower()
        w2 = word2.lower()

        if not w1 or not w2:
            return False

        # If second word starts with uppercase, preserve hyphen (e.g. Franco-Prussian)
        if word2[0].isupper():
            return False

        # If prefix or suffix is a known compound component, preserve hyphen!
        if self.preserve_true_hyphens:
            if w1 in self.compound_halves:
                return False
            if w2 in self.compound_suffixes:
                return False

        joined = w1 + w2

        # 1. Exact match in verified merged lexicon
        if joined in self.valid_merged_lexicon:
            return True

        # 2. Syllable heuristic: if w1 is not a valid standalone English word
        # and joined ends with standard morphological endings (-tion, -ment, -ing, -ly, -able)
        common_endings = ("tion", "sion", "ment", "ing", "ly", "able", "ible", "ance", "ence", "ology", "ity")
        if joined.endswith(common_endings) and len(w1) >= 3 and len(w2) >= 3:
            # If w1 itself is not a common independent noun (like 'well', 'blood', 'case')
            if w1 not in self.compound_halves:
                return True

        # Default conservative stance: PRESERVE HYPHEN in case of uncertainty
        return False

    def merge_lines_into_paragraphs(self, lines: List[str]) -> List[str]:
        """
        Merges raw line strings into well-formed paragraph strings.
        """
        if not lines:
            return []

        paragraphs: List[str] = []
        current_para_lines: List[str] = []

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                if current_para_lines:
                    paragraphs.append(self._reconstruct_paragraph_text(current_para_lines))
                    current_para_lines = []
                continue

            # Check if this line is a bullet/numbered list item
            if self.bullet_regex.match(clean_line):
                if current_para_lines:
                    paragraphs.append(self._reconstruct_paragraph_text(current_para_lines))
                    current_para_lines = []
                current_para_lines.append(clean_line)
                continue

            if not current_para_lines:
                current_para_lines.append(clean_line)
                continue

            prev_line = current_para_lines[-1]

            ends_with_terminal = bool(self.terminal_punct.search(prev_line))
            first_char = clean_line[0] if clean_line else ""
            starts_with_lower = first_char.islower()

            if ends_with_terminal and not starts_with_lower:
                paragraphs.append(self._reconstruct_paragraph_text(current_para_lines))
                current_para_lines = [clean_line]
            else:
                current_para_lines.append(clean_line)

        if current_para_lines:
            paragraphs.append(self._reconstruct_paragraph_text(current_para_lines))

        return paragraphs

    def _reconstruct_paragraph_text(self, lines: List[str]) -> str:
        """Joins lines of a single paragraph, handling hyphenation cleanly."""
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]

        result = lines[0]
        for next_line in lines[1:]:
            if self.dehyphenate and result.endswith("-"):
                words_res = result.split()
                words_next = next_line.split()
                if words_res and words_next:
                    last_w = words_res[-1]
                    first_w = words_next[0]
                    if self.is_line_break_hyphen(last_w, first_w):
                        # Merge without hyphen
                        result = result[:-1] + next_line
                        continue
                    else:
                        # Genuine compound: keep hyphen
                        result = result + next_line
                        continue

            result = result + " " + next_line

        return result
