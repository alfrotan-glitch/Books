# Release verification checklist — Basic Histology: A Learning Text

**Scientific basis:** Junqueira's Basic Histology: Text and Atlas, 17th edition is identified as the principal reference. Other standard works are listed for further reading, but independent line-by-line verification against them has **not** been established. This is an original educational work, not a reproduction of that textbook.

## Evidence rules

A green GitHub Actions build establishes that commands completed and the configured output checks passed. It **does not** certify medical accuracy, copyright clearance, print quality, or classroom effectiveness. Cite the exact commit and workflow run for every release claim. Do not reuse page counts or hashes from earlier builds.

## Required before labeling a release FINAL

- [ ] Every chapter and every answer explanation has been read end-to-end by a qualified subject-matter reviewer; corrections and reviewer identity/date are recorded.
- [ ] Quantitative and clinically significant claims are checked against appropriate references; conflicting or variable estimates are qualified.
- [x] Nine schematic atlas plates are generated entirely from the project's own source code and explicitly labeled as original non-photomicrographic artwork; no third-party microscopy images are embedded.
- [ ] Independent legal/provenance review verifies the remaining prose, citations and any rights/permission questions.
- [x] The publication workflow generates PDF, DOCX, EPUB, HTML, two synchronized CSV decks and per-file SHA-256 manifest from one source revision; the last verified illustrated build was [run 39727177604](https://github.com/alfrotan-glitch/Books/actions/runs/39727177604). Recheck a subsequent source revision using its matching run and manifest.
- [ ] PDF is inspected at full size page by page for clipping, table overflow, missing glyphs, awkward breaks and readability, including the cover and answer key.
- [ ] PDF table of contents, bookmarks, pagination and internal links are tested against the latest output.
- [x] Official W3C EPUBCheck 5.4.0 passed with zero errors and warnings for illustrated run `39727177604`.
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

## Current evidence

- Illustrated source run [39727177604](https://github.com/alfrotan-glitch/Books/actions/runs/39727177604) passed: PDF 156 pages and 45 bookmarks; DOCX 2,193 paragraphs and 83 tables; 607 flashcards and 100 synchronized questions; nine original labeled schematic plates; official EPUBCheck 5.4.0: 0 errors, 0 warnings. The latest responsive-HTML build must be checked separately.
- Automated PDF preflight checks off-page words, Unicode replacement glyphs, bookmarks and the presence of the nine images in each output; it cannot detect every problem visible to a human reader. Word was rendered for targeted visual inspection, and desktop/mobile HTML inspection identified a horizontal overflow which has now been addressed in the source and requires a matching build-and-browser retest.
- The older `FINAL_REVIEW_REPORT.md` documents a different, earlier manuscript revision and is not a current all-pages proof. This section is the current production evidence.
- Expert medical review, an independent rights/legal assessment, cross-reader EPUB tests, formal classroom evaluation, and complete page-by-page human visual print inspection are **not** documented as passed.

**Release disposition:** EDITORIAL CANDIDATE — NOT YET FINAL. Change this status only when the above evidence exists.
