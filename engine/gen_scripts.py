#!/usr/bin/env python3
"""Generate Arabic-track scene scripts (*.ar.script.json) from the parsed
question bank.

Every generated script is source-faithful and satisfies the project's
mandatory rules:
  * PURPOSE (مغزى) and TRAP (الفخ) scenes carry the docx text VERBATIM.
  * Every choice gets a verdict: right/wrong for THIS question, why it's
    wrong, and where that same choice WOULD be correct (`elsewhere`).
  * The full English stem is always displayed; narration is Arabic with
    English medical terminology preserved inline.
  * No characters/presenters -- visuals are diagrams and text only.

Per-choice `elsewhere` text is derived from the source's own bullet
explanations where they describe what a distractor actually is; that
description IS the answer to "where would this be correct". Choices with
no usable source description get a conservative fallback and are reported
so they can be deepened by hand.

Usage:
  python3 engine/gen_scripts.py questions/bank.json questions/ \
      [--course "6th Month 2013"] [--limit N] [--report]
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

ARABIC_RE = re.compile(r"[؀-ۿ]")
LATIN_RE = re.compile(r"[A-Za-z]")

# ---------------------------------------------------------------- helpers

def has_arabic(s):
    return bool(ARABIC_RE.search(s or ""))


def clean(s):
    """Normalize whitespace and strip stray markdown residue."""
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return s.strip()


def fix_ar_latin_spacing(s):
    """The source docx frequently glues an Arabic word to the next Latin
    word (and vice versa), which both looks wrong on screen and makes the
    TTS run-splitter mis-segment. Insert a space at those boundaries."""
    if not s:
        return s
    s = re.sub(r"([؀-ۿ])([A-Za-z])", r"\1 \2", s)
    s = re.sub(r"([A-Za-z])([؀-ۿ])", r"\1 \2", s)
    return re.sub(r"\s+", " ", s).strip()


def slug_course(course):
    """'6th Month 2013' -> '6mo2013'; '1st Month 2017' -> '1mo2017'."""
    m = re.match(r"(\d+)(?:st|nd|rd|th)?\s+Month\s+(\d{4})", course)
    if m:
        return f"{m.group(1)}mo{m.group(2)}"
    return re.sub(r"[^a-z0-9]+", "-", course.lower()).strip("-")


def sentence_case(s):
    return s[:1].upper() + s[1:] if s else s


def cap(s, limit):
    """Trim to `limit` chars on a word boundary.

    The verdict list is laid out on a fixed 1920x1080 canvas with five rows;
    unbounded source text overflows off-screen (confirmed by stress-testing
    the longest questions in the bank), so on-screen strings are capped.
    Narration is NOT capped -- the spoken explanation keeps the full detail.
    """
    s = clean(s)
    if len(s) <= limit:
        return balance_parens(s)
    cut = s[:limit]
    sp = cut.rfind(" ")
    if sp > limit * 0.6:
        cut = cut[:sp]
    # Balance AFTER trimming -- truncation is itself a common way to strand
    # an opening bracket.
    return balance_parens(cut.rstrip(" ,;:-—")) + "…"


# ------------------------------------------------------- bullet analysis

def split_bullet_clauses(bullet):
    """Split a bullet into the finest clauses that still describe one entity.

    A comprehensive bullet often covers several distractors at once, either
    separated by ';' or strung together with 'and'/','. Splitting only on
    ';' leaves one sweeping clause that then gets pasted onto every choice.
    So long clauses are further split on ', and' / ' and ' / ',' -- but only
    when the resulting fragment still looks like a description (contains a
    verb), so entity names like "second and third portion of the duodenum"
    aren't torn apart into meaningless pieces.
    """
    VERBISH = re.compile(
        r"\b(is|are|was|were|presents?|present|causes?|occurs?|refers?|"
        r"describes?|produces?|involves?|affects?|appears?|remains?|has|have|"
        r"typically|usually|classically|rather)\b", re.I)

    out = []
    for part in re.split(r"[;]", bullet):
        part = clean(part)
        if not part:
            continue
        out.append(part)
        if len(part) < 90:
            continue
        # Try a finer split for sweeping clauses.
        fine = [clean(x) for x in re.split(r",\s+and\s+|\s+and\s+|,\s+", part)]
        fine = [x for x in fine if len(x) >= 18 and VERBISH.search(x)]
        if len(fine) >= 2:
            out.extend(fine)
    return out


def choice_keywords(text):
    """Content tokens from a choice, used to match it to a bullet clause.

    Includes numeric/percentage tokens, not just words: plenty of questions
    have purely numeric choices ("30%", "0.8%", "2 cm"), and a word-only
    keyword set finds nothing to match on for those.
    """
    text = text or ""
    words = re.findall(r"[A-Za-z][A-Za-z\-']{2,}", text)
    stop = {
        "the", "and", "then", "with", "for", "are", "was", "were", "this",
        "that", "than", "more", "most", "less", "common", "seen", "from",
        "into", "out", "his", "her", "its", "not", "all", "can", "may",
        "has", "have", "been", "will", "would", "should", "there", "these",
        "which", "what", "when", "where", "who", "whom", "does", "did",
    }
    kws = [w.lower() for w in words if w.lower() not in stop]
    # Numbers, percentages and measurements are identity-bearing for
    # numeric-answer questions.
    kws += [m.group(0).lower() for m in re.finditer(r"\d+(?:\.\d+)?\s*%?", text)]
    return [k.strip() for k in kws if k.strip()]


# Source bullets sometimes contain editorial meta-commentary about the
# answer key itself rather than medical content. That text is useless (and
# confusing) on screen, so clauses containing it are rejected outright.
META_RE = re.compile(
    r"per the source|marked correct answer|this entry clarifies|highlighted here|"
    r"worth flagging|note:|the true/correct statement|correct exception|"
    r"\(correct\)|making (?:this|it) the (?:correct|right)",
    re.I,
)


# Option letters are referenced in several shapes across the source:
#   "(A)"  "(A, B)"  "(C, D, E — byssinosis, silicosis)"  "(A is false)"
#   "(A, B are false)"
# Matching only the first two silently loses the explanations attached to the
# rest, which is why those choices used to fall back to generic text.
LETTER_GROUP_RE = re.compile(
    r"\(\s*([A-E](?:\s*(?:,|and|&)\s*[A-E])*)\s*(?:[—\-–:,)]|(?:is|are)\b)"
)


# "EXCEPT"-style stems invert the logic of the whole question: the marked
# answer is the odd one out, and every OTHER choice is a true/valid member.
# That changes what the two mandatory per-choice statements should say --
# a distractor isn't "wrong", it's true-but-not-the-exception -- so these
# stems get their own phrasing. Detection is deliberately conservative:
# a bare lowercase "not" appears in plenty of ordinary stems.
EXCEPT_RE = re.compile(
    r"\bEXCEPT\b|\bNOT\b|\bFALSE\b|\bINCORRECT\b|"
    r"\b(?:is|are)\s+(?:not\s+true|false|incorrect)\b|"
    r"\b(?:false|incorrect|untrue|wrong)\s+statement\b|"
    r"\ball\s+.{0,40}\bexcept\b",
    re.I if False else 0,  # case-sensitive for the bare keywords
)
EXCEPT_RE_CI = re.compile(
    r"\b(?:false|incorrect|untrue|wrong)\s+statement\b|"
    r"\b(?:is|are)\s+not\s+true\b|"
    r"\ball\s+.{0,40}\bexcept\b",
    re.I,
)


def is_except_question(q):
    stem = f"{q.get('trigger_en','')} {q.get('trigger_ar','')}"
    return bool(EXCEPT_RE.search(stem) or EXCEPT_RE_CI.search(stem))


def strip_meta_tail(clause):
    """Cut a clause at the point where it stops describing medicine and starts
    commenting on the answer key.

    Source bullets often read
        "<real medical content about several options> ... making B the false
         statement (the correct exception)."
    Rejecting the whole clause because of that tail threw away the useful
    half, which is why several questions fell back to generic text. Trim the
    tail instead and keep the medicine.
    """
    m = META_RE.search(clause)
    if not m:
        return clause
    head = clause[: m.start()]
    # Also drop a dangling connector left at the cut point.
    head = re.sub(r"[\s,;—–\-]*(?:and|but|while|whereas|unlike|making)?[\s,;—–\-]*$",
                  "", head, flags=re.I)
    return clean(head)


def find_clause_for_choice(choice, bullets):
    """Find the bullet clause that specifically describes THIS choice.

    Requires real evidence that the clause is about this choice -- either an
    explicit letter reference or a match on the choice's own distinctive
    words. Without that guard a single sweeping clause gets pasted onto
    every distractor, which reads as obviously wrong on screen.
    """
    kws = choice_keywords(choice["text"])
    letter = choice["letter"]
    best, best_score = None, 0
    for bullet in bullets:
        for raw_clause in split_bullet_clauses(bullet):
            clause = strip_meta_tail(raw_clause)
            if len(clause) < 20:
                continue
            low = clause.lower()
            lettered = False
            # Letter groups appear both as bare "(C, D, E)" and annotated
            # "(C, D, E — byssinosis, pneumoconiosis, silicosis)", so match a
            # leading run of letters and ignore any trailing gloss.
            for m in re.finditer(LETTER_GROUP_RE, clause):
                group = re.split(r"\s*(?:,|and|&)\s*", m.group(1))
                if letter in [x.strip() for x in group]:
                    lettered = True
            kw_hits = sum(1 for kw in set(kws) if kw in low)
            # Demand topical evidence: either this choice is named by letter,
            # or enough of its own content words appear in the clause.
            if not lettered and kw_hits < 2:
                continue
            score = (6 if lettered else 0) + 2 * kw_hits
            if re.search(r"\b(is|are|presents?|causes?|occurs?|refers?|describes?)\b", low):
                score += 1
            if score > best_score:
                best, best_score = clause, score
    return best if best_score >= 4 else None


def balance_parens(s):
    """Drop unbalanced brackets left behind by trimming/splitting.

    Derived text is cut at sentence and contrast boundaries, which can strand
    an opening '(' with no partner (or vice versa); a lone bracket on a card
    reads as a rendering bug.
    """
    if not s:
        return s
    if s.count("(") > s.count(")"):
        s = s[: s.rfind("(")].rstrip(" ,;:-—")
    while s.count(")") > s.count("("):
        s = s.replace(")", "", 1)
    return clean(s)


def strip_letter_refs(s):
    """Remove this question's own option letters from derived text.

    Letters refer to THIS question's lettering, so leaving them in an
    "elsewhere" note (which describes a *different* hypothetical question)
    is actively confusing. Handles both bare groups "(A, B)" and annotated
    ones "(C, D, E — byssinosis, silicosis)", keeping the gloss and dropping
    only the letters.
    """
    # Annotated group: keep the explanatory tail, drop the letters.
    s = re.sub(
        r"\(\s*[A-E](?:\s*(?:,|and|&)\s*[A-E])*\s*[—\-–:]\s*([^)]*)\)",
        r"(\1)", s)
    # Verdict-style group, e.g. "(A is false)" / "(A, B are false)".
    s = re.sub(
        r"\s*\(\s*[A-E](?:\s*(?:,|and|&)\s*[A-E])*\s+(?:is|are)\s+[^)]*\)",
        "", s)
    # Bare group: drop entirely.
    s = re.sub(r"\s*\(\s*[A-E](?:\s*(?:,|and|&)\s*[A-E])*\s*\)", "", s)
    return clean(s)


# Markers that separate "what this entity actually is" (before) from
# "why it doesn't fit this question" (after).
CONTRAST_RE = re.compile(
    r"\s*(?:,\s*)?(?:\bnot\b|\brather than\b|\binstead of\b|\bdoesn't\b|"
    r"\bdoes not\b|\bwouldn't\b|\bwould not\b|\bis not\b|\bare not\b)\s+",
    re.I,
)


def describe_choice(clause, choice_text):
    """Split a bullet clause into (what it IS, why it fails HERE).

    Source clauses are typically written as
        "<entity> is/presents as <description>, not <what this question shows>"
    so the part before the contrast marker answers "where would this choice
    be correct", and the part after answers "why is it wrong here". Returning
    them separately keeps the two mandatory statements genuinely distinct
    instead of repeating one sentence twice.
    """
    if not clause:
        return None, None
    c = strip_letter_refs(clause)
    c = re.sub(r"^(?:and|but|while|whereas|however|only)\s+", "", c, flags=re.I)
    # Drop tails that refer back to THIS question's answer.
    c = re.split(r"\s+—\s+only\b", c, flags=re.I)[0]
    c = re.split(r"\s*,\s*making (?:this|it)\b", c, flags=re.I)[0]
    c = re.split(r"\s+—\s+none matches\b", c, flags=re.I)[0]
    c = clean(c).rstrip(".")
    if len(c) < 12:
        return None, None

    positive, contrast = c, None
    for m in CONTRAST_RE.finditer(c):
        # Don't split inside a parenthetical aside: source text like
        # "actually less (not more) common than inguinal" would otherwise cut
        # at the inner "not" and leave a dangling "(" fragment.
        if c.count("(", 0, m.start()) != c.count(")", 0, m.start()):
            continue
        head = clean(c[: m.start()]).rstrip(",").rstrip()
        tail = clean(c[m.end():]).rstrip(".")
        if len(head) >= 12:
            positive = head
            if tail:
                contrast = tail
        break
    return balance_parens(positive), balance_parens(contrast)


# ----------------------------------------------------- illustration logic

BODY_KEYWORDS = [
    (("abdom", "bowel", "colon", "gastric", "stomach", "liver", "biliary",
      "pancrea", "spleen", "appendic", "hernia", "peritone", "ileum",
      "duoden", "rectal", "rectum", "gallbladder", "jejun", "caecum",
      "cecum", "sigmoid", "anal", "anus", "hepat", "cholecyst", "splenic",
      "mesenter", "omentum", "gastro", "volvulus", "intussuscept",
      "diverticul", "ulcer", "varice", "ascites", "portal", "bariatric",
      "pyloric", "meckel", "fistula-in-ano", "haemorrhoid", "hemorrhoid"), "abdomen"),
    (("chest", "lung", "thorax", "pulmon", "pleural", "cardiac", "heart",
      "aortic", "esophag", "oesophag", "mediastin", "breast", "rib",
      "pneumothorax", "empyema", "bronch", "trachea", "thoracic",
      "myocard", "coronary", "valve", "mastectomy", "nipple"), "chest"),
    (("pelvi", "inguinal", "scrotal", "testic", "prostat", "bladder",
      "urethra", "femoral", "groin", "renal", "kidney", "ureter",
      "urolog", "hydrocele", "varicocele", "phimosis", "circumcis",
      "uterus", "ovarian", "penile", "perineal", "hypospadias"), "pelvis"),
    (("limb", "leg", "arm", "hand", "foot", "fracture", "tibia", "femur",
      "humerus", "digit", "vascular", "varicose", "claudicat", "ankle",
      "knee", "shoulder", "wrist", "elbow", "toe", "finger", "carpal",
      "amputat", "gangrene", "ischaemi", "ischemi", "arterial", "venous",
      "thrombos", "embol", "compartment", "nerve palsy", "burn"), "limb"),
    (("neck", "thyroid", "head", "skull", "brain", "cranial", "scalp",
      "parotid", "facial", "intracranial", "salivary", "tongue", "oral",
      "larynx", "pharyn", "tonsil", "cervical", "goitre", "goiter",
      "parathyroid", "eye", "ear", "nasal", "sinus", "meningi", "glasgow"), "head"),
]


def pick_region(*texts):
    blob = " ".join(t or "" for t in texts).lower()
    for keys, region in BODY_KEYWORDS:
        if any(k in blob for k in keys):
            return region
    return "generic"


ORDER_HINT = re.compile(r"\b(order|sequence|first|then|steps?|stage|phase)\b", re.I)


def build_illustration(q, label_en):
    """Choose a generic illustration that genuinely reflects this
    question's content, rather than decorating every scene identically."""
    stem = f"{q.get('trigger_en','')} {q.get('correct_text','')}"
    # A question about ordering/sequence -> sequence diagram from the
    # correct answer's own steps, when it reads as a chain.
    if ORDER_HINT.search(stem):
        parts = re.split(r"\s*(?:,|then|→|->)\s*", q.get("correct_text", ""))
        parts = [sentence_case(clean(p)) for p in parts if clean(p)]
        if 2 <= len(parts) <= 4:
            return {"type": "sequence", "steps": parts}
    region = pick_region(q.get("trigger_en"), q.get("correct_text"), q.get("connection_en"))
    if region != "generic":
        return {"type": "body", "region": region, "label": label_en}
    # No anatomical region and no sequence: show the key term itself rather
    # than a decorative icon, which carries no information.
    return {"type": "keyterm", "label": clean(q.get("correct_text") or label_en),
            "sub": "الإجابة الصحيحة"}


# ------------------------------------------------------------- narration

def speakable_en(text, max_words=4):
    """Return an English fragment only if it is short enough to be a TERM.

    The project's rule is Arabic narration with English used for medical
    terminology -- not for whole English sentences. The source's own
    explanations are English prose, and reading them aloud handed the English
    voice 42% of the narration and made every video far longer than it needed
    to be. Anything longer than a term stays on screen, where reading it is
    useful, and is left out of the spoken track.
    """
    t = clean(text)
    return t if t and len(t.split()) <= max_words else ""


def english_word_count(text):
    """How many English words a mixed Arabic/English string would hand to the
    English voice."""
    return len(re.findall(r"[A-Za-z][A-Za-z\-']*", text or ""))


# Boilerplate that reads fine once on a card but grates when the narrator
# repeats it for every wrong choice in a row.
SPOKEN_TRIM = [
    ("لا يتوافق مع معطيات هذا السؤال — المطلوب هنا", "المطلوب هنا"),
    ("لا يتوافق مع معطيات هذا السؤال؛ الإجابة الصحيحة هي", "الإجابة الصحيحة هي"),
    ("لا ينطبق على هذه الحالة:", "الحقيقة أن"),
    ("عبارة صحيحة فعليًا، والسؤال يطلب الاستثناء.", "صحيحة، لكنها ليست الاستثناء."),
]


def speakable_line(text, max_en_words=6):
    """Keep a mixed sentence for narration only if its English part is small
    enough to read as embedded terminology rather than an English sentence."""
    t = clean(text)
    if not t or english_word_count(t) > max_en_words:
        return ""
    for long_form, short_form in SPOKEN_TRIM:
        if t.startswith(long_form):
            t = short_form + t[len(long_form):]
            break
    return t


def speak_choice(letter, text):
    """Name a choice aloud: with its term when short, by letter alone when the
    choice is a full English statement (which is on screen anyway)."""
    term = speakable_en(text, 4)
    return f"الخيار {letter}، {term}" if term else f"الخيار {letter}"


def opts_phrase(choices):
    """Arabic narration listing the choices, English terms preserved."""
    return "، أو ".join(clean(c["text"]) for c in choices)


def build_script(course, q, course_index, total_in_course):
    cslug = slug_course(course)
    qid = f"surgery-{cslug}-{q['number']:02d}-ar"

    correct = next((c for c in q["choices"] if c["correct"]), None)
    stem_en = clean(q.get("trigger_en") or q.get("correct_text") or "")
    stem_ar = fix_ar_latin_spacing(clean(q.get("trigger_ar") or ""))
    purpose = fix_ar_latin_spacing(clean(q.get("purpose_ar") or ""))
    trap = fix_ar_latin_spacing(clean(q.get("trap_ar") or ""))
    conn_ar = fix_ar_latin_spacing(clean(q.get("connection_ar") or ""))
    conn_en = clean(q.get("connection_en") or "")
    mnem = clean(q.get("mnemonic") or "")
    mnem_note = fix_ar_latin_spacing(clean(q.get("mnemonic_note") or ""))
    bullets = [clean(b) for b in q.get("bullets", []) if clean(b)]
    except_style = is_except_question(q)

    # ---- per-choice verdicts (mandatory rule) -------------------------
    # `verdicts` carries the ON-SCREEN (capped) text; `spoken` keeps the
    # full-length version so narration never loses detail the card had to
    # trim for layout.
    verdicts = []
    spoken = []
    weak = []
    # A single sweeping source clause can legitimately describe several
    # distractors at once. Showing the identical sentence on four rows reads
    # as a bug even when it's accurate, so reuse is allowed twice and then
    # falls back to the per-choice generic form.
    desc_uses = {}
    for ch in q["choices"]:
        text = clean(ch["text"])
        if ch["correct"]:
            reason = conn_ar or f"هو الإجابة الصحيحة: {text}."
            verdicts.append({
                "letter": ch["letter"],
                "text": cap(text, 90),
                "verdict": "correct",
                "reason": cap(reason, 180),
            })
            spoken.append({"letter": ch["letter"], "text": text,
                           "verdict": "correct", "reason": reason, "elsewhere": ""})
            continue
        clause = find_clause_for_choice(ch, bullets)
        desc, contrast = describe_choice(clause, text)
        if except_style:
            # In an EXCEPT question the distractors are the TRUE statements;
            # they're "wrong" only in the sense that they are not the odd one
            # out. Saying "doesn't fit this case" about them would be false.
            # Key message first: the length cap trims the tail, so leading
            # with the long description would truncate away the actual point.
            if desc:
                reason = f"عبارة صحيحة فعليًا، والسؤال يطلب الاستثناء. {cap(desc, 95)}"
            else:
                weak.append(ch["letter"])
                reason = "عبارة صحيحة فعليًا، والسؤال يطلب الاستثناء — أي الخيار الذي لا ينطبق."
            elsewhere = (
                f"يصبح هو الإجابة في سؤال يسأل: أيٌّ مما يلي ينطبق فعلًا؟ "
                f"أما هنا فالمطلوب الاستثناء، وهو {clean(correct['text']) if correct else ''}."
            )
        elif desc:
            # "Why wrong HERE" uses the contrast half when the source gives
            # one, so it says something different from the "where it WOULD
            # be correct" line rather than repeating it.
            if contrast:
                reason = f"لا يتوافق مع معطيات هذا السؤال — المطلوب هنا {contrast}."
            else:
                reason = (
                    f"لا يتوافق مع معطيات هذا السؤال؛ الإجابة الصحيحة هي "
                    f"{clean(correct['text']) if correct else ''}."
                )
            elsewhere = f"يصبح صحيحًا في سؤال يصف {desc}."
        else:
            weak.append(ch["letter"])
            reason = f"لا يتوافق مع معطيات هذا السؤال؛ الإجابة الصحيحة هي {clean(correct['text']) if correct else ''}."
            elsewhere = (
                f"يصبح صحيحًا في سؤال يستهدف {text} تحديدًا بمعطياته المميزة، "
                "لا في السيناريو المطروح هنا."
            )
        verdicts.append({
            "letter": ch["letter"],
            "text": cap(text, 90),
            "verdict": "wrong",
            "reason": cap(reason, 170),
            "elsewhere": cap(elsewhere, 170),
        })
        spoken.append({"letter": ch["letter"], "text": text, "verdict": "wrong",
                       "reason": reason, "elsewhere": elsewhere})

    # ---- narration ----------------------------------------------------
    # Don't read all five options aloud -- they are on screen in the next
    # scene, and reciting them was ~160k characters of English across the bank.
    # The opening frame carries the stem and all choices, so the narration
    # reads the stem and then leaves a beat for the student to actually try
    # the question before the explanation starts.
    n_question = (
        f"لنبدأ بهذا السؤال. {stem_ar or ''} "
        f"أمامك {len(q['choices'])} خيارات على الشاشة — "
        "اقرأها وحاول أن تجيب قبل أن نكمل."
    ).strip()

    n_purpose = f"قبل أن نتابع، هذه هي فكرة السؤال الأساسية. مغزى السؤال: {purpose}"

    concept_bits = [b for b in [conn_ar] if b]
    if mnem_note:
        concept_bits.append(mnem_note)
    n_concept = (
        "لنفهم الفكرة الطبية وراء السؤال. " + " ".join(concept_bits)
        if concept_bits else
        "لنفهم الفكرة الطبية وراء هذا السؤال ونربط المعطيات بالتشخيص الصحيح."
    )

    # Spoken pass over the choices stays Arabic and brief. The full per-choice
    # detail -- including the source's English wording and the "where would
    # this be correct" line -- is on the card the whole time; speaking it too
    # doubled the length of the longest scene for no teaching benefit.
    wrong_v = [v for v in spoken if v["verdict"] == "wrong"]
    n_wrong_parts = [
        "لنراجع بقية الخيارات — كلها عبارات صحيحة فعليًا، والمطلوب هو الاستثناء."
        if except_style else
        "لنراجع الخيارات الخاطئة."
    ]
    for v in wrong_v:
        # Prefer the real reason when it is Arabic carrying only a term or
        # two -- saying something different (and specific) about each choice
        # is the teaching value. Fall back to a generic line only when the
        # reason is English prose, which belongs on screen instead.
        reason = speakable_line(v["reason"], 6)
        if reason:
            line = f"{speak_choice(v['letter'], v['text'])}: {reason}"
        elif except_style:
            line = f"{speak_choice(v['letter'], v['text'])}: صحيحة، لكنها ليست الاستثناء."
        else:
            line = f"{speak_choice(v['letter'], v['text'])}: لا ينطبق على هذه الحالة."
        n_wrong_parts.append(line)
    n_wrong_parts.append("والتفصيل الكامل لكل خيار، ومتى يصبح صحيحًا، مكتوب أمامك على الشاشة.")
    n_wrong = " ".join(n_wrong_parts)

    n_trap = f"وهنا الفخ الذي يقع فيه كثير من الطلاب. الفخ: {trap}"

    n_correct = (
        f"{speak_choice(correct['letter'], correct['text'])} هو الإجابة الصحيحة. {conn_ar}"
    ).strip() if correct else "الإجابة الصحيحة موضحة على الشاشة."

    # The mnemonic is an English one-liner by design -- short enough to be
    # worth saying, unlike the explanations.
    n_take = (
        f"لنُثبّت الفكرة. {conn_ar} "
        + (f"وتذكّر: {mnem}. " if mnem and len(mnem.split()) <= 10 else "")
        + (f"والإجابة الصحيحة هي {correct['letter']}." if correct else "")
    ).strip()

    summary_ar = conn_ar or purpose

    # cap() trims on a word boundary; a bare slice cut mid-word and left
    # labels reading like "…diverticulum sho".
    label_en = cap(clean(q.get("correct_text") or stem_en), 52)
    illo = build_illustration(q, label_en)

    scenes = [
        {
            "id": "QUESTION",
            "visual": "question_card",
            "caption": stem_en[:60] if stem_en else "Question",
            "illustration": illo,
            "narration": n_question,
        },
        # No separate options scene: the opening frame already shows the stem
        # and every choice together, so the student can attempt the question
        # before any teaching begins.
        {
            "id": "PURPOSE",
            "visual": "purpose_card",
            "heading_ar": "مغزى السؤال",
            "caption": "مغزى السؤال",
            "text_ar": purpose,
            "narration": n_purpose,
        },
        {
            "id": "CONCEPT",
            "visual": "mechanism_card",
            "heading_ar": "الفكرة الطبية",
            "caption": label_en or "Key concept",
            "illustration": illo,
            "card_text": conn_ar or purpose,
            "narration": n_concept,
        },
        {
            "id": "WHY_WRONG",
            "visual": "verdict_list",
            "heading_ar": "تحليل كل خيار",
            "caption": "لماذا كل خيار صحيح أو خاطئ",
            "narration": n_wrong,
            "verdicts": verdicts,
        },
        {
            "id": "TRAP",
            "visual": "trap_card",
            "heading_ar": "الفخ",
            "caption": "الفخ",
            "text_ar": trap,
            "narration": n_trap,
        },
        {
            "id": "WHY_CORRECT",
            "visual": "correct_gold",
            "caption": f"{correct['letter']}. {clean(correct['text'])[:48]}" if correct else "الإجابة الصحيحة",
            # A keyterm card here would just restate the gold banner directly
            # above it, so only carry a genuinely different visual through.
            "illustration": None if illo.get("type") == "keyterm" else illo,
            "pills": [p for p in [mnem[:46] if mnem else None] if p],
            "narration": n_correct,
        },
        {
            "id": "TAKE_HOME",
            "visual": "summary_card",
            "caption": "نلقاكم في السؤال القادم",
            "narration": n_take,
        },
    ]

    script = {
        "id": qid,
        "source": f"Surgery Board Question Bank -- {course} Course, Question {q['number']} of {total_in_course}",
        "language": "ar",
        "voice": "ar-EG-ShakirNeural",
        "rate_percent": "-10%",
        "question": stem_en,
        "question_ar": stem_ar,
        "course_label": f"Course: Surgery — {course} Course",
        "question_number": q["number"],
        "options": [{"letter": c["letter"], "text": clean(c["text"])} for c in q["choices"]],
        "correct_letter": correct["letter"] if correct else "",
        "correct_text": clean(correct["text"]) if correct else "",
        "purpose_ar": purpose,
        "trap_ar": trap,
        "summary_ar": summary_ar,
        "scenes": scenes,
    }
    return script, weak


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bank")
    ap.add_argument("outdir")
    ap.add_argument("--course", help="only this course (substring match)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    bank = json.loads(Path(args.bank).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    written, skipped, weak_report = 0, [], []
    for course_rec in bank:
        course = course_rec["course"]
        if args.course and args.course.lower() not in course.lower():
            continue
        total = len(course_rec["questions"])
        for i, q in enumerate(course_rec["questions"]):
            if not any(c["correct"] for c in q["choices"]):
                skipped.append(f"{course} Q{q['number']} (no confirmed answer in source)")
                continue
            if not q.get("purpose_ar") or not q.get("trap_ar"):
                skipped.append(f"{course} Q{q['number']} (missing purpose/trap)")
                continue
            script, weak = build_script(course, q, i, total)
            path = outdir / f"{script['id'][:-3]}.ar.script.json"
            path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
            written += 1
            if weak:
                weak_report.append(f"{course} Q{q['number']}: weak elsewhere for {','.join(weak)}")
            if args.limit and written >= args.limit:
                break
        if args.limit and written >= args.limit:
            break

    print(f"Wrote {written} scripts to {outdir}")
    if skipped:
        print(f"\nSkipped {len(skipped)} (flagged, never guessed):")
        for s in skipped:
            print("  -", s)
    if args.report and weak_report:
        print(f"\n{len(weak_report)} questions have auto-derived 'elsewhere' text that "
              f"should be deepened by hand:")
        for w in weak_report[:30]:
            print("  -", w)
        if len(weak_report) > 30:
            print(f"  ... and {len(weak_report)-30} more")
    elif weak_report:
        print(f"\n{len(weak_report)} questions flagged for hand-deepening (use --report to list)")


if __name__ == "__main__":
    main()
