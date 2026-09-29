"""
Document Output Formatter Subsystem.
Transforms structured SemanticRegions and PageResults into clean, readable, publication-grade text.
Guarantees NO SILENT DATA LOSS: running headers/footers are tagged without breaking paragraph flow.
"""

from typing import List, Optional

from src.config import ExtractionConfig, default_config
from src.models import PageResult, QualityStatus, RegionType, SemanticRegion
from src.reconstruction.headers_footers import HeaderFooterManager
from src.reconstruction.paragraphs import ParagraphReconstructor


class DocumentFormatter:
    def __init__(
        self,
        config: Optional[ExtractionConfig] = None,
        header_footer_mgr: Optional[HeaderFooterManager] = None,
    ):
        self.config = config or default_config
        self.header_footer_mgr = header_footer_mgr or HeaderFooterManager()
        self.para_reconstructor = ParagraphReconstructor(
            dehyphenate=self.config.dehyphenation_enabled,
            preserve_true_hyphens=self.config.preserve_true_hyphens,
        )

    def format_page(self, page_result: PageResult, include_page_header: bool = True) -> str:
        """Formats a single page's regions into readable text."""
        # Check if page failed
        if page_result.quality_status == QualityStatus.FAILED:
            err = page_result.error_message or "Unknown extraction failure"
            return f"\n--- [PAGE {page_result.page_num} — EXTRACTION FAILED: {err}] ---\n"

        sections: List[str] = []

        if include_page_header:
            sections.append(f"--- [Page {page_result.page_num}] ---")

        if page_result.quality_status in (QualityStatus.REVIEW_RECOMMENDED, QualityStatus.LOW_CONFIDENCE):
            warn_str = f" [REVIEW RECOMMENDED: confidence={page_result.confidence:.2f}]"
            if page_result.warnings:
                warn_str += f" ({'; '.join(page_result.warnings)})"
            sections.append(f"<!-- NOTE:{warn_str} -->")

        current_para_lines: List[str] = []
        footnotes: List[str] = []
        prev_col_idx = None
        prev_bbox = None

        def flush_paragraphs():
            nonlocal current_para_lines
            if current_para_lines:
                merged = self.para_reconstructor.merge_lines_into_paragraphs(current_para_lines)
                for p in merged:
                    if p.strip():
                        sections.append(p.strip())
                current_para_lines = []

        for region in page_result.regions:
            text = region.text.strip()
            if not text:
                continue

            # If switching between columns or spanning blocks, immediately flush!
            if prev_col_idx is not None and region.column_index != prev_col_idx:
                flush_paragraphs()

            # If large vertical paragraph gap, flush!
            if (
                prev_bbox is not None
                and region.region_type == RegionType.PARAGRAPH
                and (region.bbox.y0 - prev_bbox.y1) > 30.0
            ):
                flush_paragraphs()

            prev_col_idx = region.column_index
            prev_bbox = region.bbox

            # Context-aware Header handling (NO SILENT DELETION OF SUBSTANTIVE CONTENT)
            if region.region_type == RegionType.HEADER:
                flush_paragraphs()
                # Skip isolated marginal scanner noise / single-character artifacts
                if len(text) <= 2 or text.lower() in ("ae", "oe", "wh", "myr as 0", "و"):
                    continue
                if not (self.header_footer_mgr.is_running_header(text) or len(text) < 15):
                    sections.append(text)
                continue

            # Context-aware Footer handling
            if region.region_type == RegionType.FOOTER:
                flush_paragraphs()
                if len(text) <= 2 or text.lower() in ("ae", "oe", "wh", "oe]", "و"):
                    continue
                if not (self.header_footer_mgr.is_running_footer(text) or len(text) < 15):
                    sections.append(text)
                continue

            if region.region_type == RegionType.PAGE_NUMBER:
                # Page numbers are recorded in page provenance, suppressed from text body
                continue

            # Structural Headings (Clean book formatting without markdown syntax noise)
            if region.region_type in (RegionType.TITLE, RegionType.HEADING, RegionType.SUBHEADING):
                flush_paragraphs()
                sections.append(text)
                continue

            # Tables
            if region.region_type == RegionType.TABLE:
                flush_paragraphs()
                sections.append(text)
                continue

            # Footnotes
            if region.region_type == RegionType.FOOTNOTE:
                footnotes.append(text)
                continue

            # Captions
            if region.region_type == RegionType.CAPTION:
                flush_paragraphs()
                sections.append(f"[{text}]")
                continue

            # Standard Paragraph lines
            current_para_lines.append(text)

        flush_paragraphs()

        # Append Footnotes cleanly at bottom
        if footnotes:
            sections.append("---")
            for fn in footnotes:
                sections.append(fn)

        return "\n\n".join(sections)

    def format_book(self, page_results: List[PageResult]) -> str:
        """Formats the entire book into a single coherent document."""
        self.header_footer_mgr.analyze_document_headers_footers(page_results)
        page_texts = [self.format_page(pr, include_page_header=True) for pr in page_results]
        return "\n\n".join(page_texts) + "\n"
