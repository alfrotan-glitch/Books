# Schematic PA chest film with the four "hidden areas" circled -> assets/fig-cxr-hidden.png
import pymupdf
W,H=700,620
doc=pymupdf.open(); pg=doc.new_page(width=W,height=H)
pg.draw_rect(pg.rect,fill=(0.08,0.08,0.10),color=None)
def poly(pts,fill,col=None,w=0,close=True):
    sh=pg.new_shape(); sh.draw_polyline(pts)
    if close: sh.draw_line(pts[-1],pts[0])
    sh.finish(fill=fill,color=col,width=w,closePath=close); sh.commit()
body=(0.55,0.55,0.58); lung=(0.16,0.16,0.19)
# thorax soft tissue
poly([(90,120),(250,60),(450,60),(610,120),(650,560),(50,560)],body)
# lungs (right lung is on viewer's left)
poly([(300,110),(250,112),(180,160),(135,260),(115,420),(122,468),(170,425),(230,418),(300,440),(310,300)],lung)
poly([(400,110),(450,112),(520,160),(565,260),(585,420),(580,498),(540,440),(470,435),(420,468),(395,300)],lung)
# trachea
poly([(335,40),(365,40),(368,190),(332,190)],lung)
pg.draw_line((340,190),(300,235),color=lung,width=14); pg.draw_line((360,190),(405,235),color=lung,width=14)
# heart
sh=pg.new_shape(); sh.draw_bezier((300,300),(250,360),(260,470),(330,480)); sh.draw_line((330,480),(500,480))
sh.draw_bezier((500,480),(560,440),(520,330),(420,300)); sh.draw_line((420,300),(300,300)); sh.finish(fill=(0.72,0.72,0.75),color=None); sh.commit()
# diaphragm domes
sh=pg.new_shape(); sh.draw_bezier((120,470),(170,410),(260,410),(300,440)); sh.finish(color=(0.85,0.85,0.88),width=4,closePath=False); sh.commit()
sh=pg.new_shape(); sh.draw_bezier((420,470),(460,430),(560,430),(580,500)); sh.finish(color=(0.85,0.85,0.88),width=4,closePath=False); sh.commit()
# clavicles & spine
for a,b in [((120,140),(320,120)),((380,120),(580,140))]: pg.draw_line(a,b,color=(0.85,0.85,0.88),width=7)
pg.draw_rect(pymupdf.Rect(338,190,362,560),fill=(0.66,0.66,0.69),color=None)
gold=(0.95,0.75,0.25)
def mark(c,r,n):
    pg.draw_circle(c,r,color=gold,width=4,dashes="[10 6] 0")
    pg.draw_circle((c[0]+r*0.72,c[1]-r*0.72),15,color=None,fill=gold)
    pg.insert_text((c[0]+r*0.72-5,c[1]-r*0.72+6),str(n),fontsize=18,fontname="hebo",color=(0.08,0.08,0.1))
mark((205,165),48,1); mark((495,165),48,1)
mark((460,410),50,2)
mark((350,265),42,3)
mark((200,520),42,4); mark((500,530),42,4)
pg.insert_text((20,40),"R",fontsize=26,fontname="hebo",color=(1,1,1))
pg.get_pixmap(dpi=130).save("assets/fig-cxr-hidden.png"); print("ok")
