# Session handover

**Every new session starts cold. Without a handover, the agent re-reads half the project to
work out where you were, and you pay for that every time.**

This skill makes the end of a session write a short, specific status file and save any lasting
decisions to memory. The start of the next session then reads about 20 lines and gets going.

| Move | When | What it does |
|---|---|---|
| **Handover** | "wrap up", "handover", "done for today" | Overwrites `work/status.md` (20 lines max) and adds lasting decisions to `memory/live.md` |
| **Pickup** | "pick up", "where were we" | Reads status and memory only, tells you where things stand in 3 lines, and asks what to start with |

The skill: [`skill/session-handover/SKILL.md`](skill/session-handover/SKILL.md)

## What a handover produces

From a fictional two-hour session ([what happened](example/session-transcript-summary.md)):

**Before:** the status file nobody updated:
```markdown
- Working on week 4 numbers
- Memo
- Check store 3
```

**After** ([full file](example/status-after.md)):
```markdown
**Now:** Week 4 numbers are final; go/no-go memo is two-thirds drafted.

**Blocked**
- Section 3 needs barista feedback from stores 2 and 5 (ops lead chasing, due Thursday)

**Next**
1. Draft memo section 3 (recommendation) from `data/summary.md`; mark the feedback gaps
```

**Saved to memory** ([full list](example/memory-added.md)), because these matter beyond this
week:
```markdown
- 2026-09-01 · gotcha · Store 3 POS export writes dates as DD/MM; convert before merging or weeks double-count.
- 2026-09-01 · decision · Reward stays at 9 coffees at every store; no per-store thresholds.
```

The 20-minute detour about chart colours became one preference line. The rest of it isn't
worth paying to reload.

## Status vs memory

These are different files on purpose:

| | `work/status.md` | `memory/live.md` |
|---|---|---|
| Holds | Where the work is *right now* | What stays true across weeks |
| Each handover | **Overwritten** | **Appended to** |
| Example | "Section 3 blocked on feedback" | "Store 3 exports dates as DD/MM" |

Mixing them is how memory files bloat: a month of "worked on the memo" lines that were only true
for one afternoon.

## Setup (2 minutes)

**1.** Install the skill: copy `skill/session-handover/` into `~/.claude/skills/` (Claude Code),
or zip it and upload it in the Skills section of the Claude app's settings.

**2.** Add this to your `CLAUDE.md` so pickup happens even when you forget to ask:

```markdown
## Read first
- `work/status.md`: where the last session left off
```

**3.** At the end of a session, say *"wrap up"*. At the start of the next, say *"pick up"*.

Works on its own. Works best with [agent memory](../agent-memory/) for the lasting decisions, and the
[context kit scaffold](../../context-kit/scaffold/), which already has `work/status.md`.

## Tips

- **Hand over before the conversation gets long, not after.** Long sessions get compressed
  automatically, and detail is lost. A handover at a natural break keeps it.
- **"Next" must be startable cold.** If you couldn't hand the line to a colleague without
  explaining it, it's too vague.
- **Read the handover before you close the tab.** It takes ten seconds, and it's the only check
  that the agent understood what happened.
