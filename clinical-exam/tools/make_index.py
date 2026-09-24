"""Build chapters/94-index.md from tools/index-terms.txt (one term per line); page numbers are filled in by the PDF build."""
import pathlib, re
R = pathlib.Path(__file__).resolve().parents[1]
order = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
def key(w):
    w = w.replace('\u200c', '')
    if re.match(r'[A-Za-z]', w): return [1000] + [ord(c.lower()) for c in w]
    return [order.index(c) if c in order else 500 + ord(c) for c in w]
terms = sorted({t.strip() for t in (R / 'tools/index-terms.txt').read_text(encoding='utf-8').split('\n') if t.strip()}, key=key)
(R / 'tools/index-terms.txt').write_text('\n'.join(terms) + '\n', encoding='utf-8')
out = ['# ضمیمه: فهرست موضوعی', '', 'اعداد بعد از هر اصطلاح، شماره صفحه‌هایی اند که آن موضوع در آن‌ها بحث شده است.', ''] + [f'- **{t}**' for t in terms]
(R / 'chapters/94-index.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(len(terms), 'terms')
