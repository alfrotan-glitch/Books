#import "../lib.typ": *
#let hand(joints, title, c) = canvas(40, 56, {
  // right hand, palm view, fingers up; thumb on viewer's right? use dorsal view of right hand: thumb on left
  at(9, 26, rect(width: 22mm, height: 20mm, radius: 3mm, fill: skin, stroke: 0.6pt + navy))
  at(12, 45, rect(width: 16mm, height: 8mm, radius: 2mm, fill: skin, stroke: 0.6pt + navy))
  let fx = (12, 17, 22, 27.5); let fl = (19, 22, 21, 16)
  for (i, x) in fx.enumerate() {
    at(x - 2.2, 26 - fl.at(i), rect(width: 4.4mm, height: (fl.at(i) + 2) * 1mm, radius: 2mm, fill: skin, stroke: 0.6pt + navy))
  }
  // thumb
  poly(((9.5, 40), (4, 33), (3, 27)), s: (paint: navy, thickness: 5mm, cap: "round")); poly(((9.5, 40), (4, 33), (3, 27)), s: (paint: skin, thickness: 4.3mm, cap: "round"))
  let J = (:)
  for (i, x) in fx.enumerate() { let L = fl.at(i); J.insert("mcp" + str(i), (x, 26)); J.insert("pip" + str(i), (x, 26 - L * 0.45)); J.insert("dip" + str(i), (x, 26 - L * 0.8)) }
  J.insert("cmc", (8.5, 41)); J.insert("tmcp", (5, 34)); J.insert("tip", (3.4, 29)); J.insert("wrist", (20, 47))
  for (k, v) in J { dot(v.at(0), v.at(1), r: 0.6, fill: rgb("#c9ced6")) }
  for k in joints { let v = J.at(k); dot(v.at(0), v.at(1), r: 1.6, fill: c) }
  cl(20, 55, text(weight: "bold", title), w: 40, size: 7pt, fill: c)
})
#let figs = (
  "joint-patterns": {
    let ra = ("mcp0", "mcp1", "mcp2", "mcp3", "pip0", "pip1", "pip2", "pip3", "tmcp", "wrist")
    let oa = ("dip0", "dip1", "dip2", "dip3", "pip1", "pip2", "cmc")
    stack(dir: ttb, spacing: 2mm,
      grid(columns: 2, column-gutter: 8mm, hand(ra, "روماتوئید آرتریت", red), hand(oa, "استیوآرتریت", navy)),
      box(width: 88mm, fill: soft, radius: 3pt, inset: 3pt, grid(columns: 2, column-gutter: 4mm,
        text(size: 6.1pt)[*روماتوئید:* مفاصل قاعده انگشتان (MCP)، بندهای میانی (PIP) و مچ؛ متقارن؛ سختی صبحگاهی طولانی. بندهای آخر اکثراً سالم.],
        text(size: 6.1pt)[*استیوآرتریت:* بندهای آخر (DIP)، بندهای میانی و قاعده شست؛ در سنین بالا؛ درد با فعالیت.])))
  },
)
