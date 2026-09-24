#import "../lib.typ": *
#let figs = (
  "fundal-height": canvas(92, 70, {
    // trunk outline
    poly(((22, 2), (20, 20), (16, 36), (18, 56), (24, 68)), s: 0.7pt + grey)
    poly(((70, 2), (72, 20), (76, 36), (74, 56), (68, 68)), s: 0.7pt + grey)
    // pregnant belly contour (36 weeks)
    poly(((24, 14), (32, 12), (46, 11), (60, 12), (68, 14)), s: none)
    // landmarks
    dot(46, 8, r: 1.1, fill: navy); at(48, 5.5, text(size: 6.5pt, "زایده خنجری"))
    dot(46, 36, r: 1.1, fill: navy); at(48, 33.5, text(size: 6.5pt, "ناف"))
    poly(((38, 62), (46, 64), (54, 62)), s: 1.4pt + grey); at(48, 64.5, text(size: 6.5pt, "استخوان عانه"))
    // fundus arcs
    let arc(y, h, w, c, lab) = {
      poly(((46 - w, y + h), (46 - w * 0.7, y + h * 0.35), (46 - w * 0.35, y + h * 0.08), (46, y), (46 + w * 0.35, y + h * 0.08), (46 + w * 0.7, y + h * 0.35), (46 + w, y + h)), s: 1.1pt + c)
      bx(3, y - 2.5, 16, 6, text(weight: "bold", lab), c: c, size: 6.8pt)
      ln(19, y + 0.5, 46 - w * 0.9, y + h * 0.7, s: (paint: c, thickness: 0.4pt, dash: "dotted"))
    }
    arc(56, 5, 8, purple, "۱۲ هفته")
    arc(36, 12, 17, teal, "۲۰ هفته")
    arc(10, 22, 24, red, "۳۶ هفته")
    at(72, 44, box(width: 19mm, fill: soft, radius: 3pt, inset: 3pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 6.4pt, weight: "bold", "۲۰ تا ۳۶ هفته:"),
      text(size: 6.2pt, "سانتی‌متر ≈ هفته"),
      text(size: 6.2pt, "(±۲ سانتی‌متر)"))))
  }),
)
