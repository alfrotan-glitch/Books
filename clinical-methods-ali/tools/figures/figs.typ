#import "lib.typ": *
#let which = sys.inputs.at("fig", default: "ecg-normal")
#set page(width: auto, height: auto, margin: 3mm, fill: white)
#set text(font: "Vazirmatn", size: 8pt, fill: navy)
#let D(name) = json("data/" + name + ".json")

#let strip-fig(name, label: none, w: 150, h: 30, y0: none, marks: ()) = ecg(w, h, D(name), label: label, y0: y0, marks: marks)

#let small(name, lbl, w: 30, h: 26, y0: 16) = stack(dir: ttb, spacing: 2pt,
  ecg(w, h, D(name), y0: y0), align(center, box(width: w * 1mm, fa(lbl, size: 7pt))))

#let figs = (
  // ─────────────── Chapter 14: ECG ───────────────
  "ecg-depol": {
    // cell with + / - charges : resting, depolarising, repolarising
    let cell(title, top, bottom, arrow: none) = stack(dir: ttb, spacing: 3pt,
      box(width: 40mm, height: 16mm, stroke: 0.8pt + teal, radius: 8mm, fill: soft,
        align(center + horizon, stack(dir: ttb, spacing: 2.5mm,
          en(top, size: 9pt, weight: "bold", fill: red), en(bottom, size: 9pt, weight: "bold", fill: navy)))),
      align(center, box(width: 40mm, fa(title, size: 7.5pt, weight: "bold"))))
    grid(columns: 3, column-gutter: 5mm,
      cell("۱. حالت استراحت (پولرایزیشن)", "+ + + + + + +", "− − − − − − −"),
      cell("۲. دیپولرایزیشن (← موج برقی)", "− − − − + + +", "+ + + + − − −"),
      cell("۳. ریپولرایزیشن (بازگشت)", "+ + + − − − −", "− − − + + + +"))
  },
  "ecg-axis": {
    let R = 26mm
    box(width: 74mm, height: 74mm, {
      let c = (37mm, 33mm)
      place(dx: c.at(0) - R, dy: c.at(1) - R, circle(radius: R, stroke: 0.5pt + gray))
      // normal sector -30..+90 (drawn as wedge approx)
      for a in range(-30, 91, step: 3) {
        let r = a * 1deg
        place(line(start: c, end: (c.at(0) + R * calc.cos(r), c.at(1) + R * calc.sin(r)), stroke: 1.2pt + rgb(19,111,115,60)))
      }
      let spoke(deg, lbl) = {
        let r = deg * 1deg
        place(line(start: (c.at(0) - R * calc.cos(r), c.at(1) - R * calc.sin(r)), end: (c.at(0) + R * calc.cos(r), c.at(1) + R * calc.sin(r)), stroke: 0.4pt + gray))
        place(dx: c.at(0) + (R + 5mm) * calc.cos(r) - 5mm, dy: c.at(1) + (R + 5mm) * calc.sin(r) - 2mm,
          box(width: 10mm, align(center, en(lbl, size: 6.5pt))))
      }
      spoke(0, "I 0°"); spoke(60, "II +60°"); spoke(120, "III +120°"); spoke(90, "aVF +90°")
      spoke(-30, "aVL −30°"); spoke(-150, "aVR −150°"); spoke(180, "±180°"); spoke(-90, "−90°")
      // mean axis arrow +60
      place(line(start: c, end: (c.at(0) + R * 0.95 * calc.cos(60deg), c.at(1) + R * 0.95 * calc.sin(60deg)), stroke: 1.6pt + red))
      place(dx: 0mm, dy: 68mm, fa("ساحه سبز: محور نارمل (−۳۰° تا +۹۰°)؛ تیر سرخ: محور اوسط حدود +۶۰°", size: 6.5pt))
    })
  },
  "ecg-einthoven": {
    box(width: 64mm, height: 58mm, {
      let A = (8mm, 8mm); let B = (56mm, 8mm); let C = (32mm, 50mm)
      place(polygon(stroke: 1pt + teal, fill: soft, A, B, C))
      place(dx: 22mm, dy: 1mm, en("Lead I  (RA −  → LA +)", size: 6.5pt, weight: "bold"))
      place(dx: 0mm, dy: 30mm, rotate(-60deg, en("Lead II", size: 6.5pt, weight: "bold")))
      place(dx: 46mm, dy: 30mm, rotate(60deg, en("Lead III", size: 6.5pt, weight: "bold")))
      place(dx: 1mm, dy: 9mm, en("RA", weight: "bold", fill: red)); place(dx: 57mm, dy: 9mm, en("LA", weight: "bold", fill: red))
      place(dx: 29mm, dy: 51mm, en("LL", weight: "bold", fill: red))
      place(dx: 21mm, dy: 22mm, fa("قلب", size: 9pt, weight: "bold", fill: red))
    })
  },
  "ecg-chest": {
    box(width: 78mm, height: 50mm, {
      // simplified chest outline + electrode positions
      place(dx: 10mm, dy: 2mm, rect(width: 58mm, height: 44mm, radius: 14mm, stroke: 0.8pt + gray))
      place(dx: 38.5mm, dy: 2mm, line(length: 34mm, angle: 90deg, stroke: 0.6pt + gray))
      for y in (12, 18, 24, 30) { place(dx: 12mm, dy: y * 1mm, line(length: 54mm, stroke: (paint: gray, thickness: 0.3pt, dash: "dotted"))) }
      let e(x, y, l) = { place(dx: x * 1mm - 2.2mm, dy: y * 1mm - 2.2mm, circle(radius: 2.2mm, fill: teal)); place(dx: x * 1mm - 3mm, dy: y * 1mm + 2.6mm, box(width: 6mm, align(center, en(l, size: 6.5pt, weight: "bold")))) }
      e(35, 21, "V1"); e(42, 21, "V2"); e(46, 27, "V3"); e(50, 30, "V4"); e(57, 30, "V5"); e(63, 30, "V6")
      place(dx: 0mm, dy: 44mm, fa("V1 و V2: مسافه بین‌الضلعی چهارم راست و چپ قص؛ V4: مسافه پنجم خط ترقوی متوسط؛ V3 بین V2 و V4؛ V5 خط ابطی قدامی؛ V6 خط ابطی متوسط", size: 5.8pt))
    })
  },
  "ecg-normal": stack(dir: ttb, spacing: 3pt,
    strip-fig("normal", label: "Lead II — 25 mm/s, 10 mm/mV"),
    fa("ECG نارمل: ریتم جیبی منظم، ریت حدود ۷۵ فی دقیقه (۴ مربع بزرگ بین دو موجه R)", size: 7pt)),
  "ecg-intervals": {
    let pts = D("normal_one")
    box(width: 25mm * 1 + 0mm, height: 0mm)
    box({
      ecg(25, 32, pts, y0: 20, marks: ((6.2, 4, "P", red), (8.9, -2.5, "Q", red), (9.9, 12.5, "R", red), (11, -4, "S", red), (17.5, 5, "T", red)))
      place(dx: 0mm, dy: 25mm, box(width: 25mm, height: 7mm, {
        bracket(4.5, 7.4, "PR")
        bracket(8.6, 11.2, "QRS", dy: 3.4mm, color: red)
      }))
    })
    h(4mm)
    box(width: 58mm, align(right + horizon, stack(dir: ttb, spacing: 3pt,
      fa("اندازه‌های نارمل (کاهلان):", size: 7.5pt, weight: "bold"),
      fa("• موجه P: کمتر از ۰٫۱۲ ثانیه، ارتفاع کمتر از ۲٫۵ ملی‌متر", size: 7pt),
      fa("• PR interval: ۰٫۱۲–۰٫۲۰ ثانیه (۳–۵ مربع کوچک)", size: 7pt),
      fa("• QRS: کمتر از ۰٫۱۲ ثانیه (کمتر از ۳ مربع کوچک)", size: 7pt),
      fa("• QTc: مردها کمتر از ۰٫۴۴، خانم‌ها کمتر از ۰٫۴۶ ثانیه", size: 7pt),
      fa("• موجه T: کمتر از ۵ ملی‌متر در لیدهای اندام‌ها و کمتر از ۱۰ ملی‌متر در لیدهای صدری", size: 7pt))))
  },
  "ecg-paper": {
    box({
      ecg(40, 20, ((0, 0), (0, 0)), y0: 10)
      place(dx: 0mm, dy: 0mm, rect(width: 1mm, height: 1mm, stroke: 0.9pt + red))
      place(dx: 10mm, dy: 5mm, rect(width: 5mm, height: 5mm, stroke: 1.1pt + teal))
    })
    h(4mm)
    box(width: 62mm, align(right + horizon, stack(dir: ttb, spacing: 3pt,
      fa("مربع کوچک (سرخ): ۱ ملی‌متر = ۰٫۰۴ ثانیه = ۰٫۱ ملی‌ولت", size: 7pt),
      fa("مربع بزرگ (سبز): ۵ ملی‌متر = ۰٫۲ ثانیه = ۰٫۵ ملی‌ولت", size: 7pt),
      fa("۵ مربع بزرگ = ۱ ثانیه (سرعت کاغذ ۲۵ ملی‌متر فی ثانیه)", size: 7pt),
      fa("ریت قلبی = ۳۰۰ ÷ تعداد مربعات بزرگ بین دو موجه R", size: 7pt, weight: "bold"))))
  },
  "ecg-ape": strip-fig("atrial_ectopic", label: "Atrial ectopic beat"),
  "ecg-af": strip-fig("af", label: "Atrial fibrillation — no P waves, irregularly irregular RR"),
  "ecg-flutter": strip-fig("flutter", label: "Atrial flutter 4:1 — saw-tooth F waves (~300/min)"),
  "ecg-junctional": strip-fig("junctional", label: "Junctional rhythm — no visible P, rate ~50/min"),
  "ecg-pvc": strip-fig("pvc", label: "Ventricular ectopic (PVC) — early wide QRS, compensatory pause"),
  "ecg-vt": strip-fig("vt", label: "Ventricular tachycardia — regular wide QRS ~180/min"),
  "ecg-vf": strip-fig("vf", label: "Ventricular fibrillation — chaotic, no QRS"),
  "ecg-b1": strip-fig("block1", label: "1st-degree AV block — PR 0.30 s, every P conducted"),
  "ecg-mobitz2": strip-fig("mobitz2", label: "Mobitz II — constant PR, sudden dropped QRS"),
  "ecg-b21": strip-fig("block21", label: "2:1 AV block — every second P not conducted"),
  "ecg-wenck": strip-fig("wenck", label: "Mobitz I (Wenckebach) — PR lengthens, then a dropped QRS"),
  "ecg-chb": strip-fig("chb", label: "Complete (3rd-degree) block — P and QRS independent"),
  "ecg-rbbb": strip-fig("rbbb", w: 75, label: "RBBB (V1): rSR′, QRS ≥ 0.12 s"),
  "ecg-lbbb": strip-fig("lbbb", w: 75, label: "LBBB (V6): broad notched R, QRS ≥ 0.12 s"),
  "ecg-rad": grid(columns: 3, column-gutter: 3mm,
      small("lead_neg", "لید I: منفی"), small("lead_pos", "لید II: مثبت"), small("lead_pos", "لید aVF: مثبت")),
  "ecg-lad": grid(columns: 3, column-gutter: 3mm,
      small("lead_pos", "لید I: مثبت"), small("lead_neg", "لید II: منفی"), small("lead_neg", "لید aVF: منفی")),
  "ecg-axis-quick": table(columns: 4, stroke: 0.5pt + rgb("#9fb8bb"), inset: 5pt,
      fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
      table.header(fa("محور", fill: white, weight: "bold"), fa("لید I", fill: white, weight: "bold"), fa("لید aVF", fill: white, weight: "bold"), fa("حدود", fill: white, weight: "bold")),
      fa("نارمل"), en("+"), en("+"), en("−30° … +90°"),
      fa("انحراف به چپ"), en("+"), en("− (II هم −)"), en("−30° … −90°"),
      fa("انحراف به راست"), en("−"), en("+"), en("+90° … +180°"),
      fa("انحراف شدید"), en("−"), en("−"), en("−90° … ±180°")),
  "ecg-strain": grid(columns: 3, column-gutter: 4mm,
      small("m_scoop", "A: ST ناوه‌مانند (digitalis)"),
      small("m_strain", "B: strain pattern (LVH)"),
      small("m_ischT", "C: T معکوس متناظر (اسکیمیا)")),
  "ecg-rvh": grid(columns: 2, column-gutter: 4mm,
      small("rvh_v1", "V1: موجه R بلند (R > S)، ST↓ و T↓", w: 45), small("normal_one", "V6: موجه S عمیق‌تر", w: 25)),
  "ecg-lvh": grid(columns: 2, column-gutter: 4mm,
      small("lvh_v1", "V1: موجه S عمیق", w: 45, y0: 26, h: 34), small("lvh_v5", "V5: موجه R بلند + strain؛ S(V1) + R(V5) > ۳۵ ملی‌متر", w: 45, y0: 10, h: 34)),
  "ecg-pwaves": grid(columns: 2, column-gutter: 4mm,
      small("p_pulm", "P pulmonale: P بلند و نوک‌تیز (> ۲٫۵ ملی‌متر) در لید II", w: 45),
      small("p_mitr", "P mitrale: P دوکوهانه و عریض (≥ ۰٫۱۲ ثانیه)", w: 45)),
  "ecg-mi-zones": {
    // three concentric zones
    box(width: 60mm, height: 44mm, {
      place(dx: 6mm, dy: 2mm, circle(radius: 20mm, fill: rgb("#dcecf5"), stroke: 0.6pt + teal))
      place(dx: 12mm, dy: 8mm, circle(radius: 14mm, fill: rgb("#f7d9a8"), stroke: 0.6pt + gold))
      place(dx: 18mm, dy: 14mm, circle(radius: 8mm, fill: rgb("#e7a0a0"), stroke: 0.6pt + red))
      place(dx: 19mm, dy: 20.5mm, box(width: 14mm, align(center, fa("نکروز → Q", size: 6pt, weight: "bold"))))
      place(dx: 44mm, dy: 12mm, fa("آسیب (injury) → ST↑", size: 6.5pt))
      place(dx: 44mm, dy: 4mm, fa("اسکیمیا → T↓", size: 6.5pt))
      place(dx: 44mm, dy: 22mm, fa("نکروز → Q پتالوژیک", size: 6.5pt))
    })
  },
  "ecg-mi-evol": grid(columns: 3, column-gutter: 2.5mm, row-gutter: 3mm,
      small("m_normal", "نارمل"), small("m_stemi", "دقایق/ساعات: ST↑"), small("m_q", "ساعات/روزها: Q + ST↑"),
      small("m_tinv", "روزها/هفته‌ها: T معکوس"), small("m_old", "ماه‌ها/سال‌ها: Q دایمی")),
  "ecg-tinv": small("m_ischT", "T معکوس، متناظر و نوک‌تیز در اسکیمیا", w: 40),
  "ecg-ischaemia": grid(columns: 2, column-gutter: 4mm,
      small("m_stdep", "سقوط افقی ST (≥ ۱ ملی‌متر)", w: 35), small("m_ischT", "T معکوس متناظر", w: 35)),
  "ecg-hypok": small("hypoK", "Hypokalemia: T هموار، ST↓، موجه U برجسته", w: 40),
  "ecg-hyperk": small("hyperK", "Hyperkalemia: T بلند و نوک‌تیز، P کوچک، QRS عریض", w: 40),
  "ecg-myx": strip-fig("myx", w: 75, label: "Myxedema: low voltage, bradycardia"),
  "ecg-peric": strip-fig("peric", w: 75, label: "Pericarditis: diffuse concave (saddle) ST ↑"),
  "ecg-dig": small("digoxin", "تأثیر Digitalis: ST ناوه‌مانند (reverse tick)", w: 40),
  "ecg-aneur": small("aneur", "انوریزم بطینی: ST↑ دایمی با موجه Q", w: 40),
  "ecg-q": {
    grid(columns: 2, column-gutter: 4mm,
      small("m_normal", "Q نارمل: کوچک و باریک", w: 30),
      small("m_old", "Q پتالوژیک: ≥ ۰٫۰۴ ثانیه یا ≥ ۲۵٪ R", w: 30))
  },
  "ecg-coronary": {
    box(width: 72mm, height: 56mm, {
      // heart outline
      place(dx: 14mm, dy: 6mm, ellipse(width: 44mm, height: 46mm, fill: rgb("#f6e3e0"), stroke: 0.8pt + red))
      place(dx: 30mm, dy: 0mm, rect(width: 8mm, height: 10mm, fill: rgb("#f6e3e0"), stroke: 0.8pt + red))
      let art(pts, c: red, w: 1.6pt) = place(curve(stroke: (paint: c, thickness: w, cap: "round"), curve.move(pts.at(0)), ..pts.slice(1).map(p => curve.line(p))))
      art(((34mm, 9mm), (26mm, 14mm), (18mm, 24mm), (22mm, 40mm), (32mm, 49mm)))           // RCA
      art(((34mm, 9mm), (40mm, 13mm)))                                                    // LM
      art(((40mm, 13mm), (38mm, 25mm), (36mm, 38mm), (36mm, 50mm)))                        // LAD
      art(((40mm, 13mm), (50mm, 17mm), (55mm, 28mm), (52mm, 38mm)))                        // LCx
      place(dx: 1mm, dy: 20mm, box(width: 16mm, align(right, en("RCA", size: 6.5pt, weight: "bold"))))
      place(dx: 32mm, dy: 30mm, en("LAD", size: 6.5pt, weight: "bold"))
      place(dx: 56mm, dy: 20mm, en("LCx", size: 6.5pt, weight: "bold"))
      place(dx: 42mm, dy: 8mm, en("LM", size: 6.5pt, weight: "bold"))
      place(dx: 0mm, dy: 52mm, fa("LAD: جدار قدامی (V1–V4)؛ LCx: جدار جانبی (I، aVL، V5–V6)؛ RCA: جدار سفلی (II، III، aVF)", size: 5.8pt))
    })
  },
  "ecg-mi-ant": grid(columns: 3, column-gutter: 3mm, small("m_stemi", "V2"), small("m_stemi", "V3"), small("m_q", "V4")),
  "ecg-mi-inf": grid(columns: 3, column-gutter: 3mm, small("m_stemi", "II"), small("m_q", "III"), small("m_stemi", "aVF")),
  "ecg-mi-post": grid(columns: 2, column-gutter: 3mm, small("rvh_v1", "V1: موجه R بلند", w: 34), small("m_stdep", "V2: ST↓ (تصویر آیینه‌ای)", w: 34)),

  // ─────────────── Mind maps / schematics ───────────────
  "map-history": {
    let c = node([*تاریخچه مریض*], fill: navy, stroke: navy, size: 9pt, tc: white)
    let ns = ("معلومات شخصی: اسم، سن، جنس، شغل، آدرس", "شکایات فعلی (به ترتیب زمان)", "تاریخچه مرض فعلی (۳ پاراگراف)",
      "تاریخچه گذشته", "تاریخچه شخصی: شغل، غذا، تنباکو، خواب…", "تاریخچه خانواده‌گی", "تاریخچه اجتماعی", "تاریخچه تداوی/دوایی")
    align(center, stack(dir: ttb, spacing: 4mm, c,
      grid(columns: 2, column-gutter: 3mm, row-gutter: 2.5mm, ..ns.map(n => node(n, w: 50mm, size: 8pt)))))
  },
  "map-exam": {
    align(center, stack(dir: ttb, spacing: 4mm,
      node([*معاینه فزیکی مریض*], fill: navy, stroke: navy, size: 9pt, tc: white),
      grid(columns: 2, column-gutter: 8mm,
        stack(dir: ttb, spacing: 2.5mm, node([*معاینه عمومی*], fill: gold.lighten(60%), stroke: gold, w: 48mm),
          node("منظره عمومی، وضعیت، رفتار", w: 48mm, size: 7pt), node("خسافت، یرقان، سیانوز، کلبنگ، اذیما", w: 48mm, size: 7pt),
          node("عقدات لمفاوی، تایراید، جلد", w: 48mm, size: 7pt), node("علایم حیاتی: نبض، BP، تنفس، حرارت", w: 48mm, size: 7pt)),
        stack(dir: ttb, spacing: 2.5mm, node([*معاینه سیستمیک*], fill: gold.lighten(60%), stroke: gold, w: 48mm),
          node("تفتیش (Inspection)", w: 48mm, size: 7pt), node("جس (Palpation)", w: 48mm, size: 7pt),
          node("قرع (Percussion)", w: 48mm, size: 7pt), node("اصغا (Auscultation)", w: 48mm, size: 7pt)))))
  },
  "map-pain": {
    // SOCRATES-like wheel using the manuscript's own headings
    let items = ("محل", "مدت و دوام", "شروع", "وصف درد", "انتشار", "شدت (۰–۱۰)", "عوامل تشدیدکننده", "عوامل تخفیف‌دهنده", "اعراض مترافقه", "تغییر مکان")
    box(width: 92mm, height: 70mm, {
      let c = (46mm, 35mm)
      for (i, it) in items.enumerate() {
        let a = (i * 36 - 90) * 1deg
        let p = (c.at(0) + 32mm * calc.cos(a), c.at(1) + 26mm * calc.sin(a))
        place(line(start: c, end: p, stroke: 0.6pt + teal))
        place(dx: p.at(0) - 13mm, dy: p.at(1) - 3.2mm, node(it, w: 26mm, size: 6.8pt))
      }
      place(dx: c.at(0) - 11mm, dy: c.at(1) - 4mm, node([*ارزیابی درد*], fill: navy, stroke: navy, tc: white, w: 22mm, size: 8pt))
    })
  },
  "map-resp": {
    align(center, stack(dir: ttb, spacing: 3mm,
      node([*معاینه صدر — ترتیب*], fill: navy, stroke: navy, size: 9pt, tc: white),
      grid(columns: 2, column-gutter: 3mm, row-gutter: 3mm,
        ..(("تفتیش", "شکل و تناظر صدر، حرکات، ریت و نوع تنفس، شزن، ندبات"),
           ("جس", "موقعیت شزن و apex، اتساع صدر، اهتزازات صوتی (TVF)"),
           ("قرع", "resonant / dull / stony dull / hyper-resonant"),
           ("اصغا", "آوازهای تنفسی، آوازهای اضافی، وضاحت صوتی")).map(p => stack(dir: ttb, spacing: 2mm,
             node([*#p.at(0)*], fill: gold.lighten(60%), stroke: gold, w: 44mm), node(p.at(1), w: 44mm, size: 7.5pt)))),
      node("همیشه دو طرف را در نقاط مشابه مقایسه کنید", fill: white, stroke: red, size: 7pt, tc: red)))
  },
  "tbl-resp-signs": table(columns: 6, stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt,
    fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
    ..("حالت", "شزن", "اتساع", "TVF", "قرع", "آواز تنفسی").map(h => fa(h, size: 7pt, fill: white, weight: "bold")),
    fa("Consolidation", size: 7pt), fa("مرکزی", size: 7pt), fa("↓", size: 7pt), fa("↑", size: 7pt), fa("dull", size: 7pt), fa("bronchial", size: 7pt),
    fa("Pleural effusion", size: 7pt), fa("به طرف مقابل", size: 7pt), fa("↓", size: 7pt), fa("↓/معدوم", size: 7pt), fa("stony dull", size: 7pt), fa("↓/معدوم", size: 7pt),
    fa("Pneumothorax", size: 7pt), fa("به طرف مقابل", size: 7pt), fa("↓", size: 7pt), fa("↓", size: 7pt), fa("hyper-resonant", size: 7pt), fa("↓/معدوم", size: 7pt),
    fa("Collapse", size: 7pt), fa("به طرف مصاب", size: 7pt), fa("↓", size: 7pt), fa("↓", size: 7pt), fa("dull", size: 7pt), fa("↓", size: 7pt),
    fa("Fibrosis", size: 7pt), fa("به طرف مصاب", size: 7pt), fa("↓", size: 7pt), fa("↑/نارمل", size: 7pt), fa("dull", size: 7pt), fa("bronchial", size: 7pt),
    fa("COPD / Emphysema", size: 7pt), fa("مرکزی", size: 7pt), fa("↓ دوطرفه", size: 7pt), fa("↓", size: 7pt), fa("hyper-resonant", size: 7pt), fa("vesicular ↓ + wheeze", size: 7pt)),
  "cxr-read": {
    align(center, stack(dir: ttb, spacing: 2.5mm,
      node([*شیمای مطالعه اکسری صدر (PA)*], fill: navy, stroke: navy, tc: white, size: 8.5pt),
      grid(columns: 2, column-gutter: 3mm, row-gutter: 2.5mm,
        ..("۱. کیفیت فلم", "۲. اسکلیت صدر", "۳. وضعیت مریض", "۴. موقعیت شزن", "۵. سایه قلب (CTR < ۰٫۵)", "۶. منصف", "۷. دیافراگم (راست ۲٫۵ cm بلندتر)", "۸. ریه‌ها و پلورا").map(n => node(n, w: 44mm, size: 7.5pt)))))
  },
  "cxr-ctr": {
    box(width: 70mm, height: 52mm, {
      place(dx: 5mm, dy: 3mm, rect(width: 60mm, height: 46mm, radius: 10mm, fill: rgb("#20242a")))
      place(dx: 10mm, dy: 8mm, ellipse(width: 22mm, height: 36mm, fill: rgb("#3b4350")))
      place(dx: 38mm, dy: 8mm, ellipse(width: 22mm, height: 36mm, fill: rgb("#3b4350")))
      place(dx: 26mm, dy: 22mm, ellipse(width: 24mm, height: 22mm, fill: rgb("#d9d9d9")))
      place(dx: 33.5mm, dy: 3mm, rect(width: 3mm, height: 20mm, fill: rgb("#bfbfbf")))
      // measurements
      place(dx: 8mm, dy: 46mm, line(length: 54mm, stroke: 1pt + gold)); place(dx: 26mm, dy: 40mm, line(length: 24mm, stroke: 1pt + red))
      place(dx: 22mm, dy: 47mm, text(size: 6.5pt, fill: gold, weight: "bold", lang: "en")[B: thoracic diameter])
      place(dx: 28mm, dy: 36mm, text(size: 6.5pt, fill: red, weight: "bold", lang: "en")[A: heart])
    })
    h(3mm)
    box(width: 40mm, align(right + horizon, stack(dir: ttb, spacing: 3pt,
      fa("CTR = A ÷ B", size: 8pt, weight: "bold"), fa("نارمل: کمتر از ۰٫۵ (در فلم PA)", size: 7pt), fa("بیشتر از ۰٫۵: کاردیومیگالی", size: 7pt))))
  },
  "map-cvs": {
    align(center, stack(dir: ttb, spacing: 3mm,
      node([*معاینه سیستم قلبی و وعایی*], fill: navy, stroke: navy, size: 9pt, tc: white),
      grid(columns: 2, column-gutter: 3mm, row-gutter: 3mm,
        ..(("نبض", "ریت، ریتم، حجم، وصف، جدار شریان، radio-femoral delay"),
           ("BP و JVP", "BP در هر دو بازو؛ JVP در ۴۵°: نارمل < ۴ cm بالای زاویه قصی"),
           ("Precordium", "تفتیش، جس (apex beat، heave، thrill)، قرع"),
           ("اصغا", "محراق‌های mitral، tricuspid، pulmonary، aortic: S1، S2، S3، S4، مرمرها")).map(p => stack(dir: ttb, spacing: 2mm,
             node([*#p.at(0)*], fill: gold.lighten(60%), stroke: gold, w: 44mm), node(p.at(1), w: 44mm, size: 7.5pt))))))
  },
  "heart-areas": {
    box(width: 64mm, height: 58mm, {
      place(dx: 4mm, dy: 2mm, rect(width: 56mm, height: 52mm, radius: 12mm, stroke: 0.8pt + gray))
      place(dx: 30.5mm, dy: 2mm, rect(width: 3mm, height: 38mm, fill: rgb("#e3e3e3")))
      place(dx: 26mm, dy: 18mm, ellipse(width: 26mm, height: 24mm, fill: rgb("#f6e3e0"), stroke: 0.6pt + red))
      let pt(x, y, l, d) = { place(dx: x * 1mm - 2mm, dy: y * 1mm - 2mm, circle(radius: 2mm, fill: teal)); place(dx: x * 1mm + d * 1mm, dy: y * 1mm - 1.8mm, en(l, size: 6.5pt, weight: "bold")) }
      pt(36, 12, "P (2nd L ICS)", 3); pt(28, 12, "A (2nd R ICS)", -17); pt(29, 36, "T (LLSB)", -13); pt(46, 38, "M (apex)", 3)
      place(dx: 2mm, dy: 55mm, fa("A: ابهر؛ P: ریوی؛ T: ترای‌کسپید؛ M: مایترل (ذروه، مسافه پنجم، خط ترقوی متوسط)", size: 5.8pt))
    })
  },
  "map-gi": {
    box(width: 64mm, height: 58mm, {
      for i in range(4) { place(dx: (8 + i * 16) * 1mm, dy: 4mm, line(length: 48mm, angle: 90deg, stroke: if i == 1 or i == 2 { 0.7pt + teal } else { 0pt + white })) }
      for j in range(4) { place(dx: 8mm, dy: (4 + j * 16) * 1mm, line(length: 48mm, stroke: if j == 1 or j == 2 { 0.7pt + teal } else { 0pt + white })) }
      place(dx: 8mm, dy: 4mm, rect(width: 48mm, height: 48mm, stroke: 0.8pt + navy, radius: 3pt))
      let cell(c, r, t) = place(dx: (8 + c * 16) * 1mm, dy: (4 + r * 16) * 1mm, box(width: 16mm, height: 16mm, align(center + horizon, fa(t, size: 5.8pt))))
      cell(0, 0, "مراق راست"); cell(1, 0, "اپی‌گستر"); cell(2, 0, "مراق چپ")
      cell(0, 1, "قطنی راست"); cell(1, 1, "سروی"); cell(2, 1, "قطنی چپ")
      cell(0, 2, "حرقفی راست"); cell(1, 2, "خثلی (hypogastric)"); cell(2, 2, "حرقفی چپ")
      place(dx: 4mm, dy: 53mm, fa("نُه ناحیه بطن (نمای قدامی، راستِ مریض در سمت چپ تصویر)", size: 6pt))
    })
  },
  "map-neuro": {
    align(center, stack(dir: ttb, spacing: 3mm,
      node([*معاینه سیستم عصبی — ترتیب*], fill: navy, stroke: navy, size: 9pt, tc: white),
      grid(columns: 2, column-gutter: 3mm, row-gutter: 2.5mm,
        ..("۱. سویه شعور (GCS)", "۲. تکلم", "۳. وظایف قشری", "۴. اعصاب قحفی", "۵. اعصاب محیطی", "۶. سیستم حسی", "۷. سیستم حرکی: تون، قدرت، عکسات", "۸. مخیخ", "۹. تغییرات تروفیک", "۱۰. سیستم اوتونوم", "۱۱. علایم تخریش سحایا").map(n => node(n, w: 44mm, size: 7.5pt)))))
  },
  "tbl-umn-lmn": table(columns: 3, stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt,
    fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
    fa("علامه", size: 7pt, fill: white, weight: "bold"), fa("UMN", size: 7pt, fill: white, weight: "bold"), fa("LMN", size: 7pt, fill: white, weight: "bold"),
    fa("تون", size: 7pt), fa("↑ (spasticity)", size: 7pt), fa("↓ (flaccid)", size: 7pt),
    fa("اتروفی", size: 7pt), fa("ندارد/خفیف", size: 7pt), fa("واضح", size: 7pt),
    fa("fasciculation", size: 7pt), fa("ندارد", size: 7pt), fa("موجود", size: 7pt),
    fa("عکسات عمیق", size: 7pt), fa("↑ + clonus", size: 7pt), fa("↓/معدوم", size: 7pt),
    fa("Babinski", size: 7pt), fa("مثبت (extensor)", size: 7pt), fa("منفی (flexor)", size: 7pt),
    fa("توزیع فلج", size: 7pt), fa("گروهی از عضلات/طرف", size: 7pt), fa("عضلات منفرد/عصب", size: 7pt)),
  "gcs": table(columns: 3, stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt,
    fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
    fa("باز کردن چشم (E)", size: 7pt, fill: white, weight: "bold"), fa("عکس‌العمل شفاهی (V)", size: 7pt, fill: white, weight: "bold"), fa("عکس‌العمل حرکی (M)", size: 7pt, fill: white, weight: "bold"),
    fa("۴ خودبخودی", size: 7pt), fa("۵ آگاه (oriented)", size: 7pt), fa("۶ اطاعت از دستور", size: 7pt),
    fa("۳ به صدا", size: 7pt), fa("۴ گیچ (confused)", size: 7pt), fa("۵ تعیین محل درد", size: 7pt),
    fa("۲ به درد", size: 7pt), fa("۳ کلمات نامناسب", size: 7pt), fa("۴ دور کردن از درد", size: 7pt),
    fa("۱ هیچ", size: 7pt), fa("۲ آوازهای بی‌مفهوم", size: 7pt), fa("۳ قبض غیر نارمل", size: 7pt),
    [], fa("۱ هیچ", size: 7pt), fa("۲ بسط غیر نارمل", size: 7pt),
    [], [], fa("۱ هیچ", size: 7pt),
    table.cell(colspan: 3, fa("مجموع: ۳ تا ۱۵؛ ۸ یا کمتر = کومای شدید (نیاز به حفاظت راه هوایی)", size: 7pt))),
  "map-obs": {
    align(center, stack(dir: ttb, spacing: 3mm,
      node([*معاینه ولادی*], fill: navy, stroke: navy, size: 9pt, tc: white),
      grid(columns: 3, column-gutter: 2.5mm,
        ..(("تاریخچه", "G/P، LMP، EDD (قانون Naegele: +۹ ماه +۷ روز)، فکتورهای ریسک"),
           ("معاینه عمومی", "BP، وزن، اذیما، خسافت، ادرار (پروتین)"),
           ("معاینه بطن", "ارتفاع fundus (SFH ≈ هفته حمل)، مانورهای Leopold، FHS ۱۱۰–۱۶۰/دقیقه")).map(p => stack(dir: ttb, spacing: 2mm,
             node([*#p.at(0)*], fill: gold.lighten(60%), stroke: gold, w: 40mm), node(p.at(1), w: 40mm, size: 6.6pt))))))
  },
  "peds-vitals": table(columns: 4, stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt,
    fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
    ..("سن", "نبض (فی دقیقه)", "تنفس (فی دقیقه)", "BP تقریبی (mmHg)").map(h => fa(h, size: 7pt, fill: white, weight: "bold")),
    fa("نوزاد", size: 7pt), en("≈ 140"), en("≈ 40"), en("65/45"),
    fa("۱ ساله", size: 7pt), en("≈ 110"), en("≈ 35 (2 y)"), en("75/50"),
    fa("۳–۴ ساله", size: 7pt), en("≈ 100"), en("25–30"), en("85/60"),
    fa("۸ ساله", size: 7pt), en("≈ 90"), en("≈ 20 (> 5 y)"), en("95/65"),
    fa("۱۰–۱۱ ساله", size: 7pt), en("≈ 80"), en("≈ 20"), en("100/70")),
  "ent-rinne": table(columns: 3, stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt,
    fill: (x, y) => if y == 0 { teal } else if calc.even(y) { soft } else { white },
    ..("حالت", "Rinne (در گوش مصاب)", "Weber").map(h => fa(h, size: 7pt, fill: white, weight: "bold")),
    fa("نارمل", size: 7pt), fa("مثبت (AC > BC)", size: 7pt), fa("در وسط", size: 7pt),
    fa("کری انتقالی (conductive)", size: 7pt), fa("منفی (BC > AC)", size: 7pt), fa("به طرف گوش مصاب", size: 7pt),
    fa("کری حسی‑عصبی (sensorineural)", size: 7pt), fa("مثبت (هر دو کاهش یافته)", size: 7pt), fa("به طرف گوش سالم", size: 7pt)),
  // ─────────────── Algorithms (v1.2) ───────────────
  "alg-abcde": {
    let row(l, t, d, c) = grid(columns: (14mm, 96mm), column-gutter: 2mm,
      box(width: 14mm, height: 13mm, fill: c, radius: 3pt, align(center + horizon, text(size: 15pt, weight: "bold", fill: white, lang: "en", l))),
      box(width: 96mm, height: 13mm, fill: soft, stroke: 0.6pt + c, radius: 3pt, inset: (x: 5pt, y: 3pt),
        align(right + horizon, stack(dir: ttb, spacing: 1.6mm, fa([*#t*], size: 8pt), fa(d, size: 6.8pt)))))
    stack(dir: ttb, spacing: 1.8mm,
      row("A", "Airway — طرق هوایی", "آیا مریض صحبت می‌کند؟ stridor، خرخر، جسم اجنبی؛ باز کردن طرق هوایی", red),
      row("B", "Breathing — تنفس", "ریت تنفس، SpO₂، حرکات صدر، شزن، اصغا؛ اکسیجن در صورت ضرورت", rgb("#c2571a")),
      row("C", "Circulation — دوران", "نبض، فشار خون، capillary refill، اطراف سرد، ادرار؛ مایع وریدی", gold),
      row("D", "Disability — حالت عصبی", "AVPU یا GCS، حدقه‌ها، گلوکوز خون", teal),
      row("E", "Exposure — معاینه کامل بدن", "درجه حرارت، طفح، خونریزی، ترضیض؛ حفظ حرارت و حریم مریض", navy),
      align(center, node("هر مشکل را در همان مرحله تداوی کنید، بعد به مرحله بعدی بروید؛ بعد از هر مداخله دوباره از A شروع کنید", fill: white, stroke: red, tc: red, size: 7pt, w: 112mm)))
  },
  "alg-chestpain": {
    let Q(t) = node(t, fill: gold.lighten(65%), stroke: gold, size: 7pt, w: 50mm)
    let R(t) = node(t, fill: rgb("#fbe9e7"), stroke: red, tc: red, size: 7pt, w: 50mm)
    let N(t) = node(t, size: 7pt, w: 50mm)
    let ar = align(center, text(size: 9pt, fill: teal, "↓"))
    stack(dir: ttb, spacing: 1.5mm,
      align(center, node([*درد صدری*], fill: navy, stroke: navy, tc: white, size: 9pt, w: 50mm)), ar,
      align(center, N("ABCDE + علایم حیاتی + ECG در ۱۰ دقیقه")), ar,
      grid(columns: 2, column-gutter: 4mm, row-gutter: 2mm,
        Q("درد فشاری خلف قص، انتشار به بازو/فک، عرق"), R("Acute coronary syndrome → ECG، troponin"),
        Q("درد ناگهانی پاره‌کننده به پشت؛ تفاوت نبض دو بازو"), R("Aortic dissection"),
        Q("درد پلوریتیک + عسرت تنفس + تکی‌کاردیا؛ DVT"), R("Pulmonary embolism"),
        Q("درد ناگهانی + hyper-resonance یک طرف"), R("Pneumothorax"),
        Q("درد تیز، بهتر در نشستن و خم شدن به پیش؛ rub"), N("Pericarditis → صعود مقعر منتشر ST"),
        Q("سوزش epigastric، مرتبط با غذا"), N("GERD / peptic ulcer"),
        Q("درد موضعی، با فشار دادن جدار صدر تولید می‌شود"), N("درد عضلی‌ـ‌اسکلیتی (بعد از رد علل خطرناک)")))
  },
  "alg-dyspnea": {
    let Q(t) = node(t, fill: gold.lighten(65%), stroke: gold, size: 7pt, w: 50mm)
    let N(t) = node(t, size: 7pt, w: 50mm)
    let ar = align(center, text(size: 9pt, fill: teal, "↓"))
    stack(dir: ttb, spacing: 1.5mm,
      align(center, node([*عسرت تنفس*], fill: navy, stroke: navy, tc: white, size: 9pt, w: 50mm)), ar,
      align(center, N("SpO₂، ریت تنفس، آیا یک جمله کامل گفته می‌تواند؟")), ar,
      grid(columns: 2, column-gutter: 4mm, row-gutter: 2mm,
        Q("ویزینگ، سابقه استما/سگرت"), N("Asthma / COPD"),
        Q("orthopnea، PND، JVP بلند، کریپیتیشن قاعده‌ها، اذیما"), N("عدم کفایه قلب چپ"),
        Q("تب، سرفه با بلغم، dullness و تنفس bronchial"), N("Pneumonia"),
        Q("stony dullness، کاهش آوازهای تنفسی"), N("Pleural effusion"),
        Q("آغاز ناگهانی، hyper-resonance"), N("Pneumothorax"),
        Q("آغاز ناگهانی، صدر پاک، تکی‌کاردیا، ریسک DVT"), N("Pulmonary embolism"),
        Q("خسافت، خستگی، صدر نارمل"), N("انیمی / علل متابولیک (acidosis)")))
  },
  "alg-jaundice": {
    let col(t, c, items) = stack(dir: ttb, spacing: 1.6mm,
      node([*#t*], fill: c.lighten(75%), stroke: c, size: 7.5pt, w: 38mm),
      ..items.map(i => node(i, size: 6.6pt, w: 38mm, fill: white, stroke: c)))
    stack(dir: ttb, spacing: 2mm,
      align(center, node([*یرقان — بیلیروبین سیروم بیشتر از ۲٫۵ mg/dL*], fill: navy, stroke: navy, tc: white, size: 8.5pt, w: 90mm)),
      align(center, text(size: 9pt, fill: teal, "↓   ادرار، مواد غایطه، خارش   ↓")),
      grid(columns: 3, column-gutter: 3mm,
        col("قبل‌الکبدی (همولیتیک)", gold, ("ادرار نارمل (acholuric)", "مواد غایطه نارمل", "خسافت، طحال بزرگ", "بیلیروبین غیر مستقیم ↑")),
        col("کبدی (hepatocellular)", teal, ("ادرار تیره", "مواد غایطه کم‌رنگ یا نارمل", "کبد بزرگ و حساس؛ علایم مرض مزمن کبد", "ALT و AST ↑↑")),
        col("بعدالکبدی (انسدادی)", red, ("ادرار تیره", "مواد غایطه خاکی‌رنگ", "خارش؛ کیسه صفرای قابل جس (Courvoisier)", "ALP و GGT ↑↑"))))
  },
  "alg-weakness": {
    let Q(t) = node(t, fill: gold.lighten(65%), stroke: gold, size: 7pt, w: 50mm)
    let N(t) = node(t, size: 7pt, w: 50mm)
    stack(dir: ttb, spacing: 2mm,
      align(center, node([*ضعف اطراف — محل آفت کجاست؟*], fill: navy, stroke: navy, tc: white, size: 8.5pt, w: 90mm)),
      grid(columns: 2, column-gutter: 4mm, row-gutter: 2mm,
        Q("hemiplegia + اعصاب قحفی همان طرف، اختلالات قشری (aphasia)"), N("قشر دماغ / کپسول داخلی (UMN)"),
        Q("hemiplegia + اعصاب قحفی طرف مقابل (crossed)"), N("ساق دماغ"),
        Q("paraplegia + سویه حسی + اختلال مثانه"), N("نخاع شوکی"),
        Q("ضعف و بی‌حسی در ساحه یک ریشه/عصب؛ عکسه همان سویه کم"), N("ریشه یا عصب محیطی (LMN)"),
        Q("ضعف دیستال دو طرفه، بی‌حسی جوراب‌ـ‌دستکشی، عکسات کم"), N("Polyneuropathy"),
        Q("ضعف با خستگی‌پذیری، ptosis، حسیت نارمل"), N("اتصال عصبی‌ـ‌عضلی (myasthenia)"),
        Q("ضعف پروکسیمال دو طرفه، حسیت و عکسات نارمل"), N("Myopathy")))
  },
  "tbl-news2": { set text(dir: rtl); stack(dir: ttb, spacing: 0pt, table(columns: (27mm, 15mm, 15mm, 20mm, 20mm, 20mm, 16mm, 23mm), stroke: 0.5pt + rgb("#9fb8bb"), inset: 3.5pt, align: center + horizon,
    fill: (x, y) => if y == 0 { navy } else if x == 0 { soft } else { white },
    ..("پارامتر", "۳", "۲", "۱", "۰", "۱", "۲", "۳").map(h => fa(h, size: 7pt, fill: white, weight: "bold")),
    fa("ریت تنفس", size: 6.8pt), en("≤8", size: 6.8pt), en("", size: 6.8pt), en("9–11", size: 6.8pt), en("12–20", size: 6.8pt), en("", size: 6.8pt), en("21–24", size: 6.8pt), en("≥25", size: 6.8pt),
    fa("SpO₂ (مقیاس ۱) ٪", size: 6.8pt), en("≤91", size: 6.8pt), en("92–93", size: 6.8pt), en("94–95", size: 6.8pt), en("≥96", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt),
    fa("اکسیجن اضافی", size: 6.8pt), en("", size: 6.8pt), fa("بلی", size: 6.8pt), en("", size: 6.8pt), fa("نخیر", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt),
    fa("فشار سستولیک", size: 6.8pt), en("≤90", size: 6.8pt), en("91–100", size: 6.8pt), en("101–110", size: 6.8pt), en("111–219", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), en("≥220", size: 6.8pt),
    fa("نبض", size: 6.8pt), en("≤40", size: 6.8pt), en("", size: 6.8pt), en("41–50", size: 6.8pt), en("51–90", size: 6.8pt), en("91–110", size: 6.8pt), en("111–130", size: 6.8pt), en("≥131", size: 6.8pt),
    fa("شعور", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), fa("Alert", size: 6.8pt), en("", size: 6.8pt), en("", size: 6.8pt), en("New C/V/P/U", size: 6.4pt),
    fa("درجه حرارت °C", size: 6.8pt), en("≤35.0", size: 6.8pt), en("", size: 6.8pt), en("35.1–36.0", size: 6.8pt), en("36.1–38.0", size: 6.8pt), en("38.1–39.0", size: 6.8pt), en("≥39.1", size: 6.8pt), en("", size: 6.8pt),
    ), box(width: 156mm, fill: rgb("#fbf6ea"), stroke: 0.5pt + rgb("#9fb8bb"), inset: 4pt, fa("مجموع ۰–۴: خطر کم (نظارت معمول) • یک پارامتر ۳ یا مجموع ۵–۶: خطر متوسط (ارزیابی عاجل داکتر) • مجموع ۷ یا بیشتر: خطر بلند (ارزیابی عاجل تیم حالات عاجل)", size: 6.6pt))) },

)

#figs.at(which)
