#!/usr/bin/env python3
"""
brief-check: is this AI project brief ready to build from?

    python3 brief-check.py brief.md

Checks a brief written from brief-template.md for the gaps that sink AI projects:
missing sections, unfilled [placeholders], no baseline number, no measurable
"done", no stop rule, nobody checking the output. Prints what's missing and a
verdict. Read-only: it never edits the brief.

No installs needed. Python 3.8+.
"""

import re
import sys
from pathlib import Path

SECTIONS = ["The job", "What it costs today", "People", "Inputs", "Output",
            "Done looks like", "Must never", "When it goes wrong", "First version", "Cost"]
NUMBER = re.compile(r"\d")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}|\b\d{1,2} (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|"
                  r"\b(week|weeks|month|months|day|days)\b", re.I)
PLACEHOLDER = re.compile(r"\[[^\]]{2,}\](?!\()")  # [text], even over several lines, but not a [link](url)
UNKNOWN = re.compile(r"\b(unknown|tbc|tbd)\b|\?\?", re.I)


def split_sections(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    parts, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            current = m.group(1).strip()
            parts[current] = ""
        elif current:
            parts[current] += line + "\n"
    return text, parts


def field(body, label):
    m = re.search(rf"\*\*{re.escape(label)}[^*]*\*\*:?\s*(.*)", body)
    return m.group(1).strip() if m else ""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 brief-check.py brief.md")
    path = Path(sys.argv[1])
    text, parts = split_sections(path.read_text(encoding="utf-8"))
    blockers, warnings, good = [], [], []

    missing = [s for s in SECTIONS if s not in parts or not parts[s].strip()]
    for s in missing:
        blockers.append(f"Section missing or empty: '{s}'.")

    for s, body in parts.items():
        holes = PLACEHOLDER.findall(body)
        if holes:
            eg = " ".join(holes[0].split())
            eg = eg if len(eg) <= 60 else eg[:57] + "...]"
            blockers.append(f"'{s}' still has {len(holes)} unfilled placeholder(s), e.g. {eg}")
        elif UNKNOWN.search(body):
            warnings.append(f"'{s}' has an unknown. Fine for a draft, but note who finds out, and by when.")
    title_holes = PLACEHOLDER.findall(text.split("\n## ", 1)[0])
    if title_holes:
        blockers.append(f"Title or owner line still has placeholders: {', '.join(title_holes)}")

    def check(section, test, ok, problem, level=blockers):
        body = parts.get(section, "")
        if not body.strip() or PLACEHOLDER.search(body):
            return
        (good if test(body) else level).append(ok if test(body) else problem)

    check("What it costs today", lambda b: NUMBER.search(b),
          "Baseline has a number to compare against.",
          "'What it costs today' has no number. Without a baseline you can't show it worked.")
    check("Done looks like", lambda b: NUMBER.search(b) and DATE.search(b),
          "'Done looks like' has a number and a timeframe.",
          "'Done looks like' needs a number AND a date or timeframe, or nobody can say it's done.")
    check("First version", lambda b: len(field(b, "Stop if")) > 3,
          "There's a stop rule.",
          "'First version' has no 'Stop if'. Decide now what would make you drop it.")
    check("People", lambda b: len(field(b, "Owner")) > 1,
          "An owner is listed.", "No owner listed in 'People'.")
    check("People", lambda b: not re.search(r"\bteam\b|everyone|all of us", field(b, "Owner"), re.I),
          "The owner is a person.",
          "The owner is a team. Name one person; a team can't be held accountable.", warnings)
    check("People", lambda b: len(field(b, "Checks it")) > 1,
          "Someone checks the output.",
          "Nobody named to check the output. Say who, or say why it's safe without.", warnings)
    check("Inputs", lambda b: not re.search(r"not yet checked|no\b", field(b, "Allowed"), re.I),
          "Data is cleared for the AI tool.",
          "Inputs aren't confirmed as allowed in the AI tool. Check before building.")
    check("Must never", lambda b: re.search(r"^\s*-\s+\S", b, re.M),
          "Boundaries are written down.", "'Must never' is empty.")

    words = len(re.findall(r"\w+", text))
    if words > 700:
        warnings.append(f"About {words} words. A brief longer than a page usually hides the "
                        f"decision. Move detail to linked docs.")

    print(f"Brief check: {path.name}\n")
    for label, items, mark in (("Blocking", blockers, "x"), ("Worth fixing", warnings, "!"),
                               ("In place", good, "+")):
        if items:
            print(f"{label}:")
            for i in items:
                print(f"  {mark} {i}")
            print()
    if blockers:
        print(f"Verdict: NOT READY. Fix the {len(blockers)} blocking item(s) first.")
        sys.exit(1)
    print("Verdict: READY TO BUILD." + (" Tidy the warnings when you can." if warnings else ""))


if __name__ == "__main__":
    main()
