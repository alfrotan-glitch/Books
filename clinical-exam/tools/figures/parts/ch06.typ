#import "../lib.typ": *
#let pinkf = rgb("#f7dcd8")
#let lbox(x, y, t, s, w: 26, c: teal) = at(x, y, box(width: w * 1mm, fill: white, stroke: 0.5pt + c, radius: 2pt, inset: 3pt,
  align(center, stack(dir: ttb, spacing: 1.6mm, text(size: 7.4pt, weight: "bold", fill: c, t), text(size: 6.7pt, s)))))

#let figs = (
  "heart-areas": canvas(96, 74, {
    let g = 0.5pt + rgb("#b9bec6")
    // torso
    poly(((40, 0), (40, 6), (18, 9), (10, 16), (10, 72)), s: g)
    poly(((56, 0), (56, 6), (78, 9), (86, 16), (86, 72)), s: g)
    // heart silhouette
    poly(((42, 25), (50, 23), (59, 28), (64, 37), (62, 44), (51, 47), (42, 45), (40, 35)), s: 0.5pt + rgb("#d99a93"), fill: pinkf, closed: true)
    // clavicles
    poly(((45.5, 10), (32, 9), (20, 11)), s: 1.2pt + grey)
    poly(((50.5, 10), (64, 9), (76, 11)), s: 1.2pt + grey)
    // ribs
    for n in range(1, 7) {
      let y = 12 + (n - 1) * 6
      poly(((50.5, y), (62, y + 1.5), (74, y + 5)), s: 0.7pt + rgb("#c9ced6"))
      poly(((45.5, y), (34, y + 1.5), (22, y + 5)), s: 0.7pt + rgb("#c9ced6"))
    }
    // sternum
    at(45.5, 10, rect(width: 5mm, height: 38mm, radius: 1.5mm, fill: rgb("#e6e8ec"), stroke: 0.5pt + grey))
    ln(45.5, 18, 50.5, 18, s: 1pt + gold)
    // midclavicular line (patient's left)
    ln(62, 8, 62, 60, s: (paint: grey, thickness: 0.5pt, dash: "dashed"))
    at(63, 56, text(size: 6.2pt, fill: grey, "خط وسط ترقوه"))
    // points
    dot(42.8, 21); dot(53.2, 21); dot(53.2, 36); dot(62, 41.5, fill: red)
    for p in ((42.8, 21, "A"), (53.2, 21, "P"), (53.2, 36, "T"), (62, 41.5, "M")) {
      cl(p.at(0), p.at(1) + 0.3, text(font: "Vazirmatn", p.at(2)), w: 4, size: 6.7pt, fill: white, weight: "bold", dir: ltr)
    }
    // leaders + labels
    ln(41.4, 21, 29, 21, s: 0.5pt + teal); lbox(1, 15, "ساحه ابهری (A)", "مسافه دوم بین‌الضلعی، کنار راست قص", w: 28)
    ln(54.6, 21, 68, 17, s: 0.5pt + teal); lbox(68, 10, "ساحه ریوی (P)", "مسافه دوم، کنار چپ قص", w: 27)
    ln(54.6, 36, 68, 30, s: 0.5pt + teal); lbox(68, 24, "ساحه سه‌شرفه‌ای (T)", "مسافه چهارم و پنجم، کنار چپ قص", w: 27)
    ln(63.4, 42, 68, 46, s: 0.5pt + red); lbox(68, 43, "ساحه مایترل (M)", "ذروه: مسافه پنجم، خط وسط ترقوه", w: 27, c: red)
    ln(45.5, 18, 31, 32, s: 0.5pt + gold); lbox(1, 30, "زاویه قص", "محل ضلع دوم؛ شمارش را از اینجا شروع کنید", w: 30, c: gold)
    cl(22, 70, "راست مریض", w: 20, size: 6.9pt, fill: grey); cl(74, 70, "چپ مریض", w: 20, size: 6.9pt, fill: grey)
  }),

  "jvp-measure": canvas(96, 70, {
    let ox = 30; let oy = 62; let k = 0.7071
    let T(u, v) = (ox + u * k - v * k, oy - u * k - v * k)
    let TP(pts) = pts.map(p => T(p.at(0), p.at(1)))
    // bed
    poly(((2, oy + 2), T(0, -2)), s: 1.4pt + grey); poly((T(0, -2), T(62, -2)), s: 1.4pt + grey)
    // legs
    poly(((3, oy - 9.9), T(0, 14), T(0, 0), (3, oy)), s: 0.6pt + navy, fill: skin, closed: true)
    // torso + neck
    poly(TP(((0, 0), (40, 0), (40, 3), (48, 3), (48, 11), (40, 11), (40, 14), (0, 14))), s: 0.7pt + navy, fill: skin, closed: true)
    let hc = T(56, 7)
    at(hc.at(0) - 8, hc.at(1) - 8, circle(radius: 8mm, stroke: 0.7pt + navy, fill: skin))
    // right atrium (5 cm below sternal angle, scale 1.6 mm per cm)
    let S = T(34, 14)
    at(S.at(0) - 3.2, S.at(1) + 8 - 3.2, circle(radius: 3.2mm, fill: rgb("#e7b3ad"), stroke: 0.5pt + red))
    // jugular vein column
    poly(TP(((36, 10.5), (39, 10.2), (42, 9.8), (45.2, 9.5))), s: 2.4pt + teal)
    let J = T(45.2, 9.5)
    // references
    ln(S.at(0), S.at(1), 90, S.at(1), s: (paint: gold, thickness: 0.6pt, dash: "dashed"))
    ln(J.at(0), J.at(1), 90, J.at(1), s: (paint: teal, thickness: 0.6pt, dash: "dashed"))
    ln(88, J.at(1) + 0.6, 88, S.at(1) - 0.6, s: 0.8pt + teal)
    poly(((87.2, J.at(1) + 1.6), (88, J.at(1) + 0.4), (88.8, J.at(1) + 1.6)), s: 0.8pt + teal)
    poly(((87.2, S.at(1) - 1.6), (88, S.at(1) - 0.4), (88.8, S.at(1) - 1.6)), s: 0.8pt + teal)
    ln(S.at(0), S.at(1) + 0.8, S.at(0), S.at(1) + 4.6, s: 0.7pt + red)
    dot(S.at(0), S.at(1), r: 1.2, fill: gold)
    // labels
    ln(S.at(0) - 1, S.at(1) - 1, 20, 22, s: 0.4pt + gold)
    at(2, 16, box(width: 26mm, fill: white, stroke: 0.5pt + gold, radius: 2pt, inset: 3pt, align(center, text(size: 6.9pt, fill: gold, weight: "bold", "زاویه قص"))))
    ln(S.at(0) - 3.4, S.at(1) + 8, 20, 44, s: 0.4pt + red)
    at(2, 40, box(width: 30mm, fill: white, stroke: 0.5pt + red, radius: 2pt, inset: 3pt, align(center, stack(dir: ttb, spacing: 1.4mm,
      text(size: 6.9pt, fill: red, weight: "bold", "اذین راست"), text(size: 6.5pt, "حدود ۵ سانتی‌متر پایین‌تر از زاویه قص")))))
    ln(J.at(0), J.at(1) - 1, 48, 8, s: 0.4pt + teal)
    at(2, 2, box(width: 46mm, fill: white, stroke: 0.5pt + teal, radius: 2pt, inset: 3pt, align(center, stack(dir: ttb, spacing: 1.4mm,
      text(size: 6.9pt, fill: teal, weight: "bold", "بلندترین نقطه نبضان ورید وداجی داخلی"), text(size: 6.5pt, "فاصله عمودی آن از زاویه قص = JVP")))))
    at(64, 44, box(width: 30mm, fill: soft, radius: 3pt, inset: 4pt, align(center, stack(dir: ttb, spacing: 1.6mm,
      text(size: 6.9pt, weight: "bold", "نارمل: ۳ سانتی‌متر یا کمتر"), text(size: 6.7pt, "فشار ورید مرکزی ≈ JVP + ۵"), text(size: 6.7pt, "(سانتی‌متر آب)")))))
    at(ox + 4, oy - 1, text(size: 7.4pt, weight: "bold", fill: grey, "۴۵°"))
  }),

  "jvp-wave": canvas(96, 66, {
    // two cycles, 0.8 s each, x scale 50 mm per cycle starting x=6
    let x0 = 6; let sc = 55
    let gs(t, m, s, a) = a * calc.exp(-calc.pow(t - m, 2) / (2 * s * s))
    let jv(t) = { let u = calc.rem(t, 0.8); gs(u, 0.10, 0.035, 1.0) + gs(u, 0.21, 0.02, 0.45) - gs(u, 0.33, 0.045, 0.75) + gs(u, 0.55, 0.05, 0.85) - gs(u, 0.69, 0.045, 0.65) + gs(u, 0.90, 0.035, 1.0) * 0 }
    let ecgf(t) = { let u = calc.rem(t, 0.8); gs(u, 0.06, 0.02, 0.18) - gs(u, 0.155, 0.006, 0.12) + gs(u, 0.17, 0.008, 1.0) - gs(u, 0.185, 0.007, 0.25) + gs(u, 0.42, 0.04, 0.3) }
    let pts(f, ybase, amp) = range(0, 321).map(i => { let t = i / 200; (x0 + t / 0.8 * sc / 1, ybase - f(t) * amp) })
    at(0, 0, text(size: 6.7pt, fill: grey, "ECG"))
    poly(pts(ecgf, 14, 10), s: 0.7pt + grey)
    // S1 / S2 markers
    for k in (0, 1) {
      let b = x0 + k * sc
      ln(b + 0.19 / 0.8 * sc, 18, b + 0.19 / 0.8 * sc, 50, s: (paint: rgb("#c9ced6"), thickness: 0.4pt, dash: "dotted"))
      ln(b + 0.46 / 0.8 * sc, 18, b + 0.46 / 0.8 * sc, 50, s: (paint: rgb("#c9ced6"), thickness: 0.4pt, dash: "dotted"))
      cl(b + 0.19 / 0.8 * sc, 19.5, "S1", w: 6, size: 6.2pt, fill: grey, dir: ltr)
      cl(b + 0.46 / 0.8 * sc, 19.5, "S2", w: 6, size: 6.2pt, fill: grey, dir: ltr)
    }
    at(0, 26, text(size: 6.7pt, fill: teal, "JVP"))
    poly(pts(jv, 38, 11), s: 1.1pt + teal)
    for (t, l, dy) in ((0.10, "a", -14.2), (0.21, "c", -8), (0.33, "x", 10.5), (0.55, "v", -12.5), (0.69, "y", 9.5)) {
      cl(x0 + t / 0.8 * sc, 38 + dy, text(style: "italic", l), w: 5, size: 8.0pt, weight: "bold", fill: navy, dir: ltr)
    }
    at(2, 50, box(width: 90mm, fill: soft, radius: 3pt, inset: 4pt, grid(columns: (1fr, 1fr), column-gutter: 4mm, row-gutter: 1.6mm,
      text(size: 6.7pt)[*a:* تقلص اذین راست], text(size: 6.7pt)[*c:* بسته شدن دسام سه‌شرفه‌ای],
      text(size: 6.7pt)[*x:* استراحت اذین در سیستول], text(size: 6.7pt)[*v:* پر شدن اذین در سیستول بطین],
      text(size: 6.7pt)[*y:* باز شدن دسام سه‌شرفه‌ای], text(size: 6.7pt, fill: red)[a بزرگ: فشار بلند ریوی؛ v بزرگ: عدم کفایه سه‌شرفه‌ای])))
  }),

  "murmurs": {
    let row(title, sub, body, c: teal) = grid(columns: (58mm, 34mm), column-gutter: 2mm, align: horizon,
      box(width: 58mm, height: 11mm, {
        ln(2, 8, 56, 8, s: 0.4pt + rgb("#c9ced6"))
        for x in (6, 30, 54) { at(x - 0.6, 1.5, rect(width: 1.2mm, height: 6.5mm, fill: navy)) }
        cl(6, 10, "S1", w: 6, size: 5.7pt, fill: grey, dir: ltr); cl(30, 10, "S2", w: 6, size: 5.7pt, fill: grey, dir: ltr); cl(54, 10, "S1", w: 6, size: 5.7pt, fill: grey, dir: ltr)
        body
      }),
      box(width: 34mm, align(right, stack(dir: ttb, spacing: 1.4mm, text(size: 7.4pt, weight: "bold", fill: c, title), text(size: 6.5pt, sub)))))
    let f = rgb("#9fd0cf")
    stack(dir: ttb, spacing: 2.6mm,
      align(center, text(size: 6.9pt, fill: grey)[سیستول: از S1 تا S2 · دیاستول: از S2 تا S1 بعدی]),
      row("آواز سوم و چهارم", "S3 کمی بعد از S2؛ S4 کمی پیش از S1", {
        at(35, 4.5, rect(width: 0.9mm, height: 3.5mm, fill: gold)); cl(35.4, 2.3, "S3", w: 6, size: 5.7pt, fill: gold, dir: ltr)
        at(50, 4.5, rect(width: 0.9mm, height: 3.5mm, fill: gold)); cl(50.4, 2.3, "S4", w: 6, size: 5.7pt, fill: gold, dir: ltr) }, c: gold),
      row("تضیق ابهر", "سیستولی دفعی؛ الماسی شکل", poly(((8, 8), (16, 2.5), (27, 8)), s: 0.5pt + teal, fill: f, closed: true)),
      row("عدم کفایه مایترل", "تمام سیستول؛ یکنواخت", at(6.8, 3.5, rect(width: 22.5mm, height: 4.5mm, fill: f, stroke: 0.5pt + teal))),
      row("عدم کفایه ابهر", "اول دیاستول؛ کاهشی", poly(((30.8, 2.5), (30.8, 8), (46, 8)), s: 0.5pt + teal, fill: f, closed: true)),
      row("تضیق مایترل", "آواز بازشدن (OS)، بعد غرش وسط دیاستول", {
        at(34, 3, rect(width: 0.9mm, height: 5mm, fill: red)); cl(34.4, 1.2, "OS", w: 6, size: 5.7pt, fill: red, dir: ltr)
        poly(((36, 8), (37, 5.8), (39, 6.6), (41, 5.6), (43, 6.6), (45, 5.8), (47, 6.8), (49, 5.2), (51, 4.2), (53.3, 3.2), (53.3, 8)), s: 0.5pt + teal, fill: f, closed: true) }),
    )
  },
)
