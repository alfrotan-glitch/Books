#!/usr/bin/env python3
"""Validate all 100 examination stems and their four choices share a PDF page.

This checks the actual rendered book, not just the manuscript.
"""
from pathlib import Path
import re
import pymupdf

pdf = pymupdf.open(Path(__file__).resolve().parents[1] / "Basic_Histology_Learning_Text.pdf")
toc = pdf.get_toc()
start = next(page for _, name, page in toc if name == "100 Examination Questions") - 1
end = next(page for _, name, page in toc if name == "Answer Key with Explanations") - 1
seen = {}
problems = []
for page_index in range(start, end):
    lines = pdf[page_index].get_text().splitlines()
    starts = []
    for index, line in enumerate(lines):
        match = re.match(r"^([1-9]\d{0,2})\.\s", line)
        if match:
            starts.append((index, int(match.group(1))))
    for index, (line_index, number) in enumerate(starts):
        stop = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
        segment = "\n".join(lines[line_index:stop])
        seen.setdefault(number, []).append(page_index + 1)
        options = {letter for letter in "ABCD"
                   if re.search(r"(?m)^" + letter + r"\.\s", segment)}
        if options != set("ABCD"):
            problems.append((number, page_index + 1, "".join(sorted(options))))
assert set(seen) == set(range(1, 101)), f"Question IDs incorrect: {set(range(1, 101)) ^ set(seen)}"
assert all(len(pages) == 1 for pages in seen.values()), "Question repeated across pages"
assert not problems, f"MCQ stem/options split across pages: {problems}"
print("MCQ PAGINATION PASS: all 100 question stems and four options are together.")
