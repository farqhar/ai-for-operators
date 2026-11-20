# ai-for-operators
for everyday people

**The bits nobody demos: briefs, handovers, and agents that survive day 40.**

## What it is
A growing kit of generic, reusable pieces: Claude skills (`SKILL.md`), fill-in templates (markdown/CSV) and patterns for agents that run for weeks. Each lives in its own folder with a README, the files, and a fictional worked example.

## Who it's for
Project leads, ops people, designers, analysts — anyone setting up AI for a team without being the engineer on it. If you can edit a markdown file, you can use everything here.

## Why it exists
Most AI material is either a demo or a framework. The hard part sits in between: writing the brief, picking the one task worth automating, keeping an agent sane on day 40. These are the pieces that solved those problems for real, stripped of anything company-specific.

## Quickstart
1. Browse the category folders below and pick one item.
2. Read its README — 2 minutes.
3. **Claude skill:** copy the folder into your skills directory (or upload the `SKILL.md` in Claude settings). **Template:** copy the markdown/CSV and fill it in.
4. Try it against the `example/` data first so you know what good output looks like.

## Structure
```
ai-for-operators/
├── context-kit/          # spend fewer credits: audit, lean project layout, skill
├── file-organisation/    # keep files findable by people and agents
├── agent-ops/            # patterns for long-running agents
├── operator-templates/   # briefs, prioritisation, stage-gates
└── adoption/             # how non-technical teams take AI up
```

## Available now

**[Context kit](context-kit/)**: most AI cost is what the agent reads, not what you ask. One
command shows where your tokens go:

```
$ python3 context-audit.py my-project

  Loaded every session         3,224 tokens
  Reachable by the agent      29,384 tokens
  Blocked by deny rules            0 tokens

Suggestions:
  - CLAUDE.md is loaded every session and is ~3,224 tokens. Aim for under 1,500...
  - pos-sync.log looks like a data dump (~14,784 tokens). Keep a short sample...
```

Includes a project scaffold and a Claude skill that applies the fixes. In the worked example,
the every-session load drops from 3,224 to 174 tokens and nothing is deleted.

**[Downloads organiser](file-organisation/downloads-organiser/)**: sorts a messy Downloads
folder by filename rules. Dry run by default, never deletes, and one command undoes a run.

**[Agent memory that survives day 40](agent-ops/agent-memory/)**: a small live memory file
plus monthly archives, with a script that rolls old entries over at a size cap. In the example, 40 days
of memory goes from ~3,658 to ~1,179 tokens per session with nothing lost.

**[Session handover](agent-ops/session-handover/)**: a skill that ends each session with a short,
specific status file and saves lasting decisions to memory, so the next session starts by reading
about 20 lines instead of the whole project.

**[Which model for which job](operator-templates/model-choice/)**: a one-page guide to matching
tasks to model tiers (the small tier costs a twentieth of the mid tier and a fortieth of the large), plus a 20-minute
test to check whether a cheaper model is good enough for your work.

**[Prioritisation matrix](operator-templates/prioritisation-matrix/)**: decide which AI project
goes first. Gates knock out dealbreakers, anchored 1–5 scores keep people consistent, and a robustness check
tells you whether the winner survives different weights. Spreadsheet, script and skill.

**[Project brief](operator-templates/project-brief/)**: the one-page brief you write before you
open a tool, covering the baseline, a measurable "done", boundaries and a stop rule. Includes a checker that flags
the gaps that sink AI projects, and a skill that interviews you to fill it in.

## Where to start

Starting an AI project from scratch? The items fit together in this order:

1. **[Prioritisation matrix](operator-templates/prioritisation-matrix/):** pick the project
2. **[Project brief](operator-templates/project-brief/):** pin down what done means
3. **[Which model for which job](operator-templates/model-choice/):** pick the cheapest model that does the job
4. **[Context kit](context-kit/):** set up the folder so the agent reads only what it needs
5. **[Session handover](agent-ops/session-handover/)** and **[agent memory](agent-ops/agent-memory/):** keep it on track for weeks

Each item also works on its own. New items land as they're ready; watch the repo to catch them.

## Demo
![The context audit run on a messy project, then on the same project reorganised: tokens loaded every session drop from 3,224 to 174](context-kit/demo.gif)

## Licence
Code is MIT. Documentation, skills and templates are CC BY 4.0 — use and adapt freely, with credit.
