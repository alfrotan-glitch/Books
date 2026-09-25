#!/usr/bin/env python3
"""chapter_qa.py — fast per-chapter QA: digit corruption, garbled words, structure.

Usage: python3 tools/chapter_qa.py chapters/12-hypertension.md
"""
import re, sys, glob
from pathlib import Path

GARBLED = ['aql', 'بلاکر', 'کونجستیو', 'کونگیستیو', 'انگیدوما', 'سبتوبند', 'Clemetizole',
           'دوالوپ', 'تودالوپ', 'کاستی وریدی', 'کاتالیزور', 'مالاتیو', 'بتابلاکر',
           'بیتابلکّر', 'بتابلکّر', 'بیتابلکر', 'سوپرهشن', 'CCKD', 'ګریس', 'کورتیکنوئید',
           'کاشه', 'کاشیه',]

def check(fn):
    t = open(fn, encoding='utf-8').read()
    issues = []
    lines = t.split('\n')
    # 1) structure: 15 sections
    required = ['Core Concept', 'Definition & Classification', 'Pathophysiology',
                'Etiology', 'Symptoms & Signs', 'Clinical Examination',
                'Quick Differential', 'Investigations', 'Diagnostic Criteria',
                'Management', 'Complications', 'Prognosis', 'Memory Joggers',
                'Red Flags', 'References', 'قدم کوچک', 'اتصال به فصل', 'مرور ۶۰ ثانیه']
    APPROACH = {'01','02','03','04','05','15','24','36','45','53','59','66','71'}
    if Path(fn).name[:2] in APPROACH:
        required = ['Memory Joggers','Red Flags','References','قدم کوچک','اتصال به فصل','مرور ۶۰ ثانیه']
    if 'سبک v3' in t:
        # v3: 15-section template = author completeness checklist (audited in release/style-dna-audit-v3.md);
        # reader-facing minimum = red flags, references, 60-second review; an opened case must be closed.
        required = ['Red Flags','References','مرور ۶۰ ثانیه']
        if 'کیس' in t[:3000] and 'برگشت به کیس' not in t:
            issues.append('V3: opening case never closed (برگشت به کیس)')
    for r in required:
        if r not in t:
            issues.append(f'MISSING SECTION: {r}')
    # 2) garbled words
    for g in GARBLED:
        for i, ln in enumerate(lines, 1):
            if g in ln:
                issues.append(f'L{i} GARBLED "{g}": {ln.strip()[:100]}')
    # 3) suspicious digits: 1-2 digit value before unit where context suggests larger
    for i, ln in enumerate(lines, 1):
        if re.search(r'(?:زیر|بالای)\s*[۰-۹]{1,2}\s*(?:mmHg|mg)', ln):
            issues.append(f'L{i} DIGIT?: {ln.strip()[:100]}')
        if re.search(r'[۰-۹]\.\s*(?:mg|ساعت|روز|دقیقه)', ln):
            issues.append(f'L{i} DECMISS?: {ln.strip()[:100]}')
        if re.search(r'[۰-۹]/[۰-۹]{1,2}\b', ln) and not re.search(r'[۰-۹]{2,3}/[۰-۹]{2,3}', ln):
            # e.g. 18/120 pattern (asymmetry)
            for m in re.finditer(r'([۰-۹]{1,3})/([۰-۹]{1,3})', ln):
                a, b = m.group(1), m.group(2)
                if len(a) != len(b) and (len(a) == 1 or len(b) == 1):
                    issues.append(f'L{i} RATIO?: {ln.strip()[:100]}')
                    break
    # 4) h1 present
    if not lines or not lines[0].startswith('# '):
        issues.append('NO H1 ON LINE 1')
    # 5) dosing table presence
    if Path(fn).name[:2] not in APPROACH and 'Dose' not in t and 'دوز' not in t:
        issues.append('NO DOSING SECTION?')
    return issues

if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob('chapters/*.md'))
    total = 0
    for fn in files:
        if Path(fn).name.startswith('00'):
            continue
        iss = check(fn)
        total += len(iss)
        if iss:
            print(f'== {fn} ==')
            for x in iss:
                print('  ', x)
    print(f'\nTotal issues: {total}')
