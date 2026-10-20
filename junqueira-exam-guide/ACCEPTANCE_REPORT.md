# Acceptance report — Basic Histology: The Exam & Learning Companion

**Reviewed version:** branch `arena/8f31a7ed-books`, commit `d137690`
**Decision:** **ACCEPT WITH EXPLICIT LIMITATIONS** (see §7). No claim is made that all errors have been eliminated.

## 1. What was reviewed

| Artefact | Detail |
|---|---|
| `Junqueira_Exam_Companion_FINAL.pdf` | 142 pp, A4, 509,420 B, SHA-256 `0143333b…` |
| `Junqueira_Exam_Companion_FINAL.docx` | Pandoc build from the same source (`build_docs.py`) |
| `Junqueira_Exam_Companion_FINAL.html` | Same source, self-contained reading copy |
| `Junqueira_Exam_Companion_FINAL.epub` | EPUB 3, 214,404 B, SHA-256 `fb4ebc54…`, structurally validated |
| `deliverables/junqueira_flashcards.csv` | 550 cards, `Front,Back,Tags,Type` |
| `deliverables/junqueira_question_bank.csv` | 100 MCQs with answer, explanation and distractor analysis |
| `src/*.md` | The single manuscript from which all four editions are built |

The textbook is *Junqueira's Basic Histology: Text & Atlas*, 17th edition (Mescher, McGraw Hill, 2024; ISBN 978-1-26-493039-5), read from the four PDF parts supplied for this project.

## 2. Checks performed and results

| Check | Method | Result |
|---|---|---|
| PDF page total | PDF text extraction (`pypdfium2`) | 142 pp |
| Blank pages | Character count per page | 0 blank; 7 intentional part-divider pages |
| Contents accuracy | Every TOC entry matched to the heading on its printed page | 42/42 correct (3 part titles wrap across lines and were matched by their first line) |
| Figure citations | Each `Fig. n–m` matched to the figure number on the cited textbook page | 136/136 found |
| Table cells | Every Markdown table row checked for the header's column count | 0 mismatches |
| Symbol encoding | Counts of `µ`, `→`, `β`, `α`, `–`, `×` in the rendered PDF | All present, no mojibake |
| MCQ key distribution | Count of A/B/C/D in the question bank | 25/25/25/25 |
| MCQ completeness | Every row has 4 options, an answer letter, an explanation and a distractor note | 100/100 |
| Flashcard integrity | Duplicate-front check, tag set | 550 cards, 0 duplicates, 52 tags |
| DOCX integrity | `word/document.xml` well-formed; table count | 73 tables, parses |
| HTML integrity | Tag balance, table count, no external assets | 73 tables, no remote resources |
| EPUB structure | `tools/validate_epub.py`: OCF, OPF, nav, XHTML, links, images | PASS (0 errors, 0 warnings) |

## 3. Defects found and corrected

| # | Defect | Fix |
|---|---|---|
| 1 | MCQ stems ran into option A on the printed page (100 items) | Blank line inserted between stem and options in `src/07_mcq.md` |
| 2 | Table 12–1 was a single merged paragraph instead of a table | Rebuilt as a five-column table |
| 3 | Platelet values disagreed with the book (2–3 µm) | Corrected to **2–4 µm**, with count 150,000–400,000/µL and ~10-day lifespan |
| 4 | Thin ascending limb of the loop of Henle had no function stated | Added passive NaCl reabsorption, low water permeability |
| 5 | Microvillus core proteins and urothelial plaques imprecise | Aligned to the book: actin-bundling proteins (villin, fimbrin); uroplakin plaques |
| 6 | Chapter 4 claimed "three types of pneumocytes" | Corrected to type I and type II |
| 7 | Neutrophil diameter given as 12 µm | Corrected to 10–14 µm |
| 8 | Cutaneous receptors omitted Ruffini and Krause end bulbs | Added with locations and adequate stimuli |
| 9 | Cover carried an unearned series line ("Medical Exam Revision Series") | Replaced with an independent-companion identity and rights note |
| 10 | Appendix C duplicated Appendix A's stain table | Merged into Appendix A; TOC rebuilt on one page |

Earlier in the same review round: the cover's bold-leak in running heads, the 44 %/45 % haematocrit reconciliation, the >1 % regulatory-protein and ~1 % electrolyte/nutrient shares of plasma, and the platelet section were also corrected.

## 4. Text and science verification

* **Chapters 15–23 were audited against the extracted text of parts 3 and 4** — chapter summaries, comparison tables and a targeted probe of every number that was changed. Confirmed in the textbook text: platelets 2–4 µm, 150,000–400,000/µL, ~10-day lifespan; plasma shares in Table 12–1; passive NaCl reabsorption by the thin ascending limb; villin/fimbrin in the microvillus core and uroplakin plaques on umbrella cells; filtration slit pores 25–30 nm across a 330 nm basal lamina; 600,000 oocytes at puberty and 20–35 µm granulosa lutein cells; 35-mm cochlea, ~12,000 outer hair cells, 150 mM K⁺ endolymph and 4.6 million cones.
* **Numbers audit:** 59 uses of `µ`, 17 of `β`, 15 of `α`, 18 of `×` — all verified in context. The guide's own supplementary standard-physiology numbers (blood volume, GFR, bladder volumes) are identified as context in the front matter, not attributed to the book.
* **Known errors in the source textbook** are flagged rather than propagated: the Ch 22 summary's reversal of granulosa/theca lutein steroid products (main text correct), "zone occludens" used for zona pellucida proteins, the "oligospermia >2 mL" volume criterion, and the ~2-month spermatogenesis claim.

## 5. Visual inspection actually performed

Pages rendered to images and inspected: cover (1), title page (2), contents (3), a dense leukocyte table (59), the Chapter 15 opener (73), an MCQ page (133) and the closing page (142). The cover, title page, contents and MCQ layout were checked again after their redesign.

No image or plate from the textbook is reproduced, so there is no image-rights exposure and no mislabelled figure.

## 6. Explicit limitations

1. **Thirty pages of the source PDFs carry no extractable text** (full-page plates and covers). Every page that carried text used in the guide was machine-read; the plate pages were not all inspected individually, and where a figure sits on one of them the guide cites the figure number rather than describing the plate.
2. **The guide is a summary, not the textbook.** It follows the book's section sequence and page ranges, but it cannot replace the atlas plates or the book's own figures.
3. **MCQs are original** teaching items written for this companion; they are not past examination papers, and no frequency or "high-yield" claim rests on real exam data.
4. **EPUB validation is structural** (OCF container, OPF metadata, nav document, XHTML well-formedness, internal links, image resources, absence of external dependencies). EPUBCheck itself was not run: it requires Java, which is not installed in this environment. The EPUB was not opened in a commercial reading system here.
5. **No professional copy-editing or medical-board review** has been performed. The text was checked against the source and against standard histology; residual errors remain possible.
6. **Typography** uses DejaVu Sans / DejaVu Serif, embedded in the PDF. The design was checked on rendered pages, not audited with a colour-contrast tool.

## 7. Decision

**ACCEPT WITH EXPLICIT LIMITATIONS.** The artefacts are internally consistent, the checks in §2 pass, and the defects in §3 are corrected in the delivered files. The limitations in §6 are inherent to a single-author summary built from an image-bearing PDF, and they are stated here rather than concealed.
