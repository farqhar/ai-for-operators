---
name: project-brief
description: Write or review a one-page brief for an AI project or automation before anything gets built. Use when the user is about to start an AI project, wants to scope an automation, asks for a project brief or one-pager, or shares a brief and asks if it's ready.
---

# AI project brief

Goal: a one-page brief that someone could build from, and that tells you later whether it
worked. Write it before opening a tool.

## Writing a brief
Interview the user section by section, using `brief-template.md` (bundled next to this file).
Ask one or two questions at a time, not the whole template.

Push for specifics. These are the answers that matter most:
- **The job:** get it into one sentence: "turn ___ into ___ for ___". If it takes two
  sentences, it's two projects.
- **What it costs today:** ask for a number. "How long did it take last week?" Offer to
  estimate it with them if nobody has measured it.
- **Output:** ask for a real example of a good one. A pasted example beats any description.
- **Done looks like:** a number and a date. "Faster" is not done.
- **Owner:** one person, not a team.
- **Allowed in our AI tool?:** if it hasn't been checked, say who to ask. Don't assume.
- **Stop if:** what result after how long would mean dropping it. People resist this one,
  but it's what keeps a dud from running for six months.

"Unknown" is an acceptable answer if it's paired with who will find out. Don't invent
numbers, names or approvals to fill gaps.

Keep it to one page. If a section grows, move the detail to a linked doc.

## Checking a brief
Run `python3 <this skill's folder>/brief-check.py <brief.md>`. It reports blocking gaps
(missing sections, placeholders, no baseline number, no measurable done, no stop rule, data not
cleared) and softer warnings. Then add your own read, which the script can't do:
- Is "the job" one job?
- Is the first version actually small, buildable in days or a couple of weeks, not months?
- Does "must never" cover the scariest realistic failure?
- Does the fallback really work if the AI is switched off tomorrow?

Report blocking items first, then the two or three changes that would most improve it.

## After the brief
- Suggest saving it as `docs/brief.md` in the project folder, where the agent can find it
  (see the context kit scaffold).
- If there are several candidate projects and no brief yet, suggest the prioritisation
  matrix first.
- Put the "done" date and the "stop if" check in the owner's calendar.
