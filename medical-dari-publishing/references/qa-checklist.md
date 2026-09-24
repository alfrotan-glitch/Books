# Quality Assurance, Release Gate, Human Review Gate

## Why this is a separate pass

Every earlier phase is done by someone (or some pass) with their
attention on one thing at a time. QA is the pass where you deliberately
look across the whole finished book for problems that only show up at
the whole-book level — a term that's fine in isolation but inconsistent
with chapter 3's choice, a page break that only looks wrong once real
pagination exists, a reference that got orphaned during restructuring.
Don't treat QA as a formality after the "real" work is done — run it for
real, and be willing to find things.

## QA categories

**Content QA**
Missing chapters, duplicated sections, incomplete sentences, missing
references, broken cross-references.

**Medical QA**
Factual errors, outdated recommendations, terminology inconsistencies,
numerical errors, unit errors, unsafe statements.

**Language QA**
Spelling, grammar, punctuation, Afghan Dari terminology correctness,
Iranian-terminology contamination (re-check even after the dedicated
audit in `references/terminology-hierarchy.md` — things slip back in
during later edits).

**Typography QA**
RTL/LTR problems, broken/corrupted English terms inside Dari text,
incorrect numeral usage, inconsistent spacing, heading hierarchy
consistency.

**Layout QA**
Widows/orphans, bad page breaks, overflowing tables, clipped text,
excessive white space, awkward chapter openings, inconsistent margins.

**EPUB QA**
Invalid structure, broken navigation, malformed XHTML, CSS problems,
RTL failures. Confirm `epubcheck` was actually run and passed — don't
infer validity from the EPUB opening correctly in one app.

## Final release gate

Do not declare a book "complete" merely because files were generated.
Declare it publication-ready only when **all** of the following pass:

- Content audit
- Scientific audit
- Terminology audit
- Afghan Dari audit
- Editorial audit
- Typography audit
- Layout audit
- DOCX validation
- PDF validation
- EPUB validation
- References checked
- Major unresolved issues documented (not hidden)
- Final QA complete across all categories above

If any critical issue remains, state plainly:

```
NOT READY FOR PUBLICATION
```

followed by the specific blocking issue(s). This is the expected,
professional outcome when something is genuinely unresolved — it is not
a failure state to avoid by softening the assessment. A confident "looks
good" that later turns out to have missed something is worse for the
author than an honest "not yet, because X."

## Human review gate

AI editorial work does not replace final professional responsibility for
a medical publication. Explicitly flag these for the author's own
confirmation rather than resolving them unilaterally:

- Controversial medical claims
- Clinical recommendations
- Uncertain Afghan terminology (anything flagged, not silently replaced,
  during the terminology audit)
- Newly changing guidelines
- High-risk medication information
- Legal/copyright issues
- Publication specifications (trim size, print vendor requirements, ISBN,
  etc. — outside this skill's scope but worth flagging if unset)

Don't hide uncertainty to make the deliverable look more finished than it
is. A clearly flagged open question is a feature of a trustworthy
editorial process, not a shortcoming of it.
