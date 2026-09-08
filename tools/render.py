"""Stage 4: render assembled blocks of a page to structured text."""
import re, sys, os
from assemble import assemble, block_text, line_text, alnum, BLANK
import fixups

SECTION_HEADS = ["Before You Read", "Reading Skill", "Reading Comprehension", "Critical Thinking", "Vocabulary Comprehension",
                 "Vocabulary Skill", "Real Life Skill", "What Do You Think?", "Self Check", "Review Reading", "Fluency Strategy",
                 "Fluency Practice", "Motivational Tip", "Getting Ready", "Check Your Understanding", "Definitions", "Words in Context",
                 "Reading Passage", "Vocabulary Learning Tips", "Tips for Fluent Reading", "Are You an ACTIVE Reader?"]


def norm_apostrophes(s):
    s = re.sub(r"(\w)'(\w)", "\\1’\\2", s)
    s = re.sub(r"\b(\w+)[`´](\w)", "\\1’\\2", s)
    return s


def render_block(b):
    if b["kind"] == "table":
        out = [f"[TABLE {b['ncols']} columns]"]
        for row in b["cells"]:
            out.append(" | ".join(c if c else "" for c in row))
        out.append("[/TABLE]")
        return "\n".join(out)
    text = block_text(b)
    text = norm_apostrophes(text)
    if not text.strip():
        return ""
    plain = text.strip("* ")
    if b["kind"] == "heading":
        if b["size"] >= 20:
            return "# " + text
        return "## " + text
    if b["size"] >= 14 and b["bold"]:
        return "## " + text
    if plain in SECTION_HEADS or re.fullmatch(r"(Unit|UNIT) \d{1,2}|Chapter \d|Review \d|Vocabulary Index|Reading Rate Chart", plain):
        return "## " + text
    if b["bold"] and len(b["lines"]) == 1 and len(plain) <= 60 and not re.match(r"^[A-H]\s", plain) and not b.get("item"):
        return "**" + text + "**"
    return text


def render_page(pn):
    r = assemble(pn)
    foot = r["footer"]
    book_no = None
    foot_txt = ""
    if foot:
        foot_txt = " ".join(line_text(l) for l in foot["lines"]).strip()
        # the folio is the number printed at the outer edge of the running foot (first or last token)
        toks = foot_txt.split()
        cand = [t for t in (toks[0], toks[-1]) if re.fullmatch(r"\d{1,3}", t)] if toks else []
        if cand and abs(int(cand[0]) - (pn - 1)) <= 1:
            book_no = int(cand[0])
        elif cand and (pn - 1) in [int(c) for c in cand]:
            book_no = pn - 1
    if book_no is None:
        book_no = pn - 1
    out = [f"[PAGE {pn:03d}]  (book page {book_no})", ""]
    if r["header"]:
        ht = " ".join(line_text(l) for l in r["header"]["lines"]).strip()
        if ht:
            out.append(f"[running head: {ht}]"); out.append("")
    prev = None
    for b in r["blocks"]:
        s = render_block(b)
        if not s:
            continue
        out.append(s)
        out.append("")
    if foot_txt:
        out.append(f"[running foot: {foot_txt}]")
        out.append("")
    text = "\n".join(out)
    text = fixups.apply(pn, text)
    return text


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(render_page(int(a)))
