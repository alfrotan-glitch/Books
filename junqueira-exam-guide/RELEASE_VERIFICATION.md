# Release verification checklist — Basic Histology: A Learning Text

**Scientific basis:** Junqueira's Basic Histology: Text and Atlas, 17th edition is identified as the principal reference. Other standard works are listed for further reading, but independent line-by-line verification against them has **not** been established. This is an original educational work, not a reproduction of that textbook.

## Evidence rules

A green GitHub Actions build establishes that commands completed and the configured output checks passed. It **does not** certify medical accuracy, copyright clearance, print quality, or classroom effectiveness. Cite the exact commit and workflow run for every release claim. Do not reuse page counts or hashes from earlier builds.

## Required before labeling a release FINAL

- [ ] Every chapter and every answer explanation has been read end-to-end by a qualified subject-matter reviewer; corrections and reviewer identity/date are recorded.
- [ ] Quantitative and clinically significant claims are checked against appropriate references; conflicting or variable estimates are qualified.
- [x] Nine schematic atlas plates are generated entirely from the project's own source code and explicitly labeled as original non-photomicrographic artwork; no third-party microscopy images are embedded.
- [ ] Independent legal/provenance review verifies the remaining prose, citations and any rights/permission questions.
- [x] The publication workflow generates PDF, DOCX, EPUB, HTML, two synchronized CSV decks and per-file SHA-256 manifest from one source revision; the newest validated illustrated-plus-real-slide-companion build was [run 39845766634](https://github.com/alfrotan-glitch/Books/actions/runs/39845766634). Recheck a subsequent source revision using its matching run and manifest.
- [ ] PDF is inspected at full size page by page for clipping, table overflow, missing glyphs, awkward breaks and readability, including the cover and answer key.
- [ ] PDF table of contents, bookmarks, pagination and internal links are tested against the latest output.
- [x] Official W3C EPUBCheck 5.4.0 passed with zero errors and warnings for the current run `39845766634`.
- [ ] EPUB is opened in at least two reading applications and its navigation, tables and reflow are examined.
- [ ] DOCX is opened in a word processor and checked for tables, headings, page breaks and special characters.
- [ ] HTML is checked in a browser at desktop and mobile widths, including keyboard navigation and semantic headings.
- [ ] A sample of learners or teachers attempts the identification tasks and examination questions; ambiguous wording is revised.
- [ ] Final release files are committed or published together with hashes, build instructions, edition, date and known limitations.

## Verified illustrated editorial package — 22 October 2026

- Final validated source commit: `0d2b0db4ba81ad48a76b797cd68dcd99464af5fa`; GitHub Actions [run 39728037204](https://github.com/alfrotan-glitch/Books/actions/runs/39728037204) finished **successfully**. After its green build the generated outputs were also synchronized to `main`.
- Build artifact contains PDF, DOCX, EPUB, HTML, both generated CSV study decks, publication-manifest.json, and nine original schematic PNG plates.
- The PDF has **156 pages**, **45 bookmarks**, and nine embedded diagram images. A subsequent automated inspection verified all page text exists; seven short pages are intentional cover/part-divider pages.
- DOCX: **2,193 paragraphs and 83 tables**. Word-style section breaks and separately displayed MCQ choices are validated in the publication pipeline.
- Study material alignment: **607 flashcards** and **100 exam questions** with every key, four choices and explanation matched to the current canonical manuscript.
- EPUB: official **W3C EPUBCheck 5.4.0 = 0 errors, 0 warnings**, with nine illustrations plus a generated cover.
- Cryptographic provenance: SHA-256 values in `publication-manifest.json` matched the downloaded PDF, DOCX, EPUB and HTML bytes in a local independent verification.
- Browser verification of the actual generated **self-contained HTML** with Chromium: `390 × 844` mobile and `1280 × 900` desktop, all nine pictures loaded, 83 tables present, **document scroll width exactly equals viewport width** in both cases, and narrow tables can scroll internally.
- These are **engineering release checks**, not a signed peer review or a page-by-page print proof.

## Previous verified 157-page build — 23 October 2026

- **Exact manuscript build commit:** `798f68ad5c753f6afc7e6f720d53faf557974c88`. Successful [GitHub Actions run 39844077558](https://github.com/alfrotan-glitch/Books/actions/runs/39844077558). Published asset-sync commit on `main`: `312b56d3bd156f634a778043f0a4039018949479`.
- Four matched deliverables were downloaded as a single run artifact and independently checked against `publication-manifest.json` using SHA-256. **All four hashes matched**; do not mix output files from other runs.
- **PDF:** 157 pages; 45 bookmarks; bibliographic title, subject, keywords, and creator present and verified; nine original schematic plates embedded. Automated no-off-page-words and no-replacement-glyph checks passed. The author field is deliberately blank until rights-holder attribution is approved.
- **DOCX:** 2,195 paragraphs, 83 tables; schematic plates and separated MCQ options included; automated page-break and image-count checks passed.
- **EPUB:** official W3C EPUBCheck 5.4.0 reported **zero errors and zero warnings**; valid EPUB with 27 archive members.
- **HTML:** 916,598 extracted text characters in the structural preflight; the build validates responsive image/table styling and presence of nine images.
- **Learning assets:** 607 flashcards and 100 questions, with all 400 choices, answer keys and rationales synchronized to their manuscript source.
- The additional scientific-regression gate passed: specifically targeted outdated statements about hematopoietic stem cells, microglia, antigen presentation, cardiac repair and foveal anatomy did not reappear.
- **What this evidence does not establish:** no independent all-chapter medical signoff; no full-scale page-by-page visual/print approval; no cross-reader EPUB certification or legal/commercial rights approval. These remain explicit release blockers.

## Latest independently checked 161-page candidate — 23 October 2026

- **Authoritative build:** GitHub Actions [run 39845766634](https://github.com/alfrotan-glitch/Books/actions/runs/39845766634), successful, from source `7f04c3997207438a94a6c090c59f7954470fa209`; the generated binary files were safely synchronized to `main` in commit `881571517a01997fe37111cc47c37760559c5adc`.
- **Package verification:** downloaded the actual artifact and independently verified that each PDF, DOCX, EPUB and HTML file's SHA-256 and byte count matched `publication-manifest.json` (4 of 4).
- **PDF:** 161 pages and 46 bookmarks; title metadata included; visual spot-check covered the cover, contents, original schematic plates, Appendix E real-slide exercises, questions, answer key and ending pages. This is **not** a 161-page full-size human proof.
- **DOCX:** 2,215 paragraphs and 84 tables; PDF-rendered Word layouts were sampled during earlier illustrated revisions, but the latest edition still needs a complete editorial proof in a word processor.
- **EPUB:** W3C EPUBCheck 5.4.0 found **0 errors and 0 warnings**; 27 archive entries.
- **Study materials:** 607 regenerated flashcards and 100 exam questions; source-to-CSV comparison and high-impact scientific regression checks both passed.
- **Practical learning:** Appendix D includes nine original teaching schematics. Appendix E supplies 23 observational tasks and links to externally hosted university slides. **No third-party slide images are redistributed.**
- **Remaining gates:** independent medical specialist review, rights-holder approval and author credit, complete print-page visual proof, and cross-reader EPUB accessibility/usability evaluation are still open.

## Current evidence

- Historical earlier illustrated source run [39727177604](https://github.com/alfrotan-glitch/Books/actions/runs/39727177604) passed: PDF 156 pages and 45 bookmarks; DOCX 2,193 paragraphs and 83 tables; 607 flashcards and 100 synchronized questions; nine original labeled schematic plates; official EPUBCheck 5.4.0: 0 errors, 0 warnings. This older record has been superseded by the successful 39844077558 build above.
- Automated PDF preflight checks off-page words, Unicode replacement glyphs, bookmarks and the presence of the nine images in each output; it cannot detect every problem visible to a human reader. Word was rendered for targeted visual inspection, and desktop/mobile HTML inspection identified a horizontal overflow which has now been addressed in the source and requires a matching build-and-browser retest.
- The older `FINAL_REVIEW_REPORT.md` documents a different, earlier manuscript revision and is not a current all-pages proof. This section is the current production evidence.
- Expert medical review, an independent rights/legal assessment, cross-reader EPUB tests, formal classroom evaluation, and complete page-by-page human visual print inspection are **not** documented as passed.

**Release disposition:** EDITORIAL CANDIDATE — NOT YET FINAL. Change this status only when the above evidence exists.
