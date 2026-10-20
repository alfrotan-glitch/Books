# Final release acceptance — Basic Histology: The Exam & Learning Companion

**Date of pass:** 20 October 2026
**Branch:** `arena/8f31a7ed-books`
**Candidate examined:** `71938c8` ("Final content cleanup and scientific QA")
**Release commit produced by this pass:** `666cccf` (sources and artefacts), plus a follow-up commit containing this report
**Recommendation:** **ACCEPT WITH EXPLICIT LIMITATIONS** — see §9.

---

## 1. Release identity and checksums

All artefacts in this section were rebuilt from `666cccf` and are the files committed with it.

| Artefact | Bytes | SHA-256 |
|---|---|---|
| `Junqueira_Exam_Companion_FINAL.pdf` | 511,206 | `7b7996b53d655d7b29c71f2a6f2fb5c1082c4c4db281cee2ffd715f39ec69922` |
| `Junqueira_Exam_Companion_FINAL.epub` | 215,095 | `3f28fa3b936799b20712eca3daeae7ef79f083bb45d42672bb6699a438722aa2` |
| `Junqueira_Exam_Companion_FINAL.docx` | 177,325 | `9b2cf0b72da6a5df412a9ab1e7950bae72d3119d5ad2014b4ff6607b5dee3fb2` |
| `Junqueira_Exam_Companion_FINAL.html` | 442,414 | `367ab58b458260993818e06cf27aea009be34af4fcd5c0ffee241984b1109145` |
| `deliverables/junqueira_flashcards.csv` | 70,440 | `0d33512669193a36fc8d895397883f0c34fe9cdb0ad31925214fdab3bb151a57` |
| `deliverables/junqueira_question_bank.csv` | 31,218 | `7790a51397fff690e029123606a9c5217696e196ffb9b8a07c45f17fd6d78628` |

PDF: 142 pages, 49,285 extracted words, text SHA-256 prefix `c58b0891d21808db`. All artefacts carry the same build timestamp (`2026-10-20T16:21`), i.e. they come from one build run of one revision. `5816334` and `d137690` remain in history and untouched.

**Provenance:** every reader-facing file is generated from `src/*.md` by `build.py` (PDF), `build_docs.py` (DOCX + HTML) and `build_epub.py` (EPUB); the two CSVs by `tools/make_study_decks.py` and `tools/make_question_bank.py`. In the previous pass a clean rebuild reproduced the committed PDF's extracted text byte-for-byte (142 pp, text hash `49b60102aaf4e99c`); after this pass's edits the text hash is `c58b0891d21808db`, and a second full build in this pass reproduced 142 pages with no blank pages and no layout overflow.

---

## 2. What was actually read in this pass

**Companion text, read in full:**

- Chapter 4, 5 and 6 (`src/02a_basic_tissues.md`, 378 lines)
- Chapters 7–10 (`src/02b_basic_tissues.md`, 476 lines)
- Chapters 11–14 (`src/03_transport.md`, 500 lines)
- Chapters 15–18 (`src/04_viscera.md`, 568 lines)
- Chapters 19–23 (`src/05_systems.md`, 710 lines)
- Appendix A and Appendix B (`src/06_rapid.md`)
- Front matter (`src/00_front.md`) — study plans, page guide, block definitions

**Textbook text, read in full or near-full:**

- Every *Summary of Key Points* box of Chapters 4–23 (all are short, self-contained statements of the examinable content and were used as the checklist against which the companion was audited)
- The whole of the textbook Appendix ("Light Microscopy Stains", part 4 pp. 138–139)
- The chapter-opening and closing pages of Chapters 15–23, the full thyroid section of Chapter 20, and the body text of every passage in which the companion makes a numeric or mechanistic claim (checked by targeted search of the extracted text, then read in context)

**Not re-read line by line in this pass:** Chapters 1–3 of the companion and Chapter 24 (the rapid-review chapter). They were read in the previous pass (`71938c8`) and were sampled here through the rendered PDF and the automated checks. The 550 flashcards and the 100 MCQ explanations were **not** re-read individually in this pass; they were checked structurally (counts, duplicates, blanks, key balance, option completeness) and one MCQ explanation was corrected (§4.1).

---

## 3. Chapter-by-chapter checklist

| Ch | Title | Companion reviewed | Book facts checked | Corrections this pass |
|---|---|---|---|---|
| 1 | Histology & Its Methods | previous pass; sampled | — | — |
| 2 | The Cytoplasm | previous pass; sampled | — | — |
| 3 | The Nucleus | previous pass; sampled | — | — |
| 4 | Epithelial Tissue | full | polarity, junctions, types, glands | 0 |
| 5 | Connective Tissue | full | cells, fibres, matrix, types | 1 (Langerhans) |
| 6 | Adipose Tissue | full | white/brown, uncoupling, hormones | 0 |
| 7 | Cartilage | full | types, matrix, growth, repair | 1 (broken sentence) |
| 8 | Bone | full | cells, matrix, ossification, remodelling | 0 |
| 9 | Nerve Tissue | full | neurons, glia, BBB, regeneration | 0 |
| 10 | Muscle Tissue | full | sarcomere, triads/diads, types | 0 |
| 11 | Circulatory System | full | tunics, capillary types, lymphatics | 0 |
| 12 | Blood | full | plasma shares, cell sizes, haemostasis | 3 (heme, 4 steps, cytokines) |
| 13 | Hemopoiesis | full | lineages, growth factors, M:E ratio | 1 (M:E wording) |
| 14 | Immune System | full | MHC, T/B cells, thymus, node, spleen | 2 (tonsil capsule, iron/heme) |
| 15 | Digestive Tract | full | layers, papillae, enamel/dentin, stomach, bowel | 3 (mucous neck, jejunum, stem-cell wording) |
| 16 | Digestive Organs | full | salivary glands, pancreas, liver, gallbladder | 0 |
| 17 | Respiratory System | full | airway sequence, alveolar cells, barrier | 0 |
| 18 | Skin | full | epidermis, receptors, glands, repair | 2 (Ruffini, nail growth) |
| 19 | Urinary System | full | nephron, JGA, urothelium, urethra | 2 (hilum sentence, pyramid count) |
| 20 | Endocrine Glands | full | pituitary, adrenal, islets, thyroid, parathyroid, pineal | 0 |
| 21 | Male Reproductive | full | spermatogenesis, ducts, glands, erection | 0 |
| 22 | Female Reproductive | full | follicles, corpus luteum, uterus, placenta, breast | 2 (perivitelline, summary reversal) |
| 23 | Eye & Ear | full | tunics, aqueous, retina, cochlea, vestibular | 0 |
| App. A | Stains | full | every stain and its reported colour | 0 |
| App. B | Vocabulary | full | definitions | 0 |
| Ch. 24 | Rapid review | previous pass; sampled | spot-checks only | 0 |

---

## 4. Material corrections

### 4.1 Made in this pass (all in `src/`, all rebuilt into every format)

1. **Chapter 5, "Cells of Connective Tissue" table** (`src/02a_basic_tissues.md`). Langerhans cells were listed as a macrophage variant. They are dendritic antigen-presenting cells of the epidermis, not macrophages; the entry was removed and the osteoclast was annotated "(a fused macrophage)", which is the cell the book describes as a syncytium of fused monocytes.
2. **Chapter 7, core idea** (`src/02b_basic_tissues.md`). A sentence fragment ("…produce its outer fibrous layer. *that structurally supports*…") was repaired; no content change.
3. **Chapter 12, haemoglobin** (`src/03_transport.md`). "hem group" corrected to "heme group" (and "hem converted" to "heme converted") in both places.
4. **Chapter 12, active recall** (`src/03_transport.md`). The question asked for "three steps of hemostasis" while the chapter body, correctly, gives four. Question and answer now say four, including retraction and repair.
5. **Chapter 12, cytokines** (`src/03_transport.md`). "their Storm-like excess" replaced with plain wording ("excessive release produces a cytokine storm").
6. **Chapter 13, left shift** (`src/03_transport.md`). The sentence contradicted itself by calling band cells "metamyelocytes"; rewritten so that band (stab) cells are the immature neutrophils released early.
7. **MCQ 50 explanation** (`src/07_mcq.md`). It described the 2:1–4:1 M:E ratio as a supplementary figure "not stated" in the chapter, but Chapter 13 does state it. The explanation now attributes it correctly.
8. **Chapter 14, organ table** (`src/03_transport.md`). The tonsil was given "no capsule"; it has a partial capsule (the palatine tonsil is covered by epithelium and a hemicapsule), so the entry now reads "Partial". The spleen/thymus/lymph-node entries were checked and left unchanged.
9. **Chapter 14, iron recycling** (`src/03_transport.md`). "Iron-free heme binds hemopexin or is converted to bilirubin" conflated two steps; now: heme is carried by hemopexin and degraded to bilirubin, which is excreted in bile.
10. **Chapter 15, gastric glands table** (`src/04_viscera.md`). The mucous neck cell was described as an "immature precursor that migrates up into the pits"; the book describes it as a secretory cell of the neck and places the stem cells in the neck region. Both entries now say that.
11. **Chapter 15, small-intestine table** (`src/04_viscera.md`). "Peyer's patches sparse or absent" in the jejunum replaced by the safer, book-supported statement that they belong to the ileum.
12. **Chapter 15, stem cells** (`src/04_viscera.md`). "plus pluripotent stem cells" changed to "stem cells in the neck", matching the book's location.
13. **Chapter 18, sensory table** (`src/04_viscera.md`). Ruffini endings were described as sensing "stretch and twisting"; the book's wording is tissue distortion, which is now used.
14. **Chapter 18, nails** (`src/04_viscera.md`). The growth rates (3 mm/month and 1 mm/month) are not in the chapter and were removed rather than left as unlabelled book content.
15. **Chapter 19, kidney** (`src/05_systems.md`). A dangling sentence ("…concave medial hilum. on the medial border admits…") repaired. The pyramid count now reads "8–15 (the chapter summary says 8–12)", because the body text and the summary differ.
16. **Chapter 22, active recall** (`src/05_systems.md`). "vitelline barrier" corrected to "perivitelline barrier", the book's term.
17. **Chapter 22, corpus luteum** (`src/05_systems.md`). A short parenthetical now records that the chapter's own Summary of Key Points reverses the two lutein cell types, while the body text and Figure 22–12 (followed by the companion) give progesterone to the granulosa-lutein cells and estrogens to the theca-lutein cells.
18. **Front matter** (`src/00_front.md`). Added an explicit statement that the CLINICAL boxes mix diseases the book discusses with standard clinical correlates it does not, so no reader mistakes them for textbook content. This replaces an implied promise that everything clinical is in the book.

### 4.2 Corrections recorded in the previous pass and still in place

Platelet diameter (2–4 µm), Table 12–1 plasma shares, thin ascending limb as passive NaCl, villin/fimbrin and uroplakin plaques, pneumocyte types I and II only, neutrophil 10–14 µm, Ruffini/Krause endings, MCQ 54 stem and MCQ 88 key, the 136 plate captions rewritten from the figure register, and the removal of the last "examiner" wording from the cover text. These were verified in the source files during this pass and were not changed again.

---

## 5. Automated checks

| Check | Method | Result |
|---|---|---|
| PDF page count | pypdfium2 | **PASS** — 142 |
| Blank or near-blank pages | every page's extracted text < 80 characters | **PASS** — none |
| Text outside the type area | every 7th glyph's bounding box against a 18 pt margin | **PASS** — 0 pages out of bounds |
| Page-number sequence | footer band of every page | **PASS** — page numbers run 4–142 without a gap (front matter unnumbered by design) |
| Contents accuracy | every chapter entry matched to the page where its heading and "Book pages" line occur | **PASS** — 23/23 chapters; Chapter 24 at p115 confirmed |
| Table integrity (source) | every pipe-table row compared with its header count | **PASS** — 0 mismatches |
| Table rendering (PDF) | visual check of representative table pages (pp. 72, 91, 120, 126) | **PASS** — no clipped cells, no overflow |
| MCQ options | every question has four options, each keyed exactly once | **PASS** — 100/100 |
| MCQ key balance | count per letter | **PASS** — A 25, B 25, C 25, D 25 |
| MCQ option layout in PDF | rendered p126 inspected | **PASS** — options on separate lines |
| Flashcards | CSV parse, column set, empty cells, duplicate prompts | **PASS** — 550 rows, 0 empty, 0 duplicates |
| Question bank | CSV parse, column set, count | **PASS** — 100 rows, 11 columns |
| EPUB structure | `tools/validate_epub.py` | **PASS** — 18 files, 11 documents, 45 links, 0 errors, 0 warnings |
| EPUBCheck (official) | requires Java | **NOT RUN** — no Java runtime in the environment; the validator above is a structural check, **not** an EPUBCheck equivalent |
| DOCX structure | zip/XML inspection | **PASS** — 73 tables, no placeholder text, styles present |
| HTML structure | tag census and size | **PASS** — 34 `<h2>`, 288 `<h3>`, 73 tables, 442 kB |
| Build reproducibility | full rebuild of all four formats from the same sources | **PASS** — 142 pages again, no blank pages, same text hash |

---

## 6. Visual coverage

Rendered at 1.5–1.6× and inspected as images: **p. 11** (Chapter 1 opening), **p. 72** (Chapter 15 opening with the four-layer table), **p. 91** (Chapter 19 opening), **p. 120** (rapid-review facts and the start of the distinctions table), **p. 126** (first MCQ page, option layout), **p. 142** (scoring page, final page). Additional pages were checked in the previous pass (cover, contents, part titles, plate captions, MCQ answer key).

These pages show: running head and folio on every body page, no overlap between headings and body, table rules intact, no orphaned headings at the foot, and no clipped columns. **This is not a page-by-page visual inspection of all 142 pages**; no such claim is made.

---

## 7. Copyright and attribution

- **No atlas plate, photograph or figure from the textbook is reproduced.** The companion cites figure numbers and caption subjects so the reader can open the real image. All diagrams, tables and prose in the companion are original to this project.
- No passage of textbook prose is quoted at length. Where the book's own phrasing matters (for example "polypeptide hormones of the immune system"), it is a short phrase used for identification, not a reproduced passage.
- The title page states the source textbook, edition, author and publisher as bibliographic facts, and states that this is an independent companion, not an official publication. No McGraw Hill logo, trade dress or endorsement is used, and no publisher metadata is embedded in the EPUB (removed in `d137690`).
- The running head reads "BASIC HISTOLOGY · THE EXAM & LEARNING COMPANION"; "Basic Histology" is also the leading part of the source title.

**Questions that need a rights-holder or legal review — not answered here:**

1. Whether the cover and running head may use the words "Basic Histology" given that they also form the start of the source title.
2. Whether naming *Junqueira's Basic Histology* in the subtitle and README, with ISBN and edition, is a permissible bibliographic reference in the intended jurisdictions.
3. Whether citing figure numbers and caption subjects (without images) is acceptable, or whether even the caption wording needs permission.
4. Whether the "First edition" designation and the author byline ("prepared for medical students") create any implied affiliation.
5. Whether distribution through the intended channels (university groups, personal sharing) falls inside any educational exception.

No legal clearance is claimed. These questions are unresolved.

---

## 8. Medical and scientific limitations

- The companion has **not** been reviewed by a licensed clinician or a histology examiner. It is an AI-assisted study aid.
- Numerical values follow the textbook where the textbook gives one. Where the textbook is internally inconsistent (pyramid count 8–15 vs 8–12; lutein-cell hormones in text vs summary), the inconsistency is now disclosed rather than silently resolved.
- Standard clinical correlates outside the book's scope appear in CLINICAL boxes and are described as such in the front matter; they are not exhaustive and are not a substitute for a pathology text.
- Thirty source pages have no text layer (full-page plates and covers). No statement in the companion depends on them; figures on those pages are cited by number and not described.
- The 100 MCQs and 550 flashcards are original. They are not past papers, and no frequency claims are made.

---

## 9. Verdict

| Area | Verdict |
|---|---|
| Release identity, provenance, rebuild | **PASS** |
| Content review against the source | **PASS with stated coverage gaps** (Chapters 1–3 and 24 not re-read in this pass) |
| Corrections applied and rebuilt | **PASS** — 18 edits, all four formats regenerated |
| PDF layout and pagination | **PASS** (automated checks + representative visual inspection) |
| DOCX/HTML structure | **PASS** (structural; not visually proofed page by page) |
| EPUB | **PASS** structurally; **EPUBCheck NOT RUN** |
| CSVs | **PASS** |
| Copyright | **NOT CLEARED** — permission questions listed in §7 |
| Medical review | **NOT PERFORMED** |

**Recommendation: ACCEPT WITH EXPLICIT LIMITATIONS.** The release is internally consistent, reproducible from `src/`, free of the defects found in this pass, and honestly labelled. It should not be described as clinically reviewed, legally cleared, or error-free, and the items in §7 must be resolved before any public or commercial distribution.
