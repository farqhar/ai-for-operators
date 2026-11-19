#!/usr/bin/env python3
"""
memory-rollover: keep an agent's memory file small enough to read every session.

An agent that runs for weeks writes notes to memory/live.md. By day 40 that
file is huge, every session pays to reload it, and the important lines are
buried. This script moves the OLDEST log entries into monthly archive files
once live.md passes a size cap. Nothing is deleted, and the Pinned section
never moves.

    python3 memory-rollover.py                     # check memory/live.md, change nothing
    python3 memory-rollover.py path/to/memory      # check another memory folder
    python3 memory-rollover.py --apply             # do the rollover
    python3 memory-rollover.py --cap 1500          # use a different cap (tokens)

Expected live.md layout (see template/memory/live.md):

    ## Pinned
    - facts that must always be loaded (never rolled over)

    ## Log
    - 2026-08-03 · decision · Reward threshold set at 9 coffees.
    - 2026-08-04 · gotcha · Store 3 POS exports dates as DD/MM.
      Continuation lines are indented and stay with their entry.

No installs needed. Python 3.8+. Token counts are estimates (~4 chars/token).
"""

import argparse
import re
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4
ENTRY_RE = re.compile(r"^- (\d{4})-(\d{2})-(\d{2})\b")
LOG_HEADING = "## log"


def tokens(text):
    return round(len(text) / CHARS_PER_TOKEN)


def parse(text):
    """Split live.md into (before_log, entries, after_log).

    before_log: everything up to and including the '## Log' heading line.
    entries:    list of (date 'YYYY-MM-DD', text block) in file order.
    after_log:  any later '## ' section, kept as is.
    """
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == LOG_HEADING)
    except StopIteration:
        sys.exit("No '## Log' heading found in live.md. See the template for the layout.")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))

    before, body, after = lines[: start + 1], lines[start + 1 : end], lines[end:]
    entries, loose = [], []
    for line in body:
        m = ENTRY_RE.match(line)
        if m:
            entries.append(["-".join(m.groups()), line])
        elif entries and line.strip() and line[:1] in (" ", "\t"):
            entries[-1][1] += line  # continuation of the previous entry
        else:
            loose.append(line)  # blank lines, comments, undated notes stay put
    return "".join(before), [tuple(e) for e in entries], "".join(loose), "".join(after)


def plan(entries, frame_tokens, cap, target):
    """Pick the oldest entries to move until live.md is under target tokens."""
    total = frame_tokens + sum(tokens(t) for _, t in entries)
    if total <= cap:
        return [], total, total
    order = sorted(range(len(entries)), key=lambda i: entries[i][0])  # oldest first, stable
    move, remaining = set(), total
    for i in order:
        if remaining <= target:
            break
        move.add(i)
        remaining -= tokens(entries[i][1])
    return sorted(move), total, remaining


def write_index(archive_dir):
    rows = []
    for f in sorted(archive_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9].md")):
        dates = [ENTRY_RE.match(l) for l in f.read_text(encoding="utf-8").splitlines()]
        dates = ["-".join(m.groups()) for m in dates if m]
        if dates:
            rows.append(f"| [{f.stem}]({f.name}) | {len(dates)} | {min(dates)} to {max(dates)} |")
    (archive_dir / "INDEX.md").write_text(
        "# Memory archive\n\nOlder log entries, moved out of `live.md` by memory-rollover. "
        "Search these when you need history:\n`grep -ri \"keyword\" memory/archive/`\n\n"
        "| Month | Entries | Dates |\n|---|---:|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Roll old memory entries into monthly archives.")
    ap.add_argument("memory_dir", nargs="?", default="memory", help="folder holding live.md")
    ap.add_argument("--cap", type=int, default=2000,
                    help="roll over when live.md is above this many tokens (default 2000)")
    ap.add_argument("--target", type=float, default=0.6,
                    help="after rolling over, aim for this fraction of the cap (default 0.6)")
    ap.add_argument("--apply", action="store_true", help="actually move entries")
    args = ap.parse_args()

    mem = Path(args.memory_dir)
    live = mem / "live.md"
    if not live.is_file():
        sys.exit(f"Not found: {live}")
    text = live.read_text(encoding="utf-8")
    before, entries, loose, after = parse(text)
    frame = tokens(before + loose + after)
    move, total, remaining = plan(entries, frame, args.cap, args.cap * args.target)

    print(f"{live}: ~{total:,} tokens, {len(entries)} log entries (cap {args.cap:,}).")
    if not move:
        print("Under the cap. Nothing to roll over.")
        return

    by_month = {}
    for i in move:
        by_month.setdefault(entries[i][0][:7], []).append(entries[i])
    print(f"Would move {len(move)} oldest entries (~{total - remaining:,} tokens), "
          f"leaving ~{remaining:,}:")
    for month in sorted(by_month):
        print(f"  {len(by_month[month]):>4} entries -> archive/{month}.md")
    if frame > args.cap * args.target:
        print(f"\nNote: the Pinned section and headings alone are ~{frame:,} tokens. "
              f"Trim Pinned too, or the file will keep growing past the cap.")
    if not args.apply:
        print("\nDry run. Nothing changed. Re-run with --apply to do it.")
        return

    archive = mem / "archive"
    archive.mkdir(exist_ok=True)
    # Archive first, then rewrite live.md: if anything fails midway, entries exist twice, never zero.
    for month, items in sorted(by_month.items()):
        f = archive / f"{month}.md"
        existing = f.read_text(encoding="utf-8") if f.exists() else f"# Memory archive: {month}\n\n"
        f.write_text(existing + "".join(t if t.endswith("\n") else t + "\n" for _, t in items),
                     encoding="utf-8")
    keep = "".join(t for i, (_, t) in enumerate(entries) if i not in set(move))
    live.write_text(before + loose + keep + after, encoding="utf-8")
    write_index(archive)
    print(f"\nDone. live.md is now ~{tokens(live.read_text(encoding='utf-8')):,} tokens. "
          f"See {archive / 'INDEX.md'}.")


if __name__ == "__main__":
    main()
