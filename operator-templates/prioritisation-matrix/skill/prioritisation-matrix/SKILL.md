---
name: prioritisation-matrix
description: Help decide which AI project or automation to do first, using gates and a weighted scoring matrix with a robustness check. Use when the user has several AI ideas or automation candidates and asks which to start with, wants to prioritise or rank them, or needs to justify a choice to their team.
---

# AI project prioritisation

Goal: one project to start with, and an honest picture of how sure we can be.
The matrix supports the decision. It doesn't make the decision.

## 1. Collect candidates
Ask for the list of ideas (or gather them from what the user shares). Aim for 3–8. For each,
get a one-line description and who would own it. If there's only one idea, say a matrix
isn't needed and help them test that idea instead.

## 2. Gates first
For each project ask the three gates. A "no" parks the project however well it would score.
1. Are we allowed to put this data into an AI tool under our policies and contracts?
2. If it fails completely, can the work still get done the old way?
3. Is a named person accountable for what it produces?
If a gate is unknown, mark it `no` for now and list what needs checking.

## 3. Score each passing project, 1–5 per criterion
Use the anchors in `criteria.csv` (bundled next to this file; prefer the user's own copy
if they have one). Every criterion is phrased so 5 is good.
- **Ask for evidence, don't accept vibes.** "How many hours a week does this take now?" beats
  "is it valuable?". Put the evidence in the notes column.
- **Record confidence** per project: `high` (measured), `medium` (informed estimate),
  `low` (guess).
- Watch for the common trap: high value but poor AI fit (e.g. rosters with rules that live in
  people's heads). Score AI fit honestly, because that's where projects die.
- Score one criterion across all projects at a time, not one project at a time. It keeps the
  scale consistent.

## 4. Run it
Write the scores to `projects.csv` (columns: `project, owner, gates_passed, confidence,`
then one column per criterion key, then `notes`) and run:
`python3 <this skill's folder>/prioritise.py <criteria.csv> projects.csv --md`

## 5. Explain the result
- Lead with the recommendation: start with #1, and why, in two sentences.
- Say how solid it is, using the script's robustness section. If a small weight change flips
  first place, say exactly which value judgement decides it and ask the user which they
  believe. Don't decide it for them.
- Flag low-confidence scores on the top two and say what would firm them up.
- Name the top project's weakest criterion and suggest a first step that tests it.
- Suggest starting **one** project, not three.

## Rules
- Weights are the user's values. Never change them silently. If the user disagrees with a
  weight, change it in their criteria file, re-run, and show what moved.
- Don't fiddle scores to get a preferred answer. If the user wants a different winner, ask
  what the matrix is missing and add it as a note or a criterion, openly.
- Parked projects aren't rejected. List what would unpark each one.
