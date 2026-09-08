"""Independent content-QA corrections applied to the FROZEN master text (no pipeline re-run).
Each entry: (page, old, new, note).  `old` must match exactly once in that page's body, otherwise the run aborts,
so nothing silently drifts.  Classification is kept in tools/qa/ledger.json."""
CORR = []
def c(page, old, new, note):
    CORR.append((page, old, new, note))

# ---- p110: upside-down answer key (verified by rotating the page image) ---------------------------------
c(110, "Jeq {?cne/OJOl/J} e 8 {?000°L} 'L OU 9 SPOS al/1 JO POO S {?Sunjuip} v {?SS0p} SPaas ‘Z WIBM l {?(SISMSUY}",
  "[ANSWER KEY, printed upside down at the foot of the page] Answers: 1. warm 2. seeds 3. dogs 4. drinking 5. food of the gods 6. no 7. 1,000 8. a chocolate bar",
  "rotated answer key transcribed from the image")

# ---- p3 copyright page --------------------------------------------------------------------------------
c(3, "Director of Global Marketing: lan Martin", "Director of Global Marketing: Ian Martin", "l/I confusion, verified")
c(3, "Neil Anderson\n\nPublisher, Asia", "Neil J Anderson\n\nPublisher, Asia", "author middle initial printed on the page")
c(3, "[running foot: 12345671615 {?1312}]", "Printed in Canada\n1 2 3 4 5 6 7 16 15 14 13 12", "printing-number line, verified; it is not a running foot")
c(3, "Printed in Canada\n\nPrinted in Canada\n1 2 3", "Printed in Canada\n1 2 3", "merge with the line above (dedupe)")

# ---- p4 acknowledgments (diacritics verified on the image; "Reviewers ot" is printed that way in the book) ----
c(4, "Rajamangala University. of Technology", "Rajamangala University of Technology", "stray period")
c(4, "Hasan Hiiseyin Zeyrek Istanbul {?Kultar} University", "Hasan Hüseyin Zeyrek Istanbul Kültür University", "diacritics verified")
c(4, "Colegio Arnaldo and Centro Universitario Newton Paiva", "Colégio Arnaldo and Centro Universitário Newton Paiva", "diacritics verified")
c(4, "Reviewers for this edition ________ Mardelle", "Reviewers for this edition\n\nMardelle", "the rule after the heading is a divider, not a blank")
c(4, "Reviewers ot the second edition ________ Chiou-lan", "Reviewers ot the second edition [sic — printed thus]\n\nChiou-lan", "divider rule; typo is in the source")

# ---- p7 Vocabulary Learning Tips: three notebook boxes verified on the image ----
c(7, """**New word**

**Translation**

Part of speech Sentence where found

My own sentence

________

**healthy**

# vic JE

adjective Oliver is well-known for sharing his secrets of cooking healthy food. I exercise to stay fit and healthy.""",
"""[NOTEBOOK BOX]
[TABLE 2 columns]
New word | healthy
Translation | 健康
Part of speech | adjective
Sentence where found | Oliver is well-known for sharing his secrets of cooking healthy food.
My own sentence | I exercise to stay fit and healthy.
[/TABLE]""", "label/value notebook box; translation is the Chinese word 健康")
c(7, """Noun Verb Adjective Adverb

**happiness**

happy happily

________ ________

________""",
"""[NOTEBOOK BOX]
[TABLE 2 columns]
Noun | happiness
Verb | (blank)
Adjective | happy
Adverb | happily
[/TABLE]""", "word-family notebook box")
c(7, """**take**

go on need

**have**

**a**

long two-week short summer school

**next week**

**vacation in Italy**

with my family by myself""",
"""[NOTEBOOK BOX — collocation grid, read left to right: verb + a + adjective + vacation + phrase]
[TABLE 5 columns]
take / go on / need / have | a | long / two-week / short / summer / school | vacation | next week / in Italy / with my family / by myself
[/TABLE]""", "collocation grid")

# ---- p8: word web + flash-card figure (visually encoded; verified on the image) ----
c(8, """a frightened child

easily frightened

collocations

terribly frightened

________

unafraid

________

calm

________

unstressed

frightening (adj)

frightful

________

fright (n)

________

________ frighten (v)

frightened ________

________ scared

afraid

________

petrified

terrified""",
"""[WORD WEB — centre: frightened]
[TABLE 2 columns]
collocations | a frightened child / easily frightened / terribly frightened
antonyms | unafraid / calm / unstressed
word family | frightful (adj) / frightening (adj) / fright (n) / frighten (v)
synonyms | scared / afraid / petrified / terrified
[/TABLE]""", "word-web diagram (branches as table rows)")
c(8, """prefix: un- (meaning not)

**unhappily**

suffix: -ly (meaning an adverb)

root: happy""",
"""[DIAGRAM — the word unhappily with three labelled parts]
unhappily → prefix: un- (meaning not); root: happy; suffix: -ly (meaning an adverb)""", "prefix/root/suffix diagram")
c(8, """translation

Front""",
"""[FLASH CARD FIGURE]
Front: cut
Back: potong (translation) — picture of a hand cutting an apple — He is cutting an apple. (example sentence)""", "flash-card figure: card text was missing")

# ---- p11 self-assessment checklist: 12 statements x 2 checkbox columns (verified) ----
c(11, '1 I read something in English every day.\n\n2 I try to read where I’m comfortable and won’t be interrupted.\n\n3 I make predictions about what I’m going to read before I start reading.\n\n4 I think about my purpose of reading before I start reading.\n\n5 I keep my head still, and move only my eyes, when I read.\n\n**Start of course**\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n6 I try not to translate words from English to my first language.\n\n7 I read in phrases rather than word by word.\n\n8 I try to picture in my mind what I’m reading.\n\n9 I read silently, without moving my lips.\n\n10 I try to understand the meaning of the passage, and try not to worry about understanding the meaning of every word.\n\n11 I usually enjoy reading in English.\n\n12 I try to read as much as I can, especially outside class.\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n**End of course**\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n☐\n\n', '[TABLE 3 columns]\nStatement | Start of course | End of course\n1 I read something in English every day. | ☐ | ☐\n2 I try to read where I’m comfortable and won’t be interrupted. | ☐ | ☐\n3 I make predictions about what I’m going to read before I start reading. | ☐ | ☐\n4 I think about my purpose of reading before I start reading. | ☐ | ☐\n5 I keep my head still, and move only my eyes, when I read. | ☐ | ☐\n6 I try not to translate words from English to my first language. | ☐ | ☐\n7 I read in phrases rather than word by word. | ☐ | ☐\n8 I try to picture in my mind what I’m reading. | ☐ | ☐\n9 I read silently, without moving my lips. | ☐ | ☐\n10 I try to understand the meaning of the passage, and try not to worry about understanding the meaning of every word. | ☐ | ☐\n11 I usually enjoy reading in English. | ☐ | ☐\n12 I try to read as much as I can, especially outside class. | ☐ | ☐\n[/TABLE]\n\n', 'checkbox grid re-assembled as a table; 24 boxes preserved')

# ---- p13 Reading Skill B: diagram labels ----
c(13, "a\n\nb\n\nvil\n\nC Read the entire passage", "[DIAGRAMS] a — four ovals arranged in a cycle joined by arrows; b — three ovals in a row joined by left-to-right arrows; c — three overlapping ovals (Venn diagram)\n\nC Read the entire passage", "diagram labels a/b/c; 'vil' was OCR of the label c + line art")

# ---- p15 T/F table numbering + sidebar heading order ----
c(15, """When we learn new facts, we save them in our long-term memory. |  | 
2 You remember better if you start studying a long time before a test. |  | 
Our brains change physically when we learn new information. |  | 
34 / Saying new information out loud is a good way to remernber it: |  | 
5 You don’t""", """1 When we learn new facts, we save them in our long-term memory. |  | 
2 You remember better if you start studying a long time before a test. |  | 
3 Our brains change physically when we learn new information. |  | 
4 Saying new information out loud is a good way to remember it. |  | 
5 You don’t""", "row numbers 1/3/4 restored, 'remernber it:' fixed")
c(15, """## Critical Thinking

## Vocabulary Comprehension

## Words in Context

C Discuss the following questions with a partner.

1 Which study techniques sound useful and which do not? Why? Have you tried any of them?

2 What other ideas do you have for how to study better?

________

A Choose the best answer.""", """## Critical Thinking

C Discuss the following questions with a partner.

1 Which study techniques sound useful and which do not? Why? Have you tried any of them?

2 What other ideas do you have for how to study better?

________

## Vocabulary Comprehension

Words in Context

A Choose the best answer.""", "sidebar headings moved next to the exercises they label")

# ---- p23 Reading Skill: sidebar box and exercises A/B/C were interleaved line by line (verified on image) ----
c(23, '## Reading Skill\n\nA Scan the passage on the next page and find the dates of the four blog\n\nScanning for Details posts.\n\nPost 1: ________\n\nAn important use for Post 2: ________ scanning is to find a Post 3: ________ piece of information Post 4: ________ that we need. We do\n\n**this in everyday life**\n\nB Read each blog post quickly to find the following information.\n\nwhen we look up a word in the dictionary, Post 1: Which city did they go to first? ________ or check a telephone Post 2: Where is the market that they visited? ________ number in the phone Post 3: How long did they go hiking for? ________ directory. Use scanning Post 4: What is in Vung Tau?\n\n________\n\nwhen you need to find\n\na fact in a reading. Now read the entire passage carefully. Then answer the questions on\n\n**page 24.**\n\n________ ________\n\n', '## Reading Skill\n\nScanning for Details\n\nAn important use for scanning is to find a piece of information that we need. We do this in everyday life when we look up a word in the dictionary, or check a telephone number in the phone directory. Use scanning when you need to find a fact in a reading.\n\nA Scan the passage on the next page and find the dates of the four blog posts.\n\nPost 1: ________\n\nPost 2: ________\n\nPost 3: ________\n\nPost 4: ________\n\nB Read each blog post quickly to find the following information.\n\nPost 1: Which city did they go to first? ________\n\nPost 2: Where is the market that they visited? ________\n\nPost 3: How long did they go hiking for? ________\n\nPost 4: What is in Vung Tau? ________\n\nC Now read the entire passage carefully. Then answer the questions on page 24.\n\n', 'reading order: sidebar box separated from exercises A, B, C')

# ---- p51 ----
c(51, "most important meal • of the day", "most important meal of the day", "stray bullet artifact")
c(51, "Then answer the qu {?“Su0NS} Ori page 52.", "Then answer the questions on page 52.", "smudged print in the scan; wording is the standard instruction used in every chapter")

# ---- p107 Real Life Skill box ----
c(107, "by category; easing jobs, io example, will often be listed", "by category; teaching jobs, for example, will often be listed", "OCR: 'easing'→'teaching', 'io'→'for' (context: category Education)")

# ---- p36 Vocabulary Skill (verified on image) ----
c(36, "complete the definitions. ________ agree like appear belief honest connected) ________", "complete the definitions.\n\n[WORD BOX] agree   like   appear   belief   honest   connected", "word box")
c(36, "2\n\n0 vanish\n\n3 ________: feeling", "2 ________: to vanish\n\n3 ________: feeling", "item 2 text")
c(36, "4 ________ :to not enjoy something", "4 ________: to not enjoy something", "spacing")
c(36, "6 ________ :-have a different opinion", "6 ________: have a different opinion", "spacing/artifact")
c(36, "it’s ________ |!", "it’s ________!", "artifact")
c(36, "1 C Complete the following questions using the words from A. asking and answering", "C Complete the following questions using the words from A. Practice asking and answering", "stray '1'; the printed instruction reads 'Practice asking and answering' (verified)")
c(36, "1 Which foods do you ________ 7?", "1 Which foods do you ________?", "artifact")
c(36, ".:3 Do you agree or ________ {?thatitis} possible", "3 Do you agree or ________ that it is possible", "artifact + run-together words")
c(36, "4 Canyoumakeacoin ________ 7?", "4 Can you make a coin ________?", "run-together words + artifact")
c(36, "with the verb appear. The\n\n‘prefix dis- is placed\n\nat the beginning of a noun, verb, or adjective to make the word negative. 9", "with the verb appear. The prefix dis- is placed at the beginning of a noun, verb, or adjective to make the word negative.", "sidebar box paragraph re-joined; stray '9' and quote artifacts removed")

# ---- p31 Real Life Skill (verified on image) ----
c(31, "When you in a foreign country, ve you must complete", "When you arrive in a foreign country, you must complete", "missing word 'arrive' (split by OCR into 've')")
c(31, "Surname: ________ Given name(s): ________ Passport Number: ________ Date of expiry: ________ Place of issue: ________ Permanent address: ________ ________ Dateof ________ _ _ Gender: M F ‘Marital status: ________ Citizenship: ________ Occupation: ________ Purpose of stay: tourism ________ business ________ visit relatives ________ other ________ Length of stay: ________ days",
"""[FORM]
Surname: ________   Given name(s): ________
Passport Number: ________   Date of expiry: ________
Place of issue: ________
Permanent address: ________ ________
Date of birth: ____/____/____   Gender: M  F   Marital status: ________
Citizenship: ________
Occupation: ________
Purpose of stay: tourism ____  business ____  visit relatives ____  other ____
Length of stay: ________ days""", "form laid out line by line; 'Dateof _ _' = 'Date of birth: __/__/__'")

# ---- p42 Review 1 word web (verified on image) ----
c(42, 'computers and video games\n\nexposure to 2\n\n1 ________ points per decade\n\n{?7Tpeopleareless—} ________\n\n________ causes 3 better ________\n\n________\n\nFlynn Effect\n\n________\n\ntechnology intelligence changeind ________\n\n8 ________ nr\n\nIQ tests measures general 5 ________\n\ntests 6 ________ skills\n\nused to learn and get 9 ________\n\nGoogle and Wikipedia\n\n', '[WORD WEB — centre: intelligence]\nintelligence → Flynn Effect → 1 ________ points per decade\nintelligence → Flynn Effect → causes → exposure to 2 ________ ?\nintelligence → Flynn Effect → causes → 3 better ________ ?\nintelligence → Flynn Effect → causes → change in 4 ________ ?\nintelligence → IQ tests → measures general 5 ________\nintelligence → IQ tests → tests 6 ________ skills\nintelligence → technology → 7 people are less ________ → computers and video games\nintelligence → technology → 8 ________ effect?\nintelligence → technology → used to learn and get 9 ________ → Google and Wikipedia\n\n', 'word-web diagram transcribed branch by branch')
c(42, "**Organize**\n\n________ ________ The final stage of PRO", "**Organize**\n\nThe final stage of PRO", "rule artifacts")

# ---- p56 web-browser frame artifacts (verified on image) ----
c(56, "# (000\n\nhttp://sportsspotlight.heinle.com/yanitseng\n\n[TABLE 1 columns]\nlait\n[/TABLE]\n\n# The Unbeatable Yani Tseng\n\n# {?O0COCOCOODOOOOOOOOO}\n\n",
     "[WEB PAGE FRAME — address bar: http://sportsspotlight.heinle.com/yanitseng]\n\n# The Unbeatable Yani Tseng\n\n", "browser buttons and the dotted rule under the title were OCR'd as text")

# ---- p58 (verified on image) ----
c(58, "B complete the following paragraph", "B Complete the following paragraph", "capital")
c(58, "bigger players.” Diasis(4) ________ about his future", "bigger players.” Dias is (4) ________ about his future", "run-together words")
c(58, "play on a 5B) ________ team", "play on a (5) ________ team", "numbered blank")
c(58, "1 {?Doyouconsideryourselfain)} ________ person? Why?", "1 Do you consider yourself a(n) ________ person? Why?", "run-together words")
c(58, "2 {?Haveyouevermetain)} ________ person?", "2 Have you ever met a(n) ________ person?", "run-together words")
c(58, "4 Haveyoueverbeenina(n) ________ situation?", "4 Have you ever been in a(n) ________ situation?", "run-together words")
c(58, "The suffix -ous means to have or to\n\n**be full of.**\n\n________\n\n## Motivational Tip: Why is this reading skill important? You will practice this reading\n\nskill in this chapter,", "The suffix -ous means to have or to be full of.\n\nMotivational Tip: Why is this reading skill important? You will practice this reading skill in this chapter,", "sidebar paragraph re-joined; Motivational Tip paragraph re-joined (not a heading)")

# ---- Motivational Tip boxes split into '## heading' + orphan paragraph: re-joined (verified p89 on image; 'Sucess/suceed' are printed thus) ----
c(65, '## Motivational Tip: What do others say about learning English? Have you read\n\nanything recently in a newspaper or a magazine about the importance of being a good reader? Who made the statement? Many influential people want to improve reading skills among people in their country. Do the leaders in your country have the same goals? How can you support those goals?', 'Motivational Tip: What do others say about learning English? Have you read anything recently in a newspaper or a magazine about the importance of being a good reader? Who made the statement? Many influential people want to improve reading skills among people in their country. Do the leaders in your country have the same goals? How can you support those goals?', 'Motivational Tip paragraph re-joined')
c(79, '## Motivational Tip: How can this be applied beyond the textbook? Reading is\n\na very important life skill and is used every day to accomplish real life tasks. How can the real life skill of doing research on the Internet be used in everyday life? ________', 'Motivational Tip: How can this be applied beyond the textbook? Reading is a very important life skill and is used every day to accomplish real life tasks. How can the real life skill of doing research on the Internet be used in everyday life? ________', 'Motivational Tip paragraph re-joined')
c(89, '## Moti Tip Sucess or Effort or bility? When you suceed, is it\n\nbecause of your effort or your ability? Sucess can be a combination of both, but effort is perhaps more important. When you suceed, remember that it is because of the time you spent working on it. When you fail, remember it is not because you are not good enough, but because you need to spend more time and energy on the task', "Motivational Tip: Sucess or failure? Effort or ability? [sic — printed 'Sucess'] When you suceed, is it because of your effort or your ability? Sucess can be a combination of both, but effort is perhaps more important. When you suceed, remember that it is because of the time you spent working on it. When you fail, remember it is not because you are not good enough, but because you need to spend more time and energy on the task", 'Motivational Tip paragraph re-joined')
c(113, '## Motivational Tip: Strengthen your personal relationships. Your friends can help you\n\nachieve your reading goals. Sharing your goals can also strengthen your personal relationships. As you begin this unit, share with a friend what you hope to learn in this unit about chocolate that will help you become a better user of English.', 'Motivational Tip: Strengthen your personal relationships. Your friends can help you achieve your reading goals. Sharing your goals can also strengthen your personal relationships. As you begin this unit, share with a friend what you hope to learn in this unit about chocolate that will help you become a better user of English.', 'Motivational Tip paragraph re-joined')
c(135, '## Motivational Tip: Review your reading fluency progress. Refer to the reading rate\n\nand reading comprehension charts at the end of the beok. How would you evaluate your progress? Are your scores gradually going up? Use these charts to evaluate the progress you are making. What goals can you set for yourself as you continue to the next unit?', 'Motivational Tip: Review your reading fluency progress. Refer to the reading rate and reading comprehension charts at the end of the beok. How would you evaluate your progress? Are your scores gradually going up? Use these charts to evaluate the progress you are making. What goals can you set for yourself as you continue to the next unit?', 'Motivational Tip paragraph re-joined')
c(144, '## Motivational Tip: Too challenging or too easy? Challenging reading provides the\n\nopportunity to use effective reading strategies. Easier reading provides the opportunity to practice reading fluency. inorder to improve your reading abilities, you will need a combination of both.', 'Motivational Tip: Too challenging or too easy? Challenging reading provides the opportunity to use effective reading strategies. Easier reading provides the opportunity to practice reading fluency. inorder to improve your reading abilities, you will need a combination of both.', 'Motivational Tip paragraph re-joined')

# ---- p59 Real Life Skill: Using Dates (verified on image) ----
c(59, 'People around the WoHd Wika, aid say, the date differently.', 'People around the world write, and say, the date differently.', 'OCR garble verified')
c(59, ' | Written | TEE / Spoken\nIn the U.S.A | March 5, 2007 / 03/05/07 | March fifth, two thousand / SL\nIn England', ' | Written | Spoken\nIn the U.S.A | March 5, 2007 / 03/05/07 | March fifth, two thousand seven\nIn England', "table header/cell artifacts; 'seven' restored")
c(59, 'February 17, 2007 December 25, 2000 October 2, 1999\n\n17 February 2007\n\n25 December 2000\n\n2 October 1999', '[BOX]\nFebruary 17, 2007   December 25, 2000   October 2, 1999\n17 February 2007   25 December 2000   2 October 1999', 'date box kept as two rows')
c(59, 'C. Look at Sam’s calendar', 'C Look at Sam’s calendar', 'artifact')
c(59, 'May\n\n[TABLE 4 columns]\n |  |  | \n | Tr-ip |  | \n8 Vivian’s / dentist / appointment |  |  | \n13 14 |  |  | \ndve / today! |  |  | \n[/TABLE]\n\n28\n\nMovie night with Joe\n\n', '[CALENDAR — May; columns M T W T F S S; 1 = Wednesday]\n[TABLE 7 columns]\nM | T | W | T | F | S | S\n |  | 1 | 2 | 3 | 4 | 5\n6 | 7 | 8 | 9 | 10 | 11 | 12\n13 | 14 | 15 | 16 | 17 | 18 | 19\n20 | 21 | 22 | 23 | 24 | 25 | 26\n27 | 28 | 29 | 30 | 31 |  | \n[/TABLE]\nHandwritten notes on the calendar: 2–5 circled: "Trip to London"; 8: "Vivian\'s dentist appointment"; 12 circled: "Mary\'s birthday party"; 20 circled: "Rent is due today!"; 28 circled: "Movie night with Joe — don\'t forget!"\n\n', 'calendar transcribed (needed for exercise C answers)')

# ---- p62 passage page: upside-down answer key (read from a 180°-rotated crop) + OCR slips verified on image ----
c(62, "\ndv\n\n42\n\n[running foot:", "\n[ANSWER KEY, printed upside down at the foot of the page — answers to Before You Read A on page 60] 1 T; 2 F; 3 T; 4 F; 5 F; 6 T\n\n[running foot:", "rotated answer key decoded")
c(62, "Bad habits lke smoking", "Bad habits like smoking", "OCR slip")
c(62, "only when we get sick feel pain that we. notice.", "only when we get sick or feel pain that we notice.", "missing 'or', stray period")
c(62, "more comfortable lives. 't\n", "more comfortable lives.\n", "artifact")
c(62, "② The human body is a complex machine.\n\n10 From the day we are born,", "② The human body is a complex machine.\n\n[10] From the day we are born,", "line-number marker format")
c(62, "③ 15 Many people do not take care", "③ [15] Many people do not take care", "line-number marker format")

# ---- Dropped 'Circle' (printed inside an oval) and lost capitals at the start of instructions (verified on images p17/25/27/61/68/73/89) ----
c(17, "read the following sentences. the sentence that best describes the main idea of each paragraph.", "read the following sentences. Circle the sentence that best describes the main idea of each paragraph.", "'Circle' drawn in an oval was dropped")
c(25, "A the word or phrase that does not belong in each group.", "A Circle the word or phrase that does not belong in each group.", "'Circle' dropped")
c(27, "B skim the article to check your answers.", "B Skim the article to check your answers.", "capital")
c(61, "A Skim the first paragraph on the next page. the sentence that describes the main idea.", "A Skim the first paragraph on the next page. Circle the sentence that describes the main idea.", "'Circle' dropped")
c(61, "B skim the rest of the paragraphs. paragraph.\n\n**the main idea for each**\n\n**Paragraph 2**", "B Skim the rest of the paragraphs. Circle the main idea for each paragraph.\n\n**Paragraph 2**", "'Circle' dropped; sentence fragments re-joined")
c(61, "Humans are the only animals that cry when upset |  | ", "6 Humans are the only animals that cry when upset |  | ", "row number")
c(68, "B complete the following sentences with the correct form of the words from A,", "B Complete the following sentences with the correct form of the words from A.", "capital; comma→period")
c(73, "A the word or phrase that does not belong in each group.", "A Circle the word or phrase that does not belong in each group.", "'Circle' dropped")
c(89, "B scan the passage on the next page to see if your answers in A were correct.", "B Scan the passage on the next page to see if your answers in A were correct.", "capital")
c(99, "read the sentences below. the sentence that best describes the secret behind each person’s success.", "read the sentences below. Circle the sentence that best describes the secret behind each person’s success.", "'Circle' dropped")
c(102, "C write the occupations from A next to the definitions below.", "C Write the occupations from A next to the definitions below.", "capital")
c(109, "A the correct answer to complete each sentence.", "A Circle the correct answer to complete each sentence.", "'Circle' dropped")
c(112, "B write the meaning of the underlined words, and Circle the words", "B Write the meaning of the underlined words, and circle the words", "capital; mid-sentence 'circle' lower-case")
c(129, "B the correct answers to complete the following sentences.", "B Circle the correct answers to complete the following sentences.", "'Circle' dropped")
c(131, "B skim the remaining paragraphs. Make inferences", "B Skim the remaining paragraphs. Make inferences", "capital")
c(139, "A 0 the word or phrase that does not belong in each group.", "A Circle the word or phrase that does not belong in each group.", "'Circle' oval OCR'd as '0'")

# ---- p68 (verified on image) ----
c(68, "but he has the (M ________ of being", "but he has the (1) ________ of being", "numbered blank")
c(68, "He achieved this feat in 1854, during a (2)", "He achieved this feat in 1954, during a (2)", "digit: 1954 printed (Bannister's record)")
c(68, "between his running group and. a team", "between his running group and a team", "stray period")
c(68, "trained {?with (3)} ________ to achieve", "trained with (3) ________ to achieve", "verified")
c(68, "earningthe (4) ________ of runners", "earning the (4) ________ of runners", "run-together")
c(68, "he would {?only get (5)} ________ from breaking", "he would only get (5) ________ from breaking", "verified")
c(68, "cannot be fully exlained.", "cannot be fully explained.", "OCR slip")
c(68, "• 3 inspire ________", "3 inspire ________", "stray bullet")
c(68, "The Suffix -ion\n\n=\n\nIn this chapter, you saw the noun communication. Many COMMON Nouns in English", "The Suffix -ion\n\nIn this chapter, you saw the noun communication. Many common nouns in English", "artifact; case")

# ---- p92 (verified on image) ----
c(92, "sold out within hours. In an interview before their concert yesterday, guitarist Lee Gray and\n\nlead singer Mark Lang said", "sold out within hours.\n\nIn an interview before their concert yesterday, guitarist Lee Gray and lead singer Mark Lang said", "paragraph break restored to match print")
c(92, "said Lang. The extensive tour continues to Nagoya, Osaka, and Fukuoka\n\nbefore moving to Korea,", "said Lang.\n\nThe extensive tour continues to Nagoya, Osaka, and Fukuoka before moving to Korea,", "paragraph break restored to match print")
c(92, "expect a loud ahd energetic show", "expect a loud and energetic show", "OCR slip")
c(92, "2 ________ —:verytiring", "2 ________: very tiring", "artifact; run-together")
c(92, "3 ________ feeling happy and thrilled", "3 ________: feeling happy and thrilled", "colon")
c(92, "5 ________ made something longer", "5 ________: made something longer", "colon")
c(92, "6 ________ :more than usual; additional", "6 ________: more than usual; additional", "colon")
c(92, "7 ________ an event or happening", "7 ________: an event or happening", "colon")
c(92, "to form nouns, verbs, adjectives, and\n\nadverbs in English. It means upwards, completely, without and Ter", "to form nouns, verbs, adjectives, and adverbs in English. It means upwards, completely, without, and former.", "sidebar paragraph re-joined; 'Ter' = 'former.' (verified)")

# ---- p95 (T/F & P/W/H/L tables; verified structure) ----
c(95, " |  |  | H | \n1 This album talks", " | P | W | H | L\n1 This album talks", "table header letters restored per instruction B")
c(95, "3 Fans are told to get the live recordings / of this album’s songs instead. / 4 The artist was already famous before / this album was released.” |  |  |  | \n", "3 Fans are told to get the live recordings / of this album’s songs instead. |  |  |  | \n4 The artist was already famous before / this album was released. |  |  |  | \n", "rows 3 and 4 were merged; stray quote")
c(95, "5 This album Was released by a British", "5 This album was released by a British", "case")
c(95, "changes people’s ideas ________ a quickly\n\nb slowly", "changes people’s ideas ________\n\na quickly\n\nb slowly", "answer choice layout")
c(95, "who is able to see it? a the public\n\nb the writer", "who is able to see it?\n\na the public\n\nb the writer", "answer choice layout")
c(95, "3 Mature people usuallyhave ________ experience. a less\n\nb more", "3 Mature people usually have ________ experience.\n\na less\n\nb more", "run-together; answer choice layout")

# ---- p96 (verified on image) ----
c(96, "4 Who is likely to create an album? a a writer\n\nb a musician", "4 Who is likely to create an album?\n\na a writer\n\nb a musician", "answer choice layout")
c(96, "5 Which is an example of statement? a ‘Is that the right thing to do? b What you are doing is wrong.", "5 Which is an example of statement?\n\na Is that the right thing to do?\n\nb What you are doing is wrong.", "answer choice layout; artifact quote")
c(96, "8 If you. incorporate A into B, you ________ a add A to B\n\nb replace A with B", "8 If you incorporate A into B, you ________\n\na add A to B\n\nb replace A with B", "stray period; layout")
c(96, "Use each in a sentence. below.", "Use each in a sentence below.", "stray period")
c(96, "**effect n. a change that is caused bid something the result**\n\n“something\n\naffect fect/ v. todo something that Rae someone or something", "[DICTIONARY BOX]\neffect /ɪˈfekt/ n. a change that is caused by something or is the result of something\naffect /əˈfekt/ v. to do something that changes someone or something", "dictionary box re-transcribed from the image")
c(96, "for my trip Spain.", "for my trip to Spain.", "missing word verified")
c(96, "7 Smoking drinking too much can", "7 Smoking and drinking too much can", "missing word verified")

# ---- p106 online job ads (verified on image): '(✓)'→'(1)', {?adventur} resolved, 'Read more' buttons, stem+blank layout ----
c(106, '________ introverted adventurous responsible creative patient energetic hard-working ________\n\nB Complete the online job ads below with the appropriate adjective endings. Use your dictionary to help you.\n\n**JOBS AVAILABLE**\n\nLooking for a (✓) self-motivat ________ and (2) effect ________ teacher to join the staff at our elementary school. You must have a teaching certificate and at least five years’ experience to apply. Must also be\n\n(3) interest ________ in working with children ages 6-9.\n\n________\n\n## Read more\n\nWant to make $5,000 a month working in shorts and a T-shirt? Water World, the swimming pool specialist, has an immediate opening for an (4) {?adventur} ________ and (5) assert ________ salesperson in the Boston area.\n\n________\n\n## C Read more\n\nWe have an immediate job opening for an (6) experienc ________\n\n(7) flex ________ secretary in our very busy downtown office.\n\n________\n\nRead more\n\nScorePro, a software company that creates fun and educational math materials for children, is looking for a (8) dynam\n\n(9) enthusiast ________ computer programmer to join our company.\n\n________\n\n## C Read more\n\n', '[WORD BOX — the adjective endings are underlined in print] introverted   adventurous   responsible   creative   patient   energetic   hard-working\n\nB Complete the online job ads below with the appropriate adjective endings. Use your dictionary to help you.\n\n[WEB PAGE FRAME]\n\n**JOBS AVAILABLE**\n\nLooking for a (1) self-motivat________ and (2) effect________ teacher to join the staff at our elementary school. You must have a teaching certificate and at least five years’ experience to apply. Must also be (3) interest________ in working with children ages 6–9.\n\n[Read more >>]\n\nWant to make $5,000 a month working in shorts and a T-shirt? Water World, the swimming pool specialist, has an immediate opening for an (4) adventur________ and (5) assert________ salesperson in the Boston area.\n\n[Read more >>]\n\nWe have an immediate job opening for an (6) experienc________, (7) flex________ secretary in our very busy downtown office.\n\n[Read more >>]\n\nScorePro, a software company that creates fun and educational math materials for children, is looking for a (8) dynam________, (9) enthusiast________ computer programmer to join our company.\n\n[Read more >>]\n\n', 'job-ads block re-transcribed')
c(106, "differentiate them from\n\n①\n\nother word forms.", "differentiate them from other word forms.", "sidebar paragraph re-joined; stray disc artifact")
c(106, "Share your answers with a partner.\n\n________\n\n________\n\nMotivational Tip: Reflect", "Share your answers with a partner.\n\nMotivational Tip: Reflect", "rule artifacts")
c(106, "and then celebrate.\n\n________ ________\n\n[running foot", "and then celebrate.\n\n[running foot", "rule artifacts")

# ---- p97 / p102 run-together words ----
c(97, "4 I studied really hard for thisexam,solatleast ________ to-pass.", "4 I studied really hard for this exam, so I at least ________ to pass.", "run-together words; hyphen artifact")
c(102, "1 {?I’dliketohaveain)} ________ business selling", "1 I’d like to have a(n) ________ business selling", "run-together words")
c(102, "4 Mr. Galison is very ________ ;hisbusiness ________ always seem", "4 Mr. Galison is very ________; his business ________ always seem", "run-together words")
c(97, "Dictionary Usage Choosing the Right Word", "Dictionary Usage: Choosing the Right Word", "colon as printed in Contents")
c(97, "but are not exactly: the same.", "but are not exactly the same.", "artifact")
c(97, "choose the correct word\n\nA Expect,", "choose the correct word.\n\nA Expect,", "period")
c(97, "I expect it to be sunny. tomorrow,", "I expect it to be sunny tomorrow,", "artifact")
c(97, "Example: / look forward to going", "Example: I look forward to going", "I/slash")
c(97, "with my friends.\n\na\n\n1 The audience", "with my friends.\n\n1 The audience", "artifact")

# ---- p124 Review Reading 6 (verified on image) ----
c(124, "**Review Reading 6: Savory Chocolate**\n\n________ ________\n\n## Fluency Practice", "**Review Reading 6: Savory Chocolate**\n\n## Fluency Practice", "rule artifacts")
c(124, "They get their complex flavor and dark brown\n\ncolor from chili peppers", "They get their complex flavor and dark brown color from chili peppers", "paragraph wrongly split at the photo")
c(124, "sauce called agrodoice also uses", "sauce called agrodolce also uses", "OCR slip (Italian 'agrodolce')")
c(124, "Chefs and home cooks [20]\n\na mole dish\n\nalike are rubbing steaks with cocoa powder and adding pieces of chocolate\n\nto meat stews.", "Chefs and home cooks [20] alike are rubbing steaks with cocoa powder and adding pieces of chocolate to meat stews.\n\n[PHOTO CAPTION: a mole dish]", "paragraph re-joined; photo caption separated")

# ---- p134 (verified on image) ----
c(134, "B Complete these advertisements with the correct word from the chart.\n\n## Vocabulary Skill\n\nWord Families\n\nWhen you learn a new word in English, g it is helpful", "## Vocabulary Skill\n\nWord Families\n\nWhen you learn a new word in English, it is helpful", "artifact 'g'; heading moved before the exercise it labels (see next correction)")
c(134, "expand your vocabulary.\n\nShy? Lacking confidence?", "expand your vocabulary.\n\nB Complete these advertisements with the correct word from the chart.\n\n[AD 1] Shy? Lacking confidence?", "instruction B placed directly before the ads")
c(134, "speaking in public (✓) ________ you, our program will change your life. With (2) ________ coacheswhowill(8) ________ you every step of the way, you’ll soon overcome your fear. ________ ________\n\n________\n\nHere’sa(n) (4) ________ for people who (8) ________ the finer things", "speaking in public (1) ________ you, our program will change your life. With (2) ________ coaches who will (3) ________ you every step of the way, you’ll soon overcome your fear.\n\n[AD 2] Here’s a(n) (4) ________ for people who (5) ________ the finer things", "blank numbers (1),(3),(5) verified; run-together words; rule artifacts")
c(134, "The only limit is your (6) ________ ________ ________\n\nIf bad breath is your (7) ________ chew on our new Minty Bits. Try the freshest sweets in town, guaranteed to get rid of (8) ________ smells! ________ ________", "The only limit is your (6) ________.\n\n[AD 3] If bad breath is your (7) ________, chew on our new Minty Bits. Try the freshest sweets in town, guaranteed to get rid of (8) ________ smells!", "rule artifacts; punctuation")
c(127, "A Scanthe passage on the next page for proper nouns. Write the proper nouns you find in each paragraph below. Then 6 the correct option.", "A Scan the passage on the next page for proper nouns. Write the proper nouns you find in each paragraph below. Then circle the correct option.", "run-together; 'circle' in an oval OCR'd as '6'")
c(127, "Then circle the correct option.\n\n________\n\nParagraph 2 ________ 00\n\nThis paragraph is probably about (clothing / exercise).\n\n**Paragraph 3 ________**\n\nThis paragraph is probably about (drinks people buy / entertainment).\n\n**Paragraph ________**\n\nThis paragraph is probably about (the Internet / animals).",
       "Then circle the correct option.\n\n**Paragraph 2** ________\n\nThis paragraph is probably about (clothing / exercise).\n\n**Paragraph 3** ________\n\nThis paragraph is probably about (drinks people buy / entertainment).\n\n**Paragraph 5** ________\n\nThis paragraph is probably about (the Internet / animals).", "Paragraph 5 label restored; artifacts removed (verified)")
c(127, "Motivational Tip: Set class goal.", "Motivational Tip: Set a class goal.", "missing article — verify")

# ---- p135 (verified on image) ----
c(135, "use words like vam or\n\n**cuddly.**", "use words like warm or cuddly.", "OCR 'vam'→'warm'; box paragraph re-joined")
c(135, "charts at the end of the beok.", "charts at the end of the book.", "OCR slip")

# ---- p139 (verified on image) ----
c(139, "has risen by (✓) ________ in the last 50 years", "has risen by (1) ________ in the last 50 years", "(1) misread as check mark")
c(139, "causes a lot of (6) But science", "causes a lot of (6) ________. But science", "blank (6) missing")
c(139, "flavors from (✓) ________; they believe", "flavors from (11) ________; they believe", "(11) misread as check mark")
c(139, "any meat altematives that", "any meat alternatives that", "OCR slip")
c(139, "1 struggle relax rest\n\n2 ask consequence demand\n\n3 attracting polluting damaging\n\n4 anticipation feeling emotion\n\n5 limitation choice alternative\n\n6 support keep up limit\n\n7 interested curious keen on\n\n8 chemical fake manufactured\n\ncalm down request\n\nmood option\n\ndisgusted natural",
      "1 struggle   relax   rest   calm down\n\n2 ask   consequence   demand   request\n\n3 attracting   polluting   damaging\n\n4 anticipation   feeling   emotion   mood\n\n5 limitation   choice   alternative   option\n\n6 support   keep up   limit\n\n7 interested   curious   keen on   disgusted\n\n8 chemical   fake   manufactured   natural", "fourth column re-attached to its rows")

# ---- p154 (verified on image) ----
c(154, 'Opening this week is Eat Less/Live More, a movie that follows the journey of Jacob Harris from (✓) achiever to environmental hero. At the start of the movie, Jacob is 30 kilograms (2) weight and miserable in his (3) paid job. When his car (4) ________ heats one hot summer day, he decides to walk to work. This inspires him to think of ways he can lose weight while living a more sustainable life. As his transformation gets (5) way, the benefits turn out to be mental as much as physical, like in one hilarious scene where he stands up to a colleague who keeps trying to (6) mine him. This moviehasan(?) ________ {?stated style and ari (8)} ________ sized heart. 9/10', 'Opening this week is Eat Less/Live More, a movie that follows the journey of Jacob Harris from (1) ________ achiever to environmental hero. At the start of the movie, Jacob is 30 kilograms (2) ________ weight and miserable in his (3) ________ paid job. When his car (4) ________ heats one hot summer day, he decides to walk to work. This inspires him to think of ways he can lose weight while living a more sustainable life. As his transformation gets (5) ________ way, the benefits turn out to be mental as much as physical, like in one hilarious scene where he stands up to a colleague who keeps trying to (6) ________ mine him. This movie has an (7) ________ stated style and an (8) ________ sized heart. 9/10', 'movie review re-transcribed: blanks (1)-(8) restored')
c(154, "can put {?a(n)} ________ on a relationship?", "can put a(n) ________ on a relationship?", "verified")
c(154, "3 Thetigerisa(n) ________ animal.", "3 The tiger is a(n) ________ animal.", "run-together")
c(154, "difficult to ________ t.", "difficult to ________ it.", "verified")
c(154, "Word / (| over | under | Word | over | under\n1 weight |  |  | paid |  | ", "Word | over | under | Word | over | under\n1 weight |  |  | 6 paid |  | ", "header artifact; item 6 number")
c(154, "improve your vocabullary skills. ________ ________", "improve your vocabullary skills. [sic — printed thus]", "typo is in the source; rule artifacts removed")

# ---- '(1)' printed inside a circle misread as '(✓)' (systematic; verified on p106/p134/p139/p154) ----
c(67, "The human body really is amazing. (✓) ________ was a teenager", "The human body really is amazing. (1) ________ was a teenager", "(1) misread")
c(74, "A: It’squitea(n) (✓) ________ to get into a university like Harvard or Yale. B: Yes, (20 ________ but", "A: It’s quite a(n) (1) ________ to get into a university like Harvard or Yale.\n\nB: Yes, I (2) ________, but", "(1) misread; 'I (2)' garbled to '(20'; run-together; dialogue turns (verified)")
c(75, "from favorite (✓) to least favorite (8).", "from favorite (1) to least favorite (8).", "(1) misread")
c(130, "This (✓) ________ formal style of dress", "This (1) ________ formal style of dress", "(1) misread")
c(74, "test—it’s a(n) (3) ________\n\nA: Well, if you want to go there, you’ll need to (4) ________ your test score. B: I know, but my current score is still a(n) (6) ________ over last month’s. A: Well, I’m sure", "test—it’s a(n) (3) ________.\n\nA: Well, if you want to go there, you’ll need to (4) ________ your test score.\n\nB: I know, but my current score is still a(n) (5) ________ over last month’s.\n\nA: Well, I’m sure", "blank (5) misnumbered as (6); dialogue turns (verified)")

# ---- p145 (verified on image) ----
c(145, "use Non-metric measures, of a combination of both. The metric system uses prefixes to indicate the size of the number. The [nosh Comman; yer are milli (0.001)", "use non-metric measures, or a combination of both. The metric system uses prefixes to indicate the size of the number. The most common prefixes are milli (0.001)", "OCR garble verified")
c(145, "wetght temperature distance volume length area", "[WORD BOX] weight   temperature   distance   volume   length   area", "OCR slip; word box")
c(145, "weight | 1 pound (lb) = 453.592 grams", "weight (example answer, handwritten) | 1 pound (lb) = 453.592 grams", "first cell is the printed example answer")
c(145, "big cold heavy hot less light long more short small\n\n1 One pound is lighter than one kilogram.", "[WORD BOX] big   cold   heavy   hot   less   light   long   more   short   small\n\n1 One pound is lighter (example answer, handwritten) than one kilogram.", "word box; example answer marked")
c(145, "4 One kilometer is ________ than one mile. 5 50 ° F is ________ than 50 ° C.", "4 One kilometer is ________ than one mile.\n\n5 50 °F is ________ than 50 °C.", "items split; degree spacing")

# ---- p28 Safe Travel passage (verified on image; the missing word after 'Jamaica and' is missing in the printed book too) ----
c(28, "# Sate {?Travel}", "# Safe Travel", "title verified")
c(28, "during your trip is he last thing you want to happen. Be sure to get an international driver’s license if you plan o drive while you are abr", "during your trip is the last thing you want to happen. Be sure to get an international driver’s license if you plan to drive while you are abr", "lost first letters (t)")
c(28, "[10] ike Jamaica and —use more than one currency.", "[10] like Jamaica and —use more than one currency. [sic — a word is missing in the printed book]", "lost first letter; source omission documented")
c(28, "f you need to take medication along", "If you need to take medication along", "lost first letter")
c(28, "AS a tourist, you’ll probably", "As a tourist, you’ll probably", "case")
c(28, "the amazing sights and the other\n\n[20]\n\non your personal items.", "the amazing sights and the other [20] on your personal items.", "line-number marker inside paragraph")
c(28, "keeping it in front of you or\n\n[25]\n\nbetween your legs.", "keeping it in front of you or [25] between your legs.", "line-number marker inside paragraph")
c(28, "[30] Learn About the Locals\n\nIt’s always", "[30] **Learn About the Locals**\n\nIt’s always", "sub-heading bold like the others")
c(154, "More than the definition. aster completing this vocabulary exercise", "More than the definition. After completing this vocabulary exercise", "OCR slip verified")

# ---- p35 / p48 ----
c(35, "2 ________ Inascene, a man sits in a car from the 1990s and uses\n\na cell phone.", "2 ________ In a scene, a man sits in a car from the 1990s and uses a cell phone.", "run-together; wrapped line re-joined")
c(35, "4 ________ The hero’s skin looks green after he returns from his\n\nspace flight.", "4 ________ The hero’s skin looks green after he returns from his space flight.", "wrapped line re-joined")
c(35, "5 ________ Afire starts in the family’s kitchen.", "5 ________ A fire starts in the family’s kitchen.", "run-together")
c(48, "Volunteering is something. that anyone can do", "Volunteering is something that anyone can do", "stray period")

# ---- p52 Laura Dekker passage (verified on image) ----
c(52, "# Recor\n\nAll athletes aspire", "# Laura Dekker: Record-Setter!\n\nAll athletes aspire", "title")
c(52, "achieve that goal. As a child, Laura Dekker loved\n\n[10] the sea.", "achieve that goal.\n\nAs a child, Laura Dekker loved [10] the sea.", "paragraph break as printed")
c(52, "at the age of 6 years-and 123 days, and was greeted by her family, friends, and many. fans.", "at the age of 16 years and 123 days, and was greeted by her family, friends, and many fans.", "'16' verified; artifacts")
c(52, "[30] \"However, Guinness World Records", "[30] However, Guinness World Records", "stray quote")
c(52, "helped her to focus en-the important things inher life. \"I became good friends", "helped her to focus on the important things in her life. “I became good friends", "OCR slips; quote mark")
c(52, "[35] \"I learned a lot about myself.”", "[35] “I learned a lot about myself.”", "quote mark")
c(52, "she visited exotic islands like the Galapagos,", "she visited exotic islands like the Galápagos,", "diacritic verified")

# ---- p63 / p64 ----
c(63, "1 Which is an example of an iliness?", "1 Which is an example of an illness?", "OCR slip")
c(63, "What does surgery involve?", "2 What does surgery involve?", "item number")
c(63, "a aninjury-", "a an injury", "run-together; artifact")
c(64, "learning about volanoes and earthquakes, so maybe I’ll take a (3) ________ Class next year. ‘I’m coming home", "learning about volcanoes and earthquakes, so maybe I’ll take a (3) ________ class next year. I’m coming home", "OCR slip; case; artifact")
c(64, "Dear Aunt Marie, How are you?", "Dear Aunt Marie,\n\nHow are you?", "letter salutation line")

# ---- p94 Album Reviews: right-hand column (Marvin Gaye / The Clash) was collapsed into one paragraph; re-structured per image ----
c(94, '**Marvin Gaye What’s Going On (1971)**\n\nLength 35:38 In the late 1960s, American soul singer Marvin Gaye saw many problems around him— war, poverty’, homelessness, the negative effects of drug use—and felt the need to make a statement. What’s Going On is written from the perspective of a war veteran,² and the songs comment on social problems in a way that soul music never had before. Gaye’s record company was sure the record—his 11th—would fail, but the title track was very successful, and so was the record. What’s Going On was the first of many soul records to take on social issues. In short: This is an important record for any music fan. Focus your attention othe {?iyrics} to really understand.the music. The Clash - London calling (1979) Length 65:07 Punk pioneers The Clash crossed many music boundaries with their third album, London Calling. While the band kept their original punk sound, these songs also incorporate bits of jazz, ska, reggae, pop, and soul. The Clash were known for expressing their political views through their music, and London Calling comments on many problems in Britain at that time. This album showed that punk can and should be taken seriously. In short: This album is a great introduction to punk rock, but for true fans, spend your money on the rare live-music recordings.\n\nSomeone living in poverty is very poor.\n\n2 A veteran is someone who has fought in a war.\n\n² An acoustic guitar is a traditional guitar that doesn’t use electricity.\n\n', '**Marvin Gaye – What’s Going On (1971)**\n\nLength 35:38\n\nIn the late 1960s, American soul singer Marvin Gaye saw many problems around him—war, poverty¹, homelessness, the negative effects of drug use—and felt the need to make a statement. What’s Going On is written from the perspective of a war veteran,² and the songs comment on social problems in a way that soul music never had before. Gaye’s record company was sure the record—his 11th—would fail, but the title track was very successful, and so was the record. What’s Going On was the first of many soul records to take on social issues.\n\nIn short: This is an important record for any music fan. Focus your attention on the lyrics to really understand the music.\n\n**The Clash – London Calling (1979)**\n\nLength 65:07\n\nPunk pioneers The Clash crossed many music boundaries with their third album, London Calling. While the band kept their original punk sound, these songs also incorporate bits of jazz, ska, reggae, pop, and soul. The Clash were known for expressing their political views through their music, and London Calling comments on many problems in Britain at that time. This album showed that punk can and should be taken seriously.\n\nIn short: This album is a great introduction to punk rock, but for true fans, spend your money on the rare live-music recordings.\n\n¹ Someone living in poverty is very poor.\n\n² A veteran is someone who has fought in a war.\n\n³ An acoustic guitar is a traditional guitar that doesn’t use electricity.\n\n', "review layout restored; 'othe {?iyrics}' = 'on the lyrics'; footnote numbers 1/2/3")
c(94, "**The Beach Boys Pet Sounds (1966)**", "**The Beach Boys – Pet Sounds (1966)**", "dash as printed")
c(94, "**Bob Dylan Highway 61 Revisited (1965)**\n\nLength 51 :26", "**Bob Dylan – Highway 61 Revisited (1965)**\n\nLength 51:26", "dash; spacing")
c(94, "playing the acoustic guitar, 3 and singing", "playing the acoustic guitar,³ and singing", "footnote ref")
c(94, "politics and culture in\" America", "politics and culture in America", "artifact")
c(94, "[15] Sgt. Pepper’s Lonely Hearts Club Band. In short: This is a great record", "[15] Sgt. Pepper’s Lonely Hearts Club Band.\n\nIn short: This is a great record", "'In short' line as printed")
c(78, "4 The ________ in apassage contains details.", "4 The ________ in a passage contains details.", "run-together")
c(87, "b Ahletes generally don’t like playing video games.", "b Athletes generally don’t like playing video games.", "OCR slip")
c(128, "Companies {?activel Z 1} seek to sponsor concerts", "Companies actively seek to sponsor concerts", "OCR garble of 'actively' — verify")

# ---- T/F-style tables: missing row numbers / header letters (verified on images p15, p61, p115; same layout elsewhere) ----
c(19, "Multiple-choice tests are a good way to evaluate / intelligence. |  | ", "1 Multiple-choice tests are a good way to evaluate / intelligence. |  | ", "row number")
c(35, "The names of people who work behind the scenes are not / in the movie credits. |  | ", "1 The names of people who work behind the scenes are not / in the movie credits. |  | ", "row number")
c(53, "Lauragot the idea to sail around the world when she was 15. |  | ", "1 Laura got the idea to sail around the world when she was 15. |  | ", "row number; run-together")
c(115, "B Read the following sentences. Check (✓) if they are shown as positive +) or negative in the article.\n\n[TABLE 3 columns]\n |  | \n1 Chemicals", "B Read the following sentences. Check (✓) if they are shown as positive (+) or negative (–) in the article.\n\n[TABLE 3 columns]\n | + | –\n1 Chemicals", "header symbols verified")
c(115, "When eaten, cocoa butter can coat the teeth. |  | ", "5 When eaten, cocoa butter can coat the teeth. |  | ", "row number")
c(133, "[TABLE 3 columns]\n | A | c\nConsumers thought the brand was hurting people’s feelings. |  | ", "[TABLE 3 columns]\n | A | C\n1 Consumers thought the brand was hurting people’s feelings. |  | ", "header letter; row number")
c(133, "Consumers could vote for the winner. |  | ", "5 Consumers could vote for the winner. |  | ", "row number")

# ---- 'true (T)' printed in italic T misread as '7' ----
c(25, 'A Read the following sentences. Check (✓) true (7) or false (F). Then check the number of the post where you found the answer.', 'A Read the following sentences. Check (✓) true (T) or false (F). Then check the number of the post where you found the answer.', 'T misread as 7')
c(39, 'B Read the following sentences. Check (✓) true (7) or false (F).', 'B Read the following sentences. Check (✓) true (T) or false (F).', 'T misread as 7')
c(53, 'B Read the following sentences. Check (✓) true (7) or false (F).', 'B Read the following sentences. Check (✓) true (T) or false (F).', 'T misread as 7')
c(57, 'B Read the following sentences. Check (✓) true (7) or false (F).', 'B Read the following sentences. Check (✓) true (T) or false (F).', 'T misread as 7')
c(61, 'A Read the following sentences and check (✓) true (7) or false (F).', 'A Read the following sentences and check (✓) true (T) or false (F).', 'T misread as 7')
c(73, 'B Read the following sentences. Check (✓) true (7) or false (F).', 'B Read the following sentences. Check (✓) true (T) or false (F).', 'T misread as 7')
c(113, 'A Skim the paragraphs numbered 1-5 in the article on the next page. Then read the sentences below and check (✓) if they are true (7), somewhat true (S), or false (F).', 'A Skim the paragraphs numbered 1-5 in the article on the next page. Then read the sentences below and check (✓) if they are true (T), somewhat true (S), or false (F).', 'T misread as 7')
c(133, 'A Read the following sentences. Check (✓) true (7) or false (F).', 'A Read the following sentences. Check (✓) true (T) or false (F).', 'T misread as 7')

# ---- table headers: letters garbled by OCR (headers are defined by the exercise instruction) ----
c(57, " | T | F\"\n", " | T | F\n", "artifact")
c(75, " | Very / true | Somewhat / true | Not true' / at all\n", " | Very / true | Somewhat / true | Not true / at all\n", "artifact")
c(77, "true for television (T) or the Internet (/).\n\n[TABLE 3 columns]\n | T | \n", "true for television (T) or the Internet (I).\n\n[TABLE 3 columns]\n | T | I\n", "header I per instruction")
c(105, "[TABLE 3 columns]\n |  | [TIF\n1 A person can fit", "[TABLE 3 columns]\n | T | F\n1 A person can fit", "header per instruction")
c(111, "[TABLE 3 columns]\n | T | 2\n1 Christopher Columbus", "[TABLE 3 columns]\n | T | F\n1 Christopher Columbus", "header per instruction")
c(113, "[TABLE 4 columns]\n | T | g | \n1 Eating chocolate makes you happier. |  |  | {?F \"}\n", "[TABLE 4 columns]\n | T | S | F\n1 Eating chocolate makes you happier. |  |  | \n", "header per instruction")
c(153, "true for water (W) or rain forests (R).\n\nha\n\n[TABLE 3 columns]\n | w | R\n", "true for water (W) or rain forests (R).\n\n[TABLE 3 columns]\n | W | R\n", "artifact 'ha'; header W")

# ---- p55 photo-text artifacts; photo captions ----
c(55, "## CHAPTER 2 The Unbeatable Yani Tseng\n\nNOT.\n\nOR SALE\n\nSAIN.\n\nFOR\n\nVenus and Serena\n\nWilliams, tennis players\n\nUsain Bolt, sprinter\n\nManny Pacquaio, boxer\n",
      "## CHAPTER 2 The Unbeatable Yani Tseng\n\n[PHOTO CAPTIONS: Venus and Serena Williams, tennis players / Usain Bolt, sprinter / Manny Pacquaio, boxer]\n",
      "text inside photo (poster fragments) removed; captions joined")
# ---- p131 two product cards (side by side) ----
c(131, "CHAPTER 2 Brand Engagement Gone Wrong\n\n**Rett s Alligator Luggage**\n\n☐\n\nClean-Up Kwik Set\n\nc::) Unbreakable case c::) Comes in many attractive colors\n\nc::) Easy to wheel around\n\nc::) Everything you need to clean the house\n\nc::) Pretty and color-coordinated c::) Easy to store when you’re done\n",
      "## CHAPTER 2 Brand Engagement Gone Wrong\n\n[AD 1] **Rett’s Alligator Luggage**\n\n• Unbreakable case\n\n• Comes in many attractive colors\n\n• Easy to wheel around\n\n[AD 2] **Clean-Up Kwik Set**\n\n• Everything you need to clean the house\n\n• Pretty and color-coordinated\n\n• Easy to store when you’re done\n",
      "two product cards separated; arrow bullets")

# ---- stray punctuation artifacts before words (verified against the page image) ----
c(29, "1 'ltis important to be prepared", "1 It is important to be prepared", "OCR")
c(35, "5 ________ “production", "5 ________ production", "artifact")
c(35, "b :one part of a movie", "b one part of a movie", "artifact")
c(35, "“d a list of all the people Who worked on a movie", "d a list of all the people who worked on a movie", "artifact")
c(63, "4 \"(Children / Old people) have the most accidents", "4 (Children / Old people) have the most accidents", "artifact")
c(130, "8 ________ :cannot happen or cannot be done", "8 ________ cannot happen or cannot be done", "artifact")

# ---- p155 Real Life Skill (image-verified) ----
c(155, "Commas are used with large Humber to separate", "Commas are used with large numbers to separate", "OCR")
c(155, "Written | Spoken.\n", "Written | Spoken\n", "artifact")
c(155, "10,000 | {?ten thousand}\n", "10,000 | ten thousand\n", "image-verified")
c(53, "6 purpose aim goal reward T record work report account\n", "6 purpose aim goal reward\n\n7 record work report account\n", "row 7 separated (image-verified)")
c(53, "[running foot: 52 UNIT 4 Chapter]", "[running foot: 52 UNIT 4 Chapter 1]", "running foot")
c(153, "3 opportunity availability busy\n\npossibility\n", "3 opportunity availability busy possibility\n", "row re-joined (image-verified)")

# ---- suspects triage (image-verified) ----
c(43, "[20] {?preblem-solving} skills. This may be true for the first decade of his tests, when 1Q scores", "[20] problem-solving skills. This may be true for the first decade of his tests, when IQ scores", "OCR")
c(43, "more and more modern, 1Q scores have begun", "more and more modern, IQ scores have begun", "OCR")
c(107, "**{?Qvehidesiones}**\n\nh hotel manager", "g web designer\n\nh hotel manager", "OCR (image-verified)")
c(148, "# Clean Up Australia,\n\n# Up the World\n\n{?http://www.asrinfo.heinle.com/cleanup}\n\n# Clean\n\nlan Kiernan", "# Clean Up Australia, Clean Up the World\n\n[WEB PAGE FRAME — address bar: http://www.asrinfo.heinle.com/cleanup]\n\nIan Kiernan", "title re-joined; URL verified; Ian")
c(148, "hard work, lan has shown", "hard work, Ian has shown", "OCR")
c(121, "# {?t o}\n\n1 Have you ever used", "1 Have you ever used", "artifact (torn-paper graphic)")
c(162, "rooftop gardens that can reduce the green wall at\n\n**CaxiaForum Madrid**\n\n20 heating and cooling costs.", "rooftop gardens that can reduce [20] heating and cooling costs.", "photo caption separated; line marker")
c(162, "In New York City, public schools plant rooftop gardens that can reduce [20] heating", "[PHOTO CAPTION: the green wall at CaxiaForum Madrid]\n\nIn New York City, public schools plant rooftop gardens that can reduce [20] heating", "caption")
c(147, "1 When did lan Kiernan organize", "1 When did Ian Kiernan organize", "OCR")
c(149, "c Who ls lan Kiernan?", "c Who Is Ian Kiernan?", "OCR")
c(149, "c lan Kiernan should be rewarded", "c Ian Kiernan should be rewarded", "OCR")
c(90, "[20] So that it can be studied", "[20] so that it can be studied", "OCR capital")
c(84, "[10] athletic job..", "[10] athletic job.", "artifact")

# ---- p38 J. J. Abrams passage (image-verified) ----
c(38, "n college, Abrams co-wrote", "In college, Abrams co-wrote", "lost first letter")
c(38, "later in 008, with Mission: Impossible 111.", "later in 2006, with Mission: Impossible III.", "OCR")
c(38, "‘mystery box, because", "‘mystery box,’ because", "OCR")
c(38, "infinite! possibility", "infinite¹ possibility", "footnote ref")
c(38, "in what I do” The box", "in what I do.” The box", "OCR")
c(38, "\n\n________\n\n[running foot", "\n\n[NOTE: the footnote ¹ for “infinite” is not printed on this page in the source PDF]\n\n[running foot", "artifact rule; missing footnote documented")

# ---- footnote references / definitions ----
c(162, "grow something edible,\" said Lauren Fontana", "grow something edible,²” said Lauren Fontana", "footnote ref")
c(162, "When something sprouts up, it appears suddenly. A sprout is a young plant. 2Something that is edible can be eaten.", "¹ When something sprouts up, it appears suddenly. A sprout is a young plant.\n\n² Something that is edible can be eaten.", "footnotes")
c(86, "A person or organizations sponsors an activity", "¹ A person or organizations [sic — printed thus] sponsors an activity", "footnote marker")
c(34, "their work behind the scenes’. Here are four", "their work behind the scenes¹. Here are four", "footnote ref")
c(34, "The property (or prop”) master", "The property (or “prop”) master", "quote")
c(142, "produce meat and crops’. For example", "produce meat and crops¹. For example", "footnote ref")
c(142, "can g0 a long way.", "can go a long way.", "OCR")
c(28, "**Check Your Paperwork 1**", "**Check Your Paperwork¹**", "footnote ref in heading")
c(62, "40 of them to frown but only 20 to", "40 of them to frown¹ but only 20 to", "footnote ref")

# ---- p119 Will Shortz (image-verified) ----
c(119, "# Shortz:\n\nWhen you ask a child what they would like to be\n\nwhen they grow up", "# Will Shortz: Puzzle Maker\n\nWhen you ask a child what they would like to be when they grow up", "title; line join")
c(119, "desire to become\n\na puzzle maker-someone who", "desire to become a puzzle maker—someone who", "join; dash")
c(119, "si... 2n, Will was", "sixteen, Will was", "OCR (word partly hidden by photo edge; 'si…en' legible)")

# ---- unit-opener / flag clean-ups (image-verified) ----
c(61, "## UNIT EE\n\n", "## UNIT 5\n\n", "unit banner")
c(46, "{?[35]} expect", "[35] expect", "line number verified")
c(152, "{?[35]} our children", "[35] our children", "line number verified")
c(110, "{?xocolatl,} meaning bitter water. The Mayans used {?xocolatl} for", "xocolatl, meaning bitter water. The Mayans used xocolatl for", "verified")
c(3, "ISBN-10: {?1-133-30803-1}", "ISBN-10: 1-133-30803-1", "verified")
c(3, "NATIONAL\n\n**GEOGRAPHIC**\n\nLEARNING\n\nHEINLE\n\nCENGAGE Learning?\n\n", "[LOGOS: NATIONAL GEOGRAPHIC LEARNING · HEINLE CENGAGE Learning]\n\n", "publisher logos")

# ---- unit-opener pages: consistent "## UNIT n" banner + "# Title" (image-verified) ----
c(12, "# Exam Time\n\n## Getting Ready", "## UNIT 1\n\n# Exam Time\n\n## Getting Ready", "banner")
c(12, "3 Are you good at taking tests? How do you prepare for them?\n\n**UNIT**\n\n# 1\n\n", "3 Are you good at taking tests? How do you prepare for them?\n\n", "banner moved to top")
c(22, "# Going Abroad\n\n## Getting Ready", "## UNIT 2\n\n# Going Abroad\n\n## Getting Ready", "banner")
c(22, "most want to visit? Why?\n\n**UNIT**\n\n# 2\n\n", "most want to visit? Why?\n\n", "banner moved to top")
c(32, "**UNIT**\n\n# Movie Makers 3\n\n", "## UNIT 3\n\n# Movie Makers\n\n", "banner")
c(50, "________\n\n# Young Athletes\n\n________\n\n________\n\n________\n\n________\n\n**UNIT**\n\n# 4\n\n________\n\n## Getting Ready", "## UNIT 4\n\n# Young Athletes\n\n[FOUR PHOTOS of sports (tennis, baseball, soccer, kayaking), each with an empty label box]\n\n## Getting Ready", "banner; label boxes")
c(60, "UNIT\n\n# The Amazing Human Body 5\n\n________\n\n________\n\n________\n\n________\n\n________\n\n________ ________\n\n________\n\n________\n\n________\n\n## Getting Ready", "## UNIT 5\n\n# The Amazing Human Body\n\n[DIAGRAM: human body (organs, muscles, skeleton) with nine empty label lines]\n\n## Getting Ready", "banner; label lines")
c(70, "**UNIT**\n\n# Leisure Time 6\n\n• Sleeping\n\n• Working\n\nSpending time with friends and family\n\n• Reading and surfing the Web\n\n• Eating\n\n• Exercising\n\n• Travel\n\n", "## UNIT 6\n\n# Leisure Time\n\n[PIE CHART — legend, largest slice first: Sleeping; Working; Spending time with friends and family; Reading and surfing the Web; Eating; Exercising; Travel]\n\n", "banner; pie chart legend")
c(88, "**UNIT**\n\n# A World of Music 7\n\n", "## UNIT 7\n\n# A World of Music\n\n", "banner")
c(98, "**UNIT**\n\n# Career Paths 8\n\n", "## UNIT 8\n\n# Career Paths\n\n", "banner")
c(108, "# The Story of Chocolate\n\n## Getting Ready", "## UNIT 9\n\n# The Story of Chocolate\n\n## Getting Ready", "banner")
c(108, "good or bad for you? Why?\n\n**UNIT**\n\n# 9\n\n", "good or bad for you? Why?\n\n", "banner moved to top")
c(126, "UNIT\n\n# The Secrets of Advertising 10\n\nSales people from Red Bull, an energy drink company, drive specially designed cars.\n\nTHRIFT CENTER\n\nDOLLAR GENERAL\n\n•\n\nAdvertising billboards are very common in the United States.\n\nBig websites like YouTube make lots of money by featuring advertisements.\n\n", "## UNIT 10\n\n# The Secrets of Advertising\n\n[PHOTO CAPTION: Sales people from Red Bull, an energy drink company, drive specially designed cars.]\n\n[PHOTO CAPTION: Advertising billboards are very common in the United States.]\n\n[PHOTO CAPTION: Big websites like YouTube make lots of money by featuring advertisements.]\n\n", "banner; captions; billboard text removed")
c(136, "**UNIT**\n\n# Food and the Environment 11\n\n", "## UNIT 11\n\n# Food and the Environment\n\n", "banner")
c(146, "**UNIT**\n\n# Living for the Future 12\n\n", "## UNIT 12\n\n# Living for the Future\n\n", "banner")

# ---- chapter-opener banners (image-verified) ----
c(65, "CHAPTER 2 Seeing with the Ears\n\n**ant**\n\n## Before You Read\n\nStronger, Faster, Higher\n\n", "## CHAPTER 2 Seeing with the Ears\n\n[PHOTO CAPTIONS: ant / bat / eagle / dog]\n\n## Before You Read\n\nStronger, Faster, Higher\n\n", "banner; photo labels")
c(65, "**bat eagle dog**\n\n", "", "photo labels merged above")
c(65, "A Look at the photo and the title of the passage on the next page.\n\n________\n\nthe words that you expect to see in the passage.\n\n", "A Look at the photo and the title of the passage on the next page. Circle the words that you expect to see in the passage.\n\n[WORD BOX] ", "oval 'Circle' restored; word box")
c(65, "animals ey s illness", "animals ey s [sic — printed thus, i.e. “eyes”] illness", "printing defect in the book")
c(137, "\n\nCHAPTER 1 Engineering a Better Burger\n\n", "\n\n## CHAPTER 1 Engineering a Better Burger\n\n", "banner")
c(147, "\n\nCHAPTER 1 Clean Up Australia, Clean Up\n\nthe World\n\n", "\n\n## CHAPTER 1 Clean Up Australia, Clean Up the World\n\n", "banner")
c(109, "## CHAPTER 1 A Brief History of Chocolate\n\n________\n\n", "## UNIT 9\n\n## CHAPTER 1 A Brief History of Chocolate\n\n", "unit banner; artifact rule")
c(37, "## CHAPTER 2 The Rise of ].]. Abrams", "## CHAPTER 2 The Rise of J. J. Abrams", "OCR")

# ---- Self Check pages ----
c(45, "**SELF CHECK**\n\n**Answer the following questions.**", "## SELF CHECK\n\n**Answer the following questions.**", "heading level consistent with p83/121/159")
c(45, "5 Which of the six reading passages in units 1-3 was easiest? Which\n\nwas most difficult? Why?", "5 Which of the six reading passages in units 1-3 was easiest? Which was most difficult? Why?", "line join")
c(83, "outside. of class recently?", "outside of class recently?", "artifact")
c(159, "PaR-E |  |  | ", "PQR+E |  |  | ", "OCR")

# ---- p81 Movies for the Blind: two-column passage re-transcribed from the page image (columns were interleaved) ----
c(81, '25 newspapers and is a guest on radio shows. Forry\n\n## Movies for the Blind\n\ngives movies one of five ratings, including, “So good,\n\nWhen you think of the cinema, the phrase watching blind people like it” and “I’m glad I couldn’t see it.” a movie probably comes to mind, and, indeed, Forry became a writer after going blind at the age of moviemakers work very hard to make their films 28, and his writing skills and sense of humor are what interesting visually. They may use elaborate costumes, 30 keep people reading his reviews or listening to him on\n\n[5] beautiful locations, or amazing special effects to tell the radio. After “watching” the animated movie Up, a story. An actor’s expression or movements can also Forry commented that he wished he, too, could have sometimes say more than words.,\n\na talking dog to tell him to watch out for cars and to not “go 9 into! the ladies’ restroom ag again.”\n\nBut what about people who are blind or have trouble seeing? Movies also contain dialogue, music, and 35 Sometimes, though, it’s nice to go to a movie without\n\n10 sound effects —things that people don’t need to see reading reviews and knowing what to expect. Some in order to enjoy. Movie reviewer Marty Klein, who movie theaters have begun to offer recorded audio is blind, created a website called Blindspots to help descriptions of the movements, scenery, and special people choose movies that they can follow without effects so that blind moviegoers can follow what the help of someone explaining what is happening on 40 other audience members see on the screen. They\n\n15 the screen. He gave a rating, from 1 to 10, based on usually receive a wireless headset to wear during several things. A movie received a high rating if it has the movie. This allows them to listen to the narration only a few main characters whose voices are easy to while still hearing the movie’s music and other sounds recognize. Klein also liked interesting stories without that surround them in the theater. Jay Forry also too many changes in time and place. A large amount 45 notes that modern theaters now have excellent sound\n\n20 of dialogue between the characters was better than systems, something he appreciates more than the long silences or noisy action scenes. His reviews are average moviegoer. still online, but the site is no longer updated.\n\nIn the end, going to the movies should be a fun and\n\nAnother blind movie reviewer, Jay Forry, maintains exciting experience — for both the sighted and the the website Blindside Reviews. He also writes for 50 blind.\n\n________\n\n', '# Movies for the Blind\n\nWhen you think of the cinema, the phrase watching a movie probably comes to mind, and, indeed, moviemakers work very hard to make their films interesting visually. They may use elaborate costumes, [5] beautiful locations, or amazing special effects to tell a story. An actor’s expression or movements can also sometimes say more than words.\n\nBut what about people who are blind or have trouble seeing? Movies also contain dialogue, music, and [10] sound effects—things that people don’t need to see in order to enjoy. Movie reviewer Marty Klein, who is blind, created a website called Blindspots to help people choose movies that they can follow without the help of someone explaining what is happening on [15] the screen. He gave a rating, from 1 to 10, based on several things. A movie received a high rating if it has only a few main characters whose voices are easy to recognize. Klein also liked interesting stories without too many changes in time and place. A large amount [20] of dialogue between the characters was better than long silences or noisy action scenes. His reviews are still online, but the site is no longer updated.\n\nAnother blind movie reviewer, Jay Forry, maintains the website Blindside Reviews. He also writes for [25] newspapers and is a guest on radio shows. Forry gives movies one of five ratings, including, “So good, blind people like it” and “I’m glad I couldn’t see it.” Forry became a writer after going blind at the age of 28, and his writing skills and sense of humor are what [30] keep people reading his reviews or listening to him on the radio. After “watching” the animated movie Up, Forry commented that he wished he, too, could have a talking dog to tell him to watch out for cars and to not “go into the ladies’ restroom again.”\n\n[35] Sometimes, though, it’s nice to go to a movie without reading reviews and knowing what to expect. Some movie theaters have begun to offer recorded audio descriptions of the movements, scenery, and special effects so that blind moviegoers can follow what [40] other audience members see on the screen. They usually receive a wireless headset to wear during the movie. This allows them to listen to the narration while still hearing the movie’s music and other sounds that surround them in the theater. Jay Forry also [45] notes that modern theaters now have excellent sound systems, something he appreciates more than the average moviegoer.\n\nIn the end, going to the movies should be a fun and exciting experience—for both the sighted and the [50] blind.\n\n', 'two-column passage re-transcribed (image-verified)')

# ---- p110 A Brief History of Chocolate (image-verified) ----
c(110, "# A Brief History\n\n", "# A Brief History of Chocolate\n\n", "title")
c(110, "we know today.\n\n[20]\n\nAS popular", "we know today.\n\n[20] As popular", "line marker; OCR 'AS'")
c(110, "fashionable. By the 17th\n\nHernando Cortez\n\ncentury, the chocolate", "fashionable. By the 17th century, the chocolate", "photo caption removed from prose")
c(110, "Caco seeds became", "Caco [sic — printed thus] seeds became", "printed typo")
c(110, "in 1828.\n\nC. J. Van Houten", "in 1828. C. J. Van Houten", "join")
c(110, "“Chocolate is a magical product.”\n\n¹ The money", "“Chocolate is a magical product.”\n\n[PHOTO CAPTION: Hernando Cortez]\n\n¹ The money", "photo caption")

# ---- p90 Sounds from the Past (image-verified) ----
c(90, "\nMuch of the music we listen to today", "\n# Sounds from the Past\n\nMuch of the music we listen to today", "title")
c(90, "may go extinct.\n\nwomen play bamboo flutes\n\nThere is a growing effort to preserve music in its many forms. Some with their noses\n\n[15] researchers", "may go extinct.\n\n[PHOTO CAPTION: women play bamboo flutes with their noses]\n\nThere is a growing effort to preserve music in its many forms. Some [15] researchers", "photo caption separated; line marker inlined")
c(90, "different cultures, - genres, time periods, and places. For example, some\n\n[25]\n\npunk rock fans", "different cultures, [25] genres, time periods, and places. For example, some punk rock fans", "artifact; line marker inlined")
c(90, "\n\nfolk musicians from the island of Madagascar\n\nNow, modern technology makes it much easier to preserve music.\n\nSmart phones", "\n\n[PHOTO CAPTION: folk musicians from the island of Madagascar]\n\nNow, modern technology makes it much easier to preserve music. Smart phones", "photo caption; join")

# ---- passage titles rendered as artwork (not in the text layer/OCR); restored from the page images ----
c(18, "\n① Think about the last test", "\n# Oh, No! Not Another Test!\n\n① Think about the last test", "title (artwork)")
c(24, "\n**Posted on April 6 by Juliana**", "\n# We’re in Vietnam!\n\n**Posted on April 6 by Juliana**", "title (artwork)")
c(62, "\n① Did you know", "\n# You Are Amazing: You Are Human!\n\n① Did you know", "title (artwork)")
c(66, "\nThe human body is an amazing thing.", "\n# Seeing with the Ears\n\nThe human body is an amazing thing.", "title (artwork)")
c(72, "\nThe dictionary defines a scrapbook", "\n# Scrapbooking\n\n[WEB PAGE FRAME — address bar: http://leisurefocus.heinle.com/scrapbooking.html]\n\nThe dictionary defines a scrapbook", "title; web frame")
c(76, "\nMoving from TV to the Web\n\n________\n\nIt used to be", "\n# Moving from TV to the Web\n\nIt used to be", "title level; artifact rule")
c(128, "\n① Would you believe", "\n# Ads Are Everywhere!\n\n① Would you believe", "title (artwork)")
c(142, "\n① People become vegetarian", "\n# Is Your Diet Destroying the Environment?\n\n① People become vegetarian", "title (artwork)")
c(152, "\n① We are a planet", "\n# Resources for the Future\n\n① We are a planet", "title (artwork)")
c(114, "# Truth about Chocolate\n\n", "# The Truth about Chocolate\n\n", "title (image-verified)")

# ---- p104 personality types: paragraphs / line markers re-aligned with the page image ----
c(104, '**Realistic**\n\nRealistic people like to work with things they can see or touch. They are inclined to solve problems by doing them, rather than thinking or talking about them. They generally like to work outside and are good with tools, machines, plants, and animals.\n\n[15]\n\nJob matches: carpenter, chef, nurse, pilot\n\n**Investigative**\n\nPeople of this personality type value ideas and are strong at tasks\n\nthat allow them to investigate facts and figure out complex problems. They are better at individual\n\n[20] work like research and study, rather than leading groups of people or working in teams. Job matches: computer programmer, historian, psychologist, surgeon\n\n**Artistic**\n\nArtists are creative people. They don’t work well with structure and rules, and thrive instead in environments that allow\n\n[25] communication and a free flow of ideas. They enjoy tasks that allow them to express themselves and mix with people. Job matches: actor, art therapist, graphic designer, writer\n\n☐ Social\n\nSocial personalities love to work with people. They get the most satisfaction out of teaching\n\n[30]\n\nand helping others, and are driven to serve the community as opposed to making money. Job matches: coach, counselor, social worker, teacher\n\n**Enterprising**\n\n[35]\n\nMany great leaders and business people have enterprising personalities. These are persuasive people who are good at\n\nmaking decisions and leading teams. They tend to value money, power, and status, and will work toward achieving them. Job matches: business owner, event manager, lawyer, salesperson\n\n[40] Conventional\n\nConventional people appreciate rules and regulations, and like having structure to their lives. They are logical thinkers and have a lot of self-control, making them the perfect people to work with data and details. Job matches: accountant, analyst, editor, librarian Nowadays, anyone can take a Holland Code personality test online to find what jobs might be right for\n\n[45] them. Why not try it today?\n\n', '**Realistic**\n\nRealistic people like to work with things they can see or touch. They are inclined to solve problems by doing them, rather than thinking or talking about them. They generally like to work outside [15] and are good with tools, machines, plants, and animals. Job matches: carpenter, chef, nurse, pilot\n\n**Investigative**\n\nPeople of this personality type value ideas and are strong at tasks that allow them to investigate facts and figure out complex problems. They are better at individual [20] work like research and study, rather than leading groups of people or working in teams. Job matches: computer programmer, historian, psychologist, surgeon\n\n**Artistic**\n\nArtists are creative people. They don’t work well with structure and rules, and thrive instead in environments that allow [25] communication and a free flow of ideas. They enjoy tasks that allow them to express themselves and mix with people. Job matches: actor, art therapist, graphic designer, writer\n\n**Social**\n\nSocial personalities love to [30] work with people. They get the most satisfaction out of teaching and helping others, and are driven to serve the community as opposed to making money. Job matches: coach, counselor, social worker, teacher\n\n**Enterprising**\n\n[35] Many great leaders and business people have enterprising personalities. These are persuasive people who are good at making decisions and leading teams. They tend to value money, power, and status, and will work toward achieving them. Job matches: business owner, event manager, lawyer, salesperson\n\n[40] **Conventional**\n\nConventional people appreciate rules and regulations, and like having structure to their lives. They are logical thinkers and have a lot of self-control, making them the perfect people to work with data and details. Job matches: accountant, analyst, editor, librarian\n\nNowadays, anyone can take a Holland Code personality test online to find what jobs might be right for [45] them. Why not try it today?\n\n', 'image-verified')

# ---- p72 Scrapbooking interview (image-verified) ----
c(72, "## [20] How do you learn about new scrapbooking techniques and trends?", "[20] ## How do you learn about new scrapbooking techniques and trends?", "marker before heading")
c(72, "## Why is scrapbooking so popular\n\n[25]\n\n## these days?\n\nI think people want", "[25] ## Why is scrapbooking so popular these days?\n\nI think people want", "heading re-joined; marker")
c(72, "So many people today want to do that!\n\n[30]\n\nIn the U.S. alone,", "So many people today want to do that! [30] In the U.S. alone,", "marker inlined; join")
c(72, "and words to-show the theme.", "and words to show the theme.", "artifact hyphen")
c(132, "the company held a\n\n[10]\n\ncontest to find new models.", "the company held a [10] contest to find new models.", "marker inlined")

# ---- p177 Reading Rate Chart (image-verified) ----
c(177, '[TABLE 6 columns]\n335 | Quadrant 2 |  |  |  | Quadrant\n320 |  |  |  |  | \n305 |  |  |  |  | \n290 |  |  |  |  | \n275 |  |  |  |  | \n260 |  |  |  |  | \n245 |  |  |  |  | \n230 |  |  |  |  | \n215 |  |  |  |  | \n200 |  |  |  |  | \n185 |  |  |  |  | \n170 |  |  |  |  | \n155 |  |  |  |  | \n140 |  |  |  |  | \n125 |  |  |  |  | \n110 |  |  |  |  | \n95 |  |  |  |  | \n80 |  |  |  |  | \n65 |  |  |  |  | \n | Quadrant 1 |  |  |  | Quadrant 3\n[/TABLE]\n\n1 (20%)\n\n2 (40%)\n\n3 (60%)\n\n4 (80%)\n\n5 (100%)\n\n', '[CHART — Reading Rate Chart: a grid. Vertical axis = reading rate in words per minute (wpm), labelled from the top: 335, 320, 305, 290, 275, 260, 245, 230, 215, 200, 185, 170, 155, 140, 125, 110, 95, 80, 65, 50. Horizontal axis = comprehension score, 5 columns labelled below the grid: 1 (20%), 2 (40%), 3 (60%), 4 (80%), 5 (100%). The grid is divided into four quadrants at 200 wpm and 70% comprehension: Quadrant 2 (top left), Quadrant 4 (top right), Quadrant 1 (bottom left), Quadrant 3 (bottom right).]\n\n', 'chart described')
c(177, 'Quadrant 1: You are reading slower than 200 wpm with less than 70% comprehension. Quadrant 2: You are reading faster than 200 wpm with less than 70% comprehension. Quadrant 3: You are reading slower than 200 wpm with greater than 70% comprehension. Quadrant 4: You are reading faster than 200 wpm with greater than 70% comprehension.\n\n', '**Quadrant 1:** You are reading slower than 200 wpm with less than 70% comprehension.\n\n**Quadrant 2:** You are reading faster than 200 wpm with less than 70% comprehension.\n\n**Quadrant 3:** You are reading slower than 200 wpm with greater than 70% comprehension.\n\n**Quadrant 4:** You are reading faster than 200 wpm with greater than 70% comprehension.\n\n', 'quadrant lines separated')
c(177, 'Calculating your words-per-minute (wpm) At the end', '**Calculating your words-per-minute (wpm)** At the end', 'bold label')

# ---- p178 series ISBN grid (verified earlier against the page image) ----
c(178, '**INTRO**\n\nText Text/Audio CD Package Classroom Audio CDs Teacher’s Guide Assessment CD-ROM with Exam View\n\n**Level 1**\n\nText Text/Audio CD Package Classroom Audio CDs Teacher’s Guide Assessment CD-ROM with Exam View\'\'\n\n**Level 2**\n\nText Text/Audio CD Package Classroom Audio CDs Teacher’s Guide Assessment CD-ROM with Exam View\n\n**Level 3**\n\nText\n\nText/Audio CD Package Classroom Audio CDs Teacher’s Guide Assessment CD-ROM with Exam View"\n\n**Level 4**\n\nText Text/Audio CD Package Classroom Audio CDs Teacher’s Guide Assessment CD-ROM with Exam View:\n\n978-1-133-30812-6 978-1-133-90747-3 978-1-133-30814-0 978-1-133-30813-3 978-1-133-30802-7\n\n978-1-133-30799-0 978-1-133-90778-7 978-1-133-30801-0 978-1-133-30800-3 978-1-133-30802-7\n\n978-1-133-30803-4 978-1-133-90749-7 978-1-133-30805-8 978-1-133-30804-1 978-1-133-30802-7\n\n978-1-133-30806-5 978-1-133-90750-3 978-1-133-30808-9 978-1-133-30807-2 978-1-133-30802-7\n\n978-1-133-30809-6 978-1-4240-9422-6 978-1-133-30811-9 978-1-133-30810-2 978-1-133-30802-7', '[TABLE 6 columns]\nLevel | Text | Text/Audio CD Package | Classroom Audio CDs | Teacher’s Guide | Assessment CD-ROM with ExamView®\nINTRO | 978-1-133-30812-6 | 978-1-133-90747-3 | 978-1-133-30814-0 | 978-1-133-30813-3 | 978-1-133-30802-7\nLevel 1 | 978-1-133-30799-0 | 978-1-133-90778-7 | 978-1-133-30801-0 | 978-1-133-30800-3 | 978-1-133-30802-7\nLevel 2 | 978-1-133-30803-4 | 978-1-133-90749-7 | 978-1-133-30805-8 | 978-1-133-30804-1 | 978-1-133-30802-7\nLevel 3 | 978-1-133-30806-5 | 978-1-133-90750-3 | 978-1-133-30808-9 | 978-1-133-30807-2 | 978-1-133-30802-7\nLevel 4 | 978-1-133-30809-6 | 978-1-4240-9422-6 | 978-1-133-30811-9 | 978-1-133-30810-2 | 978-1-133-30802-7\n[/TABLE]', 'ISBN grid as table')

# ---- vocabulary index: part-of-speech labels garbled by OCR (IPA itself stays flagged) ----
c(164, "hands-on {?/'hrendz 1 on/} dj. actually", "hands-on {?/'hrendz 1 on/} adj. actually", "POS label")
c(168, "translate {?/trrens le1t,} 'trenz leit/ v. to change into another language: This book was translated into\n\n20 languages.", "translate {?/trrens le1t,} 'trenz leit/ v. to change into another language: This book was translated into 20 languages.", "line join")
c(169, "select {?/sa’lekt} Iv. v. to choose", "select {?/sa’lekt/} v. to choose", "artifact")
c(170, "rotate {?/'rou’teit/} 2. to move around", "rotate {?/'rou’teit/} v. to move around", "POS label")
c(173, "retirement /ri’tayamont/ x. the period", "retirement {?/ri’tayamont/} n. the period", "POS label; IPA flagged")
c(175, "fool /fu:l/ v to trick", "fool /fu:l/ v. to trick", "POS label")
c(167, "per /p3:r I prep. for each", "per {?/p3:r/} prep. for each", "artifact; IPA flagged")

# ---- vocabulary index: two entries run together into one paragraph -> split ----
c(166, ' is excellent at her job. exciting ', ' is excellent at her job.\n\nexciting ', 'entry split')
c(167, 'e split a large sandwich. stick to ', 'e split a large sandwich.\n\nstick to ', 'entry split')
c(168, ' frequent trips to Paris. imagine ', ' frequent trips to Paris.\n\nimagine ', 'entry split')
c(169, 'e judged by three people. looks like ', 'e judged by three people.\n\nlooks like ', 'entry split')
c(171, ' hers has a green collar. stand for ', ' hers has a green collar.\n\nstand for ', 'entry split')
c(172, 'rmed a marriage ceremony. check in ', 'rmed a marriage ceremony.\n\ncheck in ', 'entry split')
c(174, 'ated with thunder storms. break up ', 'ated with thunder storms.\n\nbreak up ', 'entry split')
c(173, "employs 18 people. no longer /nou 'la:nga/ expression adv.", "employs 18 people.\n\nno longer /nou 'la:nga/ expression adv.", "entry split")
c(175, "on the highway? immense Nmens/ adj. very large", "on the highway?\n\nimmense {?/i’mens/} adj. very large", "entry split; IPA flagged")
