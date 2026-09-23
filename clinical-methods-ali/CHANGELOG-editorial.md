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

## Scientific review v2: values cross-checked against current references (Sept 2026)

Classification: **Scientific correction / update**. Sources are listed in `SOURCES.md`.
These changes replace the earlier "flagged, not changed" status of items M1–M13 in `AUTHOR-QUERIES.md`.

| Item | New text (in book) | Original wording |
|---|---|---|
| RR adult 12-20/min | ریت نارمل در کاهلان ۱۲–۲۰ تنفس فی دقیقه | ریت نارمل ۱۴ - ۱۶ تنفس فی دقیقه |
| pulse 50-100 | حدود نارمل آن در کاهلان ۵۰–۱۰۰ فی دقیقه است (رهنمود ۲۰۱۸ ACC/AHA/HRS). | حدود نارمل آن در کاهلان ۵۰-۹۰ فی دقیقه است. |
| bradycardia <50 kept + note | اگر ریت قلب پایین‌تر از ۵۰ فی دقیقه باشد به نام برادی‌کاردیا یاد می‌گردد (رهنمود ۲۰۱۸ ACC/AHA/HRS؛ در بسیاری کتاب‌ها حد پایین‌تر از ۶۰ فی دقیقه ذکر شده است). | اگر ریت قلب پایین‌تر از ۵۰ فی دقیقه باشد به نام برادی‌کاردیا یاد می‌گردد. |
| BP categories | **اندازه‌های نارمل:** فشار خون نارمل در کاهلان کمتر از ۱۲۰/۸۰ ملی‌متر ستون سیماب است. فشار ۱۴۰/۹۰ ملی‌متر ستون سیماب یا بیشتر (در اندازه‌گیری‌های مکرر) فرط فشار خون گفته می‌شود (WHO و ESC)؛ رهنمود ACC/AHA 2017 حد ۱۳۰/۸۰ را به کار می‌برد. | **اندازه‌های نارمل:** در حالت نارمل فشار سیستولیک ۱۰۰-۱۳۹ ملی‌متر ستون سیماب و فشار دیاستولیک ۶۰-۸۹ ملی‌متر ستون سیماب است. |
| axis 59° -> ~+60°, range -30..+90 | سمت محور نارمل قلب به طرف پایین و چپ قرار دارد و به طور اوسط در حدود +۶۰° می‌باشد. حدود نارمل آن از −۳۰° تا +۹۰° است. | سمت محور نارمل قلب به طرف پایین و چپ قرار دارد که 59° می‌گردد. حدود آن برای کاهلان بالاتر از ۴۰ سال تا 0° می‌رسد. |
| axis range | محور اساسی قلب به صورت نارمل در بین −۳۰ درجه و +۹۰ درجه قرار دارد. | محور اساسی قلب به صورت نارمل در بین ۰ درجه و ۹۰ درجه قرار دارد. |
| LAD < -30° | اگر محور قلبی منفی‌تر از −۳۰ درجه باشد، به نام انحراف محور به طرف چپ یاد می‌شود. | اگر محور قلبی کمتر از ۰ درجه باشد، به نام انحراف محور به طرف چپ یاد می‌شود. |
| T amplitude | ارتفاع آن در لیدهای اندام‌ها معمولاً کمتر از ۵ ملی‌متر و در لیدهای صدری کمتر از ۱۰ ملی‌متر می‌باشد. | ارتفاع آن معمولاً بیشتر از ۲ ملی‌متر می‌باشد. |
| PR 0.12-0.20 | مدت نارمل آن ۰.۱۲–۰.۲۰ ثانیه (۳–۵ مربع کوچک) است. | مدت نارمل آن ۰.۲ ثانیه است زمانی که ریت قلبی ۷۰ فی دقیقه باشد. |
| QTc | طول آن نظر به ریت قلبی تغییر می‌کند؛ بناءً QT اصلاح‌شده (QTc) به کار می‌رود که به صورت نارمل در مردها کمتر از ۰.۴۴ و در خانم‌ها کمتر از ۰.۴۶ ثانیه است. | به صورت نارمل ۰.۴۲ ثانیه است. |
| short PR <0.12 | اگر کمتر از ۰.۱۲ ثانیه باشد کوتاه گفته می‌شود. | اگر کمتر از ۰.۱ ثانیه باشد کوتاه گفته می‌شود. |
| flutter atrial rate | ریت اذینی سریع و منظم می‌باشد (۲۵۰–۳۵۰ فی دقیقه، معمولاً حدود ۳۰۰) | ریت اذینی سریع و منظم می‌باشد (۲۰۰-۲۵۰ فی دقیقه) |
| severe MS ≤1.5 cm² | زمانی که مساحت دسام ۱٫۵ سانتی‌متر مربع یا کمتر باشد (رهنمود ۲۰۲۰ ACC/AHA): | زمانی که مساحت دسام کمتر از ۱ سانتی‌متر مربع باشد: |
| severe AS | مساحت دسام ۱ سانتی‌متر مربع یا کمتر یا گرادینت اوسط فشار ۴۰ ملی‌متر ستون سیماب یا بیشتر (رهنمود ۲۰۲۰ ACC/AHA) | مساحت دسام کمتر از ۱ سانتی‌متر مربع یا گرادینت فشار اضافه‌تر از ۵۰ ملی‌متر ستون سیماب |
| exercise test ST ≥1 mm | - سقوط افقی یا نزولی سگمنت ST به اندازه ۱ ملی‌متر یا بیشتر | - سقوط سگمنت ST اضافه تر از ۰.۵ ملی‌متر |
| brain death temp ≥36 | درجه حرارت مرکزی بدن باید ۳۶ درجه سانتی‌گرید یا بیشتر باشد (AAN 2023) | درجه حرارت بدن باید بیشتر از ۳۵ درجه سانتی‌گرید باشد |
| apnea test PaCO2 ≥60 | تنفس خود بخودی زمانی که فشار CO2 شریانی به ۶۰ ملی‌متر ستون سیماب یا بیشتر برسد (AAN 2023). | تنفس خود بخودی زمانی که فشار CO2 بیشتر از ۵۰ ملی‌متر ستون سیماب باشد. |
| pleural aspiration ≤1.5 L | نباید بیشتر از ۱٫۵ لیتر مایع را در یک زمان خارج نماییم (BTS)؛ در صورت درد صدر، سرفه یا عسرت تنفس، بذل باید زودتر متوقف شود. | نباید بیشتر از ۵۰۰ - ۸۰۰ ملی‌لیتر مایع را در یک زمان خارج نماییم. |
| liver span 6-12 cm | ساحه اصمیت کبدی در خط متوسط ترقوی به صورت نارمل ۶–۱۲ سانتی‌متر است. | ساحه اصمیت کبدی ۱۲-۱۵ سانتی‌متر عموداً به طرف سفلی ادامه دارد. |
| P duration <0.12 | مدت آن کمتر از ۰.۱۲ ثانیه | مدت آن تا ۰.۱۰ ثانیه |
| QRS <0.12 | مدت نارمل آن کمتر از ۰.۱۲ ثانیه (کمتر از ۳ مربع کوچک) است | مدت نارمل آن از ۰.۱۱ ثانیه زیاد نمی‌شود |
| LVH aVL ≥11 mm (Sokolow-Lyon) | موجه R در لید aVL ۱۱ mm یا بیشتر | موجه R در لید aVL اضافه تر از ۱۳ mm |
| FHR 110-160 | با Pinard stethoscope آوازهای قلب جنین معمولاً از هفته ۲۰–۲۴ به بعد شنیده می‌شود (با Doppler از هفته ۱۰–۱۲). ریت نارمل آن ۱۱۰–۱۶۰ فی دقیقه است (FIGO). | مقدم‌ترین زمان برای شنیدن آوازهای قلب هفته ۲۴ است. در این زمان ریت آن ۱۶۰-۱۴۰ فی دقیقه می‌باشد تا زمان ولادت به ۱۲۰ پایین می‌آید. |
| ACP | - **Acid phosphatase (prostatic):** 0-3 U/dl | - **Acid phosphatase:** 1-5 K.A. units |
| ALP | - **Alkaline phosphatase:** 30-120 U/L | - **Alkaline phosphatase:** 4-13 K.A. units |
| amylase | - **Amylase:** 30-220 U/L (60-120 Somogyi units/dl) | - **Amylase:** 60-180/100 units/ml |
| Ca | - **Calcium (total):** 9-10.5 mg/100ml (2.25-2.62 mmol/L) | - **Calcium:** 9-11 mg/100ml or 4.5-5.5 mEq/L |
| HCO3 | - **Bicarbonate (HCO₃):** 21-28 mEq/L | - **Carbonate:** 56-78 vol./100ml or 25-35 mEq/L |
| iron | - **Iron (serum):** 50-150 µg/100ml | - **Iron:** 79-196 µg/100ml |
| LDH | - **L.D.H.:** 100-190 U/L | - **L.D.H.:** 200-450 unit/ml |
| lipase | - **Lipase:** 0-160 U/L | - **Lipase:** 200-680 units/ml |
| TP | - **Proteins (total):** 6.4-8.3 gm/100ml | - **Proteins (total):** 6.0-7.8 gm/100ml |
| fibrinogen | - **Fibrinogen:** 0.2-0.4 gm/100ml (200-400 mg/100ml) | - **Fibrinogen:** 0.2-0.4 gm/100ml |
| uric acid | - **Uric acid:** 4-8.5 mg/100ml (men), 2.7-7.3 mg/100ml (women) | - **Uric acid:** 2.5-8 mg/100ml |
| K | - **Potassium:** 3.5-5.0 mEq/L (13.7-19.5 mg/100ml) | - **Potassium:** 15-20 mg/100ml or 3.5-5 mEq/L |
| creatinine | - **Creatinine:** 0.6-1.2 mg/100ml (men), 0.5-1.1 mg/100ml (women) | - **Creatinine:** 0.9-1.7 mg/100ml |
| remove duplicate creatinine line | (removed) | - **Creatinine:** 0.2-0.6 mg/100ml /  |
| FPG | - **Glucose (fasting):** 70-99 mg/100ml | - **Glucose (fasting):** 75-105 mg/100ml |
| cholesterol | - **Cholesterol (total):** < 200 mg/100ml (desirable) | - **Cholesterol:** 150-250 mg/100ml |
| pH | - **pH (arterial):** 7.35-7.45 | - **pH:** 7.38-7.44 |
| AST | - **S.G.O.T. (AST):** 0-35 U/L | - **S.G.O.T. (AST):** 10-40 karmen unit (6-18 i.u./L) |
| B12 | - **Vit B12:** 200-800 pg/ml | - **Vit B12:** 200-600 pg/ml |
| platelets | - **Blood platelets:** 150,000-400,000/c.m.m. | - **Blood platelets:** 250,000-500,000/c.m.m. |
| RBC women | - **RBC (women):** 4.0-5.2 million/c.m.m. | - **RBC (women):** 4.5-5 million/c.m.m. |
| RBC men | - **RBC (men):** 4.5-5.9 million/c.m.m. | - **RBC (men):** 4.5-6.5 million/c.m.m. |
| BT | - **Bleeding time:** 2-9 min (Ivy) | - **Bleeding time:** 2-4 min |
| ESR Westergren | - **E.S.R. (men):** up to 15 mm/hr (Westergren) / - **E.S.R. (women):** up to 20 mm/hr (Westergren) | - **E.S.R. (men):** up to 5 mm/Hrs/wintrobe / - **E.S.R. (women):** up to 15 mm method |
| MCV | - **M.C.V.:** 80-100 fl | - **M.C.V.:** 75-96 c. micron |
| MCH | - **M.C.H.:** 27-32 pg | - **M.C.H.:** 27 micro. Micro. Gm |
| MCHC | - **M.C.H.C.:** 32-36 g/dl | - **M.C.H.C.:** 32-38% |
| CSF glucose | - **Glucose:** 45-80 mg/100ml (≈ 60% of blood glucose) | - **Glucose:** 45-100% |
| semen vol WHO2021 | - **Volume:** ≥ 1.4 ml | - **Volume:** 2-5 ml |
| semen pH | - **pH:** ≥ 7.2 | - **pH:** 7.2-8 |
| semen count | - **Count (concentration):** ≥ 16 million/ml | - **Count:** 60-150 million/ml |
| semen motility | - **Motility (total):** ≥ 42% (progressive ≥ 30%) | - **Motility:** 80% or more are motile |
| semen morphology | - **Morphology (normal forms):** ≥ 4% (strict criteria) | - **Morphology:** 80-90% are normal |

## Figures v2
- 41 chapter-14 figure placeholders were replaced by schematic ECG diagrams drawn for this edition.
- 16 additional teaching figures, mind maps and summary tables were added (chapters 1–7, 9, 10, 12, 13). Each one summarises only content that is already in the text.
- Chapter 5 X-ray list: kept as a "suggested radiographs" list with a note. No real images were added.
- Source code for all figures is in `tools/figures/` (Typst + Python), and they are rebuilt with `python3 tools/figures/render.py`.

## Language & pedagogy pass v1.1 (`tools/style_pass.py`, report: `build/style-report.txt`)
- **Editorial:** 28 long or tangled sentences (over 45 words) were rewritten or split. The meaning is kept.
  - The old/new text of each one is in `tools/style_pass.py` (list `RW`).
- **Editorial:** 136 cases of «موجود می‌باشد / نمی‌باشد / می‌باشند» were changed to «وجود دارد / ندارد / دارند».
- **Editorial:** 34 cases of «فلهذا / بناءً / لذا» were changed to «بنابراین». Also: «بالآخره» → «بالاخره», «اینست» → «این است» and «از باعث» → «از سبب».
- **Editorial:** 11 vague cross-references were changed to explicit chapter numbers.
- **Scientific correction:** in complete heart block, the ventricular rate «۲۰-۶۰» was changed to junctional escape 40–60 with narrow QRS, or ventricular escape 20–40 with wide QRS (standard ECG references).
- **Scientific correction:** tendon-reflex grading «۱ = نارمل، ۲ = تند» was changed to the NINDS scale: 0, 1+, 2+ normal, 3+ brisk, 4+ with clonus.
- **Scientific correction:** SFH «inches = weeks; cm = weeks − 2» was changed to «SFH in cm ≈ gestational weeks ± 2 from 24 weeks» (NICE/ACOG).
- **Scientific/clinical clarification:**
  - Doll's-eye: the text implied that the eyes move with the head in a normal person. It now says the eyes move opposite to the head when the brainstem is intact.
  - The Kernig manoeuvre now specifies the patient's position.
  - The Rinne principle now says AC > BC.
- **Pedagogy:** each of the 14 chapters now has learning objectives, key points and a self-test. The answers are in a new appendix.
  - All of this content is drawn only from the book's own text (`tools/pedagogy/*.md`).
- The five-perspective evaluation and the roadmap to 10/10 are in `EVALUATION.md`.
