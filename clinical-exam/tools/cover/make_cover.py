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
ap.add_argument("--interior", default=str(ROOT / "build/moayena-clinical-print-interior.pdf"))
a = ap.parse_args()

pages = pymupdf.open(a.interior).page_count
spine = round(pages * a.caliper, 1)
W, H, B = 148, 210, 3                      # trim width/height, bleed (mm)
total_w = 2 * W + spine + 2 * B
total_h = H + 2 * B

src = f'''
#let navy = rgb("#0f2744"); #let teal = rgb("#136f73"); #let gold = rgb("#b8913a")
#set page(width: {total_w}mm, height: {total_h}mm, margin: 0pt)
#import "tools/cover/art.typ": cover-art
#set text(font: "Vazirmatn", lang: "fa", dir: rtl)
// background: continuous navy -> teal gradient across the whole wrap
#place(top + left, rect(width: 100%, height: 100%, fill: gradient.linear(navy, rgb("#0f4a5c"), angle: 90deg)))

// ── FRONT (left panel, incl. left bleed) ──
#place(top + left, dx: 0mm, dy: 0mm, box(width: {W + B}mm, height: 100%, clip: true,
  cover-art(w: {W + B}, h: {H + 2 * B})))
#place(top + left, dx: {B}mm, dy: {B}mm, box(width: {W}mm, height: {H}mm)[
  #v(8%)
  #align(center)[
    #text(fill: gold, size: 12pt, tracking: 2pt)[❖ ❖ ❖]
    #v(0.6em)
    #text(fill: white, size: 32pt, weight: "bold")[معاینه کلینیکی]
    #v(0.1em)
    #text(fill: rgb("#e8d7b0"), size: 17pt, weight: "bold")[از تاریخچه تا تشخیص]
    #v(0.3em)
    #text(fill: rgb("#d9e8e8"), size: 11pt)[رهنمای عملی برای محصلان طب و داکتران جوان]
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
      #text(fill: white, weight: "bold")[معاینه کلینیکی: از تاریخچه تا تشخیص]
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
  #align(center, text(size: 17pt, weight: "bold")[معاینه کلینیکی: از تاریخچه تا تشخیص])
  #v(0.8em)
  از هر پنج تشخیص، تقریباً چهارتا در گفتگو با مریض پیدا می‌شود.
  این کتاب به شما یاد می‌دهد که آن گفتگو را چطور پیش ببرید، یافته‌ها را
  چطور وزن کنید و از شکایت مریض چطور به تشخیص برسید.

  هر فصل با یک قصه کنار بستر آغاز می‌شود و با قانون‌های کوتاه و ماندگار،
  شواهد علمی تازه، دام‌های رایج و تمرین‌های روزمره ادامه می‌یابد؛
  به زبان دری افغانستان، برای کسی که می‌خواهد نه تنها معاینه کند،
  بلکه مانند یک داکتر ماهر فکر کند.

  #v(0.4em)
  #text(fill: gold, weight: "bold")[در این کتاب:]
  #set list(marker: text(fill: gold)[●], spacing: 0.8em)
  - استدلال کلینیکی: از یافته تا تشخیص
  - معاینه همه سیستم‌ها، قدم‌به‌قدم
  - رهیافت به شکایات شایع
  - چک‌لیست‌های OSCE و قانون‌های کنار بستر

  #v(1fr)
  #line(length: 100%, stroke: 0.6pt + gold)
  #v(0.3em)
  #text(size: 9pt, fill: rgb("#d9e8e8"))[برای محصلان طب، داکتران جوان و متخصصان.]
  #h(1fr)
  #text(size: 9pt, fill: gold, weight: "bold")[داکتر الله یار فروتن]
])
'''
tmp = ROOT / ".cover.typ"
tmp.write_text(src, encoding="utf-8")
out = ROOT / "build/moayena-clinical-cover-wrap.pdf"
typst.compile(str(tmp), output=str(out), root=str(ROOT), font_paths=[str(ROOT / "fonts")], ignore_system_fonts=True)
# front cover alone (trim size, no bleed) for the EPUB, rendered at 300 dpi
front = pymupdf.open(str(out))
pg = front[0]
clip = pymupdf.Rect(B / 25.4 * 72, B / 25.4 * 72, (B + W) / 25.4 * 72, (B + H) / 25.4 * 72)
pix = pg.get_pixmap(dpi=300, clip=clip)
pix.save(str(ROOT / "assets/cover.jpg"), jpg_quality=92)
tmp.unlink()
print(f"epub cover {pix.width}x{pix.height}px; interior pages={pages} caliper={a.caliper} spine={spine}mm  sheet={total_w:.1f}x{total_h}mm -> {out.name}")
