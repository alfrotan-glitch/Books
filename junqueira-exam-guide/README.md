# Basic Histology: A Learning Text

A self-contained, **technically validated editorial-candidate** course in microscopic anatomy in 24 chapters, for students of medicine, dentistry and the biomedical sciences. It teaches the cell, the four basic tissues, and the organ systems, and ends with a hundred-question practice examination. The book includes nine **original schematic histology plates** (not copied microscopy photographs), alongside descriptive slide-identification methods and structure–function explanations.

The prose and nine generated schematic plates are newly authored for this project. No third-party textbook images, plates, captions or extended passages have intentionally been reproduced, and no page ranges or questions require the reader to consult another textbook. Independent legal clearance has not been performed.

## Latest build and publication status

**Use the latest successful [Build and validate histology book workflow](https://github.com/alfrotan-glitch/Books/actions/workflows/histology-book.yml).** The workflow now rebuilds and synchronizes the tracked PDF, DOCX, EPUB, HTML, CSV study decks and publication manifest on `main` after a passing run. The GitHub Actions artifact also bundles those files and the nine original schematic plates. The manifest records SHA-256 hashes and source commit.

The latest fully validated build ([run 39845766634](https://github.com/alfrotan-glitch/Books/actions/runs/39845766634)) produced **161 PDF pages, 46 PDF bookmarks, 2,215 DOCX paragraphs, 84 tables, 9 original schematic plates, 607 flashcards and 100 synchronized MCQs**. Official W3C EPUBCheck 5.4.0 reported zero errors and warnings, and scientific regression checks passed. The artifact includes the complete Appendix E real-slide practice companion (linked university resources, not copied photographs) and SHA-256 publication manifest.

**Status: editorial candidate, not independently medically certified or fully print-proofed.** An automated green build does not replace an end-to-end specialist review, clearance of any third-party content, physical printing/visual inspection, or e-reader/Word/browser acceptance. See [RELEASE_VERIFICATION.md](RELEASE_VERIFICATION.md).

## Modern EPUB reading edition

The EPUB is now designed as a **reader-first, reflowable EPUB 3** book rather than an exported print document. Its features include:

- A newly drawn, high-resolution modern cover and discoverable ebook metadata.
- **47 small XHTML reading sections**, with chapter-level navigation for all 24 chapters and appendices.
- A dedicated clickable index linking to all nine original histology schematic plates.
- Native font-size adjustment, a clear typographic hierarchy, reader-friendly links, and contrast-aware light/dark styling.
- **84 individually scrollable comparison tables** to avoid requiring horizontal scrolling of the entire book on a phone.
- Differentiated MICRO, CLINICAL, TIP, MNEMONIC and PEARL study callouts.
- Accessible figure descriptions, table-column header markup, and no embedded proprietary fonts or externally fetched images.
- Automatic structural checks and official W3C EPUBCheck 5.4.0 on every publication build.

**Reading tip:** In Apple Books, Google Play Books or another EPUB 3-capable reading app, use the app's font/size settings, chapter contents, bookmarks and text highlights. Wide comparison tables may require a horizontal swipe *inside the table* depending on the reader. Device rendering varies; independent cross-reader acceptance is still required for a fully certified release.

## Files

| File | Purpose |
|---|---|
| `Basic_Histology_Learning_Text.pdf` | A4 book with running heads, contents and PDF outline; **latest verified CI: 161 pages** (print proof still required) |
| `Basic_Histology_Learning_Text.docx` | Editable Word version (same content, Word styles) |
| `Basic_Histology_Learning_Text.html` | Phone/tablet reading copy, self-contained, no internet needed |
| `Basic_Histology_Learning_Text.epub` | EPUB 3, reflowable, navigable, for e-readers and phones |
| `src/*.md` | The manuscript — one file per section, plain Markdown |
| `build.py` | Markdown → PDF (ReportLab), book design and layout |
| `build_docs.py` | Markdown → DOCX and HTML (pandoc) |
| `build_epub.py` | Manuscript → chapter-split EPUB 3 with modern cover and ebook semantics |
| `tools/validate_epub.py` | Internal EPUB manifest and link checks |
| `tools/epub_polish.py` | Original cover design, modern scalable CSS, chapter navigation, table/figure semantics |
| `tools/validate_modern_epub.py` | Reader-experience regression checks for EPUB chapters, tables, figures and dark mode |
| `tools/release_smoke_test.py` | Automated PDF, DOCX, EPUB, HTML structural and geometry checks |
| `tools/generate_atlas.py` | Generates nine original labeled histology schematic diagrams |
| `tools/validate_study_materials.py` | Validates CSV decks against the 100 canonical manuscript questions |
| `tools/validate_scientific_corrections.py` | Rejects regressions of verified high-impact scientific corrections |
| `tools/write_release_manifest.py` | Creates per-format SHA-256 release manifest |
| `RELEASE_VERIFICATION.md` | Explicit, evidence-based final-publication acceptance criteria |
| `COVERAGE.md` | Source ledger: what was read, what was checked, known discrepancies |
| `FINAL_REVIEW_REPORT.md` | Production record: verification evidence, hashes, limitations |

## Rebuilding

```bash
python -m pip install reportlab pypandoc_binary python-docx pymupdf lxml
python3 tools/generate_atlas.py  # Build nine original schematic plates
python3 build.py         # PDF
python3 build_docs.py    # DOCX + HTML
python3 build_epub.py    # EPUB 3
python3 tools/validate_epub.py   # EPUB structural checks
python3 tools/validate_modern_epub.py   # EPUB reading/navigation/contrast checks
python3 tools/release_smoke_test.py   # Four-format smoke tests
python3 tools/make_study_decks.py     # Regenerate flashcards and MCQs
python3 tools/make_question_bank.py   # Regenerate canonical MCQ CSV
python3 tools/validate_study_materials.py   # Check alignment
python3 tools/validate_scientific_corrections.py  # Scientific regression guard
python3 tools/write_release_manifest.py   # SHA-256 provenance file
```

Edit anything in `src/`, then re-run all four. Sections are concatenated in filename order, so a new file named `02c_whatever.md` drops in automatically.

## What is inside

- **Before you begin** — how the book works, how to study (six-week, ten-day and 48-hour plans), the Twelve Laws of Histology, exam technique, a chapter guide, and a note on sources.
- **Chapters 1–23** — each has learning objectives, a core idea, the explanation in sections, structure–function reasoning, comparison tables, clinical correlates, common misconceptions, a summary, active-recall questions, one exam-style question with a worked answer, and a practical identification task.
- **Chapter 24** — the last-24-hours rapid review: a concept map of the subject, the organ-identification algorithm, ten master tables, 100 one-line facts and 25 distinctions that decide marks.
- **Appendices** — A: stains and their chemistry; B: histology vocabulary; C: sources and evidence limits; D: nine original tissue-pattern schematic plates; E: an optional chapter-by-chapter guide to real histology slides hosted by universities, with no third-party photos reproduced.
- **Part VII** — 100 examination questions with explained answers and a scoring guide.

## Notes

- **Terminology** follows American spelling (`hematoxylin`, `esophagus`, `fiber`, `organized`), the convention of the histological literature.
- **The 100 original questions are not advertised as historical examination questions.** Specific inaccuracies were corrected and automated regressions added, but comprehensive scientific peer review remains outstanding. No topic-frequency statistics or guaranteed exam outcomes are claimed.
- **Disagreements between standard accounts are stated, not hidden.** Where authorities differ on a count or a range, the text gives both or says which one it is using. `COVERAGE.md` records the discrepancies found while checking.
- **Original schematic atlas and optional live-slide practice included:** nine labeled teaching schematics plus Appendix E's 23 practical observation challenges using institutional microscopic slide collections. No third-party photomicrographs are reproduced, and access to external resources is optional.
- **This is a teaching text, not a clinical manual.** It does not replace laboratory teaching or supervised clinical training.
- Study files in `deliverables/` (flashcards and the 100-question bank) are automatically regenerated from the manuscript and checked for synchronization during the publication workflow.
