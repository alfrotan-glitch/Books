# Building a Reference DOCX

Pandoc (and similar Markdown→DOCX converters) map document structure onto
Word **styles** using a reference document you supply — it does not
invent good-looking styles on its own. Without one, headings and body
text come out in a generic default look with no real style names, which
breaks the "must remain editable via real Word styles" requirement.

## How to create one

1. Generate a throwaway DOCX from a short sample Markdown file that uses
   every structural element the book needs (title, chapter heading,
   section heading, subsection heading, body paragraph, a note/callout,
   a warning, a "clinical pearl," a "key point," a table, a caption, a
   block reference/citation, a bibliography entry).
2. Open that DOCX in Word (or a compatible editor) and edit the actual
   **styles** (not just the text) for each of those elements: font,
   size, color, spacing, indentation, borders/shading for callout-style
   blocks.
3. Save this as `reference.docx` and keep it under version control
   alongside the project. Every future build points `reference-doc` at
   this file (see `assets/pandoc-metadata-template.yaml`).

## Style checklist

Confirm these style names exist and are styled distinctly before using
the reference doc in production: Title, Subtitle, Author, Part, Chapter,
Section, Subsection, Body Text, Note, Warning, Clinical Pearl, Key Point,
Table, Caption, Reference, Bibliography.

## Common pitfall

If a heading in the Markdown source doesn't map to the style you expect
in the output, check that the Markdown heading level (`#`, `##`, `###`)
matches how the reference doc's built-in heading levels (Heading 1,
Heading 2, ...) are styled — mismatches here are the most common cause
of "the styles look wrong" complaints, not a converter bug.

## Keep it in sync

If the design spec changes (see `references/typography-design.md`),
update the reference DOCX and rebuild — don't patch individual output
DOCX files by hand, or the next automated rebuild will silently discard
the hand-patch.
