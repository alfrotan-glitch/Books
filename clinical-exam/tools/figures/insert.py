#!/usr/bin/env python3
"""Insert figure lines after anchor paragraphs. Usage: insert.py spec.tsv  (file<TAB>anchor-prefix<TAB>figure-markdown). Idempotent."""
import sys, pathlib
for row in open(sys.argv[1], encoding='utf-8'):
    row=row.rstrip('\n')
    if not row.strip() or row.startswith('#'): continue
    f, anchor, fig = row.split('\t')
    p = pathlib.Path('chapters')/f; t = p.read_text(encoding='utf-8')
    name = fig.split('assets/figures/')[1].split(')')[0]
    if name in t: continue
    lines = t.split('\n'); hits=[i for i,l in enumerate(lines) if l.startswith(anchor)]
    if len(hits)!=1: print('ANCHOR?', f, anchor, len(hits)); continue
    i=hits[0]
    # move to end of paragraph/table block
    while i+1 < len(lines) and lines[i+1].strip(): i+=1
    lines[i+1:i+1] = ['', fig]
    p.write_text('\n'.join(lines), encoding='utf-8'); print('ok', f, name)
