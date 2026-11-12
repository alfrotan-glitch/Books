#!/usr/bin/env python3
"""Enforce 23 chapter studios and print/readable companion integrity."""
from pathlib import Path
import re
from docx import Document
import pymupdf
root=Path(__file__).resolve().parents[1]
source="\n".join(p.read_text(encoding="utf-8") for p in (root/"src").glob("*.md"))
labs=list(map(int,re.findall(r"(?m)^### Learning studio — Chapter (\d+)",source)))
assert len(labs)==23 and set(labs)==set(range(1,24)),f"Not all 23 studios: {labs}"
for n in range(1,24):
    assert f"**Reference:** Junqueira's Basic Histology, 17th ed., Chapter {n}" in source
for stem in ("Teacher_Guide","Student_Workbook"):
    md=(root/"course"/(stem+".md")).read_text(encoding="utf-8")
    heads=re.findall(r"(?m)^### (?:Lesson|Chapter) (\d+):",md)
    assert len(heads)==23 and set(map(int,heads))==set(range(1,24)),(stem,heads)
    for ext in (".pdf",".docx",".html"):
        p=root/"course"/(stem+ext)
        assert p.is_file() and p.stat().st_size>5000,p
    doc=Document(root/"course"/(stem+".docx"))
    assert doc.sections[0].page_width.mm>=209 and doc.sections[0].page_height.mm>=296
    with pymupdf.open(root/"course"/(stem+".pdf")) as pdf:
        assert len(pdf)>15,(stem,len(pdf))
        assert all(len(page.get_text().strip())>20 for page in pdf),(stem,"blank page")
    h=(root/"course"/(stem+".html")).read_text(encoding="utf-8")
    assert "<html" in h and "</html>" in h
wb=(root/"course"/"Student_Workbook.md").read_text(encoding="utf-8")
assert wb.count("**Closed-book question:**")>=115
for label in ("**Comparison:**","**Draw and identify:**","**Error detection:**"):
    assert wb.count(label)==23,(label,wb.count(label))
assert "ANSWER KEY AND FEEDBACK" in wb
print("COURSE EDITION PASS: 23 studios, 23 teaching plans, >=184 workbook exercises, six companion exports")
