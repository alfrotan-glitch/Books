"""Find small text lines NOT covered by the PDF text layer (candidates for upside-down answer keys).
Method: render page at 100 dpi, threshold, connected components -> glyph boxes (3..12 px high),
group into lines, keep lines with >= 6 glyphs that are < 30% covered by text-layer words."""
import fitz, numpy as np, sys
from scipy import ndimage
doc = fitz.open("Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf")
DPI = 100; S = DPI / 72.0
pages = [int(a) for a in sys.argv[1:]] or range(1, 180)
for pn in pages:
    pg = doc[pn-1]
    wboxes = [fitz.Rect(w[:4]) for w in pg.get_text("words")]
    pix = pg.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    dark = arr < 128
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    glyphs = []
    for i, sl in enumerate(objs):
        if sl is None: continue
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if 4 <= h <= 16 and 1 <= w <= 20:
            glyphs.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    if not glyphs: continue
    # group by baseline rows
    glyphs.sort(key=lambda g: (g[3], g[0]))
    lines = []
    for g in glyphs:
        placed = False
        for L in lines:
            if abs(L["bot"] - g[3]) <= 3 and g[0] - L["x1"] < 30:
                L["gl"].append(g); L["x1"] = max(L["x1"], g[2]); L["bot"] = (L["bot"] * (len(L["gl"]) - 1) + g[3]) / len(L["gl"])
                placed = True; break
        if not placed:
            lines.append({"gl": [g], "x1": g[2], "bot": g[3]})
    found = []
    for L in lines:
        if len(L["gl"]) < 8: continue
        x0 = min(g[0] for g in L["gl"]); y0 = min(g[1] for g in L["gl"]); x1 = L["x1"]; y1 = max(g[3] for g in L["gl"])
        r = fitz.Rect(x0 / S, y0 / S, x1 / S, y1 / S)
        if r.width < 40: continue
        cov = sum((wb & r).get_area() for wb in wboxes if wb.intersects(r))
        if cov < 0.3 * r.get_area():
            found.append((round(r.x0), round(r.y0), round(r.x1), round(r.y1), len(L["gl"])))
    if found:
        print(pn, found[:8], "..." if len(found) > 8 else "")
