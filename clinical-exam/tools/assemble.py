"""Concatenate chapters/*.md in order into build/master.md; collect bedside rules into an appendix."""
import re, json, pathlib
R = pathlib.Path(__file__).resolve().parents[1]
allp = sorted((R / "chapters").glob("*.md"))
parts = [p for p in allp if not p.name.startswith("9")]
apps = [p for p in allp if p.name.startswith("9")]
text = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in parts) + "\n"
# inside story boxes every line is its own paragraph (dialogue)
text = re.sub(r"(::: story\n)(.*?)(\n:::)", lambda m: m.group(1) + re.sub(r"(?<!\n)\n(?!\n)", "\n\n", m.group(2)) + m.group(3), text, flags=re.S)
rules = re.findall(r"::: rule\n\*\*(قانون [۰-۹0-9]+):\*\*\s*(.+?)\n:::", text, re.S)
if rules:
    text += "\n# ضمیمه: قانون‌های کنار بستر\n\n" + "\n".join(f"{i}. {b.strip()}" for i, (_, b) in enumerate(rules, 1)) + "\n"
# OSCE guide: one line per chapter checklist
osce = []
for p in parts:
    t = p.read_text(encoding="utf-8")
    h = re.search(r"^# (فصل [^:]+):\s*(.+)$", t, re.M)
    o = re.search(r"::: osce\n\*\*چک‌لیست OSCE:\s*(.+?)\*\*", t)
    if h and o:
        osce.append(f"| {h.group(1)} | {o.group(1).strip()} |")
if osce:
    text += ("\n# ضمیمه: راهنمای چک‌لیست‌های OSCE\n\n"
             "هر فصل این کتاب با یک چک‌لیست ده‌قدمی OSCE ختم می‌شود. این فهرست به شما کمک می‌کند که پیش از امتحان عملی، "
             "یا پیش از معاینه یک مریض، چک‌لیست لازم را زود پیدا کنید. هر چک‌لیست را با صدای بلند، بالای یک همصنفی، تمرین کنید؛ "
             "دست شما آنچه را که چشم تنها خوانده است، زود فراموش می‌کند.\n\n"
             "| فصل | چک‌لیست |\n|--------------------|------------------------------------------|\n" + "\n".join(osce) + "\n")
for p in apps:
    text += "\n" + p.read_text(encoding="utf-8").strip() + "\n"
(R / "build").mkdir(exist_ok=True)
(R / "build/master.md").write_text(text, encoding="utf-8")
(R / "build/index-terms.json").write_text(json.dumps({"pattern": "\uE000\uE001"}), encoding="utf-8")
print(f"assembled {len(parts)} files, {len(rules)} rules")
