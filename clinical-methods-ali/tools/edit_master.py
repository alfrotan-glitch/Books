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
t = lit("BMI = وزن (کیلوگرام) ÷ قد (متر مربع)", "BMI = وزن (کیلوگرام) ÷ مربع قد (متر²)", t,
        "BMI formula wording: divide by height squared")
t = sub(r'(\d+/\d+) ملی‌متر ستون (?=است|می‌باشد)', r'\1 ملی‌متر ستون سیماب ', t,
        "paediatric BP: missing unit word 'سیماب'", expect=4)
t = lit("**(شکل ۱۴.۲۵: الف: strain pattern :B ،scooping ST changes in digitalis effect :A متناظر در اسکیمیا T inversion :C)**",
        "**(شکل ۱۴.۲۵: A: scooping ST changes in digitalis effect؛ B: strain pattern؛ C: T inversion متناظر در اسکیمیا)**",
        t, "figure 14.25 caption: bidi-scrambled labels reordered")


# ── 2b. SCIENTIFIC UPDATES verified against current references (see CHANGELOG + SOURCES.md) ──
SCI = [
 ("ریت نارمل ۱۴ - ۱۶ تنفس فی دقیقه", "ریت نارمل در کاهلان ۱۲–۲۰ تنفس فی دقیقه", "RR adult 12-20/min"),
 ("حدود نارمل آن در کاهلان ۵۰-۹۰ فی دقیقه است.", "حدود نارمل آن در کاهلان ۵۰–۱۰۰ فی دقیقه است (رهنمود ۲۰۱۸ ACC/AHA/HRS).", "pulse 50-100"),
 ("اگر ریت قلب پایین‌تر از ۵۰ فی دقیقه باشد به نام برادی‌کاردیا یاد می‌گردد.",
  "اگر ریت قلب پایین‌تر از ۵۰ فی دقیقه باشد به نام برادی‌کاردیا یاد می‌گردد (رهنمود ۲۰۱۸ ACC/AHA/HRS؛ در بسیاری کتاب‌ها حد پایین‌تر از ۶۰ فی دقیقه ذکر شده است).", "bradycardia <50 kept + note"),
 ("**اندازه‌های نارمل:** در حالت نارمل فشار سیستولیک ۱۰۰-۱۳۹ ملی‌متر ستون سیماب و فشار دیاستولیک ۶۰-۸۹ ملی‌متر ستون سیماب است.",
  "**اندازه‌های نارمل:** فشار خون نارمل در کاهلان کمتر از ۱۲۰/۸۰ ملی‌متر ستون سیماب است. فشار ۱۴۰/۹۰ ملی‌متر ستون سیماب یا بیشتر (در اندازه‌گیری‌های مکرر) فرط فشار خون گفته می‌شود (WHO و ESC)؛ رهنمود ACC/AHA 2017 حد ۱۳۰/۸۰ را به کار می‌برد.", "BP categories"),
 ("سمت محور نارمل قلب به طرف پایین و چپ قرار دارد که 59° می‌گردد. حدود آن برای کاهلان بالاتر از ۴۰ سال تا 0° می‌رسد.",
  "سمت محور نارمل قلب به طرف پایین و چپ قرار دارد و به طور اوسط در حدود +۶۰° می‌باشد. حدود نارمل آن از −۳۰° تا +۹۰° است.", "axis 59° -> ~+60°, range -30..+90"),
 ("محور اساسی قلب به صورت نارمل در بین ۰ درجه و ۹۰ درجه قرار دارد.", "محور اساسی قلب به صورت نارمل در بین −۳۰ درجه و +۹۰ درجه قرار دارد.", "axis range"),
 ("اگر محور قلبی کمتر از ۰ درجه باشد، به نام انحراف محور به طرف چپ یاد می‌شود.", "اگر محور قلبی منفی‌تر از −۳۰ درجه باشد، به نام انحراف محور به طرف چپ یاد می‌شود.", "LAD < -30°"),
 ("ارتفاع آن معمولاً بیشتر از ۲ ملی‌متر می‌باشد.", "ارتفاع آن در لیدهای اندام‌ها معمولاً کمتر از ۵ ملی‌متر و در لیدهای صدری کمتر از ۱۰ ملی‌متر می‌باشد.", "T amplitude"),
 ("مدت نارمل آن ۰.۲ ثانیه است زمانی که ریت قلبی ۷۰ فی دقیقه باشد.", "مدت نارمل آن ۰.۱۲–۰.۲۰ ثانیه (۳–۵ مربع کوچک) است.", "PR 0.12-0.20"),
 ("به صورت نارمل ۰.۴۲ ثانیه است.", "طول آن نظر به ریت قلبی تغییر می‌کند؛ بناءً QT اصلاح‌شده (QTc) به کار می‌رود که به صورت نارمل در مردها کمتر از ۰.۴۴ و در خانم‌ها کمتر از ۰.۴۶ ثانیه است.", "QTc"),
 ("اگر کمتر از ۰.۱ ثانیه باشد کوتاه گفته می‌شود.", "اگر کمتر از ۰.۱۲ ثانیه باشد کوتاه گفته می‌شود.", "short PR <0.12"),
 ("ریت اذینی سریع و منظم می‌باشد (۲۰۰-۲۵۰ فی دقیقه)", "ریت اذینی سریع و منظم می‌باشد (۲۵۰–۳۵۰ فی دقیقه، معمولاً حدود ۳۰۰)", "flutter atrial rate"),
 ("زمانی که مساحت دسام کمتر از ۱ سانتی‌متر مربع باشد:", "زمانی که مساحت دسام ۱٫۵ سانتی‌متر مربع یا کمتر باشد (رهنمود ۲۰۲۰ ACC/AHA):", "severe MS ≤1.5 cm²"),
 ("مساحت دسام کمتر از ۱ سانتی‌متر مربع یا گرادینت فشار اضافه‌تر از ۵۰ ملی‌متر ستون سیماب",
  "مساحت دسام ۱ سانتی‌متر مربع یا کمتر یا گرادینت اوسط فشار ۴۰ ملی‌متر ستون سیماب یا بیشتر (رهنمود ۲۰۲۰ ACC/AHA)", "severe AS"),
 ("- سقوط سگمنت ST اضافه تر از ۰.۵ ملی‌متر", "- سقوط افقی یا نزولی سگمنت ST به اندازه ۱ ملی‌متر یا بیشتر", "exercise test ST ≥1 mm"),
 ("درجه حرارت بدن باید بیشتر از ۳۵ درجه سانتی‌گرید باشد", "درجه حرارت مرکزی بدن باید ۳۶ درجه سانتی‌گرید یا بیشتر باشد (AAN 2023)", "brain death temp ≥36"),
 ("تنفس خود بخودی زمانی که فشار CO2 بیشتر از ۵۰ ملی‌متر ستون سیماب باشد.", "تنفس خود بخودی زمانی که فشار CO2 شریانی به ۶۰ ملی‌متر ستون سیماب یا بیشتر برسد (AAN 2023).", "apnea test PaCO2 ≥60"),
 ("نباید بیشتر از ۵۰۰ - ۸۰۰ ملی‌لیتر مایع را در یک زمان خارج نماییم.", "نباید بیشتر از ۱٫۵ لیتر مایع را در یک زمان خارج نماییم (BTS)؛ در صورت درد صدر، سرفه یا عسرت تنفس، بذل باید زودتر متوقف شود.", "pleural aspiration ≤1.5 L"),
 ("ساحه اصمیت کبدی ۱۲-۱۵ سانتی‌متر عموداً به طرف سفلی ادامه دارد.", "ساحه اصمیت کبدی در خط متوسط ترقوی به صورت نارمل ۶–۱۲ سانتی‌متر است.", "liver span 6-12 cm"),
 ("مدت آن تا ۰.۱۰ ثانیه", "مدت آن کمتر از ۰.۱۲ ثانیه", "P duration <0.12"),
 ("مدت نارمل آن از ۰.۱۱ ثانیه زیاد نمی‌شود", "مدت نارمل آن کمتر از ۰.۱۲ ثانیه (کمتر از ۳ مربع کوچک) است", "QRS <0.12"),
 ("موجه R در لید aVL اضافه تر از ۱۳ mm", "موجه R در لید aVL ۱۱ mm یا بیشتر", "LVH aVL ≥11 mm (Sokolow-Lyon)"),
 ("مقدم‌ترین زمان برای شنیدن آوازهای قلب هفته ۲۴ است. در این زمان ریت آن ۱۶۰-۱۴۰ فی دقیقه می‌باشد تا زمان ولادت به ۱۲۰ پایین می‌آید.",
  "با Pinard stethoscope آوازهای قلب جنین معمولاً از هفته ۲۰–۲۴ به بعد شنیده می‌شود (با Doppler از هفته ۱۰–۱۲). ریت نارمل آن ۱۱۰–۱۶۰ فی دقیقه است (FIGO).", "FHR 110-160"),
 # appendix (lab)
 ("- **Acid phosphatase:** 1-5 K.A. units", "- **Acid phosphatase (prostatic):** 0-3 U/dl", "ACP"),
 ("- **Alkaline phosphatase:** 4-13 K.A. units", "- **Alkaline phosphatase:** 30-120 U/L", "ALP"),
 ("- **Amylase:** 60-180/100 units/ml", "- **Amylase:** 30-220 U/L (60-120 Somogyi units/dl)", "amylase"),
 ("- **Calcium:** 9-11 mg/100ml or 4.5-5.5 mEq/L", "- **Calcium (total):** 9-10.5 mg/100ml (2.25-2.62 mmol/L)", "Ca"),
 ("- **Carbonate:** 56-78 vol./100ml or 25-35 mEq/L", "- **Bicarbonate (HCO₃):** 21-28 mEq/L", "HCO3"),
 ("- **Iron:** 79-196 µg/100ml", "- **Iron (serum):** 50-150 µg/100ml", "iron"),
 ("- **L.D.H.:** 200-450 unit/ml", "- **L.D.H.:** 100-190 U/L", "LDH"),
 ("- **Lipase:** 200-680 units/ml", "- **Lipase:** 0-160 U/L", "lipase"),
 ("- **Proteins (total):** 6.0-7.8 gm/100ml", "- **Proteins (total):** 6.4-8.3 gm/100ml", "TP"),
 ("- **Fibrinogen:** 0.2-0.4 gm/100ml", "- **Fibrinogen:** 0.2-0.4 gm/100ml (200-400 mg/100ml)", "fibrinogen"),
 ("- **Uric acid:** 2.5-8 mg/100ml", "- **Uric acid:** 4-8.5 mg/100ml (men), 2.7-7.3 mg/100ml (women)", "uric acid"),
 ("- **Potassium:** 15-20 mg/100ml or 3.5-5 mEq/L", "- **Potassium:** 3.5-5.0 mEq/L (13.7-19.5 mg/100ml)", "K"),
 ("- **Creatinine:** 0.9-1.7 mg/100ml", "- **Creatinine:** 0.6-1.2 mg/100ml (men), 0.5-1.1 mg/100ml (women)", "creatinine"),
 ("- **Creatinine:** 0.2-0.6 mg/100ml\n", "", "remove duplicate creatinine line"),
 ("- **Glucose (fasting):** 75-105 mg/100ml", "- **Glucose (fasting):** 70-99 mg/100ml", "FPG"),
 ("- **Cholesterol:** 150-250 mg/100ml", "- **Cholesterol (total):** < 200 mg/100ml (desirable)", "cholesterol"),
 ("- **pH:** 7.38-7.44", "- **pH (arterial):** 7.35-7.45", "pH"),
 ("- **S.G.O.T. (AST):** 10-40 karmen unit (6-18 i.u./L)", "- **S.G.O.T. (AST):** 0-35 U/L", "AST"),
 ("- **Vit B12:** 200-600 pg/ml", "- **Vit B12:** 200-800 pg/ml", "B12"),
 ("- **Blood platelets:** 250,000-500,000/c.m.m.", "- **Blood platelets:** 150,000-400,000/c.m.m.", "platelets"),
 ("- **RBC (women):** 4.5-5 million/c.m.m.", "- **RBC (women):** 4.0-5.2 million/c.m.m.", "RBC women"),
 ("- **RBC (men):** 4.5-6.5 million/c.m.m.", "- **RBC (men):** 4.5-5.9 million/c.m.m.", "RBC men"),
 ("- **Bleeding time:** 2-4 min", "- **Bleeding time:** 2-9 min (Ivy)", "BT"),
 ("- **E.S.R. (men):** up to 5 mm/Hrs/wintrobe\n- **E.S.R. (women):** up to 15 mm method",
  "- **E.S.R. (men):** up to 15 mm/hr (Westergren)\n- **E.S.R. (women):** up to 20 mm/hr (Westergren)", "ESR Westergren"),
 ("- **M.C.V.:** 75-96 c. micron", "- **M.C.V.:** 80-100 fl", "MCV"),
 ("- **M.C.H.:** 27 micro. Micro. Gm", "- **M.C.H.:** 27-32 pg", "MCH"),
 ("- **M.C.H.C.:** 32-38%", "- **M.C.H.C.:** 32-36 g/dl", "MCHC"),
 ("- **Glucose:** 45-100%", "- **Glucose:** 45-80 mg/100ml (≈ 60% of blood glucose)", "CSF glucose"),
 ("- **Volume:** 2-5 ml", "- **Volume:** ≥ 1.4 ml", "semen vol WHO2021"),
 ("- **pH:** 7.2-8", "- **pH:** ≥ 7.2", "semen pH"),
 ("- **Count:** 60-150 million/ml", "- **Count (concentration):** ≥ 16 million/ml", "semen count"),
 ("- **Motility:** 80% or more are motile", "- **Motility (total):** ≥ 42% (progressive ≥ 30%)", "semen motility"),
 ("- **Morphology:** 80-90% are normal", "- **Morphology (normal forms):** ≥ 4% (strict criteria)", "semen morphology"),
]
for old, new, lab in SCI:
    n = t.count(old)
    if n == 0:
        sys.exit("ABORT sci: " + lab)
    t = t.replace(old, new)
    REPORT.append(f"{n:5d}  SCI: {lab}")
t = t.replace("اصغاً", "اصغا")

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

# ── 6. FIGURES: schematic diagrams drawn for this edition (tools/figures) ──
t = DST.read_text(encoding="utf-8")
ECG = {"۱":"ecg-depol","۲":"ecg-axis","۳":"ecg-einthoven","۴":"ecg-chest","۵":"ecg-normal","۶":"ecg-intervals","۷":"ecg-paper",
 "۸":"ecg-ape","۹":"ecg-af","۱۰":"ecg-flutter","۱۱":"ecg-junctional","۱۲":"ecg-pvc","۱۳":"ecg-vt","۱۴":"ecg-vf","۱۵":"ecg-b1",
 "۱۶":"ecg-mobitz2","۱۷":"ecg-b21","۱۸":"ecg-wenck","۱۹":"ecg-chb","۲۰":"ecg-rbbb","۲۱":"ecg-lbbb","۲۲":"ecg-rad","۲۳":"ecg-lad",
 "۲۴":"ecg-axis-quick","۲۵":"ecg-strain","۲۶":"ecg-rvh","۲۷":"ecg-lvh","۲۸":"ecg-pwaves","۲۹":"ecg-coronary","۳۰":"ecg-mi-zones",
 "۳۱":"ecg-tinv","۳۲":"ecg-q","۳۳":"ecg-mi-ant","۳۴":"ecg-mi-inf","۳۵":"ecg-mi-post","۳۶":"ecg-mi-evol","۳۷":"ecg-hypok",
 "۳۸":"ecg-hyperk","۳۹":"ecg-myx","۴۰":"ecg-peric","۴۱":"ecg-dig","۴۲":"ecg-aneur"}
def fig_md(name, cap):
    return f"![{cap}](assets/figures/{name}.png){{.bookfig}}\n"
def repl(m):
    num, cap = m.group(1), m.group(2).strip()
    name = ECG.get(num)
    if not name:
        return m.group(0)
    return fig_md(name, f"شکل ۱۴.{num}: {cap}")
t, n = re.subn(r'::: figure-ph\nشکل ۱۴\.([۰-۹]+):([^\n]*)\n:::\n', repl, t)
REPORT.append(f"{n:5d}  ch.14 figure placeholders -> schematic ECG figures")
left = t.count("::: figure-ph")
REPORT.append(f"{left:5d}  figure placeholders remaining")

# Additional teaching figures inserted after section headings (anchor, name, caption)
ADD = [
 ("## تاریخچه مریض\n", "map-history", "نقشه ذهنی ۱.۱: اجزای تاریخچه مریض"),
 ("## درد (Pain)\n", "map-pain", "نقشه ذهنی ۲.۱: نکات ارزیابی درد"),
 ("## معاینه فزیکی عمومی\n", "map-exam", "نقشه ذهنی ۳.۱: ترتیب معاینه فزیکی"),
 ("## معاینه کلینیکی صدر\n", "map-resp", "نقشه ذهنی ۴.۱: ترتیب معاینه صدر"),
 ("### ارتباط علایم فزیکی و امراض سیستم تنفسی\n", "tbl-resp-signs", "جدول خلاصه ۴.۲: علایم فزیکی در امراض عمده ریوی"),
 ("# فصل پنجم: معاینه اکسری صدر\n", "cxr-read", "شیما ۵.۱: ترتیب مطالعه اکسری صدر"),
 ("**الف) اندازه قلب:**\n", "cxr-ctr", "شیما ۵.۲: اندازه‌گیری نسبت قلبی صدری (CTR)"),
 ("## اناتومی سطحی قلب\n", "map-cvs", "نقشه ذهنی ۶.۱: ترتیب معاینه سیستم قلبی و وعایی"),
 ("### اصغا\n", "heart-areas", "شیما ۶.۲: محراق‌های اصغای قلب"),
 ("### ۲. معاینه بطن\n", "map-gi", "شیما ۷.۱: نواحی نه‌گانه بطن"),
 ("## معاینه فزیکی سیستم عصبی مرکزی\n", "map-neuro", "نقشه ذهنی ۹.۱: ترتیب معاینه سیستم عصبی"),
 ("#### Glasgow Coma Scale\n", "gcs", "جدول ۹.۲: Glasgow Coma Scale"),
 ("**جدول مقایسه‌ای نیورون حرکی سفلی و علوی:**\n", "tbl-umn-lmn", "جدول خلاصه ۹.۳: علایم کلیدی UMN و LMN"),
 ("## معاینه کلینیکی\n", "map-obs", "نقشه ذهنی ۱۰.۱: خلاصه معاینه ولادی"),
 ("## معاینه طفل\n", "peds-vitals", "جدول خلاصه ۱۲.۱: علایم حیاتی نارمل اطفال (از متن همین فصل)"),
 ("**تست Rinne:** اولاً", "ent-rinne", "جدول خلاصه ۱۳.۱: تفسیر تست‌های Rinne و Weber"),
]
k = 0
for anchor, name, cap in ADD:
    if t.count(anchor) < 1:
        sys.exit("ABORT fig anchor: " + anchor)
    i = t.index(anchor)
    if anchor.endswith("\n"):
        j = i + len(anchor)
        t = t[:j] + "\n" + fig_md(name, cap) + "\n" + t[j:]
    else:
        t = t[:i] + fig_md(name, cap) + "\n" + t[i:]
    k += 1
REPORT.append(f"{k:5d}  additional teaching figures / mind maps inserted")
# chapter-5 list of X-ray images: images not reproducible -> short note instead of a dangling list
t = t.replace("**فهرست اشکال و دیاگرام‌های فصل**\n",
  "::: note\n**یادداشت:** برای دیدن رادیوگرافی‌های واقعیِ حالات فهرست ذیل، به اطلس‌های معتبر رادیولوژی مراجعه کنید.\n:::\n\n**فهرست رادیوگرافی‌های پیشنهادی این فصل**\n", 1)
DST.write_text(t, encoding="utf-8")
with open(ROOT / "build/edit-report.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(REPORT[-3:]) + "\n")
print("\n".join(REPORT[-3:]))
