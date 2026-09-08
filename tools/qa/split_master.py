"""Split the frozen Master into per-page bodies (dict pn -> text) and the trailing QA section."""
import re
MASTER = "/home/user/Books/Active_Skills_for_Reading_2_MASTER_TEXT.txt"

FROZEN = "/home/user/Books/tools/qa/master_frozen.txt"   # git HEAD copy of the frozen extraction (stage-1 output)

def load(path=None):
    t = open(path or MASTER, encoding="utf-8").read()
    head, rest = t.split("[PAGE 001]", 1)
    rest = "[PAGE 001]" + rest
    body, tail = rest.split("\n[EXTRACTION_ISSUES]", 1)
    parts = re.split(r"(?m)^(\[PAGE \d{3}\][^\n]*)\n", body)
    pages = {}
    for i in range(1, len(parts), 2):
        pn = int(re.match(r"\[PAGE (\d{3})\]", parts[i]).group(1))
        pages[pn] = (parts[i], parts[i + 1])
    return head, pages, "[EXTRACTION_ISSUES]" + tail

if __name__ == "__main__":
    head, pages, tail = load()
    print(len(pages), min(pages), max(pages), len(head), len(tail))
