#!/usr/bin/env python3
"""One-book acceptance: 23 integrated practice sections, no editor chatter.

This checks the source and rebuilt PDF/DOCX/EPUB/HTML. It cannot substitute
for external subject-matter peer review or rights-holder approval.
"""
from pathlib import Path
import re
from zipfile import ZipFile
import pymupdf
from docx import Document
ROOT=Path(__file__).resolve().parents[1]
sources=[p.read_text(encoding="utf-8") for p in sorted((ROOT/"src").glob("*.md"))]
whole="\n".join(sources)
marker="Integrative practice: reason from the specimen"
chapters=[int(n) for n in re.findall(r"(?m)^## (\d{1,2}) ·",whole) if int(n)<=23]
assert len(chapters)==23 and set(chapters)==set(range(1,24)),chapters
assert len(re.findall(r"(?m)^### "+re.escape(marker)+r"$",whole))==23
for chapter in range(1,24):
    start=whole.find(f"## {chapter} ·")
    assert start!=-1,chapter
    m=re.search(r"(?m)^## \d{1,2} ·|^# PART",whole[start+5:])
    end=start+5+m.start() if m else len(whole)
    part=whole[start:end]
    for heading in ("### Learning objectives","### The core idea","### Integrative practice:",
                    f"### Chapter {chapter} — summary","### Active recall","### Exam-style question",
                    "### Practical identification"):
        assert heading in part,(chapter,heading)
    assert part.index("### Integrative practice:")<part.index(f"### Chapter {chapter} — summary"),chapter

def reject_old(text,label):
    for phrase in ("EDITORIAL CANDIDATE","editorial candidate","rights-holder approval",
                   "automated structural checks","the dated, identifiable references above support",
                   "ISBN requirements depend","schematic shapes do not certify slide-recognition"):
        assert phrase.casefold() not in text.casefold(),f"{label}: unexpected internal editorial text {phrase}"
reject_old(whole,"manuscript")

# Exactly one title, rendered through four electronic/print formats, not a second teacher edition.
assert not (ROOT/"course").exists(),"Separate teacher/workbook should not ship with the unified book"
base=ROOT/"Basic_Histology_Learning_Text"
with pymupdf.open(base.with_suffix(".pdf")) as pdf:
    text="\n".join(page.get_text() for page in pdf)
    assert len(re.findall(r"Integrative practice:\s*reason from the specimen",text))==23
    assert len(pdf.get_toc())>=45
    reject_old(text,"PDF")
doc=Document(base.with_suffix(".docx"))
doc_headings=[p.text for p in doc.paragraphs if p.text.startswith(marker)]
assert len(doc_headings)==23,("DOCX",len(doc_headings))
html=base.with_suffix(".html").read_text(encoding="utf-8")
from lxml import html as lxml_html
html_doc=lxml_html.fromstring(html)
html_titles=[
    " ".join("".join(node.itertext()).split())
    for node in html_doc.xpath("//h3")
]
assert sum(title==marker for title in html_titles)==23,(
    "HTML",sum(title==marker for title in html_titles))
with ZipFile(base.with_suffix(".epub")) as epub:
    from xml.etree import ElementTree as ET
    epub_titles=[]
    for name in epub.namelist():
        if not name.endswith(".xhtml"):continue
        xml=ET.fromstring(epub.read(name))
        epub_titles += [
            " ".join("".join(node.itertext()).split())
            for node in xml.findall(".//{http://www.w3.org/1999/xhtml}h3")
        ]
    assert sum(title==marker for title in epub_titles)==23,(
        "EPUB",sum(title==marker for title in epub_titles))
assert "Junqueira's Basic Histology" in whole
print("UNIFIED TEXTBOOK PASS: 23 integrated chapters, one textbook in PDF/DOCX/EPUB/HTML.")
