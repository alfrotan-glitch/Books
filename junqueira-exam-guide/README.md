# Basic Histology: A Learning Text

A self-contained course in microscopic anatomy in 24 chapters, for students of medicine, dentistry and the biomedical sciences. It teaches the cell, the four basic tissues, and the organ systems, and ends with a hundred-question practice examination. The book carries no images: it describes what to look for on a slide, how to tell one structure from its neighbour, and how each structure serves function.

The text is original. No images, plates, captions or extended passages from another publication are reproduced, and no page ranges, figure numbers or review questions point the reader to another book.

## Files

| File | Purpose |
|---|---|
| `Basic_Histology_Learning_Text.pdf` | Print-ready A4 book, 143 pages, running heads, contents page, PDF outline |
| `Basic_Histology_Learning_Text.docx` | Editable Word version (same content, Word styles) |
| `Basic_Histology_Learning_Text.html` | Phone/tablet reading copy, self-contained, no internet needed |
| `Basic_Histology_Learning_Text.epub` | EPUB 3, reflowable, navigable, for e-readers and phones |
| `src/*.md` | The manuscript — one file per section, plain Markdown |
| `build.py` | Markdown → PDF (ReportLab), book design and layout |
| `build_docs.py` | Markdown → DOCX and HTML (pandoc) |
| `build_epub.py` | Markdown → EPUB 3 (pandoc + generated cover) |
| `tools/validate_epub.py` | Structural EPUB validation (not EPUBCheck) |
| `COVERAGE.md` | Source ledger: what was read, what was checked, known discrepancies |
| `FINAL_REVIEW_REPORT.md` | Production record: verification evidence, hashes, limitations |

## Rebuilding

```bash
pip install --break-system-packages reportlab pypandoc_binary
python3 build.py         # PDF
python3 build_docs.py    # DOCX + HTML
python3 build_epub.py    # EPUB 3
python3 tools/validate_epub.py   # EPUB structural checks
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
