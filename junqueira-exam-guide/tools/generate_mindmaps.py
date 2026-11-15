#!/usr/bin/env python3
"""Generate 23 original, reference-aligned hierarchical histology mind maps.

All words come from data/chapter_mindmaps.json. The illustrations are original,
conceptual classification diagrams (not microscope images or textbook plates).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "chapter_mindmaps.json"
OUT = ROOT / "build" / "mindmaps"
W, H = 1500, 700
BG = "#F8FBFC"
NAVY = "#173544"
TEAL = "#116F70"
TEAL_LIGHT = "#E6F5F2"
PALE = "#FFFFFF"
MUTED = "#526A76"
BORDER = "#C7DADA"
CARDHEAD = "#0F5962"
GOLD = "#F2B868"
PATHS = "#558D91"

def font(size, bold=False):
    fontname = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    file = Path("/usr/share/fonts/truetype/dejavu") / fontname
    try:
        return ImageFont.truetype(str(file), size)
    except OSError:
        return ImageFont.load_default()

TITLE = font(38, True)
INTRO = font(19)
ROOT_FONT = font(40, True)
BRANCH = font(30, True)
DETAIL = font(27)
FOOT = font(16)
NUM = font(22, True)

def fit(draw, text, f, maxwidth):
    words = text.split(" ")
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0),test,font=f)[2] <= maxwidth:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def make_map(number, spec):
    im = Image.new("RGB",(W,H),BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,W,13),fill=TEAL)
    d.text((50,37),spec["title"],font=TITLE,fill=NAVY)
    d.text((53,92),f"JUNQUEIRA 17th ED.  |  CHAPTER {number:02d}  |  WHOLE -> PARTS -> FUNCTION",font=INTRO,fill=MUTED)
    rootbox=(355,137,1145,225)
    d.rounded_rectangle(rootbox,fill=TEAL,radius=20)
    box=d.textbbox((0,0),spec["root"],font=ROOT_FONT)
    d.text(((W-(box[2]-box[0]))/2,155),spec["root"],font=ROOT_FONT,fill="#FFFFFF")
    # The connectors are underneath the branch cards; each card is one direct
    # child of the main concept and contains two nested pieces of knowledge.
    d.line((750,225,750,248),fill=PATHS,width=5)
    d.line((275,248,1225,248),fill=PATHS,width=5)
    cols=[50,545,1040]
    for x in cols:
        mx=x+205
        d.line((mx,248,mx,288),fill=PATHS,width=4)
        d.line((mx,452,mx,483),fill=PATHS,width=4)
    for j, branch in enumerate(spec["branches"]):
        x=cols[j%3]
        y=289 if j<3 else 484
        width=410
        height=174
        d.rounded_rectangle((x,y,x+width,y+height),fill=PALE,outline=BORDER,width=3,radius=16)
        d.rounded_rectangle((x,y,x+width,y+57),fill=TEAL_LIGHT,radius=14)
        d.rectangle((x,y+42,x+width,y+58),fill=TEAL_LIGHT)
        d.rounded_rectangle((x+11,y+11,x+45,y+45),fill=TEAL,radius=9)
        d.text((x+21,y+13),str(j+1),font=NUM,fill="#FFFFFF")
        # Fit headers to card widths using a controlled short first line
        title=branch[0]
        title_font=BRANCH
        if d.textbbox((0,0),title,font=BRANCH)[2] > 338:
            title_font=font(26,True)
        d.text((x+56,y+12),title,font=title_font,fill=CARDHEAD)
        for k, fact in enumerate(branch[1:]):
            yy=y+78+k*43
            d.ellipse((x+18,yy+10,x+27,yy+19),fill=TEAL)
            lines=fit(d,fact,DETAIL,365)
            if len(lines)>1:
                small=font(24)
                d.text((x+39,yy-6),lines[0],font=small,fill=NAVY)
                d.text((x+39,yy+17),lines[1],font=small,fill=NAVY)
            else:
                d.text((x+39,yy),lines[0],font=DETAIL,fill=NAVY)
    d.line((50,677,1450,677),fill=BORDER,width=2)
    d.text((52,681),"ORIGINAL CONCEPT MAP  •  STUDY DIAGRAM, NOT A MICROSCOPE IMAGE",font=FOOT,fill=MUTED)
    return im

def generate():
    data=json.loads(SOURCE.read_text(encoding="utf-8"))
    assert set(map(int,data)) == set(range(1,24))
    OUT.mkdir(parents=True,exist_ok=True)
    sizes=[]
    for n in range(1,24):
        spec=data[str(n)]
        assert len(spec["branches"]) == 6 and len(spec["chains"]) == 2
        for b in spec["branches"]:
            assert len(b)==3
        im=make_map(n,spec)
        path=OUT/f"chapter_{n:02d}.png"
        im.save(path,optimize=True)
        sizes.append(path.stat().st_size)
    print(f"MIND MAPS GENERATED: {len(sizes)} original maps, total bytes {sum(sizes)}")
    return len(sizes)

if __name__=="__main__":
    generate()
