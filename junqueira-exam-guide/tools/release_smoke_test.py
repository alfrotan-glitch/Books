"""Automated structural smoke tests for all four publication formats.

These tests cannot replace independent scientific review or a visual print proof.
"""
from pathlib import Path
from zipfile import ZipFile
import re
import sys
import pymupdf
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Basic_Histology_Learning_Text"
EXPECTED = {ext: BASE.with_suffix(ext) for ext in (".pdf", ".docx", ".epub", ".html")}
for ext, path in EXPECTED.items():
    assert path.is_file() and path.stat().st_size > 1000, f"Missing or empty {ext}: {path}"

pdf = pymupdf.open(EXPECTED[".pdf"])
assert (pdf.metadata.get("title") or "").strip() == "Basic Histology: A Learning Text", (
    "PDF must include title metadata for library catalogs and accessibility"
)
assert len(pdf) >= 50, f"Unexpectedly short PDF: {len(pdf)} pages"
page_text = [p.get_text() for p in pdf]
assert all(len(t.strip()) >= 35 for t in page_text), "Blank or nearly blank PDF page detected"
assert len(pdf.get_toc()) >= 20, "Missing PDF bookmarks"
atlas_sources = sorted((ROOT / "build" / "atlas").glob("*.png"))
assert len(atlas_sources) == 9, f"Expected nine original atlas plates, got {len(atlas_sources)}"
pdf_images = sum(len(page.get_images(full=True)) for page in pdf)
assert pdf_images >= 9, f"Only {pdf_images} embedded PDF images; schematic atlas appears incomplete"
out_of_page = []
broken_glyphs = []
for number, page in enumerate(pdf, start=1):
    for word in page.get_text("words"):
        x0, y0, x1, y1 = word[:4]
        if x0 < -2 or y0 < -2 or x1 > page.rect.width + 2 or y1 > page.rect.height + 2:
            out_of_page.append((number, (round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1))))
    if "\uFFFD" in page_text[number - 1]:
        broken_glyphs.append(number)
assert not out_of_page, f"Words outside PDF page bounds: {out_of_page[:8]}"
assert not broken_glyphs, f"Unicode replacement glyphs on PDF pages: {broken_glyphs}"

assert "Histology" in " ".join(page_text[:4]), "Missing title/front matter"
assert any("Appendix" in t for t in page_text), "Missing appendices"
assert any("24" in t and "review" in t.lower() for t in page_text), "Missing rapid-review chapter"
print(f"PDF PASS: {len(pdf)} pages, {len(pdf.get_toc())} bookmarks")

doc = Document(EXPECTED[".docx"])
assert len(doc.paragraphs) >= 100, "DOCX appears incomplete"
assert len(doc.tables) >= 10, "DOCX tables missing"
assert len(doc.inline_shapes) >= 9, f"DOCX atlas incomplete: {len(doc.inline_shapes)} inline images"
assert any(p.paragraph_format.page_break_before for p in doc.paragraphs
           if p.style.name == "Heading 1" and p.text.startswith("PART VII")), (
    "DOCX Part VII must open on a new page"
)
mcq_options = [p.text for p in doc.paragraphs if "Nuclei and rough endoplasmic reticulum" in p.text]
assert mcq_options and ("\nB." in mcq_options[0]), (
    "DOCX multiple-choice options ran together instead of separate lines"
)
print(f"DOCX PASS: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")

html = EXPECTED[".html"].read_text(encoding="utf-8")
assert re.search(r"<html\b", html, re.I), "HTML document element missing"
assert "Histology" in html and "</html>" in html.lower(), "HTML title/end missing"
assert len(html) >= 50000, "HTML unexpectedly small"
assert "max-width:100%" in html or "max-width: 100%" in html, "Responsive image CSS missing"
assert "overflow-x:auto" in html or "overflow-x: auto" in html, "Mobile table scrolling CSS missing"
html_plates = len(re.findall(r"<img\b", html, flags=re.I))
assert html_plates >= 9, f"HTML atlas incomplete: {html_plates} images"
print(f"HTML PASS: {len(html)} characters")

with ZipFile(EXPECTED[".epub"]) as z:
    names = z.namelist()
    assert "mimetype" in names and z.read("mimetype") == b"application/epub+zip"
    assert any(name.endswith(".opf") for name in names), "EPUB package document missing"
    assert any(name.endswith(".xhtml") for name in names), "EPUB reading content missing"
    assert z.testzip() is None, "Corrupt EPUB archive member"
    epub_images = [name for name in names if name.lower().endswith(".png")]
    assert len(epub_images) >= 10, f"EPUB atlas/cover images missing: {epub_images}"
print(f"EPUB PASS: {len(names)} archive members")
print("Nine original schematic atlas plates present in PDF, DOCX, HTML and EPUB.")
print("Structural checks passed; scientific and visual release checks remain separate.")
