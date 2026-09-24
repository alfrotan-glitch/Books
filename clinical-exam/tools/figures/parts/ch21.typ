#import "../lib.typ": *
#let figs = (
  "milestones": canvas(96, 62, {
    let X(m) = 87 - m * 3.4
    ln(X(0), 30, X(24.5), 30, s: 1.4pt + navy)
    for m in range(0, 25, step: 3) { ln(X(m), 28.8, X(m), 31.2, s: 0.8pt + navy); cl(X(m), 33.8, fad(m), w: 6, size: 6pt, fill: grey) }
    cl(X(12), 38, "عمر (ماه)", w: 20, size: 6pt, fill: grey)
    let ev(m, up, t, s, c: teal, lvl: 0) = {
      let y = if up { 22 - lvl * 9 } else { 44 + lvl * 9 }
      ln(X(m), 30, X(m), if up { y + 4.5 } else { y - 1 }, s: 0.5pt + c)
      dot(X(m), 30, r: 1.2, fill: c)
      bx(calc.min(calc.max(X(m) - 9.5, 1), 76), if up { y - 2 } else { y - 1 }, 19, 7, [#text(weight: "bold", t)\ #text(size: 5.8pt, s)], c: c, size: 6.3pt, fill: white)
    }
    ev(1.4, true, "۶ هفته", "لبخند اجتماعی", lvl: 1)
    ev(3.6, false, "۴ ماه", "سر ثابت")
    ev(7, true, "۶–۸ ماه", "بدون کمک می‌نشیند")
    ev(9.5, false, "۹–۱۰ ماه", "چهاردست‌وپا")
    ev(13.5, true, "۱۲–۱۵ ماه", "اولین قدم‌ها", lvl: 1)
    ev(18, false, "۱۸ ماه", "۶ تا ۲۰ کلمه")
    ev(24, true, "۲ سال", "دو کلمه با هم")
    at(4, 55, box(width: 88mm, fill: rgb("#fbe9e7"), radius: 3pt, inset: 3pt, text(size: 6.2pt, fill: red)[*زنگ خطر:* لبخند نزدن تا ۱۰ هفته · ننشستن تا ۹ ماه · راه نرفتن یا هیچ کلمه تا ۱۸ ماه · از دست دادن هر مهارت، در هر عمر]))
  }),
)
