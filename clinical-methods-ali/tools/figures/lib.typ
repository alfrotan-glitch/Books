// Shared drawing helpers for book figures (compiled standalone to SVG/PNG).
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
