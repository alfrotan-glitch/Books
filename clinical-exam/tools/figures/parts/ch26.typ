#import "../lib.typ": *
#let figs = (
  "cxr-ctr": canvas(90, 64, {
    at(10, 4, rect(width: 70mm, height: 54mm, radius: 8mm, fill: rgb("#1d2733")))
    // lungs
    poly(((16, 12), (40, 8), (42, 46), (15, 50)), s: none, fill: rgb("#3a4a5c"), closed: true)
    poly(((74, 12), (50, 8), (48, 46), (75, 50)), s: none, fill: rgb("#3a4a5c"), closed: true)
    // heart + mediastinum
    poly(((41, 6), (49, 6), (50, 24), (62, 30), (64, 44), (52, 49), (36, 48), (34, 38), (40, 26)), s: none, fill: rgb("#c9ced6"), closed: true)
    // diaphragms (right slightly higher)
    poly(((14, 48), (26, 43), (42, 47)), s: 1pt + rgb("#dfe3e8")); poly(((48, 48), (62, 45), (76, 50)), s: 1pt + rgb("#dfe3e8"))
    // widths
    ln(34, 55, 64, 55, s: 1.2pt + gold); ln(34, 53.5, 34, 56.5, s: 1.2pt + gold); ln(64, 53.5, 64, 56.5, s: 1.2pt + gold)
    ln(14, 60, 76, 60, s: 1.2pt + teal); ln(14, 58.5, 14, 61.5, s: 1.2pt + teal); ln(76, 58.5, 76, 61.5, s: 1.2pt + teal)
    cl(49, 52.5, text(weight: "bold", "a: پهنای قلب"), w: 30, size: 6.3pt, fill: gold)
    cl(45, 63.5, text(weight: "bold", "b: پهنای داخلی صدر"), w: 40, size: 6.3pt, fill: teal)
    at(0, 0, box(width: 24mm, fill: white, stroke: 0.5pt + navy, radius: 3pt, inset: 3pt, text(size: 6.2pt)[در عکس PA:\ *a ÷ b کمتر از ۰٫۵*]))
    cl(20, 40, "راست", w: 10, size: 5.8pt, fill: rgb("#c9ced6")); cl(70, 40, "چپ", w: 10, size: 5.8pt, fill: rgb("#c9ced6"))
  }),
)
