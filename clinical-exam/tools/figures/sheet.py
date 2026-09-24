import sys, pymupdf
out=sys.argv[1]; names=sys.argv[2:]
imgs=[pymupdf.open(f"assets/figures/{n}.png") for n in names]
W=900; y=0; rects=[]
for d in imgs:
    r=d[0].rect; h=W/2*r.height/r.width if len(names)>1 else W*r.height/r.width
    rects.append(h)
cols=2 if len(names)>1 else 1; cw=W/cols
doc=pymupdf.open(); rows=[max(rects[i:i+cols]) for i in range(0,len(rects),cols)]
pg=doc.new_page(width=W,height=sum(rows)+10*len(rows))
yy=0
for i,n in enumerate(names):
    r=i//cols; c=i%cols
    if c==0 and i>0: yy+=rows[r-1]+10
    pg.insert_image(pymupdf.Rect(c*cw,yy,c*cw+cw-8,yy+rects[i]),filename=f"assets/figures/{n}.png")
pg.get_pixmap(dpi=110).save(out)
