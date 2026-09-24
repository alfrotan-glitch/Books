#!/usr/bin/env bash
# Build the new book: chapters/*.md -> build/master.md -> PDF (screen + print), EPUB, DOCX.
set -euo pipefail
cd "$(dirname "$0")"
OUT=build; SLUG=moayena-clinical
mkdir -p "$OUT"
python3 tools/assemble.py            # -> build/master.md, build/index-terms.json
PANDOC=$(python3 -c "import pypandoc;print(pypandoc.get_pandoc_path())")
SRC=$(mktemp --suffix=.md)
python3 tools/normalize_md.py "$OUT/master.md" "$SRC"
typ() { "$PANDOC" metadata.yaml "$SRC" -f markdown -t typst --lua-filter=tools/book.lua --standalone --template=templates/book.typst "$@"; }
compile() { cp "$1" ./.book.typ; python3 -c "import sys,typst;typst.compile('./.book.typ',output=sys.argv[1],root='.',font_paths=['fonts'],ignore_system_fonts=True)" "$2"; }
echo "PDF..."; typ -o "$OUT/$SLUG.typ"; sed -i 's/numbering: "1\./numbering: "۱./g' "$OUT/$SLUG.typ"; compile "$OUT/$SLUG.typ" "$OUT/$SLUG.pdf"
echo "PDF print..."; typ -M print-edition=true -o "$OUT/$SLUG-print.typ"; sed -i 's/numbering: "1\./numbering: "۱./g' "$OUT/$SLUG-print.typ"; compile "$OUT/$SLUG-print.typ" "$OUT/$SLUG-print-interior.pdf"
echo "DOCX..."; "$PANDOC" metadata.yaml "$SRC" -f markdown -t docx --lua-filter=tools/book.lua --toc --toc-depth=2 --reference-doc=reference.docx -o "$OUT/$SLUG.docx"
echo "EPUB..."; "$PANDOC" metadata.yaml epub-title.yaml "$SRC" -f markdown -t epub3 --lua-filter=tools/book.lua --epub-title-page=false --split-level=1 --template=templates/epub3.html --epub-cover-image=assets/cover.jpg --toc --toc-depth=2 --epub-embed-font='fonts/*.ttf' --css epub.css -o "$OUT/$SLUG.epub"
JAVA=$(python3 -c "import jdk4py;print(jdk4py.JAVA)"); JAR=$(python3 -c "import epubcheck,os;print(os.path.join(os.path.dirname(epubcheck.__file__),'epubcheck.jar'))")
"$JAVA" -jar "$JAR" "$OUT/$SLUG.epub" 2>&1 | tail -2
python3 tools/similarity.py | tail -3
rm -f "$SRC" ./.book.typ
