# Acceptance report — Junqueira's Basic Histology: The Exam Companion

**Review date:** 20 October 2026
**Reviewed commit:** `f85d8d4` (branch `arena/8f31a7ed-books`)
**Source:** *Junqueira's Basic Histology: Text & Atlas*, 17th ed., Anthony L. Mescher, McGraw Hill, 2024 (ISBN 978-1-26-493039-5), read from the four uploaded PDF parts (217 + 217 + 217 + 216 pages).

## 1. Scope of the review

| Requirement | How it was tested |
|---|---|
| Deep review of three chapters — foundational, complex tissue/system, organ system | **Ch 4** (epithelial tissue) and **Ch 12** (blood) and **Ch 19** (urinary system) read line by line against the extracted source text; every factual claim, table cell and figure citation checked |
| Student can follow without unexplained terminology | Every technical term in those chapters either defined at first use or cross-referenced to the chapter that defines it; obsolete eponyms explained |
| Instructor can teach without reconstructing missing explanations | Each chapter has objectives, a core-idea paragraph, the book's section order, comparison tables, three or four teaching callouts, one-line answers, active recall and a worked exam question |
| PDF rendering, DOCX/HTML comparison, tables, page references, readability, navigation | PDF text layer and page images; 24 contents entries compared with 24 rendered chapter openers; 74 tables counted in each of the three formats; spot-checked content in DOCX and HTML |
| Reconcile discrepancies and document the unverifiable | Section 4 below, and the *Known discrepancies* section of `COVERAGE.md` |
| Validate all flashcards and MCQs | 550 cards and 100 items checked structurally and by sampling against the chapter text |

Chapters 15–20 (the part-3 block that had not been reviewed in depth before) were also re-checked fact by fact during this review, because that is where most of the corrections were found.

## 2. Evidence from the final artifacts

The files below are the exact files produced by the final build (`build.py`, `build_docs.py`, `tools/make_study_decks.py`, `tools/make_question_bank.py`).

| Artifact | Size | SHA-256 (first 16) | Check |
|---|---|---|---|
| `Junqueira_Exam_Companion.pdf` | 527,191 B | `f1705984b7ddcdbd` | **140 pages**, 0 blank pages, 24/24 contents entries match their chapter openers |
| `Junqueira_Exam_Companion.docx` | 177,921 B | `93f3acc670032868` | Valid OOXML archive; **74 tables**; heading styles and numbering intact |
| `Junqueira_Exam_Companion.html` | 442,012 B | `a7dfec989324637e` | Self-contained, **74 tables**, `lang="en-US"`, no external assets |
| `deliverables/junqueira_flashcards.csv` | 550 rows | `6543a89479977262` | 550 cards, **0 duplicate fronts**, 0 empty or over-long backs |
| `deliverables/junqueira_question_bank.csv` | 31,312 B | `53f009b28ecae259` | 100 items, 4 distinct options each, key **25 A / 25 B / 25 C / 25 D**, explanation and distractor note on every item |

Other automated checks:

- **Figure citations:** all **136** `Fig. n–m` references were matched to the figure number printed on the cited part page, and the caption keywords were matched against the caption text on that page — **136/136 correct**, 0 mismatches.
- **Numbers:** every numeral in the manuscript was searched in the source text; all are traceable to the book (the only non-book numbers are the guide's own page numbers).
- **Tables:** row/column counts were checked in every Markdown table — 0 malformed rows; key tables were rendered and inspected in the PDF.
- **Page references:** the 24 chapter openers were located in the rendered PDF and compared with the contents page — **0 mismatches**.
- **Known-error probes in the decks:** 0 hits for the flagged book errors (lutein/theca reversal, "ZO" for ZP, "oligospermia > 2 mL", the 74-day spermatogenesis interval).

## 3. Defects found and fixed

Ten genuine defects were found in the review itself, and five more in the post-acceptance pass described in section 3a. Each was fixed in the manuscript, and every affected output was rebuilt and re-checked.

| # | Chapter | Defect | Fix |
|---|---|---|---|
| 1 | 12 | Platelets given as **2–3 µm**; book gives **2–4 µm** | Corrected, with count (150,000–400,000/µL) and lifespan (~10 days) added |
| 2 | 12 | Table 12–1 merged the "other solutes" line and gave regulatory proteins as `<1%` | Table rebuilt; regulatory proteins **>1%**, electrolytes and nutrients **~1%** |
| 3 | 12 | Hemostasis described as if the chapter gave the four-step sequence | Sequence retained but explicitly labelled as standard physiology not set out in the chapter |
| 4 | 15 | Enterocyte absorption described as **transcytosis** | Replaced with the book's mechanism (glycocalyx hydrolysis, then brush-border absorption) |
| 5 | 17 | Alveolar type I/II shares invented as **95%/5%**; alveolar diameter given as 200 µm | Replaced with the book's wording ("almost the entire surface" / "a small part of each alveolus"); unsupported diameter removed |
| 6 | 17 | "Four main types" of lung cancer | Reduced to the three the book names |
| 7 | 18 | Skin repair built around first/second intention and burns, which the chapter does not describe | Rewritten to the book's five-stage sequence; clinical terminology kept but labelled **supplementary** |
| 8 | 18 | Clinical box contained Munro microabscesses and Breslow thickness, neither in the book | Replaced with the chapter's own examples (psoriasis, skin-cancer statistics, melanoma, Merkel cell carcinoma, albinism, vitiligo, blistering diseases, CF sweat) |
| 9 | 19 | Kidney size **12 × 6 × 2.5 cm** presented as book content | Removed — the chapter gives no dimensions |
| 10 | 19–20 | Clinical boxes contained Kimmelstiel–Wilson nodules, renal-cell carcinoma, Hashimoto thyroiditis, Hürthle cells, Cushing and Conn syndromes — none in the book; and islet β/α distribution was described as central/peripheral (rodent pattern) | Clinical boxes replaced with the book's own clinical applications; islet text corrected to "scattered in human islets" |

Smaller corrections: `Synthesises`, `neighbours` and `favoured` normalised to the book's American spelling; the DOCX/HTML language tag changed from `en-GB` to `en-US`; a duplicated cortex-blood-flow line removed; the Chapter 19 one-line list aligned with the corrected table.


## 3a. Post-acceptance defect pass (frozen version)

After the version was frozen, a targeted pass looked only for material defects: contradictions between chapters and the rapid-review list, and ambiguous or wrongly explained MCQs. It found five. Each was corrected at the exact location below; nothing else was changed.

| Location | Current text (before) | Evidence | Correction |
|---|---|---|---|
| **Ch 24, Rapid Review — 100 one-line facts, item 81 (PDF p. 119)** | "Platelets = 2–3 µm, from megakaryocytes." | Chapter 12 and the book give **2–4 µm**; the line contradicted the corrected chapter | "Platelets = 2–4 µm, from megakaryocytes." |
| **Part VII, MCQ 23, option C (PDF p. 126)** | Option C "Articular hyaline" to the question "Which cartilage type lacks a perichondrium?", with the answer explanation "C is hyaline and does have perichondrium (though it is thin)" | Articular hyaline cartilage **lacks** a perichondrium — the book's own Chapter 7 review question asks "How does articular cartilage differ from most other hyaline cartilage? … It lacks a perichondrium." The item therefore had two correct answers (B and C), and the explanation was wrong | Option C changed to "Tracheal hyaline"; explanation changed to "C is hyaline and is covered by perichondrium." B remains the single correct answer |
| **Part VII, MCQ 59, stem (PDF p. 129)** | "Neonatal hemopoiesis occurs mainly in the:" with answer "Liver and spleen" | The book places liver/spleen hemopoiesis in the **second trimester**; by the neonatal period the marrow is the main site. The stem contradicted its own explanation | Stem changed to "During the second trimester, hemopoiesis occurs mainly in the:" |
| **Part VII, MCQ 61, explanation (PDF p. 135)** | "C and D contain the submucosal plexus." | Meissner's submucosal plexus lies in the **submucosa only** (option D); option C is the mucosa | "D contains the submucosal (Meissner) plexus. C is the mucosa; B is the outer covering." |
| **Part VII, MCQ 80, explanation (PDF p. 136)** | "A and B contain Meissner corpuscles." | Meissner corpuscles sit in the **dermal papillae** (option B); the basal epidermis (option A) is supplied by free nerve endings | "B contains Meissner corpuscles; A is supplied by free nerve endings. D has no corpuscles." |

No MCQ answer key changed: the bank remains 100 items with 25 A / 25 B / 25 C / 25 D, and every item still has four distinct options and a complete explanation. All 100 keys were re-read against the source during this pass and no further wrong key was found.

## 4. Without overstating the evidence

- **30 of the 867 source pages carry no text layer** (full-page plates and cover pages: part 1 pages 1–3, 20, 29, 46, 76, 79, 86, 142, 166, 174, 203; part 2 pages 60, 69, 72, 90, 158, 217; part 3 pages 42, 50, 80, 82, 127, 166, 180, 198; part 4 pages 44, 67, 71). **These pages were not all visually reviewed, and this report does not claim that they were.** No factual statement in the guide depends on them; where a figure sits on one of them, the guide cites the figure number instead of describing the figure.
- The one page of this group whose content was needed for a correction (part 2, page 158, the printed plasma table) was rendered and read directly in this review; the corrected Table 12–1 matches it.
- **No atlas plates are reproduced** (copyright). The guide cites figure numbers, part and page, so the reader opens the real image.
- **The 100 MCQs are original**, written in the style of the book's *Assess Your Knowledge* questions. They are not past examination papers, and no claim is made about examination frequency.
- **The book's own errors are flagged, not copied** — the Chapter 22 lutein/theca reversal, "ZO proteins" for ZP1–ZP3, and the semen-volume definition of oligospermia. Each is documented in the chapter and in `COVERAGE.md`.
- The guide is a **study companion**, not a substitute for the textbook or its atlas.

## 5. Decision

Every acceptance check that can be run against the real files passes: 140 pages with no blank or broken page, 24/24 contents entries correct, 136/136 figure citations correct, 74 tables consistent across PDF, DOCX and HTML, 550 cards with no duplicates or empty backs, and 100 MCQs with four distinct options, a single key and a complete explanation.

The limitations in section 4 are real but bounded, and they are stated in the guide itself rather than hidden.

**ACCEPT WITH EXPLICIT LIMITATIONS** — because the deliverables meet the agreed scope and every check run on the actual files passes, while (i) 30 source pages without a text layer were not all visually reviewed and the guide makes no claim that depends on them, (ii) no copyrighted atlas plates are reproduced, (iii) the MCQs are original rather than past-paper items, and (iv) the book's own inconsistencies are flagged rather than silently corrected.
