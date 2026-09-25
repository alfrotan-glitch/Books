"""
CLI Entrypoint for Digital Book Text Extraction System.
Supports automated inbox processing, web UI server, PDF forensics inspection, and benchmarking.
"""

import argparse
import sys
from pathlib import Path
import uvicorn

from src.config import default_config
from src.pdf.forensics import PDFForensicsEngine
from src.pdf.reader import PDFReader
from src.pipeline.book_pipeline import BookPipeline


def print_banner():
    banner = r"""
================================================================================
   DIGITAL BOOK EXTRACTION ENGINE & FORENSICS PIPELINE (PRODUCTION-GRADE)
   Windows-First & Multi-Engine OCR | Correct Reading Order & Layout Recovery
================================================================================
"""
    print(banner)


def cmd_process(args):
    default_config.ensure_directories()
    pipeline = BookPipeline(default_config)

    target_pdfs = []
    if args.pdf:
        p = Path(args.pdf)
        if not p.exists():
            print(f"[ERROR] Specified file not found: {p}")
            sys.exit(1)
        target_pdfs.append(p)
    else:
        # Scan inbox
        inbox_files = sorted(default_config.inbox_dir.glob("*.pdf"))
        if not inbox_files:
            print("[INFO] No PDF files found in inbox/ directory.")
            print("[INFO] Please place one or more PDF files into 'inbox/' and run again.")
            return
        target_pdfs.extend(inbox_files)

    print(f"[INFO] Found {len(target_pdfs)} book(s) to process.")

    for idx, pdf_path in enumerate(target_pdfs, 1):
        print(f"\n[{idx}/{len(target_pdfs)}] >>> Processing: {pdf_path.name}")
        
        def cli_progress(page_num, total, msg):
            pct = (page_num / total) * 100 if total > 0 else 0
            sys.stdout.write(f"\r   [{pct:5.1f}%] (Page {page_num}/{total}) - {msg[:45]:<45}")
            sys.stdout.flush()

        report = pipeline.process_pdf(
            pdf_path=pdf_path,
            progress_callback=cli_progress,
            force_reprocess=args.force,
        )
        print("\n   [DONE] Extraction completed!")
        print(f"   Deliverable TXT: {report.output_txt_path}")
        print(f"   HTML Report:     {report.report_html_path}")
        print(f"   JSON Report:     {report.report_json_path}")
        print(f"   CSV Page Status: {report.page_status_csv_path}")
        print(f"   Pages: {report.total_pages} total | {report.successful_pages} successful | {report.needs_review_pages} review | {report.failed_pages} failed")


def cmd_serve(args):
    default_config.ensure_directories()
    host = args.host or default_config.server_host
    port = args.port or default_config.server_port
    print_banner()
    print(f"[INFO] Starting Web Dashboard on http://{host}:{port}")
    print(f"[INFO] User can open browser at http://localhost:{port}")
    uvicorn.run("src.ui.server:app", host=host, port=port, log_level="info")


def cmd_inspect(args):
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return

    forensics = PDFForensicsEngine(default_config)
    with PDFReader(pdf_path) as reader:
        meta = forensics.analyze_document_metadata(reader.doc, pdf_path)
        print("\n--- Document Metadata & Forensics ---")
        for k, v in meta.items():
            print(f"  {k:20}: {v}")

        if args.page:
            p_num = int(args.page)
            page = reader.get_page(p_num)
            p_info = forensics.analyze_page(page, p_num)
            print(f"\n--- Forensics for Page {p_num} ---")
            for k, v in p_info.to_dict().items():
                print(f"  {k:22}: {v}")
        else:
            print(f"\nScanning first 5 pages:")
            for p_num, page in reader.stream_pages(1, min(5, reader.page_count)):
                p_info = forensics.analyze_page(page, p_num)
                print(f"  Page {p_num:3}: {p_info.classification.value:18} | NativeText: {p_info.has_native_text} | Chars: {p_info.char_count:5} | Images: {p_info.image_count}")


def cmd_benchmark(args):
    from tests.benchmark import run_full_benchmark
    print_banner()
    print("[INFO] Running Comprehensive Digital Book Extraction Benchmark Suite...")
    run_full_benchmark()


def main():
    parser = argparse.ArgumentParser(description="Digital Book Text Extraction Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    p_proc = subparsers.add_parser("process", help="Extract text from PDF(s)")
    p_proc.add_argument("pdf", nargs="?", default=None, help="Path to PDF (optional, defaults to inbox/)")
    p_proc.add_argument("--force", action="store_true", help="Force reprocess from scratch (ignore checkpoints)")

    # Serve command
    p_serve = subparsers.add_parser("serve", help="Launch Web Dashboard")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host address (default 0.0.0.0)")
    p_serve.add_argument("--port", type=int, default=8000, help="Port (default 8000)")

    # Inspect command
    p_insp = subparsers.add_parser("inspect", help="Run forensic inspection on a PDF")
    p_insp.add_argument("pdf", help="Path to PDF file")
    p_insp.add_argument("--page", type=int, default=None, help="Inspect specific page number")

    # Benchmark command
    p_bench = subparsers.add_parser("benchmark", help="Run internal benchmark test suite")

    args = parser.parse_args()

    if args.command == "process":
        cmd_process(args)
    elif args.command == "serve":
        cmd_serve(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    else:
        # Default behavior: process inbox
        print_banner()
        cmd_process(argparse.Namespace(pdf=None, force=False))


if __name__ == "__main__":
    main()
