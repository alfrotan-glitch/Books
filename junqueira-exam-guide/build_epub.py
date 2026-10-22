#!/usr/bin/env python3
"""Build the EPUB 3 edition from the same Markdown sources as the PDF.

    python3 build_epub.py

The EPUB is reflowable XHTML with a navigable table of contents, a generated
cover image, and no external dependencies.
"""

import glob
import os
import pypandoc
from tools.epub_polish import MODERN_CSS, build_cover, polish_epub

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

OUT = os.path.join(HERE, "Basic_Histology_Learning_Text.epub")
COVER = os.path.join(BUILD, "cover.png")
CSS_PATH = os.path.join(BUILD, "epub.css")
MD_PATH = os.path.join(BUILD, "book.md")

TITLE = "Basic Histology: A Learning Text"
SUBTITLE = "A self-contained course in microscopic anatomy"
RIGHTS = ("Original learning text and independently drawn teaching schematics; "
          "no third-party atlas photographs are included. Editorial candidate; "
          "not a clinical manual.")

def main():
    from tools.generate_atlas import generate
    generate()
    build_cover(COVER)
    with open(CSS_PATH, "w", encoding="utf-8") as fh:
        fh.write(MODERN_CSS)

    parts = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        with open(path, encoding="utf-8") as fh:
            parts.append(fh.read())
    with open(MD_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n\n".join(parts))

    pypandoc.convert_file(
        MD_PATH, "epub", outputfile=OUT, format="markdown",
        extra_args=[
            "--standalone",
            "--toc", "--toc-depth=2",
            "--split-level=2",
            "--epub-cover-image=" + COVER,
            "--css=" + CSS_PATH,
            "--resource-path=" + os.pathsep.join((HERE, SRC, BUILD)),
            "--metadata", "title=" + TITLE,
            "--metadata", "subtitle=" + SUBTITLE,
            "--metadata", "rights=" + RIGHTS,
            "--metadata", "lang=en-US",
            "--metadata", "date=2026",
        ],
    )
    polish_epub(OUT)
    print("Modern EPUB written:", OUT)


if __name__ == "__main__":
    main()
