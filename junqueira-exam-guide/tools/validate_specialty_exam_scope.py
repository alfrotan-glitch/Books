#!/usr/bin/env python3
"""Verify the owner-supplied Afghanistan specialty exam chapter map.

Checks 23 source chapter markers plus PDF/DOCX/EPUB/HTML render coverage.
No claim of verification against an official MoPH publication is made.
"""
import json
from pathlib import Path
import re
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "specialty_exam_scope.json").read_text(encoding="utf-8"))
medicine = set(data["internal_medicine"])
surgery = set(data["surgery"])
assert len(medicine) == 16 and len(surgery) == 18
assert len(medicine & surgery) == 11 and (medicine | surgery) == set(range(1, 24))

contents = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / "src").glob("*.md")))
pat = re.compile(r"^## (\d{1,2}) · [^\n]+\n\n\*\*SPECIALTY EXAM:\*\* ([^\n]+)", flags=re.M)
matches = list(pat.finditer(contents))
assert len(matches) == 23, f"Expected 23 chapter markers; got {len(matches)}"
observed = {}
for match in matches:
    n = int(match.group(1))
    tags = re.findall(r"\x60([A-Z ]+)\x60", match.group(2))
    assert n not in observed, f"Duplicate tag on chapter {n}"
    expected = (["INTERNAL MEDICINE"] if n in medicine else []) + (["SURGERY"] if n in surgery else [])
    assert tags == expected, f"Chapter {n}: expected {expected}, got {tags}"
    observed[n] = tags
assert set(observed) == set(range(1, 24))
print("SOURCE PASS: 23 unique chapter labels, Medicine 16 / Surgery 18 / both 11.")

# Published files have a separate textual marker on each chapter opening.
from docx import Document
import fitz
pdf = fitz.open(ROOT / "Basic_Histology_Learning_Text.pdf")
pdf_text = "\n".join(page.get_text() for page in pdf)
assert pdf_text.count("EXAM SCOPE") == 23, f"PDF labels: {pdf_text.count('EXAM SCOPE')}"
doc = Document(ROOT / "Basic_Histology_Learning_Text.docx")
doc_labels = [p.text for p in doc.paragraphs if p.text.startswith("SPECIALTY EXAM:")]
assert len(doc_labels) == 23, f"DOCX labels: {len(doc_labels)}"
html = (ROOT / "Basic_Histology_Learning_Text.html").read_text(encoding="utf-8")
assert len(re.findall(r'<p class="specialty-exam"><strong>SPECIALTY EXAM:</strong>', html)) == 23
with ZipFile(ROOT / "Basic_Histology_Learning_Text.epub") as z:
    epubs = []
    for path in z.namelist():
        if re.fullmatch(r"EPUB/text/ch\d+\.xhtml", path):
            root = ET.fromstring(z.read(path))
            for p in root.findall(".//{http://www.w3.org/1999/xhtml}p"):
                if p.get("class") == "specialty-exam":
                    epubs.append("".join(p.itertext()))
    assert len(epubs) == 23, f"EPUB labels: {len(epubs)}"
for format_, spans in (("DOCX", doc_labels), ("EPUB", epubs)):
    assert sum("INTERNAL MEDICINE" in s for s in spans) == 16, format_
    assert sum("SURGERY" in s for s in spans) == 18, format_
print("FORMATS PASS: all 23 specialty exam labels rendered in PDF, DOCX, EPUB and HTML.")
