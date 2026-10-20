#!/usr/bin/env python3
"""
Build the histology text into a print-ready PDF.

    python3 build.py

Source files live in src/ and are concatenated in filename order.
"""

import os
import re
import glob
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, NextPageTemplate, Flowable,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT_PDF = os.path.join(HERE, "Basic_Histology_Learning_Text.pdf")

PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 46, 46, 52, 46
FRAME_W = PAGE_W - ML - MR

# ---------------------------------------------------------------- palette
INK      = colors.HexColor("#17242C")
MUTED    = colors.HexColor("#5A6B75")
ACCENT   = colors.HexColor("#0E6B6B")
ACCENT_L = colors.HexColor("#DCEBEA")
RUST     = colors.HexColor("#A8481F")
RULE     = colors.HexColor("#C9D5DB")
ZEBRA    = colors.HexColor("#F4F7F8")
PAPER    = colors.HexColor("#FFFFFF")

PART_DESC = {
    "PART I":   "Chapters 1–3  ·  microscopy, the cytoplasm, and the nucleus",
    "PART II":  "Chapters 4–10  ·  the four basic tissues and their specializations",
    "PART III": "Chapters 11–14  ·  circulation, blood, hemopoiesis, and immunity",
    "PART IV":  "Chapters 15–18  ·  gut, liver, pancreas, lung, and skin",
    "PART V":   "Chapters 19–23  ·  kidney, endocrine glands, and the reproductive systems",
    "PART VI":  "Chapter 24, the master tables, and the reference appendices",
    "PART VII": "One hundred examination questions with explained answers",
    "APPENDIX C": "The book's own stain appendix, with the chemistry and use of every stain in the atlas",
}

CALLOUTS = {
    "CLINICAL": (colors.HexColor("#FBEAE7"), colors.HexColor("#A6392B"), "Clinical correlation"),
    "MICRO":    (colors.HexColor("#E4F1F0"), colors.HexColor("#0E6B6B"), "Under the microscope"),
    "TIP":      (colors.HexColor("#FCF2DA"), colors.HexColor("#9A6A12"), "Exam tip"),
    "MNEMONIC": (colors.HexColor("#EEEAF8"), colors.HexColor("#564189"), "Memory hook"),
    "PEARL":    (colors.HexColor("#E8EFF6"), colors.HexColor("#2B5C8A"), "High-yield pearl"),
}

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Body", os.path.join(FONT_DIR, "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("Body-Bold", os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold",
                              italic="Body", boldItalic="Body-Bold")
pdfmetrics.registerFont(TTFont("Head", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Head-Reg", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily("Head", normal="Head-Reg", bold="Head", italic="Head-Reg")
pdfmetrics.registerFontFamily("Head-Reg", normal="Head-Reg", bold="Head")


# ---------------------------------------------------------------- styles
def S(name, **kw):
    base = dict(fontName="Body", fontSize=9.5, leading=13.6, textColor=INK,
                spaceBefore=0, spaceAfter=5, alignment=TA_JUSTIFY)
    base.update(kw)
    return ParagraphStyle(name, **base)


STY = {
    "part_label": S("part_label", fontName="Head", fontSize=9, leading=12,
                    textColor=ACCENT, alignment=TA_LEFT, spaceAfter=6),
    "part_title": S("part_title", fontName="Head", fontSize=23, leading=29,
                    textColor=INK, alignment=TA_LEFT, spaceAfter=10),
    "chapter":    S("chapter", fontName="Head", fontSize=17, leading=22,
                    textColor=INK, alignment=TA_LEFT, spaceBefore=0, spaceAfter=3),
    "h3":         S("h3", fontName="Head", fontSize=11, leading=14.5,
                    textColor=ACCENT, alignment=TA_LEFT, spaceBefore=11, spaceAfter=4,
                    keepWithNext=1),
    "h4":         S("h4", fontName="Head-Reg", fontSize=9.8, leading=13,
                    textColor=INK, alignment=TA_LEFT, spaceBefore=8, spaceAfter=2,
                    keepWithNext=1),
    "body":       S("body"),
    "lead":       S("lead", fontName="Head-Reg", fontSize=9.6, leading=14,
                    textColor=INK),
    "boldlead":   S("boldlead", fontName="Head", fontSize=10, leading=13.5,
                    textColor=INK, alignment=TA_LEFT, spaceBefore=9, spaceAfter=3),
    "bullet":     S("bullet", leftIndent=13, bulletIndent=2, spaceAfter=2.5,
                    alignment=TA_LEFT),
    "num":        S("num", leftIndent=17, bulletIndent=2, spaceAfter=2.5,
                    alignment=TA_LEFT),
    "quote":      S("quote", fontName="Body", fontSize=9.3, leading=13.2,
                    alignment=TA_LEFT, leftIndent=9, rightIndent=9,
                    spaceBefore=8, spaceAfter=8),
    "toc0":       S("toc0", fontName="Head", fontSize=9.0, leading=10.6,
                    textColor=INK, alignment=TA_LEFT, spaceBefore=2.2),
    "toc1":       S("toc1", fontName="Head-Reg", fontSize=8.3, leading=8.9,
                    textColor=MUTED, leftIndent=12, alignment=TA_LEFT),
    "cell":       S("cell", fontName="Head-Reg", fontSize=7.9, leading=10.1,
                    alignment=TA_LEFT, spaceAfter=0),
    "cellhead":   S("cellhead", fontName="Head", fontSize=7.9, leading=10.1,
                    alignment=TA_LEFT, textColor=colors.white, spaceAfter=0),
    "source":     S("source", fontName="Head-Reg", fontSize=7.9, leading=11.4,
                    textColor=MUTED, alignment=TA_LEFT, spaceBefore=1, spaceAfter=9),
    "caption":    S("caption", fontName="Head-Reg", fontSize=7.6, leading=10,
                    textColor=MUTED, alignment=TA_LEFT, spaceBefore=2, spaceAfter=9),
}


# ---------------------------------------------------------------- inline md
def inline(text, bold="Body-Bold", base="Body"):
    """Convert a subset of inline markdown into reportlab paragraph markup.

    Bold is emitted as an explicit <font> tag rather than <b>: with these
    font families ReportLab can leak a <b> run across the short unstyled
    gaps between bold spans, which bolds whole sentences. A font tag
    switches back to the regular face reliably.
    """
    text = text.replace("&", "&amp;").replace("<br/>", "\x00BR\x00")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\x00BR\x00", "<br/>")
    text = re.sub(r"`([^`]+)`", r'<font name="Mono" size="8">\1</font>', text)
    parts = re.split(r"\*\*(.+?)\*\*", text)
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2:
            out.append('<font name="%s">%s</font>' % (bold, part))
        else:
            out.append('<font name="%s">%s</font>' % (base, part))
    text = "".join(out)
    text = re.sub(r"(?<![\*<])\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_sep(line):
    s = line.strip()
    if not s.startswith("|"):
        return False
    body = s.strip("|").replace(" ", "")
    return bool(body) and set(body) <= set("-:|")


# ---------------------------------------------------------------- blocks
def read_blocks():
    files = sorted(glob.glob(os.path.join(SRC, "*.md")))
    lines = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            lines.extend(fh.read().split("\n"))
        lines.append("")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and is_sep(lines[i + 1]):
            header = split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            blocks.append(("table", header, rows))
            continue
        if s.startswith(">"):
            q = []
            while i < n and lines[i].strip().startswith(">"):
                raw = lines[i].strip()[1:]
                if raw.startswith(" "):
                    raw = raw[1:]
                q.append(raw)
                i += 1
            while q and not q[-1].strip():
                q.pop()
            blocks.append(("quote", q))
            continue
        if s.startswith("# "):
            blocks.append(("part", s[2:].strip()))
            i += 1
            continue
        if s.startswith("## "):
            blocks.append(("chapter", s[3:].strip()))
            i += 1
            continue
        if s.startswith("### "):
            blocks.append(("h3", s[4:].strip()))
            i += 1
            continue
        if s.startswith("#### "):
            blocks.append(("h4", s[5:].strip()))
            i += 1
            continue
        if s == "---":
            blocks.append(("rule",))
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            items = []
            while i < n:
                mm_ = re.match(r"^(\d+)\.\s+(.*)$", lines[i].strip())
                if not mm_:
                    break
                items.append((mm_.group(1), mm_.group(2)))
                i += 1
            for num, txt in items:
                blocks.append(("num", num, txt))
            continue
        if s.startswith("- ") or s.startswith("* "):
            while i < n and (lines[i].strip().startswith("- ")
                             or lines[i].strip().startswith("* ")):
                blocks.append(("bullet", lines[i].strip()[2:]))
                i += 1
            continue
        para = [s]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith("#") or nxt.startswith("|")
                    or nxt.startswith(">") or nxt.startswith("- ")
                    or re.match(r"^\d+\.\s", nxt)):
                break
            para.append(nxt)
            i += 1
        blocks.append(("para", " ".join(para)))
    return blocks


# ---------------------------------------------------------------- tables
def make_table(header, rows):
    ncols = len(header)
    norm = []
    for r in rows:
        if len(r) < ncols:
            r = r + [""] * (ncols - len(r))
        elif len(r) > ncols:
            r = r[:ncols]
        norm.append(r)

    CHAR_W = 4.35          # approx width of one char at 7.9 pt DejaVu Sans
    PAD = 11.0
    mins, weights = [], []
    for c in range(ncols):
        vals = [header[c]] + [r[c] for r in norm]
        longest_word = max((len(w) for v in vals for w in v.split()), default=3)
        longest_cell = max((len(v) for v in vals), default=3)
        mins.append(longest_word * CHAR_W + PAD)
        weights.append(max(6.0, min(longest_cell, 200)) ** 0.75)

    # start from the minimum each column needs, then share out what is left
    floor_total = sum(mins)
    spare = FRAME_W - floor_total
    if spare <= 0:                       # degenerate: just scale the minimums
        widths = [FRAME_W * m / floor_total for m in mins]
    else:
        wsum = sum(weights)
        widths = [m + spare * (w / wsum) for m, w in zip(mins, weights)]

    data = [[Paragraph(inline(c, bold="Head"), STY["cellhead"]) for c in header]]
    for r in norm:
        data.append([Paragraph(inline(c, bold="Head"), STY["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(style))
    return t


class Rule(Flowable):
    def __init__(self, width, thickness=0.6, color=RULE, space=4):
        Flowable.__init__(self)
        self.width, self.thickness, self.color, self.space = width, thickness, color, space
        self.height = thickness + space * 2

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space, self.width, self.space)


# ---------------------------------------------------------------- builder
class Book(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=ML, rightMargin=MR,
                                 topMargin=MT, bottomMargin=MB,
                                 title="Basic Histology: A Learning Text",
                                 author="",
                                 subject="A self-contained course in microscopic anatomy",
                                 keywords="histology, medical education, examination revision, study guide")
        frame = Frame(ML, MB, FRAME_W, PAGE_H - MT - MB, id="body")
        self.cover_tpl = PageTemplate(id="cover", frames=[frame], onPage=self.cover)
        self.body_tpl = PageTemplate(id="body", frames=[frame], onPage=self.deco)
        self.addPageTemplates([self.cover_tpl, self.body_tpl])

    def beforeDocument(self):
        self._seen_part = False

    # -- page decoration
    def deco(self, canv, doc):
        canv.saveState()
        if doc.page <= 2:            # cover artwork and title page carry no folio
            canv.restoreState()
            return
        canv.setFont("Head-Reg", 7.4)
        canv.setFillColor(MUTED)
        canv.drawString(ML, PAGE_H - 30, "BASIC HISTOLOGY  ·  A LEARNING TEXT")
        canv.drawRightString(PAGE_W - MR, PAGE_H - 30, "First edition")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(ML, PAGE_H - 36, PAGE_W - MR, PAGE_H - 36)
        canv.line(ML, MB - 14, PAGE_W - MR, MB - 14)
        canv.setFont("Head", 8)
        canv.setFillColor(ACCENT)
        canv.drawCentredString(PAGE_W / 2, MB - 26, str(doc.page))
        canv.restoreState()

    def cover(self, canv, doc):
        canv.saveState()
        canv.setFillColor(INK)
        canv.rect(0, PAGE_H - 300, PAGE_W, 300, stroke=0, fill=1)
        canv.setFillColor(ACCENT)
        canv.rect(0, PAGE_H - 306, PAGE_W, 6, stroke=0, fill=1)

        canv.setFillColor(colors.HexColor("#6FD3CF"))
        canv.setFont("Head-Reg", 9.5)
        canv.drawString(ML, PAGE_H - 100, "A COMPLETE COURSE IN MICROSCOPIC ANATOMY")

        canv.setFillColor(colors.white)
        canv.setFont("Head", 38)
        canv.drawString(ML, PAGE_H - 152, "BASIC")
        canv.drawString(ML, PAGE_H - 192, "HISTOLOGY")

        canv.setFont("Head-Reg", 13)
        canv.setFillColor(colors.HexColor("#CFE3E2"))
        canv.drawString(ML, PAGE_H - 228, "A Learning Text")

        canv.setFillColor(INK)
        canv.setFont("Body", 12)
        canv.drawString(ML, PAGE_H - 360, "A self-contained course in microscopic anatomy,")
        canv.drawString(ML, PAGE_H - 378, "written for students who want to understand")
        canv.drawString(ML, PAGE_H - 396, "tissues, organs and the logic of their structure.")

        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.8)
        canv.line(ML, PAGE_H - 430, PAGE_W - MR, PAGE_H - 430)

        rows = [("23", "chapters"), ("100", "exam questions"),
                ("10", "master comparison tables"), ("1", "rapid-review chapter")]
        y = PAGE_H - 470
        for big, small in rows:
            canv.setFont("Head", 20)
            canv.setFillColor(ACCENT)
            canv.drawString(ML, y, big)
            canv.setFont("Head-Reg", 9)
            canv.setFillColor(INK)
            canv.drawString(ML + 46, y + 2, small)
            y -= 34

        canv.setFillColor(MUTED)
        canv.setFont("Head-Reg", 8.5)
        canv.drawString(ML, 58, "First edition  ·  Text only: no histological images are reproduced")
        canv.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = flowable.style.name
            if name == "part_title":
                self._seen_part = True
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))
                key = "part-%d" % self.page
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(), key, 0, 0)
            elif name == "chapter":
                # Front-matter headings sit at outline level 0; chapters nest under their part.
                outline = 1 if getattr(self, "_seen_part", False) else 0
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page))
                key = "ch-%d-%d" % (self.page, id(flowable) % 9999)
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(), key, outline, 0)


def group_blocks(blocks):
    """Keep a heading, its intro, and its bullets on one page when they fit.

    The 'Plates to study' lists at the end of each chapter are short; without this
    they can leave a heading and one orphaned bullet on a page of their own. The
    'Exam-style question' heading is likewise kept with its vignette and answer.
    """
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        head = b[1].strip().lower() if b[0] == "h3" else ""
        if head.startswith("plates to study"):
            group = [b]
            j = i + 1
            while j < len(blocks) and blocks[j][0] in ("para", "bullet"):
                group.append(blocks[j])
                j += 1
            out.append(("keep", group))
            i = j
            continue
        if head.startswith("exam-style question"):
            # Keep the heading with its vignette, options and answer so the
            # heading is never stranded at the foot of a page.
            group = [b]
            j = i + 1
            while j < len(blocks) and blocks[j][0] in ("para", "bullet", "num"):
                group.append(blocks[j])
                j += 1
            out.append(("keep", group))
            i = j
            continue
        if b[0] in ("h3", "h4") and i + 1 < len(blocks) and blocks[i + 1][0] in (
                "para", "bullet", "num", "table", "quote"):
            out.append(("keep", [b, blocks[i + 1]]))
            i += 2
            continue
        out.append(b)
        i += 1
    return out


def build_story(blocks):
    story = []
    first_part = True

    def brk():
        """Insert a page break unless we just inserted one."""
        if story and isinstance(story[-1], PageBreak):
            return
        story.append(PageBreak())

    for b in blocks:
        kind = b[0]

        if kind == "keep":
            inner = build_story(b[1])
            if inner:
                story.append(KeepTogether(inner))
            continue

        if kind == "part":
            title = b[1]
            if first_part:
                first_part = False
                continue
            brk()
            story.append(Spacer(1, 130))
            story.append(Rule(FRAME_W, 0.8, RULE, space=2))
            story.append(Spacer(1, 10))
            story.append(Paragraph(inline(title, bold="Head"), STY["part_title"]))
            desc = PART_DESC.get(title.split("—")[0].strip())
            if desc:
                story.append(Spacer(1, 2))
                story.append(Paragraph(desc, S("partdesc", fontName="Head-Reg", fontSize=10,
                                               leading=15, textColor=MUTED,
                                               alignment=TA_LEFT)))
            brk()
            first_part = False

        elif kind == "chapter":
            if not first_part:
                brk()
            story.append(Spacer(1, 2))
            story.append(Paragraph(inline(b[1], bold="Head"), STY["chapter"]))
            story.append(Rule(FRAME_W, 1.6, ACCENT, space=5))
            story.append(Spacer(1, 3))
            first_part = False

        elif kind == "h3":
            story.append(Paragraph(inline(b[1], bold="Head"), STY["h3"]))

        elif kind == "h4":
            story.append(Paragraph(inline(b[1], bold="Head"), STY["h4"]))

        elif kind == "para":
            txt = b[1]
            m = re.match(r"^\*\*pp\.\s*([0-9\u2013\-]+)\*\*\s*\u00b7\s*(.*)$", txt.strip())
            if m:
                pages = m.group(1).replace("-", "\u2013")
                story.append(Paragraph(
                    '<font name="Head" size="7.4" color="#0E6B6B">BOOK PAGES %s</font>'
                    '&nbsp;&nbsp;<font color="#C9D5DB">|</font>&nbsp;&nbsp;%s'
                    % (pages, inline(m.group(2), bold="Head")), STY["source"]))
            elif re.fullmatch(r"\*\*[^*]{2,90}\*\*", txt.strip()):
                story.append(Paragraph(inline(txt, bold="Head"), STY["boldlead"]))
            elif re.match(r"^\*\*\d+\.", txt):
                opts = re.split(r"\s+(?=[A-D]\.\s)", txt)
                if len(opts) == 5:                      # a multiple-choice question
                    story.append(Paragraph(inline(opts[0]),
                                           S("q", spaceBefore=7, spaceAfter=2,
                                             alignment=TA_LEFT)))
                    lines = "<br/>".join(inline(o) for o in opts[1:])
                    story.append(Paragraph(lines, S("opts", fontSize=9.2, leading=13.2,
                                                    leftIndent=16, spaceAfter=6,
                                                    alignment=TA_LEFT)))
                else:                                   # an answer key entry
                    story.append(Paragraph(inline(txt), S("a", spaceBefore=4.2,
                                                          spaceAfter=1.5,
                                                          alignment=TA_LEFT)))
            else:
                story.append(Paragraph(inline(txt), STY["body"]))

        elif kind == "bullet":
            story.append(Paragraph(inline(b[1]), STY["bullet"], bulletText="\u2022"))

        elif kind == "num":
            story.append(Paragraph(inline(b[2]), STY["num"], bulletText=b[1] + "."))

        elif kind == "rule":
            story.append(Rule(FRAME_W, 0.6, RULE, space=7))

        elif kind == "table":
            story.append(Spacer(1, 3))
            story.append(make_table(b[1], b[2]))
            story.append(Spacer(1, 9))

        elif kind == "quote":
            qlines = b[1]
            head = qlines[0] if qlines else ""
            m = re.match(r"^\*\*(CLINICAL|MICRO|TIP|MNEMONIC|PEARL)\*\*\s*[—\-·:]?\s*(.*)$", head)
            if m:
                kind_name, rest = m.group(1), m.group(2)
                bg, bar, label = CALLOUTS[kind_name]
                body = []
                if rest:
                    body.append(rest)
                body.extend(qlines[1:])
                text = "<br/>".join(x for x in body)
                text = text.replace("<br/><br/>", "<br/><br/>")
                txt = ('<font name="Head" size="7.6" color="%s">%s</font><br/>'
                       '<font name="Body" size="9.0">%s</font>'
                       % (bar.hexval().replace("0x", "#"), label.upper(), inline(text)))
                p = Paragraph(txt, ParagraphStyle(
                    "callout", parent=STY["quote"], backColor=bg,
                    borderColor=bar, borderWidth=0, leftIndent=0, rightIndent=0,
                    borderPadding=(6, 8, 6, 8), spaceBefore=8, spaceAfter=9))
                story.append(KeepTogether([p]))
            else:
                txt = "<br/>".join(inline(x) for x in qlines)
                story.append(Paragraph(txt, STY["quote"]))

    return story


def build_pdf():
    blocks = group_blocks(read_blocks())
    doc = Book(OUT_PDF)
    toc = TableOfContents()
    toc.levelStyles = [STY["toc0"], STY["toc1"]]
    toc.dotsMinLevel = 99

    imprint = (
        "This is an independent teaching text. Its prose is original; no images, plates, "
        "captions or extended passages from another publication are reproduced. Histological "
        "facts are part of the common scientific literature, and where authorities differ the "
        "text says so rather than hiding the difference. The book is not a clinical manual and "
        "does not replace laboratory instruction or medical training. Rights in this text have "
        "not been assigned; commercial distribution requires a license and an ISBN."
    )

    front = [
        NextPageTemplate("body"),
        PageBreak(),
        Spacer(1, 64),
        Paragraph("BASIC HISTOLOGY", S("tp1", fontName="Head", fontSize=34, leading=38,
                                       textColor=INK)),
        Spacer(1, 6),
        Paragraph("A Learning Text", S("tp2", fontName="Head-Reg", fontSize=17,
                                                        leading=22, textColor=ACCENT)),
        Spacer(1, 14),
        Rule(FRAME_W, 1.2, ACCENT),
        Spacer(1, 16),
        Paragraph("A self-contained course in microscopic anatomy for students of medicine, "
                  "dentistry and the biomedical sciences",
                  S("tp3", fontName="Body", fontSize=12, leading=18, textColor=INK)),
        Spacer(1, 4),
        Paragraph("First edition  \u00b7  2026", S("tp4", fontName="Head-Reg", fontSize=10,
                                                   leading=16, textColor=MUTED)),
        Spacer(1, 34),
        Paragraph("HOW THIS BOOK IS ORGANIZED", S("tg", fontName="Head", fontSize=7.6,
                                                   leading=11, textColor=ACCENT)),
        Spacer(1, 7),
        Paragraph(
            "Part I  ·  Cells and techniques: microscopy, the cytoplasm, the nucleus<br/>"
            "Part II  ·  The four basic tissues: epithelium, connective tissue, adipose, cartilage, bone, nerve, muscle<br/>"
            "Part III  ·  Transport, defense, and blood: circulation, blood, hemopoiesis, immunity<br/>"
            "Part IV  ·  Digestion and respiration: gut, associated organs, respiratory system, skin<br/>"
            "Part V  ·  Excretion and reproduction: urinary system, endocrine glands, male and female reproductive systems, eye and ear<br/>"
            "Part VI  ·  Rapid review, master tables, stains, vocabulary, and sources<br/>"
            "Part VII  ·  One hundred examination questions with explained answers",
            S("tgl", fontName="Head-Reg", fontSize=8.3, leading=13.2, textColor=INK)),
        Spacer(1, 120),
        Paragraph(imprint, S("imp", fontName="Head-Reg", fontSize=8, leading=11.5,
                             textColor=MUTED, alignment=TA_JUSTIFY)),
        PageBreak(),
        Spacer(1, 2),
        Paragraph("Contents", S("toctitle", fontName="Head", fontSize=20, leading=25,
                                textColor=INK, alignment=TA_LEFT, spaceAfter=6)),
        Rule(FRAME_W, 1.2, ACCENT),
        Spacer(1, 6),
        toc,
    ]
    story = build_story(blocks)
    doc.multiBuild(front + story)
    print("PDF written:", OUT_PDF)


if __name__ == "__main__":
    build_pdf()
