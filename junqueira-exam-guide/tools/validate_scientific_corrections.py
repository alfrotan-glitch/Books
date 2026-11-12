#!/usr/bin/env python3
"""Regression checks for verified high-impact histology corrections.

This is a guard against reintroducing previously identified inaccuracies.
It is not an independent scientific peer review.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
parts = {p.name: p.read_text(encoding="utf-8") for p in ROOT.glob("*.md")}
whole = "\n".join(parts.values()).casefold()

required = {
    "01_cells.md": ["symmetric division", "asymmetric division"],
    "02b_basic_tissues.md": [
        "embryonic yolk-sac myeloid",
        "adult cardiac muscle has very limited regenerative capacity",
    ],
    "03_transport.md": [
        "hematopoietic stem cell (hsc)",
        "**multipotent**",
        "dendritic cells, macrophages, b lymphocytes",
        "hemopexin binds free heme in plasma",
    ],
    "05_systems.md": ["central foveola", "rod-free"],
    "06_rapid.md": ["10.1038/s41583-024-00813-1", "10.1038/nri3818"],
    "07_mcq.md": [
        "which pair of lymphoid organs characteristically lacks afferent lymphatic vessels?",
        "the central foveola (the center of the fovea)",
        "**54. b**",
        "**98. d**",
    ],
}

for name, snippets in required.items():
    text = parts[name].casefold()
    for snippet in snippets:
        assert snippet.casefold() in text, f"Missing science regression marker in {name}: {snippet}"

stale = [
    "microglia, derived from monocytes",
    "microglia are the resident macrophages, derived from monocytes",
    "hematopoietic stem cell** is cd34⁺, self-renewing, and pluripotent",
    "mhc ii is on **apcs** (mostly monocyte-derived)",
    "mhc class ii** — only on **antigen-presenting cells",
    "the fovea contains cones only",
    "the fovea has only cones",
    "cardiac muscle does not regenerate",
    "cns axons do not regenerate",
    "the first work below is the one against which the text was principally checked",
]
for phrase in stale:
    assert phrase not in whole, f"Previously corrected misconception returned: {phrase}"

q = parts["07_mcq.md"]
stems, answers = q.split("## Answer Key with Explanations", 1)
assert "**54.** Which pair" in stems
assert "C. Tonsil and lymph node" in stems
assert "D. Appendix and lymph node" in stems
assert "**54. B**" in answers and "**98. D**" in answers
print("Scientific regression markers PASS: corrected high-impact claims and exam wording.")

# November 2026 target-specific string regressions; not a medical peer review.
targeted = {
    "01_cells.md": ["Most typical cycling animal cells", "primary cilia", "nine microtubule triplets"],
    "02a_basic_tissues.md": ["Embryonic tissue-resident precursors", "yolk-sac-derived CNS macrophages"],
    "05_systems.md": ["pharyngeal endoderm/ultimobranchial-body", "gonadotropin-independent",
                      "not an established fast block in humans", "modify and harden"],
    "06_rapid.md": ["10.1038/s41467-026-73385-6", "10.1002/mrd.23331"],
}
for name, phrases in targeted.items():
    for phrase in phrases:
        assert phrase.casefold() in parts[name].casefold(), f"Missing science marker: {name}: {phrase}"
for stale_phrase in ("each cell has a pair of **centrioles**", "FSH-dependent from this stage",
                     "Membrane depolarization and a **Ca²⁺ wave** trigger"):
    assert stale_phrase.casefold() not in whole, f"Outdated claim returned: {stale_phrase}"
print("November 2026 targeted correction guards PASS; external scientific approval still required.")

# Question-bank semantic audit: a correct answer key is not proof of a true rationale.
q = parts["07_mcq.md"]
assert "**10. A** — A typical primary sensory cilium has a **9 + 0 axoneme**" in q
assert "nine microtubule **triplets**" in q, "Basal-body triplets missing from MCQ 10"
assert "**35. B** — Most resident microglia originate from" in q
assert "**60. C** — Langerhans cells are dendritic" in q
for obsolete in ("The basal body is 9 + 0; the motile cilium",
                 "Microglia are mesodermal, derived from monocytes",
                 "they originate in bone marrow. **Trap:**"):
    assert obsolete.casefold() not in q.casefold(), f"Incorrect exam explanation returned: {obsolete}"
print("Three high-impact MCQ corrections PASS (targeted textual checks, not exam validation).")
