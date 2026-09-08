"""Re-join paragraphs that the extraction split in the middle of a sentence (a paragraph ending in a letter/comma
followed by a paragraph that starts with a lowercase letter).  Excludes list items (a-h), tags, headings, tables
and the vocabulary index (whose entries legitimately run on).  Text is never changed, only the paragraph break."""
import re
SKIP_PAGES = set(range(164, 180)) | {117}

def fix_joins(pn, body, log):
    if pn in SKIP_PAGES:
        return body, 0
    paras = re.split(r"\n\s*\n", body.strip("\n"))
    out = []; n = 0
    for q in paras:
        if out:
            a = out[-1]
            joinable = (re.search(r"[a-z,]$", a) and re.match(r"^[a-z]", q) and not re.match(r"^[a-h] ", q)
                        and len(a) > 30 and not a.startswith(("[", "#", "☐", "|")) and not q.startswith(("[", "#", "☐", "**"))
                        and "\n" not in a and "\n" not in q)
            if joinable:
                out[-1] = a + " " + q; n += 1; log.append((pn, a[-30:] + " ‖ " + q[:30])); continue
        out.append(q)
    return "\n" + "\n\n".join(out) + "\n\n\n", n
