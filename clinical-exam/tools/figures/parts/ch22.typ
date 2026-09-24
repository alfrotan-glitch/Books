#import "../lib.typ": *
#let figs = (
  "tug": canvas(92, 40, {
    // chair at right (start), 3 m line to left
    let chx = 80
    poly(((chx, 10), (chx, 26), (chx - 8, 26), (chx - 8, 30)), s: 1.2pt + navy)
    poly(((chx, 26), (chx, 30)), s: 1.2pt + navy); poly(((chx - 8, 20), (chx, 20)), s: 0.9pt + navy)
    ln(chx - 10, 32, 12, 32, s: (paint: teal, thickness: 0.8pt, dash: "dashed"))
    ln(12, 29, 12, 35, s: 1pt + teal)
    arrow(chx - 12, 24, 18, 24, c: teal)
    arrow(16, 17, chx - 12, 17, c: gold)
    poly(((18, 24), (14, 22.5), (13, 20.5), (14, 18.5), (16, 17)), s: 0.9pt + teal)
    cl((chx - 10 + 12) / 2, 36, text(weight: "bold", "۳ متر"), w: 14, size: 7pt, fill: teal)
    cl(chx - 4, 36, "چوکی با دسته", w: 22, size: 6pt, fill: grey)
    cl(46, 21, "بلند شدن · راه رفتن · دور خوردن · برگشتن · نشستن", w: 60, size: 6pt)
    at(1, 2, box(width: 38mm, fill: rgb("#fbe9e7"), radius: 3pt, inset: 3pt, text(size: 6.3pt, fill: red)[*۱۲ ثانیه یا بیشتر:* خطر افتادن]))
  }),
)
