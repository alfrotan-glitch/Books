#!/usr/bin/env python3
"""Reader navigation & usability checks against the actual generated publication.

Catches historic PDF TOC overflow/orphan pages and missing external live-slide
links. These checks are NOT independent medical, legal or full visual proof.
"""
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re

import fitz
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Basic_Histology_Learning_Text.pdf"
DOCX = ROOT / "Basic_Histology_Learning_Text.docx"
EPUB = ROOT / "Basic_Histology_Learning_Text.epub"
HTML = ROOT / "Basic_Histology_Learning_Text.html"
EXPECTED_HOSTS = (
    "histology.medicine.umich.edu",
    "histology.leeds.ac.uk",
    "medcell.org",
    "www.histologyguide.org",
)
with fitz.open(PDF) as pdf:
    page_text = [p.get_text() for p in pdf]
    assert len(pdf.get_toc()) >= 45, "Main contents/bookmarks appear missing"
    contents_pages = [
        (i, text) for i, text in enumerate(page_text)
        if re.search(r"(?m)^Contents$", text)
    ]
    assert len(contents_pages) == 1, f"Unexpected contents pages: {len(contents_pages)}"
    contents_index, contents_text = contents_pages[0]
    assert contents_index <= 4, "TOC not near the front matter"
    assert "Scoring and What to Do Next" in contents_text, (
        "PDF contents spill over into an isolated extra page"
    )
    annotations = [link for page in pdf for link in page.get_links()]
    internal = [x for x in annotations if x.get("kind") == fitz.LINK_GOTO]
    external = [x.get("uri", "") for x in annotations if x.get("kind") == fitz.LINK_URI]
    assert len(internal) >= 40, f"PDF has only {len(internal)} clickable internal TOC links"
    for host in EXPECTED_HOSTS:
        assert any(host in uri for uri in external), f"Missing PDF virtual microscopy link: {host}"
    assert "Text only: no histological images are reproduced" not in page_text[0]
    assert not any("\uFFFD" in text for text in page_text)
    print(
        f"PDF NAV PASS: {len(pdf)} pages; {len(pdf.get_toc())} outline entries; "
        f"{len(internal)} internal links; {len(external)} external links; complete single-page TOC"
    )

document = Document(DOCX)
docx_links = [
    rel.target_ref for rel in document.part.rels.values()
    if rel.is_external and str(rel.target_ref).startswith("https://")
]
for host in EXPECTED_HOSTS:
    assert any(host in uri for uri in docx_links), f"Missing DOCX microscopy link: {host}"
print(f"DOCX LINKS PASS: {len(docx_links)} external HTTPS links")

html = HTML.read_text(encoding="utf-8")
html_links = re.findall(r'href="(https://[^"]+)"', html)
for host in EXPECTED_HOSTS:
    assert any(host in uri for uri in html_links), f"Missing HTML microscopy link: {host}"
print(f"HTML LINKS PASS: {len(html_links)} external HTTPS links")

epub_links = []
ns = {"x": "http://www.w3.org/1999/xhtml"}
with ZipFile(EPUB) as zipped:
    for member in zipped.namelist():
        if member.endswith(".xhtml"):
            tree = ET.fromstring(zipped.read(member))
            epub_links += [
                node.get("href", "")
                for node in tree.findall(".//x:a", ns)
                if node.get("href", "").startswith("https://")
            ]
for host in EXPECTED_HOSTS:
    assert any(host in uri for uri in epub_links), f"Missing EPUB microscopy link: {host}"
print(f"EPUB LINKS PASS: {len(epub_links)} external HTTPS links")

# This verifies that four readers include click targets. It does not prove
# sites will remain online, that their images can be redistributed, or that
# every external app handles the targets identically.
print("Publication usability structure PASS; human print/reader proof remains open.")
