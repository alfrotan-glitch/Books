#!/usr/bin/env python3
"""Fail publication when flashcards or exam-bank CSVs drift from the manuscript.

Checks structural integrity, answer concordance, duplicate prompts and specific
previously corrected scientific errors. This is not a substitute for faculty review.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "07_mcq.md"
DECK = ROOT / "deliverables" / "junqueira_flashcards.csv"
BANK = ROOT / "deliverables" / "junqueira_question_bank.csv"


def rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    source = SRC.read_text(encoding="utf-8")
    question_text, answer_text = source.split("## Answer Key with Explanations", 1)
    questions = {}
    section = ""
    current = None
    for line in question_text.splitlines():
        m = re.fullmatch(r"### (.+)", line)
        if m:
            section = m.group(1)
        m = re.match(r"^\*\*(\d+)\.\*\* (.+)$", line)
        if m:
            current = int(m.group(1))
            assert current not in questions, f"Duplicate question {current}"
            questions[current] = {"stem": m.group(2), "section": section, "options": {}}
        elif current is not None and re.match(r"^A\.\s", line):
            parts = re.split(r"<br\s*/?>", line)
            assert len(parts) == 4, f"Question {current}: need four options"
            options = {}
            for letter, part in zip("ABCD", parts):
                mo = re.fullmatch(r"\s*([A-D])\.\s*(.+?)\s*", part)
                assert mo and mo.group(1) == letter, f"Question {current}: bad {letter} option"
                options[letter] = mo.group(2)
            questions[current]["options"] = options

    answer_pattern = re.compile(r"^\*\*(\d+)\. ([A-D])\*\* — (.+?)(?=\n\n|\Z)", re.M | re.S)
    keys = {}
    for m in answer_pattern.finditer(answer_text):
        num = int(m.group(1))
        assert num not in keys, f"Duplicate answer {num}"
        body = re.sub(r"\s+", " ", m.group(3)).strip()
        explanation, _, trap = body.partition("**Trap:**")
        keys[num] = (m.group(2), explanation.strip(), trap.strip())

    assert list(sorted(questions)) == list(range(1, 101)), "Expected numbered questions 1–100"
    assert sorted(keys) == sorted(questions), "Question/key numbering mismatch"
    assert all(len(x["options"]) == 4 for x in questions.values()), "Missing MCQ options"
    assert all(ex and trap for _, ex, trap in keys.values()), "Incomplete explanation or distractor rationale"

    bank = rows(BANK)
    assert len(bank) == 100, f"Question CSV has {len(bank)} rows, not 100"
    assert list(map(lambda r: int(r["No"]), bank)) == list(range(1, 101)), "Bank ordering invalid"
    for entry in bank:
        n = int(entry["No"])
        original = questions[n]
        answer, explanation, trap = keys[n]
        assert entry["Section"] == original["section"], f"Section drift in question {n}"
        assert entry["Question"] == original["stem"], f"Stem drift in question {n}"
        for letter in "ABCD":
            assert entry[letter] == original["options"][letter], f"Option {letter} drift in {n}"
        assert entry["Answer"] == answer, f"Answer drift in question {n}"
        assert entry["Explanation"] == explanation, f"Explanation drift in question {n}"
        assert entry["Why the distractors fail"] == trap, f"Distractor drift in {n}"

    deck = rows(DECK)
    assert len(deck) >= 400, f"Unexpectedly short flashcard deck: {len(deck)}"
    seen = set()
    for index, card in enumerate(deck, 1):
        prompt = card["Front"].strip()
        back = card["Back"].strip()
        assert len(prompt) >= 12 and len(back) >= 3, f"Empty/trivial card {index}"
        assert prompt.casefold() not in seen, f"Duplicate flashcard prompt: {prompt}"
        seen.add(prompt.casefold())
        assert card["Tags"].strip(), f"Missing tag in card {index}"

    all_text = "\n".join([*(r["Back"] for r in deck), *(r["Explanation"] for r in bank)])
    forbidden = [
        "Pluripotent source of all the above",
        "marker of the thymus, not a functional unit",
        "the fovea contains cones only",
        "the fovea has only cones",
        "C and D are MALT, not encapsulated organs",
        "rods contain rhodopsin, work in dim light, and are absent from the fovea",
    ]
    for phrase in forbidden:
        assert phrase.casefold() not in all_text.casefold(), f"Stale scientific claim: {phrase}"

    assert "Thymus and spleen" == bank[53]["B"], "Ambiguous Q54 fix not propagated"
    assert "foveola" in bank[97]["Question"].casefold(), "Q98 retina correction not propagated"
    print(f"Study materials PASS: {len(deck)} flashcards; {len(bank)} questions, "
          "100 matching answers, 400 matching options and rationales")


if __name__ == "__main__":
    main()
