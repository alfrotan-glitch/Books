"""Stage 1: per-page witness dump (two independent text sources).
 - Tesseract 5 LSTM (eng, tessdata_best) at 300 dpi, PSM AUTO, symbol-level iterator -> words with per-char confidences
 - embedded text layer words (rawdict) with font size / bold / italic
Output: tools/data/pages/pNNN.json.gz (coordinates in PDF points).
Usage: python3 stage1.py [page ...]
"""
import json, os, sys, gzip
import pymupdf, tesserocr
from tesserocr import RIL, PSM
from PIL import Image
from geom import ROTATED, rot_box, inside

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(os.path.dirname(ROOT), "Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf")
OUT = os.path.join(ROOT, "data", "pages")
TESSDATA = "/tmp/tessdata"
DPI = 300
S = 72.0 / DPI


def ensure_tessdata():
    os.makedirs(TESSDATA, exist_ok=True)
    f = os.path.join(TESSDATA, "eng.traineddata")
    if not os.path.exists(f):
        src = os.path.join(ROOT, "data", "eng.traineddata")
        if os.path.exists(src):
            import shutil; shutil.copy(src, f)
        else:
            raise SystemExit("eng.traineddata missing: run bootstrap.py")


def embedded_words(page):
    words = []
    d = page.get_text("rawdict")
    for b in d["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                font = sp["font"]; size = sp["size"]; flags = sp["flags"]
                bold = bool(flags & 16) or "Bold" in font
                italic = bool(flags & 2) or "Italic" in font
                cur = []

                def flush():
                    if not cur:
                        return
                    txt = "".join(c["c"] for c in cur)
                    if txt.strip():
                        x0 = min(c["bbox"][0] for c in cur); y0 = min(c["bbox"][1] for c in cur)
                        x1 = max(c["bbox"][2] for c in cur); y1 = max(c["bbox"][3] for c in cur)
                        words.append(dict(x0=round(x0, 2), y0=round(y0, 2), x1=round(x1, 2), y1=round(y1, 2), text=txt,
                                          size=round(size, 1), bold=bold, italic=italic, font=font))
                    cur.clear()
                for ch in sp["chars"]:
                    if ch["c"].isspace():
                        flush()
                    else:
                        cur.append(ch)
                flush()
    return words


def tess_words(api, img):
    api.SetImage(img)
    api.Recognize()
    ri = api.GetIterator()
    words = []
    if ri is None:
        return words
    cur = None
    blk = -1; ln = -1
    while True:
        try:
            if ri.IsAtBeginningOf(RIL.BLOCK):
                blk += 1
            if ri.IsAtBeginningOf(RIL.TEXTLINE):
                ln += 1
            if ri.IsAtBeginningOf(RIL.WORD):
                if cur:
                    words.append(cur)
                wt = ri.GetUTF8Text(RIL.WORD) or ""
                wb = ri.BoundingBox(RIL.WORD)
                wc = ri.Confidence(RIL.WORD)
                try:
                    fa = ri.WordFontAttributes() or {}
                except Exception:
                    fa = {}
                cur = dict(text=wt.strip(), conf=round(wc, 1), blk=blk, ln=ln,
                           x0=round(wb[0] * S, 2), y0=round(wb[1] * S, 2), x1=round(wb[2] * S, 2), y1=round(wb[3] * S, 2),
                           pt=fa.get("pointsize"), chars=[])
            st = ri.GetUTF8Text(RIL.SYMBOL) or ""
            sb = ri.BoundingBox(RIL.SYMBOL)
            sc = ri.Confidence(RIL.SYMBOL)
            if cur is not None and sb is not None:
                cur["chars"].append([st, round(sc, 1), round(sb[0] * S, 2), round(sb[1] * S, 2), round(sb[2] * S, 2), round(sb[3] * S, 2)])
        except Exception:
            pass
        if not ri.Next(RIL.SYMBOL):
            break
    if cur:
        words.append(cur)
    return words


def tess_rotated(api, page, clip, ang, blk_base):
    """recognise a tilted region on its de-rotated crop; boxes come back in the straightened frame."""
    import numpy as np, cv2
    r = pymupdf.Rect(*clip)
    pix = page.get_pixmap(dpi=DPI, clip=r, colorspace=pymupdf.csGRAY)
    g = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
    M = cv2.getRotationMatrix2D((g.shape[1] / 2, g.shape[0] / 2), ang, 1.0)
    rot = cv2.warpAffine(g, M, (g.shape[1], g.shape[0]), borderValue=255)
    api.SetPageSegMode(PSM.SINGLE_BLOCK)
    words = tess_words(api, Image.fromarray(rot))
    api.SetPageSegMode(PSM.AUTO)
    out = []
    for w in words:
        if not w["text"].strip():
            continue
        w = dict(w, x0=round(w["x0"] + r.x0, 2), y0=round(w["y0"] + r.y0, 2), x1=round(w["x1"] + r.x0, 2), y1=round(w["y1"] + r.y0, 2),
                 blk=w["blk"] + blk_base, rot=True)
        w["chars"] = [[c[0], c[1], round(c[2] + r.x0, 2), round(c[3] + r.y0, 2), round(c[4] + r.x0, 2), round(c[5] + r.y0, 2)] for c in w["chars"]]
        out.append(w)
    return out


def dump_page(doc, api, pn):
    page = doc[pn - 1]
    pix = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    tess = tess_words(api, img)
    emb = embedded_words(page)
    for k, (clip, ang) in enumerate(ROTATED.get(pn, [])):
        tess = [w for w in tess if not inside(w, clip)]
        tess.extend(tess_rotated(api, page, clip, ang, 1000 * (k + 1)))
        emb = [rot_box(w, clip, ang) if inside(w, clip) else w for w in emb]
    rec = dict(page=pn, width=page.rect.width, height=page.rect.height, embedded=emb, tess=tess)
    with gzip.open(os.path.join(OUT, f"p{pn:03d}.json.gz"), "wt") as f:
        json.dump(rec, f)
    return rec


def load(pn):
    with gzip.open(os.path.join(OUT, f"p{pn:03d}.json.gz"), "rt") as f:
        return json.load(f)


def main():
    ensure_tessdata()
    os.makedirs(OUT, exist_ok=True)
    doc = pymupdf.open(PDF)
    pages = [int(a) for a in sys.argv[1:]] or list(range(1, len(doc) + 1))
    api = tesserocr.PyTessBaseAPI(path=TESSDATA, lang="eng", psm=PSM.AUTO)
    for pn in pages:
        rec = dump_page(doc, api, pn)
        print(pn, len(rec["embedded"]), len(rec["tess"]), flush=True)


if __name__ == "__main__":
    main()
