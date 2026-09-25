"""gen_references.py — assemble appendix 95 (all chapter references, grouped by chapter) from chapters/*.md.
Called automatically by build.py."""
import glob, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
out = ["# ضمیمهٔ ۹۵ — منابع کتاب به ترتیب فصل", "",
       "> این ضمیمه منابع همهٔ فصل‌ها را به ترتیب فصل یک‌جا می‌آورد.", ""]
for f in sorted(glob.glob(str(ROOT / "chapters" / "[0-8][0-9]-*.md"))):
    s = Path(f).read_text(encoding="utf-8")
    title = s.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"## 📚 References\n(.*?)(?=\n## |\Z)", s, re.S)
    if not m or Path(f).name.startswith("00"):
        continue
    body = m.group(1).strip()
    out += [f"## {title}", "", body, ""]
out += ["## 📚 References", "", "این ضمیمه خودش مجموعهٔ منابع فصل‌هاست؛ منبع جداگانه ندارد.", ""]
(ROOT / "chapters" / "95-references.md").write_text("\n".join(out), encoding="utf-8")
print("written", len(out), "lines")
