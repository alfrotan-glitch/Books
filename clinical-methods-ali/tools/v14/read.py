import sys,re
a,b=int(sys.argv[1]),int(sys.argv[2])
L=open('manuscript/master.md',encoding='utf-8').read().split('\n')
skip=False
for i in range(a-1,min(b,len(L))):
    l=L[i]
    if re.match(r'^::: (objectives|keypoints|case|selftest|redflags)',l): skip=True; continue
    if skip:
        if l.strip()==':::': skip=False
        continue
    if not l.strip() or l.startswith('|') or l.startswith('![') or l.strip() in (':::','---'): continue
    print(l)
