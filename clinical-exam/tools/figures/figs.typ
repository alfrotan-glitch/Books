#import "lib.typ": *
#let which = sys.inputs.at("fig", default: "heart-areas")
#set page(width: auto, height: auto, margin: 3mm, fill: white)
#set text(font: "Vazirmatn", size: 7pt, fill: navy, lang: "fa", dir: rtl)
#import "parts/ch06.typ": figs as f06
#import "parts/ch08.typ": figs as f08
#import "parts/ch09.typ": figs as f09
#import "parts/ch11.typ": figs as f11
#import "parts/ch14.typ": figs as f14
#import "parts/ch15.typ": figs as f15
#import "parts/ch16.typ": figs as f16
#import "parts/ch17.typ": figs as f17
#import "parts/ch19.typ": figs as f19
#import "parts/ch21.typ": figs as f21
#import "parts/ch23.typ": figs as f23
#import "parts/ch24.typ": figs as f24
#import "parts/ch27.typ": figs as f27
#import "parts/ch25.typ": figs as f25
#import "parts/ch01.typ": figs as f01
#import "parts/ch02.typ": figs as f02
#import "parts/ch03.typ": figs as f03
#import "parts/ch04.typ": figs as f04
#import "parts/ch07.typ": figs as f07
#import "parts/ch12.typ": figs as f12
#import "parts/ch22.typ": figs as f22
#import "parts/ch26.typ": figs as f26
#import "parts/ch10.typ": figs as f10
#import "parts/ch18.typ": figs as f18
#import "parts/ch05.typ": figs as f05
#import "parts/ch13.typ": figs as f13
#import "parts/ch20.typ": figs as f20
#let figs = f05 + f13 + f20 + f10 + f18 + f01 + f02 + f03 + f04 + f07 + f12 + f22 + f26 + f25 + f19 + f21 + f23 + f24 + f27 + f06 + f08 + f09 + f11 + f14 + f15 + f16 + f17
#figs.at(which)
