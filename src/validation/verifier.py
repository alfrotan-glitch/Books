"""
Cross-Page Verification and Anomaly Detection Subsystem.
Verifies complete coverage, page continuity, text density anomalies,
and consecutive duplicate pages.
"""

from dataclasses import dataclass, field
import difflib
from typing import Any, Dict, List
import numpy as np

from src.models import PageResult, QualityStatus


@dataclass
class AnomalyRecord:
    page_num: int
    anomaly_type: str  # "MISSING_PAGE", "DENSITY_DROP", "CONSECUTIVE_DUPLICATE", "EMPTY_PAGE"
    severity: str      # "HIGH", "MEDIUM", "LOW"
    description: str


@dataclass
class VerificationSummary:
    is_valid: bool
    total_pages_expected: int
    total_pages_processed: int
    missing_pages: List[int]
    anomalies: List[AnomalyRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_pages_expected": self.total_pages_expected,
            "total_pages_processed": self.total_pages_processed,
            "missing_pages": self.missing_pages,
            "anomalies": [
                {
                    "page_num": a.page_num,
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "description": a.description,
                }
                for a in self.anomalies
            ],
        }


class CrossPageVerifier:
    def verify_document(
        self,
        expected_page_count: int,
        page_results: List[PageResult],
    ) -> VerificationSummary:
        """
        Validates page continuity, density drops, and duplicated pages across the document.
        """
        anomalies: List[AnomalyRecord] = []

        # 1. Check Missing Pages
        processed_page_nums = {pr.page_num for pr in page_results}
        missing_pages = [p for p in range(1, expected_page_count + 1) if p not in processed_page_nums]

        for p in missing_pages:
            anomalies.append(
                AnomalyRecord(
                    page_num=p,
                    anomaly_type="MISSING_PAGE",
                    severity="HIGH",
                    description=f"Page {p} was not processed or missing from output.",
                )
            )

        # Sort results by page_num
        sorted_results = sorted(page_results, key=lambda x: x.page_num)

        # 2. Density Anomaly Detection
        char_counts = [len(pr.text) for pr in sorted_results if len(pr.text) > 40]
        avg_char_count = float(np.mean(char_counts)) if char_counts else 500.0

        for pr in sorted_results:
            c_len = len(pr.text)
            # If not first or last page and very short
            if 1 < pr.page_num < expected_page_count:
                if c_len == 0 and pr.quality_status != QualityStatus.FAILED:
                    anomalies.append(
                        AnomalyRecord(
                            page_num=pr.page_num,
                            anomaly_type="EMPTY_PAGE",
                            severity="MEDIUM",
                            description=f"Page {pr.page_num} yielded zero characters. Check if page is blank or scan failed.",
                        )
                    )
                elif 0 < c_len < (avg_char_count * 0.12):
                    anomalies.append(
                        AnomalyRecord(
                            page_num=pr.page_num,
                            anomaly_type="DENSITY_DROP",
                            severity="LOW",
                            description=f"Page {pr.page_num} has unusually low character count ({c_len} chars vs avg {int(avg_char_count)}).",
                        )
                    )

        # 3. Consecutive Duplicate Detection
        for i in range(len(sorted_results) - 1):
            pr_current = sorted_results[i]
            pr_next = sorted_results[i + 1]

            if len(pr_current.text) > 100 and len(pr_next.text) > 100:
                matcher = difflib.SequenceMatcher(None, pr_current.text, pr_next.text)
                sim = matcher.quick_ratio()
                if sim > 0.94:
                    anomalies.append(
                        AnomalyRecord(
                            page_num=pr_next.page_num,
                            anomaly_type="CONSECUTIVE_DUPLICATE",
                            severity="MEDIUM",
                            description=f"Page {pr_next.page_num} is almost identical to Page {pr_current.page_num} (similarity {round(sim, 2)}).",
                        )
                    )

        is_valid = (len(missing_pages) == 0) and not any(a.severity == "HIGH" for a in anomalies)

        return VerificationSummary(
            is_valid=is_valid,
            total_pages_expected=expected_page_count,
            total_pages_processed=len(page_results),
            missing_pages=missing_pages,
            anomalies=anomalies,
        )
