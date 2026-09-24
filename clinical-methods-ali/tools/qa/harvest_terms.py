import re,collections
t=open('manuscript/master.md',encoding='utf-8').read()
# stop at glossary appendix to avoid self-harvest
cut=t.find('واژه‌نامه'); 
body=t
D=r'[\u0600-\u06FF\u200c]+'
pat=re.compile(r'((?:'+D+r' ){0,3}'+D+r') \(([A-Za-z][A-Za-z \-\'/]{2,40})\)')
c=collections.Counter(); first={}
for m in pat.finditer(body):
    da=m.group(1).strip(); en=m.group(2).strip()
    c[(da,en)]+=1
bye=collections.defaultdict(collections.Counter)
for (da,en),n in c.items(): bye[en.lower()][da]+=n
existing={l.split('\t')[1].lower() for l in open('tools/pedagogy/glossary.tsv',encoding='utf-8') if '\t' in l}
out=[]
for en,das in bye.items():
    da,n=das.most_common(1)[0]
    enorig=[e for (d,e) in c if e.lower()==en][0]
    out.append((da,enorig,sum(das.values()),en in existing))
out.sort(key=lambda x:-x[2])
with open('build/term-candidates.tsv','w',encoding='utf-8') as f:
    for o in out: f.write('\t'.join(map(str,o))+'\n')
print(len(out), sum(1 for o in out if not o[3]))
