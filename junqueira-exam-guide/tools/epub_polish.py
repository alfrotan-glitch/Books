#!/usr/bin/env python3
"""Modern, accessible, reflowable EPUB presentation for the histology textbook.

The cover and CSS are original. Post-processing preserves EPUB 3 semantics,
reliable chapter navigation, and the reader's font / color preferences.
No fonts, third-party photographs or remote resources are embedded.
"""
from __future__ import annotations

import math
import os
from pathlib import Path
import random
import re
import shutil
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, ZIP_STORED

from lxml import etree as ET
from PIL import Image, ImageDraw, ImageFont

X = "http://www.w3.org/1999/xhtml"
E = "http://www.idpf.org/2007/ops"
O = "http://www.idpf.org/2007/opf"
D = "http://purl.org/dc/elements/1.1/"
NS = {"x": X, "e": E, "o": O, "d": D}

MODERN_CSS = r"""
/* Basic Histology · original EPUB 3 reader-first design. */
@charset "UTF-8";
html { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }
body {
  font-family: Georgia, "Palatino Linotype", "Book Antiqua", serif;
  font-size: 1em; line-height: 1.58; margin: 0; padding: 0 1%;
  color: inherit; background: transparent;
  widows: 2; orphans: 2;
  -webkit-hyphens: auto; hyphens: auto;
}
p { margin: .45em 0 .78em; text-align: start; overflow-wrap: break-word; }
h1, h2, h3, h4 {
  font-family: -apple-system, BlinkMacSystemFont, "Avenir Next", "Segoe UI",
               "Liberation Sans", Arial, sans-serif;
  font-weight: 700; line-height: 1.23; text-align: start;
  -webkit-hyphens: none; hyphens: none; break-after: avoid;
  page-break-after: avoid;
}
h1 {
  font-size: 1.7em; letter-spacing: -.025em;
  margin: 1.6em 0 .55em; padding: 0 0 .35em;
  border-bottom: .12em solid #168986;
  break-before: page; page-break-before: always;
}
h2 {
  font-size: 1.42em; margin: 1.45em 0 .55em;
  padding-bottom: .28em; border-bottom: 1px solid #90B1B4;
}
h3 { font-size: 1.17em; margin: 1.45em 0 .45em; color: #087772; }
h4 { font-size: 1.03em; margin: 1.25em 0 .35em; }
h1 + p, h2 + p, h3 + p { margin-top: .3em; }
strong, b { font-weight: 700; }
a { color: #087772; text-decoration: underline; text-underline-offset: .12em; }
a:focus { outline: 2px solid #168986; outline-offset: 2px; }
ul, ol { margin: .45em 0 .85em; padding-left: 1.4em; }
li { padding-left: .06em; margin: .22em 0; }
li > ul, li > ol { margin-top: .2em; }
blockquote {
  margin: 1.05em 0; padding: .65em .85em;
  border-left: .23em solid #168986;
  background: #EAF4F3; color: #173C43;
  break-inside: avoid-page; page-break-inside: avoid;
}
blockquote p { margin: .2em 0; }
blockquote.note-clinical { border-left-color: #A86755; background: #F9EFE9; color: #4C352D; }
blockquote.note-micro { border-left-color: #176D99; background: #EAF2F8; color: #223E52; }
blockquote.note-mnemonic { border-left-color: #7458A1; background: #F1EDF7; color: #3D3153; }
blockquote.note-tip { border-left-color: #C38D35; background: #FAF3E4; color: #503D26; }
blockquote.note-pearl { border-left-color: #168986; background: #EAF4F3; color: #173C43; }
.table-scroll { max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 1em 0 1.2em; }
table {
  border-collapse: collapse; border-spacing: 0;
  margin: 0; width: 100%; max-width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
  font-size: .86em; line-height: 1.48;
  page-break-inside: auto;
}
thead { border-bottom: 2px solid #168986; }
th, td {
  padding: .5em .55em; vertical-align: top;
  border-bottom: 1px solid #C6D3D6;
  text-align: start; overflow-wrap: anywhere;
}
th { font-weight: 700; background: #E5F0F0; color: #173C43; }
tbody tr:nth-child(even) { background: #F2F7F7; }
tr { break-inside: avoid-page; page-break-inside: avoid; }
figure { margin: 1.25em 0 1.6em; text-align: center; break-inside: avoid-page; }
img, svg { max-width: 100%; height: auto; }
figcaption {
  font: .87em/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
  margin: .45em .15em; color: #53686C; text-align: center;
}
code, pre {
  font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
  font-size: .91em; white-space: pre-wrap; overflow-wrap: anywhere;
}
hr { border: 0; border-top: 1px solid #A8BDBE; margin: 1.5em 0; }
nav[epub|type~="toc"] > ol, nav ol.toc {
  padding-left: 1.2em; line-height: 1.5;
}
nav ol.toc li { margin: .43em 0; }
nav ol.toc ol li { margin: .24em 0; font-size: .95em; }
nav a { text-decoration: none; border-bottom: 1px solid #8CAFB1; }
section.titlepage { text-align: center; margin: 16% auto 0; max-width: 90%; }
.titlepage .title { font-size: 2.15em; border: 0; }
.titlepage .subtitle { font-size: 1.1em; }
@media (max-width: 36em) {
  body { padding: 0; }
  h1 { font-size: 1.47em; }
  h2 { font-size: 1.3em; }
  table { font-size: .83em; }
  th, td { padding: .38em .4em; }
  figure { margin: .9em 0 1.15em; }
}
@media (prefers-color-scheme: dark) {
  body { color: #E6F0F0; background: #14252B; }
  a, h3 { color: #85D5C9; }
  h1, thead { border-color: #62B8B0; }
  h2, th, td { border-color: #58686F; }
  th { background: #293F43; color: #E7F4F3; }
  tbody tr:nth-child(even) { background: #233539; }
  blockquote, blockquote.note-pearl { background: #17383C; color: #D5F0E9; }
  blockquote.note-clinical { background: #49332E; color: #FBE4D7; }
  blockquote.note-micro { background: #22394C; color: #D9ECF9; }
  blockquote.note-mnemonic { background: #3F3452; color: #EEE6F8; }
  blockquote.note-tip { background: #483B27; color: #F8EDCF; }
  figcaption { color: #B7CBCC; }
}
"""


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    return ImageFont.truetype(str(path) if path.exists() else name, size)


def build_cover(destination: str | Path) -> None:
    """Design an original high-resolution typographic/cellular cover."""
    w, h = 1600, 2400
    im = Image.new("RGB", (w, h), "#102835")
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(2026)
    # A subtle editorial grid and cellular matrix in the lower half.
    for x in range(100, w, 125):
        d.line(((x, 1060), (x, 2135)), fill=(125, 210, 207, 16), width=2)
    for y in range(1080, 2100, 125):
        d.line(((80, y), (1530, y)), fill=(125, 210, 207, 16), width=2)

    cells = [
        (1210, 1410, 340, "#116A75"),
        (740, 1760, 410, "#125268"),
        (1160, 1990, 320, "#AA646C"),
        (425, 2000, 235, "#137B81"),
        (1490, 1710, 195, "#BD7E73"),
    ]
    for cx, cy, rad, color in cells:
        d.ellipse((cx-rad, cy-rad, cx+rad, cy+rad), fill=color, outline=(177, 236, 220, 130), width=7)
        for _ in range(19):
            theta = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(.25, .73) * rad
            x, y = cx + math.cos(theta) * rr, cy + math.sin(theta) * rr
            sr = rng.uniform(4, 13)
            d.ellipse((x-sr, y-sr, x+sr, y+sr), fill=(213, 240, 224, 90))
        nr = rad * .28
        d.ellipse((cx-nr, cy-nr, cx+nr, cy+nr), fill=(240, 168, 143, 175), outline=(255, 218, 195, 165), width=7)
        d.ellipse((cx-10, cy-10, cx+10, cy+10), fill=(255, 243, 225, 185))

    # Deliberately restrained color blocks, with a strong thumbnail hierarchy.
    d.rounded_rectangle((104, 123, 825, 205), radius=22, fill=(24, 144, 145, 220))
    d.text((140, 139), "MEDICAL SCIENCE  /  LEARNING TEXT", font=_font(36, True), fill="#E7FCF5")
    d.text((100, 365), "BASIC", font=_font(165, True), fill="#FFF7ED")
    d.text((100, 555), "HISTOLOGY", font=_font(162, True), fill="#FFF7ED")
    d.rounded_rectangle((102, 787, 532, 800), radius=6, fill="#28BAAD")
    d.text((104, 870), "A Learning Text", font=_font(79), fill="#D5EFEB")
    d.text((106, 977), "Cells  ·  Tissues  ·  Organ Systems", font=_font(41), fill="#ABCACB")
    d.text((106, 2224), "ORIGINAL ILLUSTRATED EDITION", font=_font(37, True), fill="#EAF7F3")
    d.text((106, 2290), "2026   •   24 CHAPTERS   •   100 EXAM QUESTIONS", font=_font(29), fill="#AAC8C6")
    d.rectangle((0, h-20, w, h), fill="#23BBAF")
    im.save(destination, format="PNG", optimize=True)


def _xml(data: bytes) -> ET._Element:
    return ET.fromstring(data, parser=ET.XMLParser(resolve_entities=False, no_network=True))


def polish_epub(path: str | Path) -> None:
    """Add semantic reading aids; remove Pandoc-generated empty chapter pages.

    EPUB3 ZIP constraints are preserved (mimetype first, uncompressed).
    """
    path = Path(path)
    with ZipFile(path) as z:
        files = {item.filename: z.read(item.filename) for item in z.infolist()}
        original_order = z.namelist()

    removed: set[str] = set()
    illustration_destinations: list[tuple[str, str]] = []
    for name in original_order:
        if not name.startswith("EPUB/text/ch") or not name.endswith(".xhtml"):
            continue
        root = _xml(files[name])
        body = root.find(f"{{{X}}}body")
        if body is None:
            continue
        # Pandoc can create tiny synthetic link-anchor files between Parts.
        # They contain no readable words, headings or illustrations.
        visible_text = " ".join("".join(body.itertext()).split())
        has_heading = any(
            body.find(f".//{{{X}}}h{level}") is not None
            for level in (1, 2, 3, 4)
        )
        has_image = body.find(f".//{{{X}}}img") is not None
        if not visible_text and not has_heading and not has_image:
            removed.add(name)
            continue

        for table in root.findall(f".//{{{X}}}table"):
            for th in table.findall(f".//{{{X}}}thead//{{{X}}}th"):
                if "scope" not in th.attrib:
                    th.set("scope", "col")
            parent = table.getparent()
            if parent is not None:
                container = ET.Element(f"{{{X}}}div")
                container.set("class", "table-scroll")
                pos = parent.index(table)
                parent.remove(table)
                parent.insert(pos, container)
                container.append(table)

        for note in root.findall(f".//{{{X}}}blockquote"):
            beginning = " ".join(note.itertext()).lstrip().upper()
            for keyword in ("CLINICAL", "MICRO", "TIP", "MNEMONIC", "PEARL"):
                if beginning.startswith(keyword):
                    note.set("class", "note-" + keyword.lower())
                    break

        for fig in root.findall(f".//{{{X}}}figure"):
            if fig.find(f"{{{X}}}img") is not None:
                ix = len(illustration_destinations) + 1
                ident = f"illustration-{ix:02d}"
                fig.set("id", ident)
                caption = fig.find(f"{{{X}}}figcaption")
                title = " ".join(caption.itertext()).strip() if caption is not None else f"Illustration {ix}"
                illustration_destinations.append((f"{name.removeprefix('EPUB/')}" + "#" + ident, title))
        files[name] = ET.tostring(root, encoding="UTF-8", xml_declaration=True, doctype="<!DOCTYPE html>")

    # Modify package spine and manifest together, never leave phantom readers.
    opf_name = "EPUB/content.opf"
    opf = _xml(files[opf_name])
    manifest = opf.find(f"{{{O}}}manifest")
    spine = opf.find(f"{{{O}}}spine")
    removed_ids = set()
    for item in list(manifest):
        href = item.get("href", "")
        if "EPUB/" + href in removed:
            removed_ids.add(item.get("id"))
            manifest.remove(item)
    for item in list(spine):
        if item.get("idref") in removed_ids:
            spine.remove(item)
    metadata = opf.find(f"{{{O}}}metadata")
    # Avoid fabricated authors, publishers or ISBNs. Add discoverable subjects.
    if metadata is not None:
        dc_desc = ET.Element(f"{{{D}}}description")
        dc_desc.text = ("An original illustrated, reflowable microscopic anatomy learning text "
                        "covering 24 chapters, clinical correlations, nine teaching schematics, "
                        "guided slide practice and 100 explained exam questions.")
        metadata.append(dc_desc)
        for subject in ("Histology", "Microscopic anatomy", "Medical education"):
            el = ET.Element(f"{{{D}}}subject")
            el.text = subject
            metadata.append(el)
    files[opf_name] = ET.tostring(opf, encoding="UTF-8", xml_declaration=True)

    # EPUB 3 illustration list helps readers jump to the nine atlas schematics.
    nav_name = "EPUB/nav.xhtml"
    nav = _xml(files[nav_name])
    b = nav.find(f"{{{X}}}body")
    if b is not None and illustration_destinations:
        section = ET.SubElement(b, f"{{{X}}}nav")
        section.set(f"{{{E}}}type", "loi")
        # The heading names this navigation; aria-label is rejected on EPUB nav.
        h = ET.SubElement(section, f"{{{X}}}h2")
        h.text = "Illustrations"
        listing = ET.SubElement(section, f"{{{X}}}ol")
        for target, label in illustration_destinations:
            li = ET.SubElement(listing, f"{{{X}}}li")
            a = ET.SubElement(li, f"{{{X}}}a")
            a.set("href", target)
            a.text = label
    files[nav_name] = ET.tostring(nav, encoding="UTF-8", xml_declaration=True, doctype="<!DOCTYPE html>")

    with tempfile.NamedTemporaryFile(prefix="modern-epub-", suffix=".epub",
                                     dir=path.parent, delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        with ZipFile(temporary, "w") as out:
            out.writestr("mimetype", files["mimetype"], compress_type=ZIP_STORED)
            for name in original_order:
                if name == "mimetype" or name in removed:
                    continue
                out.writestr(name, files[name], compress_type=ZIP_DEFLATED, compresslevel=8)
        shutil.move(str(temporary), str(path))
    finally:
        temporary.unlink(missing_ok=True)
    print(f"EPUB polished: removed {len(removed)} empty reader pages; "
          f"{len(illustration_destinations)} figures indexed")
