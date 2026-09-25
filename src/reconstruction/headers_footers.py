"""
Header, Footer, and Page Number Management Subsystem.
Analyzes cross-page repetition, identifies running headers/footers,
and separates page numbers from body text.
"""

from collections import Counter
import re
from typing import Dict, List, Set, Tuple

from src.models import PageResult, RegionType, SemanticRegion


class HeaderFooterManager:
    def __init__(self, min_frequency_ratio: float = 0.20):
        self.min_frequency_ratio = min_frequency_ratio
        self.running_headers: Set[str] = set()
        self.running_footers: Set[str] = set()

    def normalize_text(self, text: str) -> str:
        """Normalizes header text by stripping numbers, punctuation, and whitespace."""
        cleaned = re.sub(r"[\d\.\-\—\–\|\•]", "", text.lower())
        return " ".join(cleaned.split())

    def analyze_document_headers_footers(self, page_results: List[PageResult]) -> None:
        """
        Scans all processed pages to identify recurring running headers and footers across the book.
        """
        total_pages = len(page_results)
        if total_pages < 2:
            return

        header_counts: Counter = Counter()
        footer_counts: Counter = Counter()

        for pr in page_results:
            for r in pr.regions:
                norm = self.normalize_text(r.text)
                if len(norm) >= 3:
                    if r.region_type == RegionType.HEADER:
                        header_counts[norm] += 1
                    elif r.region_type == RegionType.FOOTER:
                        footer_counts[norm] += 1

        min_count = max(2, int(total_pages * self.min_frequency_ratio))

        for text, count in header_counts.items():
            if count >= min_count:
                self.running_headers.add(text)

        for text, count in footer_counts.items():
            if count >= min_count:
                self.running_footers.add(text)

    def is_running_header(self, text: str) -> bool:
        norm = self.normalize_text(text)
        return norm in self.running_headers

    def is_running_footer(self, text: str) -> bool:
        norm = self.normalize_text(text)
        return norm in self.running_footers
