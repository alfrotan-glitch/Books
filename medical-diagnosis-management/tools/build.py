#!/usr/bin/env python3
"""build.py — assemble chapters and produce PDF (via Typst), DOCX, EPUB.

Usage:
  python3 tools/build.py            # builds all three formats
  python3 tools/build.py pdf        # only PDF
  python3 tools/build.py docx       # only DOCX
  python3 tools/build.py epub       # only EPUB
"""
import os, re, sys, html, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ROOT / "chapters"
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
FONTS = ROOT / "fonts"
TEMPLATE = ROOT / "templates" / "book.typst"
OUT_NAME = "dari-internal-medicine"

CHAPTER_ORDER = None  # natural sort by filename prefix

NAVY, TEAL, GOLD = "0f2744", "136f73", "b8913a"

def chapter_files():
    files = [f for f in CHAPTERS.glob("*.md") if not f.name.startswith("_")]
    return sorted(files)

def join_with_parts(files):
    """Join chapter texts; insert a part-divider heading when the "> **بخش …**" label changes."""
    out, current = [], None
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = re.search(r"^> \*\*(بخش [^*]+)\*\*", text, re.M)
        label = m.group(1) if m else ("ضمایم" if f.name[:1] == "9" else current)
        if label and label != current:
            out.append(f"# {label}")
            current = label
        out.append(text)
    return "\n\n".join(out)

def assemble():
    BUILD.mkdir(exist_ok=True)
    master = join_with_parts(chapter_files())
    (BUILD / "master.md").write_text(master, encoding="utf-8")
    return master

# ─────────────────────────── shared markdown parse ───────────────────────────
def parse_blocks(md):
    """Yield (kind, payload) blocks from our constrained markdown subset."""
    lines = md.split("\n")
    i = 0
    blocks = []
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            blocks.append(("code", buf))
            continue
        if not s:
            i += 1; continue
        if s == "---":
            blocks.append(("hr", None)); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            blocks.append(("h%d" % len(m.group(1)), m.group(2))); i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i+1].strip()):
            tbl = [s]; i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            blocks.append(("table", tbl)); continue
        if s.startswith("- ") or s.startswith("* ") or s.startswith("+ "):
            blocks.append(("li", s[2:])); i += 1; continue
        m = re.match(r"^(\d+)[.)]\s+(.*)$", s)
        if m:
            blocks.append(("num", (m.group(1), m.group(2)))); i += 1; continue
        if s.startswith("> "):
            blocks.append(("quote", s[2:])); i += 1; continue
        blocks.append(("p", s)); i += 1
    return blocks

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")

def inline_html(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*([^*]+?)\*([^*]+?)\*\*\*", r"<strong>\1<em>\2</em></strong>", t)
    t = re.sub(r"\*\*\*([^*]+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+?)`", r"<code>\1</code>", t)
    t = LINK_RE.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t

def table_rows(tbl):
    def cells(row):
        row = row.strip()
        if row.startswith("|"): row = row[1:]
        if row.endswith("|"): row = row[:-1]
        return [c.strip() for c in row.split("|")]
    header = cells(tbl[0])
    body = [cells(r) for r in tbl[2:]]
    return header, body

# ─────────────────────────────────── PDF (typst) ─────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from md2typst import convert as md2typst

def title_page_typst(title_md: str) -> str:
    lines = title_md.split("\n")
    title = None
    rest_lines = []
    for ln in lines:
        if ln.startswith("# ") and title is None:
            title = ln[2:].strip()
        else:
            rest_lines.append(ln)
    out = ["#block(breakable: false)[",
           "  #v(3.2em)",
           '  #align(center, text(fill: rgb("#0f2744"), weight: "bold", size: 24pt)[%s])' % (title or ""),
           "  #v(0.9em)",
           '  #align(center, line(length: 55%, stroke: 1pt + rgb("#b8913a")))',
           "]"]
    rest = "\n".join(rest_lines)
    out.append(md2typst(rest))
    return "\n".join(out)

def build_pdf():
    import typst
    files = chapter_files()
    fm_text = files[0].read_text(encoding="utf-8")
    rest_md = join_with_parts(files[1:])
    # title page = frontmatter up to first '### '
    idx = fm_text.find("\n### ")
    title_md = fm_text[:idx] if idx != -1 else fm_text
    rest_fm = fm_text[idx + 1:] if idx != -1 else ""
    body = (title_page_typst(title_md)
            + "\n#pagebreak()\n#set page(numbering: \"i\", number-align: center)\n"
            + md2typst(rest_fm)
            + "\n#set page(numbering: \"1\", number-align: center)\n"
            + md2typst(rest_md))
    tpl = TEMPLATE.read_text(encoding="utf-8").replace('#include "__BOOK__"', body)
    src = BUILD / f"{OUT_NAME}.typ"
    src.write_text(tpl, encoding="utf-8")
    out = BUILD / f"{OUT_NAME}.pdf"
    typst.compile(str(src), output=str(out), root=str(ROOT), font_paths=[str(FONTS)], ignore_system_fonts=True)
    print(f"PDF: {out}")

# ───────────────────────────────────── DOCX ──────────────────────────────────
def build_docx():
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    md = assemble()
    doc = Document()
    # base style
    style = doc.styles["Normal"]
    style.font.name = "Vazirmatn"
    style.font.size = Pt(10.5)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Vazirmatn")
    for sec in doc.sections:
        sec.top_margin = Cm(2.1); sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(1.7); sec.right_margin = Cm(1.7)

    def set_rtl(p):
        pPr = p._p.get_or_add_pPr()
        bidi = OxmlElement("w:bidi"); bidi.set(qn("w:val"), "1")
        pPr.append(bidi)

    def add_runs(p, text):
        # parse inline **bold** *italic* `code`
        text = text.replace("***", "**")
        text = LINK_RE.sub(lambda m: m.group(1), text)  # DOCX: link text only (URL kept in source/EPUB/PDF)
        pos = 0
        for m in re.finditer(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", text):
            if m.start() > pos:
                r = p.add_run(text[pos:m.start()]); r.font.name = "Vazirmatn"
            tok = m.group(0)
            if tok.startswith("**"):
                r = p.add_run(tok[2:-2].replace("*", "")); r.bold = True
            elif tok.startswith("`"):
                r = p.add_run(tok[1:-1]); r.font.name = "Courier New"
            else:
                r = p.add_run(tok[1:-1]); r.italic = True
            r.font.name = "Vazirmatn"
            pos = m.end()
        if pos < len(text):
            r = p.add_run(text[pos:]); r.font.name = "Vazirmatn"

    def shade_cell(cell, hexcolor):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), hexcolor)
        tcPr.append(shd)

    blocks = parse_blocks(md)
    for kind, payload in blocks:
        if kind == "h1":
            p = doc.add_paragraph(); p.style = doc.styles["Heading 1"]; p.paragraph_format.page_break_before = True; p.paragraph_format.space_before = Pt(0); set_rtl(p)
            r = p.add_run(payload.replace("*", "")); r.bold = True; r.font.size = Pt(19); r.font.color.rgb = RGBColor.from_string(TEAL); r.font.name = "Vazirmatn"
            p2 = doc.add_paragraph(); set_rtl(p2)
            r2 = p2.add_run("❖ " * 20); r2.font.color.rgb = RGBColor.from_string(GOLD); r2.font.size = Pt(8)
        elif kind == "h2":
            p = doc.add_paragraph(); p.style = doc.styles["Heading 2"]; p.paragraph_format.space_before = Pt(14); set_rtl(p)
            r = p.add_run(payload.replace("*", "")); r.bold = True; r.font.size = Pt(14.5); r.font.color.rgb = RGBColor.from_string(NAVY); r.font.name = "Vazirmatn"
        elif kind == "h3":
            p = doc.add_paragraph(); p.style = doc.styles["Heading 3"]; p.paragraph_format.space_before = Pt(10); set_rtl(p)
            r = p.add_run(payload.replace("*", "")); r.bold = True; r.font.size = Pt(12.5); r.font.color.rgb = RGBColor.from_string(TEAL); r.font.name = "Vazirmatn"
        elif kind == "h4":
            p = doc.add_paragraph(); p.style = doc.styles["Heading 4"]; p.paragraph_format.space_before = Pt(8); set_rtl(p)
            r = p.add_run(payload.replace("*", "")); r.bold = True; r.font.size = Pt(11.5); r.font.name = "Vazirmatn"
        elif kind == "p":
            p = doc.add_paragraph(); set_rtl(p); add_runs(p, payload)
        elif kind == "li":
            p = doc.add_paragraph(); p.paragraph_format.right_indent = Cm(0.6); set_rtl(p)
            r = p.add_run("● "); r.font.color.rgb = RGBColor.from_string(TEAL)
            add_runs(p, payload)
        elif kind == "num":
            p = doc.add_paragraph(); p.paragraph_format.right_indent = Cm(0.6); set_rtl(p)
            r = p.add_run(f"{payload[0]}. "); r.bold = True; r.font.color.rgb = RGBColor.from_string(TEAL)
            add_runs(p, payload[1])
        elif kind == "quote":
            p = doc.add_paragraph(); p.paragraph_format.right_indent = Cm(0.5); p.paragraph_format.left_indent = Cm(0.5); set_rtl(p)
            add_runs(p, payload)
            for r in p.runs:
                r.font.color.rgb = RGBColor.from_string(NAVY)
        elif kind == "code":
            for cl in payload:
                p = doc.add_paragraph(); set_rtl(p)
                p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.right_indent = Cm(0.4); p.paragraph_format.left_indent = Cm(0.4)
                r = p.add_run(cl if cl else " "); r.font.size = Pt(9.5); r.font.name = "Vazirmatn"
        elif kind == "table":
            header, rows = table_rows(payload)
            n = len(header)
            t = doc.add_table(rows=1, cols=n)
            t.style = "Table Grid"
            for j, htxt in enumerate(header):
                cell = t.rows[0].cells[j]
                cell.text = ""
                p = cell.paragraphs[0]; set_rtl(p)
                r = p.add_run(htxt.replace("*", "")); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(9.5)
                shade_cell(cell, TEAL)
            for row in rows:
                cells = t.add_row().cells
                for j in range(n):
                    cell = cells[j]
                    txt = row[j] if j < len(row) else ""
                    cell.text = ""
                    p = cell.paragraphs[0]; set_rtl(p)
                    add_runs(p, txt)
                    for r in p.runs:
                        r.font.size = Pt(9)
        elif kind == "hr":
            p = doc.add_paragraph(); set_rtl(p)
            r = p.add_run("❖ ❖ ❖"); r.font.color.rgb = RGBColor.from_string(GOLD)
    out = BUILD / f"{OUT_NAME}.docx"
    doc.save(str(out))
    print(f"DOCX: {out}")

# ───────────────────────────────────── EPUB ──────────────────────────────────
EPUB_CSS = """
body { direction: rtl; text-align: right; font-family: "Vazirmatn", serif; line-height: 1.9; font-size: 10pt; }
h1 { color: #136f73; font-size: 20pt; border-bottom: 2.5pt solid #0f2744; padding-bottom: 4pt; page-break-before: always; }
h1::after { content: "❖ ❖ ❖  ❖ ❖ ❖  ❖ ❖"; display: block; color: #b8913a; font-size: 7pt; letter-spacing: 3pt; margin-top: 6pt; }
h2 { color: #0f2744; font-size: 15pt; border-bottom: 1pt solid #b8913a; padding-bottom: 2pt; margin-top: 1.4em; }
h3 { color: #136f73; font-size: 12.5pt; margin-top: 1.1em; }
h4 { font-size: 11pt; margin-top: 0.9em; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 8.5pt; }
th { background: #136f73; color: #fff; padding: 4pt 6pt; border: 0.5pt solid #9fb8bb; text-align: right; }
td { padding: 4pt 6pt; border: 0.5pt solid #9fb8bb; }
tr:nth-child(even) td { background: #eef5f5; }
ul, ol { margin: 0.5em 0; }
li { margin: 0.25em 1.2em; }
ul li::marker { content: "●  "; color: #136f73; }
blockquote { background: #f2f7f4; border-right: 3pt solid #136f73; padding: 6pt 10pt; color: #0f2744; margin: 0.8em 0; }
pre { background: #f4f7f7; border: 0.5pt solid #cfdede; padding: 8pt; font-size: 8.5pt; white-space: pre-wrap; direction: rtl; }
strong { color: #0f2744; }
hr { border: none; border-top: 1pt solid #b8913a; margin: 1em 0; }
code { font-family: monospace; }
"""

def md_to_xhtml(md):
    blocks = parse_blocks(md)
    out = []
    for kind, payload in blocks:
        if kind == "h1": out.append(f"<h1>{inline_html(payload)}</h1>")
        elif kind == "h2": out.append(f"<h2>{inline_html(payload)}</h2>")
        elif kind == "h3": out.append(f"<h3>{inline_html(payload)}</h3>")
        elif kind == "h4": out.append(f"<h4>{inline_html(payload)}</h4>")
        elif kind == "p": out.append(f"<p>{inline_html(payload)}</p>")
        elif kind == "li": out.append(f"<li>{inline_html(payload)}</li>")
        elif kind == "num": out.append(f"<numitem>{payload[0]}. {inline_html(payload[1])}</numitem>")
        elif kind == "quote": out.append(f"<blockquote>{inline_html(payload)}</blockquote>")
        elif kind == "code":
            out.append("<pre>" + html.escape("\n".join(payload)) + "</pre>")
        elif kind == "table":
            header, rows = table_rows(payload)
            t = ["<table><tr>"]
            for htxt in header: t.append(f"<th>{inline_html(htxt)}</th>")
            t.append("</tr>")
            for row in rows:
                n = len(header)
                t.append("<tr>")
                for j in range(n):
                    t.append(f"<td>{inline_html(row[j] if j < len(row) else '')}</td>")
                t.append("</tr>")
            t.append("</table>")
            out.append("".join(t))
        elif kind == "hr": out.append("<hr/>")
    # group consecutive <li> into <ul>; numbered items as paragraphs (XHTML-valid)
    res, in_ul = [], False
    for x in out:
        if x.startswith("<li>"):
            if not in_ul: res.append("<ul>"); in_ul = True
        elif in_ul:
            res.append("</ul>"); in_ul = False
        res.append(x.replace("<numitem>", '<p class="num">').replace("</numitem>", "</p>"))
    if in_ul: res.append("</ul>")
    return "\n".join(res)

def build_epub():
    md = assemble()
    files = []
    # split into chapters at h1
    chapters = re.split(r"(?m)^# ", md)
    chap_files = []
    for idx, ch in enumerate(chapters):
        if not ch.strip():
            continue
        title = ch.split("\n", 1)[0].strip()
        fid = f"ch{idx:03d}"
        xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" dir="rtl" lang="fa">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{md_to_xhtml(ch if idx == 0 else "# " + ch)}
</body>
</html>"""
        chap_files.append((f"{fid}.xhtml", xhtml, title))
    # package
    manifest = []
    toc_entries = []
    spine = []
    for i, (fname, xhtml, title) in enumerate(chap_files):
        idf = fname[:-6]
        manifest.append(f'  <item id="{idf}" href="{fname}" media-type="application/xhtml+xml"/>')
        toc_entries.append(f'    <li><a href="{fname}">{html.escape(title)}</a></li>')
        spine.append(f'  <itemref idref="{idf}"/>')
    manifest.insert(0, '  <item id="css" href="style.css" media-type="text/css"/>')
    manifest.append('  <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

    package = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="fa">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:uuid:2b8d9a41-7c3e-4f1d-9e6a-dari0120260924</dc:identifier>
    <dc:title>رهنمای جامع تشخیص و اهتمامات طب داخلی</dc:title>
    <dc:creator>تیم بورد تخصصی طب داخلی افغانستان</dc:creator>
    <dc:language>fa-AF</dc:language>
    <dc:date>2026-09-24</dc:date>
    <meta property="dcterms:modified">2026-09-24T00:00:00Z</meta>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine page-progression-direction="rtl">
{chr(10).join(spine)}
  </spine>
</package>"""
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" dir="rtl" lang="fa">
<head><meta charset="utf-8"/><title>فهرست مطالب</title></head>
<body><nav epub:type="toc" id="toc">
<ol>
{chr(10).join(toc_entries)}
</ol>
</nav></body>
</html>"""
    out = BUILD / f"{OUT_NAME}.epub"
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo("mimetype"); zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/epub+zip")
        z.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEPUB/package.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""")
        z.writestr("OEPUB/package.opf", package)
        z.writestr("OEPUB/nav.xhtml", nav)
        z.writestr("OEPUB/style.css", EPUB_CSS)
        for fname, xhtml, title in chap_files:
            z.writestr(f"OEPUB/{fname}", xhtml)
    print(f"EPUB: {out}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    # appendix 95 is always regenerated from the chapters, so it can never go stale
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_references.py")], check=True)
    if target in ("all", "pdf"): build_pdf()
    if target in ("all", "docx"): build_docx()
    if target in ("all", "epub"): build_epub()
