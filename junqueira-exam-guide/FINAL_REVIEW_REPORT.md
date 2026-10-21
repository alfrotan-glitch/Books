# Production report — transformation into a standalone text

> **Current release-status notice (21 October 2026).** This report documents an **earlier** 143-page build, not the latest source revision. Subsequent source changes were committed through `ecb2478`, and GitHub Actions run [39606454328](https://github.com/alfrotan-glitch/Books/actions/runs/39606454328) completed successfully and uploaded the four generated formats as a build artifact. The page count, word count, checksum, per-page checks, and visual-inspection figures below are **historical** and must not be represented as checks of the latest build. The generated files tracked in the repository may also differ from the newer CI artifact. Independent medical review, image-rights assessment where relevant, EPUBCheck, cross-reader testing, and a fresh complete visual proof remain outstanding. The latest edition is therefore a **technically buildable editorial candidate, not a certified final release**.


**Product:** *Basic Histology: A Learning Text* (first edition, 2026).
**Branch:** `arena/8f31a7ed-books`.
**Artifacts:** `Basic_Histology_Learning_Text.pdf` (143 pp), `.docx`, `.epub`, `.html`.
**Scope:** the book. The 550 flashcards and the 100-question CSV bank were not touched and are not assessed here.
**What this report is:** supporting evidence for the transformation. It is not part of the book and is not a claim of independent review or legal clearance.

---

## 1. What changed

The manuscript was a chapter-by-chapter companion to a published textbook: it cited that book's page ranges, figure numbers and plate lists, told the reader which sections of it to consult, and referred to "the book" in the middle of explanations. It is now a self-contained course. A reader can start at page 1 and finish at page 143 without owning another histology text.

### 1.1 Dependent-companion material removed

| Category | Instances before | Action |
|---|---|---|
| "Book pages 71–95" lines under chapter titles | 23 | Replaced with an "In this chapter" topic line generated from the chapter's own headings |
| "Plates to study" blocks citing figure numbers | 23 | Replaced with "Practical identification" tasks: what to find, and the features that distinguish it |
| Sentences citing a figure by number | 136 | Removed or rewritten as direct observational description; no illustration is implied to exist |
| Sentences attributing a statement to "the book", "the textbook" or "the atlas" | 30+ | Rewritten as statements of the subject, with the science kept |
| Chapter-opening section lists copied from the source | 23 | Retained as the chapter's own topic list, now naming this book's headings |
| Table captions "the book's Table 4–1", "the book's Table 12–1" | 3 | Rewritten as this book's tables |
| Book appendix and plate-caption references | 8 | Rewritten; the stain material now stands as Appendix A |
| Book summary/end-of-chapter cross-references | 6 | Rewritten as this book's summaries and questions |

Two source notes were moved out of the book: the dispute over the renal pyramid count (8–15 vs 8–12) and the reversal of the lutein-cell hormones in the source's summary. The book now states the physiology and flags the common error without narrating another publication's internal conflict. The full discrepancy record is in `COVERAGE.md`.

### 1.2 Front matter replaced

`src/00_front.md` was rewritten: About this book; How this book is organized (the twelve teaching blocks); How to study (six-week, ten-day and 48-hour plans keyed to this book's parts); the Twelve Laws of Histology; exam technique; a chapter guide (chapter, title, part — no page ranges); and a note on sources pointing to Appendix C. The old front matter's study plans assumed another book's chapters and page counts and are gone.

### 1.3 Chapter apparatus

Every chapter now runs: learning objectives → core idea → explanation → structure and function → comparison tables → clinical correlates → common misconceptions → summary → active recall → examination-style question → practical identification. The heading "Chapter N — one-line answers" became "Chapter N — summary", because the list is a summary, not a set of answers to a source's questions.

### 1.4 Appendices

- **Appendix A — Stains and What They Prove:** a quick-recall table of 15 stains plus a second table giving the chemistry of each and why it is used.
- **Appendix B — Vocabulary You Should Know:** the terminology list, retained.
- **Appendix C — Sources and Further Reading:** new. It names the principal reference used for checking, lists standard works for further reading without invented editions or dates, explains what the checking covered, states what it did not cover, and records that no images or extended passages are reproduced and that no permission has been obtained.

### 1.5 Identity and build

- New title throughout: *Basic Histology: A Learning Text*; subject "a self-contained course in microscopic anatomy".
- PDF metadata, running head, cover kicker, cover blurb, cover footer, imprint, title page and EPUB/DOCX metadata all rewritten.
- Output filenames changed to `Basic_Histology_Learning_Text.*`; the old `Junqueira_Exam_Companion_FINAL.*` files were removed from the working tree (they remain in git history).
- Cover and EPUB cover artwork generated by the build; no third-party image is used.

## 2. Corrections made during the transformation

| Location | Problem | Correction |
|---|---|---|
| Ch 22 | The lutein-cell note narrated the source's summary and a figure number | Rewritten as physiology plus a common-error box |
| Ch 22 | The ZP note cited a source summary and a figure, and said "four related glycoproteins" | Rewritten: ZP1–ZP3, with ZP4 noted as a human family member |
| Ch 12 | Monocyte size note cited "the chapter's body text" and a figure legend | Rewritten as a range difference between descriptions (12–15 µm) and smear measurements (12–20 µm) |
| Ch 19 | Renal pyramid count note cited the source's summary | Rewritten: 8–15 pyramids, with 8–12 noted as an alternative count in use |
| Ch 8 | Bone matrix note said "the 17th edition gives about 50:50, and this companion follows it" | Rewritten as a statement that both 50:50 and 65:35 conventions are in use |
| Ch 9 | "The book counts six major glial types" | "There are six major glial types" |
| Ch 1 | Two table headers read "What the book says it does" and "Meaning in the book" | "What it does", "Meaning" |
| Ch 1 | The formalin note quoted the book's phrasing | Rewritten as a statement about formalin concentrations |
| Front matter | "The six parts are cumulative" alongside a seven-part structure | "The parts are cumulative" |
| How to study | "the six master tables" while Chapter 24 has ten | "the ten master tables" |
| Scoring table | "Build the six core tables" | "Build the ten master tables" |
| Whole manuscript | Mixed British and American spelling (fibre, colour, organised, artefact, oedema, licence) | Normalized to the American spelling used by the body of the text |
| Appendix C | First draft claimed the content was checked against all listed works | Rewritten: one principal reference was used for checking; the others are further reading and were not verification sources |
| Appendix C | "Mechanisms were checked for consistency" overstated what was done | "reasoned through for consistency" |

## 3. Verification actually performed

| Check | Method | Result |
|---|---|---|
| All four formats build from the same source | `build.py`, `build_docs.py`, `build_epub.py` | **PASS** |
| PDF page count | `pypdfium2` | 143 pages |
| Blank or near-blank pages | text layer, all pages, < 60 characters | none |
| Text outside the type area | char-box extremes against page box, all pages | none found |
| Contents accuracy | 44 contents entries compared with the page each names | 44/44 the named title appears on that page |
| PDF outline | `get_toc()` | 44 bookmarks |
| Residual dependency strings | text scan of the PDF: `Book pages`, `Figure`, `Fig.`, `textbook`, `companion`, `the book says`, `atlas plate`, `pp ` | 0 hits except one bibliography entry ("Junqueira's Basic Histology: Text and Atlas") |
| "Plates" in the PDF | text scan | 14 hits, all anatomical (growth plates, cartilage plates, hepatocyte plates, nail plate) |
| MCQs | key pattern scan | 100 keys, 25 A / 25 B / 25 C / 25 D |
| EPUB structure | `tools/validate_epub.py` | **PASS** — 18 files, 11 documents, 48 internal links resolved, 0 errors, 0 warnings |
| DOCX structure | `zipfile` + `document.xml` | 16 archive entries, 73 tables, no companion strings |
| HTML | title and string scan | correct title; no companion strings |
| Numeric cross-check | every number-with-unit in `src/` searched in the extracted reference text | one unmatched value: "about 1.65 turns" of DNA per nucleosome, a standard structural fact stated as approximate; recorded in `COVERAGE.md` |
| Word count | manuscript and PDF text | 45,750 words in `src/`; 47,187 words in the PDF |

**PASS/FAIL/NOT RUN.** The checks above are automated or textual. The following were **NOT RUN**: EPUBCheck (no Java environment), opening the DOCX in Word, opening the HTML in a browser, opening the EPUB in a reader, a print proof, and any independent expert or medical review.

## 4. What was inspected visually

Pages rendered and inspected at full size during this transformation: cover (1), title page (2), About this book (5), How this book is organized (6), How to study (7), Chapter 1 opener (13), Chapter 24 opener (115), Appendix A (122), Appendix C (125), question paper opener (127), scoring page (143). Earlier passes inspected 18 further pages at full size and all pages of the previous 142-page edition at contact-sheet scale; that thumbnail review does not transfer to the 143-page edition, and it is not claimed here.

**No claim is made that every page of the final 143-page book was inspected individually.** The automated checks in §3 cover every page's text layer and geometry; they cannot detect every typographic fault.

## 5. Limitations and unresolved questions

1. **Full visual inspection is incomplete.** Eleven pages were viewed at full size in this round. Contact-sheet review of an earlier edition is not a substitute.
2. **Content was not re-read end to end in this round.** The transformation was carried out with targeted reading plus scripted edits; the earlier audit's reading of all chapters remains the basis for the scientific content. A text search for dependency phrases cannot prove that no subtler dependence remains.
3. **Thirty source pages had no text layer** (listed in `COVERAGE.md`). No statement depends on them; they were not visually described.
4. **The numeric check is a search, not a proof.** It shows consistency with the reference, not that every explanation is correct.
5. **No independent review, no classroom use.** Judgements about what is high-yield are editorial.
6. **DOCX/EPUB/HTML rendering unverified.** Only their structure was checked.
7. **Copyright and rights remain unresolved.** No permission has been sought. The text reproduces no images, plates, captions or extended passages, but the use of a title, the naming of a principal reference, and the book's own title have not been reviewed by a rights holder or a lawyer. Commercial distribution would require a licence and an ISBN. This is not a legal-clearance statement.
8. **The book still describes images it does not contain** — that is its design, not an oversight: it tells the reader what a structure should look like and expects them to find it on a slide.

## 6. Rights questions for review

- Does naming a principal reference in Appendix C, and describing the text as checked against it, require permission? (It is a citation, not a reproduction, but this has not been reviewed.)
- Is the book's title, *Basic Histology: A Learning Text*, sufficiently distinct from the titles of published textbooks?
- Does the cover art (generated by the build) raise any issue? No third-party image is used.
- Do the 100 questions, written in the style of a standard examination, raise any issue? They are original and are not past-paper items.

## 7. Commits and artifacts

The transformation is committed on `arena/8f31a7ed-books` on top of the audit history; earlier commits are preserved unamended.

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `Basic_Histology_Learning_Text.pdf` | 507,261 | `9f4f233f93d715e4f8fb3801915adf61c1b3c4d47a62dce1773dd42a0a148ff4` |
| `Basic_Histology_Learning_Text.docx` | 174,707 | `6bdb2cf00769bd41553200f48d7bd59b71ee12515269191aaee3259ea5eb6bad` |
| `Basic_Histology_Learning_Text.epub` | 205,774 | `ff9452fb434169e85260ab2e7aaa4714e83c9e195352291e85f4babe19ebfc30` |
| `Basic_Histology_Learning_Text.html` | 439,342 | `ec790b5b3776de4650574ac09e07447dc151f0c601aa6d8b70e8031968258981` |

Hashes are of the files as built for this commit. DOCX, EPUB and PDF builds record timestamps, so rebuilding from identical text changes their hashes; the hashes above identify these files, not the content.

**PDF contents:** 143 pages; contents p. 3; Part I p. 12; Part VI p. 114; Part VII p. 126; answer key p. 138; scoring p. 143.
