---
name: context-audit
description: Audit a project folder for token waste and propose a leaner layout. Use when the user asks why sessions are expensive, wants to cut credit or token usage, asks to tidy or slim down a project for Claude, or says CLAUDE.md is getting long.
---

# Context audit

Goal: cut what the agent loads and reads each session, without losing anything.

## Steps

1. **Measure.** Run the bundled script on the project root:
   `python3 <this skill's folder>/context-audit.py <project> --md`
   Show the user the three totals and the top files. Say plainly that token
   counts are estimates (about 4 characters per token).

2. **Diagnose.** Group what you found into:
   - **Every-session cost:** CLAUDE.md / AGENTS.md over ~1,500 tokens.
   - **Reachable bulk:** logs, exports, dependency folders, old drafts the agent could open.
   - **Missing summaries:** big data files with no short summary next to them.

3. **Propose, don't act.** Write a short plan as a table: file, what to do
   (trim / move to `docs/` / move to `archive/` / summarise / block), and
   estimated tokens saved. Lead with the single biggest saving.
   Layout to aim for:
   - `CLAUDE.md`: under ~60 lines; "read first", "read when needed", "never read", rules
   - `work/`: live files, kept short
   - `docs/`: stable reference, pointed to from CLAUDE.md
   - `data/summary.md` in front of `data/raw/`
   - `archive/`: cold storage
   - `.claude/settings.json` deny rules, e.g. `"Read(./archive/**)"`, `"Read(./data/raw/**)"`

4. **Apply only after the user says yes.** Move files, never delete them.
   When trimming CLAUDE.md, move the removed text into a `docs/` file rather than
   discarding it. Merge into an existing `.claude/settings.json`; never overwrite it.

5. **Re-measure.** Run the script again and report before → after for each total.

## Watch for
- Deny rules block the agent from *reading* a file; they don't hide it from the user.
  If the agent genuinely needs something in `archive/`, move it back out rather than
  weakening the rule.
- A summary is only useful if it's right. When you write `data/summary.md`,
  say which numbers you calculated and ask the user to check them.
- Don't move files that build tools or scripts depend on by path without checking
  for references first.
