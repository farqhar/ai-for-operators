# Agent memory that survives day 40

**On day 1, an agent's memory file is helpful. By day 40 it's a 4,000-token wall that's reloaded
every session, and the line that matters is buried in the middle.**

This pattern keeps memory in two parts: a small **live** file the agent reads every session, and
**monthly archives** it searches only when it needs history. A script rolls old entries from
one to the other at a size cap, so the live file stays the same size no matter how long the agent
runs.

```
memory/
├── live.md              # read every session: Pinned + recent Log
└── archive/
    ├── INDEX.md         # which months exist, which dates they cover
    ├── 2026-08.md       # older log entries, searched on demand
    └── 2026-09.md
```

| Piece | What it does |
|---|---|
| [`template/memory/live.md`](template/memory/live.md) | Starting file with the Pinned / Log layout. |
| [`skill/agent-memory/SKILL.md`](skill/agent-memory/SKILL.md) | Claude skill: how to write entries, when to roll over, how to recall. |
| [`skill/agent-memory/memory-rollover.py`](skill/agent-memory/memory-rollover.py) | Moves the oldest Log entries to monthly archives once `live.md` passes a cap. Dry run by default. |
| [`example/`](example/) | A fictional agent's memory on day 40, before and after rollover. |

## What the difference looks like

The example is 40 days of a reporting agent's memory: 120 log entries.

| | Before | After rollover |
|---|---:|---:|
| `live.md`, loaded every session | ~3,658 tokens | ~1,179 tokens |
| Entries in view | 120 | 39 (the most recent) |
| Entries lost | | 0. 81 moved to `archive/2026-08.md` |

Without rollover that file keeps growing: by day 120 it would cost about three times as much to
load, for every session, for the rest of the project.

## The rules that make it work

**Pinned vs Log.** Pinned holds the few things that must always be true ("never email customers
directly"). The Log holds dated entries. Only the Log rolls over, so anything that will matter in
three months belongs in Pinned.

**One line per entry, written as a conclusion.** `- 2026-08-04 · gotcha · Store 3 exports dates as
DD/MM` is memory. "Reviewed the store 3 export" is a diary, and diaries are what make memory
files bloat.

**Never edit, supersede.** When a decision changes, add a new line:
`- 2026-09-02 · supersedes 2026-08-14 · Threshold now 10 coffees.`
You can see what changed and when, and the newest line wins.

**Read first, search second.** The agent reads `live.md` every session. It goes to the archive
only when it needs history, and then searches it (`grep`) instead of reading whole months.

## Setup (5 minutes)

**1.** Copy `template/memory/` into your project root.

**2.** Fill in Pinned: who the agent serves, what it's for, and what it must never do.

**3.** Add this to your `CLAUDE.md`:

```markdown
## Read first
- `memory/live.md`: what earlier sessions learned. Check it before asking me something
  you may already know.

## Memory
- Search `memory/archive/` only when you need history (`grep -ri "keyword" memory/archive/`).
```

**4.** Install the skill: copy `skill/agent-memory/` into `~/.claude/skills/` (Claude Code), or
zip it and upload it in the Skills section of the Claude app's settings.

**5.** Check the size now and then (or let the skill do it):

```bash
python3 ~/.claude/skills/agent-memory/memory-rollover.py memory
```

```bash
python3 ~/.claude/skills/agent-memory/memory-rollover.py memory --apply
```

Options: `--cap 1500` sets a different size limit in tokens (default 2,000), and `--target 0.5`
sets how far below the cap to trim back to (default 0.6 of the cap).

## Safety

- Nothing is deleted. Entries are written to the archive *before* they're removed from `live.md`,
  so if something goes wrong midway, an entry can end up in both places but never in neither.
- Pinned, headings and undated notes never move.
- Archive files are plain markdown. To bring an entry back, cut and paste it.

## Works with

- **[Session handover](../session-handover/)** writes decisions into this memory at the end of
  each session.
- **[Context kit](../../context-kit/)** can measure what `live.md` costs you:
  `python3 context-audit.py .`
