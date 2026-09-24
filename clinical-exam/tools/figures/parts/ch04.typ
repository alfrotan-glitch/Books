#import "../lib.typ": *
#let figs = (
  "prob-curves": canvas(92, 72, {
    let ox = 34; let oy = 62; let S = 52   // plot origin (bottom-left), size in mm
    // grid
    for i in range(0, 11) {
      let v = i / 10
      ln(ox + v * S, oy, ox + v * S, oy - S, s: 0.3pt + rgb("#e3e6ea")); ln(ox, oy - v * S, ox + S, oy - v * S, s: 0.3pt + rgb("#e3e6ea"))
    }
    for i in range(0, 11, step: 2) {
      cl(ox + i / 10 * S, oy + 3, fad(i * 10), w: 8, size: 5.8pt, fill: grey)
      cl(ox - 3.5, oy - i / 10 * S, fad(i * 10), w: 6, size: 5.8pt, fill: grey)
    }
    ln(ox, oy, ox + S, oy, s: 0.7pt + navy); ln(ox, oy, ox, oy - S, s: 0.7pt + navy)
    cl(ox + S / 2, oy + 7.5, "احتمال پیش از یافته (٪)", w: 40, size: 6.3pt)
    at(ox, oy - S - 6, box(width: 40mm, text(size: 6.3pt, "احتمال بعد از یافته (٪)")))
    let lrs = ((10, red, "۱۰"), (5, red2, "۵"), (2, gold, "۲"), (1, grey, "۱"), (0.5, teal, "۰٫۵"), (0.2, rgb("#2a7fb0"), "۰٫۲"), (0.1, purple, "۰٫۱"))
    for (lr, c, l) in lrs {
      let pts = range(0, 101).map(i => { let p = i / 100; let o = p / calc.max(1 - p, 0.0001) * lr; let q = if i == 100 { 1 } else { o / (1 + o) }; (ox + p * S, oy - q * S) })
      poly(pts, s: (if lr == 1 { (paint: c, thickness: 0.7pt, dash: "dashed") } else { 1pt + c }))
      let p = 0.5; let o = lr; let q = o / (1 + o)
      if lr > 1 { at(ox + 0.18 * S - 5, oy - (0.18 * lr / (0.82 + 0.18 * lr)) * S - 2.5, text(size: 6pt, weight: "bold", fill: c, "LR " + l)) }
      if lr < 1 { at(ox + 0.8 * S, oy - (0.8 * lr / (0.2 + 0.8 * lr)) * S + 0.5, text(size: 6pt, weight: "bold", fill: c, "LR " + l)) }
    }
    // example: 30% with LR 5 -> 68%
    let px = ox + 0.3 * S; let py = oy - 0.682 * S
    ln(px, oy, px, py, s: (paint: navy, thickness: 0.5pt, dash: "dotted")); ln(ox, py, px, py, s: (paint: navy, thickness: 0.5pt, dash: "dotted"))
    dot(px, py, r: 1, fill: navy)
    at(1, 4, box(width: 28mm, fill: soft, radius: 3pt, inset: 3pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 6.3pt, weight: "bold", "مثال:"), text(size: 6pt, "پیش از یافته ۳۰٪"), text(size: 6pt, "یافته با LR ۵"), text(size: 6pt, "بعد از یافته حدود ۶۸٪"))))
    at(1, 30, box(width: 28mm, fill: rgb("#fbe9e7"), radius: 3pt, inset: 3pt, text(size: 5.9pt)[در دو انتها (نزدیک ۰ یا ۱۰۰٪) منحنی‌ها به هم نزدیک اند: یک یافته تنها، مریض کم‌خطر را پرخطر نمی‌سازد.]))
  }),
)
