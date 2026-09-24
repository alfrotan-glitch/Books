"""Originality check: word n-gram overlap between the new book and the old source text
(«میتودهای کلینیکی علی», original + edited). Reports shared 8-word sequences."""
import re, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]
OLD = [R.parent / "clinical-methods-ali/manuscript/original/clinical-methods-ali.md",
       R.parent / "clinical-methods-ali/manuscript/master.md"]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
def words(t):
    t = re.sub(r"[\u064B-\u0652\u200c\u200f\u200e]", "", t)
    t = t.replace("ي", "ی").replace("ك", "ک")
    return re.findall(r"[\u0600-\u06FFA-Za-z]+", t)
old = set()
for p in OLD:
    if p.exists():
        w = words(p.read_text(encoding="utf-8"))
        old.update(tuple(w[i:i+N]) for i in range(len(w) - N + 1))
rep = []; tot = hit = 0
for ch in sorted((R / "chapters").glob("*.md")):
    w = words(ch.read_text(encoding="utf-8"))
    grams = [tuple(w[i:i+N]) for i in range(len(w) - N + 1)]
    h = [g for g in grams if g in old]
    tot += len(grams); hit += len(h)
    rep.append(f"{ch.name}: {len(h)}/{len(grams)} shared {N}-grams ({100*len(h)/max(1,len(grams)):.2f}%)")
    for g in h[:20]: rep.append("    " + " ".join(g))
rep.append(f"TOTAL: {hit}/{tot} shared {N}-grams = {100*hit/max(1,tot):.2f}%")
(R / "build/similarity-report.txt").write_text("\n".join(rep) + "\n", encoding="utf-8")
print("\n".join(rep))
