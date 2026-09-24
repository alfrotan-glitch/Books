// Vector cover artwork (resolution-independent). Front panel incl. bleed: 151 x 216 mm.
#let navy = rgb("#0f2744"); #let teal = rgb("#136f73"); #let gold = rgb("#c9a45a")
#let goldt = gold.transparentize(35%)
#let m(x) = x * 1mm

#let star-pts(cx, cy, r1, r2) = range(16).map(i => {
  let ang = i * 22.5deg
  let r = if calc.rem(i, 2) == 0 { r1 } else { r2 }
  (cx + r * calc.cos(ang), cy + r * calc.sin(ang))
})
#let star-tile = tiling(size: (9mm, 9mm))[
  #place(top + left, polygon(stroke: 0.35pt + goldt, fill: none, ..star-pts(4.5mm, 4.5mm, 3.6mm, 2.1mm)))
  #place(top + left, dx: 3.1mm, dy: 3.1mm, rect(width: 2.8mm, height: 2.8mm, stroke: 0.25pt + goldt))
]

#let ecg(x0, x1, y, amp, col, w) = {
  // one beat = 34 mm
  let beat = 34
  let cmds = (curve.move((m(x0), m(y))),)
  let x = x0
  while x < x1 {
    cmds += (
      curve.line((m(x + 4), m(y))),
      curve.cubic((m(x + 5), m(y - amp * 0.12)), (m(x + 7), m(y - amp * 0.12)), (m(x + 8), m(y))),   // P
      curve.line((m(x + 10), m(y))),
      curve.line((m(x + 10.8), m(y + amp * 0.1))),                                                    // Q
      curve.line((m(x + 12), m(y - amp))),                                                            // R
      curve.line((m(x + 13.2), m(y + amp * 0.28))),                                                   // S
      curve.line((m(x + 14), m(y))),
      curve.line((m(x + 17), m(y))),
      curve.cubic((m(x + 18.5), m(y - amp * 0.3)), (m(x + 21.5), m(y - amp * 0.3)), (m(x + 23), m(y))), // T
      curve.line((m(x + beat), m(y))),
    )
    x += beat
  }
  curve(stroke: (paint: col, thickness: w, join: "round", cap: "round"), ..cmds)
}

#let tube(stroke-w, ..cmds) = {
  place(top + left, curve(stroke: (paint: gold, thickness: stroke-w, cap: "round", join: "round"), ..cmds.pos()))
  place(top + left, curve(stroke: (paint: rgb("#123a55"), thickness: stroke-w * 0.45, cap: "round", join: "round"), ..cmds.pos()))
}

#let cover-art(w: 151, h: 216) = box(width: m(w), height: m(h), clip: true)[
  #place(top + left, rect(width: 100%, height: 100%, fill: gradient.linear(navy, rgb("#0f3d58"), teal, angle: 90deg)))
  // soft glow behind the stethoscope
  #place(top + left, dx: m(20), dy: m(90), circle(radius: m(60), fill: gradient.radial(teal.lighten(18%).transparentize(55%), teal.transparentize(100%))))
  // geometric corner panels
  #place(top + left, polygon(fill: star-tile, stroke: none, (0mm, m(130)), (m(10), m(140)), (m(10), m(203)), (m(60), m(203)), (m(66), m(216)), (0mm, m(216))))
  #place(top + left, polygon(fill: star-tile, stroke: none, (m(w), m(130)), (m(w - 10), m(140)), (m(w - 10), m(203)), (m(w - 60), m(203)), (m(w - 66), m(216)), (m(w), m(216))))
  #for (sw, d, c) in ((0.6pt, 0, gold), (0.3pt, 2, goldt)) {
    place(top + left, curve(stroke: sw + c, curve.move((m(0), m(126 + d))), curve.line((m(12 + d), m(138 + d))), curve.line((m(12 + d), m(201 - d))), curve.line((m(62 - d), m(201 - d))), curve.line((m(68 - d), m(216)))))
    place(top + left, curve(stroke: sw + c, curve.move((m(w), m(126 + d))), curve.line((m(w - 12 - d), m(138 + d))), curve.line((m(w - 12 - d), m(201 - d))), curve.line((m(w - 62 + d), m(201 - d))), curve.line((m(w - 68 + d), m(216)))))
  }
  // ECG trace
  #place(top + left, ecg(0, 30, 172, 18, white.transparentize(10%), 0.9pt))
  #place(top + left, ecg(34, w + 34, 172, 18, gold, 0.9pt))
  // heart (stylised)
  #let hx = 75
  #let hy = 126
  #place(top + left, curve(stroke: 0.7pt + white.transparentize(35%), fill: white.transparentize(90%),
    curve.move((m(hx), m(hy - 5))),
    curve.cubic((m(hx - 3), m(hy - 13)), (m(hx - 14), m(hy - 12)), (m(hx - 13), m(hy - 3))),
    curve.cubic((m(hx - 12), m(hy + 5)), (m(hx - 4), m(hy + 9)), (m(hx), m(hy + 13))),
    curve.cubic((m(hx + 4), m(hy + 9)), (m(hx + 12), m(hy + 5)), (m(hx + 13), m(hy - 3))),
    curve.cubic((m(hx + 14), m(hy - 12)), (m(hx + 3), m(hy - 13)), (m(hx), m(hy - 5))),
    curve.close()))
  #place(top + left, dx: m(hx - 10), dy: m(hy - 8), box(width: m(20), height: m(14), clip: true, place(top + left, ecg(-6, 20, 9, 6, gold.lighten(20%), 0.6pt))))
  // stethoscope: loop, tubing, binaurals, earpieces, chestpiece
  #tube(2.2pt,
    curve.move((m(75.5), m(176))),
    curve.cubic((m(75.5), m(165)), (m(80), m(156)), (m(90), m(146))),
    curve.cubic((m(104), m(130)), (m(99), m(102)), (m(76), m(101))),
    curve.cubic((m(52), m(100)), (m(46), m(128)), (m(58), m(142))),
    curve.cubic((m(66), m(151)), (m(84), m(150)), (m(96), m(138))),
    curve.line((m(112), m(118))))
  #tube(2pt, curve.move((m(112), m(118))), curve.cubic((m(104), m(108)), (m(100), m(96)), (m(104), m(84))))
  #tube(2pt, curve.move((m(112), m(118))), curve.cubic((m(124), m(110)), (m(134), m(100)), (m(131), m(86))))
  #place(top + left, dx: m(101.5), dy: m(80.5), rotate(-20deg, rect(width: m(5), height: m(3), radius: m(1.5), fill: gold)))
  #place(top + left, dx: m(128.5), dy: m(82.5), rotate(15deg, rect(width: m(5), height: m(3), radius: m(1.5), fill: gold)))
  #place(top + left, dx: m(109.6), dy: m(115.6), circle(radius: m(2.4), fill: gold))
  #place(top + left, dx: m(74), dy: m(174), rect(width: m(3), height: m(4), fill: gold))
  #place(top + left, dx: m(75.5 - 8.5), dy: m(185 - 8.5), circle(radius: m(8.5), fill: rgb("#11455c"), stroke: 1.4pt + gold))
  #place(top + left, dx: m(75.5 - 5.5), dy: m(185 - 5.5), circle(radius: m(5.5), stroke: 0.7pt + gold))
  #place(top + left, dx: m(75.5 - 1), dy: m(185 - 1), circle(radius: m(1), fill: gold))
]
