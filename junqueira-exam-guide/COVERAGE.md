# Source ledger and coverage record

This file records where the manuscript's content came from and what was checked. It supports the book; it is not part of it, and nothing here appears in the reader-facing text.

## Status

The manuscript began as a chapter-by-chapter companion to a published histology textbook and was rewritten, in October 2026, into a standalone text. Page ranges, figure numbers, atlas-plate lists and instructions to consult another book were removed from the manuscript. What remains is the scientific content, checked against the reference below and reorganised as this book's own course. `FINAL_REVIEW_REPORT.md` records the transformation and the verification evidence.

## Reference

Principal reference, used for checking:

> Mescher AL. *Junqueira's Basic Histology: Text and Atlas*. 17th ed. New York: McGraw Hill; 2024. ISBN 978-1-26-493039-5.

Supplied as four PDF parts:

| Part | Drive file ID | Size | Pages | Content |
|---|---|---|---|---|
| `MyDocument_part_1.pdf` | `1-_-nv4rceMlYDCpVApeGO66Tft_STYuE` | 62,340,205 B | 217 | Chapters 1–7 |
| `MyDocument_part_2.pdf` | `1xEJVpUmuU_KEWALtMaFzKy6EtQ_HaXmQ` | 67,849,114 B | 217 | Chapters 8–14 |
| `MyDocument_part_3.pdf` | `1JfkWeqqbjbmid7jMPp1RdvOkNmCfMZlA` | 85,813,411 B | 217 | Chapter 14 tail – Chapter 20 (to the thyroid) |
| `MyDocument_part_4.pdf` | `1fYyB7brkrblwVfGK1oF5596jNp90jAL8` | 49,409,277 B | 216 | Chapter 20 tail, Chapters 21–23, stain appendix |

## What was read

All four parts were text-extracted with `pypdfium2` and read. **Thirty pages across the four files carry no extractable text** (full-page plates and covers): part 1 pages 1–3, 20, 29, 46, 76, 79, 86, 142, 166, 174, 203; part 2 pages 60, 69, 72, 90, 158, 217; part 3 pages 42, 50, 80, 82, 127, 166, 180, 198; part 4 pages 44, 67, 71. No statement in the manuscript depends on a page that could not be read, and nothing in that list was visually described. Those pages were not all reviewed as images, and no claim is made that they were.

## Chapter coverage

Source pages are given for provenance only; the book itself no longer cites them.

| Ch | Title | Source pages |
|---|---|---|
| 1 | Histology & Its Methods of Study | 1–16 |
| 2 | The Cytoplasm | 17–52 |
| 3 | The Nucleus | 53–70 |
| 4 | Epithelial Tissue | 71–95 |
| 5 | Connective Tissue | 96–121 |
| 6 | Adipose Tissue | 122–128 |
| 7 | Cartilage | 129–137 |
| 8 | Bone | 138–160 |
| 9 | Nerve Tissue & the Nervous System | 161–192 |
| 10 | Muscle Tissue | 193–214 |
| 11 | The Circulatory System | 215–236 |
| 12 | Blood | 237–253 |
| 13 | Hemopoiesis | 254–266 |
| 14 | The Immune System & Lymphoid Organs | 267–294 |
| 15 | Digestive Tract | 295–328 |
| 16 | Organs Associated with the Digestive Tract | 329–348 |
| 17 | The Respiratory System | 349–370 |
| 18 | Skin | 371–392 |
| 19 | The Urinary System | 393–412 |
| 20 | Endocrine Glands | 413–438 |
| 21 | The Male Reproductive System | 439–459 |
| 22 | The Female Reproductive System | 460–489 |
| 23 | The Eye & Ear: Special Sense Organs | 490–524 |
| — | Stain appendix | 525–526 |

## Known discrepancies in the reference

1. **The Chapter 22 summary contradicts the chapter's own body text on the two lutein cell populations.** The summary gives estrogen to granulosa-lutein cells and progesterone to theca-lutein cells; the body text and the physiology are the other way round. This book states the correct assignment and flags the reversal as a common error, without attributing it to another publication.
2. **The same summary calls the zona pellucida glycoproteins "ZO proteins"; the body text gives ZP1–ZP3.** This book uses the ZP nomenclature and notes that human ZP includes ZP4.
3. **A Chapter 21 clinical box appears to define oligospermia by ejaculate volume in the opposite sense to the usual definition.** This book gives the sperm-density figure and does not repeat the volume claim.

## Verification: what was done, and what it does not cover

- Every numeric value in the manuscript was searched for in the extracted reference text. Values that could not be found were deleted or qualified, with one exception: the statement that nucleosomal DNA makes about 1.65 turns around the histone octamer, a standard structural fact not stated in the reference, which is given as approximate. A text search is not proof of accuracy: it establishes that a number is consistent with the reference, not that the surrounding explanation is right.
- Structural descriptions were compared with the reference chapter by chapter. Mechanisms and clinical correlations were reasoned through rather than checked against a second text.
- The 100 questions were checked for a single correct answer and an explanation consistent with the chapter text; key distribution is 25/25/25/25.
- **Not done:** independent expert or medical review; systematic reading of all 142 reference pages as images; EPUBCheck (no Java environment); rendering of the DOCX or HTML in Word or a browser; any legal clearance of copyright.

## Limitations

- **No images.** The book describes appearances in words. Recognition cannot be certified from a description, and no claim is made that a reader who has not used a microscope will recognise a slide.
- **Thirty reference pages had no text layer**, as listed above.
- **Ranges differ by method, fixation and observer.** Where standard accounts differ, the text gives a range or states which value it uses.
- **The book is not a clinical manual.** Clinical notes are for orientation.
