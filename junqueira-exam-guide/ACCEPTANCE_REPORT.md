# Acceptance report — Basic Histology: The Exam & Learning Companion

**Branch:** `arena/8f31a7ed-books`
**Previous release commit:** `5816334` (kept for comparison and revert)
**Decision:** **ACCEPT WITH EXPLICIT LIMITATIONS.** No claim is made that the book is scientifically perfect or publication-ready without further review.

## 1. Artefacts

| File | Detail | SHA-256 (first 16) |
|---|---|---|
| `Junqueira_Exam_Companion_FINAL.pdf` | 142 pp, A4 | `fc9cca6ffecde908` |
| `Junqueira_Exam_Companion_FINAL.epub` | EPUB 3, reflowable | `69f3d7e4542d72c4` |
| `Junqueira_Exam_Companion_FINAL.docx` | Editable manuscript | `cfb83dcccaf2f2ff` |
| `Junqueira_Exam_Companion_FINAL.html` | Self-contained reading copy | `736854a9c7e7a5e6` |
| `deliverables/junqueira_flashcards.csv` | 550 cards | rebuilt from source |
| `deliverables/junqueira_question_bank.csv` | 100 MCQs | rebuilt from source |

All four editions are generated from `src/*.md` by `build.py`, `build_docs.py` and `build_epub.py`; the decks come from `tools/make_study_decks.py` and `tools/make_question_bank.py`.

## 2. Corrections made in this pass

### Scientific

1. **TEM resolution (Chapter 1).** The chapter gave "about 3 nm" in two places and "0.2 nm" in two others. The textbook's value is **about 3 nm for routine biological sections**; the instrument's point resolution can approach 0.2 nm on ideal specimens. Both are now stated together everywhere the figure appears.
2. **Formalin concentration (Chapter 1).** The text repeated the book's compressed phrase "a buffered isotonic solution of 37% formaldehyde". A clarifying note now separates the **37–40% stock** from the working fixative, **10% formalin ≈ 3.7–4% formaldehyde**, buffered to pH 7.2–7.4.
3. **Nucleosome (Chapter 3).** "About 150 bp per turn" was wrong; it is now **about 150 bp of DNA per nucleosome (about 1.75 turns around the histone octamer)**.
4. **Nuclear pores (Chapter 3).** Added the textbook's figures: **~100 nm wide, ~34 nucleoporins, up to ~1,000 macromolecules per second**.
5. **Basophilia/eosinophilia (front matter).** The absolute rule "cells that make protein look basophilic…" is now qualified: staining reflects nucleic acid versus protein content, with mucin and lipid as poor-staining exceptions.
6. **Apoptosis versus necrosis (Chapter 3).** Added the caveat that the contrast is a teaching simplification (necroptosis, pyroptosis, and uncleared apoptotic cells can inflame tissue).
7. **Cell-cycle durations (Chapter 3).** Labelled as values for a rapidly dividing cultured cell, not adult tissues; p53 mutation frequency qualified as "commonly cited as about half".
8. **Regeneration (Chapter 3) and skeletal disease (Chapter 8).** "Cannot regenerate" and "every skeletal disease is a failure…" softened to match the evidence.

### Editorial

9. **Examiner/mark claims removed at 24 sites**, including "three questions answer 80% of slide questions", "ten headings, ten marks", "an examiner marking 200 scripts", "examiners choose images that contain one", "ten phrases that lose marks", "Two marks are lost repeatedly", "Confessions of the examiner", "The Vocabulary Examiners Expect", "Functional numbers that examiners love", and "Twenty-five distinctions that decide marks". Where the advice was useful it was rewritten neutrally (for example, the ten errors list is now "Ten common errors").
10. **Study-plan arithmetic.** "One part per week for six weeks" did not match seven parts; the plan now runs Parts I–V over the weeks and uses Part VI and Part VII in the final week.
11. **Part count.** "The part numbers refer to the five parts of this book" corrected to seven.
12. **Structure claim.** "How each chapter is built" limited to the 23 chapters of Parts I–V, which is what actually carry those blocks.
13. **Plates to study.** All **136** figure references now carry the **textbook's own caption subject** (verified against the figure captions extracted from the four parts), and the instruction is a self-test: cover the caption, state what the figure shows and the feature that identifies it.

### Question bank

14. **Q54** stem changed from singular to plural ("Which organs lack afferent lymphatic vessels?"), matching its key (thymus and spleen).
15. **Q88** distractor C ("simple squamous") was arguably correct for an inactive follicle, since the explanation itself says cells range from squamous to columnar. C is now "transitional epithelium", and the trap note was rewritten.
16. All 100 items re-checked: four distinct options each, one key, valid letter, and no trap paragraph that names the key as wrong (**0 defects found**).

## 3. Checks run

| Check | Method | Result |
|---|---|---|
| PDF page total | Text extraction of the built file | 142 pp — **PASS** |
| Blank pages | Per-page character count | 0 blank — **PASS** |
| Contents accuracy | TOC entries matched to headings on their printed pages | 42/42 — **PASS** |
| Chapter/part references | All `Chapter n`, `Part n`, `Appendix x` references resolved | all valid — **PASS** |
| Table integrity | Column count of every row in all Markdown tables | 0 mismatches — **PASS** |
| MCQ structure | Parser over all 100 items | 100 questions, 4 options, 0 duplicate options, 0 invalid keys — **PASS** |
| MCQ key vs explanation | Trap paragraphs scanned for the key letter | 0 contradictions — **PASS** |
| Flashcard integrity | Duplicate fronts, tag set | 550 cards, 0 duplicates — **PASS** |
| Cross-format consistency | Same source; spot strings present in PDF/DOCX/HTML/EPUB | **PASS** |
| Editorial residue | Regex sweep of all four rendered formats | 0 hits — **PASS** |
| EPUB structure | `tools/validate_epub.py` (OCF, OPF, nav, XHTML, links, images) | 0 errors, 0 warnings — **PASS** |
| EPUBCheck | Java runtime required | **NOT RUN** (Java not installed) |
| Visual inspection | Rendered pages 11, 16, 135 of the final PDF | inspected (fixation table, plates list, MCQ layout) |

## 4. Limitations

- **Thirty pages of the source PDFs have no text layer** (full-page plates and covers). They were not individually inspected; where a figure sits on one, the book cites the figure number and its caption rather than describing the plate.
- **No atlas images are reproduced.** All figures are referenced, not copied.
- **The 100 MCQs are original** teaching items, not past papers; no frequency or probability claim is made anywhere in the text.
- **The EPUB was validated structurally, not read in a commercial reader**, and EPUBCheck itself could not be run.
- **No external peer or medical-board review** has been performed. Statements were checked against the assigned textbook and against standard histology; residual errors remain possible.
- **Supplementary material** (a small number of standard physiology values and clinical terms absent from the textbook) is marked in the text; it is not attributed to the book.

## 5. Decision

**ACCEPT WITH EXPLICIT LIMITATIONS.** The defects identified in the brief were located in the manuscript, corrected at source, and the four editions plus both deck files were rebuilt and re-checked. The remaining limitations are stated above rather than concealed.
