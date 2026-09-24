#import "../lib.typ": *
#let cU = rgb("#bfe0de"); #let cM = rgb("#f2e2b8"); #let cL = rgb("#c9d3e6")
#let sk = 0.6pt + navy
#let mir(pts) = pts.map(p => (44 - p.at(0), p.at(1)))
#let legend = stack(dir: ltr, spacing: 3mm,
  box(width: 3mm, height: 3mm, fill: cU, stroke: sk), text(size: 6.7pt, "لوب بالایی"),
  box(width: 3mm, height: 3mm, fill: cM, stroke: sk), text(size: 6.7pt, "لوب میانی"),
  box(width: 3mm, height: 3mm, fill: cL, stroke: sk), text(size: 6.7pt, "لوب پایینی"))

#let figs = (
  "lung-lobes": {
    let RL = ((14, 4), (19, 6), (20.5, 14), (20.5, 40), (17, 44), (10, 46), (4, 47), (3, 30), (4, 16), (8, 7))
    let LL = ((30, 4), (36, 7), (40, 16), (41, 30), (40, 47), (34, 46), (29, 45), (26, 43), (29, 36), (27.5, 29), (23.5, 25), (23.5, 14), (24.5, 6))
    let front = canvas(44, 52, {
      poly(RL, s: sk, fill: cL, closed: true)
      poly(((20.5, 23), (20.5, 14), (19, 6), (14, 4), (8, 7), (4, 16), (3.4, 24)), s: none, fill: cU, closed: true)
      poly(((3.4, 24), (20.5, 23), (20.5, 40), (17, 44), (16, 44.5), (3.3, 31)), s: none, fill: cM, closed: true)
      poly(RL, s: sk, closed: true)
      ln(3.4, 24, 20.5, 23, s: 0.8pt + navy); ln(3.3, 31, 16, 44.5, s: 0.8pt + navy)
      poly(LL, s: sk, fill: cL, closed: true)
      poly(((40.7, 27), (40, 16), (36, 7), (30, 4), (24.5, 6), (23.5, 14), (23.5, 25), (27.5, 29), (29, 36), (26, 43), (29, 45)), s: none, fill: cU, closed: true)
      poly(LL, s: sk, closed: true)
      ln(40.7, 27, 29, 45, s: 0.8pt + navy)
      ln(22, 0, 22, 12, s: 2pt + grey)
      poly(((2, 9.5), (20, 8.5)), s: 1.2pt + grey); poly(((24, 8.5), (42, 9.5)), s: 1.2pt + grey)
      cl(22, 51, text(weight: "bold", "از جلو"), w: 30, size: 7.4pt)
      cl(6, 39.5, "راست", w: 10, size: 6.2pt, fill: grey); cl(38, 39.5, "چپ", w: 10, size: 6.2pt, fill: grey)
    })
    let BL = ((14, 4), (19, 6), (20, 14), (20, 46), (12, 48), (4, 47), (3, 30), (4, 16), (8, 7))
    let back = canvas(44, 52, {
      for P in (BL, mir(BL)) { poly(P, s: sk, fill: cL, closed: true) }
      poly(((20, 14), (19, 6), (14, 4), (8, 7), (4, 16), (3.4, 36)), s: none, fill: cU, closed: true)
      poly(mir(((20, 14), (19, 6), (14, 4), (8, 7), (4, 16), (3.4, 36))), s: none, fill: cU, closed: true)
      for P in (BL, mir(BL)) { poly(P, s: sk, closed: true) }
      ln(20, 14, 3.4, 36, s: 0.8pt + navy); ln(24, 14, 40.6, 36, s: 0.8pt + navy)
      ln(22, 2, 22, 50, s: (paint: grey, thickness: 0.8pt, dash: "dotted"))
      ln(20.5, 14, 23.5, 14, s: 1pt + red); ln(20.5, 47, 23.5, 47, s: 1pt + red)
      at(22.8, 11, text(size: 6.2pt, fill: red, weight: "bold", "T3")); at(22.8, 44, text(size: 6.2pt, fill: red, weight: "bold", "T10"))
      cl(22, 51, text(weight: "bold", "از پشت"), w: 30, size: 7.4pt)
      cl(6, 39.5, "چپ", w: 10, size: 6.2pt, fill: grey); cl(38, 39.5, "راست", w: 10, size: 6.2pt, fill: grey)
    })
    stack(dir: ttb, spacing: 3mm,
      grid(columns: 2, column-gutter: 6mm, front, back),
      align(center, legend),
      box(width: 94mm, fill: soft, radius: 3pt, inset: 4pt, stack(dir: ttb, spacing: 1.8mm,
        text(size: 6.9pt)[*شق افقی* (تنها در راست): در سطح غضروف ضلع چهارم.],
        text(size: 6.9pt)[*شق مایل:* از خار مهره T3 در پشت، مایل به پایین تا ضلع ششم در جلو.],
        text(size: 6.9pt)[*حد پایینی شش:* ضلع ششم در خط وسط ترقوه، ضلع هشتم در خط وسط ابط، و T10 در پشت.],
        text(size: 6.9pt, fill: teal)[نتیجه: از پشت بیشتر لوب‌های پایینی را می‌شنوید؛ لوب میانی راست را از جلو و زیر بغل.])))
  },

  "lung-states": {
    let panel(title, body, tr, r1, r2, r3, c) = stack(dir: ttb, spacing: 1.6mm,
      box(width: 22mm, height: 26mm, stroke: 0.4pt + rgb("#c9ced6"), radius: 2pt, {
        body
        // trachea (shift tr in mm)
        poly(((11, 0.5), (11, 3), (11 + tr, 7)), s: 1.8pt + grey)
        if tr != 0 { poly(((11 + tr * 0.4 - 0.9 * calc.abs(tr) / tr, 2.2), (11 + tr * 1.2, 2.2)), s: 0.6pt + red)
          poly(((11 + tr * 1.2 - 0.7 * tr / calc.abs(tr), 1.4), (11 + tr * 1.2, 2.2), (11 + tr * 1.2 - 0.7 * tr / calc.abs(tr), 3)), s: 0.6pt + red) }
      }),
      align(center, text(size: 7.4pt, weight: "bold", fill: c, title)),
      box(width: 22mm, align(center, stack(dir: ttb, spacing: 1.3mm, text(size: 6.3pt, r1), text(size: 6.3pt, r2), text(size: 6.3pt, r3)))))
    let lungR(fill: cL) = at(2, 6, rect(width: 7.5mm, height: 18mm, radius: (top: 3.5mm, bottom: 1.2mm), fill: fill, stroke: sk))
    let lungL(dx: 0, fill: cL) = at(12.5 + dx, 6, rect(width: 7.5mm, height: 18mm, radius: (top: 3.5mm, bottom: 1.2mm), fill: fill, stroke: sk))
    stack(dir: ttb, spacing: 2.5mm, grid(columns: 4, column-gutter: 2mm,
      panel("تکاثف", { lungR(); lungL(); at(2.3, 15, rect(width: 6.9mm, height: 8.7mm, radius: (bottom: 1mm), fill: tiling(size: (1.4mm, 1.4mm), place(dx: 0.3mm, dy: 0.3mm, circle(radius: 0.35mm, fill: red))))) },
        0, "قرع: مبهم", "آواز: قصبی", "قصبه‌الریه: وسط", red),
      panel("انصباب", { lungR(); lungL(); at(2.3, 14, rect(width: 6.9mm, height: 9.7mm, radius: (bottom: 1mm), fill: rgb("#8fb8e0")))
          poly(((2.3, 14), (5, 15.2), (9.2, 13.2)), s: 0.6pt + rgb("#3d6fa6")) },
        2.2, "قرع: سنگ‌مانند", "آواز: کم یا غایب", "قصبه‌الریه: دور*", rgb("#3d6fa6")),
      panel("پنوموتوراکس", { at(2, 6, rect(width: 7.5mm, height: 18mm, radius: (top: 3.5mm, bottom: 1.2mm), fill: rgb("#f4f6f9"), stroke: (paint: navy, thickness: 0.6pt, dash: "dashed")))
          at(6, 11, rect(width: 3mm, height: 8mm, radius: 1.5mm, fill: cL, stroke: sk)); lungL() },
        2.2, "قرع: پُرطنین", "آواز: کم یا غایب", "قصبه‌الریه: دور*", navy),
      panel("کلپس", { at(4, 9, rect(width: 5mm, height: 14mm, radius: (top: 2.5mm, bottom: 1mm), fill: rgb("#9aa7bf"), stroke: sk)); lungL(dx: -1.5) },
        -2.2, "قرع: مبهم", "آواز: کم", "قصبه‌الریه: به طرف آن", teal),
    ), align(center, text(size: 6.5pt, fill: grey)[طرف مریض در هر شکل، طرف چپ تصویر (شش راست مریض) است. \* تنها در انصباب بزرگ یا پنوموتوراکس فشاری.]))
  },
)
