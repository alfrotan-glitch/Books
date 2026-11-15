#!/usr/bin/env python3
"""Reader-first preflight for the concise histology study edition.

Guardrails are editorial smoke tests, not a claim of medical peer review.
"""
from pathlib import Path
import re
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Basic_Histology_Learning_Text.pdf"
BOOK = ROOT / "src"
with pymupdf.open(PDF) as pdf:
    pages = [page.get_text() for page in pdf]
    words = [len(t.split()) for t in pages]
    n = len(pdf)
    assert 145 <= n <= 260, f"Unexpectedly long/short study edition: {n} pages"
    assert pages[1].strip().startswith("Contents"), "The single cover must be followed by navigation"
    assert "A Learning Text" not in "\n".join(pages[:3]), "Outdated second title page"
    chapters = [x for x in pdf.get_toc() if re.match(r"^\d{1,2}\s*·", x[1])]
    assert len(chapters) == 24, f"Expected 23 reference chapters + review: {len(chapters)}"
    assert chapters[0][2] <= 6, "The first real lesson is too far after the cover"
    assert len(pdf.get_toc()) >= 38, "Chapter navigation incomplete"
    embedded = sum(len(p.get_images(full=True)) for p in pdf)
    assert embedded == 35, f"Expected 23 original mind maps + 12 histology schematic diagrams, found {embedded}"
    too_short = [(i+1,count) for i,count in enumerate(words) if count < 30]
    assert not too_short, f"Nearly blank or orphaned pages: {too_short}"
    overfull = [(i+1,count) for i,count in enumerate(words) if count > 400]
    assert len(overfull) <= 45, f"Too many high-density pages: {len(overfull)}"
    assert "After the Practice Examination" in pages[-1], "Final practice feedback is missing"
    print(f"READABILITY PASS: {n} pages, 35 once-placed diagrams, "
          f"{len(overfull)} pages above 400 words, no orphan pages")

front = (BOOK/"00_front.md").read_text(encoding="utf-8")
assert len(front) < 5000, f"Study introduction has grown too long: {len(front)} chars"
assert "Internal Medicine" in front and "Surgery" in front
atlas = (BOOK/"06b_atlas.md").read_text(encoding="utf-8")
assert "![" not in atlas, "Do not duplicate inline teaching plates in an appendix"
print("CURRICULUM PASS: concise study pathway and exam-track map, without duplicated atlas")
