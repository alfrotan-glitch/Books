"""Corrections applied AFTER the reading-order pass (they depend on the re-ordered text)."""
CORR_POST = []
def c(page, old, new, note=""):
    CORR_POST.append((page, old, new, note))

c(33, "## Jill\n\n“Making 9 Movie\n\n## CHAPTER 1 Behind the Scenes\n\n## Before You Read\n\n", "## UNIT 3\n\n## CHAPTER 1 Behind the Scenes\n\n## Before You Read\n\nMaking a Movie\n\n", "unit banner; sidebar sub-label")
c(113, "## CHAPTER 2 The Truth about Chocolate\n\n## Before You Read\n\n", "## UNIT 9\n\n## CHAPTER 2 The Truth about Chocolate\n\n## Before You Read\n\n", "unit banner")
