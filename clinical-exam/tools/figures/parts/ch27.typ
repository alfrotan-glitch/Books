#import "../lib.typ": *
#let figs = (
  "alg-abg": canvas(96, 84, {
    bx(30, 1, 36, 8, [*۱. pH*], fill: navy, c: navy, tc: white, size: 7.5pt)
    ln(72, 9, 24, 9, s: 0.8pt + navy); ln(48, 9, 48, 9)
    arrow(72, 9, 72, 13, c: navy); arrow(24, 9, 24, 13, c: navy)
    bx(56, 13, 32, 8, [*اسیدوز*: کمتر از ۷٫۳۵], c: red, size: 6.6pt)
    bx(8, 13, 32, 8, [*الکالوز*: بیشتر از ۷٫۴۵], c: purple, size: 6.6pt)
    for (x, c) in ((72, red), (24, purple)) { ln(x - 12, 24, x + 12, 24, s: 0.7pt + c); ln(x, 21, x, 24, s: 0.7pt + c); arrow(x - 12, 24, x - 12, 27, c: c); arrow(x + 12, 24, x + 12, 27, c: c) }
    bx(73, 27, 22, 13, [*۲. PaCO₂ بالای ۴۵*\ تنفسی], c: red, size: 6.2pt)
    bx(49, 27, 22, 13, [*۳. HCO₃ کمتر از ۲۲*\ متابولیک], c: red, size: 6.2pt)
    bx(25, 27, 22, 13, [*۲. PaCO₂ کمتر از ۳۵*\ تنفسی], c: purple, size: 6.2pt)
    bx(1, 27, 22, 13, [*۳. HCO₃ بالای ۲۶*\ متابولیک], c: purple, size: 6.2pt)
    arrow(60, 40, 60, 45, c: red)
    bx(38, 45, 44, 10, [*۴. فاصله انیونی* = Na − (Cl + HCO₃)\ نارمل حدود ۸–۱۲], c: gold, size: 6.3pt)
    ln(72, 55, 48, 55, s: 0.7pt + gold); ln(60, 55, 60, 55)
    arrow(72, 55, 72, 59, c: gold); arrow(48, 55, 48, 59, c: gold)
    bx(54, 59, 38, 17, [*بلند:* یک اسید اضافه\ کیتواسیدوز · لاکتیت (شاک، سپسیس)\ عدم کفایه کلیه · متانول], c: red, size: 6.1pt)
    bx(22, 59, 30, 17, [*نارمل:*\ اسهال\ امراض توبولی کلیه], c: gold, size: 6.1pt)
    at(1, 44, box(width: 19mm, fill: soft, radius: 3pt, inset: 3pt, text(size: 5.9pt)[نارمل‌ها:\ pH ۷٫۳۵–۷٫۴۵\ PaCO₂ ۳۵–۴۵\ HCO₃ ۲۲–۲۶]))
  }),
)
