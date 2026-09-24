#import "lib.typ": *
#let which = sys.inputs.at("fig", default: "heart-areas")
#set page(width: auto, height: auto, margin: 3mm, fill: white)
#set text(font: "Vazirmatn", size: 7pt, fill: navy, lang: "fa", dir: rtl)
#import "parts/ch06.typ": figs as f06
#import "parts/ch08.typ": figs as f08
#import "parts/ch09.typ": figs as f09
#import "parts/ch11.typ": figs as f11
#let figs = f06 + f08 + f09 + f11
#figs.at(which)
