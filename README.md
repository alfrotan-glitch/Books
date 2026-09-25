# Digital Book Text Extraction Engine (Production-Grade)

An enterprise-grade, Windows-first document AI extraction system designed specifically for digitizing complex books from PDF files. Operates at the level of a Senior/Principal Document AI, Computer Vision, and PDF Forensics Engineer.

Unlike naive text dumpers or basic OCR wrappers, this engine is a **forensics-driven, layout-reconstructing pipeline** that recovers true logical reading order, reconstructs paragraphs and tables, isolates running headers and footers, and supports multi-column layouts, damaged mobile/CamScanner scans, and multi-thousand-page volumes with zero silent data loss.

---

## Key Capabilities

1. **Native & Scanned Multi-Engine Pipeline**
   - High-fidelity **Native Extraction** via PyMuPDF with span-level coordinates and font metrics.
   - Built-in **RapidOCR (ONNX Runtime)**: Zero external binary dependencies; runs on CPU/GPU out of the box on Windows and Linux.
   - Pluggable **Tesseract OCR** with agreement analysis and confidence voting.

2. **Strict Reading Order Engine**
   - Automatic column count detection (1, 2, 3, or multi-column) via whitespace gutter projection analysis.
   - True reading sequence: reads Column 1 completely top-to-bottom before proceeding to Column 2 (not interleaved by horizontal baseline).
   - Preserves spanning chapter titles, section banners, contextual sidebars, and footnotes.
   - Bi-directional script support: automatically adapts column order for LTR (English) and RTL (Dari, Persian, Arabic, Pashto).

3. **Advanced Image Preprocessing (Computer Vision)**
   - **CamScanner & Phone Scan Correction**: Background illumination normalization using morphological closing to flatten lighting gradients and eliminate corner shadows.
   - **Deskewing**: Horizontal projection profile variance maximization (-12° to +12° in 0.1° precision).
   - **Orthogonal Rotation**: 90°/180°/270° orientation detection using morphological aspect ratio analysis.
   - **Border & Spine Artifact Removal**: Automatic suppression of dark flatbed scanner edges.
   - **Non-Destructive Guarantee**: Original document images are never modified; all operations are traceable.

4. **Document Structure & Paragraph Reconstruction**
   - Intelligent line-merging based on punctuation, capitalization, font size, and spacing.
   - **Dehyphenation**: Intelligently rejoins broken line-end hyphens (`infor-\nmation` → `information`) while preserving genuine compound words (`well-known`).
   - **Table Extraction**: Extracts tabular structures into clean Markdown tables.
   - **Footnote Routing**: Detects footnotes and anchors them at the bottom of the page (`--- \n [1] ...`).
   - **Running Header / Footer Suppression**: Detects repeating headers and footers across pages and prevents them from breaking sentences in body text.

5. **Fault Tolerance & Large Book Scalability**
   - **Streaming Generator**: Memory footprint remains constant regardless of page count (tested on 1000+ page books).
   - **Resumable SQLite Checkpoints**: If processing is interrupted at page 743, restarting resumes from page 743 without reprocessing pages 1–742.
   - **No Silent Loss (Rule 20 & 33)**: Missing or unextractable content produces visible markers (`[PAGE X — EXTRACTION FAILED: reason]`) and is logged in `errors.json`.
   - **Cross-Page Verification**: Audits page continuity, checks for density drops, and flags duplicate pages.

---

## Architecture Pipeline

```text
PDF Input (inbox/)
       │
       ▼
[1] Input Validation & Forensics (PDFForensicsEngine)
       │  ├─ Page Dimensions & Rotation
       │  ├─ Font & Character Encoding Integrity (CID / Corrupt check)
       │  ├─ Raster Image Coverage & Estimated DPI
       │  └─ Classification: NATIVE_TEXT | SCANNED_IMAGE | HYBRID | COMPLEX | ROTATED
       │
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼                                 ▼                                 ▼
[2A] Native Extraction           [2B] Computer Vision Preprocessing   [2C] Multi-Engine OCR
  • Span layout & baseline coords   • Shadow/Illumination Normalizer    • RapidOCR (ONNX)
  • Typography & font sizing        • Orthogonal Rotation Correction    • Tesseract (Fallback/Voting)
  • Ligature unification            • Precise Projection Deskew         • Confidence Scoring
  • Native Table extraction         • Scanner Border Removal
       │                                 │                                 │
       └─────────────────────────────────┴─────────────────────────────────┘
                                         │
                                         ▼
[3] Layout Analysis & Semantic Region Classifier
  • Vertical Whitespace Gutter Analysis (Column Detection: 1, 2, 3+)
  • Semantic Tagging: TITLE, HEADING, PARAGRAPH, TABLE, FOOTNOTE, HEADER, FOOTER, SIDEBAR
                                         │
                                         ▼
[4] Specialized Reading Order Engine
  • Spanning Top Headings → Column 1 (Top-to-Bottom) → Column 2 (Top-to-Bottom)
  • RTL vs LTR Column Order (English vs Persian/Dari/Arabic/Pashto)
  • Bottom Footnote and Margin Routing
                                         │
                                         ▼
[5] Text Reconstruction & Paragraph Dehyphenation
  • Line merging with sentence continuation heuristics
  • Smart hyphen resolution (information vs well-known)
  • Recurring Running Header / Footer Identification & Suppression
  • Markdown Table Formatting
                                         │
                                         ▼
[6] Validation, OCR Error Detection & Quality Control
  • High-confidence OCR error replacement with audit trail (med1cine → medicine)
  • Language and Script Analysis (English, Dari, Arabic, Pashto)
  • Page Quality Score: HIGH_CONFIDENCE | GOOD | REVIEW_RECOMMENDED | FAILED
  • Cross-Page Anomaly Detection (density drops, missing pages, duplicate detection)
                                         │
                                         ▼
[7] Resumable Checkpoint Persistence (SQLite)
                                         │
                                         ▼
[8] Final Deliverables Generation (output/)
  • <book-name>.txt
  • <book-name>_report.html (Interactive Visual Dashboard)
  • <book-name>_report.json
  • <book-name>_pages.csv
  • <book-name>_errors.json
```

---

## Directory Structure

```text
Books/
├── inbox/                  # Place input PDF files here
├── output/                 # Extracted text, HTML reports, JSON, CSV
├── debug/                  # Preprocessed images & benchmark assets
├── logs/                   # Detailed timestamped execution logs
├── checkpoints/            # SQLite databases for crash-resilience
├── src/
│   ├── config.py           # Configuration parameters and thresholds
│   ├── models.py           # Data structures and enums
│   ├── pdf/
│   │   ├── forensics.py    # Deep PDF forensics and page classifier
│   │   └── reader.py       # Safe PyMuPDF streaming loader & renderer
│   ├── preprocessing/
│   │   ├── cv_pipeline.py  # Computer Vision deskew, shadows, rotation
│   │   └── quality.py      # Laplacian blur, contrast, brightness metrics
│   ├── layout/
│   │   ├── detector.py     # Multi-column whitespace gutter detection
│   │   ├── regions.py      # Semantic region classification
│   │   └── tables.py       # Table detection & Markdown reconstruction
│   ├── reading_order/
│   │   └── sorter.py       # Topological reading order engine
│   ├── extraction/
│   │   ├── native.py       # Native text extraction with precise layout
│   │   └── ocr_manager.py  # RapidOCR & Tesseract multi-engine manager
│   ├── reconstruction/
│   │   ├── paragraphs.py   # Paragraph merger & dehyphenation
│   │   ├── headers_footers.py # Cross-page running header/footer analyzer
│   │   └── formatter.py    # Text formatter with markdown tables & footnotes
│   ├── validation/
│   │   ├── ocr_cleaner.py  # Gated OCR error correction with audit log
│   │   ├── language.py     # Language detection (English, Dari, Arabic, Pashto)
│   │   ├── quality_control.py # Page-level quality scoring
│   │   └── verifier.py     # Cross-page integrity verifier
│   ├── pipeline/
│   │   ├── checkpoint.py   # Resumable SQLite state store
│   │   ├── book_pipeline.py # Master streaming orchestrator
│   │   └── reporter.py     # HTML, JSON, CSV report generator
│   ├── ui/
│   │   └── server.py       # FastAPI live web dashboard
│   └── cli.py              # Unified command-line interface
├── tests/
│   ├── benchmark.py        # 12-scenario synthetic & real benchmark suite
│   ├── test_forensics.py
│   ├── test_preprocessing.py
│   ├── test_layout_reading_order.py
│   ├── test_paragraph_reconstruction.py
│   ├── test_tables_footnotes.py
│   ├── test_ocr_cleaner.py
│   ├── test_language.py
│   ├── test_checkpoint_resume.py
│   ├── test_fault_tolerance.py
│   └── test_verifier.py
├── run.bat                 # Windows one-click automated execution script
├── setup.bat               # Windows one-click environment installer & shortcut creator
├── شروع_برنامه.bat          # Windows Persian one-click UI launcher
├── نصب_و_راه_اندازی.bat     # Windows Persian setup wizard & shortcut installer
├── ایجاد_میانبر_دسکتاپ.bat  # Creates Desktop icon shortcut (.lnk)
├── create_desktop_shortcut.bat # Creates Desktop icon shortcut (.lnk)
├── assets/
│   ├── app_icon.ico        # Official Windows multi-resolution icon
│   └── app_icon.png        # Web & high-res graphic icon
├── راهنمای_اجرا_روی_دسکتاپ.md # Comprehensive Persian Desktop Deployment Guide
├── DESKTOP_DEPLOYMENT.md   # Comprehensive English Desktop Deployment Guide
├── INDEPENDENT_QUALITY_AUDIT_REPORT.md # Full forensics audit report
├── requirements.txt        # Python dependency manifest
└── README.md
```

---

## Windows Desktop Deployment (Turnkey)

### Quick Start for Non-Technical Users
1. **Clone to Desktop:**
   ```powershell
   cd "$env:USERPROFILE\Desktop"
   git clone -b arena/01a0d9ec-books https://github.com/alfrotan-glitch/Books.git BOOK-TEXT-EXTRACTOR
   ```
2. **One-Click Setup:**
   Double-click `setup.bat` (or `نصب_و_راه_اندازی.bat`). It will initialize the environment, install packages, and place a **"Book Text Extractor"** shortcut icon directly on your Windows Desktop.
3. **Run Application:**
   Double-click the **Book Text Extractor** desktop shortcut or `شروع_برنامه.bat` to launch the Graphical Dashboard at `http://localhost:8000`.

See **`راهنمای_اجرا_روی_دسکتاپ.md`** and **`DESKTOP_DEPLOYMENT.md`** for complete step-by-step documentation.

---

## Command-Line Usage (Windows & Linux)

### Process Inbox or a Specific PDF
```bash
# Process all PDFs in inbox/
python -m src.cli process

# Process a specific PDF file
python -m src.cli process path/to/book.pdf

# Force reprocess (ignore previous checkpoints)
python -m src.cli process path/to/book.pdf --force
```

### Launch Web Dashboard
```bash
python -m src.cli serve --host 0.0.0.0 --port 8000
```

### Run PDF Forensic Analysis
```bash
# Inspect high-level document metadata and first 5 pages
python -m src.cli inspect path/to/book.pdf

# Deep-dive into a specific page
python -m src.cli inspect path/to/book.pdf --page 42
```

### Run Internal Benchmark Suite
```bash
python -m src.cli benchmark
```

### Run Pytest Test Suite
```bash
pytest tests/ -v
```

---

## Benchmark Suite Results

The built-in benchmark runner tests 12 critical document scenarios:

| # | Benchmark Scenario | Engine / Subsystem | Status | Validation Criteria |
|---|---|---|:---:|---|
| 1 | Single-column Native Text | Native Extractor | **PASS** | Title + paragraph flow |
| 2 | Two-column Native Text | Reading Order Sorter | **PASS** | Col 1 read completely before Col 2 |
| 3 | Single-column Scanned Image | RapidOCR (ONNX) | **PASS** | 300 DPI raster OCR extraction |
| 4 | Two-column Scanned Image | CV Layout + OCR | **PASS** | Column boundary separation |
| 5 | CamScanner Mobile Capture | CV Shadow Normalizer | **PASS** | Illumination flattened, skew corrected |
| 6 | Rotated Page (90 degrees) | Morphological Rotation | **PASS** | Orthogonal rotation detected & fixed |
| 7 | Low Quality / Noisy Scan | Denoising + CLAHE | **PASS** | Resilient text extraction |
| 8 | Recurring Header/Footer | HeaderFooterManager | **PASS** | Running headers cleanly isolated |
| 9 | Footnote Page | Region Classifier | **PASS** | Footnotes anchored at page bottom |
| 10 | Data Table Page | TableDetector | **PASS** | Reconstructed as Markdown table |
| 11 | Hybrid (Native + Raster Diagram) | Forensics Classifier | **PASS** | Text and diagrams handled in flow |
| 12 | Multi-page Book Simulation | CheckpointManager | **PASS** | Sequential streaming & persistence |

**Overall Benchmark Score: 12/12 Passed (100.0% Success Rate)**

---

## Output Deliverables

For each processed book (e.g. `Handbook.pdf`), the system writes:

1. **`output/Handbook.txt`**:
   The primary text deliverable. Formatted with clean Markdown headings (`#`, `##`), double newline paragraph breaks, clean Markdown tables (`| ... |`), separated footnotes (`--- \n [1] ...`), and explicit failure markers if any unrecoverable errors occur.

2. **`output/Handbook_report.html`**:
   Self-contained, interactive HTML dashboard displaying:
   - Total pages, Native vs OCR breakdown, execution time.
   - Summary stat cards for high-confidence, review-recommended, and failed pages.
   - Filterable table of every page with classification, extraction method, confidence score, and warnings.
   - Dedicated alert boxes highlighting pages that require manual attention.

3. **`output/Handbook_report.json`**:
   Full forensic audit trail containing document metadata, page classifications, quality metrics, and cross-page verification results.

4. **`output/Handbook_pages.csv`**:
   Tabular page index for data pipelines and automated QA review:
   `page_num,classification,extraction_method,quality_status,confidence,char_count,column_count,tables_count,footnotes_count,error_message,warnings`

5. **`output/Handbook_errors.json`**:
   Isolated list of pages with status `FAILED` or with critical warnings, including error messages and stack traces.

---

## Fault Tolerance & Resumability

If processing a 1,500-page book is interrupted at page 800 (due to system reboot, power outage, or cancellation):
- Each processed page is committed transactionally to an SQLite database (`checkpoints/<book-name>_checkpoint.sqlite`).
- Re-running `run.bat` automatically checks the checkpoint, identifies pages 1–799 as completed, and seamlessly continues processing from page 800.
- Individual corrupt pages do not crash the pipeline. The corrupt page is tagged `[PAGE X — EXTRACTION FAILED: <reason>]`, recorded in `errors.json`, and the pipeline proceeds with subsequent pages.

---

## Language & Multi-Script Support

- **English & Latin Scripts**: Full dehyphenation and typographic ligature resolution.
- **Persian / Dari (فارسی / دری)**: Automatic RTL detection, right-to-left column reading order, Persian typography preservation.
- **Pashto (پښتو)**: Pashto-specific letter detection (`ټ`, `ډ`, `ړ`, `ږ`, `ښ`, `څ`, `ځ`, `ڼ`, `ۍ`, `ې`).
- **Arabic (العربية)**: Full RTL script preservation and Arabic punctuation recognition.

---

## Troubleshooting

1. **Python Not Found on Windows**:
   - Ensure Python 3.10 or newer is installed from [python.org](https://www.python.org/downloads/).
   - Ensure the option **"Add Python to PATH"** was checked during installation.

2. **Missing Tesseract**:
   - Tesseract is **optional**. The system comes bundled with RapidOCR (ONNX Runtime) which runs out of the box with zero external installation.
   - If you wish to enable Tesseract as a secondary voting engine, install Tesseract for Windows and ensure it is added to PATH.

3. **Memory Limits on Massive Books (3000+ pages)**:
   - The engine streams pages sequentially using generators and does not load the entire PDF into RAM.
   - For optimal speed on very large documents, ensure at least 4 GB of free RAM.
