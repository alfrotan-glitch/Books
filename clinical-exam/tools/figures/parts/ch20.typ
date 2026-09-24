#import "../lib.typ": *
#let figs = (
  "figo-cycle": canvas(98, 70, {
    cl(49, 3, text(weight: "bold", "عادت ماهوار نارمل (FIGO 2018)"), w: 90, size: 7.5pt)
    // frequency ruler: days 15..45 mapped 90mm..8mm (RTL: fewer days on the right)
    let X(d) = 92 - (d - 15) * 2.7
    let y = 16
    poly(((X(15), y), (X(24), y), (X(24), y + 7), (X(15), y + 7)), s: none, fill: rgb("#fbe9e7"), closed: true)
    poly(((X(24), y), (X(38), y), (X(38), y + 7), (X(24), y + 7)), s: none, fill: rgb("#d7ecec"), closed: true)
    poly(((X(38), y), (X(45), y), (X(45), y + 7), (X(38), y + 7)), s: none, fill: rgb("#fbe9e7"), closed: true)
    ln(X(15), y + 7, X(45), y + 7, s: 0.7pt + navy)
    for d in range(15, 46, step: 5) { ln(X(d), y + 7, X(d), y + 8.5); cl(X(d), y + 11, fad(d), w: 8, size: 5.6pt) }
    for d in (24, 38) { ln(X(d), y - 1, X(d), y + 8.5, s: 1pt + teal); cl(X(d), y - 3, text(weight: "bold", fill: teal, fad(d)), w: 8, size: 6.4pt) }
    cl((X(24) + X(38)) / 2, y + 3.8, text(weight: "bold", "نارمل"), w: 30, size: 6.6pt, fill: teal)
    cl((X(15) + X(24)) / 2, y + 3.8, "زیاد تکرار", w: 22, size: 5.8pt, fill: red)
    cl((X(38) + X(45)) / 2, y + 3.8, "کم تکرار", w: 18, size: 5.8pt, fill: red)
    cl(49, y + 15, "طول دوره به روز (از روز اول یک عادت تا روز اول عادت بعدی)", w: 90, size: 5.8pt, fill: grey)
    let row(yy, t, v, c) = { bx(64, yy, 31, 9, text(weight: "bold", t), fill: c, c: c, tc: white, size: 6.4pt); bx(3, yy, 60, 9, v, fill: white, c: c, size: 6pt) }
    row(36, "مدت خونریزی", [تا *۸ روز* نارمل؛ بیشتر از ۸ روز = طولانی], teal)
    row(47, "منظم بودن", [فرق کوتاه‌ترین و درازترین دوره *۷ تا ۹ روز* یا کمتر], navy)
    row(58, "مقدار", [به قضاوت مریض: آیا زندگی روزمره‌اش را مختل می‌سازد؟], gold)
  }),
)
