#import "../lib.typ": *
#let K = 2.1
#let T(pts) = pts.map(p => (p.at(0) * K, p.at(1) * K))
#let figs = (
  "clubbing": {
    let finger(clubbed) = canvas(44, 30, {
      let body = if clubbed { ((1, 8), (6.5, 8), (10.5, 6.9), (15, 5.4), (18.4, 5.9), (20.1, 8.3), (19.9, 12.2), (16, 14.2), (11.5, 13.2), (1, 12.8)) } else { ((1, 8), (10.8, 8), (16, 6.3), (18.6, 7.2), (19.3, 9.2), (18.6, 11.6), (14, 12.8), (1, 12.8)) }
      poly(T(body), s: 0.8pt + navy, fill: skin, closed: true)
      let nail = if clubbed { ((10.5, 6.9), (15, 5.4), (18.4, 5.9), (20.1, 8.3)) } else { ((10.8, 8), (16, 6.3), (18.6, 7.2), (19.3, 9.2)) }
      poly(T(nail), s: 1.6pt + red2)
      if clubbed { poly(T(((3.5, 8.9), (16.5, 4.9))), s: 0.8pt + teal) }
      else { poly(T(((4, 8), (10.8, 8), (17.5, 5.8))), s: 0.8pt + teal) }
      cl(12, 3, text(weight: "bold", if clubbed { "زاویه ۱۸۰° یا بیشتر" } else { "زاویه حدود ۱۶۰°" }), w: 26, size: 6.8pt, fill: teal)
      cl(18, 29, text(weight: "bold", if clubbed { "چوب طبل شدن" } else { "نارمل" }), w: 24, size: 7.2pt, fill: if clubbed { red } else { navy })
    })
    stack(dir: ttb, spacing: 2mm,
      grid(columns: 2, column-gutter: 6mm, finger(false), finger(true)),
      box(width: 94mm, fill: soft, radius: 3pt, inset: 3pt, text(size: 6.2pt)[زاویه میان بستر ناخن و جلد پشت انگشت را از پهلو ببینید. در چوب طبل شدن این زاویه از بین می‌رود و بند آخر پندیده می‌شود. اگر پشت ناخن‌های دو انگشت مشابه را به هم بچسبانید، پنجره الماسی کوچک میان آن‌ها در چوب طبل شدن دیده نمی‌شود (تست Schamroth).]))
  },
)
