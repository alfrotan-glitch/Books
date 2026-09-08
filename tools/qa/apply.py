"""Apply the QA corrections to the FROZEN master (tools/qa/master_frozen.txt = stage-1 output) and write the
corrected master. Idempotent: always starts from the frozen snapshot.
Steps: 1) whole-page transcriptions (page_text.py)  2) exact-once string corrections (corrections.py)
       3) reading-order pass for sidebar headings (reorder.py)  4) post-reorder corrections (corrections_post.py)"""
import sys, re, json
sys.path.insert(0, "/home/user/Books/tools/qa")
from split_master import load, MASTER, FROZEN
from corrections import CORR
from page_text import PAGE_TEXT
head, pages, tail = load(FROZEN)
applied = 0
for page, text in PAGE_TEXT.items():
    pages[page] = (pages[page][0], "\n" + text.strip("\n") + "\n\n\n"); applied += 1
for page, old, new, note in CORR:
    marker, body = pages[page]
    n = body.count(old)
    if n != 1:
        print(f"ABORT page {page}: pattern found {n} times: {old[:70]!r}"); sys.exit(1)
    pages[page] = (marker, body.replace(old, new, 1)); applied += 1
# reading-order pass
from reorder import reorder_page
log = []; moved = 0
for pn in range(1, 180):
    nb, m = reorder_page(pn, pages[pn][1], log)
    pages[pn] = (pages[pn][0], nb); moved += m
from linemarks import fix_linemarks
lm_log = []; lm = 0
for pn in range(1, 180):
    nb, c_ = fix_linemarks(pn, pages[pn][1], lm_log)
    pages[pn] = (pages[pn][0], nb); lm += c_
try:
    from corrections_post import CORR_POST
except ImportError:
    CORR_POST = []
for page, old, new, note in CORR_POST:
    marker, body = pages[page]
    n = body.count(old)
    if n != 1:
        print(f"ABORT(post) page {page}: pattern found {n} times: {old[:70]!r}"); sys.exit(1)
    pages[page] = (marker, body.replace(old, new, 1)); applied += 1
out = head + "".join(pages[p][0] + "\n" + pages[p][1] for p in range(1, 180)) + "\n" + tail
json.dump(log, open("/home/user/Books/tools/qa/reorder_log.json", "w"), indent=0)
open("/home/user/Books/tools/qa/master_out.txt", "w", encoding="utf-8").write(out)   # always: preview of result
if "--write" in sys.argv:
    open(MASTER, "w", encoding="utf-8").write(out)
    print("written", applied, "corrections;", moved, "sidebar heading groups re-ordered;", lm, "line-marker fixes")
else:
    print("dry run OK:", applied, "corrections;", moved, "sidebar heading groups would be re-ordered;", lm, "line-marker fixes")
