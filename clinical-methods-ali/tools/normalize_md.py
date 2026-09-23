#!/usr/bin/env python3
"""Structural-only normalisation for Pandoc (no wording changes):
insert a blank line before a list that directly follows a paragraph line,
so Pandoc renders it as a list instead of running it into the paragraph."""
import re, sys
LIST = re.compile(r'^\s*([-*+]|[0-9۰-۹]+[.)])\s+')
src = open(sys.argv[1], encoding='utf-8').read().split('\n')
out = []
for line in src:
    if LIST.match(line) and out and out[-1].strip() and not LIST.match(out[-1]):
        out.append('')
    out.append(line)
# Persian-digit ordered-list markers ("۱. ") are not recognised by Pandoc;
# rewrite the marker only (the renderers display them again in Dari digits).
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
out = [re.sub(r'^(\s*)([۰-۹]+)([.)])\s', lambda m: m.group(1)+m.group(2).translate(FA)+m.group(3)+' ', l) for l in out]
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
