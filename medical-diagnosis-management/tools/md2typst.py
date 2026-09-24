#!/usr/bin/env python3
"""md2typst.py — convert the book's constrained Markdown subset to Typst.

Supported subset (all chapter files must respect this):
  # h1 (chapter), ## h2, ### h3, #### h4
  paragraphs, "- " bullets, "1." ordered lists
  pipe tables with header row
  fenced ``` code blocks (algorithms / text diagrams)
  > blockquotes
  --- horizontal rule
  inline: **bold**, *italic*, `code`

Styling lives in templates/book.typst (show rules), not in this file.
"""
import sys, re

# Typst special chars in TEXT mode that must be backslash-escaped.
# Parentheses ( ) are NOT special in Typst text — leave them alone.
# < > must be escaped (label syntax)
ESC = str.maketrans({c: "\\" + c for c in "#$@\\{}[]^<>"})

def esc(t: str) -> str:
    return t.translate(ESC)

def inline(t: str) -> str:
    """Escape specials; keep **bold** *italic* `code` verbatim (Typst handles them)."""
    parts = re.split(r"(`[^`]+`)", t)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 2:
            out.append(p)
        else:
            s = esc(p)
            s = s.replace('//', '\/\/').replace('/*', '\/*').replace('*/', '*\/')
            out.append(s)
    return "".join(out)

def table_rows(tbl):
    def cells(row):
        row = row.strip()
        if row.startswith("|"): row = row[1:]
        if row.endswith("|"): row = row[:-1]
        return [c.strip() for c in row.split("|")]
    header = cells(tbl[0])
    body = [cells(r) for r in tbl[2:]]
    n = len(header)
    body = [row + [""] * (n - len(row)) for row in body]
    return header, body

def md_table_to_typst(tbl):
    header, rows = table_rows(tbl)
    n = len(header)
    cols = ", ".join(["auto"] * n)
    out = ["#figure(",
           f"  table(columns: ({cols}),",
           '    stroke: 0.5pt + rgb("#9fb8bb"),',
           "    inset: (x: 5pt, y: 4pt),",
           '    fill: (x, y) => if y == 0 { rgb("#136f73") } else if calc.even(y) { rgb("#eef5f5") } else { white },',
           "    " + ", ".join("[*%s*]" % inline(h) for h in header) + ","]
    for r in rows:
        out.append("    " + ", ".join("[%s]" % inline(c) for c in r) + ",")
    out.append("  ),")
    out.append("  caption: none,")
    out.append(")")
    return "\n".join(out)

def convert(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    in_code = False
    code_buf = []
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            if in_code:
                out.append('#block(breakable: true, fill: rgb("#f4f7f7"), inset: 9pt, radius: 3pt, stroke: 0.5pt + rgb("#cfdede")) {')
                out.append('  #set par(leading: 0.75em)')
                out.append('  #set text(size: 9.5pt)')
                for cl in code_buf:
                    out.append("  " + esc(cl) if cl else "  ")
                out.append("}")
                out.append("#v(0.3em)")
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(ln.rstrip())
            i += 1
            continue
        if not s:
            i += 1
            continue
        if s == "---":
            out.append('#block(above: 0.5em, below: 0.5em)[#align(center, line(length: 100%, stroke: 0.9pt + rgb("#b8913a")))]')
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            out.append(("=" * level) + " " + esc(title))
            i += 1
            continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            tbl = [s]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(md_table_to_typst(tbl))
            out.append("#v(0.4em)")
            continue
        if s.startswith("> "):
            out.append('#block(breakable: false, fill: rgb("#f2f7f4"), inset: (x: 9pt, y: 6pt), radius: 3pt, stroke: 0.8pt + rgb("#136f73"), above: 0.35em, below: 0.35em) {')
            out.append('  #set text(fill: rgb("#0f2744"))')
            out.append("  " + inline(s[2:]))
            out.append("}")
            i += 1
            continue
        if s.startswith("- ") or s.startswith("+ "):
            out.append("- " + inline(s[2:]))
            i += 1
            continue
        m = re.match(r"^(\d+)[.)]\s+(.*)$", s)
        if m:
            out.append(f"{m.group(1)}. " + inline(m.group(2)))
            i += 1
            continue
        out.append(inline(s))
        i += 1
    return "\n".join(out)

if __name__ == "__main__":
    md = open(sys.argv[1], encoding="utf-8").read()
    print(convert(md))
