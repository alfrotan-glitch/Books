#import "../lib.typ": *
#let figs = (
  "tuning-fork": {
    let head(dir, bad, title, weber, rinneR, rinneL, c) = stack(dir: ttb, spacing: 1.6mm,
      canvas(28, 26, {
        at(6, 3, ellipse(width: 16mm, height: 20mm, fill: skin, stroke: 0.6pt + navy))
        // ears: viewer left = patient right
        at(3.5, 10, ellipse(width: 3.5mm, height: 6mm, fill: if bad == "R" { rgb("#f3c1bb") } else { skin }, stroke: 0.6pt + if bad == "R" { red } else { navy }))
        at(21, 10, ellipse(width: 3.5mm, height: 6mm, fill: skin, stroke: 0.6pt + navy))
        // fork at vertex
        poly(((13, 0), (13, 3.5)), s: 1pt + grey); poly(((15, 0), (15, 3.5)), s: 1pt + grey); poly(((13, 3.5), (15, 3.5)), s: 1pt + grey)
        if dir == 0 { cl(14, 12, "•", w: 4, size: 10pt, fill: c) }
        if dir == -1 { arrow(14, 13, 7, 13, c: c) }
        if dir == 1 { arrow(14, 13, 21, 13, c: c) }
      }),
      align(center, text(size: 7pt, weight: "bold", fill: c, title)),
      box(width: 28mm, align(center, stack(dir: ttb, spacing: 1.3mm,
        text(size: 6.2pt)[Weber: #weber], text(size: 6.2pt)[Rinne گوش راست: #rinneR], text(size: 6.2pt)[Rinne گوش چپ: #rinneL]))))
    stack(dir: ttb, spacing: 3mm,
      grid(columns: 3, column-gutter: 4mm,
        head(0, "", "نارمل", "وسط", "هوا بهتر از استخوان", "هوا بهتر از استخوان", teal),
        head(-1, "R", "کری انتقالی راست", "به طرف گوش راست (مریض)", [*استخوان بهتر از هوا*], "هوا بهتر از استخوان", red),
        head(1, "R", "کری حسی‌عصبی راست", "به طرف گوش چپ (سالم)", "هوا بهتر (هر دو کم)", "هوا بهتر از استخوان", purple)),
      align(center, text(size: 6pt, fill: grey)[گوش سرخ = گوش مریض · چپ تصویر = گوش راست مریض · دیاپازون ۵۱۲ هرتز]))
  },
)
