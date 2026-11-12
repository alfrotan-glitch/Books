#!/usr/bin/env python3
"""Create original A4 teacher and workbook PDF/DOCX/HTML from course markdown."""
from pathlib import Path
import os,re,html
import pypandoc
from docx import Document
from docx.shared import Mm,Pt,RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,HRFlowable
R=Path(__file__).resolve().parents[1]; D=R/"course"
F="/usr/share/fonts/truetype/dejavu"
for name,filename in (("Body","DejaVuSerif.ttf"),("Body-Bold","DejaVuSerif-Bold.ttf"),
                      ("Head","DejaVuSans.ttf"),("Head-Bold","DejaVuSans-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(name,os.path.join(F,filename)))
pdfmetrics.registerFontFamily("Body",normal="Body",bold="Body-Bold")
INK=colors.HexColor("#19313A"); TEAL=colors.HexColor("#076C69")
def markup(t):
    t=html.escape(t)
    t=re.sub(r"\*\*(.*?)\*\*",r"<b>\1</b>",t)
    t=re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",r"<i>\1</i>",t)
    return t
def pdf_build(md,out,title):
    styles={
        "p":ParagraphStyle("p",fontName="Body",fontSize=9.2,leading=14.4,spaceAfter=7,textColor=INK),
        "h1":ParagraphStyle("h1",fontName="Head-Bold",fontSize=18,leading=23,spaceBefore=20,spaceAfter=13,textColor=INK,keepWithNext=True),
        "h2":ParagraphStyle("h2",fontName="Head-Bold",fontSize=13,leading=18,spaceBefore=18,spaceAfter=8,textColor=TEAL,keepWithNext=True),
        "h3":ParagraphStyle("h3",fontName="Head-Bold",fontSize=10.4,leading=15,spaceBefore=13,spaceAfter=5,textColor=INK,keepWithNext=True),
        "c":ParagraphStyle("c",fontName="Head",fontSize=7.2,leading=10,textColor=INK,spaceAfter=0),
        "ch":ParagraphStyle("ch",fontName="Head-Bold",fontSize=7.2,leading=10,textColor=colors.white,spaceAfter=0),
    }
    story=[];lines=md.splitlines();i=0;page_count=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line=="---": story.append(HRFlowable(width="100%",color=TEAL,thickness=.7));i+=1;continue
        h=re.match(r"^(#{1,4})\s+(.+)",line)
        if h:
            lv=min(len(h.group(1)),3);txt=h.group(2)
            if (txt.startswith("Lesson ") or txt.startswith("Chapter ")) and page_count>2:
                story.append(PageBreak())
            if "ANSWER KEY AND FEEDBACK" in txt:story.append(PageBreak())
            story.append(Paragraph(markup(txt),styles[f"h{lv}"]));page_count+=1;i+=1;continue
        if line.startswith("|") and i+1<len(lines) and lines[i+1].strip().startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                cells=[c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-:\s]+",x) for x in cells): rows.append(cells)
                i+=1
            if len(rows)>1:
                n=max(map(len,rows));wid=(A4[0]-92)/n
                data=[[Paragraph(markup(row[j]) if j<len(row) else "",styles["ch" if r==0 else "c"]) for j in range(n)] for r,row in enumerate(rows)]
                t=Table(data,colWidths=[wid]*n,repeatRows=1)
                t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),INK),
                    ("GRID",(0,0),(-1,-1),.25,colors.HexColor("#B7CDCC")),
                    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
                story.append(t);story.append(Spacer(1,9))
            continue
        para=[line];i+=1
        if not re.match(r"^[-*] |^\d+\.\s",line):
            while i<len(lines) and lines[i].strip() and not re.match(r"^(?:#{1,4} |[-*] |\d+\. |\||---$)",lines[i].strip()):
                para.append(lines[i].strip());i+=1
        s=" ".join(para)
        if s.startswith("- "):s="&#8226;&nbsp; "+s[2:]
        story.append(Paragraph(markup(s),styles["p"]))
    def on_page(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(TEAL)
        canvas.line(45,A4[1]-37,A4[0]-45,A4[1]-37)
        canvas.setFont("Head",7);canvas.setFillColor(TEAL)
        canvas.drawString(45,A4[1]-28,"BASIC HISTOLOGY • REFERENCE-FIRST COURSE EDITION")
        canvas.drawCentredString(A4[0]/2,27,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=54,bottomMargin=45,
         title=title,author="",allowSplitting=True)
    doc.build(story,onFirstPage=on_page,onLaterPages=on_page)
for stem,title in (("Teacher_Guide","Histology Teacher's Guide"),("Student_Workbook","Histology Student Workbook")):
    file=D/(stem+".md"); assert file.is_file()
    docx=D/(stem+".docx");ht=D/(stem+".html");pdf=D/(stem+".pdf")
    pypandoc.convert_file(str(file),"docx",outputfile=str(docx),extra_args=["--toc","--toc-depth=2"])
    d=Document(docx)
    for sec in d.sections:
        sec.page_width=Mm(210);sec.page_height=Mm(297)
        sec.left_margin=Mm(18);sec.right_margin=Mm(18)
        sec.top_margin=Mm(18);sec.bottom_margin=Mm(18)
    normal=d.styles["Normal"];normal.font.name="Georgia";normal.font.size=Pt(9.5)
    normal.paragraph_format.line_spacing=1.16
    for level in range(1,5):
        n=f"Heading {level}"
        if n in d.styles:
            st=d.styles[n];st.font.bold=True;st.font.color.rgb=RGBColor(7,108,105)
            st.paragraph_format.keep_with_next=True
    d.save(docx)
    pypandoc.convert_file(str(file),"html5",outputfile=str(ht),extra_args=["--standalone","--toc","--toc-depth=2","--metadata","pagetitle="+title])
    txt=ht.read_text(encoding="utf-8")
    css="<style>body{font:16px/1.56 Georgia,serif;max-width:56rem;margin:auto;padding:2rem;color:#19313a}h1,h2,h3{font-family:Arial,sans-serif;color:#076c69}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #bbcecb;padding:.45rem}th{background:#19313a;color:white}nav#TOC{background:#eef7f4;padding:1rem}</style>"
    ht.write_text(txt.replace("</head>",css+"</head>"),encoding="utf-8")
    pdf_build(file.read_text(encoding="utf-8"),pdf,title)
    print("COURSE GENERATED:",stem,{e:(D/(stem+e)).stat().st_size for e in (".pdf",".docx",".html")})
