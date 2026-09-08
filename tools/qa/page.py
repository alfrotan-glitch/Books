import sys
sys.path.insert(0, "/home/user/Books/tools/qa")
from split_master import load
head, pages, tail = load()
for a in sys.argv[1:]:
    pn = int(a); print(pages[pn][0]); print(pages[pn][1])
