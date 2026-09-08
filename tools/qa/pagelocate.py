"""Locate master paragraphs on the page using the stage-1 word dumps (tools/data/pages/pNNN.json.gz).
Returns, for each paragraph of a page body, the (x0, y0) of its first matched word (or None)."""
import gzip, json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

def norm(t):
    t = t.lower().replace("’", "'").replace("—", "-").replace("–", "-")
    return re.sub(r"[^a-z0-9]", "", t)

_cache = {}
def words(pn):
    if pn not in _cache:
        d = json.load(gzip.open(f"{ROOT}/tools/data/pages/p{pn:03d}.json.gz"))
        ws = []
        for src in ("tess", "embedded"):
            for w in d[src]:
                n = norm(w["text"])
                if n:
                    ws.append((n, w["x0"], w["y0"], src))
        _cache[pn] = ws
    return _cache[pn]

def para_tokens(p):
    if p.startswith("[TABLE"):
        p = p.split("\n", 1)[1] if "\n" in p else ""
    p = re.sub(r"^\[[^\]]*\]\s*", "", p)  # drop tags like [IMAGE ...]
    p = p.replace("|", " ").replace("/", " ")
    toks = [norm(t) for t in p.split()]
    toks = [t for t in toks if t and not re.fullmatch(r"_+", t)]
    return toks

def locate(pn, body, ntok=6, prefer=None):
    """prefer: optional function(x) -> bool; among equal-length matches choose the first for which prefer(x) is true."""
    ws = words(pn)
    n_ws = [w[0] for w in ws]
    out = []
    paras = re.split(r"\n\s*\n", body.strip("\n"))
    for p in paras:
        toks = para_tokens(p)
        pos = None
        if toks:
            key = toks[:ntok]
            # fuzzy in-order match: each following token must appear within the next 3 word slots
            def plausible(a, b):
                # consecutive matched words must be on the same line (to the right) or on one of the next lines
                xa, ya = ws[a][1], ws[a][2]; xb, yb = ws[b][1], ws[b][2]
                dy = yb - ya
                if abs(dy) < 7:
                    return xb > xa - 2          # same line, to the right
                return 7 <= dy < 22             # or on the next line
            def run_from(i):
                k = 1; j = i
                for t in key[1:]:
                    hit = None
                    for d in (1, 2, 3):
                        if j + d < len(n_ws) and n_ws[j + d] == t and plausible(j, j + d):
                            hit = j + d; break
                    if hit is None: break
                    j = hit; k += 1
                return k
            best = []
            for i in range(len(n_ws)):
                if n_ws[i] != key[0]: continue
                k = run_from(i)
                best.append((k, i))
            if best:
                kmax = max(k for k, _ in best)
                cands = [i for k, i in best if k == kmax]
                ok = kmax >= 3 or (kmax == len(key) and sum(len(t) for t in key) >= 6) or (kmax == 2 and sum(len(t) for t in key[:2]) >= 9)
                if ok:
                    i = cands[0]
                    if prefer is not None and p.startswith("## "):
                        for c_ in cands:
                            if prefer(ws[c_][1]):
                                i = c_; break
                    pos = (ws[i][1], ws[i][2], ws[i][3], kmax)
        out.append((p, pos))
    return out

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    from split_master import load
    h, pages, t = load()
    for a in sys.argv[1:]:
        pn = int(a)
        print(f"=== page {pn}")
        for p, pos in locate(pn, pages[pn][1]):
            s = p.replace("\n", " ⏎ ")[:70]
            if pos:
                print(f"  x={pos[0]:6.1f} y={pos[1]:6.1f} {pos[2][:4]} k={pos[3]} | {s}")
            else:
                print(f"  {'?':>22} | {s}")
