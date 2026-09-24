#set text(font: ("Vazirmatn",), size: 11pt, lang: "fa", dir: rtl)
#show heading.where(level: 1): it => {
  pagebreak()
  block(breakable: false)[
    #text(fill: rgb("#136f73"), weight: "bold", size: 21pt)[#it]
    #v(0.3em)
    #line(length: 100%, stroke: 1.4pt + rgb("#0f2744"))
  ]
}
= این یک عنوان فصل است
متن آزمایشی.
== عنوان دو
بیشتر متن.
#figure(
  table(columns: (auto,auto),
    stroke: 0.5pt, 
    *ستون یک*, *ستون دو*,
    ۱, ۲,
  ),
)
#block(fill: rgb("#f4f7f7"), inset: 9pt, radius: 3pt, stroke: 0.5pt + rgb("#cfdede"))[
  خط اول الگوریتم
  خط دوم الگوریتم
]
