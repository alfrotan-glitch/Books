#!/usr/bin/env python3
"""Build the full print cover (back + spine + front, with 3 mm bleed) for the
right-bound (RTL) A5 paperback.  Spine width = interior pages x paper caliper.

Usage: python3 tools/cover/make_cover.py [--caliper 0.055]
The caliper (mm per PAGE, i.e. half a leaf) MUST be confirmed with the printer:
  80 g/m2 uncoated offset ~0.050-0.057, 90 g/m2 ~0.060, 70 g/m2 ~0.045.
Laid flat and viewed from outside, a right-bound book has the FRONT cover on
the LEFT of the spine and the BACK cover on the RIGHT.
"""
import argparse, pathlib, typst, pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--caliper", type=float, default=0.055)
ap.add_argument("--interior", default=str(ROOT / "build/clinical-methods-ali-print-interior.pdf"))
a = ap.parse_args()

pages = pymupdf.open(a.interior).page_count
spine = round(pages * a.caliper, 1)
W, H, B = 148, 210, 3                      # trim width/height, bleed (mm)
total_w = 2 * W + spine + 2 * B
total_h = H + 2 * B

src = f'''
#let navy = rgb("#0f2744"); #let teal = rgb("#136f73"); #let gold = rgb("#b8913a")
#set page(width: {total_w}mm, height: {total_h}mm, margin: 0pt)
#set text(font: "Vazirmatn", lang: "fa", dir: rtl)
// background: continuous navy -> teal gradient across the whole wrap
#place(top + left, rect(width: 100%, height: 100%, fill: gradient.linear(navy, rgb("#0f4a5c"), angle: 90deg)))

// ── FRONT (left panel, incl. left bleed) ──
#place(top + left, dx: 0mm, dy: 0mm, box(width: {W + B}mm, height: 100%, clip: true,
  image("assets/cover-art.jpg", width: 100%, height: 100%, fit: "cover")))
#place(top + left, dx: {B}mm, dy: {B}mm, box(width: {W}mm, height: {H}mm)[
  #v(15%)
  #align(center)[
    #text(fill: gold, size: 12pt, tracking: 2pt)[❖ ❖ ❖]
    #v(0.6em)
    #text(fill: white, size: 30pt, weight: "bold")[میتودهای کلینیکی علی]
    #v(0.1em)
    #text(fill: rgb("#d9e8e8"), size: 13pt)[متن کامل معاینات کلینیکی]
    #v(0.5em)
    #line(length: 35%, stroke: 1pt + gold)
    #v(0.6em)
    #text(fill: gold, size: 13pt, weight: "bold")[داکتر الله یار فروتن]
  ]
])

// ── SPINE ──
#place(top + left, dx: {W + B}mm, dy: 0mm, rect(width: {spine}mm, height: 100%, fill: navy, stroke: none))
#place(top + left, dx: {W + B}mm, dy: {B}mm, box(width: {spine}mm, height: {H}mm,
  align(center + horizon, rotate(-90deg, reflow: true,
    box(width: {H - 30}mm)[
      #set text(size: {min(12, spine * 0.45):.1f}pt)
      #text(fill: white, weight: "bold")[میتودهای کلینیکی علی]
      #h(1fr) #text(fill: gold, size: 0.8em)[❖] #h(1fr)
      #text(fill: gold, weight: "bold")[داکتر الله یار فروتن]
    ]))))

// ── BACK (right panel) ──
#place(top + left, dx: {W + B + spine}mm, dy: {B}mm, box(width: {W}mm, height: {H}mm,
  inset: (x: 15mm, top: 20mm, bottom: 14mm))[
  #set par(justify: true, leading: 0.95em, spacing: 1.2em)
  #set text(fill: white, size: 11.5pt)
  #align(center, text(fill: gold, size: 12pt, tracking: 2pt)[❖ ❖ ❖])
  #v(0.8em)
  #align(center, text(size: 18pt, weight: "bold")[میتودهای کلینیکی علی])
  #v(0.8em)
  «میتودهای کلینیکی علی» رهنمای درسی معاینات کلینیکی به زبان دری است؛ از
  گرفتن تاریخچه و معاینه عمومی تا معاینه سیستم‌های قلبی‌وعایی، تنفسی، هضمی،
  عصبی، حرکی، ولادی، نسایی، اطفال، گوش و بینی و گلو، و خوانش
  الکتروکاردیوگرام.

  هر فصل با اهداف آموزشی آغاز می‌شود و با نکات کلیدی، علایم خطر،
  کیس کلینیکی و سؤالات خودآزمایی پایان می‌یابد. اصطلاحات طبی با معادل
  انگلیسی آن‌ها آمده‌اند و اندازه‌های نارمل با رهنمودهای معتبر و به‌روز
  مقایسه و تصحیح شده‌اند.

  #v(0.4em)
  #text(fill: gold, weight: "bold")[در این کتاب:]
  #set list(marker: text(fill: gold)[●], spacing: 0.8em)
  - ۱۴ فصل و ۵ ضمیمه
  - ۶۳ شکل، شیما و الگوریتم
  - ۱۵ کیس کلینیکی و ۱۵ مجموعه سؤال با جواب
  - جدول اندازه‌های نارمل لابراتواری و فهرست اصطلاحات دری ـ انگلیسی

  #v(1fr)
  #line(length: 100%, stroke: 0.6pt + gold)
  #v(0.3em)
  #text(size: 9pt, fill: rgb("#d9e8e8"))[برای محصلان طب، داکتران جوان و استادان طب کلینیکی.]
  #h(1fr)
  #text(size: 9pt, fill: gold, weight: "bold")[داکتر الله یار فروتن]
])
'''
tmp = ROOT / ".cover.typ"
tmp.write_text(src, encoding="utf-8")
out = ROOT / "build/clinical-methods-ali-cover-wrap.pdf"
typst.compile(str(tmp), output=str(out), root=str(ROOT), font_paths=[str(ROOT / "fonts")], ignore_system_fonts=True)
tmp.unlink()
print(f"interior pages={pages} caliper={a.caliper} spine={spine}mm  sheet={total_w:.1f}x{total_h}mm -> {out.name}")
