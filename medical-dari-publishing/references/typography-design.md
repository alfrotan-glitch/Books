# Book Design & Typography

Design priority order for a medical publication: **readability, then
academic professionalism, then medical usability** — not decorative
complexity. A medical textbook that looks striking but is harder to read
at 2am on a hospital ward has failed its actual job.

## Design spec to define per project

Before typesetting, establish and document:

- Trim size
- Margins and gutter
- Typography (body font, heading font, monospace/code font if needed)
- Font hierarchy (title / chapter / section / subsection / body / caption)
- Chapter-opening design
- Paragraph styles (body, list, blockquote/callout variants)
- Table style
- Callout box types: definitions, clinical notes/pearls, warnings, key
  points — each visually distinct but consistent
- Reference/bibliography formatting
- Headers, footers, running heads, page numbers
- Figure and table caption style

## RTL / Dari typography — the part that's easy to get wrong

Because the book's base direction is right-to-left (Dari), mixed-script
content needs deliberate handling, not just "it'll render fine":

- RTL paragraph direction for Dari prose
- Correct behavior at RTL/LTR boundaries (an English or Latin term
  embedded in a Dari sentence must not visually scramble or reverse)
- English medical terms — must stay visually intact and left-to-right
  even inside an RTL paragraph
- Latin anatomical terminology — same requirement
- Numbers — Persian/Arabic-Indic vs. Western Arabic numerals: pick one
  convention and apply it consistently (Afghan Dari technical/medical
  text commonly uses Western Arabic numerals — confirm against the
  project's existing convention or the terminology glossary's usage
  notes rather than assuming)
- Units, abbreviations, equations — must not become visually corrupted
  by bidi reordering
- Drug names, references, URLs, DOI strings — these are typically LTR
  runs inside RTL text and need the same care as English terms

**Fonts**: choose an open-license typeface family with solid Perso-Arabic
script support and good Latin-script pairing, since every page mixes
scripts. Options that have worked well for this kind of mixed Dari/
English medical content: Vazirmatn (versatile, strong Latin pairing),
Noto Nastaliq Urdu or Noto Sans Arabic (broad glyph coverage), or
Scheherazade/Lateef (more traditional Naskh forms) for body text, paired
with a clean neutral Latin sans (e.g. Work Sans) for English terms and a
distinct display face for chapter openers/titles if a more editorial
feel is wanted. Confirm license terms allow embedding in DOCX/PDF/EPUB
before shipping.

If the project already has an established look (check the project's own
files/memory before designing from scratch), match it rather than
introducing a new design system per book in the same series.

## DOCX style system

Generate DOCX using real Word paragraph/character styles, not manual
per-paragraph formatting — manual formatting breaks the moment the
author edits the file themselves, and blocks TOC/navigation generation.

Define reusable styles at minimum for: Title, Subtitle, Author, Part,
Chapter, Section, Subsection, Body, Note, Warning, Clinical Pearl, Key
Point, Table, Caption, Reference, Bibliography.

The practical way to get real styles out of a Markdown-to-DOCX pipeline
(see `references/production-pipeline.md`) is a **reference DOCX** —a
template document with these styles pre-defined, which pandoc (or
equivalent) maps Markdown structure onto. See
`assets/docx-reference-styles-notes.md` for how to build and maintain
one. The output document must remain editable by the author afterward —
if the author can't select "Heading 2" and have it look right, the style
system failed.
