"""
Language Detection and Script Direction Subsystem.
Supports English, Dari/Persian, Arabic, and Pashto.
Identifies RTL text direction to guide layout and reading order engines.
"""

from dataclasses import dataclass
import re
from typing import Dict, Tuple


@dataclass
class LanguageProfile:
    primary_language: str  # "eng", "fas" (Dari/Persian), "ara", "pus" (Pashto)
    is_rtl: bool
    confidence: float
    script_distribution: Dict[str, float]


class LanguageDetector:
    def __init__(self):
        # Specific Persian/Dari letters not found in standard Arabic: گ چ پ ژ
        self.persian_markers = set("گچپژ")
        # Specific Pashto letters: ټ ډ ړ ږ ښ څ ځ ڼ ۍ ې
        self.pashto_markers = set("ټډړږښڅځڼۍې")
        # Standard Arabic markers: ة ئ ؤ ى
        self.arabic_markers = set("ةئؤى")

    def analyze_text(self, text: str) -> LanguageProfile:
        """Analyzes text to determine script, primary language, and RTL direction."""
        if not text or not text.strip():
            return LanguageProfile(
                primary_language="eng",
                is_rtl=False,
                confidence=1.0,
                script_distribution={"latin": 0.0, "arabic": 0.0},
            )

        latin_chars = 0
        arabic_chars = 0
        persian_marker_hits = 0
        pashto_marker_hits = 0
        arabic_marker_hits = 0

        for ch in text:
            code = ord(ch)
            # Latin ranges
            if (65 <= code <= 90) or (97 <= code <= 122):
                latin_chars += 1
            # Arabic & Persian Unicode ranges
            elif 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F or 0xFB50 <= code <= 0xFDFF or 0xFE70 <= code <= 0xFEFF:
                arabic_chars += 1
                if ch in self.persian_markers:
                    persian_marker_hits += 1
                if ch in self.pashto_markers:
                    pashto_marker_hits += 1
                if ch in self.arabic_markers:
                    arabic_marker_hits += 1

        total_letters = latin_chars + arabic_chars
        if total_letters == 0:
            return LanguageProfile(
                primary_language="eng",
                is_rtl=False,
                confidence=0.5,
                script_distribution={"latin": 0.0, "arabic": 0.0},
            )

        latin_ratio = latin_chars / total_letters
        arabic_ratio = arabic_chars / total_letters

        script_dist = {
            "latin": round(latin_ratio, 3),
            "arabic": round(arabic_ratio, 3),
        }

        # RTL Decision
        is_rtl = arabic_ratio > latin_ratio

        if is_rtl:
            # Distinguish Pashto, Dari/Persian, Arabic
            if pashto_marker_hits >= 2:
                lang = "pus"  # Pashto
                conf = min(0.98, 0.75 + (pashto_marker_hits * 0.05))
            elif persian_marker_hits >= 1:
                lang = "fas"  # Persian / Dari
                conf = min(0.98, 0.80 + (persian_marker_hits * 0.04))
            elif arabic_marker_hits >= 2:
                lang = "ara"  # Arabic
                conf = 0.85
            else:
                lang = "fas"  # Default Persian/Dari in this domain
                conf = 0.75
        else:
            lang = "eng"
            conf = min(0.99, latin_ratio)

        return LanguageProfile(
            primary_language=lang,
            is_rtl=is_rtl,
            confidence=round(conf, 3),
            script_distribution=script_dist,
        )
