#!/usr/bin/env bash
#
# build_pipeline.sh
#
# Template build script for the single-source Markdown -> DOCX/PDF/EPUB
# pipeline described in references/production-pipeline.md. Copy this into
# the project and fill in the paths for that project — it is a starting
# point, not a one-size-fits-all script (trim size, fonts, and language
# metadata differ per book).
#
# Requires: pandoc, a XeLaTeX distribution (e.g. texlive-xetex +
# texlive-latex-extra / lmodern), and epubcheck for validation.

set -euo pipefail

# --- Project-specific paths: edit these ---
MASTER_MD="manuscript/master.md"          # single-source Markdown manuscript
METADATA="pandoc-metadata.yaml"           # from assets/pandoc-metadata-template.yaml
REFERENCE_DOCX="reference.docx"           # from assets/docx-reference-styles-notes.md
OUT_DIR="build"
BOOK_SLUG="book"                          # used for output filenames

mkdir -p "$OUT_DIR"

# --- DOCX ---
echo "Building DOCX..."
pandoc "$METADATA" "$MASTER_MD" \
  --from=markdown \
  --to=docx \
  --reference-doc="$REFERENCE_DOCX" \
  --toc --toc-depth=2 \
  -o "$OUT_DIR/${BOOK_SLUG}.docx"

# --- PDF (XeLaTeX, RTL-capable) ---
echo "Building PDF..."
pandoc "$METADATA" "$MASTER_MD" \
  --from=markdown \
  --to=pdf \
  --pdf-engine=xelatex \
  --toc --toc-depth=2 \
  -o "$OUT_DIR/${BOOK_SLUG}.pdf"

# --- EPUB3 ---
echo "Building EPUB..."
pandoc "$METADATA" "$MASTER_MD" \
  --from=markdown \
  --to=epub3 \
  --toc --toc-depth=2 \
  -o "$OUT_DIR/${BOOK_SLUG}.epub"

# --- Validate EPUB ---
if command -v epubcheck >/dev/null 2>&1; then
  echo "Validating EPUB with epubcheck..."
  epubcheck "$OUT_DIR/${BOOK_SLUG}.epub"
else
  echo "epubcheck not found on PATH — install it and run this validation" \
       "before calling the EPUB done (see references/production-pipeline.md)."
fi

echo "Done. Outputs in $OUT_DIR/"
echo "Remember: rebuild all three formats together after any content change" \
     "significant enough to affect more than copyediting."
