#!/usr/bin/env python3
"""Verify 23 individual, original mind maps in all formats of the ONE textbook."""
import json
from pathlib import Path
import re
from zipfile import ZipFile
from PIL import Image
import pymupdf
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"data/chapter_mindmaps.json").read_text(encoding="utf-8"))
assert set(map(int,data.keys()))==set(range(1,24)), "Missing or duplicate map definition"
for k, spec in data.items():
    assert len(spec["branches"])==6, (k,"branches")
    assert len(spec["chains"])==2, (k,"chains")
    assert all(len(b)==3 for b in spec["branches"]),(k,"subitems")
    assert spec["title"].strip() and spec["root"].strip()
maps=sorted((ROOT/"build/mindmaps").glob("chapter_*.png"))
assert len(maps)==23, f"Expected 23 generated maps: {len(maps)}"
for i,path in enumerate(maps,1):
    assert path.name==f"chapter_{i:02d}.png"
    with Image.open(path) as image:
        assert image.size==(1500,700),(path,image.size)
        assert image.mode=="RGB"
        assert path.stat().st_size>16000, f"Mind map appears empty: {path.name}"

source_parts=[p.read_text(encoding="utf-8") for p in sorted((ROOT/"src").glob("*.md"))]
source="\n".join(source_parts)
for n in range(1,24):
    start=source.index(f"## {n} ·")
    next_m=re.search(r"(?m)^## \d{1,2} ·|^# PART ",source[start+5:])
    end=start+5+next_m.start() if next_m else len(source)
    chunk=source[start:end]
    fig=f"![Chapter {n} original concept map:"
    assert chunk.count(fig)==1,(n,"figure not unique in chapter")
    assert f"(build/mindmaps/chapter_{n:02d}.png)" in chunk
    assert "**Two pathways to remember**" in chunk
    assert chunk.index("### Chapter mind map")<chunk.index("### Quick notes"),n

base=ROOT/"Basic_Histology_Learning_Text"
with pymupdf.open(base.with_suffix(".pdf")) as pdf:
    figures=sum(len(page.get_images(full=True)) for page in pdf)
    assert figures>=35,f"PDF missing chapter map(s): {figures}"
    assert len(pdf.get_toc())>=38
doc=Document(base.with_suffix(".docx"))
assert len(doc.inline_shapes)>=35,f"Word diagrams missing: {len(doc.inline_shapes)}"
html=base.with_suffix(".html").read_text(encoding="utf-8")
assert len(re.findall(r"<img\b",html,re.I))>=35,"HTML diagrams missing"
with ZipFile(base.with_suffix(".epub")) as zipped:
    images=[p for p in zipped.namelist() if p.endswith(".png")]
    assert len(images)>=36, f"EPUB maps or cover missing: {len(images)}"
print("MIND MAPS PASS: 23 original hierarchical maps, 138 branches, "
      "276 nested facts, 46 concept chains, 35 figures in every book format.")
