# Multi-Format Production Pipeline

## Principle: one source, three outputs

Maintain a **single Markdown master manuscript** with YAML front-matter
metadata (title, author, language, rights, etc.) as the single source of
truth, and generate DOCX, PDF, and EPUB from it — never hand-author each
format separately. Hand-authoring three formats guarantees they drift
out of sync the first time the author asks for a change.

This pipeline (pandoc-based, single Markdown source → DOCX/PDF/EPUB) is
not theoretical — it's a toolchain that has already been used
successfully for Dari/English medical-education books end to end,
including a full RTL Dari EPUB with embedded fonts that passed
`epubcheck` with zero errors and zero warnings. Prefer it over
improvising a new toolchain per project.

Start from `assets/pandoc-metadata-template.yaml` for the front matter
and `scripts/build_pipeline.sh` for the build commands.

## DOCX production

- Convert from the Markdown master using a **reference DOCX** (see
  `references/typography-design.md` and
  `assets/docx-reference-styles-notes.md`) so headings/body/callouts map
  onto real Word styles, not manual formatting.
- Verify after generation: style names are correct and consistent, TOC
  (if present) is generated from actual heading styles, tables render
  cleanly, and the document opens and edits normally in Word (no
  corruption warnings).
- The DOCX is also a legitimate deliverable in its own right (the
  editable "final editable DOCX" in the output package), not just an
  intermediate step.

## PDF production

- Use XeLaTeX (or another Unicode/RTL-capable LaTeX engine) as the PDF
  engine — plain `pdflatex` will not handle Perso-Arabic script
  correctly. A `lmodern`-style font package install is commonly needed
  as a dependency; confirm the toolchain has what it needs before
  assuming the build will succeed silently.
- RTL text direction, proper bidi behavior at script boundaries, and
  correct rendering of the chosen Dari typeface are the main failure
  points — check these visually in the actual output, don't assume
  correctness from the source Markdown looking right.
- Check after generation: page dimensions/margins match the design spec,
  fonts are embedded, no missing-glyph boxes anywhere (scan mixed-script
  pages especially), no orphan/widow problems, headings don't strand at
  the bottom of a page, tables don't break awkwardly across pages,
  figures are placed sensibly, no accidental blank pages, page numbering
  is correct throughout, TOC page references are accurate, and
  bookmarks/metadata are set.
- If the book is headed for professional printing, be explicit about
  whether a given PDF is the **screen PDF** or the **print-ready PDF**
  (bleed, color profile, and margin requirements can differ) — don't
  hand over one file and call it both.

## EPUB production

- Produce a valid EPUB3. Verify structurally: `mimetype` is first in the
  archive and stored uncompressed, `nav.xhtml` and `toc.ncx` are present
  and correct, `content.opf` metadata is complete (title, author,
  publisher, description, rights, language).
- Set text direction (`dir="rtl"`) and language metadata correctly for
  Dari content; verify mixed English/Dari runs render without corruption
  in an actual e-reader or EPUB validator preview, not just by reading
  the XHTML source.
- Embed fonts only where the license explicitly permits it (SIL Open
  Font License-type fonts are the safe default — confirm before
  embedding anything else). Declare the cover with both the EPUB3
  `properties="cover-image"` attribute and the legacy `<meta
  name="cover">` tag for cross-reader compatibility.
- Check images, captions, tables, footnotes, and internal/cross-chapter
  links resolve correctly, and that chapter navigation (both the nav doc
  and in-reader table of contents) is complete and in the right order.
- The EPUB should be **reflowable** by default; only build fixed-layout
  if the project explicitly requires it (e.g. a heavily illustrated
  layout that can't reflow sensibly).
- **Always validate with the official W3C `epubcheck` tool** before
  calling an EPUB done. A build that "looks right" in one reader can
  still fail validation elsewhere. Zero errors and zero warnings is the
  bar, not "no errors."

## Cover and visual assets

If a custom cover is part of the scope, treat it as a small design task
in its own right: define a color/typography system consistent with the
book's interior design, generate it, and make sure it satisfies both
modes of cover declaration used by EPUB readers (see above). Don't ship
a generic placeholder cover as if it were final.

## Build hygiene

- Rebuild all three formats from the master after any content change
  significant enough to affect more than copyediting — don't patch one
  output format by hand while leaving the others stale.
- Keep the build reproducible: the same Markdown source plus the same
  metadata/template files should regenerate the same outputs. If the
  build depends on installing something (a font, a LaTeX package), note
  that dependency where the build script lives so a future session
  doesn't have to rediscover it by trial and error.
