#import "../lib.typ": *
#let card(x, y, t, when, len, core, c) = {
  bx(x, y, 22, 7, text(weight: "bold", t), fill: c, c: c, tc: white, size: 6.8pt)
  bx(x, y + 7, 22, 27, stack(dir: ttb, spacing: 1.6mm, text(size: 5.6pt, fill: grey, when), text(size: 6pt, weight: "bold", len), text(size: 5.6pt, core)), fill: white, c: c)
}
#let figs = (
  "case-formats": canvas(98, 84, {
    bx(29, 1, 40, 9, text(weight: "bold", "یک مریض، یک قصه"), fill: navy, c: navy, tc: white, size: 7.5pt)
    for x in (13, 37.5, 61.5, 86) { ln(49, 10, x, 15, s: 0.6pt + navy) }
    card(75, 15, "یک‌خطی", "در آغاز هر معرفی", "یک جمله", "عمر، جنس، زمینه مهم، شکایت و مدت", teal)
    card(51, 15, "معرفی شفاهی", "در راپور صبح و ویزیت", "۳ تا ۵ دقیقه", "هفت قدم؛ قصه مرض فعلی درازترین", navy)
    card(27, 15, "SOAP", "یادداشت روزانه", "برای هر مشکل جدا", "ذهنی، عینی، ارزیابی، پلان", gold)
    card(3, 15, "SBAR", "تحویل و تیلفون", "حدود ۳۰ ثانیه", "وضعیت، زمینه، ارزیابی، درخواست روشن", red)
    cl(49, 55, text(weight: "bold", "هفت قدم معرفی شفاهی"), w: 60, size: 7pt)
    let steps = ("یک‌خطی", "قصه مرض فعلی", "سوابق مربوط", "معاینه", "معاینات مؤثر", "ارزیابی", "پلان")
    let ws = (10, 22, 11, 11, 11, 11, 9)
    let x = 95
    for (i, s) in steps.enumerate() {
      let w = ws.at(i); x = x - w
      let c = if i == 1 { navy } else if i == 5 { teal } else { soft }
      let tc = if i == 1 or i == 5 { white } else { navy }
      bx(x, 60, w - 0.8, 10, text(size: 5.4pt, weight: if i == 1 or i == 5 { "bold" } else { "regular" }, s), fill: c, c: teal, tc: tc)
    }
    at(3, 73, box(width: 92mm, fill: rgb("#fdf6e7"), radius: 3pt, inset: 3pt, text(size: 6pt, fill: rgb("#8a6a22"))[*انتخاب، نشانه فکر است:* قصه مرض فعلی درازترین قسمت است؛ ارزیابی جایی است که استدلال شما دیده می‌شود.]))
  }),
)
