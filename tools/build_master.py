"""Concatenate tools/data/ocr/pNNN.txt into the master text file, run automated QA, append the QA report."""
import os, re, json, sys, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(ROOT, "data", "ocr")
BOOK = os.path.dirname(ROOT)
MASTER = os.path.join(BOOK, "Active_Skills_for_Reading_2_MASTER_TEXT.txt")
QAFILE = os.path.join(BOOK, "Active_Skills_for_Reading_2_EXTRACTION_QA.txt")
N = 179

# manual QA findings (page, section, problem, severity, recommendation) — maintained by hand after visual checks
MANUAL_ISSUES = json.load(open(os.path.join(ROOT, "qa_issues.json"))) if os.path.exists(os.path.join(ROOT, "qa_issues.json")) else []


def load_pages():
    pages = {}
    for pn in range(1, N + 1):
        f = os.path.join(OCR, f"p{pn:03d}.txt")
        pages[pn] = open(f).read() if os.path.exists(f) else None
    return pages


def auto_qa(pages, stats):
    issues = []
    words_per_page = {}
    for pn, t in pages.items():
        if t is None:
            issues.append(dict(page=pn, problem="page file missing", severity="CRITICAL", action="re-run extraction for this page"))
            continue
        body = re.sub(r"^\[PAGE .*?\n", "", t)
        body = re.sub(r"\[running (head|foot):.*?\]", "", body)
        words = re.findall(r"[A-Za-z]{2,}", body)
        words_per_page[pn] = len(words)
        if len(words) < 25:
            issues.append(dict(page=pn, problem=f"very little text ({len(words)} words) — artwork / opener page?", severity="LOW", action="confirm the page is a visual page"))
        flags = re.findall(r"\{\?([^}]*)\}", body)
        if flags:
            issues.append(dict(page=pn, problem="uncertain OCR tokens flagged {?…}: " + ", ".join(flags[:12]) + (" …" if len(flags) > 12 else ""), severity="LOW" if len(flags) <= 3 else "MEDIUM", action="check the flagged words against the page image"))
        # suspicious character sequences
        junk = re.findall(r"[^\W\d_]*[^\x00-\x7F’“”—–…①-⑳☐✓•¹²³⁰-⁹☐■●]+[^\W\d_]*", body)
        junk = [j for j in junk if not re.search(r"[À-ÿ]", j)]
        if junk:
            issues.append(dict(page=pn, problem="unusual characters: " + ", ".join(sorted(set(junk))[:8]), severity="LOW", action="inspect"))
        # duplicated paragraphs inside the page
        paras = [p.strip() for p in body.split("\n\n") if len(p.strip()) > 60]
        dup = [p for p, c in collections.Counter(paras).items() if c > 1]
        if dup:
            issues.append(dict(page=pn, problem="duplicated paragraph(s): " + dup[0][:60] + "…", severity="MEDIUM", action="remove duplicate if not genuine repetition"))
        st = stats.get(str(pn)) or stats.get(pn)
        if st and st["coverage"] < 0.9 and st["raw_words"] > 40:
            issues.append(dict(page=pn, problem=f"coverage of embedded text layer {st['coverage']:.2f} — some words of the text layer are not in the output", severity="MEDIUM", action="compare with page image; text may be photo lettering, dropped junk or genuinely missing"))
    # duplicated paragraphs across pages (identical long paragraphs)
    seen = {}
    for pn, t in pages.items():
        if not t:
            continue
        for p in t.split("\n\n"):
            p = p.strip()
            if len(p) > 120 and not p.startswith("["):
                if p in seen and seen[p] != pn:
                    issues.append(dict(page=pn, problem=f"paragraph identical to one on page {seen[p]}: {p[:50]}…", severity="MEDIUM", action="verify (review units legitimately repeat instructions)"))
                seen.setdefault(p, pn)
    return issues, words_per_page


def main():
    pages = load_pages()
    stats = json.load(open(os.path.join(OCR, "stats.json"))) if os.path.exists(os.path.join(OCR, "stats.json")) else {}
    auto, wpp = auto_qa(pages, stats)
    issues = MANUAL_ISSUES + auto
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    issues.sort(key=lambda i: (i["page"], sev_order.get(i["severity"], 9)))
    out = []
    out.append("ACTIVE SKILLS FOR READING 2 — THIRD EDITION — MASTER TEXT EXTRACTION")
    out.append("Source: Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf (179 PDF pages; printed page = PDF page − 1)")
    out.append("Conventions: [PAGE nnn] = PDF page marker; '# ' / '## ' = headings; **bold** = bold labels; ________ = writing line / blank;")
    out.append("☐ = check box; ① ② … = numbered paragraph / step discs; [5] [10] … = printed line numbers of reading passages;")
    out.append("{?word} = uncertain OCR reading; [TABLE n columns] … [/TABLE] rows with ' | ' cell separators (' / ' = line break inside a cell);")
    out.append("[running foot: …] = page footer (chapter title + page number) kept for reference; [IMAGE — NO TEXT] = artwork without text.")
    out.append("")
    for pn in range(1, N + 1):
        t = pages[pn]
        if t is None:
            out.append(f"[PAGE {pn:03d}]\n\n[EXTRACTION FAILED]\n")
            continue
        out.append(t.rstrip() + "\n")
    # QA report
    ocr_pages = N  # every page is a scan with an embedded OCR layer; the pipeline re-OCRed all of them
    unresolved = sorted({i["page"] for i in issues if i["severity"] in ("HIGH", "CRITICAL")})
    manual = sorted({i["page"] for i in issues if i["severity"] in ("MEDIUM", "HIGH", "CRITICAL")})
    rep = []
    rep.append("[EXTRACTION QA REPORT]")
    rep.append("")
    rep.append(f"Total PDF pages: {N}")
    rep.append(f"Pages successfully processed: {sum(1 for t in pages.values() if t is not None)}")
    rep.append(f"Pages requiring OCR: {ocr_pages} (the PDF is a scan with a low-quality embedded OCR layer on every page; all pages were re-OCRed with Tesseract and fused word-by-word with the embedded layer)")
    rep.append(f"Pages with unresolved issues (HIGH/CRITICAL): {len(unresolved)}" + (": " + ", ".join(map(str, unresolved)) if unresolved else ""))
    rep.append(f"Pages requiring manual verification (MEDIUM or worse): {len(manual)}" + (": " + ", ".join(map(str, manual)) if manual else ""))
    rep.append(f"Pages with uncertain-OCR flags {{?…}}: {sum(1 for t in pages.values() if t and '{?' in t)}")
    rep.append(f"Total words extracted: {sum(wpp.values())}")
    rep.append("Page continuity: " + ("OK — markers [PAGE 001] … [PAGE 179] each present exactly once" if all(pages[p] and pages[p].startswith(f"[PAGE {p:03d}]") for p in range(1, N + 1)) else "PROBLEM"))
    rep.append("")
    rep.append("[ISSUES]")
    rep.append("")
    for i in issues:
        rep.append(f"Page: {i['page']}" + (f"  Section: {i['section']}" if i.get("section") else ""))
        rep.append(f"Problem: {i['problem']}")
        rep.append(f"Severity: {i['severity']}")
        rep.append(f"Action/recommendation: {i['action']}")
        rep.append("")
    out.append("")
    out.append("[EXTRACTION_ISSUES]")
    out.append("(see the full list under [ISSUES] in the QA report below)")
    out.append("")
    out.extend(rep)
    open(MASTER, "w").write("\n".join(out))
    open(QAFILE, "w").write("\n".join(rep))
    print("master:", MASTER, len("\n".join(out)), "chars; issues", len(issues), "; words", sum(wpp.values()))


if __name__ == "__main__":
    main()
