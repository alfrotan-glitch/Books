#import "../lib.typ": *
#let figs = (
  "history-map": {
    let funnel = canvas(40, 58, {
      poly(((2, 4), (38, 4), (28, 22), (12, 22)), s: 0.6pt + teal, fill: rgb("#d6ecea"), closed: true)
      poly(((12, 23), (28, 23), (24, 36), (16, 36)), s: 0.6pt + gold, fill: rgb("#f2e6c4"), closed: true)
      poly(((16, 37), (24, 37), (22, 48), (18, 48)), s: 0.6pt + red, fill: rgb("#f6d5d1"), closed: true)
      cl(20, 11, text(weight: "bold", "سؤال باز"), w: 26, size: 7pt); cl(20, 16, "«از اول بگویید»", w: 30, size: 6pt)
      cl(20, 28, text(weight: "bold", "متمرکز"), w: 14, size: 6.5pt); cl(20, 32, "«بیشتر بگویید»", w: 16, size: 5.4pt)
      cl(20, 42.5, text(weight: "bold", "بسته"), w: 8, size: 5.8pt)
      cl(20, 53, "از باز به بسته", w: 30, size: 6.3pt, fill: grey)
    })
    let room(k, t, c: teal) = box(width: 17mm, height: 11mm, fill: white, stroke: 0.6pt + c, radius: 1.5pt,
      align(center + horizon, stack(dir: ttb, spacing: 1.2mm, text(size: 7pt, weight: "bold", fill: c, k), text(size: 5.8pt, t))))
    let house = canvas(56, 66, {
      poly(((1, 16), (28, 2), (55, 16)), s: 0.8pt + navy, fill: rgb("#e6ebf3"), closed: true)
      cl(28, 11.5, text(weight: "bold", "هفت خانه تاریخچه"), w: 40, size: 7pt)
      at(1, 16, rect(width: 54mm, height: 48mm, stroke: 0.8pt + navy, fill: rgb("#f7f8fa")))
      at(2.5, 18, grid(columns: 3, column-gutter: 1.2mm, row-gutter: 1.4mm,
        room("۳", "قصه مرض فعلی", c: red), room("۲", "شکایت اصلی"), room("۱", "هویت"),
        room("۶", "خانواده"), room("۵", "دواها و حساسیت"), room("۴", "گذشته طبی"),
        [], room("۷", "زندگی و محیط"), []))
      at(2.5, 54, box(width: 51mm, height: 8mm, fill: soft, radius: 1.5pt, align(center + horizon, text(size: 5.9pt)[بعد: مرور سیستم‌ها · نظر مریض (تصور، نگرانی، انتظار)])))
    })
    grid(columns: 2, column-gutter: 3mm, house, funnel)
  },
)
