import sys, pymupdf
PDF = "/home/user/Books/Active_Skills_for_Reading_2_Book_[languagecentre.ir]-1.pdf"
pn = int(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2:6]); dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 110
doc = pymupdf.open(PDF)
pix = doc[pn - 1].get_pixmap(dpi=dpi, clip=pymupdf.Rect(x0, y0, x1, y1))
out = f"/home/user/Books/tools/qa/crop_{pn:03d}.png"
pix.save(out); print(out)
