#import "../lib.typ": *
#let figs = (
  "mse-wheel": canvas(96, 96, {
    let cx = 48; let cy = 48; let RX = 35; let RY = 38
    let items = (("۱", "ظاهر و رفتار", "لباس، تماس چشم، حرکات"), ("۲", "گپ زدن", "سرعت، مقدار، آهنگ"), ("۳", "مزاج و عاطفه", "کلمات مریض / دید شما"), ("۴", "شکل فکر", "جریان و ربط فکرها"),
      ("۵", "محتوای فکر", "هذیان، وسواس، خودکشی"), ("۶", "ادراک", "توهم شنیداری یا دیداری"), ("۷", "شناخت", "هوشیاری، جهت‌یابی، حافظه"), ("۸", "بصیرت", "آیا می‌داند مریض است؟"))
    for (i, it) in items.enumerate() {
      let a = -90deg + i * 45deg
      ln(cx + 14 * calc.cos(a), cy + 14 * calc.sin(a), cx + (RX - 9) * calc.cos(a), cy + (RY - 7) * calc.sin(a), s: 0.6pt + teal)
    }
    at(cx - 14, cy - 14, circle(radius: 14mm, fill: navy))
    cl(cx, cy - 4, text(weight: "bold", "معاینه حالت روانی"), w: 26, size: 6.8pt, fill: white)
    cl(cx, cy + 3, "عکسی از همین لحظه", w: 26, size: 5.8pt, fill: rgb("#c9d6e3"))
    for (i, (k, t, s)) in items.enumerate() {
      let a = -90deg + i * 45deg
      let x = cx + RX * calc.cos(a); let y = cy + RY * calc.sin(a)
      let c = if i == 4 { red } else if i == 6 { gold } else { teal }
      at(x - 12.5, y - 5.5, box(width: 25mm, height: 11mm, fill: white, stroke: 0.6pt + c, radius: 2pt, inset: 1.5pt,
        align(center + horizon, stack(dir: ttb, spacing: 1.1mm, text(size: 6.3pt, weight: "bold", fill: c, k + ". " + t), text(size: 5.3pt, s)))))
    }
  }),
)
