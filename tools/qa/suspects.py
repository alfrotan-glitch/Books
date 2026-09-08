"""Automated suspicious-token detector over the master (independent of the pipeline)."""
import re, sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from split_master import load
from wordfreq import zipf_frequency
def known(w): return zipf_frequency(w, "en") > 1.0

h, pages, t = load()
pat_tok = re.compile(r"[A-Za-z][A-Za-z’'\-]*")
out = {}
for pn, (m, body) in pages.items():
    sus = []
    for line in body.split("\n"):
        if line.startswith("[running foot"): continue
        # 1. explicit flags
        for f in re.findall(r"\{\?[^}]*\}", line):
            sus.append(("flag", f))
        # 2. odd char sequences
        for f in re.findall(r"[A-Za-z]*[<>~^`\\]+[A-Za-z]*", line):
            sus.append(("oddchar", f))
        # 3. lowercase letter followed directly by uppercase inside a word (e.g. "AS a", "wetght" no) -> camel
        for f in re.findall(r"\b[a-z]+[A-Z][a-z]+\b", line):
            sus.append(("camel", f))
        # 4. digit inside word
        for f in re.findall(r"\b[A-Za-z]+[0-9]+[A-Za-z]+\b", line):
            sus.append(("digit", f))
        # 5. unknown long words
        if known:
            for w in pat_tok.findall(line):
                wl = w.lower().strip("’'-")
                if len(wl) >= 4 and not known(wl) and "-" not in wl and "’" not in wl and "'" not in wl:
                    sus.append(("unk", w))
    sus = [s for s in sus if not (s[0]=="camel" and s[1] in ("iStockphoto","eBay","YouTube"))]
    if sus: out[pn] = sus
json.dump(out, open(f"{HERE}/suspects.json", "w"), indent=0, ensure_ascii=False)
for pn, sus in out.items():
    print(pn, " ".join(f"{k}:{v}" for k, v in sus))
