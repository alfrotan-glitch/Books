#!/usr/bin/env bash
# Build DOCX / PDF / EPUB from the single Markdown master (medical-dari-publishing skill pipeline).
# Toolchain (no apt access in the sandbox, so everything comes from PyPI):
#   pip install --user pypandoc_binary typst jdk4py epubcheck
# PDF engine: Typst (via pandoc --to=typst), RTL shaping with embedded Vazirmatn (SIL OFL).
set -euo pipefail
cd "$(dirname "$0")"
MASTER="${1:-manuscript/master.md}"
OUT=build; SLUG=clinical-methods-ali
PANDOC=$(python3 -c "import pypandoc;print(pypandoc.get_pandoc_path())")
mkdir -p "$OUT"
# Strip the GitHub-only RTL <div> wrapper for production formats.
SRC=$(mktemp --suffix=.md)
grep -v -E '^\s*</?div( dir="rtl" align="right")?>\s*$' "$MASTER" > "$SRC"
python3 tools/normalize_md.py "$SRC" "$SRC"

echo "DOCX..."
"$PANDOC" metadata.yaml "$SRC" -f markdown -t docx --lua-filter=tools/book.lua --toc --toc-depth=2 \
  $( [ -f reference.docx ] && echo --reference-doc=reference.docx ) -o "$OUT/$SLUG.docx"

echo "PDF (Typst)..."
"$PANDOC" metadata.yaml "$SRC" -f markdown -t typst --lua-filter=tools/book.lua --standalone --template=templates/book.typst -o "$OUT/$SLUG.typ"
sed -i 's/numbering: "1\./numbering: "۱./g' "$OUT/$SLUG.typ"
cp "$OUT/$SLUG.typ" ./.book.typ
python3 - ./.book.typ "$OUT/$SLUG.pdf" <<'PY'
import sys, typst
typst.compile(sys.argv[1], output=sys.argv[2], root=".", font_paths=["fonts"], ignore_system_fonts=True)
PY

echo "EPUB3..."
"$PANDOC" metadata.yaml "$SRC" -f markdown -t epub3 --lua-filter=tools/book.lua --epub-title-page=false --split-level=1 --template=templates/epub3.html --epub-cover-image=assets/cover.jpg --toc --toc-depth=2 \
  --epub-embed-font='fonts/*.ttf' --css epub.css -o "$OUT/$SLUG.epub"

echo "epubcheck..."
JAVA=$(python3 -c "import jdk4py;print(jdk4py.JAVA)")
JAR=$(python3 -c "import epubcheck,os;print(os.path.join(os.path.dirname(epubcheck.__file__),'epubcheck.jar'))")
"$JAVA" -jar "$JAR" "$OUT/$SLUG.epub"
rm -f "$SRC" ./.book.typ
echo "Outputs in $OUT/"
