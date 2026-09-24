#import "../lib.typ": *
#let figs = (
  "abcde": {
    let row(l, t, look, act, c) = grid(columns: (12mm, 80mm), column-gutter: 2mm,
      box(width: 12mm, height: 13mm, fill: c, radius: 3pt, align(center + horizon, text(size: 15pt, weight: "bold", fill: white, dir: ltr, l))),
      box(width: 80mm, height: 13mm, fill: white, stroke: 0.6pt + c, radius: 3pt, inset: (x: 4pt, y: 2pt), align(horizon, stack(dir: ttb, spacing: 1.5mm,
        text(size: 7.2pt, weight: "bold", fill: c, t), text(size: 6.3pt)[#look], text(size: 6.3pt, fill: grey)[#act]))))
    stack(dir: ttb, spacing: 1.6mm,
      box(width: 94mm, fill: soft, radius: 3pt, inset: 3pt, align(center, text(size: 6.6pt)[امنیت خود · صدا زدن مریض · *کمک خواستن* — بعد به ترتیب:])),
      row("A", "راه هوایی", "خُرخُر، غرغر، stridor، سکوت؛ حرکت ضد هم صدر و بطن", "باز کردن راه هوایی، کشیدن ترشحات", red),
      row("B", "تنفس", "سرعت تنفس، SpO₂، قرینگی، جای قصبه‌الریه، قرع و اصغا", "اکسیجن ۹۴–۹۸٪ (۸۸–۹۲٪ در خطر احتباس CO₂)", red2),
      row("C", "گردش خون", "گرمی دست، پُر شدن مویرگی، نبض، فشار، ادرار، خونریزی", "دو کانول بزرگ، مایع کم و ارزیابی دوباره", gold),
      row("D", "وظایف عصبی", "AVPU یا GCS، مردمک‌ها، قند خون، حرکت اعضا", "قند پایین را همان لحظه درمان کنید", teal),
      row("E", "معاینه کامل", "بثورات، زخم، پاها، پشت، حرارت", "حفظ محرمیت و گرمی مریض", navy),
      box(width: 94mm, fill: rgb("#fbe9e7"), radius: 3pt, inset: 3pt, align(center, text(size: 6.6pt, fill: red)[هر مشکل را در همان مرحله درمان کنید؛ بعد از هر درمان، دوباره از A.])))
  },
)
