#import "../lib.typ": *
#let figs = (
  "diag-sources": {
    let bar(t, n, vals) = stack(dir: ttb, spacing: 1.5mm,
      text(size: 7pt, weight: "bold")[#t #text(size: 6.2pt, weight: "regular", fill: grey, n)],
      box(width: 88mm, height: 9mm, stack(dir: rtl, ..vals.map(((v, c, l)) => box(width: v * 0.88mm, height: 9mm, fill: c,
        align(center + horizon, text(size: 6.8pt, fill: white, weight: "bold", l)))))))
    stack(dir: ttb, spacing: 4mm,
      bar("Hampton، ۱۹۷۵", "(۸۰ مریض)", ((82.5, teal, "تاریخچه ۸۲٪"), (8.75, gold, "۹٪"), (8.75, purple, "۹٪"))),
      bar("Peterson، ۱۹۹۲", "(۸۰ مریض)", ((76, teal, "تاریخچه ۷۶٪"), (12, gold, "۱۲٪"), (11, purple, "۱۱٪"), (1, rgb("#c9ced6"), ""))),
      align(center, stack(dir: rtl, spacing: 3mm,
        box(width: 3mm, height: 3mm, fill: teal), text(size: 6.3pt, "تاریخچه"),
        box(width: 3mm, height: 3mm, fill: gold), text(size: 6.3pt, "معاینه"),
        box(width: 3mm, height: 3mm, fill: purple), text(size: 6.3pt, "لابراتوار"))))
  },
)
