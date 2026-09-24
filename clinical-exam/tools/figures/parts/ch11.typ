#import "../lib.typ": *
#let tag(x, y, t, s, w: 24, c: teal) = at(x, y, box(width: w * 1mm, fill: white, stroke: 0.5pt + c, radius: 2pt, inset: 2.4pt,
  align(center, stack(dir: ttb, spacing: 1.3mm, text(size: 7.2pt, weight: "bold", fill: c, dir: ltr, t), text(size: 6.3pt, s)))))
#let figs = (
  "dermatomes": canvas(96, 92, {
    mannequin(48, y0: 2)
    let y0 = 2; let cx = 48
    ln(cx - 10, y0 + 24, cx + 10, y0 + 24, s: (paint: teal, thickness: 0.7pt, dash: "dashed"))
    ln(cx - 8.5, y0 + 36, cx + 8.5, y0 + 36, s: (paint: teal, thickness: 0.7pt, dash: "dashed"))
    // points on patient's right (viewer left) hand & leg, left side labels; trunk labels on right
    dot(cx - 20, y0 + 50.5, r: 0.9, fill: red); dot(cx - 16.6, y0 + 54, r: 0.9, fill: red); dot(cx - 15.0, y0 + 54, r: 0.9, fill: gold)
    ln(cx - 20.8, y0 + 50.8, 22, 44, s: 0.4pt + red); tag(1, 38, "C6", "شست دست", w: 21, c: red)
    ln(cx - 16.6, y0 + 54.8, 22, 58, s: 0.4pt + red); tag(1, 52, "C7", "انگشت میانه", w: 21, c: red)
    ln(cx - 15.3, y0 + 55, 22, 70, s: 0.4pt + gold); tag(1, 65, "C8", "انگشت کوچک", w: 21, c: gold)
    ln(cx + 10, y0 + 24, 72, 22, s: 0.4pt + teal); tag(72, 16, "T4", "سطح نوک ثدیه", w: 23)
    ln(cx + 8.5, y0 + 36, 72, 36, s: 0.4pt + teal); tag(72, 30, "T10", "سطح ناف", w: 23)
    dot(cx - 4, y0 + 78, r: 0.9, fill: navy); ln(cx - 4.8, y0 + 78.4, 22, 82, s: 0.4pt + navy); tag(1, 78, "L4", "داخل ساق و قوزک داخلی", w: 21, c: navy)
    dot(cx + 6.2, y0 + 85.6, r: 0.9, fill: rgb("#5b4a9e")); ln(cx + 7, y0 + 85.6, 72, 70, s: 0.4pt + rgb("#5b4a9e")); tag(72, 63, "L5", "پشت پا و شست پا", w: 23, c: rgb("#5b4a9e"))
    dot(cx + 10.3, y0 + 86.4, r: 0.9, fill: red2); ln(cx + 11, y0 + 86.6, 72, 84, s: 0.4pt + red2); tag(72, 78, "S1", "کناره خارجی و کف پا", w: 23, c: red2)
    cl(cx - 20, 91, "راست مریض", w: 16, size: 6.2pt, fill: grey); cl(cx + 20, 91, "چپ مریض", w: 16, size: 6.2pt, fill: grey)
  }),

  "reflexes": canvas(96, 90, {
    mannequin(48, y0: 2)
    let y0 = 2; let cx = 48
    let hit(x, y, c) = { dot(x, y, r: 1.3, fill: c); at(x - 0.5, y - 1, text(size: 5.7pt, fill: white, weight: "bold", "")) }
    hit(cx - 13, y0 + 32, teal); ln(cx - 14.4, y0 + 32, 25, 22, s: 0.4pt + teal); tag(1, 16, "C5–C6", "دوسر بازو (قات آرنج)", w: 24)
    hit(cx - 15.7, y0 + 45, gold); ln(cx - 17.1, y0 + 45, 25, 40, s: 0.4pt + gold); tag(1, 34, "C5–C6", "بازویی‌کعبری (نزدیک مچ)", w: 24, c: gold)
    hit(cx + 13, y0 + 32, rgb("#5b4a9e")); ln(cx + 14.4, y0 + 32, 71, 22, s: 0.4pt + rgb("#5b4a9e")); tag(71, 16, "C7", "سه‌سر بازو (پشت آرنج)", w: 24, c: rgb("#5b4a9e"))
    hit(cx - 6, y0 + 66, navy); ln(cx - 7.4, y0 + 66, 25, 62, s: 0.4pt + navy); tag(1, 56, "L3–L4", "زانو (وتر زیر کاسه زانو)", w: 24, c: navy)
    hit(cx + 6, y0 + 82, red); ln(cx + 7.4, y0 + 82, 71, 74, s: 0.4pt + red); tag(71, 68, "S1", "قوزک (وتر Achilles در پشت)", w: 24, c: red)
    at(70, 36, box(width: 25mm, fill: soft, radius: 3pt, inset: 3pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 6.7pt, weight: "bold", "از پایین به بالا:"),
      text(size: 6.5pt)[۱–۲: قوزک], text(size: 6.5pt)[۳–۴: زانو], text(size: 6.5pt)[۵–۶: دوسر], text(size: 6.5pt)[۷–۸: سه‌سر])))
  }),

  "umn-lmn": canvas(96, 62, {
    // brain
    at(70, 2, box(width: 22mm, height: 14mm, radius: 7mm, fill: rgb("#e9e4f4"), stroke: 0.6pt + rgb("#5b4a9e"), align(center + horizon, text(size: 6.9pt, weight: "bold", "قشر دماغ"))))
    // cord
    at(40, 22, box(width: 16mm, height: 16mm, radius: 3mm, fill: rgb("#eef2f7"), stroke: 0.6pt + navy))
    at(41, 23, text(size: 6.2pt, fill: grey, "نخاع"))
    dot(46, 33, r: 1.8, fill: gold)
    poly(((81, 16), (81, 26), (52, 26), (47.5, 31.5)), s: 1.4pt + teal)
    poly(((44.3, 33.5), (30, 33.5), (22, 40), (14, 40)), s: 1.4pt + gold)
    at(4, 34, box(width: 10mm, height: 12mm, radius: 4mm, fill: rgb("#f3d6d2"), stroke: 0.6pt + red, align(center + horizon, text(size: 6.7pt, "عضله"))))
    cl(46, 40.5, "حجره شاخ قدامی", w: 22, size: 6.2pt, fill: gold)
    // brackets
    at(50, 44, box(width: 44mm, fill: white, stroke: 0.6pt + teal, radius: 3pt, inset: 3.5pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 7.4pt, weight: "bold", fill: teal, "ضایعه نیورون حرکی بالایی"),
      text(size: 6.6pt)[تون زیاد · رفلکس‌ها تشدیدیافته · Babinski مثبت · حجم عضله تقریباً نارمل])))
    at(2, 48, box(width: 44mm, fill: white, stroke: 0.6pt + gold, radius: 3pt, inset: 3.5pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 7.4pt, weight: "bold", fill: rgb("#8a6a22"), "ضایعه نیورون حرکی پایینی"),
      text(size: 6.6pt)[کاهش حجم · لرزش زیر جلد · تون کم · رفلکس کم یا غایب])))
    ln(66, 26, 66, 43.5, s: (paint: teal, thickness: 0.5pt, dash: "dotted"))
    ln(24, 40, 24, 47.5, s: (paint: gold, thickness: 0.5pt, dash: "dotted"))
    at(2, 3, box(width: 60mm, fill: soft, radius: 3pt, inset: 4pt, text(size: 6.7pt)[راه حرکی دو نیورون دارد: نیورون بالایی از قشر دماغ تا نخاع، و نیورون پایینی از شاخ قدامی نخاع تا عضله. جای ضایعه، نوع نشانه‌ها را تعیین می‌کند.]))
  }),
)
