---
name: medical-dari-publishing
description: Pipeline for editing, scientifically validating, typesetting, and publishing medical/health-science manuscripts — with special depth for Afghan Dari clinical books — into publication-ready DOCX, PDF, and EPUB. Use whenever the user is working on a medical textbook, clinical manual, medical-English hybrid book, postgraduate study book, or other health-science manuscript and wants it edited, fact-checked, terminology-normalized, designed, typeset, or exported — even if they only say "editing," "a final version," "the book files," or "check this chapter," not just "publish." Also trigger for auditing/normalizing Afghan Dari medical terminology, distinguishing Afghan Dari from Iranian Persian, building/maintaining a book's terminology glossary, or running QA/release-readiness checks on a manuscript. Not for casual single-sentence proofreading or non-medical creative writing — use for manuscript/chapter/book-length medical or health-science work.
---

# Medical Dari Publishing

## What this skill is

A production pipeline that turns a medical/health-science manuscript into a
professionally edited, scientifically validated, typeset, and multi-format
published book (DOCX + PDF + EPUB). It is written to behave like a
coordinated editorial and production team — medical editor, clinical
subject-matter expert, fact-checker, terminology editor, Dari language
editor, copy editor, book designer, typesetter, and QA/prepress lead — not
like a single generic writing pass. It is reusable across medical
textbooks, clinical manuals, medical-English hybrid books, and
postgraduate study material, and it is built with special depth for books
whose publication language is **Afghan Dari**, not Iranian Persian.

Load this file first. It gives you the workflow and the non-negotiable
principles. Go to the files in `references/` for the detail you need at
each phase — don't try to hold the whole pipeline in your head at once,
and don't skip a phase because the manuscript "looks fine."

## Non-negotiable principles

These override convenience, speed, and the instinct to make prose sound
more sophisticated. Read them before touching the manuscript:

1. **The language is Afghan Dari — never Iranian Persian.** This is the
   single most important standing rule in this skill and it is
   non-negotiable. Every term, phrase, and idiom in the final book must
   be what an Afghan physician or medical student actually uses — not
   what is standard, correct, or elegant in Iran. Shared script and
   shared vocabulary do not make Iranian Persian usage acceptable here.
   **Before normalizing, translating, or "improving" any Dari sentence,
   check it against `references/terminology-hierarchy.md`.** Run the
   Iranian-Persian contamination audit there as its own explicit pass,
   not as an afterthought folded into general copyediting — vocabulary,
   administrative/educational terms, orthographic conventions, and
   idiom are all in scope, not just individual medical words. If you
   cannot confirm a term is genuinely Afghan usage, do not guess and do
   not default to whatever "sounds right" in Persian generally — flag
   it instead (see rule 3 below).
2. **Medical correctness always outranks style.** Never smooth, simplify,
   or dramatize a clinical statement in a way that changes its medical
   meaning. If a sentence is medically wrong, fix the medicine first, then
   the prose.
3. **Never invent.** Not a citation, not a DOI, not a study, not an
   author, not a lab value, not an Afghan terminology equivalent. If you
   can't verify a term is genuinely Afghan usage, say so and flag it —
   don't fill the gap with a plausible-sounding Persian coinage just
   because it's fluent.
4. **No silent scientific changes.** Any correction to a medical fact,
   dose, diagnostic criterion, or clinical recommendation gets logged with
   a classification and, where practical, the original wording preserved
   in the audit record. See `references/editorial-workflow.md`.
5. **No fake completeness.** Never announce a manuscript, chapter, or
   format as "done," "publication-ready," or "complete" unless it has
   actually passed the relevant checks in `references/qa-checklist.md` —
   including the Afghan Dari / Iranian-Persian audit specifically. If
   something is unresolved, say `NOT READY FOR PUBLICATION` and name the
   blocking issue — that phrase is a status report, not a failure to
   avoid.
6. **Flag what needs a human.** Controversial claims, high-risk
   medication information, uncertain terminology (Afghan-vs-Iranian
   included), and legal/copyright questions get surfaced for the
   author's confirmation, not resolved unilaterally and buried in a
   diff.

## When a manuscript comes in: don't just start rewriting

Before editing a single sentence:

1. **Inspect the manuscript** — length, structure, chapter/section
   pattern, existing front/back matter, current format (Markdown, DOCX,
   plain text, etc.).
2. **Identify subject and audience** — medical students, practicing
   physicians, postgraduate trainees, medical-English learners, etc. This
   changes vocabulary level, density, and what needs more scaffolding.
3. **Check source/reference availability** — does the manuscript already
   cite sources? Are there specific guidelines it should track (e.g. a
   national protocol, WHO guidance)?
4. **Establish terminology requirements** — is there an existing glossary
   (check the project's own files/memory first), or does one need to be
   built from scratch? See `references/terminology-hierarchy.md`.
5. **Establish design requirements** — target format(s), whether this is
   screen-only or also headed for print, trim size if known.
6. **Identify missing information** and **draft a short production plan**
   naming which phases below apply and in what order.
7. **State your assumptions** where you had to pick reasonable defaults,
   then proceed — don't stall the pipeline on questions you can answer
   with a documented, reversible assumption. Reserve actual questions for
   points where guessing wrong would waste real work (e.g. "is this for
   print or screen-only," when the answer changes the whole PDF spec).

For a manuscript with no existing terminology glossary, build the
glossary skeleton (`assets/terminology-glossary-template.csv`) as part of
this step — everything downstream depends on it being the single source
of truth.

## The workflow

Work in phases. Each phase has its own reference file with the detailed
checklist — read it when you reach that phase rather than trying to
front-load everything. For a long manuscript, run the full phase sequence
**per chapter**, then run phases 6–8 again at the whole-book level (see
"Working with long manuscripts" below).

| Phase | What happens | Reference |
|---|---|---|
| 0 | Intake & production plan | (above) |
| 1 | Structural audit — architecture, chapter order, hierarchy, cross-references | `references/editorial-workflow.md` (Level 1) |
| 2 | Medical/scientific accuracy review, evidence check, safety layer | `references/medical-accuracy-review.md` |
| 3 | Terminology normalization + Afghan-Dari-vs-Iranian-Persian audit | `references/terminology-hierarchy.md` |
| 4 | Language & copy editing (grammar, punctuation, style, consistency) | `references/editorial-workflow.md` (Levels 3–5) |
| 5 | Book design & typesetting spec (styles, RTL typography, layout) | `references/typography-design.md` |
| 6 | Multi-format production — DOCX, PDF, EPUB | `references/production-pipeline.md` |
| 7 | Quality assurance across all categories | `references/qa-checklist.md` |
| 8 | Release gate, human-review flags, final output package | `references/qa-checklist.md`, `references/output-package.md` |

A phase is never skipped because an earlier phase "probably" covered it.
Structural problems hide inside medically-correct sentences; terminology
problems hide inside grammatically-correct sentences. Each phase looks
for a different failure mode.

### Phase 2 shorthand: the medical-safety trip-wires

While every category in `references/medical-accuracy-review.md` matters,
these stop the pipeline immediately and get flagged before anything else
continues: incorrect doses, contraindication errors, drug interaction
errors, unsafe treatment claims, and outdated emergency recommendations.
Don't let "improve the prose" momentum carry you past one of these.

### Phase 3 shorthand: the terminology rule of thumb

Dari medical term with the English/Latin equivalent in parentheses is the
default presentation style — e.g. `فشار خون (Blood Pressure)` — but don't
force a Persian coinage onto a term that is clinically standard in
English/Latin; preserve the internationally standard term alongside the
Dari explanation instead of fabricating an artificial equivalent. Full
authority hierarchy and the Iranian-Persian contamination audit procedure
are in `references/terminology-hierarchy.md` — read it before normalizing
terminology, not after.

## Working with long manuscripts

For a multi-chapter or multi-volume project:

- **The terminology glossary is the spine.** Every chapter reads from and
  writes to the same glossary file. A term is decided once; every later
  chapter reuses that decision. Don't re-litigate a term that's already
  in the glossary unless new evidence suggests the existing entry is
  wrong — and if you change it, propagate the change and note it in the
  editorial change log.
- **Work chapter-by-chapter for phases 1–4**, checking each chapter's
  changes against the glossary and against continuity with prior
  chapters (recurring patients, running examples, cross-references).
- **Run phases 5–8 at the book level**, once enough chapters are ready to
  make design, production, and QA meaningful — running a full EPUB build
  after every single paragraph edit wastes time; batch it.
- **Keep the master manuscript as a single source of truth** (see
  `references/production-pipeline.md`) and generate DOCX/PDF/EPUB from
  it, rather than hand-editing each output format separately — otherwise
  the formats drift out of sync.
- Never destroy or overwrite the original manuscript. Keep the version
  chain named per `references/editorial-workflow.md`.

## Editorial change log

Every substantive change (anything beyond pure copyediting) gets recorded
as it happens, not reconstructed from memory at the end. Classify each
entry as one of: Editorial, Terminological, Scientific correction,
Clinical correction, Updated evidence, Structural, Formatting,
Publication/prepress. Format and full guidance:
`references/editorial-workflow.md`.

## Producing the actual files

When you're ready to generate DOCX/PDF/EPUB, read
`references/production-pipeline.md` first — it documents a pandoc-based,
single-markdown-source pipeline (real Word styles via a reference DOCX,
XeLaTeX for PDF with RTL/Dari support, EPUB3 validated with epubcheck)
that has already been used successfully for Dari and English medical
books, rather than having you improvise a new toolchain per project. Use
`assets/pandoc-metadata-template.yaml` as the starting metadata block and
`scripts/build_pipeline.sh` as the build-command template.

Follow the file-creation and artifact rules from your main instructions
for where the actual output files go (workspace vs. final deliverables
directory) — this skill governs the editorial and production *content*,
not where Claude's tooling places files.

## Release gate

Before saying a manuscript, chapter, or format is ready, run the checks
in `references/qa-checklist.md` in full and check the result against
`references/output-package.md` for what a complete delivery includes. If
anything blocking remains, the answer is `NOT READY FOR PUBLICATION` plus
a specific, actionable list — never a soft "mostly done" that leaves the
user to discover the gaps themselves.
