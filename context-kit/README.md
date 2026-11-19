# Context kit: spend fewer credits

**Most AI cost is the stuff the agent reads, not the question you ask.**

Every session, an agent like Claude Code loads your `CLAUDE.md`, then opens whatever
files it thinks it needs. You pay for those tokens every time. A 400-line instruction file, a log
someone left in the project folder, last quarter's export: none of them help, and you pay for them on
every task.

This kit gives you three things:

| Piece | What it does |
|---|---|
| [`skill/context-audit/context-audit.py`](skill/context-audit/context-audit.py) | Measures it. Ranks every file by estimated tokens and tells you what to trim, archive or block. |
| [`scaffold/`](scaffold/) | Prevents it. A project layout with clear live / reference / cold zones and a short `CLAUDE.md`. |
| [`skill/context-audit/SKILL.md`](skill/context-audit/SKILL.md) | Fixes it. A Claude skill that runs the audit, proposes a leaner layout and applies it once you agree. |

## What the difference looks like

The [`example/`](example/) is a fictional cafe loyalty pilot, in two states:

| | [Before](example/audit-before.md) | [After](example/audit-after.md) |
|---|---:|---:|
| Loaded every session | 3,224 tokens | 174 tokens |
| Reachable by the agent | 29,384 tokens | 3,067 tokens |

Nothing was deleted. The meeting notes moved from `CLAUDE.md` into `docs/`, the log and the old
draft went to `archive/`, the raw export sits behind a 10-line summary, and two deny rules keep
the agent out of the cold folders.

## Quickstart (2 minutes)

**1. Measure your project.** You need Python 3, which is already on macOS.

```bash
python3 skill/context-audit/context-audit.py ~/path/to/your/project
```

You'll get three totals, the largest files and a list of suggestions. Add `--md` for a markdown
report you can paste into a doc.

**2. Fix the biggest item.** Usually it's one of these:
- `CLAUDE.md` is long. Keep the rules and pointers and move everything else into `docs/`.
- A log, export or `node_modules/` is reachable. Add a deny rule (see below).
- A big data file has no summary. Write a short `data/summary.md` and block the raw folder.

**3. Re-run** and check the numbers moved.

**Starting a new project?** Copy `scaffold/` and fill in the brackets.

## The one setting that matters

Claude Code won't open files that match a `Read` deny rule in `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": ["Read(./archive/**)", "Read(./data/raw/**)"]
  }
}
```

This is the real lever, more than any instruction in `CLAUDE.md`. "Please don't read
archive/" is a request the agent can forget, while a deny rule is enforced. The audit
script reads these rules, so blocked files show up as blocked.

## Using the skill

Copy the `skill/context-audit/` folder into `~/.claude/skills/` (Claude Code), or zip it and
upload it in the Skills section of the Claude app's settings. Then ask:
*"Audit this project's context and suggest a leaner layout."* It measures, proposes a plan with
estimated savings, and only moves files once you approve. It never deletes.

## Fine print

- Token counts are estimates (about 4 characters per token). They're good for finding what's
  big, not for exact billing.
- Binary files (images, PDFs, zips) are skipped. Agents mostly don't read them unless asked.
- Options: `--top 30` lists more files, and `--big 3000` lowers the "big file" threshold.
