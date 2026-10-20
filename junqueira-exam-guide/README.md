# Junqueira's Basic Histology — The Exam Companion

A 103-page condensed revision book built from **Junqueira's Basic Histology: Text & Atlas, 17th edition (Anthony L. Mescher)**, written for medical students preparing for examinations.

## Files

| File | Purpose |
|---|---|
| `Junqueira_Exam_Companion.pdf` | Print-ready A4 book with running heads, contents page, PDF bookmarks |
| `Junqueira_Exam_Companion.docx` | Editable Word version (same content, Word styles + TOC) |
| `Junqueira_Exam_Companion.html` | Phone/tablet reading copy, self-contained, no internet needed |
| `src/*.md` | The manuscript — one file per section, plain Markdown |
| `build.py` | Markdown → PDF (ReportLab), book design and layout |
| `build_docs.py` | Markdown → DOCX and HTML (pandoc) |

## Rebuilding

```bash
pip install --break-system-packages reportlab pypandoc_binary
python3 build.py         # PDF
python3 build_docs.py    # DOCX + HTML
```

Edit anything in `src/`, then re-run. Sections are concatenated in filename order, so a new file named `02c_whatever.md` drops in automatically.

## What is inside

- **Before you begin** — how to use the book, the Twelve Laws of Histology, exam technique, three study plans (6 weeks / 10 days / 48 hours)
- **Chapters 1–23** — each follows the textbook's own section sequence and titles, with **printed page ranges** under the chapter title, plus: the core idea, a **CLINICAL** correlation, a **MICRO** identification cue, and tips or mnemonics
- **Source map** — a table matching every chapter to its printed page range and to the page of the uploaded PDF part where it begins
- **Chapter 24** — the last-24-hours rapid review: organ-identification algorithm, ten master tables, 100 one-line facts, 25 distinctions that decide marks, the eight most common errors
- **Appendix A** — stains and what they prove
- **Appendix B** — the vocabulary examiners expect
- **Part VII** — 100 examination MCQs with explained answers and a scoring guide

## Notes

- Source book: Junqueira's Basic Histology: Text & Atlas, 17th ed., Anthony L. Mescher, McGraw Hill, 2024 (ISBN 978-1-264-93039-5). Chapter and section structure, page ranges and the edition's stated purpose are taken from the book itself.
- Chapters 1–19, and the pituitary, adrenal, pancreatic islet and thyroid sections of Chapter 20, have been checked against the uploaded PDF of the book. The remainder of Chapter 20 and Chapters 21–23 are written to the same chapter structure and will be aligned when the final part of the PDF is supplied.
- This is a study summary, not a replacement for the textbook or its atlas plates. The images that make histology memorable are in the book; this companion gives you the rules those images illustrate.
- Terminology follows the textbook's American spelling (`hematoxylin`, `esophagus`, `fiber`), so every term can be searched in the source.
