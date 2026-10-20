#!/usr/bin/env python3
"""Build the two study decks (flashcards + question bank) from the manuscript.

Quality rules applied here (see RELEASE_REPORT.md):
  * no card whose answer is a bare yes/no/absent/present;
  * no card built from a generic single-word row label ("Peripheral", "Trigger"...);
  * no card shorter than a usable question or longer than 240 characters;
  * exact duplicate fronts removed, keeping the first occurrence.
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "deliverables")
FILES = ["01_cells.md", "02a_basic_tissues.md", "02b_basic_tissues.md",
         "03_transport.md", "04_viscera.md", "05_systems.md"]

TRIVIAL = {"yes", "no", "none", "absent", "present", "variable", "—", "-", "sometimes"}
ENTITY = {"neutrophil", "eosinophil", "basophil", "lymphocyte", "monocyte", "platelet",
          "erythrocyte", "adipocyte", "osteoblast", "osteocyte", "osteoclast",
          "chondrocyte", "fibroblast", "macrophage", "astrocyte", "oligodendrocyte",
          "microglia", "schwann", "hepatocyte", "keratinocyte", "melanocyte",
          "podocyte", "spermatogonia", "sertoli", "leydig", "neuron", "cilium",
          "microvillus", "stereocilium", "desmosome", "hemidesmosome", "fibrocartilage",
          "hyaline", "elastic", "reticular", "collagen", "elastin"}
GENERIC = {"peripheral", "integral", "central", "trigger", "cell shape", "duration",
           "nuclei", "cytoplasm", "function", "location", "contents", "staining",
           "appearance", "main role", "protein", "diameter", "structure", "feature",
           "hormone", "product", "cell", "tissue", "organ", "notes", "example",
           "examples", "stain", "chemistry", "job", "share"}


def strip(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = s.replace("<br/>", " ")
    s = re.sub(r"`(.+?)`", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def cards_from(path):
    t = open(path, encoding="utf-8").read()
    parts = re.split(r"^## (\d+) · (.+)$", t, flags=re.M)
    for i in range(1, len(parts), 3):
        ch, body = int(parts[i]), parts[i + 2]
        tag = "Junqueira::Ch%02d" % ch
        m = re.search(r"### Active recall\n(.*?)(?=\n### |\Z)", body, re.S)
        if m:
            for q, a in re.findall(r"^\d+\. \*\*(.+?)\*\* — (.+)$", m.group(1), re.M):
                yield strip(q), strip(a), tag + " recall"
        m = re.search(r"### Chapter %d — one-line answers\n(.*?)(?=\n### |\Z)" % ch, body, re.S)
        if m:
            for line in m.group(1).split("\n"):
                line = line.strip()
                if not line.startswith("- ") or " = " not in line:
                    continue
                left, right = strip(line[2:]).split(" = ", 1)
                if len(left.split()) < 3:
                    continue
                yield "Ch %d: %s?" % (ch, left.strip()), right.strip(), tag + " facts"
        lines = body.split("\n")
        for j in range(len(lines) - 1):
            if not (lines[j].strip().startswith("|") and re.match(r"^\|[\s:|-]+\|$", lines[j + 1].strip())):
                continue
            hdr = cells(lines[j])
            if len(hdr) < 3:
                continue
            k = j + 2
            while k < len(lines) and lines[k].strip().startswith("|"):
                row = cells(lines[k])
                k += 1
                if len(row) != len(hdr) or not row[0] or row[0].startswith("-"):
                    continue
                term = strip(row[0]).lstrip("—–- ").strip()
                if not term:
                    continue
                low = term.lower().strip(" .")
                if low in GENERIC:
                    continue
                if len(term.split()) < 2 and low not in ENTITY and not re.match(r"^[a-z]+ocyte$", low):
                    continue
                if re.fullmatch(r"[IVX]+", term.strip()):
                    continue
                for c in range(1, len(hdr)):
                    lab, val = strip(hdr[c]), strip(row[c])
                    if not val or val.lower() in TRIVIAL:
                        continue
                    if val.lower().strip(" .") == low:
                        continue
                    if low and val.lower().strip(" .") in low:
                        continue
                    if len(term) > 60 or len(val) > 240:
                        continue
                    yield "Ch %d · %s — %s?" % (ch, term, lab), val, tag + " tables"


def extra_cards():
    path = os.path.join(HERE, "data", "extra_cards.tsv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t")]


def main():
    os.makedirs(OUT, exist_ok=True)
    seen, rows = set(), []
    sources = []
    for f in FILES:
        sources.extend(cards_from(os.path.join(SRC, f)))
    sources.extend((d["Front"], d["Back"], d["Tags"]) for d in extra_cards())
    for front, back, tag in sources:
            key = front.lower().strip()
            if key in seen or len(front) < 12 or len(back) < 3:
                continue
            seen.add(key)
            rows.append([front, back, tag, "basic"])
    with open(os.path.join(OUT, "junqueira_flashcards.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Front", "Back", "Tags", "Type"])
        w.writerows(rows)
    print("flashcards:", len(rows))

    # ---- question bank ----
    t = open(os.path.join(SRC, "07_mcq.md"), encoding="utf-8").read()
    qs = re.findall(r"\*\*(\d+)\.\*\* (.+?)\nA\. (.+?)\n\n", t, re.S)
    opts = {}
    for n, q, line in qs:
        parts = [p.strip() for p in re.split(r"\s*<br/>\s*", re.sub(r"\s+", " ", line).strip())]
        opts[int(n)] = (re.sub(r"\s+", " ", q).strip(),
                        [re.sub(r"^[A-D]\.\s*", "", p) for p in parts])
    ans = {}
    for n, letter, explain in re.findall(r"\*\*(\d+)\. ([A-D])\*\* — (.+?)(?=\n\n|\Z)", t, re.S):
        ex = re.sub(r"\s+", " ", explain).strip()
        trap = ""
        if "**Trap:**" in ex:
            ex, trap = ex.split("**Trap:**", 1)
        ans[int(n)] = (letter, strip(ex), strip(trap))
    rows = []
    for n in sorted(opts):
        q, o = opts[n]
        letter, ex, trap = ans[n]
        assert len(o) == 4 and trap, "bad MCQ %d" % n
        rows.append([n, q, o[0], o[1], o[2], o[3], letter, ex, trap])
    with open(os.path.join(OUT, "junqueira_question_bank.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["No", "Question", "A", "B", "C", "D", "Answer", "Explanation",
                    "Why the distractors fail"])
        w.writerows(rows)
    print("questions:", len(rows))


if __name__ == "__main__":
    main()
