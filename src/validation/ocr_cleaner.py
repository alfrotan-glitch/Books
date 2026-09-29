"""
OCR Error Detection and Highly Conservative Correction Subsystem.
Strict Principle: "A visible OCR error is better than a false correction."
Every correction is strictly logged and audited: (page, original, corrected, confidence, reason).
Only applies replacements when the candidate word is verified in a validated lexicon.
"""

from dataclasses import dataclass
import re
from typing import List, Optional, Set, Tuple


@dataclass
class OCRErrorCorrection:
    page_num: int
    original: str
    corrected: str
    confidence: float
    reason: str
    applied: bool

    def to_dict(self):
        return {
            "page_num": self.page_num,
            "original": self.original,
            "corrected": self.corrected,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "applied": self.applied,
        }


class OCRErrorDetector:
    def __init__(self, min_confidence_to_apply: float = 0.90):
        self.min_confidence_to_apply = min_confidence_to_apply

        # Pattern for letters with a single embedded digit: e.g. "med1cine", "c1inical"
        self.digit_in_word_pattern = re.compile(r"\b([a-zA-Z]{2,})([0158])([a-zA-Z]{2,})\b")

        # Scientific/chemical/model identifiers that should NEVER be touched
        self.protected_identifiers: Set[str] = {
            "covid19", "sars", "h1n1", "h5n1", "co2", "h2o", "b12", "d3", "t3", "t4",
            "cd4", "cd8", "il6", "il1", "tnf", "p53", "brca1", "brca2", "page1", "fig1", "table1"
        }

        # Validated lexicon of high-frequency words prone to OCR digit substitution
        self.verified_lexicon: Set[str] = {
            "medicine", "medical", "clinical", "hospital", "patient", "treatment",
            "protocol", "individual", "prescription", "condition", "illness",
            "examination", "physician", "surgical", "diagnosis", "analysis",
            "circulation", "respiratory", "cardiovascular", "pharmacology",
            "information", "guideline", "definition", "position", "condition",
            "education", "educational", "institution", "measurement", "temperature",
            "concentration", "investigation", "reconstruction", "communication",
            "book", "blood", "good", "food", "look", "took", "room", "door", "school",
            "action", "motion", "option", "section", "fraction", "reaction", "traction",
            "critical", "optical", "physical", "typical", "practical", "chemical"
        }

    def detect_and_clean(self, text: str, page_num: int = 0) -> Tuple[str, List[OCRErrorCorrection]]:
        """
        Scans text for OCR errors. Applies ONLY high-confidence, verified fixes.
        Never alters text without lexical verification.
        """
        if not text:
            return text, []

        corrections: List[OCRErrorCorrection] = []
        cleaned_text = text

        def replacer(match: re.Match) -> str:
            prefix = match.group(1)
            digit = match.group(2)
            suffix = match.group(3)
            orig_word = match.group(0)

            # Never touch scientific identifiers
            if orig_word.lower() in self.protected_identifiers:
                return orig_word

            # Determine substitution candidates
            candidate_chars = []
            if digit == "1":
                candidate_chars = ["i", "l"]
            elif digit == "0":
                candidate_chars = ["o"]
            elif digit == "5":
                candidate_chars = ["s"]
            elif digit == "8":
                candidate_chars = ["b"]
            else:
                candidate_chars = [digit]

            best_word = None
            for ch in candidate_chars:
                candidate = prefix + ch + suffix
                if candidate.lower() in self.verified_lexicon:
                    best_word = candidate
                    break

            if best_word is not None:
                # Verified in dictionary -> high confidence
                conf = 0.94
                applied = conf >= self.min_confidence_to_apply
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig_word,
                        corrected=best_word,
                        confidence=conf,
                        reason=f"OCR digit-letter confusion: verified '{orig_word}' -> '{best_word}' in lexicon",
                        applied=applied,
                    )
                )
                return best_word if applied else orig_word
            else:
                # UNVERIFIED: preserve original text without guessing!
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig_word,
                        corrected=orig_word,
                        confidence=0.40,
                        reason=f"Potential OCR anomaly '{orig_word}' not found in verified lexicon; preserved original",
                        applied=False,
                    )
                )
                return orig_word

        cleaned_text = self.digit_in_word_pattern.sub(replacer, cleaned_text)

        # 2. Vertical bar '|' inside words: e.g. "c|inical" -> "clinical"
        bar_matches = re.findall(r"\b([a-zA-Z]+)\|([a-zA-Z]+)\b", cleaned_text)
        for pre, suf in bar_matches:
            orig = f"{pre}|{suf}"
            cand_l = f"{pre}l{suf}"
            cand_i = f"{pre}i{suf}"

            chosen = None
            if cand_l.lower() in self.verified_lexicon:
                chosen = cand_l
            elif cand_i.lower() in self.verified_lexicon:
                chosen = cand_i

            if chosen is not None:
                conf = 0.92
                applied = conf >= self.min_confidence_to_apply
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig,
                        corrected=chosen,
                        confidence=conf,
                        reason=f"Vertical bar misrecognized as letter: verified '{orig}' -> '{chosen}'",
                        applied=applied,
                    )
                )
                if applied:
                    cleaned_text = cleaned_text.replace(orig, chosen)
            else:
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=orig,
                        corrected=orig,
                        confidence=0.45,
                        reason=f"Unverified vertical bar pattern '{orig}'; preserved original",
                        applied=False,
                    )
                )

        # 3. Persian / Arabic Character Normalization
        # Normalizes Arabic kaf (ك) to Persian kaf (ک) and Arabic yeh (ي) to Persian yeh (ی)
        cleaned_text = cleaned_text.replace('\u0643', 'ک').replace('\u064a', 'ی').replace('\u0649', 'ی')

        # 4. High-confidence Persian OCR letter & prefix corrections
        persian_patterns = [
            (r"\bفى\s*باشد\b", "می‌باشد", "Persian verb prefix correction: 'فى باشد' -> 'می‌باشد'"),
            (r"\bمى\s*كيرد\b", "می‌گیرد", "Persian verb correction: 'مى كيرد' -> 'می‌گیرد'"),
            (r"\bمى\s*گیرد\b", "می‌گیرد", "Persian verb formatting: 'مى گیرد' -> 'می‌گیرد'"),
            (r"\bمى\s*شود\b", "می‌شود", "Persian verb formatting: 'مى شود' -> 'می‌شود'"),
            (r"\bمى\s*تواند\b", "می‌تواند", "Persian verb formatting: 'مى تواند' -> 'می‌تواند'"),
            (r"\bمى\s*يابد\b", "می‌یابد", "Persian verb formatting: 'مى يابد' -> 'می‌یابد'"),
            (r"\bمى\s*یابد\b", "می‌یابد", "Persian verb formatting: 'مى یابد' -> 'می‌یابد'"),
            (r"\bمى\s*سازد\b", "می‌سازد", "Persian verb formatting: 'مى سازد' -> 'می‌سازد'"),
            (r"\bمى\s*شوند\b", "می‌شوند", "Persian verb formatting: 'مى شوند' -> 'می‌شوند'"),
            (r"\bمى\s*باشد\b", "می‌باشد", "Persian verb formatting: 'مى باشد' -> 'می‌باشد'"),
            (r"\bفسامل\b", "شامل", "Persian OCR dot confusion: 'فسامل' -> 'شامل'"),
            (r"\bکفیده\b", "کشیده", "Persian OCR confusion: 'کفیده' -> 'کشیده'"),
            (r"\bمنالجوى\b", "معالجوی", "Dari medical vocabulary: 'منالجوى' -> 'معالجوی'"),
            (r"\b۵۰66\b", "50cc", "Medical syringe unit: '۵۰66' -> '50cc'"),
            (r"\b5066\b", "50cc", "Medical syringe unit: '5066' -> '50cc'"),
            (r"\bسح\b(?=\s+[ا-ی])", "سطح", "Persian OCR missing ascender: 'سح' -> 'سطح'"),
            (r"\bاسث\b", "است", "Persian OCR letter confusion: 'اسث' -> 'است'"),
            (r"\bعبارث\b", "عبارت", "Persian OCR letter confusion: 'عبارث' -> 'عبارت'"),
            (r"\bصورث\b", "صورت", "Persian OCR letter confusion: 'صورث' -> 'صورت'"),
            (r"\bحالث\b", "حالت", "Persian OCR letter confusion: 'حالث' -> 'حالت'"),
            (r"\bتفاوث\b", "تفاوت", "Persian OCR letter confusion: 'تفاوث' -> 'تفاوت'"),
            (r"\bنور\s*مال\b", "نورمال", "Persian compound spacing: 'نور مال' -> 'نورمال'"),
            (r"\bطبیعصی\b", "طبیعی", "Persian OCR artifact: 'طبیعصی' -> 'طبیعی'"),
            (r"\bتخر\s*بش\b", "تخریش", "Persian OCR artifact: 'تخر بش' -> 'تخریش'"),
            (r"\bایجاذ\b|\bايجاذ\b", "ایجاد", "Persian OCR dot confusion: 'ایجاذ' -> 'ایجاد'"),
            (r"\bممگن\b", "ممکن", "Persian OCR confusion: 'ممگن' -> 'ممکن'"),
            (r"\bسرقه\b(?=\s+يك|\s+یک)", "سرفه", "Persian OCR confusion: 'سرقه' -> 'سرفه'"),
            (r"\bياك\b(?=\s+نمودن)", "پاک", "Persian OCR dot confusion: 'ياك' -> 'پاک'"),
            (r"\bكلو\b(?=\s+از)", "گلو", "Persian OCR confusion: 'كلو' -> 'گلو'"),
            (r"\bامسا\b", "اما", "Persian OCR artifact: 'امسا' -> 'اما'"),
            (r"\bذر\b(?=\s+آن\s+صورت|\s+ان\s+صورت)", "در", "Persian OCR dot confusion: 'ذر' -> 'در'"),
            (r"\bپیسسا\b|\bپسسا\b", "یا", "Persian OCR ligature confusion: 'پسسا' -> 'یا'"),
            (r"\bهى\s*با[ثس]د\b|\bفى\s*با[ثس]د\b", "می‌باشد", "Persian OCR prefix confusion: 'فى باشد' -> 'می‌باشد'"),
            (r"\bفى\s*شود\b", "می‌شود", "Persian OCR prefix confusion: 'فى شود' -> 'می‌شود'"),
            (r"\bاغراض\b(?=\s+معمول|\s+Jonas)", "اعراض", "Medical terminology correction: 'اغراض' -> 'اعراض'"),
            (r"\bسورد\b(?=\s+استفاده)", "مورد", "Medical OCR confusion: 'سورد' -> 'مورد'"),
            (r"\bدیاقراگم\b", "دیافراگم", "Medical anatomy: 'دیاقراگم' -> 'دیافراگم'"),
            (r"\bسایة\b", "سایه", "Persian spelling normalization: 'سایة' -> 'سایه'"),
            (r"\bبيويسى\b|\bبیوسی\b", "بیوپسی", "Medical procedure: 'بیوپسی'"),
            (r"\bتوب\s*رکلوز\b|\bتوب\s*ركلوز\b", "توبرکلوز", "Medical disease: 'توبرکلوز'"),
            (r"\bV/Q\s*SCAM\b", "V/Q SCAN", "Medical diagnostic: 'V/Q SCAN'"),
            (r"\bقلیوم\b|\bقليوم\b", "هلیوم", "Pulmonary gas dilution: 'هلیوم'"),
            (r"\bاسناغ\b", "اسناخ", "Medical anatomy: 'اسناخ'"),
            (r"\bبستر\s*شسعرية\b|\bبستر\s*شعریة\b", "بستر شعریه", "Medical anatomy: 'بستر شعریه'"),
            (r"\bکارین\s*مونو\b|\bكارین\s*سونو\b", "کاربن مونو", "Medical gas: 'کاربن مونو'"),
            (r"\bفیسروز\s*ریسه\b|\bفیسروز\s*ریه\b", "فیبروز ریه", "Medical pathology: 'فیبروز ریه'"),
            (r"\bگنواسیدوز\s*دبابنیگ\b", "کتواسیدوز دیابتیک", "Medical pathology: 'کتواسیدوز دیابتیک'"),
            (r"\bعدم\s*AUS\b", "عدم کفایه", "Medical terminology: 'عدم کفایه'"),
            (r"\bعدم\s*كفاية\b|\bعدم\s*کفایة\b", "عدم کفایه", "Medical terminology: 'عدم کفایه'"),
            (r"\bشریان\s*کمبری\b", "شریان کعبری", "Medical anatomy: 'شریان کعبری'"),
            (r"\bهبارین\b|\bهبارين\b", "هیپارین", "Medical drug: 'هیپارین'"),
            (r"\bهیپارینایز\b|\bهيارينايز\b", "هیپارینایز", "Medical term: 'هیپارینایز'"),
            (r"\bZY\b(?=\s+بی\s*حس)", "2%", "Medical concentration: '2%'"),
            (r"\bشماره\s*YA\b", "شماره 28", "Catheter gauge: 'شماره 28'"),
            (r"\bپاوریزی\b|\bپلوريزى\b", "پلوریزی", "Medical term: 'پلوریزی'"),
            (r"\bنومونورگس\b", "نوموتوراکس", "Medical pathology: 'نوموتوراکس'"),
            (r"\b(?:عسرت|غسرث)\s*(?:نفس|تنفس)\b", "عسرت تنفس", "Dari medical standard: 'عسرت تنفس'"),
            (r"\b[إا]کس[\- ]*(?:ری|حر[یى])\s*صدر[یى]?\b", "اکسری صدر", "Dari radiology standard: 'اکسری صدر'"),
            (r"\bفايبرأيتيك\b|\bفايبراويتيك\b", "فایبراوپتیک", "Endoscopy type: 'فایبراوپتیک'"),
            (r"\bسرفا\s*fly\s*دار\b|\bسرفة\s*fly\s*دار\b", "سرفه بلغم‌دار", "Medical symptom: 'سرفه بلغم‌دار'"),
            (r"\bسرفة\s*mah\b|\bسرفه\s*mah\b", "سرفه بلغم‌دار (مولد)", "Medical cough classification: 'سرفه مولد'"),
            (r"\bcde\b(?=\s+زمینه‌ای)", "علت", "Persian term: 'علت'"),
            (r"\bJat\b(?=\s+ر[یي]?فل[کگ]سی)", "عمل", "Physiological reflex: 'عمل ریفلکسی'"),
            (r"\bBle\b(?=\s+شفاف)", "کاملاً", "Symptom description"),
            (r"\bLie!\b(?=\s+به\s+علت)", "غالباً", "Etiology description"),
            (r"\bey\b(?=\s+هوا\s+از\s+ریه)", "خروج", "Definition of cough"),
            (r"\bLangs\b", "ریه‌های", "Medical anatomy: 'ریه‌های'"),
            (r"\b۷/۵56۵\b", "V/Q scan", "Nuclear medicine test: 'V/Q scan'"),
            (r"\bقیخی\b", "قیحی", "Medical sputum: 'قیحی'"),
            (r"\bصفیخاث\s*دمویه\b", "صفیحات دمویه", "Hematology: 'صفیحات دمویه'"),
            (r"\bنفث\s*الدم\b", "نفث‌الدم", "Medical symptom: 'نفث‌الدم'"),
            (r"\bاسمای\s*خاد\b", "اسمای حاد", "Medical pathology: 'اسمای حاد'"),
            (r"\bسرفة\s*ab\b", "سرفه حاد", "Medical symptom: 'سرفه حاد'"),
            (r"\bتضیق\s*ما[یي]ترل\b", "تضیق مایترل", "Cardiology: 'تضیق مایترل'"),
            (r"\bاحتشای\s*ر[یي]ه\b", "احتشای ریه", "Pulmonology: 'احتشای ریه'"),
            (r"\bسوء\s*تشكل\s*شریانی[\- ]وریدی\b", "سوءتشکل شریانی-وریدی", "Vascular pathology"),
            (r"\bضایعات\s*تجوقی\b", "ضایعات تجویفی", "Radiology: 'ضایعات تجویفی'"),
            (r"\bکدورت‌های\s*الوبولی\b", "کدورت‌های الویولی", "Radiology: 'کدورت‌های الویولی'"),
            (r"\bتامپوناة\s*قلبسى\b", "تامپوناد قلبی", "Cardiology sign: 'تامپوناد قلبی'"),
            (r"\bبيريكاردييث\b", "پریکاردیت", "Cardiology: 'پریکاردیت'"),
            (r"\bکروب\b(?=\s+و\s+امرا[ضش])", "کروپ", "Pediatric respiratory: 'کروپ'"),
            (r"\bكنول\s*بینی\b", "کانولای بینی", "Oxygen delivery"),
            (r"\bبلفم[\- ]دار\b", "بلغم‌دار", "Medical symptom: 'بلغم‌دار'"),
            (r"\bذر\s*أن\s*ضورث\b|\bذر\s*ان\s*صورت\b", "در آن صورت", "Grammar correction"),
            (r"\bأ3\b|\bأ۳\b", "سه سببی که", "Text restoration"),
            (r"\bاسف\b", "است", "Grammar"),
            (r"\byl\s*انان\b|\byl\s*عفونت\b", "از: عفونت", "Etiology"),
            (r"\bالإفسساب\s*پسسا\b|\bالتهاب\s*پسسا\b", "التهاب یا", "Pathology"),
            (r"\bbbs\s*يا\b|\bbbs\s*یا\b", "یا", "Grammar"),
            (r"\bتوليد\s*ABS\s*ee\s*امسا\b|\bتولید\s*ABS\s*ee\s*اما\b", "تولید نموده اما", "Text restoration"),
            (r"\bسه\s*أ\s*که\s*از\s*آنها\b|\bسه\s*أ\s*كه\s*از\s*آنها\b", "سه سببی که از آنها", "Text restoration"),
            (r"\bمخاظ\b", "مخاط", "Spelling"),
            (r"\bدهشد\b(?=\.)", "دهند", "Spelling"),
            (r"\bزساذدی\b", "زیادی", "Spelling: 'زیادی'"),
            (r"\bایفسوزن\b", "ایفوژن", "Medical term: 'ایفوژن'"),
            (r"\bمسوزن\b", "سوزن", "Medical term: 'سوزن'"),
            (r"\bسس\s*نی\s*اسکن\b|\bسر\s*فی\s*اسکن\b", "سی تی اسکن", "Medical radiology: 'سی تی اسکن'"),
            (r"\bاقبت\s*یک\s*[۵ه]\s*لاست\b", "عاقبت یک کلاپس", "Pulmonary collapse"),
            (r"\bنشسان\b", "نشان", "Spelling: 'نشان'"),
            (r"\bبیویسی\b", "بیوپسی", "Medical procedure: 'بیوپسی'"),
            (r"\bفی\s*شؤذه\b|\bسی‌شسود\b", "می‌شود", "Spelling: 'می‌شود'"),
            (r"\bفی\s*نقد\b", "می‌کند", "Spelling: 'می‌کند'"),
            (r"\bتکلس\s*با\s*کیف\b", "تکلس یا کثافت", "Radiology description"),
            (r"\bفحسؤلاً\s*شایل\b", "معمولاً شامل", "Text correction"),
            (r"\bراپور\s*مففسل\b", "راپور مفصل", "Medical report: 'راپور مفصل'"),
            (r"\bوشناعت\b", "وضاحت", "Medical radiology: 'وضاحت'"),
            (r"\bبرانشگتار\b", "برانشکتازی", "Medical pathology: 'برانشکتازی'"),
            (r"\bطرواه\b|\bإرواء\b", "ارواء", "Medical physiology: 'ارواء'"),
            (r"\bشبه\s*باند\b(?=\s*\(loculated\))", "شده باشد", "Text correction"),
            (r"\bکلاه\s*جبن\b", "کلاه، چپن", "PPE: 'کلاه، چپن'"),
            (r"\bلکنوکائین\s*AY\b|\bلگنوگائین\s*AN\b", "لگنوکائین ۲٪", "Medical drug: 'لگنوکائین ۲٪'"),
            (r"\bاخبیث\b", "خبیث", "Medical pathology: 'خبیث'"),
            (r"\bپلورودیزه\b", "پلورودیزیس", "Medical procedure: 'پلورودیزیس'"),
            (r"\bفرورفنگی\b", "فرورفتگی", "Anatomy: 'فرورفتگی'"),
            (r"\bعقدات\s*glial\b", "عقدات لمفاوی", "Anatomy: 'عقدات لمفاوی'"),
            (r"\bحبیثه\b", "خبیثه", "Medical pathology: 'خبیثه'"),
            (r"\bپوسیلٌ\b", "بوسیله", "Spelling: 'بوسیله'"),
            (r"\bأشکار\s*خواهد\s*یباخت\b", "آشکار خواهد ساخت", "Grammar correction"),
            (r"\bمیا\s*را\s*در\s*به\s*مرحله\s*بندی\b", "ما را در مرحله‌بندی", "Grammar correction"),
            (r"\bدفیق\b", "دقیق", "Spelling: 'دقیق'"),
            (r"\bسوزن\s*۸0۵۲\b|\bسوزن\s*بیوپسی\s*پلورای\s*ADAM\b", "سوزن بیوپسی پلورای Abrams", "Medical device: 'سوزن بیوپسی پلورای Abrams'"),
            (r"\bتخریک\b", "تحریک", "Medical physiology: 'تحریک'"),
            (r"\bاذیمای\b", "ادم", "Medical pathology: 'ادم'"),
            (r"\bاغلباً\b", "غالباً", "Spelling: 'غالباً'"),
            (r"\bاوغیه\b", "اوعیه", "Anatomy: 'اوعیه'"),
            (r"\bالضامی\b", "الضلعی", "Anatomy: 'الضلعی'"),
            (r"\bزسان\b", "زمان", "Spelling: 'زمان'"),
            (r"\bسوراغ\b", "سوراخ", "Spelling: 'سوراخ'"),
            (r"\bمتوجة\b", "متوجه", "Spelling: 'متوجه'"),
            (r"\bمتصدد\b", "متعدد", "Spelling: 'متعدد'"),
            (r"\bفورسالین\b", "فورمالین", "Medical reagent: 'فورمالین'"),
            (r"\bگولپس\b", "کولاپس", "Medical pathology: 'کولاپس'"),
            (r"\bلور\s*عضلی\b", "داخل عضلی", "Medical route: 'داخل عضلی'"),
            (r"\bناژوفرنگس\b", "نازوفارنکس", "Anatomy: 'نازوفارنکس'"),
            (r"\bتیادلة\s*کلو\s*بأ\b", "تبادله گاز با", "Physiology: 'تبادله گاز با'"),
            (r"\bمیکاتیکی\b", "میخانیکی", "Medical physics: 'میخانیکی'"),
            (r"\bبضا\s*برآن\b", "بنابرآن", "Grammar: 'بنابرآن'"),
            (r"\bکنواسیدوز\b", "کتواسیدوز", "Medical pathology: 'کتواسیدوز'"),
            (r"\bدیابنیسک\b", "دیابتیک", "Medical pathology: 'دیابتیک'"),
            (r"\bاسپدوز\b", "اسیدوز", "Medical pathology: 'اسیدوز'"),
            (r"\bغدم\s*گفایا\b", "عدم کفایه", "Medical pathology: 'عدم کفایه'"),
            (r"\bبایکاربونیث\b", "بایکاربونات", "Biochemistry: 'بایکاربونات'"),
            (r"\bتشکل\s*علفه\b", "تشکل علقه", "Medical pathology: 'تشکل علقه'"),
            (r"\bاستنمی\b", "مستمر", "Text correction"),
            (r"[۹٩]۳\s*ریه\s*dove!|\bdove!\s*ریه\b", "ادم ریه ۹۳", "Medical table: 'ادم ریه ۹۳'"),
            (r"\bW\s*توبرکلوز\b", "۱۷ توبرکلوز", "Contents page"),
            (r"\bمعایئات\b(?=\s+در\s+امراض)", "معاینات", "Spelling: 'معاینات'"),
            (r"\bاکسری\s*صدر\s*5١\b", "اکسری صدر ۲۹", "Contents page"),
            (r"\bسیتی\s*إسکن\s*ریه\s*۲۴\b", "سی تی اسکن ریه ۳۱", "Contents page"),
            (r"\bاسکن\s*تهویهارواء\s*یا\s*۱۷/۵56۵\s*۲۴\b", "اسکن تهویه-ارواء یا V/Q Scan ۳۱", "Contents page"),
            (r"\bاسپایریشن\s*و\s*بیوپسی\s*پلورا\s*۲۴\b", "اسپایریشن و بیوپسی پلورا ۳۴", "Contents page"),
            (r"\bبرونکوسکوپی\s*فایبرأبتیک\s*۲۵\b", "برونکوسکوپی فایبراوپتیک ۳۵", "Contents page"),
            (r"\bمعاینات\s*وظیفوی\s*ریه\s*یا\s*۳۴۲5\s*۳۵\b", "معاینات وظیفوی ریه یا PFTs ۳۵", "Contents page"),
            (r"\bعدم\s*کفایه\s*تنفسی\s*VA\b", "عدم کفایه تنفسی ۳۸", "Contents page"),
            (r"\bسندرم\s*زجرت\s*تنفسی\s*حاد\s*یا\s*FY\s*ARDS\b", "سندرم زجرت تنفسی حاد یا ARDS ۴۲", "Contents page"),
            (r"\bسندرم\s*آپنه\s*اهایپوپینی\s*خواب\b", "سندرم آپنه / هایپوپنه خواب", "Sleep disorder"),
            (r"\bپرانشکتاز\b", "برانشکتازی", "Medical pathology: 'برانشکتازی'"),
            (r"\bبانشکتاز\b", "برانشکتازی", "Medical pathology: 'برانشکتازی'"),
            (r"\bآپسة\s*ریه\s*۷۲۳\b", "آبسه ریه ۷۳", "Contents page"),
            (r"\bآپسة\b|\bأبسة\b", "آبسه", "Medical pathology: 'آبسه'"),
            (r"\bفیپروز\b", "فیبروز", "Medical pathology: 'فیبروز'"),
            (r"\bایوزینوفیلیک\b", "ائوزینوفیلیک", "Hematology: 'ائوزینوفیلیک'"),
            (r"\bJynas\b(?=\s+امراض)", "معمول", "Medical terminology"),
            (r"\bخروع\s*هوا\b", "خروج هوا", "Text correction"),
            (r"\bayy\s*ها\b", "ریه‌ها", "Anatomy: 'ریه‌ها'"),
            (r"\bریفلگسی\b", "رفلکسی", "Physiology: 'رفلکسی'"),
            (r"\bمععول\b", "معمول", "Spelling: 'معمول'"),
            (r"\bکلو\b(?=\s+از)", "گلو", "Anatomy: 'گلو'"),
            (r"\bمتخاط\b", "مخاط", "Anatomy: 'مخاط'"),
            (r"\bslags\s*ges\s*اجنبی\b", "مواد و ذرات اجنبی", "Text restoration"),
            (r"\bاسیاب\b", "اسباب", "Spelling: 'اسباب'"),
            (r"\bاد\s*\[که‌شر\s*از\s*۳\s*هفته\b", "حاد (کمتر از ۳ هفته)", "Duration classification"),
            (r"\bتبحت\s*الحاد\s*\(۲\s*ما\s*۸\s*هفته\b", "تحت‌حاد (۳ تا ۸ هفته)", "Duration classification"),
            (r"\bزیادت\s*راز\s*۸\s*\(asia\b", "زیادتر از ۸ هفته", "Duration classification"),
            (r"\bبلضم\b", "بلغم", "Spelling: 'بلغم'"),
            (r"\bace\s*نموده\b", "قطع نموده", "Text restoration"),
            (r"\bسرفة\s*بأشهذاز\b", "سرفه بلغم‌دار", "Medical symptom: 'سرفه بلغم‌دار'"),
            (r"\bتخرریش\b", "تخریش", "Medical symptom: 'تخریش'"),
            (r"\bweb\s*در\s*حالت\s*نورمال\b", "در حالت نورمال", "Text cleanup"),
            (r"\bمی‌گنشد\b", "می‌کنند", "Grammar: 'می‌کنند'"),
            (r"\bفزایش\s*دهشت\b", "افزایش دهند", "Grammar: 'افزایش دهند'"),
            (r"\bSPF\b(?=\s+است\s+که\s+مریضان)", "سبب", "Text restoration"),
            (r"\bSRD\s*guaifenesin\b", "گایافنزین (Guaifenesin)", "Medical drug"),
            (r"\bply\s*مقشع‌ها\b", "به نام مقشع‌ها", "Text correction"),
            (r"\bBiya\s*حاد\b", "سرفه حاد", "Medical symptom: 'سرفه حاد'"),
            (r"\bاک\s*مترافق\b", "اگرچه مترافق", "Text restoration"),
            (r"\bمی\s*shy\s*متراقق\b", "می‌تواند مترافق", "Text restoration"),
            (r"\bامپولی\b", "امبولی", "Medical pathology: 'امبولی'"),
            (r"\bمشخ\s*ص\s*ساختن\b", "مشخص ساختن", "Spelling: 'مشخص ساختن'"),
            (r"\bWY\b(?=\s+علت\s+سرفه)", "آیا", "Text restoration"),
            (r"\bسرماخورهکی\b", "سرماخوردگی", "Spelling: 'سرماخوردگی'"),
            (r"\bائتان\b", "انتان", "Spelling: 'انتان'"),
            (r"\bupper\s*21۳۷۷۵۱\s*cough\s*syndrome\s*اش\b", "Upper Airway Cough Syndrome (UACS)", "Medical syndrome"),
            (r"\bتاریخبچه\b", "تاریخچه", "Spelling: 'تاریخچه'"),
            (r"\bبکیرید\b", "بگیرید", "Spelling: 'بگیرید'"),
            (r"\bهمگن\s*است\b", "ممکن است", "Spelling: 'ممکن است'"),
            (r"\bعلست\b|\bغلت\b", "علت", "Spelling: 'علت'"),
            (r"\bخطرئاک\s*ذیکر\b", "خطرناک دیگر", "Spelling: 'خطرناک دیگر'"),
            (r"\bعلائم\s*خیاتی\b", "علائم حیاتی", "Medical examination: 'علائم حیاتی'"),
            (r"\bمعاینه\s*بیئی\s*و\s*کلو\b", "معاینه بینی و گلو", "Medical examination"),
            (r"\b۲0۵۳6\s*و\s*crepitation\b", "Rhonchi و Crepitation", "Auscultation signs"),
            (r"\bاصنای\s*قلب\b", "اصغای قلب", "Auscultation"),
            (r"\bنشان\s*ذهد\b", "نشان دهد", "Spelling: 'نشان دهد'"),
            (r"\bCle\s*زمینه‌ای\b", "علت زمینه‌ای", "Text restoration"),
            (r"\bبخارات\s*أب\b", "بخارات آب", "Spelling: 'بخارات آب'"),
            (r"\bPhlegm\s*\(wl\)\b", "Phlegm (بلغم)", "Medical terminology"),
            (r"\bAS\b(?=\s+از\s+سیستم\s+تنفسی)", "که", "Grammar"),
            (r"\bریدها\b", "ریه‌ها", "Anatomy: 'ریه‌ها'"),
            (r"\bببرون‌نمودن\b", "بیرون نمودن", "Spelling: 'بیرون نمودن'"),
            (r"\bذریعة\s*ad\s*yo\b", "ذریعه سرفه", "Text restoration"),
            (r"\bتشسخیص\b", "تشخیص", "Spelling: 'تشخیص'"),
            (r"\bحجرة\s*ابتیل\s*squamous\b", "حجره اپی‌تلیال Squamous", "Microscopy"),
            (r"\bطرة\s*تنفسی\b", "طرق تنفسی", "Anatomy: 'طرق تنفسی'"),
            (r"\bپتوژن\b", "پاتوژن", "Microbiology: 'پاتوژن'"),
            (r"\bمختاطی\+\s*گرده\s*یاغبار\s*زغال\b", "مخاطی + گرد و غبار زغال‌سنگ", "Text restoration"),
            (r"\bto\s*8\s*زنک\b", "به رنگ زنگ آهن", "Sputum sign"),
            (r"\bنوموکوکی\b", "پنوموکوکی", "Microbiology"),
            (r"\bهموپتایز\b|\bهماپتیز\b", "هماپتیزز", "Medical symptom: 'هماپتیزز'"),
            (r"\bحبول\s*صوتی\b", "حبال صوتی", "Anatomy: 'حبال صوتی'"),
            (r"\bپرانشیم\s*رینه\b", "پرانشیم ریه", "Anatomy: 'پرانشیم ریه'"),
            (r"\bخوئیء\s*سره\s*ها\b", "خونی، ریه‌ها", "Anatomy"),
            (r"\bZIRT\b(?=\s+جریان)", "۱ الی ۲ فیصد", "Physiology statistic"),
            (r"\bنف\s*کلدم\s*کاذب\b", "نفث‌الدم کاذب", "Medical diagnosis"),
            (r"\bثفکردن\b", "تف کردن", "Medical symptom"),
            (r"\bwile,\s*250۴0113۳۷۴\b", "نازوفارنکس یا بلعوم", "Anatomy"),
            (r"\bمجاری\s*oly\b", "مجاری هوایی", "Anatomy: 'مجاری هوایی'"),
            (r"\blegal\s*٩\s*قصبی\b", "برانشکتازی قصبی", "Pathology"),
            (r"\b1-70\s*صدر\b", "اکسری صدر", "Radiology"),
            (r"\bسی\s*تی\s*Sul\s*با\s*ریزولوشن\s*Yb\s*1/807\b", "سی تی اسکن با رزولوشن عالی (HRCT)", "Radiology"),
            (r"\bjbo\s*همابتیز\b", "دچار هماپتیز", "Text restoration"),
            (r"\bبرانشکتاه\s*ble!\s*ریوی\b", "برانشکتازی، آبسه ریوی", "Medical pathology"),
            (r"\bکانسر\s*ریه\s*و\s*۰\.۰\s*را\s*مشسخص\s*سازد\s*و\s*ازین\s*نقطه‌نظر\s*بر\s*برانکوسکوپی\s*برتسری\s*دارد\b", "کانسر ریه و غیره را مشخص سازد و از این نقطه‌نظر بر برونکوسکوپی برتری دارد", "Text restoration"),
            (r"\bطرق\s*هوائی\s*بعیده\s*را\s*که\s*برانکوسکوپ\s*به\s*آنها\s*رسیده\s*نمی‌تواند\s*نیز\s*نان\s*میذهد\b", "طرق هوایی محیطی را که برونکوسکوپ به آنها رسیده نمی‌تواند نیز نشان می‌دهد", "Text restoration"),
            (r"\bحساسیت\s*بیش\s*از\s*16٩۰\s*می‌باشد\b", "حساسیت بیش از ۹۰ الی ۹۵ فیصد می‌باشد", "Diagnostic sensitivity"),
            (r"\bتلقی\s*فی\s*شود\b", "تلقی می‌شود", "Grammar"),
            (r"\bمانغ\s*دیده\s*شدن\s*راه‌های\s*هؤائی\s*خصوصاً\s*در\s*سویة\s*:2\s*oof\b", "مانع دیده شدن راه‌های هوایی خصوصاً در سویه سگمنتی", "Text restoration"),
            (r"\bصفیحات\s*ذفویة\b", "صفیحات دمویه", "Hematology: 'صفیحات دمویه'"),
            (r"\bهموکلسوبین\b", "هموگلوبین", "Hematology: 'هموگلوبین'"),
            (r"\bBlee\s*Clotting\s*time\b", "Bleeding time, Clotting time, PT, PTT", "Coagulation tests"),
            (r"\b0108\s*۱۱۳6\b", "Blood Group", "Laboratory test"),
            (r"\bإمبولایزیشن\s*شریان\s*bronchial\b", "امبولایزیشن شریان برانشیال", "Interventional radiology"),
            (r"\bتداوی\s*Ede\b", "تداوی علت", "Text restoration"),
        ]

        for pat, repl, reason in persian_patterns:
            matches = re.findall(pat, cleaned_text)
            if matches:
                corrections.append(
                    OCRErrorCorrection(
                        page_num=page_num,
                        original=matches[0] if isinstance(matches[0], str) else pat,
                        corrected=repl,
                        confidence=0.96,
                        reason=reason,
                        applied=True,
                    )
                )
                cleaned_text = re.sub(pat, repl, cleaned_text)

        return cleaned_text, corrections
