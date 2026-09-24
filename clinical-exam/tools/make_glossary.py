"""Build chapters/92-glossary.md from tools/glossary.tsv (Dari<TAB>English), sorted in Dari alphabetical order."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[1]
order = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
def key(w):
    w = w.replace('\u200c', '')
    return [order.index(c) if c in order else 500 + ord(c) for c in w]
rows = [l.split('\t') for l in (R / 'tools/glossary.tsv').read_text(encoding='utf-8').strip().split('\n')]
rows.sort(key=lambda r: key(r[0]))
out = ['# ضمیمه: فهرست اصطلاحات دری ـ انگلیسی', '',
       'این فهرست اصطلاحاتی را که در کتاب به کار رفته اند، با معادل انگلیسی آن‌ها نشان می‌دهد تا خواندن کتاب‌های انگلیسی و رهنمودهای بین‌المللی برای شما آسان شود.', '',
       '| دری | English |', '|------------------------------|------------------------------|']
out += [f'| {d} | {e} |' for d, e in rows]
(R / 'chapters/92-glossary.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(len(rows), 'terms')
