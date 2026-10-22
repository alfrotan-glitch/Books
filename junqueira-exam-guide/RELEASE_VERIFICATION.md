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

## Current evidence

- Illustrated source run [39727177604](https://github.com/alfrotan-glitch/Books/actions/runs/39727177604) passed: PDF 156 pages and 45 bookmarks; DOCX 2,193 paragraphs and 83 tables; 607 flashcards and 100 synchronized questions; nine original labeled schematic plates; official EPUBCheck 5.4.0: 0 errors, 0 warnings. The latest responsive-HTML build must be checked separately.
- Automated PDF preflight checks off-page words, Unicode replacement glyphs, bookmarks and the presence of the nine images in each output; it cannot detect every problem visible to a human reader. Word was rendered for targeted visual inspection, and desktop/mobile HTML inspection identified a horizontal overflow which has now been addressed in the source and requires a matching build-and-browser retest.
- The older `FINAL_REVIEW_REPORT.md` documents a different, earlier manuscript revision and is not a current all-pages proof.
- Expert medical review, an independent rights/legal assessment, cross-reader EPUB tests, formal classroom evaluation, and complete page-by-page human visual print inspection are **not** documented as passed.

**Release disposition:** EDITORIAL CANDIDATE — NOT YET FINAL. Change this status only when the above evidence exists.
