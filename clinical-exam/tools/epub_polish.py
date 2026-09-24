#!/usr/bin/env python3
"""Post-process the pandoc EPUB into a publication-grade EPUB 3.

- real <title> for every document (chapter name, not the file name)
- EPUB structural semantics + DPUB-ARIA roles (part, chapter, appendix, glossary,
  bibliography, index; tip / notice / example / note for the book's boxes)
- title page and copyright page (mirrors the PDF imprint)
- Dari landmarks (cover, title page, TOC, start of text, glossary, references, index)
- tables wrapped for horizontal scrolling on small screens
- Apple Books font flag
Usage: epub_polish.py book.epub metadata.yaml
"""
import re, sys, zipfile, html, os, shutil, tempfile

src, meta_path = sys.argv[1], sys.argv[2]

def meta(key):
    m = re.search(rf'^{key}:\s*"(.*)"\s*$', open(meta_path, encoding='utf-8').read(), re.M)
    return m.group(1) if m else ''

TITLE, SUB, AUTHOR = meta('title'), meta('subtitle'), meta('author')
EDITION, DATE, RIGHTS = meta('edition'), meta('date-display'), meta('rights')
PUBLISHER, ISBN = meta('publisher'), meta('isbn')

tmp = tempfile.mkdtemp()
with zipfile.ZipFile(src) as z:
    z.extractall(tmp)
E = os.path.join(tmp, 'EPUB')
T = os.path.join(E, 'text')

BOX = {  # class: (role, aria-label)
    'rule': ('doc-tip', 'قانون'),
    'practice': ('doc-tip', 'تمرین فردا صبح'),
    'pitfall': ('doc-notice', 'دام'),
    'case': ('doc-example', 'کیس برای فکر کردن'),
    'story': ('doc-example', 'قصه'),
    'evidence': ('note', 'شواهد'),
    'expert': ('note', 'برای متخصص'),
    'summary': ('note', 'خلاصه'),
    'osce': ('note', 'چک‌لیست OSCE'),
    'bigidea': ('note', 'ایده بزرگ'),
}

def kind(h1):
    if h1.startswith('بخش'): return 'part', 'doc-part', 'bodymatter'
    if h1.startswith('فصل'): return 'chapter', 'doc-chapter', 'bodymatter'
    if 'فهرست موضوعی' in h1: return 'index', 'doc-index', 'backmatter'
    if 'اصطلاحات' in h1: return 'glossary', 'doc-glossary', 'backmatter'
    if 'منابع' in h1: return 'bibliography', 'doc-bibliography', 'backmatter'
    if h1.startswith('ضمیمه'): return 'appendix', 'doc-appendix', 'backmatter'
    return 'introduction', 'doc-introduction', 'frontmatter'

landmarks = {}
for fn in sorted(os.listdir(T)):
    if not re.match(r'ch\d+\.xhtml$', fn): continue
    p = os.path.join(T, fn); t = open(p, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    if not m: continue
    h1 = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
    et, role, matter = kind(h1)
    t = t.replace('<link rel="stylesheet" type="text/css" href="../styles/stylesheet1.css" />',
                  '<link rel="stylesheet" type="text/css" href="../styles/stylesheet1.css" />\n  <link rel="stylesheet" type="text/css" href="../styles/themes.css" />', 1)
    t = re.sub(r'<title>.*?</title>', f'<title>{html.escape(h1)}</title>', t, 1, re.S)
    t = re.sub(r'<body epub:type="[^"]*">', f'<body epub:type="{matter}">', t, 1)
    t = re.sub(r'<h1>((?:فصل|بخش)[^:<]*|ضمیمه): ([^<]*)</h1>',
               r'<h1><span class="h1-label">\1</span><span class="h1-sep">: </span><span class="h1-title">\2</span></h1>', t, 1)
    t = re.sub(r'<section id="([^"]*)" class="level1">',
               lambda mm: f'<section id="{mm.group(1)}" class="level1 {et}" epub:type="{et}" role="{role}">', t, 1)
    for cls, (r, lab) in BOX.items():
        t = t.replace(f'<div class="{cls}">', f'<div class="{cls}" role="{r}" aria-label="{lab}">')
    t = re.sub(r'<th([^>]*)>\s*</th>', r'<td\1></td>', t)   # empty corner cells are not headers
    t = re.sub(r'(<body[^>]*>)', r'\1\n<main>', t, 1).replace('</body>', '</main>\n</body>', 1)
    t = re.sub(r'<table(\s[^>]*)?>', lambda mm: '<div class="table-wrap">' + mm.group(0), t)
    t = t.replace('</table>', '</table></div>')
    open(p, 'w', encoding='utf-8').write(t)
    sec = re.search(r'<section id="([^"]*)"', t)
    anchor = f'text/{fn}' + (f'#{sec.group(1)}' if sec else '')
    if et == 'introduction' and 'intro' not in landmarks: landmarks['intro'] = anchor
    if et == 'chapter' and 'body' not in landmarks: landmarks['body'] = anchor
    if et in ('index', 'glossary', 'bibliography'): landmarks[et] = anchor

# ---- title page + copyright page ----
rows = [('نام کتاب', f'{TITLE}: {SUB}' if SUB else TITLE), ('مؤلف', AUTHOR)]
if PUBLISHER: rows.append(('ناشر', PUBLISHER))
if EDITION: rows.append(('نوبت چاپ', EDITION))
if DATE: rows.append(('سال نشر', DATE))
if ISBN: rows.append(('شابک (ISBN)', ISBN))
dl = '\n'.join(f'<div><dt>{html.escape(a)}:</dt> <dd>{html.escape(b)}</dd></div>' for a, b in rows)
head = lambda title: f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="fa-AF" xml:lang="fa-AF" dir="rtl">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="../styles/stylesheet1.css" />
  <link rel="stylesheet" type="text/css" href="../styles/themes.css" />
</head>
'''
open(os.path.join(T, 'titlepage.xhtml'), 'w', encoding='utf-8').write(head(TITLE) + f'''<body epub:type="frontmatter">
<main>
<section class="titlepage" epub:type="titlepage">
  <h1 class="book-title">{html.escape(TITLE)}</h1>
  <p class="book-subtitle">{html.escape(SUB)}</p>
  <hr class="gold" />
  <p class="book-by">تألیف</p>
  <p class="book-author">{html.escape(AUTHOR)}</p>
  {f'<p class="book-publisher">{html.escape(PUBLISHER)}</p>' if PUBLISHER else ''}
  <p class="book-date">{html.escape(DATE)}</p>
</section>
<section class="imprint" epub:type="copyright-page" aria-label="شناسنامه کتاب">
  <dl class="imprint-list">
{dl}
  </dl>
  <p>{html.escape(RIGHTS)}</p>
  <p class="muted">مریضان و قصه‌های این کتاب فرضی اند؛ هر شباهت با اشخاص واقعی تصادفی است.</p>
  <p class="muted">این کتاب صرف برای مقاصد آموزشی تهیه گردیده است و جانشین قضاوت کلینیکی داکتر معالج نمی‌باشد.</p>
</section>
</main>
</body>
</html>
''')

# ---- OPF: manifest, spine, Apple font flag, ARIA feature ----
opf_p = os.path.join(E, 'content.opf'); opf = open(opf_p, encoding='utf-8').read()
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(meta_path)), 'epub-themes.css'), os.path.join(E, 'styles', 'themes.css'))
opf = opf.replace('<item id="stylesheet1"', '<item id="themes" href="styles/themes.css" media-type="text/css" />\n    <item id="stylesheet1"', 1)
opf = opf.replace('<item id="nav"', '<item id="titlepage" href="text/titlepage.xhtml" media-type="application/xhtml+xml" />\n    <item id="nav"', 1)
opf = opf.replace('<itemref idref="nav" />', '<itemref idref="titlepage" />\n    <itemref idref="nav" />', 1)
extra = ''
if 'ibooks:specified-fonts' not in opf:
    extra += '    <meta property="ibooks:specified-fonts">true</meta>\n'
if 'accessibilityFeature">ARIA' not in opf:
    extra += '    <meta property="schema:accessibilityFeature">ARIA</meta>\n'
if 'accessibilityFeature">readingOrder' in opf and 'accessibilityFeature">index' not in opf:
    extra += '    <meta property="schema:accessibilityFeature">index</meta>\n'
opf = opf.replace('  </metadata>', extra + '  </metadata>', 1)
open(opf_p, 'w', encoding='utf-8').write(opf)

# ---- nav: Dari landmarks ----
nav_p = os.path.join(E, 'nav.xhtml'); nav = open(nav_p, encoding='utf-8').read()
L = [('text/cover.xhtml', 'cover', 'جلد'), ('text/titlepage.xhtml', 'titlepage', 'صفحه عنوان'),
     ('#toc', 'toc', 'فهرست مطالب')]
if 'intro' in landmarks: L.append((landmarks['intro'], 'introduction', 'پیش از آغاز'))
if 'body' in landmarks: L.append((landmarks['body'], 'bodymatter', 'آغاز متن'))
for k, lab in (('glossary', 'فهرست اصطلاحات'), ('bibliography', 'منابع'), ('index', 'فهرست موضوعی')):
    if k in landmarks: L.append((landmarks[k], k, lab))
lm = '<nav epub:type="landmarks" id="landmarks" hidden="hidden">\n  <h2>نشانه‌ها</h2>\n  <ol>\n' + ''.join(
    f'    <li><a href="{h}" epub:type="{e}">{lab}</a></li>\n' for h, e, lab in L) + '  </ol>\n</nav>'
nav = re.sub(r'<nav epub:type="landmarks".*?</nav>', lm, nav, 1, re.S)
open(nav_p, 'w', encoding='utf-8').write(nav)

# ---- NCX: add title page entry is optional; leave ----
# ---- rezip (mimetype first, stored) ----
out = src + '.tmp'
with zipfile.ZipFile(out, 'w') as z:
    z.write(os.path.join(tmp, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(tmp):
        for f in sorted(files):
            full = os.path.join(root, f); rel = os.path.relpath(full, tmp)
            if rel == 'mimetype': continue
            z.write(full, rel, compress_type=zipfile.ZIP_DEFLATED)
os.replace(out, src); shutil.rmtree(tmp)
print('polished', len(landmarks), 'landmarks')
