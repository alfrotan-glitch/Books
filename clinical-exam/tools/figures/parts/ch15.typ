#import "../lib.typ": *
#let figs = (
  "neck-nodes": {
    let head = canvas(56, 62, {
      // head profile facing right
      poly(((14, 28), (10, 18), (13, 8), (22, 3), (33, 3), (41, 8), (44, 16), (47, 22), (45, 24), (46, 28), (44, 31), (44, 35), (38, 38), (32, 38), (29, 36)),
        s: 0.7pt + navy, fill: skin, closed: false)
      poly(((14, 28), (16, 36), (18, 52), (8, 58), (54, 58), (40, 50), (38, 38)), s: 0.7pt + navy, fill: skin, closed: false)
      // ear
      at(22, 17, ellipse(width: 4.5mm, height: 7mm, stroke: 0.6pt + navy, fill: skin))
      // SCM
      poly(((24, 26), (29, 38), (35, 50), (38, 56)), s: (paint: rgb("#e2b8a8"), thickness: 3.2mm, cap: "round"))
      // clavicle
      poly(((20, 56), (46, 55)), s: 1.2pt + grey)
      // jaw line
      poly(((29, 36), (27, 30), (26, 26)), s: 0.5pt + grey)
      let n(x, y, k, c: teal) = { dot(x, y, r: 1.9, fill: c); cl(x, y + 0.2, str(k), w: 4, size: 6pt, fill: white, weight: "bold", dir: ltr) }
      n(40, 38, 1); n(33, 35, 2); n(28, 19, 3); n(18, 22, 4); n(12, 29, 5)
      n(33, 45, 6); n(24, 44, 7); n(36, 52.5, 8, c: red)
    })
    let items = ("زیر چانه", "زیر فک", "جلوی گوش", "پشت گوش", "پشت سر", "زنجیر قدامی (جلوی عضله)", "زنجیر خلفی (پشت عضله)", "بالای ترقوه")
    grid(columns: (58mm, 36mm), column-gutter: 2mm, align: horizon, head,
      box(width: 36mm, fill: soft, radius: 3pt, inset: 4pt, stack(dir: ttb, spacing: 2mm,
        text(size: 7pt, weight: "bold", "ترتیب لمس"),
        ..items.enumerate().map(((i, t)) => text(size: 6.5pt, fill: if i == 7 { red } else { navy })[#str(i + 1). #t]),
        text(size: 6pt, fill: red)[عقده بالای ترقوه چپ: به سرطان بطن یا صدر فکر کنید.])))
  },

  "breast-palp": canvas(92, 56, {
    // breast outline
    at(22, 8, circle(radius: 20mm, fill: skin, stroke: 0.7pt + navy))
    poly(((56, 20), (66, 12), (72, 8)), s: (paint: skin, thickness: 7mm, cap: "round"))
    poly(((56, 20), (66, 12), (72, 8)), s: (paint: navy, thickness: 0.6pt, dash: "dashed"))
    at(40, 26, circle(radius: 2.2mm, fill: rgb("#c99a86")))
    // vertical strips
    let xs = range(0, 9).map(i => 23 + i * 4.3)
    let pts = ()
    for (i, x) in xs.enumerate() {
      let top = 28 - calc.sqrt(calc.max(0, 400 - calc.pow(x - 42, 2))) + 1.5
      let bot = 28 + calc.sqrt(calc.max(0, 400 - calc.pow(x - 42, 2))) - 1.5
      if calc.rem(i, 2) == 0 { pts.push((x, bot)); pts.push((x, top)) } else { pts.push((x, top)); pts.push((x, bot)) }
    }
    poly(pts, s: 0.8pt + teal)
    arrow(pts.at(pts.len() - 2).at(0), pts.at(pts.len() - 2).at(1), pts.last().at(0), pts.last().at(1), c: teal)
    cl(72, 3, "دنباله بغلی", w: 20, size: 6.5pt, fill: red)
    at(2, 2, box(width: 20mm, fill: soft, radius: 3pt, inset: 3pt, stack(dir: ttb, spacing: 1.5mm,
      text(size: 6.5pt, weight: "bold", "خطوط عمودی"),
      text(size: 6pt, "از ترقوه تا زیر ثدیه؛ از وسط قص تا خط بغل"),
      text(size: 6pt, "سه درجه فشار در هر نقطه"))))
  }),
)
