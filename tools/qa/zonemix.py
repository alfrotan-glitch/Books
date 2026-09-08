"""Detect paragraphs whose words come from BOTH the sidebar zone and the main column (interleaving defects)."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pagelocate import words, para_tokens, norm
from split_master import load
from reorder import zone, SINGLE_COLUMN, SIDE_HEAD
from pagelocate import locate

def has_sidebar(pn, body):
    for p, pos in locate(pn, body, prefer=lambda x: zone(pn, x) == "side"):
        if SIDE_HEAD.match(p) and pos and zone(pn, pos[0]) == "side":
            return True
    return False

def align(pn, toks):
    """greedy in-order alignment of paragraph tokens to page words; returns list of (tok, x, y) for matched tokens"""
    ws = words(pn)
    n_ws = [w[0] for w in ws]
    # anchor: first robust match of 3 consecutive tokens
    out = []
    j = 0
    # find start
    start = None
    for i in range(len(toks) - 2):
        key = toks[i:i+3]
        for k in range(len(n_ws) - 2):
            if n_ws[k:k+3] == key:
                start = (i, k); break
        if start: break
    if not start:
        return out
    ti, wi = start
    out.append((toks[ti], ws[wi][1], ws[wi][2]))
    for t in toks[ti+1:]:
        hit = None
        for d in range(1, 12):
            if wi + d < len(n_ws) and n_ws[wi + d] == t:
                hit = wi + d; break
        if hit is None:
            continue
        wi = hit
        out.append((t, ws[wi][1], ws[wi][2]))
    return out

if __name__ == "__main__":
    h, pages, t = load()
    sel = [int(a) for a in sys.argv[1:]] or sorted(pages)
    for pn in sel:
        if pn in SINGLE_COLUMN: continue
        body = pages[pn][1]
        if not has_sidebar(pn, body): continue
        for para in re.split(r"\n\s*\n", body.strip("\n")):
            if para.startswith(("[running foot", "Motivational Tip", "## ")): continue
            toks = para_tokens(para)
            if len(toks) < 8: continue
            al = align(pn, toks)
            if len(al) < 6: continue
            side = sum(1 for _, x, _ in al if zone(pn, x) == "side")
            main = len(al) - side
            if side >= 3 and main >= 3:
                print(f"p{pn:03d} side={side:3d} main={main:3d} | {para[:90]!r}")
