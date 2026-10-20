import re, json, sys

def load(f): return open(f).read()
def save(f,t): open(f,'w').write(t)

def chapter_bounds(t, n):
    m = re.search(r'^## %d · .*$' % n, t, re.M)
    if not m: return None
    start = m.start()
    nxt = re.search(r'^## \d+ · |^# PART', t[m.end():], re.M)
    end = m.end() + (nxt.start() if nxt else len(t)-m.end())
    return start, end

def add_objectives(t, n, block):
    b = chapter_bounds(t, n)
    if not b: return t, False
    s, e = b
    chunk = t[s:e]
    marker = '### The core idea'
    i = chunk.find(marker)
    if i == -1: return t, False
    chunk = chunk[:i] + block.strip() + "\n\n" + chunk[i:]
    return t[:s] + chunk + t[e:], True

def add_end(t, n, block):
    b = chapter_bounds(t, n)
    if not b: return t, False
    s, e = b
    chunk = t[s:e].rstrip() + "\n\n" + block.strip() + "\n\n"
    return t[:s] + chunk + t[e:], True

def apply(path, obj, end):
    t = load(path)
    for n, blocks in obj.items():
        t, ok = add_objectives(t, n, blocks)
        assert ok, f"objectives failed ch{n} in {path}"
    for n, blocks in end.items():
        t, ok = add_end(t, n, blocks)
        assert ok, f"end failed ch{n} in {path}"
    save(path, t)
    print("patched", path, len(obj), len(end))
