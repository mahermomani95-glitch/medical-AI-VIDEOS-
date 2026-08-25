#!/usr/bin/env python3
"""Parse the Surgery Master Video Project source text into a structured
question bank (questions/bank.json).

The source docx (exported to text) is highly regular: 22 course banners,
each followed by `**QUESTION N**` blocks with fixed sub-headers. This
parser turns all 1031 of them into machine-readable records so scripts can
be authored from real source content instead of re-searching the doc per
question.

Usage: python3 engine/parse_bank.py <source.txt> <out.json>
"""
import json
import re
import sys
from pathlib import Path

COURSE_RE = re.compile(r"^\*\*Surgery — (.+?) Course\*\*$")
COUNT_RE = re.compile(r"^\*(\d+) questions?\*$")
QUESTION_RE = re.compile(r"^\*\*QUESTION (\d+)\*\*$")
CHOICE_RE = re.compile(r"^(?:\*\*)?([A-E])\.\s*(.+?)(?:\s*✓)?(?:\*\*)?$")
ARABIC_RE = re.compile(r"[؀-ۿ]")

# Section headers inside a question block.
H_TRIGGER = "TRIGGER / QUESTION STEM"
H_ANSWER = "CORRECT ANSWER + ALL CHOICES + EXPLANATION"
H_CONNECT = "CONNECTION SENTENCE / MNEMONIC"
H_PURPOSE = "PURPOSE — مغزى السؤال"
H_TRAP = "TRAP — الفخ"


def strip_md(s: str) -> str:
    """Remove bold/italic markers and the ✓ correct-answer marker."""
    s = s.replace("✓", "")
    s = re.sub(r"\*+", "", s)
    return s.strip()


def has_arabic(s: str) -> bool:
    return bool(ARABIC_RE.search(s))


def parse(text: str):
    lines = [ln.rstrip() for ln in text.split("\n")]
    courses = []
    current_course = None
    current_q = None
    section = None

    def close_q():
        nonlocal current_q
        if current_q and current_course:
            current_course["questions"].append(current_q)
        current_q = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        m = COURSE_RE.match(line)
        if m:
            close_q()
            current_course = {"course": m.group(1), "declared_count": None, "questions": []}
            courses.append(current_course)
            section = None
            continue

        if current_course is not None and current_course["declared_count"] is None:
            m = COUNT_RE.match(line)
            if m:
                current_course["declared_count"] = int(m.group(1))
                continue

        m = QUESTION_RE.match(line)
        if m and current_course is not None:
            close_q()
            current_q = {
                "number": int(m.group(1)),
                "trigger_en": None,
                "trigger_ar": None,
                "correct_text": None,
                "correct_ar": None,
                "choices": [],
                "connection_en": None,
                "connection_ar": None,
                "mnemonic": None,
                "mnemonic_note": None,
                "purpose_ar": None,
                "trap_ar": None,
                "bullets": [],
            }
            section = None
            continue

        if current_q is None:
            continue

        # Section switches.
        plain = strip_md(line)
        if H_TRIGGER in plain:
            section = "trigger"
            continue
        if H_ANSWER in plain:
            section = "answer"
            continue
        if H_CONNECT in plain:
            section = "connect"
            continue
        if plain.startswith("PURPOSE") and "مغزى" in plain:
            section = "purpose"
            continue
        if plain.startswith("TRAP") and "الفخ" in plain:
            section = "trap"
            continue

        # Bullet lines (per-choice reasoning material) can appear after trap.
        if line.startswith("•"):
            current_q["bullets"].append(strip_md(line.lstrip("•").strip()))
            continue

        if section == "trigger":
            if has_arabic(line):
                if current_q["trigger_ar"] is None:
                    current_q["trigger_ar"] = plain
            else:
                if current_q["trigger_en"] is None:
                    current_q["trigger_en"] = plain
            continue

        if section == "answer":
            m = CHOICE_RE.match(line)
            if m:
                letter, body = m.group(1), strip_md(m.group(2))
                current_q["choices"].append({
                    "letter": letter,
                    "text": body,
                    "correct": "✓" in line,
                })
                continue
            if line.startswith("الإجابة الصحيحة"):
                current_q["correct_ar"] = plain
                continue
            if current_q["correct_text"] is None and not has_arabic(line):
                current_q["correct_text"] = plain
                continue
            continue

        if section == "connect":
            if "Mnemonic" in line or "🧠" in line:
                current_q["mnemonic"] = strip_md(line.replace("🧠", "")).replace("Mnemonic:", "").strip()
                continue
            if has_arabic(line):
                if current_q["connection_ar"] is None:
                    current_q["connection_ar"] = plain
                elif current_q["mnemonic_note"] is None:
                    current_q["mnemonic_note"] = plain
            else:
                if current_q["connection_en"] is None:
                    current_q["connection_en"] = plain
            continue

        if section == "purpose":
            val = plain
            for prefix in ("مغزى السؤال:", "مغزى السؤال :"):
                if val.startswith(prefix):
                    val = val[len(prefix):].strip()
            if current_q["purpose_ar"] is None:
                current_q["purpose_ar"] = val
            continue

        if section == "trap":
            val = plain
            for prefix in ("الفخ:", "الفخ :"):
                if val.startswith(prefix):
                    val = val[len(prefix):].strip()
            if current_q["trap_ar"] is None:
                current_q["trap_ar"] = val
            continue

    close_q()
    return courses


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    courses = parse(src.read_text(encoding="utf-8"))

    total = sum(len(c["questions"]) for c in courses)
    print(f"Parsed {len(courses)} courses, {total} questions")
    for c in courses:
        n = len(c["questions"])
        declared = c["declared_count"]
        flag = "" if declared == n else f"  <-- declared {declared}"
        print(f"  {c['course']}: {n}{flag}")

    # Integrity report -- which questions are missing required fields.
    missing = []
    for c in courses:
        for q in c["questions"]:
            gaps = [k for k in ("trigger_en", "correct_text", "purpose_ar", "trap_ar") if not q.get(k)]
            if not q["choices"]:
                gaps.append("choices")
            if not any(ch["correct"] for ch in q["choices"]):
                gaps.append("no_marked_correct")
            if gaps:
                missing.append((c["course"], q["number"], gaps))
    print(f"\nQuestions with gaps: {len(missing)}")
    for course, num, gaps in missing[:40]:
        print(f"  {course} Q{num}: {', '.join(gaps)}")
    if len(missing) > 40:
        print(f"  ... and {len(missing) - 40} more")

    out.write_text(json.dumps(courses, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
