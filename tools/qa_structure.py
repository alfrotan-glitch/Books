"""QA pass 2 helpers: structural checks over the rendered pages."""
import os, re, json, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(ROOT, "data", "ocr")

UNIT_OPENERS = {1: 12, 2: 22, 3: 32, 4: 50, 5: 60, 6: 70, 7: 88, 8: 98, 9: 108, 10: 126, 11: 136, 12: 146}
REVIEW_OPENERS = {1: 42, 2: 80, 3: 118, 4: 156}
SECTION_HEADS = ["Before You Read", "Reading Skill", "Reading Comprehension", "Critical Thinking", "Vocabulary Comprehension",
                 "Vocabulary Skill", "Real Life Skill", "What do you think", "Self Check", "Fluency Strategy", "Fluency Practice"]


def load():
    return {pn: open(os.path.join(OCR, f"p{pn:03d}.txt")).read() for pn in range(1, 180)}


def main():
    P = load()
    # 1. page markers
    for pn, t in P.items():
        assert t.startswith(f"[PAGE {pn:03d}]"), pn
    print("page markers OK 1..179")
    # 2. unit openers contain "UNIT" and the number
    for u, pn in UNIT_OPENERS.items():
        t = P[pn]
        ok = re.search(r"\bUNIT\b", t) and re.search(rf"(^|\n)#* ?{u}\s*$", t, re.M)
        print(f"unit {u:2d} opener p{pn}: {'OK' if ok else 'CHECK'}  title: {re.search(r'^# (.*)$', t, re.M).group(1) if re.search(r'^# (.*)$', t, re.M) else '?'}")
    for r, pn in REVIEW_OPENERS.items():
        t = P[pn]
        print(f"review {r} p{pn}: {'OK' if 'Review' in t else 'CHECK'} :: {t.splitlines()[2][:60]}")
    # 3. chapter pages: each unit has chapter 1 (opener+1) and chapter 2 (opener+5)
    for u, pn in UNIT_OPENERS.items():
        for k, off in ((1, 1), (2, 5)):
            t = P[pn + off]
            m = re.search(r"CHAPTER (\d)", t)
            print(f"  unit {u} chapter {k} p{pn+off}: {'OK' if m and m.group(1) == str(k) else 'CHECK'} sections: " +
                  ", ".join(s for s in SECTION_HEADS if s.lower() in t.lower()))
    # 4. section heads per chapter spread (pages opener+1 .. opener+9)
    missing = []
    for u, pn in UNIT_OPENERS.items():
        span = "\n".join(P[p] for p in range(pn + 1, pn + 10))
        for s in ["Before You Read", "Reading Skill", "Reading Comprehension", "Critical Thinking", "Vocabulary Comprehension", "Vocabulary Skill", "Real Life Skill", "What do you think"]:
            c = len(re.findall(re.escape(s), span, re.I))
            if (s in ("Real Life Skill", "What do you think") and c < 1) or (s not in ("Real Life Skill", "What do you think") and c < 2):
                missing.append((u, s, c))
    print("section-head shortfalls (unit, section, count):", missing)
    # 5. vocabulary index continuity: headwords alphabetical within chapter blocks
    idx = "\n".join(P[p] for p in range(164, 176))
    heads = re.findall(r"^([a-z][a-z\-’' ]{1,25}) (?:\{\?)?/", idx, re.M)
    print("vocabulary index headwords found:", len(heads))
    # 6. exercise letters have instructions (A/B/C lines followed by text)
    bad = []
    for pn, t in P.items():
        for m in re.finditer(r"^([A-D])\s*$", t, re.M):
            bad.append((pn, m.group(1)))
    print("bare exercise letters (marker without instruction on the same line):", bad[:30], len(bad))
    # 7. flags / suspicious tokens
    flags = collections.Counter()
    for pn, t in P.items():
        flags[pn] = len(re.findall(r"\{\?", t))
    print("pages with most flags:", flags.most_common(10))
    # 8. words
    tot = sum(len(re.findall(r"[A-Za-z]{2,}", t)) for t in P.values())
    print("total words:", tot)
    short = [(pn, len(re.findall(r"[A-Za-z]{2,}", t))) for pn, t in P.items() if len(re.findall(r"[A-Za-z]{2,}", t)) < 60]
    print("short pages:", short)


if __name__ == "__main__":
    main()
