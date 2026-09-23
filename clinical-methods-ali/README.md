# میتودهای کلینیکی علی — production project

Set up following `medical-dari-publishing.skill` (repo root).

## Status: NOT READY FOR PUBLICATION

**Done — book design (Phase 5) and production pipeline (Phase 6):**
- Cover (`assets/cover.jpg`, background `assets/cover-art.jpg`, AI-generated artwork) with title and author.
- Front matter: half-title, title page, imprint/copyright page with a medical disclaimer, and a styled table of contents.
- Body: A5 with mirrored margins for RTL binding, Vazirmatn 10.5 pt justified. Each chapter opens on a right-hand page with its own design. Running header shows book and chapter titles; page numbers in Dari digits; boxed H2 headings; teal/gold table styling; Dari list numbering.
- The DOCX uses the same fonts, colours and A5 page via `reference.docx`. The EPUB uses the cover and `epub.css`.
- Design proof: `proofs/design-proof-DRAFT.pdf`. It is built from the only verbatim text saved so far (`manuscript/original/opening-excerpt.md`, the opening of chapter 1) and carries a «پیش‌نویس» watermark.

**Blocking:** the full manuscript is not in the repository. The text pasted into the chat
could not be saved in full, and the skill forbids reconstructing it. Phases 1–4 (structure,
medical accuracy, Afghan-Dari terminology, language) and the final QA can't run until the file is uploaded.

## Next step for the author
Upload the complete manuscript (`.docx`, `.md` or `.txt`) to
`clinical-methods-ali/manuscript/original/`. It stays untouched as version 1. Then run the
editorial phases → `manuscript/master.md` → `./build.sh`.

## Phase 0 – Production plan (assumptions are marked; all can be reversed)
| Phase | Plan |
|---|---|
| 0 Intake | Author: Dr Allah Yar Frotan (Dari spelling to confirm). Audience: *assumed* medical students. 14 chapters + normal values + ECG (per the author's description). |
| 1 Structure | Heading hierarchy audit, chapter order, cross-references. |
| 2 Medical accuracy | Normal values, diagnostic criteria and any drug/dose statements checked; safety trip-wires flagged first. |
| 3 Terminology | Build `glossary.csv`; run a separate Afghan-Dari vs Iranian-Persian audit; `tools/terminology_scanner.py`. |
| 4 Language/copy | Dari grammar, punctuation, numerals, spacing. |
| 5 Design | A5, print-ready with mirrored margins (also used for screen), Vazirmatn (SIL OFL, `fonts/`). |
| 6 Production | `./build.sh` → DOCX, PDF (Typst engine), EPUB3 + epubcheck. |
| 7–8 QA / release | `references/qa-checklist.md`; output package per `references/output-package.md`. |

Editing works per chapter (phases 1–4), with every change logged in `CHANGELOG-editorial.md`.

## Version chain
`manuscript/original/` (as received) → `manuscript/working.md` → `…-scientific.md` →
`…-language.md` → `manuscript/master.md` (single source) → `build/` outputs (git-ignored).

## Toolchain (verified in this sandbox with a smoke test)
`pip install --user pypandoc_binary typst jdk4py epubcheck`, then run `./build.sh`.
Result: RTL rendering, embedded fonts and mixed Dari/English all correct; epubcheck
returned 0 errors / 0 warnings on the test sample. XeLaTeX isn't available here, so
Typst is used as the PDF engine.

## Open questions for the author (human-review gate)
- Author: **Dr Allah Yar Frotan**. Title page uses the transliteration «داکتر الله‌یار فروتن» — please confirm the spelling.
- Publisher: not supplied (omitted, not invented). Copyright line «© ۲۰۲۶ داکتر الله‌یار فروتن. تمام حقوق محفوظ است.» is a proposal — confirm.
- Year shown: ۱۴۰۵ هجری شمسی — confirm. ISBN / edition: add `isbn:` / `edition:` in `metadata.yaml` if available.
- Remove `draft-watermark` from `metadata.yaml` only after QA passes and the author signs off.
- Print or screen only? If print, what trim size?
- Is there a national protocol or reference textbook the normal values should be checked against?
