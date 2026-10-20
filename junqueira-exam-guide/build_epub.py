#!/usr/bin/env python3
"""Build the EPUB 3 edition from the same Markdown sources as the PDF.

    python3 build_epub.py

The EPUB is reflowable XHTML with a navigable table of contents, a generated
cover image, and no external dependencies.
"""

import glob
import os
import pypandoc
from PIL import Image, ImageDraw, ImageFont

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
RIGHTS = ("Original text. No images or extended passages from other publications "
          "are reproduced. A teaching text, not a clinical manual.")

CSS = """
body { font-family: serif; line-height: 1.55; margin: 0 5%; color: #17242C; }
h1, h2, h3, h4 { font-family: sans-serif; line-height: 1.2; color: #17242C; }
h1 { font-size: 1.55em; margin: 1.4em 0 .5em; page-break-before: always; }
h2 { font-size: 1.28em; margin: 1.3em 0 .4em; border-bottom: 1px solid #C9D5DB;
     padding-bottom: .2em; }
h3 { font-size: 1.08em; color: #0E6B6B; margin: 1.1em 0 .3em; }
p { margin: .5em 0; text-align: left; }
ul, ol { margin: .4em 0 .7em 1.1em; padding: 0; }
li { margin: .18em 0; }
table { border-collapse: collapse; width: 100%; margin: .8em 0 1.1em;
        font-family: sans-serif; font-size: .78em; }
th { background: #17242C; color: #fff; text-align: left; }
th, td { padding: .28em .35em; border-bottom: 1px solid #C9D5DB;
         vertical-align: top; word-wrap: break-word; }
tbody tr:nth-child(even) { background: #F4F7F8; }
blockquote { margin: .9em 0; padding: .5em .8em; border-left: 3px solid #0E6B6B;
             background: #F6F9F9; font-size: .95em; }
code { font-family: monospace; font-size: .9em; }
img { max-width: 100%; height: auto; }
"""


def make_cover():
    w, h = 1600, 2400
    img = Image.new("RGB", (w, h), "#17242C")
    d = ImageDraw.Draw(img)
    bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 58)
    tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44)
    d.rectangle([0, h - 26, w, h], fill="#0E6B6B")
    d.text((130, 300), "BASIC", font=bold, fill="#FFFFFF")
    d.text((130, 470), "HISTOLOGY", font=bold, fill="#FFFFFF")
    d.line([130, 700, 700, 700], fill="#0E6B6B", width=8)
    d.text((130, 760), "A Learning", font=small, fill="#DCEBEA")
    d.text((130, 840), "Text", font=small, fill="#DCEBEA")
    d.text((130, 1010), "A self-contained course in", font=tiny, fill="#8FA3AD")
    d.text((130, 1075), "microscopic anatomy", font=tiny, fill="#8FA3AD")
    d.text((130, 1140), "for students of medicine and science", font=tiny, fill="#8FA3AD")
    d.text((130, h - 180), "First edition  ·  2026", font=tiny, fill="#8FA3AD")
    img.save(COVER, "PNG")


def main():
    make_cover()
    with open(CSS_PATH, "w", encoding="utf-8") as fh:
        fh.write(CSS)

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
            "--split-level=1",
            "--epub-cover-image=" + COVER,
            "--css=" + CSS_PATH,
            "--metadata", "title=" + TITLE,
            "--metadata", "subtitle=" + SUBTITLE,
            "--metadata", "rights=" + RIGHTS,
            "--metadata", "lang=en-US",
            "--metadata", "date=2026",
        ],
    )
    print("EPUB written:", OUT)


if __name__ == "__main__":
    main()
