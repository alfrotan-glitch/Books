#!/usr/bin/env python3
"""Check reproducible premium editorial identity in the generated four book formats."""
from pathlib import Path
from zipfile import ZipFile
import pymupdf, re
from docx import Document
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/"Basic_Histology_Learning_Text"
with pymupdf.open(base.with_suffix(".pdf")) as pdf:
    front=pdf[0]
    text=front.get_text()
    for phrase in ("BASIC","HISTOLOGY","SMART STUDY NOTES",
                   "23","35","100","INDEPENDENT"):
        assert phrase in text,(phrase,"cover")
    assert len(front.get_drawings())>=12,("Premium cover vector motif missing")
    assert "Junqueira" in text
    assert len(pdf.get_toc())>=38
    assert not any(len(p.get_text().split())<30 for p in pdf)
html=base.with_suffix(".html").read_text(encoding="utf-8")
assert len(re.findall(r'<h3 class="note-summary" id="quick-notes',html))==23
assert len(re.findall(r'<h3 class="concept-map-title" id="chapter-mind-map',html))==23
assert "max-width: 43rem" in html
doc=Document(base.with_suffix(".docx"))
assert doc.paragraphs[0].text.strip()=="Basic Histology: Smart Study Notes"
assert len(doc.inline_shapes)>=35
with ZipFile(base.with_suffix(".epub")) as epub:
    names=epub.namelist()
    assert any(name.endswith("cover.png") for name in names)
    xhtml="".join(epub.read(n).decode("utf-8") for n in names if n.endswith(".xhtml"))
    assert xhtml.count('class="note-summary"')>=23
    assert xhtml.count('class="concept-map-title"')>=23
print("PREMIUM DESIGN PASS: original vector cover, visual hierarchy, 35 figures, "
      "and coordinated PDF/DOCX/HTML/EPUB reading systems.")
