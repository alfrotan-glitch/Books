#!/usr/bin/env python3
"""Reproducible editorial pass: manuscript/original/clinical-methods-ali.md -> manuscript/master.md

Every rule here is logged (with counts) to build/edit-report.txt and summarised in
CHANGELOG-editorial.md. The original file is never modified.
Rules are deliberately conservative: orthography/terminology normalisation, structure,
bidi repair and *unambiguous* unit typos only. Anything medically uncertain is
FLAGGED (see README / CHANGELOG), not changed.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "manuscript/original/clinical-methods-ali.md"
DST = ROOT / "manuscript/master.md"
REPORT = []

def sub(pattern, repl, text, label, flags=0, expect=None):
    new, n = re.subn(pattern, repl, text, flags=flags)
    REPORT.append(f"{n:5d}  {label}")
    if expect is not None and n != expect:
        sys.exit(f"ABORT: rule '{label}' matched {n}, expected {expect}")
    return new

def lit(old, new, text, label, expect=1):
    n = text.count(old)
    REPORT.append(f"{n:5d}  {label}")
    if n != expect:
        sys.exit(f"ABORT: literal '{label}' found {n}x, expected {expect}")
    return text.replace(old, new)

t = SRC.read_text(encoding="utf-8")

# ── 1. STRUCTURE ────────────────────────────────────────────────
t = sub(r'^\s*</?div[^>]*>\s*$\n?', '', t, "remove GitHub-only RTL <div> wrapper", flags=re.M, expect=2)
t = lit("# میتودهای کلینیکی علی\n\n## متن کامل معاینات کلینیکی\n\n---\n\n", "", t,
        "book title/subtitle headings -> cover & title page (metadata)")
t = lit("\n---\n\n**پایان متن**\n", "\n", t, "remove 'پایان متن' end marker")

# ECG = chapter 14 (its figures are already numbered ۱۴.x); normal values -> appendix at the end
m_app = re.search(r'^# اندازه‌های نارمل\n.*?(?=^# الکتروکاردیوگرافی)', t, flags=re.M | re.S)
appendix = m_app.group(0)
t = t[:m_app.start()] + t[m_app.end():]
t = lit("# الکتروکاردیوگرافی (ECG)", "# فصل چهاردهم: الکتروکاردیوگرافی (ECG)", t, "number ECG chapter as 14")
appendix = appendix.replace("# اندازه‌های نارمل", "# ضمیمه: اندازه‌های نارمل لابراتواری", 1)
appendix = re.sub(r'\n---\s*$', '\n', appendix.rstrip() + "\n")
t = t.rstrip() + "\n\n" + appendix
REPORT.append("    1  move normal-values section after chapter 14 as an appendix")

# ── 2. UNAMBIGUOUS UNIT / TYPO CORRECTIONS (logged as scientific) ──
t = lit("- **Bilirubin:** 0.3-1.0 mg/100mg", "- **Bilirubin:** 0.3-1.0 mg/100ml", t, "Bilirubin unit mg/100mg -> mg/100ml")
t = lit("98-106 mEq/ml", "98-106 mEq/L", t, "Chlorides unit mEq/ml -> mEq/L")
t = lit("- **Amylase:** 60-180/100 units/ml", "- **Amylase:** 60-180 units/100ml (Somogyi)", t, "Amylase unit order")
t = lit("- **Creatinine:** 0.2-0.6 mg/100ml", "- **Creatine:** 0.2-0.6 mg/100ml", t,
        "duplicate 'Creatinine' 0.2-0.6 -> 'Creatine' (FLAGGED for author)")
t = lit("- **E.S.R. (men):** up to 5 mm/Hrs/wintrobe\n- **E.S.R. (women):** up to 15 mm method",
        "- **E.S.R. (men):** up to 5 mm/hr (Wintrobe method)\n- **E.S.R. (women):** up to 15 mm/hr (Wintrobe method)",
        t, "ESR rows: split unit text re-joined")
t = lit("- **Glucose:** 45-100%", "- **Glucose:** 45-100 mg%", t, "CSF glucose unit % -> mg% (range FLAGGED for author)")
t = lit("- **M.C.H.:** 27 micro. Micro. Gm", "- **M.C.H.:** 27 pg (µµg)", t, "MCH unit")
t = lit("- **M.C.V.:** 75-96 c. micron", "- **M.C.V.:** 75-96 fl (cubic micron)", t, "MCV unit")
t = lit("BMI = وزن (کیلوگرام) ÷ قد (متر مربع)", "BMI = وزن (کیلوگرام) ÷ مربع قد (متر²)", t,
        "BMI formula wording: divide by height squared")
t = sub(r'(\d+/\d+) ملی‌متر ستون (?=است|می‌باشد)', r'\1 ملی‌متر ستون سیماب ', t,
        "paediatric BP: missing unit word 'سیماب'", expect=4)
t = lit("**(شکل ۱۴.۲۵: الف: strain pattern :B ،scooping ST changes in digitalis effect :A متناظر در اسکیمیا T inversion :C)**",
        "**(شکل ۱۴.۲۵: A: scooping ST changes in digitalis effect؛ B: strain pattern؛ C: T inversion متناظر در اسکیمیا)**",
        t, "figure 14.25 caption: bidi-scrambled labels reordered")

# LMN/UMN table: row 12 duplicates row 4 and is self-contradictory ('نمی‌باشد / می‌باشد')
t = lit("| ۱۲. موجودیت fasciculation و fibrillation نمی‌باشد / می‌باشد. | ۱۲. — |\n", "", t,
        "LMN/UMN table: drop duplicate/contradictory row 12 (see row 4)")
t = lit("| ۱۳. هر دو سیستم", "| ۱۲. هر دو سیستم", t, "LMN/UMN renumber 13->12")
t = lit("| ۱۳. تنها سیستم", "| ۱۲. تنها سیستم", t, "LMN/UMN renumber 13->12 (UMN)")
t = lit("| ۱۴. اختلالات معصروی", "| ۱۳. اختلالات معصروی", t, "LMN/UMN renumber 14->13")
t = lit("| ۱۴. تشوشات معصروی", "| ۱۳. تشوشات معصروی", t, "LMN/UMN renumber 14->13 (UMN)")
t = lit("| مشاهدات | Exudate |", "| مشاهدات | اگزودت (Exudate) |", t, "exudate table header bilingual")

# ── 3. ORTHOGRAPHY (Afghan Dari conventions; majority form in manuscript) ──
t = sub(r'اصغ(?:أ|اء)', 'اصغا', t, "اصغأ/اصغاء -> اصغا (70 occurrences already use اصغا)")
t = sub(r'توام(?=\s)', 'توأم', t, "توام -> توأم (majority form)")
t = sub(r'هیچگونه', 'هیچ‌گونه', t, "هیچگونه -> هیچ‌گونه (ZWNJ)")
t = sub(r'خانوادگی', 'خانواده‌گی', t, "خانوادگی -> خانواده‌گی (Afghan convention, cf. زنده‌گی in MS)")
t = sub(r'ساییدگی', 'ساییده‌گی', t, "ساییدگی -> ساییده‌گی (consistency)")
t = sub(r'اضافه تر', 'اضافه‌تر', t, "اضافه تر -> اضافه‌تر (ZWNJ)")
t = sub(r'ي', 'ی', t, "Arabic yeh -> Persian yeh")
t = sub(r'علامة', 'علامه', t, "علامة -> علامه")
t = sub(r'حدقة', 'حدقه', t, "حدقة -> حدقه")
t = sub(r'اطلاعات', 'معلومات', t, "اطلاعات -> معلومات (Afghan usage; used 21x in MS)")
t = lit("- آیا بیمار معلوم می‌شود", "- آیا مریض معلوم می‌شود", t, "بیمار -> مریض (Afghan clinical usage)")
t = sub(r'"([^"\n]{1,40})"', r'«\1»', t, "ASCII quotes -> «guillemets»")
t = sub(r'(?<![۰-۹])(?<!شکل )([۰-۹]+)\.(?=[۰-۹])', r'\1٫', t, "Dari decimal separator . -> ٫ between Dari digits")
t = sub(r'(?<=\S) +([،؛:؟!])(?=\s)', r'\1', t, "remove space before Dari punctuation")
# Latin digits inside Dari prose of paediatric BP -> Dari digits
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
t = sub(r'(ساله |نوزادان )(\d+/\d+)(?= ملی)', lambda m: m.group(1)+m.group(2).translate(FA), t,
        "paediatric BP values: Latin -> Dari digits in Dari sentence")

# ── 4. READING AIDS (structure only, no wording change) ──
t = sub(r'^(?:> )?(\*\*یادداشت:\*\*.*)$', lambda m: f'::: note\n{m.group(1)}\n:::', t,
        "'یادداشت' paragraphs -> styled note boxes", flags=re.M)
t = sub(r'^\*\*\((شکل [۰-۹]+\.[۰-۹]+:[^\n]*)\)\*\*$', r'::: figure-ph\n\1\n:::', t,
        "figure references -> figure-placeholder boxes (images not supplied)", flags=re.M)
# two adjacent figure boxes need a blank line between them
t = re.sub(r':::\n::: figure-ph', ':::\n\n::: figure-ph', t)

DST.write_text(t, encoding="utf-8")
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build/edit-report.txt").write_text("\n".join(REPORT) + "\n", encoding="utf-8")
print("\n".join(REPORT))
print(f"wrote {DST} ({len(t)} chars)")

# ── 5. APPENDIX: bullet lists of lab values -> two-column tables (readability; values unchanged) ──
t = DST.read_text(encoding="utf-8")
head, app = t.split("# ضمیمه: اندازه‌های نارمل لابراتواری", 1)
out, rows = [], []
def flush():
    if rows:
        out.append("| آزمایش (Test) | اندازه نارمل (Normal value) |")
        out.append("|---|---|")
        out.extend(rows); out.append("")
        rows.clear()
n = 0
for line in app.split("\n"):
    m = re.match(r'^(\s*)- \*\*(.+?):\*\*\s*(.*)$', line)
    if m:
        name = ("— " if m.group(1) else "") + m.group(2)
        rows.append(f"| {name} | {m.group(3) or '—'} |"); n += 1
    else:
        if line.strip() == "" and rows:
            continue
        flush(); out.append(line)
flush()
app = re.sub(r'\n{3,}', '\n\n', "\n".join(out))
t = head + "# ضمیمه: اندازه‌های نارمل لابراتواری" + app
DST.write_text(t, encoding="utf-8")
print(f"{n:5d}  appendix lab-value list items -> table rows")
with open(ROOT / "build/edit-report.txt", "a", encoding="utf-8") as f:
    f.write(f"{n:5d}  appendix lab-value list items -> table rows\n")
