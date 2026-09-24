#import "../lib.typ": *
#let yn(x, y, t, c: grey) = cl(x, y, text(weight: "bold", t), w: 10, size: 6pt, fill: c)
#let figs = (
  "scrotal-alg": canvas(96, 92, {
    bx(26, 1, 44, 8, text(weight: "bold", "پندیدگی کیسه خصیه"), fill: navy, c: navy, tc: white, size: 7.5pt)
    arrow(48, 9, 48, 13, c: navy)
    bx(22, 13, 52, 9, [*۱.* آیا بالای آن می‌رسید؟], size: 6.8pt)
    // no -> hernia (right side in RTL)
    ln(74, 17.5, 84, 17.5, s: 0.8pt + navy); arrow(84, 17.5, 84, 24, c: red); yn(80, 15, "نه", c: red)
    bx(72, 24, 23, 12, [*فتق*\ ضربه سرفه], c: red, fill: rgb("#fbe9e7"), size: 6.3pt)
    arrow(48, 22, 48, 28, c: navy); yn(52, 25, "بلی", c: teal)
    bx(20, 28, 48, 9, [*۲.* آیا جدا از خصیه است؟], size: 6.8pt)
    ln(24, 37, 24, 42, s: 0.8pt + navy); ln(64, 37, 64, 42, s: 0.8pt + navy)
    yn(68, 39.5, "نه", c: navy); yn(20, 39.5, "بلی", c: navy)
    // not separate branch (right)
    bx(48, 42, 34, 9, [*۳.* روشنی عبور می‌کند؟], size: 6.4pt)
    bx(6, 42, 34, 9, [*۳.* روشنی عبور می‌کند؟], size: 6.4pt)
    for x in (54, 76, 12, 34) { arrow(x, 51, x, 57, c: navy) }
    yn(79, 54, "بلی", c: teal); yn(57, 54, "نه", c: red); yn(37, 54, "بلی", c: teal); yn(15, 54, "نه", c: navy)
    bx(66, 57, 22, 16, [*هایدروسیل*\ خصیه داخل آن حس نمی‌شود], c: teal, size: 6pt)
    bx(43, 57, 22, 16, [*تومور خصیه*\ سخت، بی‌درد، سنگین], c: red, fill: rgb("#fbe9e7"), size: 6pt)
    bx(24, 57, 18, 16, [*کیست بربخ*\ بالا و عقب خصیه], c: teal, size: 6pt)
    bx(3, 57, 20, 16, [*واریکوسیل*\ «کیسه کرم‌ها»، بیشتر چپ], c: gold, size: 6pt)
    at(3, 77, box(width: 90mm, fill: rgb("#fbe9e7"), radius: 3pt, inset: 3pt, text(size: 6.1pt, fill: red)[*کتله سخت داخل خصیه:* الترا ساوند و راجع عاجل. هرگز از راه کیسه خصیه سوزن یا برش نزنید. هایدروسیل تازه در کاهل جوان هم الترا ساوند می‌خواهد.]))
  }),
)
