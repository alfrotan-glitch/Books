# Editorial Workflow: Levels, Classification, Versioning

## The six editing levels

Work through these as distinct passes — each one looks for a different
class of problem, and doing them in one blended pass tends to miss
things.

**Level 1 — Structural Editing**
Book architecture, chapter order, section hierarchy, logical progression,
repetition, missing sections, unnecessary sections, cross-references.

**Level 2 — Medical Editing**
Factual accuracy, clinical correctness, scientific consistency,
terminology correctness, currency of knowledge. Full detail in
`references/medical-accuracy-review.md`.

**Level 3 — Language Editing**
Dari grammar, spelling, punctuation, sentence structure, readability,
professional style.

**Level 4 — Terminology Editing**
Normalize medical terms, abbreviations, anatomical names, drug names,
lab terminology, units, and their English equivalents. Full detail in
`references/terminology-hierarchy.md`.

**Level 5 — Copy Editing**
Punctuation, capitalization, spacing, numerals, abbreviation consistency,
repeated words, formatting consistency.

**Level 6 — Production Editing**
Page layout, headings, tables, figures, captions, footnotes, references,
headers/footers, page numbers, TOC, indexes where applicable. Full detail
in `references/typography-design.md` and `references/production-pipeline.md`.

## Editorial philosophy

The goal of editing is not to make the text sound more sophisticated. Aim
for: medically accurate, natural in Afghan Dari, academically
professional, clear, concise where appropriate, readable, consistent,
pedagogically useful, publication quality.

Avoid: artificial/overly literary Persian; unnecessarily complicated
sentences; machine-translation patterns; excessive Arabic constructions
where a natural Dari phrasing exists; Iranian terminology when Afghan
terminology is established; awkward literal translations from English.

Preserve the author's intended meaning unless that meaning is
scientifically incorrect — an editor's job is to serve the author's
voice and the reader's understanding, not to substitute the editor's own
voice.

## Classifying changes

Every substantive change gets one label:

- **Editorial** — style, clarity, flow; meaning unchanged
- **Terminological** — a term was normalized per the glossary/hierarchy
- **Scientific correction** — a factual/clinical error was fixed
- **Clinical correction** — a clinical recommendation, dose, or safety
  issue was fixed
- **Updated evidence** — content was current when written but has since
  been superseded by newer guidance
- **Structural** — reorganization, added/removed/reordered sections
- **Formatting** — layout, styling, non-content production changes
- **Publication/prepress** — changes made specifically for
  DOCX/PDF/EPUB output correctness (not content changes)

Pure copyediting-level fixes (typos, obvious punctuation) don't need a
change-log entry each; everything else does.

## The editorial change log

Keep a running log (a simple table works) with, at minimum: chapter/
location, classification, brief description of the change, and — for
Scientific correction / Clinical correction / Updated evidence entries —
the original wording, so it's auditable. This log is itself part of the
final deliverable set (`references/output-package.md`).

## Version control

Never overwrite or destroy the original manuscript. Track distinct
versions as the manuscript moves through the pipeline:

1. Original manuscript (as received — untouched, kept as reference)
2. Working manuscript (active editing copy)
3. Scientifically corrected manuscript (post medical-accuracy pass)
4. Language-edited manuscript (post Dari language + terminology pass)
5. Final master manuscript (single source of truth for production)
6. DOCX production version
7. PDF production version
8. EPUB production version

Every major transformation should be traceable back through this chain —
if the author asks "why does this sentence say X now," you should be
able to point to which version introduced the change and why (via the
change log).

For long, multi-session projects, name files so the version is obvious
from the filename (e.g. a suffix or directory per stage) rather than
relying on modification timestamps alone.
