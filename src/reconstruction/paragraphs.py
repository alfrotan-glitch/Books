"""
Paragraph Reconstruction and Hyphenation Subsystem.
Merges broken OCR/PDF lines into coherent paragraphs and intelligently resolves line-break hyphens.
"""

import re
from typing import List, Tuple
from src.models import TextLine


class ParagraphReconstructor:
    def __init__(self, dehyphenate: bool = True, preserve_true_hyphens: bool = True):
        self.dehyphenate = dehyphenate
        self.preserve_true_hyphens = preserve_true_hyphens

        # Common compound prefixes/words that legitimately retain hyphens
        self.known_hyphenated_prefixes = {
            "self", "all", "cross", "ex", "quasi", "well", "co", "pre", "non", "anti", "post"
        }

        # Terminal punctuation regex (Western + Arabic/Persian)
        self.terminal_punct = re.compile(r"[\.\!\?؟؛\:\。\！\？]$")

        # Bullet or list item prefix regex
        self.bullet_regex = re.compile(r"^(?:[\-\*•–—]|(?:\d+|[a-zA-Z])[\.\)])\s+")

    def is_line_break_hyphen(self, word1: str, word2: str) -> bool:
        """
        Determines whether word1 ending with '-' followed by word2 was broken by line wrapping.
        e.g., 'infor-' + 'mation' -> True (join to 'information')
        e.g., 'well-' + 'known' -> False (keep 'well-known')
        """
        w1 = word1.rstrip("-").lower()
        w2 = word2.lower()

        if not w1 or not w2:
            return False

        # If prefix is a standard hyphenated prefix, preserve the hyphen
        if self.preserve_true_hyphens and w1 in self.known_hyphenated_prefixes:
            return False

        # If second word starts with uppercase, probably a hyphenated proper noun (e.g. Anglo-Saxon)
        if word2[0].isupper():
            return False

        # If both words are purely alphabetic, and combined length >= 5
        if w1.isalpha() and w2.isalpha():
            return True

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

            # Check if previous line ended with terminal punctuation
            ends_with_terminal = bool(self.terminal_punct.search(prev_line))

            # Check if current line starts with lowercase (clear continuation)
            first_char = clean_line[0] if clean_line else ""
            starts_with_lower = first_char.islower()

            if ends_with_terminal and not starts_with_lower:
                # Finished paragraph
                paragraphs.append(self._reconstruct_paragraph_text(current_para_lines))
                current_para_lines = [clean_line]
            else:
                # Continuation of current paragraph
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
                # Extract last word from result and first word from next_line
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
                        # Keep hyphen
                        result = result + next_line
                        continue

            # Standard space separation
            result = result + " " + next_line

        return result
