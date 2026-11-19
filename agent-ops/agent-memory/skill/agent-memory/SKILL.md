---
name: agent-memory
description: Keep a long-running agent's memory useful and small. Use when setting up memory for an agent or project, when asked to remember something for future sessions, when memory/live.md is getting long, or when asked to recall a past decision.
---

# Agent memory

Memory lives in `memory/` at the project root:
- `memory/live.md`: loaded every session. **Pinned** (always true) + **Log** (dated entries).
- `memory/archive/YYYY-MM.md`: older log entries, read only when needed.
- `memory/archive/INDEX.md`: which months exist and what dates they cover.

## Setting up
If `memory/live.md` doesn't exist, create it from the template layout: `# Memory`, a
`## Pinned` section with 2–3 lines about who the agent serves and what it must never do, and
an empty `## Log`. Suggest adding to CLAUDE.md under "Read first": `memory/live.md`.

## Writing to memory
Add one line to the end of `## Log`:

`- YYYY-MM-DD · type · what a future session needs to know`

Types: `decision`, `preference`, `gotcha`, `fact`, `supersedes`.

- **Write conclusions, not activity.** "Store 3 exports dates as DD/MM" is memory.
  "Looked at the store 3 export" is not.
- **Check before writing.** If it's already in Pinned or Log, don't add it again.
- **Never edit old entries.** When something changes, add
  `- 2026-09-02 · supersedes 2026-08-14 · Threshold now 10 coffees, not 9.`
  The history stays honest and the newest line wins.
- **Promote what lasts.** A preference or rule that will matter for months belongs in
  Pinned, because Log entries eventually roll into the archive. Ask before promoting, and
  keep Pinned to ~10 lines.
- Only write what the user would be comfortable seeing. Never store secrets, passwords or
  personal details about third parties.

## Keeping it small
After writing, if `live.md` looks long (roughly 150+ lines), run:
`python3 <this skill's folder>/memory-rollover.py memory`
Show the user the dry-run summary. Run with `--apply` only after they agree. It moves the
oldest Log entries into `archive/YYYY-MM.md` and never deletes anything. Pinned never moves.

## Recalling
1. Check `live.md` first.
2. If the answer isn't there, read `archive/INDEX.md`, then search the archive:
   `grep -ri "keyword" memory/archive/`. Read only the matching lines, not whole months.
3. If an entry has a later `supersedes` line, the later line is the current truth.
4. Say where the answer came from ("from the 2026-08-14 log entry").
