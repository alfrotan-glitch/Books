#import "../lib.typ": *
#let cF = rgb("#f2e2b8"); #let cMg = rgb("#bfe0de"); #let cH = rgb("#c9d3e6")
#let trunk(x0, y0, w, h, marks: true) = {
  poly(((x0, y0), (x0 + w, y0), (x0 + w + 2, y0 + h * 0.55), (x0 + w - 1, y0 + h), (x0 + 1, y0 + h), (x0 - 2, y0 + h * 0.55)), s: 0.6pt + grey, fill: skin, closed: true)
  if marks {
  poly(((x0 + 2, y0 + h * 0.22), (x0 + w * 0.3, y0 + h * 0.18), (x0 + w / 2, y0 + 2)), s: 0.7pt + grey)
  poly(((x0 + w - 2, y0 + h * 0.22), (x0 + w * 0.7, y0 + h * 0.18), (x0 + w / 2, y0 + 2)), s: 0.7pt + grey)
  // inguinal ligaments
  poly(((x0 + 4, y0 + h * 0.8), (x0 + w / 2 - 3, y0 + h - 1)), s: 0.7pt + grey)
  poly(((x0 + w - 4, y0 + h * 0.8), (x0 + w / 2 + 3, y0 + h - 1)), s: 0.7pt + grey)
  }
  dot(x0 + w / 2, y0 + h * 0.52, r: 0.8, fill: grey)
}
#let figs = (
  "abd-regions": canvas(96, 80, {
    let x0 = 14; let y0 = 4; let w = 68; let h = 66
    trunk(x0, y0, w, h, marks: false)
    let xa = x0 + 22; let xb = x0 + 46; let ya = y0 + 22; let yb = y0 + 44
    // central column colouring (embryological pain zones)
    at(xa, y0 + 2, rect(width: 24mm, height: 20mm, fill: cF.transparentize(20%)))
    at(xa, ya, rect(width: 24mm, height: 22mm, fill: cMg.transparentize(20%)))
    at(xa, yb, rect(width: 24mm, height: 21mm, fill: cH.transparentize(20%)))
    for x in (xa, xb) { ln(x, y0 - 1, x, y0 + h + 1, s: (paint: navy, thickness: 0.6pt, dash: "dashed")) }
    for y in (ya, yb) { ln(x0 - 3, y, x0 + w + 3, y, s: (paint: navy, thickness: 0.6pt, dash: "dashed")) }
    let cell(cx, cy, t, s) = { cl(cx, cy - 2, text(weight: "bold", t), w: 22, size: 7.0pt); cl(cx, cy + 2.6, s, w: 22, size: 6.0pt, fill: grey) }
    let c1 = x0 + 11; let c2 = x0 + 34; let c3 = x0 + 57
    cell(c1, y0 + 12, "زیر دنده راست", "جگر، کیسه صفرا")
    cell(c2, y0 + 10, "شرسوف", "معده، اثناعشر، پانقراس")
    cell(c3, y0 + 12, "زیر دنده چپ", "طحال")
    cell(c1, y0 + 33, "پهلوی راست", "گرده راست، کولون صاعد")
    cell(c2, y0 + 30, "اطراف ناف", "روده باریک")
    cell(c3, y0 + 33, "پهلوی چپ", "گرده چپ، کولون نازل")
    cell(c1, y0 + 55, "حفره حرقفی راست", "اپندکس، اعور")
    cell(c2, y0 + 55, "بالای عانه", "مثانه، رحم")
    cell(c3, y0 + 55, "حفره حرقفی چپ", "سیگموئید")
    at(4, 72, stack(dir: ltr, spacing: 2.5mm,
      box(width: 3mm, height: 3mm, fill: cF), text(size: 6.5pt, "درد روده پیشین"),
      box(width: 3mm, height: 3mm, fill: cMg), text(size: 6.5pt, "درد روده میانی"),
      box(width: 3mm, height: 3mm, fill: cH), text(size: 6.5pt, "درد روده پسین"),
      text(size: 6.5pt, fill: grey, "  · چپ تصویر = راست مریض")))
  }),

  "abd-palp": {
    let p1 = canvas(44, 52, {
      trunk(4, 2, 36, 44)
      // liver (patient's right = viewer left) and spleen
      poly(((6, 9), (20, 8), (27, 10), (22, 14), (10, 17), (6, 15)), s: 0.6pt + red, fill: rgb("#e7b3ad"), closed: true)
      poly(((33, 9), (38, 11), (37.5, 16), (34, 15)), s: 0.6pt + rgb("#5b4a9e"), fill: rgb("#d9d2ee"), closed: true)
      arrow(10, 42, 10, 19, c: red)
      arrow(12, 41, 33.5, 17.5, c: rgb("#5b4a9e"))
      cl(22, 50, "هر دو را از حفره حرقفی راست آغاز کنید", w: 44, size: 6.5pt)
      cl(10.5, 44.5, "جگر", w: 10, size: 6.5pt, fill: red); cl(30, 30, "طحال", w: 10, size: 6.5pt, fill: rgb("#5b4a9e"))
    })
    let fl = rgb("#8fb8e0")
    let loops(xs, y) = for x in xs { at(x - 2.2, y - 2.2, circle(radius: 2.2mm, fill: white, stroke: 0.5pt + grey)) }
    let p2 = canvas(24, 52, {
      at(1, 12, box(width: 22mm, height: 16mm, radius: 8mm, clip: true, stroke: 0.7pt + navy, fill: white, {
        place(top + left, dy: 9mm, rect(width: 22mm, height: 7mm, fill: fl))
        place(top + left, dx: 0mm, dy: 4mm, rect(width: 3.5mm, height: 6mm, fill: fl))
        place(top + left, dx: 18.5mm, dy: 4mm, rect(width: 3.5mm, height: 6mm, fill: fl))
      }))
      loops((8, 12, 16), 17)
      arrow(24, 20, 22.5, 20, c: red, head: 1.2)
      cl(12, 33, text(weight: "bold", "۱. به پشت"), w: 24, size: 7.0pt)
      cl(12, 37.5, "پهلوی چپ مریض: مبهم", w: 24, size: 6.3pt, fill: red)
    })
    let p3 = canvas(24, 52, {
      at(4, 4, box(width: 16mm, height: 22mm, radius: 8mm, clip: true, stroke: 0.7pt + navy, fill: white, {
        place(top + left, dy: 13mm, rect(width: 16mm, height: 9mm, fill: fl))
      }))
      loops((9, 13), 9); loops((11,), 13)
      arrow(22, 5, 20.2, 5, c: teal, head: 1.2)
      cl(12, 33, text(weight: "bold", "۲. به پهلوی راست"), w: 24, size: 7.0pt)
      cl(12, 37.5, "همان نقطه: طنین‌دار", w: 24, size: 6.3pt, fill: teal)
      cl(12, 42, "= مایع آزاد", w: 24, size: 6.3pt, fill: teal)
    })
    grid(columns: 3, column-gutter: 3mm, p1, p2, p3)
  },
)
