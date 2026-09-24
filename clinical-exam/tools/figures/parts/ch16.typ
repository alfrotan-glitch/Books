#import "../lib.typ": *
#let field(mode) = {
  // mode: array of two strings for left/right eye: "none", "full", "left", "right"
  let one(m) = box(width: 11mm, height: 11mm, {
    place(top + left, circle(radius: 5.5mm, fill: white, stroke: 0.6pt + navy))
    if m == "full" { place(top + left, circle(radius: 5.5mm, fill: navy)) }
    if m == "left" { place(top + left, box(width: 5.5mm, height: 11mm, clip: true, circle(radius: 5.5mm, fill: navy))) }
    if m == "right" { place(top + left, dx: 5.5mm, box(width: 5.5mm, height: 11mm, clip: true, place(top + left, dx: -5.5mm, circle(radius: 5.5mm, fill: navy)))) }
  })
  stack(dir: ltr, spacing: 2mm, one(mode.at(0)), one(mode.at(1)))
}
#let figs = (
  "visual-fields": {
    let pw = canvas(50, 66, {
      let L = teal; let R = gold
      at(12, 2, circle(radius: 5mm, fill: white, stroke: 0.7pt + navy)); at(30, 2, circle(radius: 5mm, fill: white, stroke: 0.7pt + navy))
      cl(17, 0, "چشم چپ", w: 16, size: 6pt, fill: grey); cl(35, 0, "چشم راست", w: 16, size: 6pt, fill: grey)
      // left eye fibres: temporal (lateral) stays left, nasal crosses to right tract
      poly(((14, 11), (22.5, 24), (16, 34), (14, 50), (18, 60)), s: 1.1pt + L)
      poly(((19, 11), (25, 24), (35, 34), (37, 50), (33, 60)), s: 1.1pt + L)
      // right eye fibres
      poly(((38, 11), (29.5, 24), (36, 34), (38, 50), (34, 60)), s: 1.1pt + R)
      poly(((33, 11), (27, 24), (17, 34), (15, 50), (19, 60)), s: 1.1pt + R)
      at(10, 58, box(width: 32mm, height: 6mm, radius: 3mm, fill: rgb("#e9e4f4"), stroke: 0.5pt + purple, align(center + horizon, text(size: 6pt, "قشر بینایی (پس سر)"))))
      let mk(x, y, k) = { dot(x, y, r: 2.2, fill: red); cl(x, y + 0.2, k, w: 4, size: 6.5pt, fill: white, weight: "bold", dir: ltr) }
      mk(36, 17, "1"); mk(26, 24, "2"); mk(37, 40, "3")
      cl(26, 28.5, "کیازما", w: 12, size: 6pt, fill: navy)
    })
    let row(k, t, s, m) = grid(columns: (6mm, 24mm, 24mm), column-gutter: 2mm, align: horizon,
      box(width: 6mm, height: 6mm, radius: 3mm, fill: red, align(center + horizon, text(size: 7pt, fill: white, weight: "bold", k))),
      stack(dir: ttb, spacing: 1.4mm, text(size: 6.8pt, weight: "bold", t), text(size: 6pt, fill: grey, s)),
      field(m))
    grid(columns: 2, column-gutter: 4mm, align: horizon, pw,
      stack(dir: ttb, spacing: 5mm,
        grid(columns: (6mm, 24mm, 11mm, 11mm), column-gutter: 2mm, [], [], align(center, text(size: 6.2pt, fill: grey, "راست")), align(center, text(size: 6.2pt, fill: grey, "چپ"))),
        row("1", "عصب بینایی راست", "کوری تمام چشم راست", ("none", "full")),
        row("2", "کیازمای بصری", "کوری نیمه خارجی هر دو چشم", ("left", "right")),
        row("3", "راه بینایی راست (پشت کیازما)", "کوری نیمه چپ هر دو چشم (همسان)", ("left", "left")),
        text(size: 6pt, fill: grey)[رشته‌های نیمه داخلی (بینی) هر شبکیه در کیازما عبور می‌کنند.]))
  },
)
