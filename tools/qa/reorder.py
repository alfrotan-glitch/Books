"""Reading-order correction: move sidebar section headings (## Reading Comprehension, ## Critical Thinking,
## Vocabulary Comprehension, ## Vocabulary Skill, ...) — together with their sidebar sub-label / explanatory box —
to the position in the main-column flow that matches their vertical position on the page.
Only re-orders existing paragraphs; never changes text."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from pagelocate import locate, para_tokens

def is_right(pn):
    # printed odd pages (= even PDF pages) carry the sidebar on the right
    return pn % 2 == 0
SKIP_HEAD = re.compile(r"^## (UNIT|Unit|CHAPTER|Chapter|Review|REVIEW|Self Check|Fluency|Reading Rate)")
SIDE_HEAD = re.compile(r"^## (Before You Read|Reading Skill|Reading Comprehension|Critical Thinking|Vocabulary Comprehension|"
                       r"Vocabulary Skill|VOCabulary Skill|Real Life Skill)\s*$")

def zone(pn, x):
    if is_right(pn):
        return "side" if x > 400 else "main"
    return "side" if x < 150 else "main"

SINGLE_COLUMN = set(range(1, 12)) | set(range(42, 50)) | set(range(80, 88)) | set(range(118, 126)) | set(range(156, 180))

def reorder_page(pn, body, log):
    if pn in SINGLE_COLUMN:
        return body, 0
    paras = re.split(r"\n\s*\n", body.strip("\n"))
    loc = [pos for _, pos in locate(pn, body, prefer=lambda x: zone(pn, x) == "side")]
    assert len(loc) == len(paras)
    n = len(paras)
    # identify sidebar groups
    groups = []   # (start, end_exclusive, heading_y)
    i = 0
    while i < n:
        p = paras[i]; pos = loc[i]
        if SIDE_HEAD.match(p) and pos and zone(pn, pos[0]) == "side":
            j = i + 1
            while j < n:
                q = paras[j]; qp = loc[j]
                if SIDE_HEAD.match(q):
                    break
                if q.startswith("## ") and (not qp or zone(pn, qp[0]) != "side"):
                    break
                if qp and zone(pn, qp[0]) == "side" and not q.startswith("[running foot") and not q.startswith("Motivational Tip"):
                    j += 1; continue
                break
            groups.append((i, j, pos[1]))
            i = j
        else:
            i += 1
    if not groups:
        return body, 0
    grouped = set()
    for a, b, _ in groups:
        grouped.update(range(a, b))
    rest = [k for k in range(n) if k not in grouped]
    # main-column y sequence among rest
    def y_of(k):
        pos = loc[k]
        if pos and zone(pn, pos[0]) == "main":
            return pos[1]
        return None
    def y_of_any(k):
        pos = loc[k]
        return pos[1] if pos else None
    out_idx = list(rest)
    inserts = []  # (position in out_idx, group)
    for a, b, hy in groups:
        target = None
        for t, k in enumerate(out_idx):
            y = y_of(k)
            if y is None or y < hy - 12:
                continue
            # confirm with the next located main paragraph
            nxt = next((y_of(k2) for k2 in out_idx[t+1:] if y_of(k2) is not None), None)
            if nxt is None or nxt >= hy - 12:
                target = t; break
        if target is not None:
            # step back over un-located paragraphs that belong to the start of the new section:
            # the exercise instruction line ("A ...") or a short label — never over numbered items
            def steppable(q):
                if y_of_any(q) is not None and y_of_any(q) >= hy - 12:
                    return True                      # located (any zone) at/below the heading
                if y_of_any(q) is not None:
                    return False
                s = paras[q]
                if s.startswith(("## ", "[running foot", "[TABLE", "[")) or re.match(r"^\d+ ", s):
                    return False
                return bool(re.match(r"^[A-E] [A-Z]", s)) or (re.search(r"[A-Za-z]", s) and len(para_tokens(s)) <= 4)
            while target > 0 and steppable(out_idx[target-1]):
                target -= 1
        if target is None:
            # before running foot / motivational tip at the end
            target = len(out_idx)
            while target > 0 and (paras[out_idx[target-1]].startswith("[running foot") or paras[out_idx[target-1]].startswith("Motivational Tip")):
                target -= 1
        inserts.append((target, list(range(a, b))))
    # build output: insert groups (stable, in order of target then original order)
    result = []
    inserts.sort(key=lambda x: x[0])
    ins_i = 0
    for t, k in enumerate(out_idx):
        while ins_i < len(inserts) and inserts[ins_i][0] == t:
            result.extend(inserts[ins_i][1]); ins_i += 1
        result.append(k)
    while ins_i < len(inserts):
        result.extend(inserts[ins_i][1]); ins_i += 1
    assert sorted(result) == list(range(n))
    moved = sum(1 for a, b, _ in groups)
    for a, b, hy in groups:
        after = result.index(b - 1)
        nxt = paras[result[after + 1]] if after + 1 < len(result) else "<END>"
        log.append((pn, paras[a][:40], hy, nxt.replace("\n", " ")[:60]))
    new_body = "\n" + "\n\n".join(paras[k] for k in result) + "\n\n\n"
    return new_body, moved

if __name__ == "__main__":
    from split_master import load
    h, pages, t = load()
    log = []; total = 0
    sel = [int(a) for a in sys.argv[1:]] or sorted(pages)
    for pn in sel:
        nb, m = reorder_page(pn, pages[pn][1], log)
        total += m
    for pn, head, hy, nxt in log:
        print(f"p{pn:03d} y={hy:5.0f} {head:40s} -> {nxt}")
    print("groups moved:", total)
