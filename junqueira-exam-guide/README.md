# Basic Histology: Smart Study Notes

**One cohesive, illustrated study and teaching book**, following Chapters 1–23 of *Junqueira's Basic Histology: Text & Atlas*, 17th edition (Mescher, 2024). Chapter 24 is rapid review, followed by 100 original multiple-choice practice questions with explanations.

The reader-facing book is generated from one canonical Markdown manuscript. For each chapter it includes a hierarchy mind map, concise quick notes, essential structure–function explanations, tissue-recognition clues, comparison tables, active recall, a worked example and practical identification.

## Content at a glance

- **23 original hierarchical mind maps** and **12 original tissue schematics**, embedded alongside relevant lessons.
- **23 Junqueira-aligned primary chapters**, one rapid-review chapter and **100 original practice MCQs**. Question stems are not official prior Ministry examinations.
- **607 flashcards** generated from the manuscript, with a synchronized 100-question CSV deck in `deliverables/`.
- A study-path label for **Internal Medicine (16 chapters)** and **Surgery (18 chapters)**. These labels are owner-supplied study guidance; confirm against the current official Afghanistan MoPH syllabus.
- Optional links to externally hosted real-slide resources; no third-party microscopy photographs are republished.

## Read the book

All four formats contain the same content:

| Format | Purpose |
|---|---|
| `Basic_Histology_Learning_Text.pdf` | A4, linked table of contents, print and desktop reading |
| `Basic_Histology_Learning_Text.docx` | Editable teaching/printing copy |
| `Basic_Histology_Learning_Text.epub` | Reflowable e-reader and phone copy |
| `Basic_Histology_Learning_Text.html` | Standalone browser reading copy |

The canonical source is in `src/*.md`. **Edit the source rather than only changing generated PDFs or Word files.**

## Build and verification

See the [GitHub Actions publication workflow](https://github.com/alfrotan-glitch/Books/actions/workflows/histology-book.yml) for the latest passing run and reproducible artifacts. **Do not trust static page numbers in documentation**; the generated `publication-manifest.json` records the exact source commit, PDF page count and SHA-256 for each build output.

To run locally with Python, Pandoc, EPUBCheck and the requirements installed:

```bash
python tools/make_study_decks.py
python tools/make_question_bank.py
python build.py
python build_docs.py
python build_epub.py
python tools/validate_study_materials.py
python tools/validate_scientific_corrections.py
python tools/validate_unified_book.py
python tools/validate_mindmaps.py
python tools/validate_mcq_pagination.py
python tools/validate_reader_experience.py
python tools/validate_publication_usability.py
python tools/validate_modern_epub.py
python tools/release_smoke_test.py
python tools/write_release_manifest.py
```

The GitHub Actions workflow additionally runs official **W3C EPUBCheck** and synchronizes the generated binaries after a passing build.

## Editorial policy

The manuscript is an **independent study companion** based on the assigned Junqueira chapter order. It is **not** an official Ministry book, an authorized reproduction of Junqueira, or evidence of guaranteed exam success. A passing software test does not replace expert scientific peer review or license and print approvals.

Original illustrations and their current attribution status are tracked in [the image rights ledger](rights/image_ledger.csv). Rights/owner sign-off and confirmation of the latest official syllabus are still required before an externally certified or commercial publication.

**Audit integration (17 November 2026):** corrected growth-plate zonation and selected MCQs, repaired a Golgi description, removed 23 repetitive practice templates without deleting the chapter-specific active recall, fixed PDF trailing spacer pagination, and made 100 MCQ stems and their options unbreakable on the page. No unrelated root-level files were removed during this content review.
