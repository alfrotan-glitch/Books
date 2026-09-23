# میتودهای کلینیکی علی — production project

Set up following `medical-dari-publishing.skill` (repo root).

## Status: NOT READY FOR PUBLICATION

**Blocking:** the manuscript is not in the repo yet. The previous attempt to save it
was abandoned because the source text was no longer available, and the skill forbids
reconstructing or inventing content. Nothing below has been edited yet.

## Next step for the author
Upload the manuscript (`.md`, `.txt` or `.docx`) to
`clinical-methods-ali/manuscript/original/`. That file stays untouched as version 1.

## Phase 0 – Production plan (assumptions are marked; all can be reversed)
| Phase | Plan |
|---|---|
| 0 Intake | Author: Dr Allah Yar Frotan (Dari spelling to confirm). Audience: *assumed* medical students. 14 chapters + normal values + ECG (per the author's description). |
| 1 Structure | Heading hierarchy audit, chapter order, cross-references. |
| 2 Medical accuracy | Normal values, diagnostic criteria and any drug/dose statements checked; safety trip-wires flagged first. |
| 3 Terminology | Build `glossary.csv`; run a separate Afghan-Dari vs Iranian-Persian audit; `tools/terminology_scanner.py`. |
| 4 Language/copy | Dari grammar, punctuation, numerals, spacing. |
| 5 Design | *Assumed* A5, screen-first, Vazirmatn (SIL OFL, `fonts/`). |
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
- Author: **Dr Allah Yar Frotan** (confirmed by user). Still needed: the Dari spelling of the name for the title page, the publisher, and the copyright holder (left as `TODO` in `metadata.yaml`; not invented).
- Print or screen only? If print, what trim size?
- Is there a national protocol or reference textbook the normal values should be checked against?
