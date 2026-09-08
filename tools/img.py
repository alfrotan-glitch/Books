"""Image analysis on the scanned page: horizontal rules (writing lines / blanks), vertical rules, ruled tables,
check boxes and photographs.  All coordinates returned in PDF points.  Results are cached in tools/data/img."""
import os, json
import numpy as np, cv2, pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(os.path.dirname(ROOT), "Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf")
CACHE = os.path.join(ROOT, "data", "img")
DPI = 200
S = 72.0 / DPI
_doc = None


def page_gray(pn):
    global _doc
    if _doc is None:
        _doc = pymupdf.open(PDF)
    page = _doc[pn - 1]
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()


def _runs(mask_row):
    """start,end (exclusive) of True runs in a 1-D boolean array."""
    d = np.diff(np.concatenate(([0], mask_row.astype(np.int8), [0])))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def hrules(g, min_len_pt=14, max_thick_pt=2.6):
    """Horizontal dark rules: list of dict(x0,x1,y,yl,yr,thick,clear,clear_above,clear_below,boxy) in pt.
    Skew-tolerant: per-row dark runs that overlap vertically-adjacent runs are merged."""
    dark = g < 140
    H, W = dark.shape
    min_len = int(min_len_pt / S)
    cand = []
    for y in range(H):
        row = dark[y]
        if row.sum() < min_len:
            continue
        runs = _runs(row)
        merged = []
        for a, b in runs:                       # bridge 1-2 px breaks in a scanned rule
            if merged and a - merged[-1][1] <= 2:
                merged[-1] = (merged[-1][0], b)
            else:
                merged.append((a, b))
        for a, b in merged:
            if b - a >= min_len:
                cand.append((y, a, b))
    # group runs into rules: consecutive rows whose runs overlap by >= 60%
    rules = []
    open_ = []
    for y, a, b in cand:
        placed = None
        for r in open_:
            if r["ye"] >= y - 1:
                ov = min(r["b"], b) - max(r["a"], a)
                if ov >= 0.6 * min(b - a, r["b"] - r["a"]):
                    placed = r; break
        if placed:
            placed["ye"] = y; placed["a"] = min(placed["a"], a); placed["b"] = max(placed["b"], b)
            placed["rows"].append((y, a, b))
        else:
            r = dict(ys=y, ye=y, a=a, b=b, rows=[(y, a, b)])
            open_.append(r); rules.append(r)
        open_ = [r for r in open_ if r["ye"] >= y - 1]
    out = []
    max_thick = max_thick_pt / S
    for r in rules:
        thick_rows = r["ye"] - r["ys"] + 1
        # skewed rule: thickness = dark rows per column
        cols = np.zeros(r["b"] - r["a"], dtype=np.int32)
        for y, a, b in r["rows"]:
            cols[a - r["a"]:b - r["a"]] += 1
        thick = float(cols[cols > 0].mean()) if (cols > 0).any() else thick_rows
        if thick > max_thick:
            continue
        length = r["b"] - r["a"]
        if length < min_len:
            continue
        # clearance: no dark pixels in bands above / below the rule (text sitting on the rule -> underline / table)
        ya0 = max(0, r["ys"] - int(4 / S)); ya1 = max(0, r["ys"] - 2)
        yb0 = min(H, r["ye"] + 3); yb1 = min(H, r["ye"] + int(4 / S) + 1)
        band_a = dark[ya0:ya1, r["a"]:r["b"]] if ya1 > ya0 else np.zeros((1, 1), bool)
        band_b = dark[yb0:yb1, r["a"]:r["b"]] if yb1 > yb0 else np.zeros((1, 1), bool)
        clear_above = band_a.mean() < 0.02
        clear_below = band_b.mean() < 0.02
        clear = clear_above and clear_below
        # boxy: a vertical dark run touches an end of the rule (table / box border)
        xs0 = max(0, r["a"] - 2); xs1 = min(W, r["b"] + 2)
        vband_l = dark[max(0, r["ys"] - int(6 / S)):min(H, r["ye"] + int(6 / S)), xs0:min(W, xs0 + 4)]
        vband_r = dark[max(0, r["ys"] - int(6 / S)):min(H, r["ye"] + int(6 / S)), max(0, xs1 - 4):xs1]
        boxy = bool(vband_l.mean() > 0.5 or vband_r.mean() > 0.5)
        left_rows = [y for y, a, b in r["rows"] if a <= r["a"] + 3]
        right_rows = [y for y, a, b in r["rows"] if b >= r["b"] - 3]
        yl = (sum(left_rows) / len(left_rows) if left_rows else (r["ys"] + r["ye"]) / 2) * S
        yr = (sum(right_rows) / len(right_rows) if right_rows else (r["ys"] + r["ye"]) / 2) * S
        out.append(dict(x0=r["a"] * S, x1=r["b"] * S, y=(r["ys"] + r["ye"]) / 2 * S, yl=yl, yr=yr, thick=thick * S,
                        clear=bool(clear), clear_above=bool(clear_above), clear_below=bool(clear_below), boxy=boxy))
    return out


def merge_collinear(hr, tol_y=2.2, gap=6):
    """merge rule fragments that continue each other (skewed scans split one rule into offset, overlapping pieces).
    Two clear rules separated by a real gap (> 3 pt) stay separate (two half-width writing lines)."""
    hr = sorted(hr, key=lambda h: (h["x0"], h["y"]))
    out = []
    for h in hr:
        h = dict(h)
        for m in out:
            if abs(m.get("yr", m["y"]) - h.get("yl", h["y"])) <= tol_y and -8 <= h["x0"] - m["x1"] <= gap and abs(m["thick"] - h["thick"]) < 1.5 and h["x1"] > m["x1"] \
                    and not (m["clear"] and h["clear"] and h["x0"] - m["x1"] > 3):
                m["x1"] = h["x1"]; m["yr"] = h.get("yr", h["y"]); m["clear"] = m["clear"] and h["clear"]
                m["clear_above"] = m["clear_above"] and h["clear_above"]; m["clear_below"] = m["clear_below"] and h["clear_below"]
                m["boxy"] = m.get("boxy") or h.get("boxy")
                m["y"] = (m.get("yl", m["y"]) + m["yr"]) / 2
                break
        else:
            out.append(h)
    # a thin duplicate detection lying inside a longer rule at (almost) the same y (anti-aliased edge of a heading
    # underline etc.) is not a rule of its own
    keep = []
    for h in out:
        dup = any(m is not h and abs(m["y"] - h["y"]) <= 1.5 and m["x0"] <= h["x0"] + 3 and m["x1"] >= h["x1"] - 3
                  and (m["x1"] - m["x0"]) > (h["x1"] - h["x0"]) for m in out)
        if not dup:
            keep.append(h)
    return keep


def vrules(g, min_len_pt=25, max_thick_pt=2.6):
    vr = [dict(y0=r["x0"], y1=r["x1"], x=r["y"], thick=r["thick"], clear=r["clear"]) for r in hrules(g.T, min_len_pt, max_thick_pt)]
    vr.sort(key=lambda v: (v["y0"], v["x"]))
    out = []
    for v in vr:
        v = dict(v)
        for m in out:
            if abs(m["x_end"] - v["x"]) <= 2.2 and -8 <= v["y0"] - m["y1"] <= 6 and v["y1"] > m["y1"]:
                m["y1"] = v["y1"]; m["x_end"] = v["x"]; m["x"] = (m["x_start"] + v["x"]) / 2
                break
        else:
            v["x_start"] = v["x"]; v["x_end"] = v["x"]
            out.append(v)
    return out


def checkboxes(g):
    """Small hollow squares (survey / self-check boxes) -> list of dict(x0,y0,x1,y1) in pt.
    The boxes are printed with a light top/left edge and a drop shadow, so we look for a white square interior
    enclosed by a non-white frame on all four sides."""
    white = (g > 200).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
    out = []
    lo, hi = 4 / S, 17 / S           # interior size in px
    H, W = g.shape
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if not (lo <= w <= hi and lo <= h <= hi and 0.75 <= w / h <= 1.33):
            continue
        if area < 0.85 * w * h:
            continue                     # not a filled square (letter counters etc.)
        # square interior: the corner regions of the bounding box belong to the component (a round counter of
        # 'o' / 'e' has empty corners)
        comp = (lab[y:y + h, x:x + w] == i)
        k = max(1, min(w, h) // 5)
        corners = [comp[:k, :k].mean(), comp[:k, -k:].mean(), comp[-k:, :k].mean(), comp[-k:, -k:].mean()]
        if min(corners) < 0.5:
            continue
        # frame: rows just above / below and columns just left / right must be non-white over most of the span
        pad = 3
        if y - pad < 0 or x - pad < 0 or y + h + pad > H or x + w + pad > W:
            continue
        top = (g[y - pad:y, x:x + w] < 190).any(axis=0).mean()
        bot = (g[y + h:y + h + pad, x:x + w] < 190).any(axis=0).mean()
        left = (g[y:y + h, x - pad:x] < 190).any(axis=1).mean()
        right = (g[y:y + h, x + w:x + w + pad] < 190).any(axis=1).mean()
        if min(top, bot, left, right) < 0.8:
            continue
        # frame must be thin: 6 px further out it is white again on at least two sides (not a letter / table cell)
        far = 9
        fx0 = max(0, x - far); fx1 = min(W, x + w + far); fy0 = max(0, y - far); fy1 = min(H, y + h + far)
        outer_top = (g[fy0:fy0 + 2, x:x + w] > 200).mean() if fy0 + 2 <= y - pad else 0
        outer_left = (g[y:y + h, fx0:fx0 + 2] > 200).mean() if fx0 + 2 <= x - pad else 0
        outer_bot = (g[fy1 - 2:fy1, x:x + w] > 200).mean() if fy1 - 2 >= y + h + pad else 0
        outer_right = (g[y:y + h, fx1 - 2:fx1] > 200).mean() if fx1 - 2 >= x + w + pad else 0
        if sum(v > 0.7 for v in (outer_top, outer_left, outer_bot, outer_right)) < 2:
            continue
        out.append(dict(x0=(x - 2) * S, y0=(y - 2) * S, x1=(x + w + 2) * S, y1=(y + h + 2) * S))
    ded = []
    for b in sorted(out, key=lambda b: (b["y0"], b["x0"])):
        if not any(abs(b["x0"] - d["x0"]) < 4 and abs(b["y0"] - d["y0"]) < 4 for d in ded):
            ded.append(b)
    return ded


def tables(hr, vr, W, H):
    """Ruled grids: >= 2 horizontal rules spanning the same x-range and >= 1 vertical rule crossing them."""
    out = []
    used = set()
    # join collinear fragments separated by small gaps (a vertical rule crossing a horizontal one can leave a
    # white gap in the scan)
    frag = sorted([dict(h) for h in hr], key=lambda h: (round(h["y"] / 3), h["x0"]))
    joined = []
    for h in frag:
        if joined and abs(joined[-1]["y"] - h["y"]) <= 2.5 and -3 <= h["x0"] - joined[-1]["x1"] <= 10:
            joined[-1]["x1"] = max(joined[-1]["x1"], h["x1"])
            joined[-1]["clear"] = joined[-1]["clear"] and h["clear"]
        else:
            joined.append(h)
    hs = sorted([h for h in joined if h["x1"] - h["x0"] >= 60], key=lambda h: h["y"])
    # merge vertical fragments that overlap / nearly touch at the same x
    vv = sorted([dict(v) for v in vr], key=lambda v: (round(v["x"] / 4), v["y0"]))
    vm = []
    for v in vv:
        for m in vm:
            if abs(m["x"] - v["x"]) <= 3 and v["y0"] <= m["y1"] + 8 and v["y1"] >= m["y0"] - 8:
                m["y0"] = min(m["y0"], v["y0"]); m["y1"] = max(m["y1"], v["y1"])
                break
        else:
            vm.append(v)
    vr = vm
    for i, h in enumerate(hs):
        if i in used:
            continue
        grp = [h]; idx = [i]
        for j in range(i + 1, len(hs)):
            k = hs[j]
            if ((abs(k["x0"] - h["x0"]) < 12 and abs(k["x1"] - h["x1"]) < 25) or (abs(k["x0"] - h["x0"]) < 25 and abs(k["x1"] - h["x1"]) < 12)
                    or (abs(k["x0"] - h["x0"]) < 14 and abs(k["x1"] - h["x1"]) < 14)) \
                    and k["y"] - grp[-1]["y"] < 90:
                grp.append(k); idx.append(j)
        if len(grp) < 2:
            continue
        x0 = min(k["x0"] for k in grp); x1 = max(k["x1"] for k in grp)
        # vertical rules inside the x-range; keep the rows they span (>= 2 verticals covering >= 2 rows)
        vin = [v for v in vr if x0 - 4 <= v["x"] <= x1 + 4]
        best = None
        for a in range(len(grp)):
            for b in range(len(grp) - 1, a, -1):
                ya, yb = grp[a]["y"], grp[b]["y"]
                vs = [v for v in vin if v["y0"] <= ya + 6 and v["y1"] >= yb - 6 and (v["y1"] - v["y0"]) >= 0.6 * (yb - ya)]
                if len(vs) >= 2:
                    if best is None or (b - a) > (best[1] - best[0]):
                        best = (a, b, vs)
                    break
        if best is None:
            continue
        a, b, vs = best
        grp = grp[a:b + 1]; idx = idx[a:b + 1]
        y0 = grp[0]["y"]; y1 = grp[-1]["y"]
        cols = sorted(set(round(v["x"]) for v in vs))
        merged_cols = []
        for c in cols:
            if not merged_cols or c - merged_cols[-1] > 6:
                merged_cols.append(c)
        cols = merged_cols
        # table outline: use the widest horizontal rule of the group (rounded corners shorten the top / bottom rule)
        x0 = min(k["x0"] for k in grp); x1 = max(k["x1"] for k in grp)
        if cols[0] > x0 + 12:
            cols.insert(0, x0)
        else:
            cols[0] = min(cols[0], x0)
        if cols[-1] < x1 - 12:
            cols.append(x1)
        else:
            cols[-1] = max(cols[-1], x1)
        if len(cols) < 2:
            continue
        rows = [k["y"] for k in grp]
        # header row above the first spanned rule: a rule of the same group up to 24 pt above whose x-range
        # matches (rounded-corner top border) and a column rule reaching into that band
        if a > 0:
            top = hs[idx[0] - 1] if idx[0] - 1 >= 0 else None
            cand = [k for k in hs if 4 < y0 - k["y"] <= 40 and abs(k["x0"] - x0) < 14 and abs(k["x1"] - x1) < 14]
            if cand:
                k = min(cand, key=lambda k: y0 - k["y"])
                if sum(1 for v in vin if v["y0"] <= k["y"] + 12 and v["y1"] >= y0 - 6) >= 2:
                    rows.insert(0, k["y"]); y0 = k["y"]
        # footer row below the last spanned rule (rounded-corner bottom border)
        cand = [k for k in hs if 4 < k["y"] - y1 <= 40 and abs(k["x0"] - x0) < 14 and abs(k["x1"] - x1) < 14]
        if cand:
            k = min(cand, key=lambda k: k["y"] - y1)
            # the outline verticals must reach (almost) down to that rule
            if sum(1 for v in vin if v["y1"] >= k["y"] - 12 and v["y0"] <= y1 + 6) >= 2:
                rows.append(k["y"]); y1 = k["y"]
        used.update(idx)
        out.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, cols=cols, rows=rows))
    # merge tables that overlap (the same grid detected twice from different rule subsets)
    merged = []
    for t in sorted(out, key=lambda t: (t["y0"], t["x0"])):
        for m in merged:
            xo = min(m["x1"], t["x1"]) - max(m["x0"], t["x0"]); yo = min(m["y1"], t["y1"]) - max(m["y0"], t["y0"])
            if xo > 0 and yo > 0 and (yo >= 0.5 * min(m["y1"] - m["y0"], t["y1"] - t["y0"])):
                m["x0"] = min(m["x0"], t["x0"]); m["x1"] = max(m["x1"], t["x1"]); m["y0"] = min(m["y0"], t["y0"]); m["y1"] = max(m["y1"], t["y1"])
                cols = sorted(set(m["cols"]) | set(t["cols"]))
                cc = []
                for c in cols:
                    if not cc or c - cc[-1] > 6:
                        cc.append(c)
                m["cols"] = cc
                rows = sorted(set(m["rows"]) | set(t["rows"]))
                rr = []
                for r in rows:
                    if not rr or r - rr[-1] > 4:
                        rr.append(r)
                m["rows"] = rr
                break
        else:
            merged.append(dict(t))
    return merged


def photos(g):
    """Photographs / dark tinted panels: large connected regions of mid/dark tone."""
    mask = (g < 215).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if w * S < 60 or h * S < 60:
            continue
        fill = area / float(w * h)
        if fill < 0.55:
            continue
        reg = g[y:y + h, x:x + w]
        hist = np.bincount(reg.ravel() // 16, minlength=16) / reg.size
        if hist.max() > 0.75 and reg.mean() > 200:
            continue
        tone = float(reg.mean()) / 255.0
        # a tinted text panel has one dominant background tone; a photograph does not
        mode = int(np.argmax(np.bincount(reg.ravel(), minlength=256)))
        uniform = bool(((reg >= mode - 12) & (reg <= mode + 12)).mean() > 0.45)
        out.append(dict(x0=x * S, y0=y * S, x1=(x + w) * S, y1=(y + h) * S, fill=float(fill), tone=tone, panel=uniform))
    # light photographs (mid-tone texture rather than dark mass): density of mid-grey pixels
    mid = ((g > 40) & (g < 205)).astype(np.float32)
    k = int(12 / S)
    dens = cv2.blur(mid, (k, k))
    mask = (dens > 0.35).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if w * S < 50 or h * S < 50 or area / float(w * h) < 0.5:
            continue
        box = dict(x0=x * S, y0=y * S, x1=(x + w) * S, y1=(y + h) * S)
        if any(p["x0"] - 6 <= box["x0"] and box["x1"] <= p["x1"] + 6 and p["y0"] - 6 <= box["y0"] and box["y1"] <= p["y1"] + 6 for p in out):
            continue
        reg = g[y:y + h, x:x + w]
        out.append(dict(box, fill=float(area / float(w * h)), tone=float(reg.mean()) / 255.0, light=True))
    return out


def analyse(pn, force=False):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"p{pn:03d}.json")
    if not force and os.path.exists(f):
        return json.load(open(f))
    g = page_gray(pn)
    H, W = g.shape
    hr = hrules(g)
    from geom import ROTATED
    for clip, ang in ROTATED.get(pn, []):
        hr = [h for h in hr if not (clip[0] <= (h["x0"] + h["x1"]) / 2 <= clip[2] and clip[1] <= h["y"] <= clip[3])]
        x0, y0, x1, y1 = [int(round(v / S)) for v in clip]
        crop = g[y0:y1, x0:x1]
        M = cv2.getRotationMatrix2D((crop.shape[1] / 2, crop.shape[0] / 2), ang, 1.0)
        rot = cv2.warpAffine(crop, M, (crop.shape[1], crop.shape[0]), borderValue=255)
        for h in hrules(rot):
            h["x0"] += x0 * S; h["x1"] += x0 * S; h["y"] += y0 * S; h["yl"] += y0 * S; h["yr"] += y0 * S
            hr.append(h)
    hr = merge_collinear(hr)
    vr = vrules(g)
    cb = checkboxes(g)
    tb = tables(hr, vr, W * S, H * S)
    ph = photos(g)
    res = dict(hrules=hr, vrules=vr, boxes=cb, tables=tb, photos=ph, width=W * S, height=H * S)
    json.dump(res, open(f, "w"))
    return res


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        r = analyse(int(a), force=True)
        print("page", a, "hrules", len(r["hrules"]), "vrules", len(r["vrules"]), "boxes", len(r["boxes"]), "tables", len(r["tables"]), "photos", len(r["photos"]))
        for t in r["tables"]:
            print("  table cols", [round(c) for c in t["cols"]], "rows", [round(y) for y in t["rows"]])
        for h in r["hrules"]:
            if h["clear"]:
                print("  rule", round(h["x0"]), round(h["x1"]), round(h["y"]), round(h["thick"], 1), "boxy" if h["boxy"] else "")
        for b in r["boxes"]:
            print("  box", round(b["x0"]), round(b["y0"]), round(b["x1"]), round(b["y1"]))
        for p in r["photos"]:
            print("  photo", round(p["x0"]), round(p["y0"]), round(p["x1"]), round(p["y1"]), round(p["fill"], 2), round(p["tone"], 2))
