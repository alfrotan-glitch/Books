# Terminology System: Afghan Dari Medical Terminology

## The core distinction

"Persian" is not one target. Iranian Persian (Farsi) and Afghan Dari share
a written script and a large common vocabulary, but they diverge in
medical, administrative, and educational register — word choice,
preferred loanwords, and idiom. A term that is standard, elegant Persian
in an Iranian medical text can read as foreign, or simply wrong, to an
Afghan physician or medical student. Treat this as a real terminological
boundary, not a stylistic nuance to smooth over.

**Never assume "Persian = Iranian Persian."** The target for this skill
is always: professional medical Dari as used in Afghanistan's clinical,
academic, and educational environment.

## Authority hierarchy

When terminology choices conflict or are uncertain, resolve in this
order — higher sources override lower ones:

1. Official Afghan Ministry of Public Health terminology and documents
2. Afghan medical universities / recognized Afghan medical education
   sources (e.g. Kabul University of Medical Sciences-associated
   materials)
3. Established terminology used in Afghan hospitals and clinical
   education
4. Standard international medical terminology
5. Major internationally recognized medical textbooks
6. WHO terminology where applicable
7. Other authoritative medical references
8. General dictionaries — last resort only

When you have web search available and the term is uncertain, search for
it rather than guessing from general Persian-language knowledge — general
fluency in Persian is not the same as knowing Afghan clinical usage.

**If a reliable Afghan equivalent cannot be established: don't invent
one.** Retain the internationally recognized medical/English/Latin term
and give a clear Dari explanation instead of fabricating a translation.
A flagged gap is honest; a fabricated coinage is a defect that looks like
progress.

## Presentation format

Default structure for introducing a term:

```
Dari medical term (English medical equivalent)
```

Example: `فشار خون (Blood Pressure)`

When the English/Latin term is the clinically standard one physicians
actually use in speech and charting (common for many specific diagnoses,
drug names, lab tests, eponyms), preserve it rather than forcing an
artificial Dari coinage:

Example: `ترومبوز ورید عمقی (Deep Vein Thrombosis)` — kept bilingual
because "DVT" as spoken/written shorthand is itself part of clinical
practice.

Distinguish, for every term you touch, which category it falls in:

- Afghan Dari terminology (preferred form)
- Iranian Persian terminology (avoid when an Afghan equivalent exists)
- Arabic-derived terminology (often shared and acceptable — check usage)
- English medical terminology (frequently kept as-is)
- Latin anatomical terminology (standard, rarely translated)
- Internationally standardized terminology (WHO/ICD-style terms — do not
  force a Persian equivalent onto these purely for linguistic purity)

## Iranian-Persian contamination audit (explicit final pass)

Run this as its own pass, separate from general copyediting, ideally near
the end of the language-editing phase.

For every term flagged as suspicious:

1. **Identify it** — note the term and where it appears.
2. **Determine whether it's genuinely Iranian-specific**, versus simply
   an uncommon-but-acceptable shared form. Not every unfamiliar word is
   Iranian; some are just less frequent in Afghan usage without being
   wrong.
3. **Search for established Afghan usage** — official Afghan health
   sources, Afghan medical education materials, how Afghan clinicians
   actually write it.
4. **Replace only when reliable Afghan terminology exists.** Don't
   replace on suspicion alone.
5. **If uncertain, flag it instead of guessing.** List it in the
   editorial change log under "Terminological" with an open question,
   rather than silently picking one side.

Categories worth scanning across, since contamination isn't only
vocabulary: Iranian medical terminology, Iranian administrative
terminology (e.g. how institutions, degrees, or health-system roles are
named), Iranian educational terminology, Iranian orthographic conventions
(spelling variants that differ from common Afghan practice), and Iranian
idiomatic/lexical choices more broadly.

The goal is **not** linguistic nationalism for its own sake — it's
producing text that reads as natural, authentic, professional Afghan
medical Dari to the audience who will actually use the book. When in
doubt, prefer whatever an Afghan physician or medical student would
actually say or write in that context.

## The terminology dictionary — single source of truth

Maintain one project-level glossary for the whole book (see
`assets/terminology-glossary-template.csv`). Every chapter reads from and
writes to this same file — a medical concept should not drift across
multiple different Dari renderings in different chapters without a
deliberate, documented reason (e.g. a deliberately simplified form in an
early beginner chapter vs. the full clinical term introduced later).

Each entry should carry:

| Field | Purpose |
|---|---|
| Dari term | The preferred Afghan Dari rendering |
| English term | The standard English equivalent |
| Latin term (optional) | Anatomical/pharmacological Latin form if relevant |
| Abbreviation | Common abbreviation, if any (e.g. DVT, MI, qSOFA) |
| Preferred form | Which rendering to use going forward |
| Forbidden / non-preferred forms | Iranian-Persian or otherwise rejected variants, so they can be scanned for automatically |
| Source / authority | Which tier of the hierarchy above justified this choice |
| Usage notes | Context-dependent notes (e.g. "use full term on first mention per chapter, abbreviation after") |
| First appearance | Chapter/section where the term is first introduced, for continuity tracking |

Once a term has an entry, later chapters **reactivate** it rather than
re-explaining it from zero (this mirrors general pedagogical continuity
practice, not just terminology — see the project's own continuity system
if one exists for the book). If you have access to `scripts/`, the
terminology scanner in `scripts/terminology_scanner.py` can check a
chapter's text against the glossary's forbidden-forms column
automatically once the glossary has entries populated.

## What this hierarchy does not authorize

- It does not authorize replacing a correct international/English/Latin
  medical term with an awkward Persian coinage just to "look more Dari."
- It does not authorize guessing at Afghan terminology when no reliable
  source is available — flag instead.
- It does not authorize treating every Iranian-sounding word as
  automatically wrong — some vocabulary is shared and correct in both;
  the test is actual Afghan clinical/academic usage, not word origin.
