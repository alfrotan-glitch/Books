#!/usr/bin/env python3
"""Build the DOCX and HTML editions from the same Markdown sources."""

import os
import glob
import re
import pypandoc

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

META = """---
title: "Basic Histology: A Learning Text"
subtitle: "A self-contained course in microscopic anatomy"
author: ""
date: "2026"
lang: en-US
---
"""

CSS = """
:root { --ink:#17242C; --muted:#5A6B75; --accent:#0E6B6B; --rule:#C9D5DB; --zebra:#F4F7F8; }
* { box-sizing: border-box; }
body { margin:0 auto; max-width: 46rem; padding: 2rem 1.2rem 5rem;
  font-family: Georgia, "Times New Roman", serif; color: var(--ink);
  line-height: 1.62; background:#fff; font-size: 17px; }
h1 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 1.9rem;
  line-height:1.15; margin: 3rem 0 .6rem; padding-top: 1.4rem;
  border-top: 3px solid var(--accent); }
h1:first-of-type { border-top: none; }
h2 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 1.45rem;
  margin: 2.6rem 0 .5rem; padding-bottom:.45rem; border-bottom: 2px solid var(--accent); }
h3 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: 1.12rem;
  color: var(--accent); margin: 1.8rem 0 .35rem; }
h4 { font-family: "Helvetica Neue", Arial, sans-serif; font-size: .98rem; margin: 1.2rem 0 .3rem; }
p { margin: .55rem 0; text-align: justify; }
figure { max-width: 100%; margin: 1.3rem 0; }
img { display:block; max-width:100%; height:auto; }
table { display:block; overflow-x:auto; max-width:100%; width:100%; -webkit-overflow-scrolling:touch;
  border-collapse: collapse; margin: 1rem 0 1.4rem; font-size: .84rem;
  font-family: "Helvetica Neue", Arial, sans-serif; }
th { background: var(--ink); color:#fff; text-align:left; font-weight:700; }
th, td { padding: .45rem .55rem; vertical-align: top; border-bottom: 1px solid var(--rule); }
tbody tr:nth-child(even) { background: var(--zebra); }
blockquote { margin: 1.1rem 0; padding: .8rem 1rem; border-left: 4px solid var(--accent);
  background:#F6F9F9; font-size: .95rem; }
blockquote p:first-child { margin-top:0; }
blockquote p:last-child { margin-bottom:0; }
code { font-family: "SF Mono", Menlo, monospace; font-size: .85em; background:#EEF2F4;
  padding: .1em .3em; border-radius:3px; }
ol, ul { padding-left: 1.4rem; }
li { margin: .25rem 0; }
hr { border:0; border-top:1px solid var(--rule); margin: 2rem 0; }
a { color: var(--accent); }
nav#TOC { background:#F6F9F9; padding: 1rem 1.2rem; border:1px solid var(--rule); margin: 2rem 0; }
nav#TOC > ul { list-style:none; padding-left:0; }
nav#TOC ul ul { padding-left: 1rem; font-size:.9rem; }
nav#TOC a { text-decoration:none; }
"""


MCQ_OPTS = re.compile(r"\s+(?=[A-D]\.\s)")


def hard_break_options(text):
    """Put each MCQ option on its own line in the DOCX and HTML editions."""
    out = []
    for line in text.split("\n"):
        if re.match(r"^\*\*\d+\.\*\*", line):
            parts = MCQ_OPTS.split(line)
            if len(parts) == 5:
                line = parts[0] + "".join("  \n" + p for p in parts[1:])
        elif re.match(r"^A\.\s", line) and re.search(r"<br\s*/?>", line):
            # The manuscript stores all four options on one Markdown line.
            # Explicit hard breaks are needed for Word, EPUB and HTML output;
            # Pandoc otherwise merges the distractors into a single run.
            options = [piece.strip() for piece in re.split(r"<br\s*/?>", line)]
            if len(options) == 4 and all(re.match(r"^[A-D]\.\s", p) for p in options):
                line = "  \n".join(options)
        out.append(line)
    return "\n".join(out)


def combined():
    parts = [META]
    for f in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        with open(f, encoding="utf-8") as fh:
            parts.append(fh.read())
    text = hard_break_options("\n\n".join(parts))
    path = os.path.join(BUILD, "combined.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def main():
    from tools.generate_atlas import generate
    generate()
    md = combined()

    docx = os.path.join(HERE, "Basic_Histology_Learning_Text.docx")
    pypandoc.convert_file(md, "docx", outputfile=docx, extra_args=[
        "--toc", "--toc-depth=2", "--resource-path=" + os.pathsep.join((HERE, SRC, BUILD)),
    ])
    # Ensure major parts and appendices open on fresh pages in editable Word.
    from docx import Document
    document = Document(docx)
    for para in document.paragraphs:
        title = para.text.strip()
        if ((para.style.name == "Heading 1" and title.startswith("PART "))
                or (para.style.name == "Heading 2" and title.startswith("Appendix "))):
            para.paragraph_format.page_break_before = True
    document.save(docx)
    print("DOCX written:", docx)

    css_path = os.path.join(BUILD, "style.css")
    with open(css_path, "w", encoding="utf-8") as fh:
        fh.write(CSS)

    html = os.path.join(HERE, "Basic_Histology_Learning_Text.html")
    pypandoc.convert_file(md, "html5", outputfile=html, extra_args=[
        "--standalone", "--toc", "--toc-depth=2", "--embed-resources",
        "--css=" + css_path, "--resource-path=" + os.pathsep.join((HERE, SRC, BUILD)),
        "--metadata", "pagetitle=Basic Histology: A Learning Text",
    ])
    print("HTML written:", html)


if __name__ == "__main__":
    main()
