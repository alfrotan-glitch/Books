"""Page-specific corrections applied to the rendered text.  Only objectively verifiable repairs (checked against
the page image) — never rewrites.  Literal replacements that stop matching raise a warning so silent drift is
noticed.  PAGE_TEXT replaces the whole page body (used for artwork-only pages such as the cover)."""
import re, sys

# whole-page transcriptions (pages that are artwork / logos with almost no OCR-able text)
PAGE_TEXT = {
    1: """# ACTIVE Skills for Reading 2

Third Edition

Neil J Anderson

National Geographic Learning / Heinle Cengage Learning

[COVER: photograph artwork; title lettering "ACTIVE Skills for Reading", level numeral "2", author name and publisher logos]
""",
}

# (old, new) literal replacements per page; each must match exactly once or a warning is printed
FIXUPS = {
    14: [("{?forjlist}", "for just"), ("“nolding area”", "“holding area”")],
    18: [("interviews ,where", "interviews, where"), ("They, believe", "They believe"), ("arent the best", "aren’t the best")],
    19: [("aiscussion", "discussion"), ("Agood test", "A good test"), ("{?It is}", "It is")],
}

# regions replaced by a verified transcription (page -> list of (regex matching the garbled span, replacement))
REGION_TEXT = {
    64: [
        (r"\(RootWords.*?(?=\n\nB Complete the following letter using words from A\.)",
         "[TABLE 2 columns]\nRoot Words | Meaning\nbio • | • sound\npsych • | • culture\nphon • | • life\nphysio • | • nature / body\ngeo • | • mind\nsocio • | • earth\n[/TABLE]\n\n"
         "1 ________: the study of life\n\n2 ________: the study of the mind\n\n3 ________: the study of the earth\n\n4 ________: the study of speech sounds\n\n5 ________: the study of the body\n\n6 ________: the study of culture"),
        (r"a \(✓\) ________ class called", "a (1) ________ class called"),
        (r"\{\?weeks7can '\. t\} wait to see youl", "weeks—can’t wait to see you!"),
        (r"isn’t\. for me", "isn’t for me"),
        (r"meanings of oot : words", "meanings of root words"),
    ],
    124: [
        (r"\{\?a moleaish\} dich", "a mole dish"),
    ],
    138: [
        (r"# Engineering\n\n# Better \{\?Burger\}", "# Engineering a Better Burger"),
    ],
    51: [
        (r"\[running foot: 50 UNIT 4 Chapter\]", "[running foot: 50 UNIT 4 Chapter 1]"),
    ],
    69: [
        (r"\(Root \| Meaning", "Root | Meaning"),
        (r"opt- I opthalmo- \| eye", "opt- / opthalmo- | eye"),
    ],
    145: [
        (r"1 pound \(Ib\) = 453\.592 grams", "1 pound (lb) = 453.592 grams"),
        (r"1 inch \(in\) = 25 cm", "1 inch (in) = 2.5 cm"),
        (r"4\.5 liters \(I\)", "4.5 liters (l)"),
        (r"0 Celsius \(0C\)", "0 Celsius (°C)"),
        (r"square meters \(sq\?\)", "square meters (sq²)"),
    ],
    26: [
        (r"Greetings from Madrid!.*?Love, Jamie",
         "Greetings from Madrid!\n"
         "I can’t believe I’m finally here. The trip from Seoul was long and (1) ________, but I made it. My (2) ________ is "
         "nice; I’m staying in a guesthouse in the center of Madrid. I got a cheap and (3) ________ room—it only has a small bed "
         "and shower! The weather here is (4) ________ —it’s warm and sunny, with clear blue skies every day. It’s great for "
         "sightseeing, because there’s a wide (5) ________ of things to see and do. Tomorrow I’m taking a train south to "
         "Andalusia to visit the city of Granada. I’m really looking forward to seeing the Alhambra Palace. I’m also really (6) ________ "
         "to try the food—especially gazpacho, a kind of cold soup which I hear is (7) ________ —very different from anything else "
         "in Spain. I promise I’ll bring you back a present. See you next month!\n\nLove, Jamie"),
        (r"Plaza de Santa Ana 21.*?(?=\n\nA Write)", "Plaza de Santa Ana 21\n\nMadrid, Spain\n\n26014\n\n[POSTCARD: stamp artwork; address lines]"),
        (r"A Write the correct form of the adjectives in the box on the lines below\..*?(?=\n\nB Change)",
         "A Write the correct form of the adjectives in the box on the lines below.\n\n"
         "excite   interest   relax   confuse   please   embarrass   bore   worry\n\n"
         "I feel . . . exci ted ________ (handwritten sample answer: “excited”)\n\n"
         "because it’s . . . exci ting ________ (handwritten sample answer: “exciting”)"),
        (r"\(7\) pleas with your", "(7) pleas ________ with your"),
        (r"\(6\) worr— ________", "(6) worr ________"),
        (r"intakingavacationtoan\(3\)excit", "in taking a vacation to an (3) excit"),
        (r"\{\?Want a \(4\) relax\}", "Want a (4) relax"),
    ],
}

# global regular-expression repairs (safe, mechanical)
GLOBAL_RE = [
    (r"(\w)'(\w)", r"\1’\2"),           # straight apostrophe inside a word -> typographic
    (r"\b(\w+) ’ (\w)", r"\1’\2"),
    (r" ,", ","),
    (r"\( ", "("),
    (r" \)", ")"),
    (r"(\d) %", r"\1%"),
]


def apply(pn, text):
    if pn in PAGE_TEXT:
        head = text.split("\n", 1)[0]
        return head + "\n\n" + PAGE_TEXT[pn]
    for old, new in FIXUPS.get(pn, []):
        if old in text:
            text = text.replace(old, new, 1)
        else:
            print(f"FIXUP NOT APPLIED page {pn}: {old!r}", file=sys.stderr)
    for pat, rep in REGION_TEXT.get(pn, []):
        new_text, n = re.subn(pat, rep, text, count=1, flags=re.S)
        if n == 0:
            print(f"REGION FIXUP NOT APPLIED page {pn}: {pat[:40]!r}", file=sys.stderr)
        text = new_text
    for pat, rep in GLOBAL_RE:
        text = re.sub(pat, rep, text)
    return text
