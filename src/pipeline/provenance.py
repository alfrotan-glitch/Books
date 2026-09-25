"""
Page Provenance and Completeness Audit Subsystem.
Maintains complete mathematical audit trail for every page:
Layer 1: Original Page Forensics & Checksum
Layer 2: Structured Geometric Extraction (BBoxes, Regions, Tokens)
Layer 3: Final Reconstructed Publication Text
Audits: missing pages, empty pages, density drops, duplicates, corrections.
"""

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models import PageResult, QualityStatus
from src.validation.verifier import VerificationSummary


@dataclass
class PageProvenanceRecord:
    page_num: int
    raw_char_count: int
    final_char_count: int
    text_sha256: str
    forensics: Dict[str, Any]
    extraction_method: str
    quality_status: str
    confidence: float
    regions_count: int
    tables_count: int
    footnotes_count: int
    corrections_count: int
    warnings: List[str]
    raw_preview: str
    final_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "raw_char_count": self.raw_char_count,
            "final_char_count": self.final_char_count,
            "text_sha256": self.text_sha256,
            "forensics": self.forensics,
            "extraction_method": self.extraction_method,
            "quality_status": self.quality_status,
            "confidence": round(self.confidence, 3),
            "regions_count": self.regions_count,
            "tables_count": self.tables_count,
            "footnotes_count": self.footnotes_count,
            "corrections_count": self.corrections_count,
            "warnings": self.warnings,
            "raw_preview": self.raw_preview,
            "final_preview": self.final_preview,
        }


@dataclass
class BookProvenanceManifest:
    book_name: str
    pdf_path: str
    total_pages_input: int
    total_pages_processed: int
    successful_pages: int
    review_recommended_pages: int
    failed_pages: int
    empty_pages: List[int]
    suspiciously_short_pages: List[int]
    duplicate_pages: List[int]
    missing_pages: List[int]
    page_records: List[PageProvenanceRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_name": self.book_name,
            "pdf_path": self.pdf_path,
            "completeness_audit": {
                "total_pages_input": self.total_pages_input,
                "total_pages_processed": self.total_pages_processed,
                "successful_pages": self.successful_pages,
                "review_recommended_pages": self.review_recommended_pages,
                "failed_pages": self.failed_pages,
                "empty_pages": self.empty_pages,
                "suspiciously_short_pages": self.suspiciously_short_pages,
                "duplicate_pages": self.duplicate_pages,
                "missing_pages": self.missing_pages,
                "is_complete_zero_loss": len(self.missing_pages) == 0 and self.failed_pages == 0,
            },
            "pages": [p.to_dict() for p in self.page_records],
        }


class ProvenanceAuditor:
    @staticmethod
    def audit_and_generate_manifest(
        book_name: str,
        pdf_path: str,
        total_input_pages: int,
        page_results: List[PageResult],
        formatted_pages: Dict[int, str],
        verification: Optional[VerificationSummary] = None,
        output_dir: Optional[Path] = None,
    ) -> BookProvenanceManifest:
        """
        Builds a comprehensive provenance audit manifest and saves it to JSON.
        """
        page_records: List[PageProvenanceRecord] = []

        empty_pages = []
        suspicious_pages = []
        duplicate_pages = []

        if verification:
            for a in verification.anomalies:
                if a.anomaly_type == "EMPTY_PAGE":
                    empty_pages.append(a.page_num)
                elif a.anomaly_type == "DENSITY_DROP":
                    suspicious_pages.append(a.page_num)
                elif a.anomaly_type == "CONSECUTIVE_DUPLICATE":
                    duplicate_pages.append(a.page_num)

        processed_page_nums = {pr.page_num for pr in page_results}
        missing_pages = [p for p in range(1, total_input_pages + 1) if p not in processed_page_nums]

        for pr in page_results:
            final_text = formatted_pages.get(pr.page_num, pr.text)
            text_hash = hashlib.sha256(final_text.encode("utf-8")).hexdigest()

            rec = PageProvenanceRecord(
                page_num=pr.page_num,
                raw_char_count=len(pr.text),
                final_char_count=len(final_text),
                text_sha256=text_hash,
                forensics={"classification": pr.classification.value},
                extraction_method=pr.extraction_method.value,
                quality_status=pr.quality_status.value,
                confidence=pr.confidence,
                regions_count=len(pr.regions),
                tables_count=pr.tables_count,
                footnotes_count=pr.footnotes_count,
                corrections_count=sum(1 for w in pr.warnings if "Auto-corrected" in w),
                warnings=pr.warnings,
                raw_preview=(pr.text[:140] + "...") if len(pr.text) > 140 else pr.text,
                final_preview=(final_text[:140] + "...") if len(final_text) > 140 else final_text,
            )
            page_records.append(rec)

        success_count = sum(1 for pr in page_results if pr.quality_status in (QualityStatus.HIGH_CONFIDENCE, QualityStatus.GOOD))
        review_count = sum(1 for pr in page_results if pr.quality_status == QualityStatus.REVIEW_RECOMMENDED)
        fail_count = sum(1 for pr in page_results if pr.quality_status in (QualityStatus.FAILED, QualityStatus.LOW_CONFIDENCE))

        manifest = BookProvenanceManifest(
            book_name=book_name,
            pdf_path=pdf_path,
            total_pages_input=total_input_pages,
            total_pages_processed=len(page_results),
            successful_pages=success_count,
            review_recommended_pages=review_count,
            failed_pages=fail_count,
            empty_pages=sorted(list(set(empty_pages))),
            suspiciously_short_pages=sorted(list(set(suspicious_pages))),
            duplicate_pages=sorted(list(set(duplicate_pages))),
            missing_pages=missing_pages,
            page_records=page_records,
        )

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            provenance_file = output_dir / f"{book_name}_provenance.json"
            with open(provenance_file, "w", encoding="utf-8") as f:
                json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)

        return manifest
