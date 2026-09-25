"""
Master Book Extraction Pipeline.
Coordinates forensics, layout detection, multi-engine OCR, reading order,
quality control, error recovery, streaming, checkpointing, and output generation.
"""

from collections import Counter
import datetime
import logging
from pathlib import Path
import time
from typing import Callable, Dict, List, Optional
import pymupdf

from src.config import ExtractionConfig, default_config
from src.extraction.native import NativeTextExtractor
from src.extraction.ocr_manager import OCRManager
from src.layout.detector import ColumnDetector
from src.models import (
    BookReport,
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
    RegionType,
    SemanticRegion,
)
from src.pdf.forensics import PDFForensicsEngine
from src.pdf.reader import PDFReader
from src.pipeline.checkpoint import CheckpointManager
from src.pipeline.reporter import ReportGenerator
from src.reconstruction.formatter import DocumentFormatter
from src.reconstruction.headers_footers import HeaderFooterManager
from src.validation.language import LanguageDetector
from src.validation.ocr_cleaner import OCRErrorDetector
from src.validation.quality_control import QualityControlEngine
from src.validation.verifier import CrossPageVerifier


class BookPipeline:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config
        self.config.ensure_directories()

        # Initialize subcomponents
        self.forensics_engine = PDFForensicsEngine(self.config)
        self.native_extractor = NativeTextExtractor(self.config)
        self.ocr_manager = OCRManager(self.config)
        self.language_detector = LanguageDetector()
        self.ocr_cleaner = OCRErrorDetector()
        self.qc_engine = QualityControlEngine(self.config)
        self.verifier = CrossPageVerifier()

        # Logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("BookPipeline")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            log_dir = self.config.logs_dir / timestamp
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "extraction.log"

            fh = logging.FileHandler(str(log_file), encoding="utf-8")
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            logger.addHandler(ch)

        return logger

    def process_pdf(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        force_reprocess: bool = False,
    ) -> BookReport:
        """
        Processes an entire PDF book with streaming page processing, fault tolerance,
        and resumable checkpointing.
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        book_name = pdf_path.stem
        self.logger.info(f"Starting extraction for book: {pdf_path.name}")

        checkpoint_mgr = CheckpointManager(self.config.checkpoints_dir, book_name)
        if force_reprocess:
            checkpoint_mgr.clear()

        completed_pages = checkpoint_mgr.get_completed_pages()
        if completed_pages:
            self.logger.info(
                f"Resuming from checkpoint: {len(completed_pages)} pages already completed."
            )

        with PDFReader(pdf_path) as reader:
            total_pages = reader.page_count
            doc_meta = self.forensics_engine.analyze_document_metadata(reader.doc, pdf_path)
            self.logger.info(f"Document Info: {total_pages} pages, Version: {doc_meta.get('pdf_version')}")

            # Stream pages one by one
            for page_num, page in reader.stream_pages(1, total_pages):
                if page_num in completed_pages and not force_reprocess:
                    if progress_callback:
                        progress_callback(page_num, total_pages, f"Page {page_num} loaded from checkpoint")
                    continue

                if progress_callback:
                    progress_callback(page_num, total_pages, f"Processing page {page_num}/{total_pages}")

                page_start_t = time.time()
                try:
                    page_result = self._process_single_page(reader, page, page_num)
                    checkpoint_mgr.save_page(page_result)
                    elapsed = time.time() - page_start_t
                    self.logger.info(
                        f"Page {page_num}/{total_pages} processed ({page_result.extraction_method.value}) "
                        f"- Status: {page_result.quality_status.value} in {elapsed:.2f}s"
                    )
                except Exception as exc:
                    self.logger.error(f"Error on Page {page_num}: {exc}", exc_info=True)
                    # Fault isolation: record failure and continue
                    failed_result = PageResult(
                        page_num=page_num,
                        classification=PageClassification.UNKNOWN,
                        extraction_method=ExtractionMethod.FALLBACK,
                        text="",
                        quality_status=QualityStatus.FAILED,
                        confidence=0.0,
                        error_message=str(exc),
                        warnings=[f"Unhandled exception during extraction: {exc}"],
                    )
                    checkpoint_mgr.save_page(failed_result)

        # Retrieve all page results from checkpoint (preserves order)
        all_results = checkpoint_mgr.get_all_results()

        # Run Cross-page Header/Footer Analysis
        header_footer_mgr = HeaderFooterManager(self.config.recurring_header_min_frequency)
        header_footer_mgr.analyze_document_headers_footers(all_results)

        # Run Cross-Page Verification
        verification = self.verifier.verify_document(total_pages, all_results)

        # Format Full Book Text
        formatter = DocumentFormatter(self.config, header_footer_mgr)
        formatted_pages_map = {pr.page_num: formatter.format_page(pr, include_page_header=True) for pr in all_results}
        full_book_text = "\n\n".join(formatted_pages_map[pr.page_num] for pr in all_results) + "\n"

        # Generate Page Provenance Manifest & Completeness Audit
        from src.pipeline.provenance import ProvenanceAuditor
        provenance_manifest = ProvenanceAuditor.audit_and_generate_manifest(
            book_name=book_name,
            pdf_path=str(pdf_path),
            total_input_pages=total_pages,
            page_results=all_results,
            formatted_pages=formatted_pages_map,
            verification=verification,
            output_dir=self.config.output_dir,
        )
        self.logger.info(f"Generated provenance & completeness audit: {book_name}_provenance.json")

        # Write Output Text File
        output_txt_path = self.config.output_dir / f"{book_name}.txt"
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_book_text)
        self.logger.info(f"Generated output text deliverable: {output_txt_path}")

        # Compute Book Statistics
        total_time = time.time() - start_time
        report = self._build_book_report(
            book_name=book_name,
            pdf_path=str(pdf_path),
            total_pages=total_pages,
            page_results=all_results,
            processing_time=total_time,
            output_txt_path=str(output_txt_path),
        )

        # Generate Reports (JSON, HTML, CSV, Errors)
        ReportGenerator.generate_all_reports(report, self.config.output_dir, verification)

        self.logger.info(
            f"Extraction Complete for {book_name}: {report.successful_pages}/{total_pages} succeeded, "
            f"{report.needs_review_pages} need review, {report.failed_pages} failed."
        )
        return report

    def _process_single_page(
        self,
        reader: PDFReader,
        page: pymupdf.Page,
        page_num: int,
    ) -> PageResult:
        """Processes an individual page according to forensic classification."""
        rect = page.rect
        width_pt = rect.width
        height_pt = rect.height

        forensics = self.forensics_engine.analyze_page(page, page_num)
        classification = forensics.classification

        # Detect language / RTL direction
        sample_text = page.get_text("text")[:500] if forensics.has_native_text else ""
        lang_profile = self.language_detector.analyze_text(sample_text)
        is_rtl = lang_profile.is_rtl

        ordered_regions: List[SemanticRegion] = []
        method_used = ExtractionMethod.NATIVE
        ocr_confidence = 1.0
        warnings: List[str] = list(forensics.notes)

        # Decision Pipeline: Native vs OCR
        if (
            forensics.has_native_text
            and classification not in (PageClassification.SCANNED_IMAGE, PageClassification.ROTATED)
        ):
            # Attempt Native Extraction
            ordered_regions = self.native_extractor.process_page(page, page_num, is_rtl=is_rtl)
            method_used = ExtractionMethod.NATIVE
            ocr_confidence = 1.0

            # Verify if native extraction actually yielded text
            total_extracted = sum(len(r.text) for r in ordered_regions)
            if total_extracted < self.config.min_native_chars:
                if self.ocr_manager.is_ocr_available:
                    self.logger.info(f"Page {page_num}: Native extraction sparse ({total_extracted} chars), falling back to OCR.")
                    warnings.append("Native extraction produced minimal text; performed OCR fallback.")
                    image = reader.render_page_to_numpy(page_num, dpi=self.config.ocr_dpi)
                    ordered_regions, prep_res, method_used, ocr_confidence, ocr_warn = self.ocr_manager.process_image(
                        image, page_num, is_rtl=is_rtl
                    )
                    warnings.extend(ocr_warn)
                else:
                    warnings.append("OCR engine not available; retained native extraction output.")
        else:
            # Scanned / Image / Rotated / Complex layout -> Render high-DPI image and run OCR pipeline
            if self.ocr_manager.is_ocr_available:
                image = reader.render_page_to_numpy(page_num, dpi=self.config.ocr_dpi)
                ordered_regions, prep_res, method_used, ocr_confidence, ocr_warn = self.ocr_manager.process_image(
                    image, page_num, is_rtl=is_rtl
                )
                warnings.extend(ocr_warn)
            else:
                # Fallback: check if page has any native text before declaring failure
                raw_text = page.get_text("text").strip()
                if raw_text:
                    ordered_regions = self.native_extractor.process_page(page, page_num, is_rtl=is_rtl)
                    method_used = ExtractionMethod.FALLBACK
                    ocr_confidence = 0.7
                    warnings.append("No OCR engine available; extracted raw PDF text layer.")
                else:
                    raise RuntimeError(
                        "این صفحه اسکن‌شده تصویری است اما موتور OCR فعال نیست. "
                        "پایتون ۳.۱۴ از RapidOCR پشتیبانی نمی‌کند؛ لطفاً پایتون ۳.۱۲ استاندارد را نصب کنید."
                    )

        # Perform OCR Error Detection and High-Confidence Cleaning
        for reg in ordered_regions:
            cleaned, corrections = self.ocr_cleaner.detect_and_clean(reg.text, page_num=page_num)
            reg.text = cleaned
            for c in corrections:
                if c.applied:
                    warnings.append(f"Auto-corrected: {c.original} -> {c.corrected} ({c.reason})")

        # Assemble single-page raw text for QC
        combined_text = "\n\n".join(r.text for r in ordered_regions if r.text.strip())

        # Quality Control
        metrics, status = self.qc_engine.evaluate_page(
            page_num=page_num,
            raw_text=combined_text,
            page_width_pt=width_pt,
            page_height_pt=height_pt,
            ocr_confidence=ocr_confidence,
            language=lang_profile.primary_language,
            language_confidence=lang_profile.confidence,
            warnings=warnings,
        )

        # Count tables and footnotes
        tables_count = sum(1 for r in ordered_regions if r.region_type == RegionType.TABLE)
        footnotes_count = sum(1 for r in ordered_regions if r.region_type == RegionType.FOOTNOTE)

        # Determine column count from body regions
        cols = {r.column_index for r in ordered_regions if r.column_index >= 0}
        col_count = max(1, len(cols))

        return PageResult(
            page_num=page_num,
            classification=classification,
            extraction_method=method_used,
            text=combined_text,
            regions=ordered_regions,
            quality_status=status,
            quality_metrics=metrics,
            column_count=col_count,
            confidence=ocr_confidence,
            warnings=warnings,
            tables_count=tables_count,
            footnotes_count=footnotes_count,
        )

    def _build_book_report(
        self,
        book_name: str,
        pdf_path: str,
        total_pages: int,
        page_results: List[PageResult],
        processing_time: float,
        output_txt_path: str,
    ) -> BookReport:
        native_count = sum(1 for pr in page_results if pr.extraction_method == ExtractionMethod.NATIVE)
        ocr_count = sum(
            1 for pr in page_results if pr.extraction_method in (ExtractionMethod.OCR_RAPIDOCR, ExtractionMethod.OCR_TESSERACT)
        )
        hybrid_count = sum(1 for pr in page_results if pr.extraction_method == ExtractionMethod.OCR_HYBRID)

        successful_count = sum(
            1 for pr in page_results if pr.quality_status in (QualityStatus.HIGH_CONFIDENCE, QualityStatus.GOOD)
        )
        review_count = sum(
            1 for pr in page_results if pr.quality_status == QualityStatus.REVIEW_RECOMMENDED
        )
        failed_count = sum(
            1 for pr in page_results if pr.quality_status in (QualityStatus.FAILED, QualityStatus.LOW_CONFIDENCE)
        )
        high_conf_count = sum(
            1 for pr in page_results if pr.quality_status == QualityStatus.HIGH_CONFIDENCE
        )

        review_pages = [pr.page_num for pr in page_results if pr.quality_status == QualityStatus.REVIEW_RECOMMENDED]
        failed_pages = [
            pr.page_num for pr in page_results if pr.quality_status in (QualityStatus.FAILED, QualityStatus.LOW_CONFIDENCE)
        ]

        # Layout breakdown
        layout_counter: Counter = Counter()
        for pr in page_results:
            c = pr.column_count
            name = "Single-column" if c <= 1 else f"{c}-column"
            layout_counter[name] += 1

        # Language breakdown
        lang_counter: Counter = Counter()
        for pr in page_results:
            lang_counter[pr.quality_metrics.language] += 1

        ocr_engines = []
        if any(pr.extraction_method in (ExtractionMethod.OCR_RAPIDOCR, ExtractionMethod.OCR_HYBRID) for pr in page_results):
            ocr_engines.append("RapidOCR (ONNX)")
        if any(pr.extraction_method in (ExtractionMethod.OCR_TESSERACT, ExtractionMethod.OCR_HYBRID) for pr in page_results):
            ocr_engines.append("Tesseract")

        return BookReport(
            book_name=book_name,
            pdf_path=pdf_path,
            total_pages=total_pages,
            native_pages=native_count,
            ocr_pages=ocr_count,
            hybrid_pages=hybrid_count,
            successful_pages=successful_count,
            needs_review_pages=review_count,
            failed_pages=failed_count,
            high_confidence_pages=high_conf_count,
            ocr_engines_used=ocr_engines,
            layout_types=dict(layout_counter),
            detected_languages=dict(lang_counter),
            processing_time_sec=processing_time,
            output_txt_path=output_txt_path,
            review_pages_list=review_pages,
            failed_pages_list=failed_pages,
            page_results=page_results,
        )
