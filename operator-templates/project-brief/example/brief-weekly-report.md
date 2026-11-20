# Brief: Weekly store report drafts

_Owner: Ops lead · Date: 2026-09-08 · Status: approved_

## The job
Turn the Monday POS export into a draft weekly report for the ops lead to check and send to
the five store managers.

## What it costs today
The ops lead spends about 3 hours every Monday building the report by hand (timed over 4 weeks:
2h40 to 3h20). Two of the last eight reports went out with a wrong store total.

## People
- **Owner** (accountable for the output): Ops lead
- **Uses it:** Five store managers, area manager
- **Checks it before it goes anywhere:** Ops lead, every week, before sending

## Inputs
- **Comes from:** Monday POS export (CSV), plus last week's report for comparison
- **Sensitive?** Internal: sales figures, no customer or staff personal data
- **Allowed in our AI tool?** Yes, internal sales data is cleared for the team's Claude plan (confirmed by the finance manager, 2026-09-02)

## Output
- **Looks like:** One page, the 5-row store table first (redemption rate first column), then 3 bullet points on what changed. Model: the 2026-08-25 report, which the area manager called "the one to copy"
- **Goes to:** Email to store managers and the area manager

## Done looks like
The ops lead spends under 30 minutes on the Monday report, with no wrong totals, for 4 weeks
running by 2026-10-31.

## Must never
- Send anything itself. It drafts; the ops lead sends.
- Guess a missing number. If a store's data is missing, say so in the draft.

## When it goes wrong
- **Most likely mistake:** Store 3's export writes dates as DD/MM, which double-counts weeks
- **How we'd notice:** The draft states each store's date range at the top; the ops lead checks it
- **Fallback:** Build the report by hand as now (template kept in the shared drive)

## First version
- **In:** Draft table and bullets from the export, as a Claude project with the export uploaded each Monday
- **Out (for now):** Charts, automatic emailing, pulling the export automatically
- **Stop if:** The ops lead is still spending over 90 minutes on it after 3 weeks

## Cost
- **To build:** About 4 hours of the ops lead's time to set up and test on 4 past weeks
- **To run:** Covered by the existing Claude Team plan
- **Ongoing care:** 10 minutes a week reviewing; update the instructions when the report format changes
