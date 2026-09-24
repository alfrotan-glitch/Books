// Shared drawing helpers for book figures (compiled standalone to SVG/PNG).
#let grey = rgb("#8a8f98")
#let skin = rgb("#fbeee6")
#let red2 = rgb("#c2571a")
#let purple = rgb("#5b4a9e")
#let navy  = rgb("#0f2744")
#let teal  = rgb("#136f73")
#let gold  = rgb("#b8913a")
#let soft  = rgb("#eef5f5")
#let red   = rgb("#b3261e")
#let pink  = rgb("#eea7a7")
#let pinkl = rgb("#f9dcdc")

#let fa(body, size: 8pt, fill: navy, weight: "regular") = text(lang: "fa", dir: rtl, size: size, fill: fill, weight: weight, body)
#let en(body, size: 7.5pt, fill: navy, weight: "regular") = text(lang: "en", dir: ltr, size: size, fill: fill, weight: weight, body)

// ECG strip on standard paper. pts in mm (x right, y up), baseline at y0 (mm from top).
#let ecg(w, h, pts, y0: none, label: none, marks: ()) = {
  let y0 = if y0 == none { h * 0.62 } else { y0 }
  box(width: w * 1mm, height: h * 1mm, clip: true, stroke: 0.4pt + pink, {
    for x in range(0, w + 1) {
      place(line(start: (x * 1mm, 0mm), end: (x * 1mm, h * 1mm),
        stroke: if calc.rem(x, 5) == 0 { 0.45pt + pink } else { 0.18pt + pinkl }))
    }
    for y in range(0, h + 1) {
      place(line(start: (0mm, y * 1mm), end: (w * 1mm, y * 1mm),
        stroke: if calc.rem(y, 5) == 0 { 0.45pt + pink } else { 0.18pt + pinkl }))
    }
    let P = pts.map(p => (p.at(0) * 1mm, (y0 - p.at(1)) * 1mm))
    place(curve(stroke: (paint: black, thickness: 0.85pt, join: "round"),
      curve.move(P.at(0)), ..P.slice(1).map(p => curve.line(p))))
    for m in marks {
      // m = (x_mm, y_mm_above_baseline, text, color)
      place(dx: m.at(0) * 1mm - 3mm, dy: (y0 - m.at(1)) * 1mm - 3mm,
        box(width: 6mm, height: 4mm, align(center + horizon,
          text(size: 7pt, weight: "bold", fill: m.at(3), lang: "en", m.at(2)))))
    }
    if label != none {
      place(top + left, dx: 1.2mm, dy: 1mm,
        box(fill: white, inset: (x: 2pt, y: 1pt), radius: 1pt,
          text(size: 7.5pt, weight: "bold", fill: navy, lang: "en", label)))
    }
  })
}

#let caption-strip(body) = align(center, block(inset: (top: 2pt), body))

// Horizontal bracket with label under a strip (x in mm from strip left)
#let bracket(x1, x2, lbl, dy: 0mm, color: teal) = place(dx: x1 * 1mm, dy: dy, {
  let w = (x2 - x1) * 1mm
  place(line(start: (0mm, 0mm), end: (0mm, 2mm), stroke: 0.7pt + color))
  place(line(start: (w, 0mm), end: (w, 2mm), stroke: 0.7pt + color))
  place(line(start: (0mm, 1mm), end: (w, 1mm), stroke: 0.7pt + color))
  place(dy: 2.3mm, box(width: w, align(center, text(size: 6.5pt, fill: color, weight: "bold", lbl))))
})

// Mind-map node
#let node(body, fill: soft, stroke: teal, size: 7.5pt, w: auto, weight: "regular", tc: navy) = box(
  fill: fill, stroke: 0.7pt + stroke, radius: 4pt, inset: (x: 5pt, y: 3.5pt), width: w,
  align(center, text(lang: "fa", dir: rtl, size: size, fill: tc, weight: weight, body)))

// ---- coordinate helpers (mm, origin top-left) ----
#let at(x, y, body) = place(top + left, dx: x * 1mm, dy: y * 1mm, body)
#let ln(x1, y1, x2, y2, s: 0.6pt + navy) = place(top + left, line(start: (x1 * 1mm, y1 * 1mm), end: (x2 * 1mm, y2 * 1mm), stroke: s))
#let poly(pts, s: 0.8pt + navy, fill: none, closed: false) = place(top + left, curve(stroke: s, fill: fill,
  curve.move((pts.at(0).at(0) * 1mm, pts.at(0).at(1) * 1mm)),
  ..pts.slice(1).map(p => curve.line((p.at(0) * 1mm, p.at(1) * 1mm))),
  ..if closed { (curve.close(),) } else { () }))
// label centred on (x,y), width w mm
#let cl(x, y, body, w: 30, size: 7pt, fill: navy, weight: "regular", dir: rtl) = place(top + left, dx: (x - w / 2) * 1mm, dy: y * 1mm - size * 0.7,
  box(width: w * 1mm, align(center, text(size: size, fill: fill, weight: weight, dir: dir, body))))
#let dot(x, y, r: 1.4, fill: teal) = place(top + left, dx: (x - r) * 1mm, dy: (y - r) * 1mm, circle(radius: r * 1mm, fill: fill))
#let canvas(w, h, body) = box(width: w * 1mm, height: h * 1mm, body)
#let fn(x) = if type(x) == str { x } else { str(x) }

// thick outlined limb segments
#let limb(pts, w: 4.5) = { poly(pts, s: (paint: navy, thickness: (w + 0.6) * 1mm, cap: "round", join: "round")); }
#let limbf(pts, w: 4.5) = { poly(pts, s: (paint: skin, thickness: w * 1mm, cap: "round", join: "round")); }
#let arrow(x1, y1, x2, y2, c: red, w: 0.9pt, head: 1.6) = {
  ln(x1, y1, x2, y2, s: w + c)
  let dx = x2 - x1; let dy = y2 - y1; let L = calc.sqrt(dx * dx + dy * dy)
  let ux = dx / L; let uy = dy / L
  poly(((x2 - head * ux + head * 0.55 * uy, y2 - head * uy - head * 0.55 * ux), (x2, y2), (x2 - head * ux - head * 0.55 * uy, y2 - head * uy + head * 0.55 * ux)), s: none, fill: c, closed: true)
}
// front mannequin centred at cx, top at y0 (height ~ 86 mm)
#let mannequin(cx, y0: 0) = {
  let P(x, y) = (cx + x, y0 + y)
  let arms = ((P(-8, 17), P(-13, 32), P(-16, 46)), (P(8, 17), P(13, 32), P(16, 46)))
  let legs = ((P(-5, 44), P(-6, 66), P(-6, 84)), (P(5, 44), P(6, 66), P(6, 84)))
  for a in arms + legs { limb(a, w: if a.at(0).at(1) > y0 + 30 { 6 } else { 4.2 }) }
  for a in arms + legs { limbf(a, w: if a.at(0).at(1) > y0 + 30 { 6 } else { 4.2 }) }
  // hands (palms forward, thumbs lateral)
  for sgn in (-1, 1) {
    let h = P(sgn * 16.6, 49)
    at(h.at(0) - 2.2, h.at(1) - 2.2, circle(radius: 2.4mm, fill: skin, stroke: 0.5pt + navy))
    poly((P(sgn * 18.2, 48), P(sgn * 20, 50.5)), s: (paint: navy, thickness: 1.3mm, cap: "round"))
    poly((P(sgn * 18.2, 48), P(sgn * 20, 50.5)), s: (paint: skin, thickness: 0.8mm, cap: "round"))
    for (i, fx) in ((0, 18.2), (1, 16.6), (2, 15.0)).map(((i, v)) => (i, v)) {
      poly((P(sgn * fx, 51), P(sgn * fx, 54)), s: (paint: navy, thickness: 1.1mm, cap: "round"))
      poly((P(sgn * fx, 51), P(sgn * fx, 54)), s: (paint: skin, thickness: 0.65mm, cap: "round"))
    }
  }
  // feet
  for sgn in (-1, 1) { let f = P(sgn * 7.5, 86); at(f.at(0) - 3, f.at(1) - 1.6, ellipse(width: 6mm, height: 3.2mm, fill: skin, stroke: 0.5pt + navy)) }
  // torso + neck + head
  poly((P(-2, 11), P(2, 11), P(2, 16), P(-2, 16)), s: 0.5pt + navy, fill: skin, closed: true)
  poly((P(-9, 15), P(9, 15), P(10, 30), P(8, 46), P(-8, 46), P(-10, 30)), s: 0.6pt + navy, fill: skin, closed: true)
  at(cx - 5.5, y0 + 1, circle(radius: 5.5mm, fill: skin, stroke: 0.6pt + navy))
  dot(cx, y0 + 36, r: 0.5, fill: navy)
  for sgn in (-1, 1) { dot(cx + sgn * 4.5, y0 + 24, r: 0.5, fill: navy) }
}
