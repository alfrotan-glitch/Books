# Basic Histology: A Learning Text

A self-contained, **editorial-candidate** course in microscopic anatomy in 24 chapters, for students of medicine, dentistry and the biomedical sciences. It teaches the cell, the four basic tissues, and the organ systems, and ends with a hundred-question practice examination. The book carries no images: it describes what to look for on a slide, how to tell one structure from its neighbour, and how each structure serves function.

The text is original. No images, plates, captions or extended passages from another publication are reproduced, and no page ranges, figure numbers or review questions point the reader to another book.

## Latest build and publication status

**Use the files attached to the most recent successful [Build and validate histology book workflow](https://github.com/alfrotan-glitch/Books/actions/workflows/histology-book.yml).** GitHub's tracked `Basic_Histology_Learning_Text.*` files may predate subsequent manuscript edits; a workflow artifact is tied to its source commit. The artifact bundles all four formats and `publication-manifest.json` with their SHA-256 hashes.

The latest fully observed structural build before this README update was 149 PDF pages, 44 PDF bookmarks, 2,139 DOCX paragraphs, 79 DOCX tables, and EPUBCheck v5.4.0 with zero errors or warnings. Check the new workflow run for later revisions.

**Status: editorial candidate, not independently medically certified or fully print-proofed.** An automated green build does not replace an end-to-end specialist review, clearance of any third-party content, physical printing/visual inspection, or e-reader/Word/browser acceptance. See [RELEASE_VERIFICATION.md](RELEASE_VERIFICATION.md).

## Files

| File | Purpose |
|---|---|
| `Basic_Histology_Learning_Text.pdf` | A4 book with running heads, contents and PDF outline; **latest CI build: 149 pages** (print proof still required) |
| `Basic_Histology_Learning_Text.docx` | Editable Word version (same content, Word styles) |
| `Basic_Histology_Learning_Text.html` | Phone/tablet reading copy, self-contained, no internet needed |
| `Basic_Histology_Learning_Text.epub` | EPUB 3, reflowable, navigable, for e-readers and phones |
| `src/*.md` | The manuscript — one file per section, plain Markdown |
| `build.py` | Markdown → PDF (ReportLab), book design and layout |
| `build_docs.py` | Markdown → DOCX and HTML (pandoc) |
| `build_epub.py` | Markdown → EPUB 3 (pandoc + generated cover) |
| `tools/validate_epub.py` | Additional internal EPUB structural checks |
| `tools/release_smoke_test.py` | Automated PDF, DOCX, EPUB, HTML structural and geometry checks |
| `tools/write_release_manifest.py` | Creates per-format SHA-256 release manifest |
| `RELEASE_VERIFICATION.md` | Explicit, evidence-based final-publication acceptance criteria |
| `COVERAGE.md` | Source ledger: what was read, what was checked, known discrepancies |
| `FINAL_REVIEW_REPORT.md` | Production record: verification evidence, hashes, limitations |

## Rebuilding

```bash
python -m pip install reportlab pypandoc_binary python-docx pymupdf
python3 build.py         # PDF
python3 build_docs.py    # DOCX + HTML
python3 build_epub.py    # EPUB 3
python3 tools/validate_epub.py   # EPUB structural checks
python3 tools/release_smoke_test.py   # Four-format smoke tests
python3 tools/write_release_manifest.py   # SHA-256 provenance file
```

Edit anything in `src/`, then re-run all four. Sections are concatenated in filename order, so a new file named `02c_whatever.md` drops in automatically.

## What is inside

- **Before you begin** — how the book works, how to study (six-week, ten-day and 48-hour plans), the Twelve Laws of Histology, exam technique, a chapter guide, and a note on sources.
- **Chapters 1–23** — each has learning objectives, a core idea, the explanation in sections, structure–function reasoning, comparison tables, clinical correlates, common misconceptions, a summary, active-recall questions, one exam-style question with a worked answer, and a practical identification task.
- **Chapter 24** — the last-24-hours rapid review: a concept map of the subject, the organ-identification algorithm, ten master tables, 100 one-line facts and 25 distinctions that decide marks.
- **Appendices** — A: stains and what they prove, with the chemistry behind each; B: the vocabulary examiners expect; C: sources and further reading, with an honest account of how the text was checked and what that checking does not cover.
- **Part VII** — 100 examination questions with explained answers and a scoring guide.

## Notes

- **Terminology** follows American spelling (`hematoxylin`, `esophagus`, `fiber`, `organized`), the convention of the histological literature.
- **No facts are invented and no past-paper claims are made.** The 100 questions were written for this book in the style of a standard histology examination; they are not past examination questions, and no topic-frequency statistics are claimed.
- **Disagreements between standard accounts are stated, not hidden.** Where authorities differ on a count or a range, the text gives both or says which one it is using. `COVERAGE.md` records the discrepancies found while checking.
- **No histological images are reproduced.** Descriptions replace pictures; the reader is expected to take them to a microscope or a slide collection.
- **This is a teaching text, not a clinical manual.** It does not replace laboratory teaching or supervised clinical training.
- Ancillary study files in `deliverables/` (flashcards, question-bank CSV) are not part of the book and are not maintained as part of it.
