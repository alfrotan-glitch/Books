"""Circled numerals: dark filled discs with a light digit inside (paragraph numbers in the margin of reading
passages, numbered steps).  -> list of dict(x0,y0,x1,y1,n,conf) in pt; n = recognised digit string or ''."""
import os, json
import numpy as np, cv2
import img
import tesserocr
from tesserocr import PSM
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "data", "discs")
S = img.S
_api = None


def api():
    global _api
    if _api is None:
        _api = tesserocr.PyTessBaseAPI(path="/tmp/tessdata", lang="eng", psm=PSM.SINGLE_CHAR)
        _api.SetVariable("tessedit_char_whitelist", "0123456789")
    return _api


def detect(pn, force=False):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"p{pn:03d}.json")
    if not force and os.path.exists(f):
        return json.load(open(f))
    g = img.page_gray(pn)
    dark = (g < 150).astype(np.uint8)     # the discs are printed in a mid-dark colour (blue / purple / black)
    # detach thin lines (margin brackets, rules) touching the discs: remove pixels that belong to long thin
    # horizontal / vertical runs, then open with a 3x3 kernel
    hlines = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (int(22 / S), 1)))
    vlines = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(22 / S))))
    dark = (dark & (1 - (hlines | vlines))).astype(np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, cent = cv2.connectedComponentsWithStats(dark, connectivity=8)
    out = []
    lo, hi = 8 / S, 15 / S            # margin discs are 12-13 pt, in-text list discs 10-11 pt; title glyphs are larger
    seen = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if not (lo <= w <= hi and lo <= h <= hi + 4 and 0.7 <= w / h <= 1.25):
            continue
        fill = area / (np.pi * (w / 2) * (h / 2))
        if fill < 0.55 or fill > 1.05:
            continue                       # a disc with a light digit knocked out has fill ~0.7-0.9
        # boundary must be round: pixels near the corners of the box are NOT part of the component
        comp = (lab[y:y + h, x:x + w] == i)
        k = max(1, min(w, h) // 5)
        corners = [comp[:k, :k].mean(), comp[:k, -k:].mean(), comp[-k:, :k].mean(), comp[-k:, -k:].mean()]
        if max(corners) > 0.35:
            continue
        # light digit inside: the central area has pixels much lighter than the disc body
        body = g[y:y + h, x:x + w][comp]
        body_tone = float(np.median(body)) if body.size else 0
        c = g[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4]
        if c.size == 0 or not (0.05 <= (c > body_tone + 60).mean() <= 0.7):
            continue                       # no digit (solid dot) or a hollow letter 'O' / 'C'
        # the light digit must be enclosed by the disc (a 'C' / 'G' glyph has no enclosed hole)
        sub_ = comp.astype(np.uint8)
        cnts_, _ = cv2.findContours(sub_.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled_ = np.zeros_like(sub_)
        cv2.drawContours(filled_, cnts_, -1, 1, thickness=-1)
        holes = int(filled_.sum()) - int(sub_.sum())
        if holes < 0.025 * filled_.sum():
            continue
        # the outline must be round: bold digits ("6", "8" of a numbered heading) have holes too but are not
        # ellipses.  Trim bracket stubs (rows / columns narrower than 60% of the maximum) before comparing.
        rw = filled_.sum(axis=1); rr = np.where(rw >= 0.3 * rw.max())[0]
        cw = filled_.sum(axis=0); cc = np.where(cw >= 0.3 * cw.max())[0]
        core = filled_[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1]
        ch, cw_ = core.shape
        if not (0.8 <= cw_ / max(1, ch) <= 1.25):
            continue
        ell = np.zeros_like(core)
        cv2.ellipse(ell, (cw_ // 2, ch // 2), (cw_ // 2, ch // 2), 0, 0, 360, 1, -1)
        iou = (core & ell).sum() / max(1, (core | ell).sum())
        if iou < 0.87:
            continue
        # the ring must be reasonably uniform (a photo blob is not): body tone below 135
        if body_tone > 135:
            continue
        # recognise the digit: invert the disc, pad, OCR as single char
        pad = 6
        crop = g[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad]
        mask = np.zeros_like(crop); yy0 = pad if y - pad >= 0 else y; xx0 = pad if x - pad >= 0 else x
        sub = comp.astype(np.uint8)
        # fill the holes (the knocked-out digit) so the mask covers the whole disc
        cnts, _ = cv2.findContours(sub.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(sub)
        cv2.drawContours(filled, cnts, -1, 1, thickness=-1)
        mask[yy0:yy0 + h, xx0:xx0 + w] = filled
        # inside the disc: the digit is the part that is much lighter than the disc body -> black digit on white
        thr = body_tone + 0.5 * (255 - body_tone)
        cands = [np.where((mask > 0) & (crop > thr), 0, 255).astype(np.uint8)]
        inv0 = np.where(mask > 0, 255 - crop, 255).astype(np.uint8)
        cands.append(np.where(mask > 0, np.clip((inv0.astype(int) - 60) * 2, 0, 255), 255).astype(np.uint8))
        # restrict to the round disc body (drop bracket stubs above / below): keep rows whose mask width is >= 60% max
        widths = mask.sum(axis=1)
        rows = np.where(widths >= 0.6 * widths.max())[0]
        if len(rows):
            r0, r1 = rows[0], rows[-1]
            cands += [c[max(0, r0 - 1):r1 + 2, :] for c in cands]
        a = api()
        txt, conf = "", 0.0
        for inv in cands:
            for scale in (4, 3):
                big = cv2.resize(inv, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                big = cv2.copyMakeBorder(big, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
                a.SetImage(Image.fromarray(big))
                a.Recognize()
                t_ = (a.GetUTF8Text() or "").strip(); c_ = float(a.MeanTextConf())
                if t_ and c_ > conf and len(t_) <= 2:
                    txt, conf = t_, c_
                if conf >= 80:
                    break
            if conf >= 80:
                break
        out.append(dict(x0=x * S, y0=y * S, x1=(x + w) * S, y1=(y + h) * S, n=txt, conf=float(conf)))
    json.dump(out, open(f, "w"))
    return out


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        for d in detect(int(a), force=True):
            print(a, round(d["x0"]), round(d["y0"]), round(d["x1"]), round(d["y1"]), repr(d["n"]), round(d["conf"]))
