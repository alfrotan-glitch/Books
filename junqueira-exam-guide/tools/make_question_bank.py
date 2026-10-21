#!/usr/bin/env python3
"""Export Part VII (the 100 examination questions) to a CSV question bank.

Columns: No,Section,Question,A,B,C,D,Answer,Explanation,Distractors.
The explanation and distractor notes are the ones printed in the book's
answer key, split at the "Trap:" marker.
"""
import csv
import re

src = open("src/07_mcq.md", encoding="utf-8").read()
qpart = src.split("## Answer Key with Explanations")[0]
kpart = src.split("## Answer Key with Explanations")[1]

section, questions = "", {}
for line in qpart.split("\n"):
    m = re.match(r"^### (.+)$", line)
    if m:
        section = m.group(1).strip()
        continue
    m = re.match(r"^\*\*(\d+)\.\*\* (.+)$", line)
    if m:
        qno, stem = int(m.group(1)), m.group(2).strip()
        questions[qno] = {"section": section, "q": stem, "opts": {}}
        continue
    if questions and re.search(r"\bA\.\s", line):
        last = max(questions)
        for part in re.split(r"<br\s*/?>", line):
            m = re.match(r"^\s*([A-D])\.\s*(.+?)\s*$", part)
            if m:
                questions[last]["opts"][m.group(1)] = m.group(2).strip()

key = {}
for m in re.finditer(r"^\*\*(\d+)\. ([A-D])\*\* — (.+?)(?:\n\n|\Z)", kpart, re.M | re.S):
    body = re.sub(r"\s+", " ", m.group(3)).strip()
    expl, _, trap = body.partition("**Trap:**")
    key[int(m.group(1))] = (m.group(2), expl.strip(), trap.strip())

missing = [n for n in questions if n not in key or len(questions[n]["opts"]) != 4]
print("questions", len(questions), "keys", len(key), "incomplete", missing)

with open("deliverables/junqueira_question_bank.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["No", "Section", "Question", "A", "B", "C", "D", "Answer", "Explanation", "Why the distractors fail"])
    for n in sorted(questions):
        q = questions[n]
        ans, expl, trap = key[n]
        w.writerow([n, q["section"], q["q"], q["opts"]["A"], q["opts"]["B"], q["opts"]["C"],
                    q["opts"]["D"], ans, expl, trap])
print("wrote", len(questions))
