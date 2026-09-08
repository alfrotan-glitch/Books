"""Independent check: words of the PDF's embedded text layer that do not appear in the Master page.
The embedded layer is noisy, so only report dictionary words (>=4 letters) missing from the page AND from the
neighbouring pages (to tolerate small boundary differences)."""
import re, sys, json, collections
import pymupdf
sys.path.insert(0, "/home/user/Books/tools/qa"); sys.path.insert(0, "/home/user/Books/tools")
from split_master import load
from quality import is_word
PDF = "/home/user/Books/Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf"
head, pages, tail = load()
doc = pymupdf.open(PDF)
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("—", "-").replace("–", "-").replace("\u00ad", "")
    return s.lower()
def toks(s):
    return re.findall(r"[a-z][a-z'\-]{2,}", norm(s))
report = {}
for pn in range(1, 180):
    pg = doc[pn - 1]
    words = pg.get_text("words")
    layer = " ".join(w[4] for w in words)
    master = pages[pn][1]
    mset = set(toks(master))
    nb = set()
    for q in (pn - 1, pn + 1):
        if q in pages: nb |= set(toks(pages[q][1]))
    missing = collections.Counter()
    for w in toks(layer):
        core = w.strip("'-")
        if len(core) < 4 or not is_word(core): continue
        if core in mset or w in mset: continue
        # tolerate hyphenation / plural / possessive variants
        if any(v in mset for v in (core + "s", core[:-1], core + "'s", core.rstrip("s"))): continue
        if core in nb: continue
        missing[core] += 1
    # words in master not in layer (possible hallucination / tesseract junk)
    lset = set(toks(layer))
    extra = collections.Counter()
    for w in toks(master):
        core = w.strip("'-")
        if len(core) < 4 or core in lset: continue
        if any(v in lset for v in (core + "s", core[:-1], core + "'s")): continue
        if is_word(core): continue          # dictionary word tesseract read that the weak layer missed: fine
        extra[core] += 1
    report[pn] = dict(missing=sorted(missing), extra=sorted(extra), layer_words=len(words), master_words=len(toks(master)))
json.dump(report, open("/home/user/Books/tools/qa/layer_report.json", "w"), indent=0)
tot_m = sum(len(r["missing"]) for r in report.values()); tot_e = sum(len(r["extra"]) for r in report.values())
print("pages", len(report), "missing-word entries", tot_m, "extra-nonword entries", tot_e)
for pn, r in report.items():
    if len(r["missing"]) >= 3 or len(r["extra"]) >= 3:
        print(pn, "MISSING:", r["missing"][:15], "| EXTRA:", r["extra"][:10])
