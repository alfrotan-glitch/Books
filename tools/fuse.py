"""Stage 2: word-level fusion of the two witnesses (tesseract symbols + embedded text layer).
fuse_page(pn) -> list of word dicts: x0,y0,x1,y1,text,size,bold,italic,conf,src,flag,h
src: tess | emb | emb-only | glyph
"""
import re, sys, os, json, gzip
from quality import is_word

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(ROOT, "data", "pages")
PUNCT = ".,;:!?()[]{}\"'“”‘’…—–-/"


def load(pn):
    with gzip.open(os.path.join(PAGES, f"p{pn:03d}.json.gz"), "rt") as f:
        return json.load(f)


def alnum(s):
    return re.sub(r"[^0-9A-Za-z]", "", s)


def letters(s):
    return re.sub(r"[^A-Za-z]", "", s)


def clean(tok):
    """token consists of letters/digits plus ordinary punctuation only"""
    return bool(tok) and not re.search(r"[^0-9A-Za-z.,;:!?()\[\]\"'“”‘’…—–\-/&%$@+=*#°²³¹⁰⁴⁵⁶⁷⁸⁹\s]", tok)


def dict_ok(tok):
    """token (with punctuation) is a dictionary word / number / short token"""
    core = tok.strip(PUNCT + "“”‘’")
    if not core:
        return False
    if re.fullmatch(r"\d+([.,]\d+)*%?", core):
        return True
    if re.fullmatch(r"[A-Za-z]", core):
        return True
    if "/" in core:
        return all(dict_ok(p) for p in core.split("/") if p)
    if re.fullmatch(r"\d+(st|nd|rd|th|s)", core):
        return True
    if is_word(core.lower()):
        return True
    # proper nouns: capitalised, plausible letter pattern, <= 8 chars (guarded)
    if re.fullmatch(r"[A-Z][a-z]{2,7}", core) and re.search(r"[aeiouy]", core.lower()):
        return True
    return False


def inter(a, b):
    xo = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
    yo = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
    return xo * yo if xo > 0 and yo > 0 else 0.0


def area(a):
    return max(0.0, a["x1"] - a["x0"]) * max(0.0, a["y1"] - a["y0"])


def h_med(t):
    hs = sorted(c[5] - c[3] for c in t["chars"] if c[0].isalnum())
    return hs[len(hs) // 2] if hs else (t["y1"] - t["y0"])


def prep_tess(rec):
    out = []
    for w in rec["tess"]:
        t = w["text"]
        if not t.strip():
            continue
        t2 = re.sub(r"[_]{2,}", "", t)
        t2 = re.sub(r"^[—_\-]{3,}$", "", t2)
        if not t2.strip():
            continue
        chars = [c for c in w["chars"] if c[0].strip()]
        if not chars:
            continue
        # a blank rule glued to the word ("—__create"): tesseract emits dash/underscore glyphs over the rule
        if any(c[0] == "_" for c in chars) and re.search(r"[A-Za-z0-9]", t2):
            chars = [c for c in chars if c[0] != "_"]
            while chars and chars[0][0] in "—–-_" :
                chars = chars[1:]
            while chars and chars[-1][0] in "—–_":
                chars = chars[:-1]
            if not chars:
                continue
            t2 = "".join(c[0] for c in chars)
        # a symbol box stretched over a printed rule: clip it to a normal width at its far end
        ws_ = sorted(c[4] - c[2] for c in chars)
        medw = ws_[len(ws_) // 2] if ws_ else 5
        if len(ws_) <= 3:
            medw = min(medw, max(ws_[0], 3))
        hgt = max(c[5] for c in chars) - min(c[3] for c in chars)
        fixed = []
        for k, c in enumerate(chars):
            cw = c[4] - c[2]
            if (cw > max(12, 3.5 * medw) or (cw > 2.2 * hgt and cw > 12)) and c[0].isalnum():
                c = list(c)
                gw = min(max(medw, 3), 0.75 * hgt)
                if k > 0 and c[2] < fixed[-1][4] - 1 and k + 1 < len(chars):
                    # box starts under the previous letters: the glyph sits between its neighbours
                    c[2] = fixed[-1][4]; c[4] = min(c[2] + gw, chars[k + 1][2])
                    if c[4] <= c[2]:
                        c[4] = c[2] + gw
                elif k + 1 < len(chars) and chars[k + 1][2] - c[4] < 3:
                    c[2] = c[4] - gw
                else:
                    c[4] = c[2] + gw
            fixed.append(c)
        chars = fixed
        # the instruction verb "Circle" printed inside a hand-drawn oval (box ~19 pt tall, garbled text)
        hh = max(c[5] for c in chars) - min(c[3] for c in chars)
        if hh >= 15 and re.match(r"^[Cc]irc", t2) and len(t2) <= 9 and w["x0"] > 100:
            x0 = min(c[2] for c in chars); x1 = x0 + 28
            y0 = min(c[3] for c in chars) + 5; y1 = max(c[5] for c in chars) - 5
            out.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, text="Circle", conf=99.0, chars=[("C", 99.0, x0, y0, x1, y1)], ln=w["ln"], blk=w["blk"], pt=w.get("pt"), oval=True))
            continue
        # symbols separated by a large horizontal gap (a rule / blank glued to the word): keep the larger run
        runs = [[chars[0]]]
        for c in chars[1:]:
            if c[2] - runs[-1][-1][4] > 12:
                runs.append([c])
            else:
                runs[-1].append(c)
        if len(runs) > 1:
            runs.sort(key=lambda r: (len([c for c in r if c[0].isalnum()]), len(r)), reverse=True)
            chars = runs[0]
            t2 = "".join(c[0] for c in chars)
        x0 = min(c[2] for c in chars); y0 = min(c[3] for c in chars); x1 = max(c[4] for c in chars); y1 = max(c[5] for c in chars)
        h = y1 - y0; wd = x1 - x0
        if h > 60 or wd > 320:
            continue  # illustration blobs
        cmin = min(c[1] for c in chars)
        conf = w["conf"]
        if clean(t2) and len(alnum(t2)) >= 3 and dict_ok(t2) and re.search(r"[A-Za-z]", t2) and not (h >= 20 and w["conf"] < 60) \
                and not (len(alnum(t2)) <= 3 and w["conf"] < 40) and not (w["conf"] < 10 and not is_word(alnum(t2).lower())):
            conf = max(conf, min(cmin, 99.0))
        out_raw = w["conf"]
        out.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, text=t2.strip(), conf=conf, chars=chars, ln=w["ln"], blk=w["blk"], pt=w.get("pt"), raw=out_raw))
    # tesseract sometimes reads the same printed word twice (a second "line" made of the tail of a word, e.g.
    # "Preparing" + "paring" on the same baseline, boxes overlapping): drop the duplicate that is a suffix of
    # a longer word covering the same area
    dup = set()
    for i, a in enumerate(out):
        for j, b in enumerate(out):
            if i == j or j in dup:
                continue
            ta = alnum(a["text"]); tb = alnum(b["text"])
            if len(tb) >= 3 and len(ta) > len(tb) and ta.endswith(tb) and b["x0"] >= a["x0"] - 1 and b["x1"] <= a["x1"] + 6 \
                    and min(a["y1"], b["y1"]) - max(a["y0"], b["y0"]) > 0.6 * (b["y1"] - b["y0"]):
                dup.add(j)
    out = [o for k, o in enumerate(out) if k not in dup]
    return out


def prep_emb(rec, leaders=None):
    out = []
    if leaders is None:
        leaders = []
    for w in rec["embedded"]:
        if w["size"] < 4 or (w["x1"] - w["x0"]) < 1.0 or (w["y1"] - w["y0"]) < 1.0:
            continue
        t = w["text"].strip()
        if not t:
            continue
        if re.fullmatch(r"\.{6,}", t) and (w["x1"] - w["x0"]) >= 30 or re.fullmatch(r"\.{4,}", t) and (w["x1"] - w["x0"]) >= 15:
            leaders.append(dict(w, text="…"))
            continue   # dot leaders: re-added as a single glyph after fusion
        if len(re.sub(r"[_\-—–.:;,·]", "", t)) < 0.5 * len(t) and len(t) >= 3:
            continue   # rule / leader-dot junk
        m = re.match(r"^[@\x91%]+([A-Za-z].*)$", t)
        if m and (w["x1"] - w["x0"]) > 30:
            t = m.group(1)
            w = dict(w, x0=w["x0"] + 26)
        # the instruction verb "Circle" printed inside a hand-drawn oval comes through as a wide "@" token
        if re.fullmatch(r"[@\x91%]+", t) and (w["x1"] - w["x0"]) >= 25 and w["size"] <= 12:
            out.append(dict(w, text="Circle", oval=True))
            continue
        # the embedded layer marks specks / dots as "·" or a hair-line "•"; a real bullet is >= 3 pt wide
        if t in ("·", "•", "●"):
            if (w["x1"] - w["x0"]) < 3:
                continue
            t = "•"
        out.append(dict(w, text=t))
    return out


BULLET_GLYPHS = {"•", "●", "·", "*", "¢", "e", "c", "o", "«", "©"}


def fuse_page(pn):
    rec = load(pn)
    tess = prep_tess(rec)
    leaders = []
    emb = prep_emb(rec, leaders)
    # --- one-to-one assignment emb -> tess
    pairs = []
    for ti, t in enumerate(tess):
        tw = max(0.5, t["x1"] - t["x0"]); th = t["y1"] - t["y0"]
        for ei, e in enumerate(emb):
            yov = min(t["y1"], e["y1"]) - max(t["y0"], e["y0"])
            if yov <= 0 or yov < 0.5 * min(th, e["y1"] - e["y0"]):
                continue
            xov = min(t["x1"], e["x1"]) - max(t["x0"], e["x0"])
            if xov <= 0:
                continue
            ew = max(0.5, e["x1"] - e["x0"])
            fe = xov / ew; ft = xov / tw
            if fe >= 0.5 or (ft >= 0.5 and fe >= 0.15):
                pairs.append((xov * yov, ti, ei, fe, ft))
    pairs.sort(reverse=True)
    e_of_t = {}
    t_of_e = {}
    for sc, ti, ei, fe, ft in pairs:
        if ei in t_of_e:
            continue
        if ti in e_of_t and fe < 0.5:
            continue
        t_of_e[ei] = ti
        e_of_t.setdefault(ti, []).append(ei)

    words = []
    lines_first = {}
    for i, t in enumerate(tess):
        key = (t["blk"], t["ln"])
        if not alnum(t["text"]):
            continue                       # glyphs / specks do not count as the first word of a line
        if key not in lines_first or t["x0"] < tess[lines_first[key]]["x0"]:
            lines_first[key] = i

    for ti, t in enumerate(tess):
        text = t["text"]; conf = t["conf"]
        es = sorted([emb[ei] for ei in e_of_t.get(ti, [])], key=lambda e: e["x0"])
        etext = " ".join(e["text"] for e in es) if es else None
        ea = alnum(etext) if etext else ""
        ta = alnum(text)
        h = t["y1"] - t["y0"]
        size = es[0]["size"] if es else None
        if size is None and t.get("pt") and 5 <= t["pt"] <= 60 and h > 0 and t["pt"] <= 2.2 * h:
            size = t["pt"]              # tesseract point size, only when consistent with the box height
        bold = any(e["bold"] for e in es) if es else False
        italic = all(e["italic"] for e in es) if es else False
        out = dict(x0=t["x0"], y0=t["y0"], x1=t["x1"], y1=t["y1"], size=size, bold=bold, italic=italic, conf=conf, src="tess", flag=False, h=h, lx0=t["x0"], raw=t.get("raw", conf), ti=ti)
        first_on_line = lines_first.get((t["blk"], t["ln"])) == ti
        if t.get("oval"):
            out.update(text="Circle", src="glyph"); words.append(out); continue

        # ---- special glyphs -----------------------------------------------------------------------
        # bullets: tesseract reads them as tiny 'e', 'c', '®', '©', '*'... ; emb has '•'
        if es and len(es) == 1 and es[0]["text"] in ("•", "·", "●") and (len(text) <= 2 or h <= 6):
            out.update(text="•", src="glyph"); words.append(out); continue
        if not es and text in ("•", "●", "·") and h <= 8:
            out.update(text="•", src="glyph"); words.append(out); continue
        if es and len(es) == 1 and es[0]["text"] in ("•", "·") and re.fullmatch(r"[^\w]{1,2}|[ecoa]", text) and h <= 7:
            out.update(text="•", src="glyph"); words.append(out); continue
        if not es and re.fullmatch(r"[@©®]", text) and h <= 7:
            out.update(text="•", src="glyph"); words.append(out); continue
        # tiny non-alnum tess glyph + emb bullet
        if es and len(es) == 1 and es[0]["text"] in ("•", "·") and not alnum(text) and (t["x1"] - t["x0"]) <= 6 and h <= 6:
            out.update(text="•", src="glyph"); words.append(out); continue
        # superscript footnote reference
        if len(es) == 2 and re.fullmatch(r"\d", es[1]["text"]) and es[1]["size"] <= 0.8 * es[0]["size"] and es[1]["x0"] >= es[0]["x1"] - 2 \
                and letters(es[0]["text"]).lower() == letters(text).lower() and re.search(r"[?'’!1l7\)]$|\d$", text):
            sup = "⁰¹²³⁴⁵⁶⁷⁸⁹"[int(es[1]["text"])]
            out.update(text=es[0]["text"] + sup, src="emb"); words.append(out); continue
        # check mark glyph "(✓)"
        if re.fullmatch(r"\(\s*[vV/✓v'’\"]+\s*\)", text) or (es and re.fullmatch(r"[\{\(\[][I|l1'\)\}\]]{2,5}", etext) and re.fullmatch(r"\(.{1,2}\)", text)):
            prev_t = [w for w in words if w["src"] != "blank" and 0 <= t["x0"] - w["x1"] <= 8 and abs(w["y0"] - t["y0"]) < 6]
            after_check = any(w["text"].lower().rstrip(",.") in ("check", "tick") for w in prev_t)
            emb_junk = bool(es) and re.fullmatch(r"[\{\(\[][I|l1'\)\}\]\"./tiqvVw ]{2,5}", etext) and not re.fullmatch(r"\([a-zA-Z]\)", etext)
            if after_check or emb_junk:
                out.update(text="(✓)", src="glyph"); words.append(out); continue
        # spiral-binding ring artwork in the left margin read as a capital 'C'
        if not es and re.fullmatch(r"[CG\(]", text) and h >= 11 and t["x0"] < 70 and conf < 90:
            continue
        # an equals sign confirmed by the embedded layer (measurement tables)
        eq_sign = text == "=" and es and len(es) == 1 and es[0]["text"] == "=" and conf >= 80
        if h <= 2.5 and not re.fullmatch(r"[-–—_.,]", text) and not eq_sign:
            continue
        if h <= 2.5 and not es:
            continue
        if h <= 2.5 and es and not any(dict_ok(e["text"]) and len(alnum(e["text"])) >= 2 for e in es) \
                and not (len(es) == 1 and es[0]["text"] == text and text in ".,") and not eq_sign:
            continue
        # item letter / number with a glued speck
        if es and len(es) == 1 and re.fullmatch(r"[a-h]|[A-H]|\d{1,2}", es[0]["text"]) and conf < 85 and text != es[0]["text"] \
                and len(text) <= 3 and (alnum(text).startswith(alnum(es[0]["text"])) or alnum(es[0]["text"]) in alnum(text) or not alnum(text)):
            out.update(text=es[0]["text"], src="emb"); words.append(out); continue
        # circled numeral seen as tiny '©'/'@' -> dropped here, the disc detector (assemble) re-inserts it
        if re.fullmatch(r"[@©®●]", text) and 8 <= h <= 14 and (not es or len(alnum(es[0]["text"])) <= 1):
            continue
        if h >= 15 and re.match(r"^[Cc]irc", text) and (t["x0"] > 100 or not es):
            out.update(text="Circle", src="glyph"); out["size"] = 10.0
            out["y0"] = t["y0"] + 5; out["y1"] = t["y1"] - 5; out["h"] = out["y1"] - out["y0"]
            for e in es:
                et = e["text"].lstrip("@\x91")
                if et and dict_ok(et) and e["x0"] > t["x0"] + 20:
                    words.append(dict(x0=e["x0"], y0=out["y0"], x1=e["x1"], y1=out["y1"], size=e["size"], bold=e["bold"], italic=e["italic"],
                                      conf=60.0, src="emb", flag=False, text=et, h=out["h"], lx0=e["x0"], sup=True))
            words.append(out); continue

        # ---- text decision -------------------------------------------------------------------------
        tclean = clean(text); tdict = dict_ok(text)
        if len(es) == 1 and (es[0]["x1"] - es[0]["x0"]) > 1.4 * (t["x1"] - t["x0"]) and re.search(r"[-—/]", etext):
            parts = [p for p in re.split(r"[-—/]", etext) if alnum(p)]
            if parts and ta:
                import difflib
                best = max(parts, key=lambda p: difflib.SequenceMatcher(None, alnum(p), ta).ratio())
                if difflib.SequenceMatcher(None, alnum(best), ta).ratio() >= 0.6:
                    etext = best; ea = alnum(etext)
        m = re.fullmatch(r"([A-Za-z]{2,})[’'‘]([A-Za-z]{3,})([.,;:!?]?)", text)
        if m and conf < 60 and m.group(2) not in ("re", "ve", "ll") and dict_ok(m.group(1)) and dict_ok(m.group(2)) and not dict_ok(text):
            text = m.group(1) + " " + m.group(2) + m.group(3); tclean = True; tdict = True; conf = max(conf, 60)
        # trailing digit / letter read as punctuation ('Chapter?' for emb 'Chapter' + '2')
        if len(es) >= 2 and ta and ta == alnum("".join(e["text"] for e in es[:-1])) and re.fullmatch(r"\d{1,2}|[a-hA-H]", es[-1]["text"]) \
                and re.search(r"[^\w\s]$", text) and t["chars"][-1][1] < 95:
            for e in es:
                words.append(dict(x0=e["x0"], y0=t["y0"], x1=e["x1"], y1=t["y1"], size=e["size"], bold=e["bold"], italic=e["italic"],
                                  conf=conf, src="emb", flag=False, text=e["text"], h=h, lx0=e["x0"], sup=True))
            continue
        two_short = (es and len(es) == 2 and all(dict_ok(e["text"]) and len(alnum(e["text"])) >= 1 for e in es) and
                     alnum("".join(e["text"] for e in es)) == ta and es[1]["x0"] - es[0]["x1"] >= 1.5 and
                     all(len(alnum(e["text"])) <= 4 for e in es) and len(ta) <= 6)
        if es and len(es) >= 2 and (not tdict or two_short or (not is_word(text.lower().strip(PUNCT)) and all(dict_ok(e["text"]) for e in es) and alnum("".join(e["text"] for e in es)) == ta)):
            cat = "".join(e["text"] for e in es)
            if re.search(r"[-—]:", cat) and "—" in text and tclean and alnum(cat) == ta:
                pass                      # embedded layer garbles em-dash compounds as "-:"; keep tesseract
            elif not two_short and (clean(cat) and dict_ok(cat) and letters(cat).lower() == letters(text).lower()[:len(letters(cat))] or (clean(cat) and dict_ok(cat) and len(letters(cat)) == len(letters(text)))):
                text = cat; tclean = True; tdict = True; conf = max(conf, 60)
            elif alnum(cat) == ta and all(dict_ok(e["text"]) for e in es) and (not is_word(text.lower().strip(PUNCT)) or len(es) >= 3 or two_short):
                for e in es:
                    words.append(dict(x0=e["x0"], y0=t["y0"], x1=e["x1"], y1=t["y1"], size=e["size"], bold=e["bold"], italic=e["italic"],
                                      conf=conf, src="emb", flag=False, text=e["text"], h=h, lx0=e["x0"]))
                continue
        out["sup"] = etext is not None
        if etext is None:
            nlet = len(letters(text))
            cover = [e for e in emb if min(t["y1"], e["y1"]) - max(t["y0"], e["y0"]) > 0.5 * h and
                     min(t["x1"], e["x1"]) - max(t["x0"], e["x0"]) >= 0.6 * max(0.5, t["x1"] - t["x0"])]
            covered = any(len(ta) >= 3 and ta in alnum(e["text"]) for e in cover)
            camel = all(dict_ok(p) for p in re.findall(r"[A-Z]?[a-z]+", text)) and nlet >= 6 and tclean
            dashed = text.lstrip("—–-")
            lonely = len(ta) == 1 and not any(v is not t and (0 <= v["x0"] - t["x1"] <= 40 or 0 <= t["x0"] - v["x1"] <= 12)
                                                and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.4 * h for v in tess) \
                                  and not any(0 <= v["x0"] - t["x1"] <= 40 and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.4 * h for v in emb)
            if lonely and conf < 90:
                continue
            # large lettering (>= 20 pt box) recognised with low confidence and no embedded support -> artwork
            if h >= 20 and conf < 60 and nlet <= 5:
                continue
            # a single character with a box much taller than its neighbours' text (rounded panel corner / border speck)
            if len(ta) <= 1 and h >= 12 and conf < 50:
                continue
            if len(ta) == 1 and conf < 30:
                continue
            # a short token, low confidence, whose box is taller than the line it sits in -> border artwork
            if nlet <= 3 and conf < 45 and h >= 12:
                nb = [v for v in tess if v is not t and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.4 * (v["y1"] - v["y0"]) and abs(v["x0"] - t["x1"]) < 60]
                if not nb or all((v["y1"] - v["y0"]) < 0.75 * h for v in nb):
                    continue
            if tclean and tdict and (conf >= 60 or nlet >= 4 and conf >= 45):
                chosen = text
            elif covered and tclean:
                chosen = text
            elif dashed != text and clean(dashed) and dict_ok(dashed) and (covered or conf >= 45):
                chosen = text
            elif camel:
                chosen = text; out["flag"] = conf < 50
            elif tclean and conf >= 85 and nlet >= 3:
                chosen = text
            elif re.fullmatch(r"[A-H]", text) and h >= 11 and not bold and t["x0"] < 70:
                continue
            elif re.fullmatch(r"[a-h]|[A-H]|\d{1,2}[.)]?", text) and conf >= 60 and h <= 14 and \
                    (any(0 <= v["x0"] - t["x1"] <= 40 and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.4 * h for v in tess if v is not t) or
                     any(0 <= v["x0"] - t["x1"] <= 40 and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.4 * h for v in emb)):
                chosen = text
            elif text == "|" and 5.5 <= h <= 9.5 and any(v is not t and 0 <= v["x0"] - t["x1"] <= 6 and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.5 * h
                                                          and re.match(r"^[a-z]{2,}", v["text"]) and dict_ok(v["text"]) for v in tess):
                chosen = "I"
            elif len(ta) == 0:
                if text in ("—", "-", "–", ".", ",", ":", ";", "?", "!", "(", ")", '"', "“", "”", "’", "'", "/", "&", "%", "$", "=", "+", "×", "°") and conf >= 40:
                    chosen = text
                else:
                    continue
            elif conf >= 70 and nlet >= 3 and h <= 16:
                chosen = text; out["flag"] = True
            else:
                continue
        else:
            eclean = clean(etext); edict = dict_ok(etext)
            # a lone glyph both layers see as junk (embedded: apostrophe / quote speck; tesseract: low-confidence
            # single character) at a panel border -> artwork
            if len(ta) <= 1 and not alnum(etext) and conf < 50:
                continue
            # tesseract read a capital I as a bracket / bar ("[n", "|t", "(f")
            if re.fullmatch(r"[\[\(\{|!¦]" + re.escape(etext[1:]), text) and etext[:1] == "I" and edict and len(etext) <= 4:
                text = etext; ta = ea; tclean = True; tdict = True; conf = max(conf, 90)
            prev_sentence_end = any(v is not t and 0 <= t["x0"] - v["x1"] <= 12 and min(v["y1"], t["y1"]) - max(v["y0"], t["y0"]) > 0.5 * h
                                    and re.search(r"[.!?]$", v["text"]) for v in tess)
            # tesseract missed the first (decorative / clipped) capital: "nswer" vs embedded "Answer"
            if len(es) == 1 and etext[:1].isupper() and etext[1:] == text and len(text) >= 3 and dict_ok(etext) and first_on_line:
                text = etext; ta = ea; tclean = True; tdict = True; conf = max(conf, 80)
            case_only = ta.lower() == ea.lower() and ta != ea and eclean
            if case_only and etext[:1].isupper() and text[:1].islower() and (first_on_line or (bold and size and size >= 11) or prev_sentence_end):
                chosen = etext; out["src"] = "emb"
            elif tclean and conf >= 88:
                chosen = text
            elif tclean and tdict and conf >= 50:
                chosen = text
            elif ta == ea and text != etext:
                # same letters, punctuation differs: prefer the apostrophe-bearing variant when the letters form
                # a contraction, else the tesseract reading (better at punctuation)
                if re.search(r"[’']", etext) and not re.search(r"[’']", text) and re.fullmatch(r"[A-Za-z]+[’'][a-z]{1,2}", etext):
                    chosen = etext; out["src"] = "emb"
                else:
                    chosen = text
            elif re.fullmatch(r"\d{1,3}(,\d{3})+", etext) and re.fullmatch(r"[\d.,]+", text) and conf < 60 and \
                    re.sub(r"\D", "", text) == re.sub(r"\D", "", etext)[-len(re.sub(r"\D", "", text)):]:
                chosen = etext; out["src"] = "emb"
            elif eclean and edict and not tdict:
                chosen = etext; out["src"] = "emb"
            elif tclean and tdict and not (conf < 10 and not is_word(ta.lower())):
                chosen = text
            elif eclean and edict and (first_on_line or (bold and size and size >= 11)) and etext[:1].isupper():
                chosen = etext; out["src"] = "emb"
            elif eclean and edict and len(ea) >= 3 and conf < 60:
                chosen = etext; out["src"] = "emb"
            else:
                import difflib
                tt = len(ta); ee = len(ea)
                if eclean and ee > tt and conf < 60:
                    chosen = etext; out["src"] = "emb"
                else:
                    chosen = text
                if conf < 60:
                    out["flag"] = True
        # ---- post-decision strips ------------------------------------------------------------------
        chosen = re.sub(r"^[|¦!]+(?=[A-Za-z]{2})", "", chosen)
        m = re.fullmatch(r"[\[\(\{|]([a-z][a-z]?)([.,;:!?]?)", chosen)
        if m and first_on_line and dict_ok("I" + m.group(1)) and not is_word(m.group(1)) and (etext is None or not re.match(r"^[\[\(\{]", etext)):
            chosen = "I" + m.group(1) + m.group(2)          # "[n" / "(t" at line start -> "In" / "It"
        if es and re.match(r"^[‘'\"“]", chosen) and not re.match(r"^[‘'\"“]", etext) and letters(chosen) == letters(etext):
            chosen = chosen[1:]
        if es and re.match(r"^[\(\[\{]", chosen) and (letters(chosen) == letters(etext) or
                                                        (chosen[1:].lower() == etext[1:].lower() and etext[0].isupper() and len(etext) >= 4)) and \
                not re.match(r"^[\(\[\{]", etext) and not re.search(r"[\)\]\}]", chosen):
            c0 = t["chars"][0]
            if c0[0] in "([{" and ((c0[5] - c0[3]) > 1.5 * h_med(t) or not any(e["text"].startswith(("(", "[", "{")) for e in es)):
                chosen = chosen[1:]
                if chosen and chosen[0].islower() and etext[0].isupper() and chosen.lower() == etext[1:].lower() and dict_ok(etext):
                    chosen = etext
        if es and re.match(r"^[\(\[\{]", chosen) and etext.startswith(("(", "[", "{")) and len(es) >= 2 and \
                len(alnum(es[0]["text"])) == 0 and (es[0]["x1"] - es[0]["x0"]) >= 6:
            chosen = chosen[1:]
        if es and re.search(r"[\)\]\}]$", chosen) and len(es) >= 2 and len(alnum(es[-1]["text"])) == 0 and \
                es[-1]["text"] in (")", "]", "}") and (es[-1]["x1"] - es[-1]["x0"]) >= 6 and not re.search(r"[\(\[\{]", chosen):
            chosen = chosen[:-1]
        if es and re.search(r"[,;]$", chosen) and not re.search(r"[,;.]$", etext) and letters(chosen) == letters(etext) and conf < 96:
            chosen = chosen[:-1]
        # a question mark read as an apostrophe ("passage’" / emb "passage'r"): the glyph is much taller than an apostrophe
        if re.search(r"[A-Za-z]’$", chosen) and len(t["chars"]) >= 2 and t["chars"][-1][0] in "’'" and (etext is None or not re.search(r"[’']$", etext)):
            c = t["chars"][-1]
            xh = [ch[5] - ch[3] for ch in t["chars"] if ch[0] in "aceimnorsuvwxz"]
            xheight = sum(xh) / len(xh) if xh else 0.6 * h
            if (c[5] - c[3]) >= 1.1 * xheight and h >= 5:
                chosen = chosen[:-1] + "?"
        chosen = "I" if chosen == "|" else chosen
        ch = t["chars"]
        if len(ch) >= 2 and chosen and text.endswith(chosen) and len(chosen) < len(text) and not text.startswith(chosen):
            k = len(text) - len(chosen)
            if k < len(ch):
                rest = ch[k:]
                out.update(x0=min(c[2] for c in rest), y0=min(c[3] for c in rest), y1=max(c[5] for c in rest))
                out["h"] = out["y1"] - out["y0"]; out["lx0"] = out["x0"]
                if out["size"] and out["size"] > 2.0 * max(out["h"], 4):
                    out["size"] = None
        elif len(ch) >= 2 and chosen and text.startswith(chosen) and len(chosen) < len(text):
            k = len(text) - len(chosen)
            if k < len(ch):
                rest = ch[:-k]
                out.update(x1=max(c[4] for c in rest), y0=min(c[3] for c in rest), y1=max(c[5] for c in rest))
                out["h"] = out["y1"] - out["y0"]
                if out["size"] and out["size"] > 2.0 * max(out["h"], 4):
                    out["size"] = None
        if not chosen:
            continue
        out["text"] = chosen
        words.append(out)

    # ---- dot leaders (".........") between a label and a value: one "…" glyph keeping the line together ----
    # join leader fragments on the same line (a stray glyph splits the run of dots)
    leaders.sort(key=lambda e: (round((e["y0"] + e["y1"]) / 2 / 4), e["x0"]))
    merged_l = []
    for e in leaders:
        if merged_l and abs(merged_l[-1]["y0"] - e["y0"]) <= 3 and -2 <= e["x0"] - merged_l[-1]["x1"] <= 8:
            merged_l[-1] = dict(merged_l[-1], x1=e["x1"])
        else:
            merged_l.append(dict(e))
    leaders = merged_l
    # tesseract junk read from the dots ("fod", "SOR", "gm", "LO", "ern", "u"): low-confidence tokens inside a leader run
    junk = []
    for w in words:
        if w["src"] == "tess" and min(w["conf"], w.get("raw", w["conf"])) < 60 and len(alnum(w["text"])) <= 3:
            for e in leaders:
                if e["x0"] - 2 <= w["x0"] and w["x1"] <= e["x1"] + 8 and abs((w["y0"] + w["y1"]) / 2 - (e["y0"] + e["y1"]) / 2) <= 12:
                    junk.append(w); break
    words = [w for w in words if w not in junk]
    for e in leaders:
        # the embedded boxes are vertically offset from the scan: snap to the nearest word line on the right
        right = [w for w in words if alnum(w["text"]) and -4 <= w["x0"] - e["x1"] <= 40 and abs((w["y0"] + w["y1"]) / 2 - (e["y0"] + e["y1"]) / 2) <= 12]
        if not right:
            continue
        r = min(right, key=lambda w: abs((w["y0"] + w["y1"]) / 2 - (e["y0"] + e["y1"]) / 2))
        yc_ = (r["y0"] + r["y1"]) / 2
        left = [w for w in words if alnum(w["text"]) and w["y0"] - 3 <= yc_ <= w["y1"] + 3 and -4 <= e["x0"] - w["x1"] <= 40]
        if left and not any(alnum(w["text"]) and w["x0"] > e["x0"] + 4 and w["x1"] < e["x1"] - 4 and w["y0"] - 3 <= yc_ <= w["y1"] + 3 for w in words):
            words.append(dict(x0=e["x0"], y0=r["y0"], x1=e["x1"], y1=r["y1"], size=r["size"], bold=False, italic=False,
                              conf=99.0, src="glyph", flag=False, text="…", h=r["y1"] - r["y0"], leader=True))
    # ---- garbled tesseract spans over clean embedded text --------------------------------------------
    # tesseract sometimes merges two printed lines into one tall box of junk ("DS de", "sir Cg", "Cry"): a
    # tess-sourced token with low raw confidence, not a dictionary word, whose box is >= 1.5x taller than the
    # embedded words it covers, is replaced by those embedded words when they are clean dictionary words
    junk_ti = set()
    for w in words:
        if w["src"] != "tess" or w.get("raw", w["conf"]) >= 45 or len(alnum(w["text"])) > 4 or "ti" not in w:
            continue
        hw = w["y1"] - w["y0"]
        if hw < 16:
            continue                        # a normal-height word box is not a merged-lines blob
        cov = [e for e in emb if inter(w, e) > 0.5 * area(e)]
        if not cov or not all(clean(e["text"]) and dict_ok(e["text"]) and len(alnum(e["text"])) >= 2 and hw >= 1.3 * (e["y1"] - e["y0"]) for e in cov):
            continue
        if any(alnum(e["text"]).lower() == alnum(w["text"]).lower() for e in cov):
            continue                        # tesseract agrees with the embedded word: genuine large type
        junk_ti.add(w["ti"])
    # neighbours of a junk blob on the same tesseract line that are equally tall, low-confidence and not
    # covering any embedded word ("Cg" next to "sir") go too
    if junk_ti:
        blobs = [w for w in words if w.get("ti") in junk_ti]
        for w in words:
            if w["src"] == "tess" and "ti" in w and w["ti"] not in junk_ti and w.get("raw", w["conf"]) < 45 and (w["y1"] - w["y0"]) >= 16 \
                    and len(alnum(w["text"])) <= 4 and not any(inter(w, e) > 0.3 * area(e) for e in emb) \
                    and any(abs(b["y0"] - w["y0"]) < 4 and (0 <= w["x0"] - b["x1"] <= 20 or 0 <= b["x0"] - w["x1"] <= 20) for b in blobs):
                junk_ti.add(w["ti"])
    if junk_ti:
        blobs = [w for w in words if w.get("ti") in junk_ti]
        # low-confidence tess neighbours on the blob's line whose embedded partner is a different word ("or" over
        # "word") are unreliable too: drop them so the embedded word is recovered
        for w in words:
            if w["src"] == "tess" and "ti" in w and w["ti"] not in junk_ti and w.get("raw", w["conf"]) < 60 and len(alnum(w["text"])) <= 4 \
                    and any(abs(b["y0"] - w["y0"]) < 6 and (0 <= w["x0"] - b["x1"] <= 20 or 0 <= b["x0"] - w["x1"] <= 20) for b in blobs):
                cov = [e for e in emb if inter(w, e) >= 0.4 * area(e) and clean(e["text"]) and dict_ok(e["text"])]
                if cov and not any(alnum(e["text"]).lower() == alnum(w["text"]).lower() for e in cov):
                    junk_ti.add(w["ti"])
        words = [w for w in words if w.get("ti") not in junk_ti]
        # the embedded words covered by the removed junk become eligible for recovery below
        t_of_e = {ei: v for ei, v in t_of_e.items() if v not in junk_ti}
    # ---- embedded-only recovery (words tesseract missed entirely) ----------------------------------
    for ei, e in enumerate(emb):
        if ei in t_of_e:
            continue
        t = e["text"]
        if e["size"] < 6:
            continue
        core = alnum(t)
        if not core and t not in ("=", "•", "·", ":"):
            continue
        if any(inter(e, w) > 0.3 * area(e) for w in words):
            continue
        ok = False
        yc = (e["y0"] + e["y1"]) / 2
        if e.get("oval"):
            words.append(dict(x0=e["x0"], y0=e["y0"], x1=e["x1"], y1=e["y1"], size=e["size"], bold=False, italic=False,
                              conf=80.0, src="glyph", flag=False, text="Circle", h=e["y1"] - e["y0"]))
            continue
        if re.fullmatch(r"\d{1,3}\.?", t) and e["size"] < 20:
            ok = True
        elif re.fullmatch(r"\d{1,3}(,\d{3})+", t) and e["size"] < 20:
            ok = True                      # thousands-separated number tesseract missed (table cell)
        elif t in ("•", "·") and 6 <= e["size"] <= 14:
            ok = any(w["y0"] - 2 <= yc <= w["y1"] + 2 and 0 <= w["x0"] - e["x1"] <= 16 and alnum(w["text"]) for w in words)
            if ok:
                words.append(dict(x0=e["x0"], y0=e["y0"], x1=e["x1"], y1=e["y1"], size=e["size"], bold=False, italic=False,
                                  conf=50.0, src="glyph", flag=False, text="•", h=e["y1"] - e["y0"]))
                continue
        elif re.fullmatch(r"[a-h]\.?", t) and e["size"] < 14:
            ok = True
        elif re.fullmatch(r"[A-H]", t) and 9.5 <= e["size"] <= 17 and (e["bold"] or e["x0"] < 70 or e["x0"] > 400):
            ok = True
        elif re.fullmatch(r"[TF]", t) and e["size"] <= 13 and e["x0"] > 400:
            ok = True
        elif t == "=" and e["bold"] and e["size"] >= 11:
            left = [w for w in words if w["y0"] - 2 <= yc <= w["y1"] + 2 and 0 <= e["x0"] - w["x1"] <= 14 and re.fullmatch(r"[A-Z]", w["text"])]
            left_e = [x for x in emb if x is not e and x["y0"] - 2 <= yc <= x["y1"] + 2 and 0 <= e["x0"] - x["x1"] <= 14 and re.fullmatch(r"[A-Z]", x["text"])]
            right = [w for w in words if w["y0"] - 2 <= yc <= w["y1"] + 2 and 0 <= w["x0"] - e["x1"] <= 14 and w["bold"]]
            ok = bool((left or left_e) and right)
            if ok and not left:
                x = left_e[0]
                if not any(inter(x, w) > 0.3 * area(x) for w in words):
                    words.append(dict(x0=x["x0"], y0=x["y0"], x1=x["x1"], y1=x["y1"], size=x["size"], bold=True, italic=x["italic"],
                                      conf=50.0, src="emb-only", flag=False, text=x["text"], h=x["y1"] - x["y0"]))
        elif t == ":" and e["size"] <= 12:
            right = [w for w in words if w["y0"] - 3 <= yc <= w["y1"] + 3 and 0 <= w["x0"] - e["x1"] <= 8 and alnum(w["text"])]
            lefttxt = [w for w in words if w["y0"] - 3 <= yc <= w["y1"] + 3 and 0 <= e["x0"] - w["x1"] <= 3 and alnum(w["text"])]
            ok = bool(right) and not lefttxt
        elif re.fullmatch(r"[A-Z][a-z]+\d{1,3}", t) and dict_ok(re.sub(r"\d", "", t)):
            t = re.sub(r"(\d)", r" \1", t, count=1); ok = True
        elif clean(t) and len(core) >= 2 and e["size"] < 30 and len(letters(t)) >= 0.6 * len(t) and dict_ok(t):
            ok = True
        if ok:
            words.append(dict(x0=e["x0"], y0=e["y0"], x1=e["x1"], y1=e["y1"], size=e["size"], bold=e["bold"], italic=e["italic"],
                              conf=50.0, src="emb-only", flag=False, text=t, h=e["y1"] - e["y0"]))
    # punctuation-only tokens without embedded support must sit inside a text line
    keep = []
    for w in words:
        if w["src"] == "tess" and not alnum(w["text"]):
            yc = (w["y0"] + w["y1"]) / 2
            near = [v for v in words if v is not w and alnum(v["text"]) and v["y0"] - 2 <= yc <= v["y1"] + 2 and
                    (0 <= w["x0"] - v["x1"] <= 12 or 0 <= v["x0"] - w["x1"] <= 12)]
            if not near:
                continue
        keep.append(w)
    words = keep
    for w in words:
        if w["size"] is None:
            w["size"] = round(w["h"] * 1.35, 1) if not re.search(r"[A-Zbdfhklt0-9]", w["text"]) else round(w["h"] * 1.1, 1)
    words.sort(key=lambda w: (round(w["y0"] / 4), w["x0"]))
    return words


if __name__ == "__main__":
    for a in sys.argv[1:]:
        for w in fuse_page(int(a)):
            print(f'{w["x0"]:6.0f}{w["y0"]:6.0f}{w["x1"]:6.0f}{w["y1"]:6.0f} c{w["conf"]:5.1f} {w["src"]:8s} sz{w["size"]:5} {"B" if w["bold"] else " "}{"I" if w["italic"] else " "} {"?" if w["flag"] else " "} {w["text"]!r}')
