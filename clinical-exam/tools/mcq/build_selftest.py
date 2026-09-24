#!/usr/bin/env python3
"""Append the second-round MCQs (tools/mcq/q2.tsv) to chapters/90-self-test.md. Idempotent.
Options are rotated so the keyed answer is spread evenly over الف/ب/ج/د."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / 'chapters/90-self-test.md'
L = ['الف', 'ب', 'ج', 'د']
fa = lambda n: str(n).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
t = P.read_text(encoding='utf-8')
MARK = '## دور دوم: کیس‌های کوتاه'
if MARK in t:
    head, rest = t.split(MARK, 1)
    ans_old = rest.split('## جواب‌ها', 1)[1]
    t = head.rstrip() + '\n\n## جواب‌ها' + ans_old
    t = '\n'.join(l for l in t.split('\n') if not (l[:3].rstrip('.').isdigit() and int(l.split('.')[0]) > 54))
rows = [r.rstrip('\n').split('\t') for r in open(ROOT / 'tools/mcq/q2.tsv', encoding='utf-8') if r.strip()]
parts = [(1, 5, 'بخش اول: ذهن داکتر'), (6, 18, 'بخش دوم: سیستم‌ها'), (19, 23, 'بخش سوم: مریضان خاص'), (24, 27, 'بخش چهارم: از شکایت تا تشخیص')]
qs, ans = [], []
n = 55
for lo, hi, title in parts:
    qs.append(f'### {title}\n')
    for i, r in enumerate([r for r in rows if lo <= int(r[0]) <= hi]):
        ch, q, *opts, key, why = r
        k = L.index(key); target = (n - 55) % 4
        order = list(range(4)); correct = opts[k]
        others = [o for j, o in enumerate(opts) if j != k]
        new = others[:target] + [correct] + others[target:]
        qs.append(f'**{fa(n)}.** {q}\n\n' + '  '.join(f'{L[j]}) {o}' for j, o in enumerate(new)) + '\n')
        ans.append(f'{n}. **{L[target]}.** {why} *(فصل {fa(ch)})*')
        n += 1
body, answers = t.split('## جواب‌ها', 1)
body = body.rstrip() + '\n\n' + MARK + '\n\nاین دور، کیس‌های کوتاه کنار بستر است. هر سؤال یک قانون کتاب را در یک موقعیت واقعی می‌آزماید.\n\n' + '\n'.join(qs)
answers = answers.rstrip() + '\n' + '\n'.join(ans) + '\n'
t = body + '\n## جواب‌ها' + answers
t = t.replace('این ۵۴ سؤال، برای هر فصل دو سؤال،', 'این ۱۳۵ سؤال، برای هر فصل پنج سؤال،')
P.write_text(t, encoding='utf-8')
print('questions', n - 1)
