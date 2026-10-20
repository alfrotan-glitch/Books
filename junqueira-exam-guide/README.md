# Junqueira's Basic Histology — The Exam Companion

A **138-page** revision book built from **Junqueira's Basic Histology: Text & Atlas, 17th edition (Anthony L. Mescher, McGraw Hill, 2024)**, written for medical students preparing for examinations. Every chapter has been read against the uploaded PDF of the book, in all four parts.

## Files

| File | Purpose |
|---|---|
| `Junqueira_Exam_Companion.pdf` | Print-ready A4 book with running heads, contents page, PDF bookmarks |
| `Junqueira_Exam_Companion.docx` | Editable Word version (same content, Word styles) |
| `Junqueira_Exam_Companion.html` | Phone/tablet reading copy, self-contained, no internet needed |
| `deliverables/junqueira_flashcards.csv` | Anki-importable cards (`Front,Back,Tags,Type`) |
| `deliverables/junqueira_question_bank.csv` | 100 MCQs with answer, explanation, and why each distractor fails |
| `COVERAGE.md` | Chapter-by-chapter audit trail, plus the known discrepancies in the source |
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
- **Chapters 1–23** — each follows the textbook's own section sequence and titles, with **printed page ranges** under the chapter title, plus:
  - **learning objectives** and the **core idea**
  - the book's sections in order, condensed, with **comparison tables**
  - **CLINICAL**, **MICRO**, **TIP** and **MNEMONIC** callouts
  - **one-line answers** for the last night before an exam
  - **active-recall questions** with answers
  - one **exam-style MCQ** with the reason each distractor fails
  - **Plates to study** — six atlas figures per chapter, with the part and page where each figure sits
- **Source map** — every chapter matched to its printed page range and to the page of the uploaded PDF part where it begins
- **Chapter 24** — the last-24-hours rapid review: a concept map of the whole book, the organ-identification algorithm, ten master tables, 100 one-line facts, 25 distinctions that decide marks
- **Appendices** — stains and what they prove; the vocabulary examiners expect
- **Part VII** — 100 examination MCQs with explanations and a scoring guide
- **Appendix C** — the book's own stain appendix, with the chemistry and use of every stain in the atlas

## Notes

- Source book: Junqueira's Basic Histology: Text & Atlas, 17th ed., Anthony L. Mescher, McGraw Hill, 2024 (ISBN 978-1-264-93039-5).
- **All four uploaded parts have been read in full**: part 1 for Chapters 1–7, part 2 for Chapters 8–14, part 3 for the tail of Chapter 14 through the thyroid section of Chapter 20, and part 4 for the parathyroid and pineal sections of Chapter 20, Chapters 21–23, and Appendix A. The Source Map gives the exact starting page of every chapter.
- **No facts are invented and no past-paper claims are made.** The 100 MCQs were written for this guide in the style of the book's *Assess Your Knowledge* questions; they are not past examination questions, and no topic-frequency statistics are claimed.
- **Known source discrepancies are flagged rather than copied.** Chapter 22's Summary of Key Points reverses the hormones of the two lutein cell types (the body text, figure legend and end-of-chapter question all contradict it), and calls the zona pellucida glycoproteins "ZO proteins" where the body gives ZP1–ZP3. Both are documented in `COVERAGE.md` and in the chapter itself.
- **No source scans are reproduced**, because the atlas plates are copyrighted. The guide cites figure numbers, parts and pages so you can open the real image; any schematic in the guide is original.
- This is a study summary, not a replacement for the textbook or its atlas plates.
- Terminology follows the textbook's American spelling (`hematoxylin`, `esophagus`, `fiber`), so every term can be searched in the source.
