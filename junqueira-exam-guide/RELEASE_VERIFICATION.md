# Release verification checklist — Basic Histology: A Learning Text

**Scientific basis:** Junqueira's Basic Histology: Text and Atlas, 17th edition, supplemented by independently checked standard histology and clinical references. This is an original educational work, not a reproduction of that textbook.

## Evidence rules

A green GitHub Actions build establishes that commands completed and the configured output checks passed. It **does not** certify medical accuracy, copyright clearance, print quality, or classroom effectiveness. Cite the exact commit and workflow run for every release claim. Do not reuse page counts or hashes from earlier builds.

## Required before labeling a release FINAL

- [ ] Every chapter and every answer explanation has been read end-to-end by a qualified subject-matter reviewer; corrections and reviewer identity/date are recorded.
- [ ] Quantitative and clinically significant claims are checked against appropriate references; conflicting or variable estimates are qualified.
- [ ] All diagrams, photographs, tables and quotations have documented provenance and required permissions; original artwork is identified as such.
- [ ] The latest source commit produces PDF, DOCX, EPUB and HTML from a single build; exact artifact hashes are recorded.
- [ ] PDF is inspected at full size page by page for clipping, table overflow, missing glyphs, awkward breaks and readability, including the cover and answer key.
- [ ] PDF table of contents, bookmarks, pagination and internal links are tested against the latest output.
- [ ] EPUBCheck passes; EPUB is opened in at least two reading applications and its navigation, tables and reflow are examined.
- [ ] DOCX is opened in a word processor and checked for tables, headings, page breaks and special characters.
- [ ] HTML is checked in a browser at desktop and mobile widths, including keyboard navigation and semantic headings.
- [ ] A sample of learners or teachers attempts the identification tasks and examination questions; ambiguous wording is revised.
- [ ] Final release files are committed or published together with hashes, build instructions, edition, date and known limitations.

## Current evidence

- Latest confirmed successful CI build of source commit `ecb2478`: [run 39606454328](https://github.com/alfrotan-glitch/Books/actions/runs/39606454328), with a four-format artifact.
- The older `FINAL_REVIEW_REPORT.md` documents a different, earlier manuscript revision and is not a current all-pages proof.
- Expert review, copyright clearance, EPUBCheck, reader-app tests and complete visual inspection are not documented as passed.

**Release disposition:** EDITORIAL CANDIDATE — NOT YET FINAL. Change this status only when the above evidence exists.
