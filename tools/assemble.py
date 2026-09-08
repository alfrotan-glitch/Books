"""Stage 3: layout assembly.  Takes the fused words of a page plus the image analysis and produces an ordered list
of blocks: dict(kind, lines=[{text, x0, y0, size, bold, italic}], x0, y0, x1, y1, size, bold, ...).
kinds: heading, para, item, table, footer, header, note
"""
import re, sys, os, json, statistics, collections
from fuse import fuse_page, alnum, letters, dict_ok, clean
import img, discs
from quality import is_word, words

CIRCLED = "⓪①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
BLANK = "________"
ITEM_RE = re.compile(r"^(\d{1,2}[.)]?|[a-h][.)]?|[A-H][.)]?|[•●■☐▪○]|\(?[a-h]\)|\(?\d{1,2}\)|[ivx]{1,4}\.)$")


# ------------------------------------------------------------------------------------------------------------
# helpers
def yc(w):
    return (w["y0"] + w["y1"]) / 2


def overlap_y(a, b):
    return min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])


def is_blank(w):
    return w["text"] == BLANK


def is_item_marker(w, nxt):
    """w is an item marker (number / letter / bullet) followed by a word to its right on the same line"""
    t = w["text"]
    if not ITEM_RE.match(t):
        return False
    if nxt is None:
        return t in ("•", "●", "■", "☐") or bool(re.fullmatch(r"\d{1,2}\.?", t))
    gap = nxt["x0"] - w["x1"]
    if re.fullmatch(r"[a-h]", t):
        # a lower-case letter is a marker only if it is followed by a clear gap (articles 'a' have gap <= 4.1)
        if w["src"] == "emb-only" and gap >= 4.5:
            return True                # embedded layer keeps the bold marker letters tesseract dropped
        if t != "a" and gap >= 4.5:
            return True                # only "a" is also an English word
        return gap >= 5.5 and (w.get("bold") or gap >= 7 or nxt["text"][:1].isupper() or is_blank(nxt))
    if re.fullmatch(r"[A-H]", t):
        return gap >= 4 and (w.get("bold") or w["size"] >= 11 or (nxt.get("bold") and nxt["text"][:1].isupper()))
    if re.fullmatch(r"\d{1,2}", t):
        return gap >= 3.5 and gap <= 40 and not re.match(r"^[%°,.\d]", nxt["text"]) and not re.match(r"^(percent|million|billion|thousand|hours?|minutes?|years?|days?|weeks?|months?|kilometers?|miles?|dollars|pounds|to|and|or|of|p\.m\.|a\.m\.|pm|am|o'clock|times)$", nxt["text"].lower())
    return gap >= 2


# ------------------------------------------------------------------------------------------------------------
def collect(pn):
    words = fuse_page(pn)
    ana = img.analyse(pn)
    W, H = ana["width"], ana["height"]
    dd = discs.detect(pn)

    # ---- check boxes / discs: remove words that overlap them, add glyph words --------------------------------
    boxes = ana["boxes"]
    def hit(w, b, frac=0.5):
        xo = min(w["x1"], b["x1"]) - max(w["x0"], b["x0"]); yo = min(w["y1"], b["y1"]) - max(w["y0"], b["y0"])
        if xo <= 0 or yo <= 0:
            return False
        return xo * yo >= frac * max(1e-6, (w["x1"] - w["x0"]) * (w["y1"] - w["y0"]))
    words = [w for w in words if not any(hit(w, b, 0.4) for b in boxes)]
    for b in boxes:
        words.append(dict(x0=b["x0"], y0=b["y0"], x1=b["x1"], y1=b["y1"], text="☐", size=10.0, bold=False, italic=False, conf=99, src="glyph", flag=False, h=b["y1"] - b["y0"]))
    # discs: margin paragraph numbers and in-text list numbers.  Keep only detections that are not letter
    # counters of large type: a disc overlapping a word of the text layer with size > 13 is a glyph hole.
    def on_big_text(d):
        for w in words:
            if (w["size"] or 10) > 13 and min(w["x1"], d["x1"]) - max(w["x0"], d["x0"]) > 0 and min(w["y1"], d["y1"]) - max(w["y0"], d["y0"]) > 0:
                # the word IS the disc (tesseract reading of the white digit in the disc, e.g. "[3]", "@", "©")
                if (w["x1"] - w["x0"]) <= 16 and (w["y1"] - w["y0"]) <= 16 and hit(w, d, 0.5) and \
                        (re.fullmatch(r"[\[\(\{|]\d[\]\)\}|]?|\d[\]\)\}|]", w["text"]) or not alnum(w["text"]) or w["conf"] < 60):
                    continue
                # a single digit / 'O' box of the same footprint as the disc (the disc itself read as a numeral)
                if (w["x1"] - w["x0"]) <= 18 and (w["y1"] - w["y0"]) <= 26 and len(w["text"]) <= 2 and \
                        re.fullmatch(r"[0-9Oo@©®]{1,2}", w["text"]) and hit(d, w, 0.8) and w["src"] in ("emb-only", "tess", "emb"):
                    continue
                return True
        return False
    dd = [d for d in dd if not on_big_text(d) and (d["y0"] > 60 or d["x0"] < 90)]
    # in-text discs (not in the margin) need a confidently recognised digit
    dd = [d for d in dd if (d["x0"] < 90 or d["x0"] > 500) or (d["n"].isdigit() and d["conf"] >= 60)]
    margin_discs = [d for d in dd if d["x0"] < 90 or d["x0"] > 500]
    for d in dd:
        words = [w for w in words if not hit(w, d, 0.3)]
    # number the margin discs sequentially top-to-bottom, use OCR digit when confident and consistent
    margin_discs.sort(key=lambda d: d["y0"])
    for k, d in enumerate(margin_discs):
        n = d["n"] if d["n"].isdigit() and d["conf"] >= 60 else ""
        d["num"] = int(n) if n else None
    # consistency: if the confident digits are increasing and match k+offset use the offset, else sequential
    nums = [(k, d["num"]) for k, d in enumerate(margin_discs) if d["num"] is not None]
    offset = None
    if nums:
        offs = {n - k for k, n in nums}
        if len(offs) == 1:
            offset = offs.pop()
    if offset is None:
        offset = 1
    for k, d in enumerate(margin_discs):
        n = k + offset
        d["glyph"] = CIRCLED[n] if 0 <= n < len(CIRCLED) else f"({n})"
    text_discs = [d for d in dd if d not in margin_discs]
    text_discs.sort(key=lambda d: (round(d["y0"] / 6), d["x0"]))
    for k, d in enumerate(text_discs):
        n = int(d["n"]) if d["n"].isdigit() and d["conf"] >= 60 else k + 1
        d["glyph"] = CIRCLED[n] if 0 <= n < len(CIRCLED) else f"({n})"
    for d in dd:
        words.append(dict(x0=d["x0"], y0=d["y0"], x1=d["x1"], y1=d["y1"], text=d["glyph"], size=10.0, bold=True, italic=False, conf=99, src="glyph", flag=False, h=d["y1"] - d["y0"], disc=True, margin=d in margin_discs))

    # ---- rules -> blanks ------------------------------------------------------------------------------------
    hr = ana["hrules"]
    tables = ana["tables"]
    def in_table(x0, x1, y):
        return any(t["x0"] - 4 <= x0 and x1 <= t["x1"] + 4 and t["y0"] - 4 <= y <= t["y1"] + 4 for t in tables)
    def in_photo(x0, y0, x1, y1):
        return any(p["x0"] - 2 <= x0 and x1 <= p["x1"] + 2 and p["y0"] - 2 <= y0 and y1 <= p["y1"] + 2 for p in ana["photos"])
    blanks = []
    vr = ana["vrules"]
    def boxy(h):
        # a vertical rule starting / ending near one end of the rule -> box border (rounded corners included);
        # short writing lines (< 60 pt) only count when the vertical rule really touches them
        tol = 9 if (h["x1"] - h["x0"]) >= 60 else 3
        for v in vr:
            for xe in (h["x0"], h["x1"]):
                if abs(v["x"] - xe) <= tol and (abs(v["y0"] - h["y"]) <= tol or abs(v["y1"] - h["y"]) <= tol):
                    return True
        return False
    def stacked(h):
        # same-length rule at (nearly) the same x within 10..24 pt above / below -> member of a stack of writing lines
        L = h["x1"] - h["x0"]
        return any(k is not h and k["clear"] and abs(k["x0"] - h["x0"]) <= 3 and abs((k["x1"] - k["x0"]) - L) <= 4
                   and 10 <= abs(k["y"] - h["y"]) <= 24 for k in hr)
    def band_fragment(h):
        # slanted decorative colour band (Self Check pages): a swarm of thin short fragments whose y drifts
        if h["thick"] > 0.7 or (h["x1"] - h["x0"]) > 160:
            return False
        near = [k for k in hr if k is not h and k["thick"] <= 0.7 and (k["x1"] - k["x0"]) <= 160 and abs(k["y"] - h["y"]) <= 12
                and (k["x0"] < h["x1"] + 60 and k["x1"] > h["x0"] - 60)]
        ys = {round(k["y"]) for k in near}
        drift = sum(1 for k in near if 1 <= abs(k["y"] - h["y"]) <= 6)
        return (len(near) >= 4 and len(ys) >= 3) or (len(near) >= 3 and drift >= 2)
    for h in hr:
        L = h["x1"] - h["x0"]
        if h["boxy"] or L < 14 or boxy(h):
            continue
        if band_fragment(h):
            continue
        # faint edge of a notepad / box artwork: thin (<= 0.5 pt) rule with other thin fragments at the same y
        # further right and no text on the line or in the 30 pt above it
        if h["thick"] <= 0.5 and any(k is not h and k["thick"] <= 0.5 and abs(k["y"] - h["y"]) <= 2 and k["x0"] > h["x1"] + 4 for k in hr):
            around = [w for w in words if alnum(w["text"]) and w["x1"] > h["x0"] - 20 and w["x0"] < h["x1"] + 250 and h["y"] - 16 <= w["y1"] <= h["y"] + 3]
            if not around:
                continue
        # arcs of a hand-drawn oval around an instruction word ("Circle") scanned as short rules
        if L < 24 and any(w.get("oval") or (w["text"] == "Circle" and w["src"] in ("glyph", "tess")) for w in words
                          if w["x0"] - 12 <= h["x0"] and h["x1"] <= w["x1"] + 12 and w["y0"] - 12 <= h["y"] <= w["y1"] + 12):
            continue
        if not h["clear"] and not (h["clear_above"] and L < 60 and stacked(h)):
            continue
        if in_table(h["x0"], h["x1"], h["y"]):
            continue
        if h["thick"] > 2.2:
            continue
        if h["thick"] >= 1.2 and L >= 0.5 * W:
            continue                     # section divider
        if h["thick"] >= 1.2 and L >= 300:
            # a long rule with no text on either side within 12 pt above it is a divider, not a writing line
            above = [w for w in words if alnum(w["text"]) and -14 <= h["y"] - w["y1"] <= 3 and w["x1"] > h["x0"] and w["x0"] < h["x1"]]
            if not above:
                continue
        # a full-width rule is a divider unless it is part of a stack of writing lines
        if L > 0.72 * W:
            stack = [k for k in hr if k is not h and k["clear"] and abs((k["x1"] - k["x0"]) - L) < 30 and 10 <= abs(k["y"] - h["y"]) <= 24]
            if not stack:
                continue
        # a rule directly under text of the same width is an underline (heading underline) -> not a blank
        under = [w for w in words if w["y1"] <= h["y"] + 3 and w["y1"] >= h["y"] - 6 and w["x0"] >= h["x0"] - 4 and w["x1"] <= h["x1"] + 4 and alnum(w["text"])]
        if under and sum(u["x1"] - u["x0"] for u in under) > 0.6 * L:
            continue
        big = [w for w in words if (w["size"] or 10) >= 14 and w["y1"] <= h["y"] + 4 and w["y1"] >= h["y"] - 14 and w["x1"] > h["x0"] and w["x0"] < h["x1"] and alnum(w["text"])]
        if big and sum(u["x1"] - u["x0"] for u in big) > 0.4 * L:
            continue                     # underline of a large heading
        # chapter-title rule: a long rule (>= 300 pt) directly under a bold heading block (size >= 14) within 30 pt
        if L >= 300 and h["y"] < 140:
            big2 = [w for w in words if (w["size"] or 10) >= 14 and w["bold"] and w["y1"] <= h["y"] + 4 and w["y1"] >= h["y"] - 30 and alnum(w["text"])]
            if len(big2) >= 2:
                continue
        # a printed em dash at the end of a large word is not a writing line
        if L <= 24 and any((w["size"] or 10) >= 12 and w["text"].endswith(("—", "–", "-")) and abs(w["x1"] - h["x1"]) <= 4 and w["y0"] <= h["y"] <= w["y1"] for w in words):
            continue
        # photo frame edges
        if any(p["x0"] - 6 <= h["x0"] and h["x1"] <= p["x1"] + 6 and (abs(h["y"] - p["y0"]) <= 6 or abs(h["y"] - p["y1"]) <= 6 or p["y0"] <= h["y"] <= p["y1"])
               and not p.get("panel") for p in ana["photos"]):
            continue
        blanks.append(dict(x0=h["x0"], y0=h["y"] - 7, x1=h["x1"], y1=h["y"] + 1, text=BLANK, size=10.0, bold=False, italic=False, conf=99, src="blank", flag=False, h=8, rule_y=h["y"], L=L))
    # one writing line scanned as two fragments (small gap, nothing printed in between) -> one blank
    blanks.sort(key=lambda b: (round(b["rule_y"] / 3), b["x0"]))
    merged = []
    for b in blanks:
        if merged and abs(merged[-1]["rule_y"] - b["rule_y"]) <= 2.5 and 0 <= b["x0"] - merged[-1]["x1"] <= 12 \
                and merged[-1]["L"] < 0.4 * W and b["L"] < 0.4 * W \
                and not any(alnum(w["text"]) and merged[-1]["x1"] - 1 <= w["x0"] and w["x1"] <= b["x0"] + 1 and abs(yc(w) - b["rule_y"]) < 8 for w in words):
            merged[-1]["x1"] = b["x1"]; merged[-1]["L"] = merged[-1]["x1"] - merged[-1]["x0"]
        else:
            merged.append(b)
    blanks = merged
    # remove words that are just rule fragments read as text ("—", "_", "..." lying on a rule) and words fully
    # inside a blank that are conf-0 junk
    keep = []
    for w in words:
        if w["src"] == "tess" and re.fullmatch(r"[—–_\-=~.,:;'\"“”’‘`]+", w["text"]):
            if re.fullmatch(r"[.,:;]+", w["text"]):
                if any(abs(yc(w) - b["rule_y"]) < 5 and b["x0"] + 2 <= w["x0"] and w["x1"] <= b["x1"] - 3 for b in blanks):
                    continue
            elif any(abs(yc(w) - b["rule_y"]) < 5 and b["x0"] - 3 <= w["x0"] and w["x1"] <= b["x1"] + 3 for b in blanks):
                continue
        keep.append(w)
    words = keep
    # drop tess-only junk sitting on a blank (Arial-Italic dummy handwriting excluded by conf)
    keep = []
    for w in words:
        on_blank = [b for b in blanks if b["x0"] - 2 <= w["x0"] and w["x1"] <= b["x1"] + 2 and -12 <= b["rule_y"] - w["y1"] <= 4]
        if on_blank and w["src"] == "tess" and (w["flag"] or w["conf"] < 60 or re.fullmatch(r"([A-Za-z])\1{2,}", alnum(w["text"]))):
            continue
        if on_blank and w["src"] == "emb-only" and not (w["bold"]):
            # embedded layer often has dummy strings on writing lines
            if not dict_ok(w["text"]) or len(alnum(w["text"])) <= 2:
                continue
        keep.append(w)
    words = keep + blanks
    return words, ana, W, H


# ------------------------------------------------------------------------------------------------------------
def header_footer(words, W, H):
    head, foot, body = [], [], []
    body_words = [w for w in words if 30 <= yc(w) < H - 40 and alnum(w["text"])]
    last_body = max((w["y1"] for w in body_words), default=0)
    # the running foot is the lowest text line (y >= H-40); text lines above it that continue a body line stay body
    def foot_type(w):
        # running-foot type is 8-9 pt; the embedded layer sometimes reports 10 for it -> accept 10 when the box is short
        return (w["size"] or 10) <= 9.6 or ((w["size"] or 10) <= 10.6 and (w["y1"] - w["y0"]) <= 9.5)
    cand = [w for w in words if yc(w) >= H - 40 and foot_type(w) and alnum(w["text"])]
    foot_line_y = max((yc(w) for w in cand), default=None)
    if foot_line_y is None:
        # slightly shifted scan: accept the lowest line down to H-50 when it carries a folio at the outer edge
        cand2 = [w for w in words if yc(w) >= H - 50 and foot_type(w) and alnum(w["text"])]
        if cand2:
            y2 = max(yc(w) for w in cand2)
            line2 = [w for w in cand2 if abs(yc(w) - y2) <= 5]
            if any(re.fullmatch(r"\d{1,3}", w["text"]) and (w["x0"] < 60 or w["x1"] > W - 60) for w in line2) and \
                    not any(30 <= yc(w) < y2 - 6 and w["y1"] > y2 - 14 and alnum(w["text"]) for w in words):
                cand = cand2; foot_line_y = y2
                H = y2 + 30   # so the "y >= H - 40" tests below use this line as the foot
    # the running foot carries the folio (a 1-3 digit bold number at the outer edge); footnotes of a passage
    # are set in light 7-8 pt type and stay in the body even when they reach the foot area
    foot_line = [w for w in cand if foot_line_y is not None and abs(yc(w) - foot_line_y) <= 5]
    folio = [w for w in foot_line if re.fullmatch(r"\d{1,3}", w["text"]) and (w["x0"] < 60 or w["x1"] > W - 60)]
    # words of the foot line that are set smaller than the folio and form a long run (>= 6 words) are a footnote
    small = [w for w in foot_line if folio and (w["size"] or 10) <= folio[0]["size"] - 0.8]
    footnote = set(id(w) for w in small) if len(small) >= 6 else set()
    # the last body line: text within 8 pt above the foot line is body only when it is a real text line (the foot
    # line itself must not be counted as "body" when a line sits just above it)
    last_body = max((w["y1"] for w in body_words if foot_line_y is None or yc(w) < foot_line_y - 6), default=0)
    for w in words:
        y = yc(w)
        if y < 30 and (w["size"] or 10) <= 12:
            head.append(w)
        elif y >= H - 40 and foot_type(w) and (y - last_body >= 7 or w["y0"] - last_body >= 3) \
                and (foot_line_y is None or abs(y - foot_line_y) <= 5) and id(w) not in footnote:
            foot.append(w)
        else:
            body.append(w)
    # the footer contains only the running foot: strip bullet / rule junk
    foot = [w for w in foot if w["text"] not in ("•", "●", BLANK, "☐")]
    foot.sort(key=lambda w: w["x0"])
    return head, foot, body


def drop_junk(words, ana, W, H):
    out = []
    # specks on table borders: a low-confidence single character sitting on / just outside a table edge
    tables = ana.get("tables", [])
    def on_table_edge(w):
        xc = (w["x0"] + w["x1"]) / 2; yc_ = yc(w)
        for t in tables:
            if t["y0"] - 8 <= yc_ <= t["y1"] + 8 and (abs(xc - t["x0"]) <= 8 or abs(xc - t["x1"]) <= 8):
                return True
            if t["x0"] - 8 <= xc <= t["x1"] + 8 and (abs(yc_ - t["y0"]) <= 8 or abs(yc_ - t["y1"]) <= 8):
                return True
        return False
    def starts_line(w):
        # a word begins within 12 pt to the right on the same line (item number / letter followed by text)
        return any(v is not w and alnum(v["text"]) and 0 <= v["x0"] - w["x1"] <= 12 and overlap_y(v, w) > 0.4 * (w["y1"] - w["y0"]) for v in words)
    def at_table_corner(w):
        for t in tables:
            for cx in (t["x0"], t["x1"]):
                for cy in (t["y0"], t["y1"]):
                    if w["x0"] - 6 <= cx <= w["x1"] + 6 and w["y0"] - 6 <= cy <= w["y1"] + 6:
                        return True
        return False
    words = [w for w in words if not (w["src"] == "tess" and 2 <= len(w["text"]) <= 3 and w["conf"] < 85 and not w.get("disc")
                                      and at_table_corner(w) and not (is_word(w["text"].lower()) and len(w["text"]) >= 3) and not w["text"].isdigit())]
    words = [w for w in words if not (w["src"] == "tess" and len(w["text"]) == 1 and w["text"] not in ("☐",) and w["conf"] < 80
                                      and not w.get("disc") and on_table_edge(w) and w.get("size", 10) <= 12
                                      and not (w["text"].isalnum() and starts_line(w) and not (w["text"] in "Il|" and (w["y1"] - w["y0"]) >= 11)))]
    # embedded-only numerals / brackets inside a photograph (answer-sheet artwork etc.)
    def in_photo(w):
        return any(p["x0"] - 2 <= w["x0"] and w["x1"] <= p["x1"] + 2 and p["y0"] - 2 <= w["y0"] and w["y1"] <= p["y1"] + 2
                   and not p.get("panel") for p in ana["photos"])
    for w in words:
        t = w["text"]
        if w["src"] == "emb-only" and in_photo(w) and (re.fullmatch(r"\d{1,3}|[A-Za-z]", t) or not dict_ok(t) or len(alnum(t)) <= 2):
            continue
        if w["src"] == "tess" and in_photo(w) and (w["conf"] < 90 and not (dict_ok(t) and len(alnum(t)) >= 3)):
            # lettering inside photos: keep only confident dictionary words (captions are outside photos)
            continue
        # photo lettering: tess-only words wholly inside a photograph, single word lines
        if w["src"] in ("tess",) and w.get("flag"):
            for p in ana["photos"]:
                if not p.get("panel") and p["x0"] <= w["x0"] and w["x1"] <= p["x1"] and p["y0"] <= w["y0"] and w["y1"] <= p["y1"]:
                    # ... unless it is a dictionary word continuing a confident title line inside the photo
                    hh = w["y1"] - w["y0"]
                    if dict_ok(t) and len(alnum(t)) >= 3 and any(v is not w and v["src"] == "tess" and not v.get("flag") and v["conf"] >= 80
                                                                 and overlap_y(v, w) > 0.5 * hh and abs((v["y1"] - v["y0"]) - hh) < 0.5 * hh
                                                                 and (0 <= w["x0"] - v["x1"] <= 15 or 0 <= v["x0"] - w["x1"] <= 15) for v in words):
                        out.append(w)
                    break
            else:
                out.append(w)
            continue
        if w["src"] == "tess" and w["conf"] < 60 and not dict_ok(t):
            inside = [p for p in ana["photos"] if not p.get("panel") and p["x0"] <= w["x0"] and w["x1"] <= p["x1"] and p["y0"] <= w["y0"] and w["y1"] <= p["y1"]]
            if inside:
                continue
        out.append(w)
    return out


def margin_numbers(words, W):
    """line numbers printed in the margin of reading passages (5, 10, 15 ...) -> "[n]" markers"""
    out = []
    for w in words:
        t = w["text"]
        if re.fullmatch(r"\d{1,2}", t) and int(t) % 5 == 0 and int(t) <= 60 and (w["size"] or 10) <= 11.5 and (w["x0"] < 95 or w["x1"] > 500) \
                and not w.get("bold") and ((w["y1"] - w["y0"]) <= 9.5 or (w["src"] == "emb-only" and (w["y1"] - w["y0"]) <= 15)):
            # a genuine margin number stands alone: no word within 8 pt on its line side (a right-margin number
            # may sit close to a long justified line: allow 3 pt on the text side when the number is beyond x=505)
            gap_l = 3 if w["x0"] > 505 else 8
            near = [v for v in words if v is not w and overlap_y(v, w) > 0 and (0 <= v["x0"] - w["x1"] <= 8 or 0 <= w["x0"] - v["x1"] <= gap_l)]
            # ... and other item numbers of the same list sit at the same x above / below (steps of ~14 pt)
            column = [v for v in words if v is not w and re.fullmatch(r"\d{1,2}", v["text"]) and abs(v["x0"] - w["x0"]) <= 2.5
                      and 8 <= abs(yc(v) - yc(w)) <= 32 and int(v["text"]) in (int(t) - 1, int(t) + 1)]
            if not near and not column:
                out.append(dict(w, text=f"[{t}]", margin_no=True))
                continue
        out.append(w)
    return out


def drop_numeral_runs(words):
    """OCR noise: sequences of isolated numerals / letters at the same x (spiral binding, scale artwork)"""
    return words


# ------------------------------------------------------------------------------------------------------------
def group_lines(words):
    """group words into text lines by vertical overlap; each line sorted by x."""
    ws = sorted(words, key=lambda w: (yc(w), w["x0"]))
    lines = []
    for w in ws:
        best = None
        for ln in lines[-12:]:
            ov = min(ln["y1"], w["y1"]) - max(ln["y0"], w["y0"])
            hmin = min(ln["y1"] - ln["y0"], w["y1"] - w["y0"])
            if (w["y1"] - w["y0"]) < 4 and not alnum(w["text"]):
                # punctuation speck: belongs to the line whose vertical range contains it
                if ln["y0"] - 2 <= yc(w) <= ln["y1"] + 2:
                    best = ln; break
                continue
            if ov > 0.45 * hmin and abs(yc(w) - ln["yc"]) < 0.6 * max(hmin, 4):
                # horizontal proximity: allow anywhere on the line (columns are cut before this stage)
                best = ln; break
        if best is None:
            lines.append(dict(words=[w], y0=w["y0"], y1=w["y1"], yc=yc(w)))
        else:
            best["words"].append(w)
            ys = [v["y0"] for v in best["words"] if alnum(v["text"])] or [v["y0"] for v in best["words"]]
            ye = [v["y1"] for v in best["words"] if alnum(v["text"])] or [v["y1"] for v in best["words"]]
            best["y0"] = statistics.median(ys); best["y1"] = statistics.median(ye); best["yc"] = (best["y0"] + best["y1"]) / 2
    for ln in lines:
        ln["words"].sort(key=lambda w: w["x0"])
        ln["x0"] = min(w["x0"] for w in ln["words"]); ln["x1"] = max(w["x1"] for w in ln["words"])
        sizes = [w["size"] for w in ln["words"] if alnum(w["text"]) and w["size"]]
        ln["size"] = statistics.median(sizes) if sizes else (ln["words"][0]["size"] or 10)
        ln["bold"] = sum(1 for w in ln["words"] if w["bold"] and alnum(w["text"])) > 0.5 * max(1, sum(1 for w in ln["words"] if alnum(w["text"])))
    lines.sort(key=lambda l: (l["yc"], l["x0"]))
    return lines


def line_text(ln):
    parts = []
    ws_all = ln["words"]
    for i, w in enumerate(ws_all):
        t = w["text"]
        # a low-confidence full stop speck at the end of a line whose next line continues the sentence
        if w.get("flag") and t == "." and w["conf"] < 60 and i == len(ws_all) - 1 and i > 0 and (w["y1"] - w["y0"]) <= 2.5 \
                and re.search(r"[A-Za-z]$", ws_all[i - 1]["text"]) and not ws_all[i - 1]["text"][:1].isupper():
            continue
        if w.get("flag"):
            t = "{?" + t + "}"
        if i > 0:
            prev = ln["words"][i - 1]
            if w["x0"] - prev["x1"] > 0.35 * (w["size"] or 10) or prev["text"] == BLANK or t == BLANK or True:
                parts.append(" ")
        parts.append(t)
    s = "".join(parts).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r" ([,.;:!?])(?= |$)", r"\1", s)
    s = re.sub(r"(\() ", r"\1", s)
    s = re.sub(r" (\))", r"\1", s)
    return s


# ------------------------------------------------------------------------------------------------------------
def xy_cut(words, W, H, depth=0, seps=()):
    """recursive XY cut on word boxes: returns list of word groups in reading order (top-down, left-right)."""
    if not words:
        return []
    # hard separators (tinted panel edges / long vertical rules) cut the zone even when the white gap is narrow
    if depth < 6:
        ws_ = [w for w in words if alnum(w["text"]) or w["text"] in (BLANK, "☐", "…", "(✓)", "✓")]
        if len(ws_) >= 2:
            zy0 = min(w["y0"] for w in ws_); zy1 = max(w["y1"] for w in ws_)
            for sx, sy0, sy1 in sorted(seps, key=lambda s: -(min(s[2], zy1) - max(s[1], zy0))):
                cover = min(sy1, zy1) - max(sy0, zy0)
                if cover >= 0.7 * (zy1 - zy0) or (sy0 <= zy0 + 6 and sy1 >= zy1 - 6):
                    left = [w for w in words if (w["x0"] + w["x1"]) / 2 <= sx]
                    right = [w for w in words if (w["x0"] + w["x1"]) / 2 > sx]
                    crossing = [w for w in ws_ if w["x0"] < sx - 3 and w["x1"] > sx + 3]
                    # a text line that straddles the separator where the separator does not exist (above / below it)
                    for w in ws_:
                        if w["x1"] <= sx and (w["y1"] < sy0 + 2 or w["y0"] > sy1 - 2):
                            if any(v["x0"] >= sx and abs(yc(v) - yc(w)) < 4 and v["x0"] - w["x1"] < 2.5 * (w["size"] or 10) for v in ws_):
                                crossing.append(w); break
                    if left and right and not crossing and any(alnum(w["text"]) for w in left) and any(alnum(w["text"]) for w in right):
                        return xy_cut(left, W, H, depth + 1, seps) + xy_cut(right, W, H, depth + 1, seps)
    ws = [w for w in words if alnum(w["text"]) or w["text"] in (BLANK, "☐", "…", "(✓)", "✓") or w["src"] == "bridge"]
    if len([w for w in ws if w["src"] != "bridge"]) < 2 or depth > 8:
        return [words]
    sizes = sorted(w["size"] or 10 for w in ws if w["src"] != "bridge")
    med = sizes[len(sizes) // 2]
    x0 = min(w["x0"] for w in ws); x1 = max(w["x1"] for w in ws)
    y0 = min(w["y0"] for w in ws); y1 = max(w["y1"] for w in ws)
    # horizontal bands (gaps in y)
    ys = sorted(ws, key=lambda w: w["y0"])
    gaps = []
    cur = ys[0]["y1"]
    for w in ys[1:]:
        if w["y0"] - cur >= 0.75 * med:
            gaps.append((w["y0"] - cur, cur, w["y0"]))
        cur = max(cur, w["y1"])
    # vertical gutters (gaps in x) that span the whole group height
    xs = sorted(ws, key=lambda w: w["x0"])
    vg = []
    cur = xs[0]["x1"]
    for w in xs[1:]:
        if w["x0"] - cur >= 11:
            vg.append((w["x0"] - cur, cur, w["x0"]))
        cur = max(cur, w["x1"])
    # prefer the widest vertical gutter if the group is tall enough, else the largest horizontal gap
    zone_h = y1 - y0
    best_v = max(vg, default=None)
    # a short zone (1-2 lines) is still split at a wide gutter when the two sides do not share a text line
    # (e.g. "UNIT 4 | CHAPTER 1 Title" and "Before You Read | A Read the following ...")
    short_ok = False
    if best_v and zone_h < 2.2 * med and best_v[0] >= 18 and depth < 6:
        g, a, b = best_v
        L = [w for w in ws if (w["x0"] + w["x1"]) / 2 <= a + g / 2 and w["src"] != "bridge"]
        R = [w for w in ws if (w["x0"] + w["x1"]) / 2 > a + g / 2 and w["src"] != "bridge"]
        if L and R:
            lsz = sorted(w["size"] or 10 for w in L)[len(L) // 2]; rsz = sorted(w["size"] or 10 for w in R)[len(R) // 2]
            lb = sum(1 for w in L if w["bold"]) > len(L) / 2; rb = sum(1 for w in R if w["bold"]) > len(R) / 2
            short_ok = abs(lsz - rsz) > 1.5 or lb != rb
            # not when the words on both sides of the gap belong to one continuous line (same baseline, the
            # right part starting with a lower-case word or the left part ending mid-sentence)
            lw = max(L, key=lambda w: w["x1"]); rw = min(R, key=lambda w: w["x0"])
            if abs(yc(lw) - yc(rw)) <= 3 and (rw["text"][:1].islower() or not re.search(r"[.!?:]$", lw["text"])) \
                    and abs((lw["size"] or 10) - (rw["size"] or 10)) < 1.5 and lw["bold"] == rw["bold"] \
                    and not re.fullmatch(r"\d{1,2}", lw["text"]):
                short_ok = False
    def row_grid(L, R):
        """numbered rows whose cells are spread across the zone width (word grids such as "1 popular  decision
        opinion agreement"): the left part starts with item numbers, the right part does not, and the lines
        pair up 1:1 by y -> the gutter is a column gap inside rows, not a layout gutter."""
        Ll = group_lines([w for w in L if w["src"] != "bridge"]); Rl = group_lines([w for w in R if w["src"] != "bridge"])
        if len(Ll) < 3 or len(Ll) != len(Rl):
            return False
        starts = sum(1 for ln in Ll if re.fullmatch(r"\d{1,2}\.?", ln["words"][0]["text"]))
        rstarts = sum(1 for ln in Rl if re.fullmatch(r"\d{1,2}\.?|[a-h]\.?|[A-H]", ln["words"][0]["text"]))
        if starts < 0.7 * len(Ll) or rstarts > 0.3 * len(Rl):
            return False
        paired = sum(1 for p in Ll if any(abs(p["yc"] - q["yc"]) <= 3 for q in Rl))
        nw = sorted(len(ln["words"]) for ln in Rl)
        return paired >= 0.8 * len(Ll) and nw[len(nw) // 2] <= 5
    if best_v and (zone_h >= 2.2 * med or short_ok) and depth < 6:
        g, a, b = best_v
        left = [w for w in words if (w["x0"] + w["x1"]) / 2 <= a + g / 2]
        right = [w for w in words if (w["x0"] + w["x1"]) / 2 > a + g / 2]
        if left and right and row_grid(left, right):
            left = right = None
        if left and right:
            # a vertical gutter that is narrow relative to the text is only trusted if both sides have >= 2 lines
            return xy_cut(left, W, H, depth + 1, seps) + xy_cut(right, W, H, depth + 1, seps)
    if gaps:
        g, a, b = max(gaps)
        top = [w for w in words if yc(w) <= (a + b) / 2]
        bot = [w for w in words if yc(w) > (a + b) / 2]
        if top and bot:
            return xy_cut(top, W, H, depth + 1, seps) + xy_cut(bot, W, H, depth + 1, seps)
    return [words]


def separators(ana, words=()):
    seps = []
    for p in ana.get("photos", []):
        if p.get("panel") and (p["y1"] - p["y0"]) >= 40:
            seps.append((p["x0"] - 2, p["y0"], p["y1"]))
            seps.append((p["x1"] + 2, p["y0"], p["y1"]))
    tables = ana.get("tables", [])
    for v in ana.get("vrules", []):
        if v["y1"] - v["y0"] < 60:
            continue
        # column rules of a detected table are handled by the table logic, not as zone separators
        if any(t["x0"] - 6 <= v["x"] <= t["x1"] + 6 and v["y0"] >= t["y0"] - 8 and v["y1"] <= t["y1"] + 8 for t in tables):
            continue
        # stems of large reversed-out letters (white-on-black banners) are not separators
        big = [w for w in words if (w["size"] or 10) >= 13 and min(w["y1"], v["y1"]) - max(w["y0"], v["y0"]) > 0.5 * (w["y1"] - w["y0"])]
        if big and (v["y1"] - v["y0"]) <= 40 and any(w["x0"] - 8 <= v["x"] <= w["x1"] + 8 for w in big):
            continue
        seps.append((v["x"], v["y0"], v["y1"]))
    return seps


def bridge_gutters(words, W, ana=None):
    """word gaps that are NOT column gutters (inter-word spaces in justified text, 'A ... B' pairs) get
    zero-width bridge tokens so the XY cut does not split them.  Returns words plus bridges."""
    lines = group_lines(words)
    bridges = []
    # x positions where many lines start: a column edge (never bridge into it)
    starts = collections.Counter(round(ln["x0"] / 3) * 3 for ln in lines if len(ln["words"]) >= 2)
    col_edges = {x for x, c in starts.items() if c >= 4}
    # separators: vertical rules and tinted panel edges
    seps = []
    if ana:
        seps += [(v["x"], v["y0"], v["y1"]) for v in ana.get("vrules", []) if v["y1"] - v["y0"] >= 30]
        seps += [(p["x0"], p["y0"], p["y1"]) for p in ana.get("photos", []) if p.get("panel")]
        seps += [(p["x1"], p["y0"], p["y1"]) for p in ana.get("photos", []) if p.get("panel")]
    for ln in lines:
        ws = ln["words"]
        for a, b in zip(ws, ws[1:]):
            gap = b["x0"] - a["x1"]
            if gap < 11:
                continue
            if any(a["x1"] - 2 <= sx <= b["x0"] + 2 and sy0 - 4 <= ln["yc"] <= sy1 + 4 for sx, sy0, sy1 in seps):
                continue
            if any(abs(b["x0"] - x) <= 3 for x in col_edges) and gap >= 14:
                continue
            # a gap inside running text (both neighbours are lower-case words, or a word followed by punctuation)
            if gap <= 30 and alnum(a["text"]) and alnum(b["text"]) and not (b["text"][:1].isupper() and gap > 20) \
                    and not re.fullmatch(r"[A-H]|\d{1,2}\.?|[a-h]\.?", b["text"]) and abs((a["size"] or 10) - (b["size"] or 10)) < 2:
                bridges.append(dict(x0=a["x1"], y0=a["y0"], x1=b["x0"], y1=a["y1"], text="", size=a["size"], bold=False, italic=False, conf=99, src="bridge", flag=False, h=a["h"]))
            # blank followed by punctuation / text on the same line
            if gap <= 20 and (a["text"] == BLANK or b["text"] == BLANK):
                bridges.append(dict(x0=a["x1"], y0=a["y0"], x1=b["x0"], y1=a["y1"], text="", size=a["size"], bold=False, italic=False, conf=99, src="bridge", flag=False, h=a["h"]))
    return words + bridges


# ------------------------------------------------------------------------------------------------------------
def split_line_gaps(lines):
    """a line whose words are separated by a gap > 8 em, or before an item marker, is split into pieces
    (side-by-side items / two-column option lists)."""
    out = []
    for ln in lines:
        ws = ln["words"]
        pieces = [[ws[0]]]
        for a, b in zip(ws, ws[1:]):
            gap = b["x0"] - a["x1"]
            em = (a["size"] or 10)
            nxt_after_b = None
            k = ws.index(b)
            if k + 1 < len(ws):
                nxt_after_b = ws[k + 1]
            marker = is_item_marker(b, nxt_after_b) and gap >= 1.2 * em and not is_blank(a) and not (a["text"].endswith((",", "and", "or")) and re.fullmatch(r"\d{1,2}", b["text"]))
            if gap > 8 * em or (marker and gap > 2.0 * em):
                pieces.append([b])
            else:
                pieces[-1].append(b)
        for p in pieces:
            out.append(dict(ln, words=p, x0=p[0]["x0"], x1=p[-1]["x1"]))
    return out


def mark_footnotes(lines, H):
    """footnote lines (small type near the page foot starting with a digit) -> superscript digit marker"""
    for ln in lines:
        if ln["y0"] >= H - 80 and ln["size"] <= 8.5 and len(ln["words"]) >= 2 and re.fullmatch(r"\d", ln["words"][0]["text"]):
            n = int(ln["words"][0]["text"])
            ln["words"][0] = dict(ln["words"][0], text="⁰¹²³⁴⁵⁶⁷⁸⁹"[n], footnote=True)
            ln["footnote"] = True
    return lines


def make_blocks(lines):
    """merge consecutive lines into blocks (paragraphs / items)."""
    blocks = []
    for ln in lines:
        first = ln["words"][0]
        nxt = ln["words"][1] if len(ln["words"]) > 1 else None
        starts_item = is_item_marker(first, nxt) or first.get("disc") or first.get("margin_no") or first.get("footnote")
        if blocks:
            prev = blocks[-1]
            pl = prev["lines"][-1]
            gap = ln["y0"] - pl["y1"]
            size_jump = abs(ln["size"] - prev["size"]) > 1.6
            bold_change = ln["bold"] != pl["bold"] and not (first["text"][:1].islower() and not ln["bold"])
            indent = ln["x0"] - prev["x0"]
            same_col = abs(ln["x0"] - prev["x0"]) < 60 or (ln["x0"] > prev["x0"] and ln["x0"] - prev["x0"] < 60)
            pmark = ln.get("pmark")
            headword = prev.get("headword")
            # dictionary-style entry: "word /pronunciation/ ..." starts a new block
            if nxt is not None and re.match(r"^/", nxt["text"]) and re.match(r"^[A-Za-z][A-Za-z'’\-]*$", first["text"]):
                starts_item = True
            # hanging indent: the line returns to the block's left edge after indented run-over lines
            if len(prev["lines"]) >= 1 and ln["x0"] < pl["x0"] - 8 and ln["x0"] <= prev["x0"] + 2 and prev.get("hanging_ok", True):
                starts_item = True
            join = (gap < 0.9 * max(ln["size"], pl["size"]) and gap > -4 and not starts_item and not size_jump and
                    not bold_change and same_col and not pmark and not headword and
                    abs(ln["x0"] - prev["x0"]) < 60 and not (prev.get("item") and ln["x0"] < prev["x0"] - 4))
            # word-list grids ("____ director ____ create ..."): keep one printed line per output line
            def gridlike(l):
                nb = sum(1 for w in l["words"] if w["text"] in (BLANK, "☐"))
                return nb >= 2 and nb >= 0.4 * len(l["words"])
            if join and gridlike(ln) and gridlike(pl):
                join = False
            # leader lines ("label ...... value"): one printed line per output line
            if join and any(w.get("leader") for w in ln["words"]) and any(w.get("leader") for w in pl["words"]):
                join = False
            if prev.get("kind") == "heading":
                join = join and ln["size"] >= 14
                # run-over line of a chapter title (indented under the title, same size, same weight)
                if not join and ln["size"] >= 14 and ln["bold"] and pl["bold"] and abs(ln["size"] - pl["size"]) <= 1 \
                        and -4 < gap < 0.9 * ln["size"] and 0 <= ln["x0"] - prev["x0"] <= 120 and not starts_item and not pmark:
                    join = True
            # a continuation line of a hanging-indent item sits to the right of the marker
            if join:
                prev["lines"].append(ln)
                prev["x0"] = min(prev["x0"], ln["x0"]); prev["x1"] = max(prev["x1"], ln["x1"]); prev["y1"] = ln["y1"]
                continue
        b = dict(lines=[ln], x0=ln["x0"], x1=ln["x1"], y0=ln["y0"], y1=ln["y1"], size=ln["size"], bold=ln["bold"], item=bool(starts_item), kind="para")
        if ln["size"] >= 20 or (ln["size"] >= 15 and ln["bold"] and len(line_text(ln)) < 80):
            b["kind"] = "heading"
        blocks.append(b)
    return blocks


def dehyphenate(texts):
    """join hyphenated line breaks when the joined form is a dictionary word"""
    out = []
    i = 0
    while i < len(texts):
        t = texts[i]
        if i + 1 < len(texts) and re.search(r"[a-z]-$", t):
            m = re.search(r"([A-Za-z]+)-$", t)
            nxt = texts[i + 1]
            m2 = re.match(r"^([a-z]+)([^\sA-Za-z]*)", nxt)
            if m and m2:
                a, b = m.group(1).lower(), m2.group(1).lower()
                W_ = words()
                # a genuine hyphenated compound broken at the hyphen ("well-|known", "student-|friendly"): both
                # halves are words of >= 3 letters and the compound is not itself a plain dictionary word
                compound = a in W_ and b in W_ and len(a) >= 3 and len(b) >= 3 and (a + b) not in W_
                if compound:
                    t = t + "\u2060"        # keep the hyphen, join without a space
                elif is_word(a + b):
                    t = t[:-1] + "\u00ad"  # soft hyphen marker, removed by joiner
        out.append(t)
        i += 1
    return out


def block_text(b):
    lines = [line_text(ln) for ln in b["lines"]]
    lines = dehyphenate(lines)
    s = ""
    for t in lines:
        if s.endswith("\u00ad"):
            s = s[:-1] + t
        elif s.endswith("\u2060"):
            s = s[:-1] + t
        elif s:
            s += " " + t
        else:
            s = t
    return s


# ------------------------------------------------------------------------------------------------------------
def table_blocks(words, ana):
    """words inside ruled tables -> table blocks; returns (table_blocks, remaining_words)"""
    out = []
    rest = list(words)
    for t in ana["tables"]:
        def in_t(w):
            if w["src"] == "bridge" or not (t["x0"] - 3 <= (w["x0"] + w["x1"]) / 2 <= t["x1"] + 3):
                return False
            if t["y0"] - 3 <= yc(w) <= t["y1"] + 3:
                return True
            # a tall box (bold digit read with a stretched box) whose top lies inside the table
            return t["y0"] <= w["y0"] and w["y0"] <= t["y1"] - 6 and (w["y1"] - w["y0"]) > 12 and len(w["text"]) <= 2 and w["y1"] <= t["y1"] + 3
        inside = [w for w in rest if in_t(w)]
        def followed(w):
            return any(v is not w and alnum(v["text"]) and 0 <= v["x0"] - w["x1"] <= 8 and overlap_y(v, w) > 0.4 * (v["y1"] - v["y0"]) for v in inside)
        inside = [w for w in inside if not (w["src"] == "tess" and w["conf"] < 70 and len(alnum(w["text"])) <= 1 and not re.fullmatch(r"[A-Za-z]", w["text"])
                                            and not (w["text"].isdigit() and (w["conf"] >= 50 or followed(w))))]
        for w in inside:
            if w["text"] == "o" and (w["bold"] or w["src"] == "tess") and w["y0"] < t["rows"][1] and re.fullmatch(r"[a-z]", w["text"]):
                w["text"] = "O"          # header letter of a T/F-style table read as lower case
        if not inside:
            continue
        rest = [w for w in rest if w not in inside]
        cols = t["cols"]; rows = t["rows"]
        grid = {}
        for w in inside:
            xc = (w["x0"] + w["x1"]) / 2
            ci = max(0, min(len(cols) - 2, next((k for k in range(len(cols) - 1) if xc < cols[k + 1]), len(cols) - 2)))
            ri = max(0, min(len(rows) - 2, next((k for k in range(len(rows) - 1) if yc(w) < rows[k + 1]), len(rows) - 2)))
            grid.setdefault((ri, ci), []).append(w)
        cells = []
        for ri in range(len(rows) - 1):
            row = []
            for ci in range(len(cols) - 1):
                ws = grid.get((ri, ci), [])
                if ws:
                    lns = group_lines(ws)
                    txt = " / ".join(line_text(l) for l in lns)
                else:
                    txt = ""
                row.append(txt)
            cells.append(row)
        # header rows above the first rule (words between y0-14 and y0) stay outside
        out.append(dict(kind="table", cells=cells, ncols=len(cols) - 1, x0=t["x0"], x1=t["x1"], y0=t["y0"], y1=t["y1"], size=10, bold=False, lines=[]))
    return out, rest


# ------------------------------------------------------------------------------------------------------------
def assemble(pn):
    words, ana, W, H = collect(pn)
    head, foot, body = header_footer(words, W, H)
    body = drop_junk(body, ana, W, H)
    body = margin_numbers(body, W)
    tbl, body = table_blocks(body, ana)
    # blanks that are the answer line of an item on the same line: keep; standalone blanks stay as lines
    # margin markers (paragraph discs, line numbers) are attached to the nearest text line afterwards
    markers = [w for w in body if (w.get("disc") and w.get("margin")) or w.get("margin_no")]
    body = [w for w in body if w not in markers]
    body_b = bridge_gutters(body, W, ana)
    # a ruled table spanning several columns blocks the vertical gutters for the XY cut (it belongs to the
    # reading flow at its position): represent it by bridge tokens along its top and bottom edge
    for t in tbl:
        if t["y1"] - t["y0"] < 20:
            continue
        for yy in (t["y0"] + 8, (t["y0"] + t["y1"]) / 2, t["y1"] - 8):
            body_b.append(dict(x0=t["x0"] + 2, y0=yy - 1, x1=t["x1"] - 2, y1=yy + 1, text="", size=10.0, bold=False, italic=False,
                               conf=99, src="bridge", flag=False, h=2, tbl=True))
    groups = xy_cut(body_b, W, H, 0, separators(ana, body))
    glines = []
    for g in groups:
        g = [w for w in g if w["src"] != "bridge"]
        if not g:
            continue
        glines.append(group_lines(g))
    all_lines = [ln for ls in glines for ln in ls]
    for m in markers:
        cands = []
        for ln in all_lines:
            if not any(alnum(w["text"]) for w in ln["words"]):
                continue
            right = ln["x0"] >= m["x1"] - 3 and ln["x0"] - m["x1"] <= 45
            left = ln["x1"] <= m["x0"] + 3 and m["x0"] - ln["x1"] <= 45
            dy = abs(ln["yc"] - yc(m))
            if (right or left) and dy <= 9:
                cands.append((dy, ln, right))
        if cands:
            dy, ln, right = min(cands, key=lambda c: c[0])
            if right:
                ln["words"].insert(0, m); ln["x0"] = m["x0"]
            else:
                ln["words"].append(m); ln["x1"] = m["x1"]
            ln["pmark"] = True
        else:
            # no text line beside the marker: give it its own line in the group that contains its y
            placed = False
            for ls in glines:
                if ls and ls[0]["y0"] - 6 <= yc(m) <= ls[-1]["y1"] + 6:
                    ls.append(dict(words=[m], y0=m["y0"], y1=m["y1"], yc=yc(m), x0=m["x0"], x1=m["x1"], size=m["size"], bold=False, pmark=True))
                    ls.sort(key=lambda l: (l["yc"], l["x0"]))
                    placed = True; break
            if not placed:
                glines.append([dict(words=[m], y0=m["y0"], y1=m["y1"], yc=yc(m), x0=m["x0"], x1=m["x1"], size=m["size"], bold=False, pmark=True)])
    blocks = []
    for lines in glines:
        lines = split_line_gaps(lines)
        lines = mark_footnotes(lines, H)
        for ln in lines:
            ln["pmark"] = bool(ln.get("pmark") or ln["words"][0].get("disc") or ln["words"][0].get("margin_no"))
        bl = make_blocks(lines)
        blocks.extend(bl)
    # insert tables at their vertical position
    for t in tbl:
        blocks.append(t)
    # order: by reading order already; tables inserted by y then x
    def key(b):
        return (b["y0"], b["x0"])
    # blocks from xy_cut are in reading order; we only need to position tables: insert each table before the first
    # block that starts below it in the same column region
    ordered = [b for b in blocks if b["kind"] != "table"]
    for t in sorted(tbl, key=key):
        idx = len(ordered)
        for i, b in enumerate(ordered):
            if b["y0"] > t["y0"] + 4 and (b["x1"] > t["x0"] and b["x0"] < t["x1"]):
                idx = i; break
        ordered.insert(idx, t)
    blocks = ordered
    head_b = dict(kind="header", lines=group_lines(head), x0=0, y0=0, x1=W, y1=30, size=8, bold=False) if head else None
    foot_b = dict(kind="footer", lines=group_lines(foot), x0=0, y0=H - 40, x1=W, y1=H, size=8, bold=False) if foot else None
    return dict(page=pn, W=W, H=H, blocks=blocks, header=head_b, footer=foot_b)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        r = assemble(int(a))
        for b in r["blocks"]:
            if b["kind"] == "table":
                print("[TABLE]")
                for row in b["cells"]:
                    print("  | " + " | ".join(row))
                print("[/TABLE]")
            else:
                print(f'{b["kind"]:8s} x{b["x0"]:4.0f} y{b["y0"]:4.0f} sz{b["size"]:5.1f} {"B" if b["bold"] else " "} {block_text(b)}')
        if r["footer"]:
            print("FOOT", " ".join(line_text(l) for l in r["footer"]["lines"]))
