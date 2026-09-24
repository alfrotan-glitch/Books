# معاینه کلینیکی: از تاریخچه تا تشخیص — new original book

**Author:** داکتر الله یار فروتن · **Language:** Afghan Dari · **Status:** in writing. Front matter and chapters 1–4 are drafted.

This book is written from scratch. The old manuscript («میتودهای کلینیکی علی») is **not** used as a text source. Originality is checked with `tools/similarity.py` against both the original and the edited old text; the current result is **0 shared 8-word sequences**.

- Plan and chapter list: `BLUEPRINT.md`
- Voice and box conventions: `STYLE-GUIDE.md`
- Sources: `SOURCES.md`
- Chapters: `chapters/NN-*.md`, assembled by `tools/assemble.py`. The bedside-rules appendix is generated automatically.
- Build: `./build.sh`, then `python3 tools/cover/make_cover.py`. Outputs go to `build/`; sample PDFs are copied to `release/`.
