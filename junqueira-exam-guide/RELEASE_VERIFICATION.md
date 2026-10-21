# Release verification checklist — Basic Histology: A Learning Text

**Scientific basis:** Junqueira's Basic Histology: Text and Atlas, 17th edition is identified as the principal reference. Other standard works are listed for further reading, but independent line-by-line verification against them has **not** been established. This is an original educational work, not a reproduction of that textbook.

## Evidence rules

A green GitHub Actions build establishes that commands completed and the configured output checks passed. It **does not** certify medical accuracy, copyright clearance, print quality, or classroom effectiveness. Cite the exact commit and workflow run for every release claim. Do not reuse page counts or hashes from earlier builds.

## Required before labeling a release FINAL

- [ ] Every chapter and every answer explanation has been read end-to-end by a qualified subject-matter reviewer; corrections and reviewer identity/date are recorded.
- [ ] Quantitative and clinically significant claims are checked against appropriate references; conflicting or variable estimates are qualified.
- [ ] All diagrams, photographs, tables and quotations have documented provenance and required permissions; original artwork is identified as such.
- [x] Source commit `d5d3c20` produced PDF, DOCX, EPUB and HTML in a single successful CI build, with SHA-256 hashes in the generated manifest. Recheck this requirement for any later source revision.
- [ ] PDF is inspected at full size page by page for clipping, table overflow, missing glyphs, awkward breaks and readability, including the cover and answer key.
- [ ] PDF table of contents, bookmarks, pagination and internal links are tested against the latest output.
- [x] Official W3C EPUBCheck 5.4.0 passed with zero errors and warnings on the CI build for `d5d3c20`.
- [ ] EPUB is opened in at least two reading applications and its navigation, tables and reflow are examined.
- [ ] DOCX is opened in a word processor and checked for tables, headings, page breaks and special characters.
- [ ] HTML is checked in a browser at desktop and mobile widths, including keyboard navigation and semantic headings.
- [ ] A sample of learners or teachers attempts the identification tasks and examination questions; ambiguous wording is revised.
- [ ] Final release files are committed or published together with hashes, build instructions, edition, date and known limitations.

## Current evidence

- Latest confirmed full validation of source commit `d5d3c20`: [run 39609970381](https://github.com/alfrotan-glitch/Books/actions/runs/39609970381); four formats plus SHA-256 release manifest. PDF: 149 pages and 44 bookmarks. DOCX: 2,139 paragraphs and 79 tables. EPUB: official EPUBCheck 5.4.0 reports 0 errors, 0 warnings.
- Automated PDF preflight additionally checks for off-page words and Unicode replacement glyphs; both checks passed. It cannot detect every problem visible to a human reader.
- The older `FINAL_REVIEW_REPORT.md` documents a different, earlier manuscript revision and is not a current all-pages proof.
- Expert review, an independent rights/legal assessment, cross-reader opening tests and complete page-by-page human visual inspection are **not** documented as passed.

**Release disposition:** EDITORIAL CANDIDATE — NOT YET FINAL. Change this status only when the above evidence exists.
