import re,sys,collections
t=open('manuscript/master.md',encoding='utf-8').read()
L=t.split('\n')
chk={
 'arabic_yk':r'[يكة]',
 'latin_comma_in_dari':r'[\u0600-\u06FF]\s*,\s*[\u0600-\u06FF]',
 'latin_semicolon_dari':r'[\u0600-\u06FF]\s*;\s*[\u0600-\u06FF]',
 'latin_qmark_dari':r'[\u0600-\u06FF]\s*\?',
 'space_before_punct':r'[\u0600-\u06FF] +[،؛:.!؟](?!\.)',
 'no_space_after_punct':r'[،؛][^\s\d»)\]]',
 'double_space':r'\S  +\S',
 'repeated_word':r'(?<![\u0600-\u06FF\u200c])([\u0600-\u06FF\u200c]{2,}) \1(?![\u0600-\u06FF\u200c])',
 'double_punct':r'[،؛]{2}|\.\.(?!\.)|،\.|\.،',
 'mi_without_zwnj':r'(?<![\u0600-\u06FF\u200c])(می|نمی) (?=[\u0600-\u06FF])',
 'ha_without_zwnj':r'[\u0600-\u06FF] ها(?![\u0600-\u06FF])',
 'iranian':r'(?<![\u0600-\u06FF])(بیمار|بیمارستان|پزشک|درصد|آزمایشگاه|بزرگسال|سرمه|تومور|پرستار|دکتر|سیگار|بیماری)(?![\u0600-\u06FF])',
 'western_digit_in_dari':r'[\u0600-\u06FF] [0-9]+ [\u0600-\u06FF]',
 'kasra_space':r'  ',
}
res=collections.defaultdict(list)
for i,l in enumerate(L,1):
    if l.startswith(('<!--','```','![','|---')): continue
    for k,p in chk.items():
        for m in re.finditer(p,l):
            res[k].append((i,l[max(0,m.start()-30):m.end()+30]))
# bracket balance per paragraph
for i,l in enumerate(L,1):
    for a,b in ['()','«»','[]']:
        if l.count(a)!=l.count(b): res['unbalanced_'+a].append((i,l[:120]))
for k,v in res.items():
    print(f'== {k}: {len(v)}')
    for x in v[:int(sys.argv[1]) if len(sys.argv)>1 else 6]: print('  ',x[0],x[1])
