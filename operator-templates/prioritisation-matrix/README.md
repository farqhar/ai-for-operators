# Weighted prioritisation matrix

**Every team has more AI ideas than time. The loudest idea usually goes first, and it's
often the one with the worst fit.**

This is a scoring matrix for deciding which AI project to start with. It does three things a
gut call doesn't:

1. **Gates before scores.** Three yes/no questions knock out dealbreakers *before* anything is
   scored, because no amount of value makes up for "we're not allowed to put this data in an AI tool".
2. **Scores with anchors.** Each criterion has written descriptions of what a 1, 3 and 5 look
   like, so "4 for value" means the same thing from different people.
3. **A robustness check.** It tells you whether the winner would still win if your weights were a
   bit different, and if not, exactly which value judgement decides it.

| Piece | Use it for |
|---|---|
| [`prioritisation-matrix.xlsx`](prioritisation-matrix.xlsx) | The spreadsheet: works in Excel, Google Sheets and Numbers. Live formulas, dropdowns, scoring guide on hover. |
| [`criteria.csv`](criteria.csv) + [`projects.csv`](projects.csv) | The same matrix as plain files, for the script and the skill. |
| [`skill/prioritisation-matrix/`](skill/prioritisation-matrix/) | A Claude skill that interviews you, scores with evidence, runs the check and explains the result. |
| [`example/`](example/) | Six fictional projects for a cafe group, scored and ranked. |

## The criteria

All phrased so **5 is good**. The weights add up to 100, and the score runs from 20 to 100.

| Criterion | Weight | Scores 5 when… |
|---|---:|---|
| Value | 25 | It saves a day or more a week, or directly affects revenue |
| Frequency | 15 | The task happens daily or many times a day |
| AI fit | 15 | Text-heavy, pattern-based, producing a draft a person reviews |
| Low risk if wrong | 15 | Mistakes are cheap and obvious |
| Data ready | 10 | The inputs are digital and reachable today |
| Easy to build | 10 | It works with a prompt or skill this week |
| Committed owner | 10 | A named owner with time is asking for it |

The full 1/3/5 descriptions are in [`criteria.csv`](criteria.csv) and on the spreadsheet's
Criteria tab. **The weights are a starting point, not the truth.** A team that can't afford a
mistake should weight risk higher, and a team proving AI's worth should weight value and
frequency higher. Change them before you score, not after you see the result.

## The gates

A "no" to any of these parks the project, however well it would score:

1. Are we allowed to put this data into an AI tool under our policies and contracts?
2. If it fails completely, can the work still get done the old way?
3. Is a named person accountable for what it produces?

## What the example shows

| Rank | Project | Score |
|---:|---|---:|
| 1 | Weekly store report drafts | 86 |
| 2 | Supplier invoice data entry | 76 |
| 3 | Review reply drafts | 72 |
| 4 | Staff roster generation | 64 |
| 5 | Barista training Q&A bot | 62 |
| – | Auto-approve refund requests | parked |

Three lessons are built into it:
- **The refund project would have come second** (79), with top marks for value and frequency.
  It's parked because nobody is accountable when it gets a refund wrong. That's what the gates are for.
- **Rosters have the most value and still come fourth.** The rules live in managers' heads (AI fit 2)
  and a wrong roster hurts people (risk 2). High value with poor fit is the classic first-project trap.
- **The winner is boring.** A report the ops lead rewrites every Monday: clean data, low risk, works
  this week. Good first projects usually look like this, because they build trust for the
  ambitious ones.

The script also confirms the lead is robust: the report drafts stay first even if any single
weight moves 10 points either way ([full output](example/ranking.md)).

## Quickstart

**Spreadsheet (most people):** open `prioritisation-matrix.xlsx` (or upload it to Google
Sheets). Check the weights on the Criteria tab, answer the Gates, then fill in the Matrix tab.
Hover any criterion header to see what 1, 3 and 5 mean. Look at the Example tab first.

**Script (for the robustness check):** fill in `projects.csv`, then:

```bash
python3 skill/prioritisation-matrix/prioritise.py criteria.csv projects.csv
```

Add `--md` for a markdown report.

**Skill:** copy `skill/prioritisation-matrix/` into `~/.claude/skills/` (Claude Code), or zip it
and upload it in the Skills section of the Claude app's settings, then say *"help me decide which
AI project to start with"*. It asks for evidence behind each score and records how confident
you are.

## Using it well

- **Score one criterion at a time across all projects**, not one project at a time. Your scale
  stays consistent.
- **Write the evidence in the notes column.** "Ops lead spends 3 hours every Monday" is a
  score. "Seems valuable" is a guess. Mark guesses as low confidence.
- **Treat anything within 5 points as a tie**, and decide on what the matrix doesn't capture,
  like timing, politics or who's excited.
- **Start one project.** The matrix ranks them all, but running three pilots at once is how
  none of them get finished.
- **Re-score every quarter.** Models get better, data gets cleaner and owners free up, so last
  quarter's fourth place can be this quarter's first.
