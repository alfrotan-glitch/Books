"""Word-list helpers shared by the fusion / assembly stages."""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
_words = None

EXTRA = """a an the i im ive id ill youre youve youll youd hes shes weve theyre theyve isnt arent wasnt werent dont doesnt didnt
cant couldnt wouldnt shouldnt wont havent hasnt hadnt lets thats whats wheres whos hows theres heres ok okay tv dvd cd cds
dvds mp3 ipod internet online email emails website websites blog blogs blogger bloggers scrapbook scrapbooking scrapbooks
toefl ielts toeic ngl cengage heinle anderson tseng yani dekker laura hmong vietnam vietnamese juliana jamie madrid seoul
andalusia alhambra gazpacho granada montessori waldorf harrison gerontology sudoku wii xbox playstation nintendo smartphone
smartphones app apps facebook twitter youtube google wikipedia texting texted texts multitasking multitask sms selfie
skim skimming scan scanning scanned infer inferring inference paraphrase paraphrasing synonyms antonyms collocation
collocations prefix prefixes suffix suffixes homophones homonyms idiom idioms phrasal ize ise ise ed ing ly er est ness
ment tion sion able ible ful less ous ive al ic ial ity ty un re dis mis pre post inter over under sub super trans en em
non anti bi tri multi semi ex micro macro tele auto bio geo photo graph phon scope logy ology meter ist ian ess ee eer ery
uk usa us cm km kg mph mm ml l g kph lb lbs oz ft in etc vs eg ie am pm bc ad ce bce
""".split()


def words():
    global _words
    if _words is None:
        _words = set()
        f = os.path.join(ROOT, "data", "words.txt")
        if os.path.exists(f):
            _words.update(w.strip().lower() for w in open(f, encoding="utf-8", errors="ignore"))
        _words.update(EXTRA)
    return _words


def is_word(tok):
    """lower-cased token is a known word (also accepts regular plurals / -ed / -ing / -ly / possessives / hyphen compounds)"""
    tok = tok.lower()
    if not tok:
        return False
    W = words()
    if tok in W:
        return True
    if tok.endswith("'s") and tok[:-2] in W:
        return True
    if tok.endswith("s'") and tok[:-1] in W:
        return True
    if "-" in tok:
        parts = [p for p in tok.split("-") if p]
        return bool(parts) and all(is_word(p) for p in parts)
    for suf in ("s", "es", "ed", "d", "ing", "ly", "er", "est", "ness", "ment", "ful", "less"):
        if tok.endswith(suf) and len(tok) > len(suf) + 2:
            stem = tok[:-len(suf)]
            if stem in W or (stem + "e") in W or (stem.endswith(stem[-1] * 2) and stem[:-1] in W) or (stem.endswith("i") and (stem[:-1] + "y") in W):
                return True
    return False


def score(text):
    """fraction of alphabetic tokens (>= 2 letters) that are dictionary words"""
    toks = re.findall(r"[A-Za-z][A-Za-z'\-]+", text)
    if not toks:
        return 0.0
    return sum(1 for t in toks if is_word(t)) / len(toks)
