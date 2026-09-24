#!/usr/bin/env python3
"""
terminology_scanner.py

Scans one or more manuscript text files against the project's terminology
glossary CSV and reports any occurrence of a "forbidden" / non-preferred
form (e.g. Iranian-Persian variants rejected in favor of an Afghan Dari
form) so they can be reviewed and fixed.

This is a deterministic consistency check, not a substitute for the
actual terminology audit described in
references/terminology-hierarchy.md — it only catches terms the glossary
already knows about. Populate the glossary's forbidden_forms column as
terms get decided during editing; the scanner gets more useful as the
glossary grows.

Usage:
    python3 terminology_scanner.py --glossary glossary.csv manuscript1.md manuscript2.md

Glossary CSV columns expected (see assets/terminology-glossary-template.csv):
    dari_term, english_term, latin_term, abbreviation, preferred_form,
    forbidden_forms, source_authority, usage_notes, first_appearance

`forbidden_forms` may contain multiple variants separated by `;`.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


def load_glossary(path: Path):
    entries = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            forbidden_raw = (row.get("forbidden_forms") or "").strip()
            if not forbidden_raw:
                continue
            forbidden = [t.strip() for t in re.split(r"[;|]", forbidden_raw) if t.strip()]
            if forbidden:
                entries.append(
                    {
                        "preferred_form": (row.get("preferred_form") or row.get("dari_term") or "").strip(),
                        "forbidden": forbidden,
                        "source_authority": (row.get("source_authority") or "").strip(),
                    }
                )
    return entries


# Word-boundary logic for Arabic-script text.
# A plain substring search produced false positives (e.g. forbidden "نای"
# matched inside "معنایش"). A hit now requires:
#   * left boundary: previous char is not an Arabic-script letter and not ZWNJ;
#   * right boundary: next char is not an Arabic-script letter, OR it is ZWNJ
#     (e.g. "بیمار‌ها"), OR the term is followed by a short inflectional suffix
#     and then a boundary (e.g. "بیماران", "درمانی").
# Latin-script forbidden terms use ordinary \b word boundaries.
_AR_LETTER = r"\u0620-\u064A\u066E-\u06D3\u06D5\u06FA-\u06FF"
_SUFFIXES = ["ها", "های", "ان", "ی", "ای", "یی", "ات", "ش", "م", "ت"]


def _pattern(term: str) -> re.Pattern:
    if re.search(r"[\u0600-\u06FF]", term):
        suf = "|".join(sorted((re.escape(s) for s in _SUFFIXES), key=len, reverse=True))
        return re.compile(
            rf"(?<![{_AR_LETTER}\u200c]){re.escape(term)}"
            rf"(?=\u200c|[^{_AR_LETTER}]|$|(?:{suf})(?:[^{_AR_LETTER}]|$))"
        )
    return re.compile(rf"\b{re.escape(term)}\b")


def scan_file(path: Path, entries):
    text = path.read_text(encoding="utf-8")
    hits = []
    seen = set()  # duplicate glossary rows must not produce duplicate hits
    for entry in entries:
        for forbidden_term in entry["forbidden"]:
            for m in _pattern(forbidden_term).finditer(text):
                if (m.start(), forbidden_term) in seen:
                    continue
                seen.add((m.start(), forbidden_term))
                line_no = text.count("\n", 0, m.start()) + 1
                hits.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "found": forbidden_term,
                        "preferred": entry["preferred_form"],
                        "authority": entry["source_authority"],
                    }
                )
    return hits


def main():
    parser = argparse.ArgumentParser(description="Scan manuscript files for non-preferred terminology forms.")
    parser.add_argument("--glossary", required=True, type=Path, help="Path to the terminology glossary CSV")
    parser.add_argument("files", nargs="+", type=Path, help="Manuscript file(s) to scan")
    args = parser.parse_args()

    if not args.glossary.exists():
        print(f"Glossary not found: {args.glossary}", file=sys.stderr)
        sys.exit(1)

    entries = load_glossary(args.glossary)
    if not entries:
        print("No forbidden_forms entries found in glossary — nothing to scan for yet.")
        sys.exit(0)

    all_hits = []
    for file_path in args.files:
        if not file_path.exists():
            print(f"Warning: file not found, skipping: {file_path}", file=sys.stderr)
            continue
        all_hits.extend(scan_file(file_path, entries))

    if not all_hits:
        print("No non-preferred terminology forms found.")
        sys.exit(0)

    print(f"Found {len(all_hits)} occurrence(s) of non-preferred terminology:\n")
    for hit in all_hits:
        print(f"  {hit['file']}:{hit['line']}  '{hit['found']}'  ->  prefer '{hit['preferred']}'  [{hit['authority']}]")

    sys.exit(2)  # nonzero exit so this can be used as a CI-style gate


if __name__ == "__main__":
    main()
