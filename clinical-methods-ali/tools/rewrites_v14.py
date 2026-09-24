"""v1.4 deep language edit: grammar, punctuation, wording, word choice (Afghan Dari).
Applied LAST by style_pass.py, on the finished master text.
GLOBAL = regex rules; FIX = (old, new) literal pairs; each old must occur (count checked)."""
GLOBAL = [
    (r"سوال", "سؤال", "spelling سؤال"),
    (r"(اجر|ابتد|اروا?|اد|ابتل|صفر|استم|امع|خل|وع|بن|دو|اعض|احتش)اء(?=[\s،.؛:)»])", r"\1ا", "final hamza dropped (Afghan orthography)"),
    (r"ابتدائی", "ابتدایی", "ابتدایی"),
    (r"آکسیجن", "اکسیجن", "one spelling: اکسیجن"),
    (r"(مرض|اسم|دست|رأس)‌اش(?=[\s،.؛:])", r"\1ش", "ـ‌اش after consonant → ـش"),
]
FIX = []

# literal fixes are kept as plain text in tools/v14/*.txt:
#   <<< old text          (or <<<N old text  when it occurs N times)
#   >>> new text
import pathlib as _pl, re as _re
for _f in sorted((_pl.Path(__file__).parent / "v14").glob("*.txt")):
    _old = None; _cnt = 1
    for _ln in _f.read_text(encoding="utf-8").splitlines():
        _m = _re.match(r"^<<<(\d*) (.*)$", _ln)
        if _m:
            _old = _m.group(2); _cnt = int(_m.group(1) or 1); continue
        if _ln.startswith(">>> ") and _old is not None:
            FIX.append((_old.replace("\\n", "\n"), _ln[4:].replace("\\n", "\n"), _cnt)); _old = None
