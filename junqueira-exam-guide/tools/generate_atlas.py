#!/usr/bin/env python3
"""Generate original, labeled schematic histology plates.

These drawings are NOT photomicrographs and do not portray diagnostic specimens.
All geometry is generated locally; no copyrighted atlas images are embedded.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "atlas"
W, H = 1440, 850
BG = "#F6FAFB"
INK = "#183443"
ACCENT = "#087E82"
MUTED = "#54707B"
LINE = "#A2B8C0"
PINK = "#E9A9B9"
PURPLE = "#7358A4"
PALE = "#DBEFF0"
TISSUE = "#F3D9E1"
FIBER = "#C486A0"
GOLD = "#E7C478"

def font(size, bold=False):
    basename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    location = Path("/usr/share/fonts/truetype/dejavu") / basename
    try:
        return ImageFont.truetype(str(location), size)
    except OSError:
        return ImageFont.load_default()

F36, F24, F20, F17 = font(36, True), font(24, True), font(20, True), font(17)
F15, F13 = font(15), font(13)

def text(d, xy, label, fill=INK, f=F15):
    d.text(xy, label, font=f, fill=fill)

def dot(d, cx, cy, radius, fill=PURPLE):
    d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=fill)

def nucleus(d, x, y, rx=10, ry=14):
    d.ellipse((x-rx, y-ry, x+rx, y+ry), fill=PURPLE)

def box(d, rect, fill=PALE, outline=LINE, width=3, radius=12):
    d.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)

def membrane(d, x0, x1, y):
    d.line([(x0,y),(x1,y)], fill=ACCENT, width=5)

def create_canvas(title, sub):
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,W,16), fill=ACCENT)
    text(d,(64,45),title,f=F36)
    text(d,(66,102),sub,fill=MUTED,f=F17)
    d.line([(64,146),(W-64,146)],fill=LINE,width=2)
    d.line([(64,790),(W-64,790)],fill=LINE,width=2)
    text(d,(66,802),"ORIGINAL TEACHING SCHEMATIC  •  NOT A MICROSCOPE IMAGE  •  NOT TO SCALE",fill=MUTED,f=F13)
    return im,d

def make_panel(d, x, label, note):
    y, w, h=181,408,576
    box(d,(x,y,x+w,y+h),fill="white",outline="#CAD9DE",width=3)
    text(d,(x+20,y+18),label,f=F20)
    d.line([(x+19,y+55),(x+w-19,y+55)],fill=LINE,width=2)
    text(d,(x+18,y+h-45),note,fill=MUTED,f=F13)
    return (x+23,y+75,x+w-23,y+h-68)

def pattern(d, kind, a):
    x0,y0,x1,y1=a
    cx=(x0+x1)//2
    rng=random.Random(kind)
    if kind=="squamous":
        by=y1-92
        membrane(d,x0+10,x1-10,by+30)
        for i in range(7):
            x=x0+16+i*49
            d.polygon([(x,by),(x+48,by-5),(x+49,by+17),(x,by+17)],
                      fill="#F7DCE4",outline=FIBER)
            nucleus(d,x+24,by+7,9,5)
    elif kind=="columnar":
        by=y1-100
        membrane(d,x0+10,x1-10,by+20)
        for i in range(10):
            x=x0+15+i*34
            d.rectangle((x,by-110,x+33,by+17),fill="#F4CADB",outline=FIBER,width=2)
            nucleus(d,x+17,by-28,8,15)
            for t in range(0,33,5):
                d.line([(x+t,by-114),(x+t,by-124)],fill=ACCENT,width=2)
    elif kind=="stratified":
        by=y1-95
        membrane(d,x0+10,x1-10,by+27)
        for j in range(4):
            for i in range(9):
                x=x0+10+i*39+(18 if j%2 else 0)
                y=by-35-j*42
                d.rounded_rectangle((x,y,x+42,y+38),radius=9,fill="#EFB9CB",outline=FIBER,width=2)
                nucleus(d,x+21,y+18,9 if j<3 else 15,11 if j<3 else 5)
    elif kind in ("hyaline","elastic","fibro"):
        box(d,(x0+10,y0+45,x1-10,y1-25),fill="#D7E7F0",outline="#ABC9D8",width=2,radius=5)
        for i in range(12):
            x=rng.randint(x0+45,x1-45)
            y=rng.randint(y0+80,y1-80)
            if kind=="fibro":
                x=x0+55+(i%3)*120+rng.randint(-8,8)
                y=y0+90+(i//3)*85
            d.ellipse((x-23,y-15,x+23,y+15),fill="#F7EBF0",outline=FIBER,width=3)
            nucleus(d,x,y,8,9)
        if kind=="elastic":
            for j in range(20):
                yy=y0+62+j*19
                coords=[(xx,yy+int(7*math.sin(xx/13+j))) for xx in range(x0+24,x1-22,12)]
                d.line(coords,fill=PURPLE,width=3)
        if kind=="fibro":
            for j in range(10):
                yy=y0+63+j*36
                d.line([(x0+18,yy),(x1-18,yy+6)],fill="#B47A99",width=9)
    elif kind in ("artery","vein","lymphatic"):
        if kind=="artery":
            d.ellipse((cx-158,y0+50,cx+158,y0+375),fill="#CF8FA3",outline="#B26985",width=5)
            d.ellipse((cx-91,y0+121,cx+91,y0+301),fill="#F1C1CE",outline=ACCENT,width=6)
            d.ellipse((cx-75,y0+139,cx+75,y0+284),fill="white",outline=FIBER,width=3)
        if kind=="vein":
            d.ellipse((cx-160,y0+68,cx+160,y0+350),fill="#E3AFBF",outline="#B26985",width=4)
            d.ellipse((cx-132,y0+90,cx+132,y0+328),fill="white",outline=FIBER,width=5)
            d.line([(cx-18,y0+102),(cx+25,y0+157),(cx+40,y0+117)],fill="#C990A5",width=8)
        if kind=="lymphatic":
            d.ellipse((cx-151,y0+66,cx+145,y0+349),fill=PALE,outline=ACCENT,width=5)
            d.ellipse((cx-141,y0+77,cx+134,y0+338),fill="white",outline=LINE,width=2)
            d.line([(cx-14,y0+78),(cx+43,y0+135)],fill=ACCENT,width=5)
            d.line([(cx+43,y0+135),(cx+80,y0+100)],fill=ACCENT,width=5)
            for i in range(8):
                dot(d,rng.randint(cx-115,cx+115),rng.randint(y0+110,y0+305),4,fill="#E9C680")
    elif kind in ("duodenum","ileum","colon"):
        y=y0+58
        # intestinal mucosa starts at line y+150; folds/villi extend to y
        if kind!="colon":
            for j in range(5):
                x=x0+35+j*69
                d.rounded_rectangle((x,y,x+42,y+155),radius=22,fill=TISSUE,outline=FIBER,width=3)
                d.ellipse((x+12,y+37,x+22,y+50),fill=PURPLE)
        else:
            d.rectangle((x0+12,y+140,x1-12,y+161),fill=TISSUE)
        for j in range(6):
            x=x0+25+j*56
            d.rounded_rectangle((x,y+160,x+30,y+285),radius=15,fill="#F6CAD8",outline=FIBER,width=3)
            dot(d,x+15,y+225,6)
        membrane(d,x0+5,x1-5,y+293)
        if kind=="duodenum":
            for j in range(8):
                xx=x0+30+(j%4)*86
                yy=y+332+(j//4)*44
                d.ellipse((xx,yy,xx+52,yy+32),fill=PALE,outline=ACCENT,width=3)
        if kind=="ileum":
            for j in range(14):
                xx=x0+33+(j%5)*57
                yy=y+337+(j//5)*32
                dot(d,xx,yy,14,fill="#A58AC7")
        if kind=="colon":
            for j in range(9):
                dot(d,x0+32+j*37,y+171+((j%3)*27),5,fill="#E9AD6B")
    elif kind in ("glomerulus","pct","dct"):
        if kind=="glomerulus":
            d.ellipse((cx-150,y0+46,cx+150,y0+365),fill="#E9C8D2",outline=FIBER,width=4)
            d.ellipse((cx-119,y0+77,cx+119,y0+335),fill="white",outline=FIBER,width=4)
            for i in range(19):
                theta=2*math.pi*i/19
                xx=cx+int(65*math.cos(theta))
                yy=y0+205+int(75*math.sin(theta))
                d.ellipse((xx-23,yy-24,xx+23,yy+24),fill="#EAB5C5",outline=PURPLE,width=3)
            text(d,(x0+76,y1-25),"Bowman space",f=F15)
        else:
            cy=y0+205
            d.ellipse((cx-150,cy-140,cx+150,cy+140),fill="#E8ABB9",outline=FIBER,width=4)
            d.ellipse((cx-86,cy-86,cx+86,cy+86),fill="white",outline="#D49CB0",width=5)
            for i in range(16):
                th=2*math.pi*i/16
                xx=cx+int(117*math.cos(th))
                yy=cy+int(113*math.sin(th))
                nucleus(d,xx,yy,9,12)
                if kind=="pct":
                    for j in range(3):
                        rr=77+j*7
                        x=cx+int(rr*math.cos(th))
                        y=cy+int(rr*math.sin(th))
                        dot(d,x,y,3,ACCENT)
            if kind=="dct":
                text(d,(x0+62,y1-32),"Open, clearer lumen",f=F15)
            else:
                text(d,(x0+62,y1-32),"Brush-border rim",f=F15)
    elif kind in ("lobule","portal","sinusoid"):
        cy=y0+215
        if kind=="lobule":
            pts=[(cx+int(165*math.cos(k*math.pi/3)),cy+int(160*math.sin(k*math.pi/3))) for k in range(6)]
            d.polygon(pts,fill="#F2D9DB",outline=FIBER)
            dot(d,cx,cy,29,fill="#B57A9C")
            for pt in pts:
                dot(d,*pt,11,fill=ACCENT)
                d.line([(cx,cy),pt],fill="#C49CAF",width=6)
        if kind=="portal":
            d.ellipse((cx-157,cy-145,cx+157,cy+145),fill="#F4D7DE",outline=FIBER,width=3)
            for xx,yy,rad,col in [(cx-65,cy,50,ACCENT),(cx+70,cy-45,28,"#B96C85"),(cx+65,cy+76,31,GOLD)]:
                d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),fill="white",outline=col,width=11)
        if kind=="sinusoid":
            for row in range(5):
                yy=y0+100+row*67
                coords=[(xx,yy+15*math.sin(xx/21+row)) for xx in range(x0+20,x1-20,10)]
                d.line(coords,fill=ACCENT,width=8)
                for i in range(8):
                    xx=x0+40+i*38
                    nucleus(d,xx,yy+34,9,9)
    elif kind in ("thymus","node","spleen"):
        cy=y0+215
        if kind=="thymus":
            d.ellipse((cx-145,cy-155,cx+145,cy+155),fill="#AF99C9",outline=PURPLE,width=4)
            d.ellipse((cx-99,cy-103,cx+99,cy+103),fill="#E8D9ED",outline="#CAB4D8",width=3)
            for rr in range(18,62,12):
                d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=FIBER,width=6)
        if kind=="node":
            d.ellipse((cx-145,cy-155,cx+145,cy+155),fill="#D0C0E2",outline=PURPLE,width=5)
            d.ellipse((cx-90,cy-93,cx+90,cy+93),fill="#E8DBEE",outline=LINE,width=2)
            for theta in [0,1.5,3,4.5]:
                xx=cx+int(112*math.cos(theta))
                yy=cy+int(118*math.sin(theta))
                dot(d,xx,yy,31,fill="#8A6BAF")
        if kind=="spleen":
            d.ellipse((cx-153,cy-155,cx+153,cy+155),fill="#EAB4C0",outline="#A66B80",width=5)
            for i in range(9):
                xx=rng.randint(cx-120,cx+120)
                yy=rng.randint(cy-115,cy+115)
                dot(d,xx,yy,rng.randint(14,32),fill="#7C639C")
            d.line([(cx-75,cy-80),(cx+50,cy+87)],fill=ACCENT,width=7)
    elif kind in ("osteon","trabeculae","cartilagebone"):
        cy=y0+210
        if kind=="osteon":
            for r in range(145,17,-23):
                d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=FIBER,width=9)
                for t in range(0,360,60):
                    a=math.radians(t+r)
                    dot(d,cx+int(r*math.cos(a)),cy+int(r*math.sin(a)),6,PURPLE)
            dot(d,cx,cy,20,ACCENT)
        elif kind=="trabeculae":
            for j in range(6):
                xx=x0+15+j*68
                d.line([(xx,y0+30),(xx+95,y0+370)],fill="#E6B7C5",width=23)
            for j in range(5):
                yy=y0+45+j*76
                d.line([(x0+20,yy),(x1-20,yy+25)],fill="#E6B7C5",width=19)
            for i in range(27):
                dot(d,rng.randint(x0+25,x1-25),rng.randint(y0+35,y0+370),4,PURPLE)
        else:
            d.polygon([(x0+10,y0+335),(x0+10,y0+110),(x1-10,y0+110),(x1-10,y0+335)],fill="#DFE8F0")
            for j in range(9):
                x=x0+45+j*34
                d.ellipse((x-18,y0+190,x+18,y0+215),fill="#F9E3E8",outline=FIBER,width=3)
                nucleus(d,x,y0+203,7,7)
            d.rectangle((x0+10,y0+320,x1-10,y0+355),fill="#C788A1")
    elif kind in ("thickskin","thinskin","gland"):
        cy=y0+200
        if kind!="gland":
            height=120 if kind=="thickskin" else 45
            d.rectangle((x0+20,y0+50,x1-20,y0+50+height),fill="#E2A9B8",outline=FIBER,width=4)
            d.rectangle((x0+20,y0+50,x1-20,y0+88 if kind=="thickskin" else y0+64),fill="#E8CD9D")
            d.rectangle((x0+20,y0+53+height,x1-20,y0+395),fill="#F2DEE4",outline=FIBER,width=3)
            if kind=="thinskin":
                d.line([(cx+55,y0+335),(cx-20,y0+8)],fill="#5B4D50",width=10)
                d.ellipse((cx+22,y0+286,cx+95,y0+360),fill="#E5B3C3",outline=FIBER,width=4)
        else:
            d.rectangle((x0+20,y0+40,x1-20,y0+400),fill="#F2DEE4")
            for i in range(6):
                xx=cx+int(52*math.cos(i*math.pi/3))
                yy=y0+245+int(66*math.sin(i*math.pi/3))
                d.ellipse((xx-28,yy-28,xx+28,yy+28),fill="#E7AEC0",outline=PURPLE,width=4)
            d.line([(cx,y0+190),(cx,y0+80)],fill=ACCENT,width=12)

PLATES = [
    ("epithelial_patterns","Epithelial organization","Count layers, then identify the luminal surface and basal boundary",
     [("Simple squamous","squamous","Single thin layer"),("Simple columnar","columnar","Tall absorptive cells"),("Stratified squamous","stratified","Multiple layers; flat surface")]),
    ("cartilage_patterns","Cartilage matrix patterns","Observe lacunae, fiber organization, and perichondrial context",
     [("Hyaline","hyaline","Smooth type-II-rich matrix"),("Elastic","elastic","Elastic fiber network"),("Fibrocartilage","fibro","Fibrous bundles; no perichondrium")]),
    ("vascular_patterns","Vessels in cross section","Wall architecture is more reliable than lumen shape alone",
     [("Muscular artery","artery","Conspicuous muscular media"),("Vein","vein","Thinner media; wider lumen"),("Initial lymphatic","lymphatic","Very thin endothelial wall")]),
    ("intestinal_patterns","Identifying intestinal segments","Search the mucosa and submucosa for regional landmarks",
     [("Duodenum","duodenum","Submucosal Brunner glands"),("Ileum","ileum","Aggregated Peyer patches"),("Colon","colon","Crypts; no villi")]),
    ("renal_patterns","Renal cortical landmarks","Use a renal corpuscle and tubular epithelial differences",
     [("Renal corpuscle","glomerulus","Capillary tuft in Bowman's capsule"),("Proximal tubule","pct","Eosinophilic, brush border"),("Distal tubule","dct","Paler, clearer lumen")]),
    ("hepatic_patterns","Liver lobule landmarks","Distinguish portal structures, sinusoids and the central vein",
     [("Classical lobule","lobule","Flow toward central vein"),("Portal triad area","portal","Vein, artery and duct"),("Sinusoidal plates","sinusoid","Hepatocytes border channels")]),
    ("lymphoid_patterns","Lymphoid organ architecture","Distinguish lobules, follicles, and red/white pulp",
     [("Thymus","thymus","Cortex, medulla, Hassall bodies"),("Lymph node","node","Cortical B-cell follicles"),("Spleen","spleen","White pulp amid red pulp")]),
    ("bone_patterns","Supporting tissue architecture","Compare lamellae, trabeculae and cartilage lacunae",
     [("Compact bone","osteon","Osteons around central canals"),("Spongy bone","trabeculae","Network of trabeculae"),("Hyaline cartilage","cartilagebone","Chondrocytes in lacunae")]),
    ("skin_patterns","Skin section landmarks","Compare epidermal thickness and adnexal structures",
     [("Thick skin","thickskin","Thick corneum; no hair"),("Thin skin","thinskin","Hair and thinner epidermis"),("Sweat gland coil","gland","Epithelial secretory tubules")]),
]

def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    for name,title,subtitle,panels in PLATES:
        im,d=create_canvas(title,subtitle)
        for x,(label,kind,note) in zip((59,516,973),panels):
            a=make_panel(d,x,label,note)
            pattern(d,kind,a)
        path=OUT/(name+".png")
        im.save(path,"PNG",optimize=True)
        print(path.name,path.stat().st_size)
    return len(PLATES)

if __name__=="__main__":
    generate()
