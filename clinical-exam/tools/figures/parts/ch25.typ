#import "../lib.typ": *
#let D(name) = json("../data/" + name + ".json")
#let strip(name, t, s, c: navy, ht: 22, y0: none) = stack(dir: ttb, spacing: 1.4mm,
  align(right, [#text(size: 7pt, weight: "bold", fill: c, t) #h(2mm) #text(size: 6.3pt, fill: grey, s)]),
  ecg(92, ht, D(name), y0: y0))
#let beat(name, t, c: navy) = stack(dir: ttb, spacing: 1.2mm, ecg(30, 24, D(name), y0: 15), align(center, box(width: 30mm, text(size: 6.4pt, weight: "bold", fill: c, t))))
#let figs = (
  "ecg-tachy": stack(dir: ttb, spacing: 3mm,
    strip("af", "فبریلیشن اذینی", "بدون موج P؛ فاصله RR کاملاً نامنظم", c: teal),
    strip("flutter", "فلاتر اذین", "دندانه‌های اره‌مانند؛ بلاک ۴ به ۱ در این نمونه", c: purple),
    strip("vt", "تکی‌کاردی بطینی", "کمپلکس‌های QRS پهن و منظم؛ خطرناک", c: red, ht: 28, y0: 15)),
  "ecg-blocks": stack(dir: ttb, spacing: 3mm,
    strip("block1", "بلاک درجه اول", "فاصله PR ثابت و دراز؛ هر P یک QRS دارد", c: teal),
    strip("wenck", "موبیتز I (ونکه‌باخ)", "فاصله PR کم‌کم دراز می‌شود تا یک QRS بیفتد", c: gold),
    strip("mobitz2", "موبیتز II", "فاصله PR ثابت؛ QRS ناگهان می‌افتد", c: red2),
    strip("chb", "بلاک کامل", "موج‌های P و QRS جدا از هم", c: red)),
  "ecg-st": grid(columns: 3, column-gutter: 3mm, row-gutter: 3mm,
    beat("m_normal", "نارمل"), beat("m_stemi", "ST بلند: آسیب حاد", c: red), beat("m_stdep", "ST پایین: اسکیمی", c: red2),
    beat("m_tinv", "T معکوس", c: purple), beat("m_q", "موج Q عمیق: حمله قدیمی", c: navy), beat("hyperK", "T نوک‌تیز: پتاسیم بلند", c: teal)),
  "ecg-territories": canvas(92, 56, {
    // heart schematic: LV ring divided into walls
    let cx = 30; let cy = 28
    at(cx - 20, cy - 20, circle(radius: 20mm, fill: rgb("#f7dcd8"), stroke: 0.7pt + red))
    at(cx - 10, cy - 10, circle(radius: 10mm, fill: white, stroke: 0.6pt + red))
    ln(cx - 20, cy, cx - 10, cy, s: 0.6pt + red); ln(cx + 10, cy, cx + 20, cy, s: 0.6pt + red)
    ln(cx, cy - 20, cx, cy - 10, s: 0.6pt + red); ln(cx, cy + 10, cx, cy + 20, s: 0.6pt + red)
    cl(cx, cy - 14.5, text(weight: "bold", "قدامی"), w: 16, size: 6.6pt)
    cl(cx, cy + 15.5, text(weight: "bold", "پایینی"), w: 16, size: 6.6pt)
    cl(cx + 15, cy + 0.3, text(weight: "bold", "جانبی"), w: 12, size: 6.3pt)
    cl(cx - 15, cy + 0.3, text(weight: "bold", "حجاب"), w: 12, size: 6.3pt); cl(cx - 15, cy + 3.6, "بین بطینی", w: 12, size: 5.6pt, fill: grey)
    cl(cx, cy + 0.3, "بطین چپ", w: 16, size: 6pt, fill: grey)
    let row(t, l, a, c) = box(width: 40mm, fill: white, stroke: 0.6pt + c, radius: 2.5pt, inset: 3pt, stack(dir: ttb, spacing: 1.4mm,
      text(size: 6.8pt, weight: "bold", fill: c, t), text(size: 6.3pt, dir: ltr, l), text(size: 6pt, fill: grey, a)))
    at(52, 1, stack(dir: ttb, spacing: 2mm,
      row("قدامی", "V1 – V4", "شاخه نزولی قدامی چپ", red),
      row("پایینی", "II, III, aVF", "اکثراً کرونری راست", navy),
      row("جانبی", "I, aVL, V5, V6", "شاخه سرکمفلکس", teal)))
  }),
)
