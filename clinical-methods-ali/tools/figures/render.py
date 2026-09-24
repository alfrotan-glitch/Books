#!/usr/bin/env python3
"""Render every figure defined in figs.typ to assets/figures/<name>.png (400 ppi PNG for EPUB/DOCX + vector SVG for the PDF)."""
import re, sys, pathlib, typst
HERE = pathlib.Path(__file__).parent; ROOT = HERE.parent.parent
OUT = ROOT / "assets/figures"; OUT.mkdir(parents=True, exist_ok=True)
names = re.findall(r'^\s*"([a-z0-9-]+)":', (HERE / "figs.typ").read_text(), flags=re.M)
only = sys.argv[1:] or names
bad = []
for n in only:
    try:
        png = typst.compile(str(HERE / "figs.typ"), format="png", ppi=400, root=str(ROOT),
                            font_paths=[str(ROOT / "fonts")], ignore_system_fonts=True, sys_inputs={"fig": n})
        (OUT / f"{n}.png").write_bytes(png)
        svg = typst.compile(str(HERE / "figs.typ"), format="svg", root=str(ROOT),
                            font_paths=[str(ROOT / "fonts")], ignore_system_fonts=True, sys_inputs={"fig": n})
        (OUT / "svg").mkdir(exist_ok=True)
        (OUT / "svg" / f"{n}.svg").write_bytes(svg)   # vector copy used by the PDF build
    except Exception as e:
        bad.append((n, str(e)[:300]))
print(f"rendered {len(only) - len(bad)}/{len(only)}")
for b in bad: print("FAIL", *b)
