# AI project brief

**The brief you write before you open a tool.**

Most AI projects that fizzle don't fail on the technology. They fail because nobody wrote down
what "done" meant, what it cost before, or what would make you stop. Six weeks in, the tool
technically works, nobody can say whether it helped, and it quietly stops being used.

This is a one-page template that forces those answers early, plus a checker that tells you
whether a brief is ready to build from.

| Piece | What it does |
|---|---|
| [`brief-template.md`](brief-template.md) | The one-page template. Ten short sections. |
| [`skill/project-brief/brief-check.py`](skill/project-brief/brief-check.py) | Checks a brief for the gaps that sink projects and gives a verdict. |
| [`skill/project-brief/SKILL.md`](skill/project-brief/SKILL.md) | Claude skill: interviews you to write the brief, or reviews one you've written. |
| [`example/`](example/) | A ready brief and a vague one, with what the checker says about each. |

## The sections, and why each one is there

| Section | The question | Why it matters |
|---|---|---|
| **The job** | Turn ___ into ___ for ___? | If it takes two sentences, it's two projects. |
| **What it costs today** | How many hours, errors or dollars, now? | Without a baseline you can never show it worked. |
| **People** | Who owns it, uses it, checks it? | A team can't be accountable. One named person can. |
| **Inputs** | Where does the data come from, and are we allowed to use it? | The most common late surprise is data you weren't cleared to use. |
| **Output** | What does a good one look like? | Paste a real example. It beats any description. |
| **Done looks like** | What number, by when? | "Faster and better" never finishes. |
| **Must never** | What's off limits? | Write the boundary before the first mistake, not after. |
| **When it goes wrong** | Likely mistake, how you'd notice, fallback? | AI makes mistakes. Plan the catch, not the perfection. |
| **First version** | What's in, what waits, when do you stop? | The stop rule is what keeps a dud from running for six months. |
| **Cost** | Build, run, and ongoing care? | Ongoing care is the cost everyone forgets. |

## What the checker catches

The [vague brief](example/brief-vague.md) is the kind most projects actually start with: "use
AI to make the weekly reports faster and better".

```
$ python3 brief-check.py brief-vague.md

Blocking:
  x Section missing or empty: 'Must never'.
  x 'What it costs today' has no number. Without a baseline you can't show it worked.
  x 'Done looks like' needs a number AND a date or timeframe, or nobody can say it's done.
  x 'First version' has no 'Stop if'. Decide now what would make you drop it.
  x Inputs aren't confirmed as allowed in the AI tool. Check before building.

Worth fixing:
  ! The owner is a team. Name one person; a team can't be held accountable.
  ! Nobody named to check the output. Say who, or say why it's safe without.

Verdict: NOT READY. Fix the 5 blocking item(s) first.
```

The [ready brief](example/brief-weekly-report.md) is the same project done properly:
"3 hours every Monday" becomes "under 30 minutes, no wrong totals, 4 weeks running by
31 October", with a stop rule of "still over 90 minutes after 3 weeks". It passes.

The checker reads structure, not judgement. It can't tell you the first version is too big or the
fallback wouldn't really work. The skill adds that read.

## Quickstart

**1.** Copy `brief-template.md` and fill it in. Twenty minutes is plenty; if it takes longer,
the project isn't clear yet, and that's useful to know.

**2.** Check it:

```bash
python3 skill/project-brief/brief-check.py my-brief.md
```

**3.** Save it as `docs/brief.md` in the project folder, so the agent can read it (see the
[context kit scaffold](../../context-kit/scaffold/)).

**Or use the skill:** copy `skill/project-brief/` into `~/.claude/skills/` (Claude Code), or zip
it and upload it in the Skills section of the Claude app's settings, then say *"help me write a
brief for…"*. It asks one or two questions at a time and pushes for numbers.

## Where it fits

1. **[Prioritisation matrix](../prioritisation-matrix/):** decide which project goes first.
2. **This brief:** pin down what that project is, and what done means.
3. **[Which model for which job](../model-choice/):** fill in the Cost section.
4. **[Context kit](../../context-kit/):** set up the project folder so the agent reads only what it needs.
5. **[Session handover](../../agent-ops/session-handover/)** and
   **[agent memory](../../agent-ops/agent-memory/):** keep it on track while it runs.

The example follows the winner of the prioritisation matrix example (weekly store report
drafts) through to its brief.
