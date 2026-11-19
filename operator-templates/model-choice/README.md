# Which model for which job

**The biggest model is the default in most tools. For a lot of everyday work it's also 20 to
40 times the price of a model that would do the job just as well.**

This is a one-page guide to matching the job to the model, plus a 20-minute test to find out
whether a cheaper model is good enough for *your* tasks, so you're not taking anyone's word for it.

## The tiers

Every major AI provider sells roughly three sizes. Using Claude as the example
(API list prices, November 2026, per million tokens):

| Tier | Claude model | Input | Output | Relative cost |
|---|---|---:|---:|---:|
| **Small** | Haiku 5.5 | $0.10 | $0.50 | 1× |
| **Mid** | Sonnet 5.5 | $2.00 | $10.00 | 20× |
| **Large** | Opus 5.5 | $4.00 | $20.00 | 40× |
| **Frontier** | Fable 5.2 | $8.00 | $40.00 | 80× |

Prices change every few months; the *gaps between tiers* are what matter, and they've stayed
wide. Check [current pricing](https://platform.claude.com/docs/en/about-claude/pricing) before you budget.

**What that gap means in practice:** sorting 1,000 customer emails (about 500 words each, a one-word
label back) costs roughly **7 cents on the small tier and $2.80 on the large one**. Same job, same result,
if the small one gets the labels right. That "if" is what the test below checks.

**On a subscription plan** (Claude Pro, Max, Team) you don't see a bill per task, but the same
logic applies to your usage limits: bigger models use up your allowance faster.

## Match the job to the tier

| Job | Start with | Step up when |
|---|---|---|
| Sorting, tagging, routing ("is this a complaint, a question or an order?") | Small | It mislabels more than 1 in 20 on your test set |
| Pulling fields out of documents (dates, amounts, names) into a table | Small | Documents are messy or the fields need judgement |
| Reformatting, translating, cleaning up text | Small | Tone or nuance matters to the reader |
| Summarising a clear document | Small | The document is long, technical, or the summary drives a decision |
| Drafting emails, posts and docs from your notes | Mid | It keeps missing the point you're making |
| Everyday chat, brainstorming, spreadsheet formulas | Mid | Rarely needs more |
| Research across many sources, comparing options | Mid | Sources conflict and someone has to judge |
| Agents that work through files over many steps | Mid or Large | It loses the thread, loops, or needs lots of correcting |
| Strategy, ambiguous problems, high-stakes writing | Large | The large model has had a fair try and still falls short |
| Hard reasoning, long autonomous projects, complex code | Large | Then Frontier, only if Large demonstrably fails |

**Rule of thumb:** start one tier lower than your instinct, and step up only when you see it
fail on real work, not because you're worried it might.

## Before you switch models, try these

Two other dials often save as much as changing models, with less risk:

1. **Feed it less.** Most cost is what the model *reads*. A short brief and a summary beat
   pasting the whole folder. See the [context kit](../../context-kit/).
2. **Turn down the effort.** Newer models let you choose how hard they think (Claude Code and
   the API have an *effort* setting). Low effort on a big model is often enough for routine work
   and costs a fraction of high effort.

## Judge cost per finished job, not per message

A cheap model that needs three attempts and twenty minutes of your edits isn't cheap. Count the
whole job: the attempts, the fixing, and your time. That's why the test below scores
**"would I send this with light edits?"** and not "was it perfect?".

## The 20-minute test

Use [`model-trial.csv`](model-trial.csv) to record it.

1. **Pick one task you repeat** (weekly report, email triage, meeting summary).
2. **Collect 5 real examples** of it, including one awkward one.
3. **Run all 5 on your usual model, then on one tier down.** Same prompt, same inputs.
4. **Score each one:** would you send it with light edits? Yes or no.
5. **Decide:** if the cheaper tier passes 4 or more out of 5, switch that task. If it passes 2 or
   fewer, stay. If it's 3, try the cheaper tier with more effort or a clearer prompt, then re-test.
   Look at *which* one failed: if it's the awkward example, a common pattern is the cheaper
   model for routine runs and the bigger one only for exceptions.
6. **Re-test when models change.** New releases move the line, usually downwards: last year's
   large-model job is often this year's mid-model job.

## Where to change it

- **Claude app:** the model picker by the message box.
- **Claude Code:** `/model`
- **API / automations (n8n, Make, scripts):** the `model` setting on each step. Mix tiers
  within one workflow: a small model to triage, a bigger one only for the items that need it.
