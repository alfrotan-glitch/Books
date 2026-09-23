# Editorial change log
| Chapter/location | Classification | Change | Original wording (for scientific/clinical) |
|---|---|---|---|
| Whole book | Design (non-textual) | Book template, cover, front matter, DOCX reference styles, EPUB CSS added. No manuscript wording changed. | — |
| Opening excerpt (design proof only) | Structural | Book title/subtitle headings moved to the cover/title page; blank line added before lists so they render; Persian-digit list markers converted by `tools/normalize_md.py` at build time only (renders in Dari digits). | Original kept in `manuscript/original/opening-excerpt.md` |

## Full-manuscript pass (source: `main:Manuscript`, commit e1ab743, 7,331 lines)

The original is kept verbatim in `manuscript/original/clinical-methods-ali.md`.
Every edit below is produced by `tools/edit_master.py` (reproducible), and the counts come from `build/edit-report.txt`.

| Location | Classification | Change | Original wording |
|---|---|---|---|
| Whole book | Structural | Removed the `<div dir="rtl">` wrapper, the title headings (now on the cover and title page) and «پایان متن» | kept in original |
| ECG chapter | Structural | Numbered «فصل چهاردهم» (its figures were already ۱۴.x) | «# الکتروکاردیوگرافی (ECG)» |
| Normal values | Structural | Moved after ch. 14 as «ضمیمه: اندازه‌های نارمل لابراتواری»; bullet lists turned into 2-column tables | «# اندازه‌های نارمل» |
| Appendix, Bilirubin | Scientific (unit typo) | mg/100mg → mg/100ml | 0.3-1.0 mg/100mg |
| Appendix, Chlorides | Scientific (unit typo) | mEq/ml → mEq/L | 98-106 mEq/ml |
| Appendix, Amylase | Scientific (unit format) | 60-180 units/100ml (Somogyi) | 60-180/100 units/ml |
| Appendix, first "Creatinine" | Scientific (**FLAGGED M2**) | renamed Creatine | Creatinine: 0.2-0.6 mg/100ml |
| Appendix, CSF glucose | Scientific (**FLAGGED M3**) | % → mg% | Glucose: 45-100% |
| Appendix, ESR | Formatting/scientific | split unit text re-joined: mm/hr (Wintrobe) | "up to 5 mm/Hrs/wintrobe" / "up to 15 mm method" |
| Appendix, MCV / MCH | Scientific (unit) | fl (cubic micron) / pg (µµg) | "c. micron" / "micro. Micro. Gm" |
| Ch. 3, BMI | Scientific (formula wording) | «÷ مربع قد (متر²)» | «÷ قد (متر مربع)» |
| Ch. 12, paediatric BP | Language/unit | missing «سیماب» added (4×), digits made Dari | «ملی‌متر ستون است» |
| Ch. 9, LMN/UMN table | Structural (**S4**) | duplicate, self-contradictory row 12 removed; rows renumbered | «۱۲. موجودیت fasciculation و fibrillation نمی‌باشد / می‌باشد.» |
| Ch. 14, fig. 14.25 | Formatting (bidi) | scrambled A/B/C labels reordered | «الف: strain pattern :B ،scooping …» |
| Whole book | Orthography (Afghan Dari) | اصغأ/اصغاء→اصغا (13), توام→توأم (3), خانوادگی→خانواده‌گی (6), ساییدگی→ساییده‌گی (2), هیچگونه→هیچ‌گونه (2), اضافه تر→اضافه‌تر (8), Arabic ي/ة→ی/ه (5) | — |
| Whole book | Terminology (Afghan usage) | اطلاعات→معلومات (1), بیمار→مریض (1) | — |
| Whole book | Typography | ASCII "…"→«…» (14); Dari decimal «٫» (20); 47 «یادداشت» → note boxes; 41 figure refs → placeholder boxes | — |

Iranian-Persian audit: the manuscript is already in a consistent Afghan clinical register
(مریض، داکتر، شفاخانه، معاینه، معلومات، کاهلان، فیصد). Only the two items above were replaced.
Terms like «بررسی» (7×) and «ویژه» (4×) are shared vocabulary and were left as is.

Items needing the author's decision are listed in `AUTHOR-QUERIES.md`.

Raw rule counts:
```
    2  remove GitHub-only RTL <div> wrapper
    1  book title/subtitle headings -> cover & title page (metadata)
    1  remove 'پایان متن' end marker
    1  number ECG chapter as 14
    1  move normal-values section after chapter 14 as an appendix
    1  Bilirubin unit mg/100mg -> mg/100ml
    1  Chlorides unit mEq/ml -> mEq/L
    1  Amylase unit order
    1  duplicate 'Creatinine' 0.2-0.6 -> 'Creatine' (FLAGGED for author)
    1  ESR rows: split unit text re-joined
    1  CSF glucose unit % -> mg% (range FLAGGED for author)
    1  MCH unit
    1  MCV unit
    1  BMI formula wording: divide by height squared
    4  paediatric BP: missing unit word 'سیماب'
    1  figure 14.25 caption: bidi-scrambled labels reordered
    1  LMN/UMN table: drop duplicate/contradictory row 12 (see row 4)
    1  LMN/UMN renumber 13->12
    1  LMN/UMN renumber 13->12 (UMN)
    1  LMN/UMN renumber 14->13
    1  LMN/UMN renumber 14->13 (UMN)
    1  exudate table header bilingual
   13  اصغأ/اصغاء -> اصغا (70 occurrences already use اصغا)
    3  توام -> توأم (majority form)
    2  هیچگونه -> هیچ‌گونه (ZWNJ)
    6  خانوادگی -> خانواده‌گی (Afghan convention, cf. زنده‌گی in MS)
    2  ساییدگی -> ساییده‌گی (consistency)
    8  اضافه تر -> اضافه‌تر (ZWNJ)
    3  Arabic yeh -> Persian yeh
    1  علامة -> علامه
    1  حدقة -> حدقه
    1  اطلاعات -> معلومات (Afghan usage; used 21x in MS)
    1  بیمار -> مریض (Afghan clinical usage)
   14  ASCII quotes -> «guillemets»
   20  Dari decimal separator . -> ٫ between Dari digits
    0  remove space before Dari punctuation
    5  paediatric BP values: Latin -> Dari digits in Dari sentence
   47  'یادداشت' paragraphs -> styled note boxes
   41  figure references -> figure-placeholder boxes (images not supplied)
   68  appendix lab-value list items -> table rows
```
