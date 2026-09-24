# Draws a labelled schematic ECG complex on standard paper -> assets/fig-ecg-complex.png
import pymupdf, math
S=12            # px per mm (1 small square)
Wmm,Hmm=60,34
W,H=Wmm*S,Hmm*S
doc=pymupdf.open(); pg=doc.new_page(width=W,height=H)
pink=(0.98,0.80,0.82); dpink=(0.93,0.55,0.60)
for i in range(Wmm+1):
    pg.draw_line((i*S,0),(i*S,H),color=dpink if i%5==0 else pink,width=1.4 if i%5==0 else 0.5)
for j in range(Hmm+1):
    pg.draw_line((0,j*S),(W,j*S),color=dpink if j%5==0 else pink,width=1.4 if j%5==0 else 0.5)
base=24*S   # baseline y (mm 24)
def g(t):   # t in mm along x -> height in mm (10 mm = 1 mV)
    def bump(c,w,a): return a*math.exp(-((t-c)/w)**2)
    y=0
    y+=bump(12,1.6,2.0)                  # P
    y+=bump(20.2,0.35,-1.2)              # Q
    y+=bump(21.2,0.45,13.0)              # R
    y+=bump(22.3,0.40,-3.5)              # S
    y+=bump(31,2.6,3.5)                  # T
    return y
pts=[(x/10*S, base-g(x/10)*S) for x in range(40,560)]
pg.draw_polyline(pts,color=(0.06,0.15,0.27),width=2.6)
navy=(0.06,0.15,0.27); teal=(0.07,0.44,0.45); gold=(0.72,0.57,0.23)
def lab(x,y,s,c=navy,fs=15): pg.insert_text((x*S,y*S),s,fontsize=fs,fontname="hebo",color=c)
lab(11.3,20.6,"P"); lab(19.2,26.8,"Q"); lab(20.6,9.8,"R"); lab(23.2,29.0,"S"); lab(30.4,18.9,"T")
def span(x1,x2,y,s,c):
    pg.draw_line((x1*S,y*S),(x2*S,y*S),color=c,width=2)
    for x in (x1,x2): pg.draw_line((x*S,(y-0.8)*S),(x*S,(y+0.8)*S),color=c,width=2)
    pg.insert_text(((x1+x2)/2*S-len(s)*4.6,(y-1.1)*S),s,fontsize=16,fontname="hebo",color=c)
span(10.2,20.0,30.5,"PR 0.12-0.20 s",teal)
span(20.0,22.9,33.2,"QRS <0.12 s",gold)
span(20.0,35.0,5.2,"QT (QTc <450-470 ms)",teal)
pg.draw_line((22.9*S,(base-0.2*S)),(27.5*S,base-0.2*S),color=(0.75,0.1,0.1),width=3)
pg.insert_text((23.0*S,(26.3)*S),"ST",fontsize=16,fontname="hebo",color=(0.75,0.1,0.1))
# scale key
pg.draw_rect(pymupdf.Rect(40.5*S,9*S,59.5*S,16.5*S),color=navy,fill=(1,1,1),width=0.8)
pg.insert_text((41*S,11*S),"1 small square = 0.04 s, 1 mm",fontsize=15,fontname="helv",color=navy)
pg.insert_text((41*S,13.2*S),"1 large square = 0.20 s, 5 mm",fontsize=15,fontname="helv",color=navy)
pg.insert_text((41*S,15.4*S),"25 mm/s   10 mm = 1 mV",fontsize=15,fontname="helv",color=navy)
pg.get_pixmap(dpi=150).save("assets/fig-ecg-complex.png")
print("ok")
