#import "../lib.typ": *
#let figs = (
  "diabetic-foot": canvas(98, 92, {
    // plantar view of right foot (big toe on the left of the drawing, as seen by the examiner facing the sole)
    let sole = ((24, 26), (30, 24), (36, 25), (40, 30), (41, 40), (39, 52), (37, 64), (38, 76), (33, 86), (24, 88), (16, 84), (14, 74), (16, 62), (15, 50), (12, 38), (13, 30), (18, 26))
    poly(sole, s: 0.8pt + navy, fill: skin, closed: true)
    // toes
    at(11, 13, ellipse(width: 10mm, height: 12mm, fill: skin, stroke: 0.8pt + navy))
    for (x, y, w) in ((22, 14, 6.4), (28.5, 16, 5.8), (34, 18.5, 5.2), (38.6, 22, 4.6)) { at(x, y, ellipse(width: w * 1mm, height: w * 1.25mm, fill: skin, stroke: 0.7pt + navy)) }
    // three test sites
    for (x, y, n) in ((16, 19, "۱"), (18.5, 34, "۲"), (36, 36, "۳")) {
      at(x - 3, y - 3, circle(radius: 3mm, fill: teal))
      cl(x, y + 0.6, text(weight: "bold", n), w: 6, size: 6.5pt, fill: white)
    }
    // callus: avoid
    at(22, 76, ellipse(width: 10mm, height: 7mm, fill: rgb("#e8d9b5"), stroke: (paint: gold, dash: "dashed")))
    cl(27, 93, "", w: 1)
    cl(26, 5, text(weight: "bold", "کف پای راست"), w: 34, size: 7pt)
    // legend
    bx(47, 12, 48, 24, align(right, text(size: 6pt)[*سه نقطه در هر پا (IWGDF)*\ ۱. کف بند آخر شست پا\ ۲. سر استخوان اول کف پا\ ۳. سر استخوان پنجم کف پا]), fill: soft, c: teal)
    bx(47, 39, 48, 34, align(right, text(size: 5.8pt)[*روش*\ • اول روی دست مریض نشان دهید؛ بعد چشم‌ها بسته.\ • عمود بزنید تا تار خم شود؛ حدود ۲ ثانیه.\ • در هر نقطه: دو بار واقعی، یک بار دروغی.\ • «حس می‌کنید؟ کدام پا؟»\ • دو جواب درست از سه = حس محافظتی موجود.]), fill: white, c: navy)
    bx(47, 76, 48, 12, align(right, text(size: 5.8pt, fill: red)[*روی پینه، زخم یا جای جراحت نزنید*؛ در کناره آن امتحان کنید.]), fill: rgb("#fbe9e7"), c: red)
  }),
)
