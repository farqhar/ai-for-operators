# Example: a reporting agent on day 40 (fictional)

An agent supporting the Harbour Cafe loyalty pilot (the same fictional project as the
[context kit example](../../../context-kit/example/)) has logged three entries a day for 40 days.

- `before/memory/live.md`: 120 entries, ~3,658 tokens, all loaded every session.
- `after/memory/`: the same memory after one rollover. `live.md` keeps the Pinned section and
  the 39 most recent entries (~1,179 tokens). The 81 older entries are in `archive/2026-08.md`,
  listed in `archive/INDEX.md`.

Try it from the `agent-memory/` folder:

```bash
python3 skill/agent-memory/memory-rollover.py example/before/memory
```

It prints the plan and changes nothing. Add `--apply` on a copy to see the rollover happen.

Notice the repeated "Ops lead wants weekly numbers as a 5-row table" entries in the log. That's
the classic mistake: a lasting preference written over and over as a Log entry. It belongs in
Pinned, written once.
