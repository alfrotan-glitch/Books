"""Driver: render every page to tools/data/ocr/pNNN.txt with a coverage check against the raw text layer.
Usage: python3 runall.py [first last]"""
import os, re, sys, json, traceback
import pymupdf
from render import render_page
from fuse import alnum

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(os.path.dirname(ROOT), "Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf")
OUT = os.path.join(ROOT, "data", "ocr")
EXPECTED_LOW = {1, 126, 167}


def coverage(pn, text, doc):
    """fraction of the embedded layer's dictionary-ish words (>= 4 letters) that appear in the rendered text"""
    raw = doc[pn - 1].get_text("text")
    raw_words = [w for w in re.findall(r"[A-Za-z]{4,}", raw)]
    if not raw_words:
        return 1.0, 0
    have = set(re.findall(r"[A-Za-z]{4,}", text.lower()))
    hit = sum(1 for w in raw_words if w.lower() in have)
    return hit / len(raw_words), len(raw_words)


def main():
    os.makedirs(OUT, exist_ok=True)
    args = [int(a) for a in sys.argv[1:]]
    doc = pymupdf.open(PDF)
    pages = range(args[0], args[1] + 1) if len(args) == 2 else (args or range(1, len(doc) + 1))
    stats = {}
    for pn in pages:
        try:
            text = render_page(pn)
        except Exception:
            print(f"ERROR page {pn}", file=sys.stderr)
            traceback.print_exc()
            text = f"[PAGE {pn:03d}]\n\n[EXTRACTION FAILED — see log]\n"
        cov, n = coverage(pn, text, doc)
        flags = len(re.findall(r"\{\?", text))
        stats[pn] = dict(coverage=round(cov, 3), raw_words=n, flags=flags, chars=len(text))
        with open(os.path.join(OUT, f"p{pn:03d}.txt"), "w") as f:
            f.write(text)
        note = ""
        if cov < 0.97 and pn not in EXPECTED_LOW:
            note = "  LOW COVERAGE"
        print(f"{pn:3d} cov {cov:.3f} words {n:4d} flags {flags:2d}{note}", flush=True)
    with open(os.path.join(OUT, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1)


if __name__ == "__main__":
    main()
