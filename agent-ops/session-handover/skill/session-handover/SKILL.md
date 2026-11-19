---
name: session-handover
description: End a work session cleanly so the next one starts fast, or pick up where the last one left off. Use when the user says wrap up, handover, end of session, save progress, we're done for today, or when context is getting long; and at the start of a session when the user says pick up, continue, where were we, or what's next.
---

# Session handover

Two moves: **handover** at the end of a session, **pickup** at the start of the next.
The goal is that the next session reads ~20 lines instead of re-reading the project.

## Handover (end of session)

1. **Work out what changed this session.** From the conversation and the files you touched:
   what got done, what was decided, what's blocked, what's next.

2. **Overwrite `work/status.md`** (create `work/` if needed). Replace the file, don't append.
   Hard limit: 20 lines, blank lines included.

   ```markdown
   # Status: YYYY-MM-DD

   **Now:** [the state of the work in one sentence]

   **Done this session**
   - [outcome, not activity: "Draft memo v2 in docs/memo.md", not "worked on memo"]

   **Blocked**
   - [what, and who or what it's waiting on] (or "Nothing")

   **Next**
   1. [the very next action, specific enough to start without asking]
   2. [then this]

   **Start by reading:** [1–3 files the next session needs, with paths]
   ```

3. **Save what lasts to memory.** Decisions, preferences and gotchas that will matter in
   future sessions go into `memory/live.md` as Log lines
   (`- YYYY-MM-DD · decision · ...`). Status is temporary; memory is permanent. If there's no
   `memory/live.md`, list them under a **Decisions** heading in `status.md` instead and suggest
   setting up agent memory.
   Don't save: what you did step by step, things already in memory, secrets, or anything
   the user wouldn't want written down.

4. **Show the user** the new status (it's short) and the memory lines you added, and ask
   if anything's wrong or missing. Fix it before they go.

5. If you changed files that aren't saved anywhere else (no git, no sync), say so plainly.

## Pickup (start of session)

1. Read, in order: `CLAUDE.md` (if not already loaded), `work/status.md`, `memory/live.md`.
   Don't read anything else yet.
2. Tell the user in 3 lines or fewer: where things stand, what's blocked, the next action.
3. Ask: "Start with [next action], or something else?" Then read only the files that
   task needs.

If `work/status.md` is missing or older than the files around it, say so, and offer to rebuild
it from recent changes instead of guessing.

## Rules
- Status is overwritten every handover. If the user wants history, copy the old one to
  `archive/status-YYYY-MM-DD.md` first. Never delete it without asking.
- Be specific. "Next: finish the memo" is useless. "Next: write the cost section of
  docs/memo.md using data/summary.md" can be started cold.
- Never mark something done that wasn't verified. "Draft written, not yet checked" is fine.
