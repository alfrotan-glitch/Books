"""Concatenate chapters/*.md in order into build/master.md; collect bedside rules into an appendix."""
import re, json, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
parts = sorted((R / "chapters").glob("*.md"))
text = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in parts) + "\n"
# inside story boxes every line is its own paragraph (dialogue)
text = re.sub(r"(::: story\n)(.*?)(\n:::)", lambda m: m.group(1) + re.sub(r"(?<!\n)\n(?!\n)", "\n\n", m.group(2)) + m.group(3), text, flags=re.S)
rules = re.findall(r"::: rule\n\*\*(قانون [۰-۹0-9]+):\*\*\s*(.+?)\n:::", text, re.S)
if rules:
    text += "\n# ضمیمه: قانون‌های کنار بستر\n\n" + "\n".join(f"{i}. {b.strip()}" for i, (_, b) in enumerate(rules, 1)) + "\n"
(R / "build").mkdir(exist_ok=True)
(R / "build/master.md").write_text(text, encoding="utf-8")
(R / "build/index-terms.json").write_text(json.dumps({"pattern": "\uE000\uE001"}), encoding="utf-8")
print(f"assembled {len(parts)} files, {len(rules)} rules")
