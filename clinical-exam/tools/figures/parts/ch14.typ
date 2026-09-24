#import "../lib.typ": *
#let epi = rgb("#f3d9c9"); #let der = rgb("#fbeee6")
#let skinbar(body) = box(width: 26mm, height: 12mm, {
  at(0, 5, rect(width: 26mm, height: 2mm, fill: epi))
  at(0, 7, rect(width: 26mm, height: 5mm, fill: der))
  ln(0, 5, 26, 5, s: 0.6pt + rgb("#b27a5c"))
  body
})
#let cell(name, en, def, body) = stack(dir: ttb, spacing: 1.4mm, skinbar(body),
  align(center, [#text(size: 7.2pt, weight: "bold", name) #text(size: 6.2pt, fill: grey, "(" + en + ")")]),
  box(width: 26mm, align(center, text(size: 6.2pt, def))))
#let pig = rgb("#8a5a44")
#let figs = (
  "skin-lesions": grid(columns: 3, column-gutter: 5mm, row-gutter: 4mm,
    cell("لکه", "macule", "هموار، کمتر از ۱ سانتی‌متر", at(10, 5, rect(width: 6mm, height: 1.2mm, fill: pig))),
    cell("پچ", "patch", "هموار، بیشتر از ۱ سانتی‌متر", at(3, 5, rect(width: 20mm, height: 1.2mm, fill: pig))),
    cell("دانه", "papule", "برجسته و جامد، کمتر از ۱", at(9.5, 2.2, ellipse(width: 7mm, height: 5.5mm, fill: rgb("#d98f7a"), stroke: 0.5pt + pig))),
    cell("گره", "nodule", "عمیق‌تر، بیشتر از ۱ سانتی‌متر", at(8, 2.5, ellipse(width: 10mm, height: 8.5mm, fill: rgb("#d98f7a"), stroke: 0.5pt + pig))),
    cell("پلاک", "plaque", "پهن و هموار، بیشتر از ۱", at(3, 3, rect(width: 20mm, height: 2.6mm, radius: 1mm, fill: rgb("#d98f7a"), stroke: 0.5pt + pig))),
    cell("کهیر", "wheal", "پندیده و گذرا (ساعت‌ها)", at(5, 2.6, ellipse(width: 16mm, height: 5mm, fill: rgb("#f2b8b0"), stroke: (paint: rgb("#d9776a"), thickness: 0.5pt, dash: "dashed")))),
    cell("آبله کوچک", "vesicle", "مایع صاف، کمتر از ۰٫۵", at(10, 2.4, ellipse(width: 6mm, height: 5mm, fill: rgb("#d8ecf7"), stroke: 0.6pt + rgb("#3d6fa6")))),
    cell("آبله بزرگ", "bulla", "مایع صاف، بیشتر از ۰٫۵", at(6, 0.6, ellipse(width: 14mm, height: 8.5mm, fill: rgb("#d8ecf7"), stroke: 0.6pt + rgb("#3d6fa6")))),
    cell("چرک‌دانه", "pustule", "پُر از چرک", at(10, 2.4, ellipse(width: 6mm, height: 5mm, fill: rgb("#f1e08a"), stroke: 0.6pt + rgb("#b0901c")))),
  ),
)
