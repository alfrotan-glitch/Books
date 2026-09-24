#import "../lib.typ": *
#let tag(x, y, t, w: 22, c: red) = at(x, y, box(width: w * 1mm, fill: white, stroke: 0.5pt + c, radius: 2pt, inset: 2.4pt, align(center, text(size: 6.4pt, weight: "bold", fill: c, t))))
#let figs = (
  "pulse-sites": canvas(96, 92, {
    mannequin(48, y0: 2)
    let y0 = 2; let cx = 48
    let p(x, y) = dot(x, y, r: 1.3, fill: red)
    p(cx - 3, y0 + 13); ln(cx - 4.3, y0 + 13, 24, 12, s: 0.4pt + red); tag(1, 8, "سباتی (carotid)")
    p(cx - 13, y0 + 31); ln(cx - 14.3, y0 + 31, 24, 28, s: 0.4pt + red); tag(1, 24, "عضدی (brachial)")
    p(cx - 17.8, y0 + 46.5); ln(cx - 19, y0 + 46.5, 24, 44, s: 0.4pt + red); tag(1, 40, "کعبری (radial)")
    p(cx + 4, y0 + 47); ln(cx + 5.3, y0 + 47, 72, 40, s: 0.4pt + red); tag(72, 36, "فخذی (femoral)")
    p(cx + 6, y0 + 66); ln(cx + 7.3, y0 + 66, 72, 58, s: 0.4pt + red); tag(72, 54, "پوپلیتیل (popliteal)*")
    p(cx - 4.2, y0 + 83); ln(cx - 5.5, y0 + 83, 24, 78, s: 0.4pt + red); tag(1, 74, "تیبیال خلفی")
    p(cx + 7.5, y0 + 85.5); ln(cx + 8.8, y0 + 85.5, 72, 78, s: 0.4pt + red); tag(72, 74, "پشت پا", w: 23)
    cl(48, 91, "* نبض پوپلیتیل در پشت زانو، با زانوی کمی خم، لمس می‌شود.", w: 90, size: 5.8pt, fill: grey)
  }),
)
