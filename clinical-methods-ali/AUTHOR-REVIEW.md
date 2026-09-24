# مرور مؤلف ـ فهرست اصلاحات علمی برای امضای نهایی
# Author review — scientific changes for final sign-off

**Book:** «معاینه کلینیکی: از تاریخچه تا تشخیص» — داکتر الله یار فروتن
**Status:** All changes are already applied in `release/`. Each one was checked against the sources in `SOURCES.md`.
This sheet does not block printing. It is the author's record of what changed compared with the original manuscript (`manuscript/original/clinical-methods-ali.md`).

## How to review
Tick each block, or write «اصلاح: …» (correct to …) next to it. Any correction goes into `tools/v14/` as a fix file, then the book is rebuilt.

| # | Block | Where the details are (old → new wording) | Sign-off |
|---|---|---|---|
| 1 | Vital signs and cardiovascular values: RR 12–20, pulse 50–100, bradycardia, BP categories, valve severity | `CHANGELOG-editorial.md` § Scientific review v2 | ☐ |
| 2 | ECG values: axis −30° to +90°, LAD/RAD, PR, QTc, T amplitude, flutter, escape rhythms, blocks | same § + § v1.4 (Ch. 14) | ☐ |
| 3 | Lab appendix: electrolytes, haematology, CSF, semen (WHO 2021) (was AUTHOR-QUERIES M1–M13) | § Scientific review v2 | ☐ |
| 4 | Neurology (Ch. 9): reflex grading, gait, autonomic tests, unconscious patient, brain death (AAN 2023), LP | § v1.4 | ☐ |
| 5 | Obstetrics and gynaecology (Ch. 10–11): parity, landmarks, APH/PROM, FIGO 2018 bleeding, cervical screening (WHO 2021) | § v1.4 | ☐ |
| 6 | Paediatrics (Ch. 12): milestones, fontanelle, BP (AAP 2017), IMCI breathing cut-offs | § v1.4 | ☐ |
| 7 | ENT (Ch. 13): ear anatomy, tuning-fork tests, fistula test, rhinoscopy, epistaxis | § v1.4 | ☐ |
| 8 | Added teaching material (not in the original): objectives, red flags, key points, 15 cases, 15 self-tests, 63 schematic figures, glossary, index | `README.md`, `tools/pedagogy/` | ☐ |
| 9 | Language edits (no change in meaning): about 2,500 edits in total | `CHANGELOG-v1.4-fixes.md`, `build/style-report.txt` | ☐ |
| 10 | Title change: «میتودهای کلینیکی علی» → «معاینه کلینیکی: از تاریخچه تا تشخیص» | `metadata.yaml` | ☐ |

Items knowingly left as in the original: CSF pressure 7–20 cm H₂O (an older convention), acid phosphatase in U/dl, and colour index 0.9.

Signature / date: ____________________
