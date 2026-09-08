"""Normalise passage line-number markers.
The frozen extraction prints the printed margin line numbers (5, 10, 15, ...) as "[n]" — but on some pages they came
through bare ("10 opportunity at 16 ...") and, far more often, the marker started a NEW paragraph in the middle of a
sentence.  This pass (passage pages only):
  1. bare paragraph-initial multiples of 5 -> "[n]" (only when the page also carries other line markers);
  2. a marker paragraph whose predecessor is plain prose that does not end a sentence is re-joined to it.
Text is never changed apart from the marker brackets and the paragraph join."""
import re

PASSAGE_PAGES = [14, 18, 24, 28, 34, 38, 43, 46, 48, 52, 56, 62, 66, 72, 76, 81, 84, 86, 90, 94, 100, 104, 110, 114,
                 119, 122, 124, 128, 132, 138, 142, 148, 152, 157, 160, 162]
END = re.compile(r"[.!?…”\"’)\]:;]\s*$|[.!?]\S?\s*$")
MARK = re.compile(r"^(?:\[(\d+)\]|(\d+)) (?=\S)")

def fix_linemarks(pn, body, log):
    if pn not in PASSAGE_PAGES:
        return body, 0
    paras = re.split(r"\n\s*\n", body.strip("\n"))
    marks = [(i, m) for i, q in enumerate(paras) for m in [MARK.match(q)] if m
             and int(m.group(1) or m.group(2)) % 5 == 0 and 0 < int(m.group(1) or m.group(2)) <= 70]
    if len(marks) < 2:
        return body, 0
    changed = 0
    # 1. bare -> bracketed (skip a bare "5" that follows an exercise item "4 ...")
    for i, m in marks:
        if m.group(2):
            prev = paras[i - 1] if i else ""
            if m.group(2) == "5" and re.match(r"^(\[4\]|4) ", prev):
                continue
            paras[i] = "[" + m.group(2) + "]" + paras[i][m.end() - 1:]
            changed += 1; log.append((pn, "bracket", paras[i][:50]))
    # 2. re-join a marker paragraph to a predecessor that does not end a sentence
    out = []
    for i, q in enumerate(paras):
        m = MARK.match(q)
        if out and m and m.group(1) and int(m.group(1)) % 5 == 0:
            prev = out[-1]
            prev_is_tag = prev.startswith("[") and not MARK.match(prev)
            prose = (not prev.startswith(("#", "**", "☐", "|")) and not prev_is_tag and len(prev) > 40
                     and not re.match(r"^\d+ ", prev) and not END.search(prev)
                     and not re.match(r"^[A-E] [A-Z]", prev)
                     and (len(q) > len(m.group(0)) + 20 or re.search(r"[.!?]$", q)))   # short marker lines only if they end the sentence
            if prose:
                out[-1] = prev.rstrip() + " " + q
                changed += 1; log.append((pn, "join", prev[-30:] + " ‖ " + q[:30]))
                continue
        out.append(q)
    return "\n" + "\n\n".join(out) + "\n\n\n", changed

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from split_master import load
    h, pages, t = load("/home/user/Books/tools/qa/master_out.txt")
    log = []; tot = 0
    for pn in [int(a) for a in sys.argv[1:]] or PASSAGE_PAGES:
        nb, c = fix_linemarks(pn, pages[pn][1], log); tot += c
    for l in log: print(l)
    print("changes:", tot)
