# Example: Harbour Cafe loyalty pilot (fictional)

The same project in two states, so you can see what the audit catches.

- `before/`: everything in one pile. Meeting notes and a 60-question survey pasted into
  `CLAUDE.md`, a POS log and a full-year export sitting next to the brief, and an old draft memo.
- `after/`: the same content, reorganised with the [scaffold](../scaffold/).
  Nothing was deleted.

Reports: [audit-before.md](audit-before.md) · [audit-after.md](audit-after.md)

Run it yourself from the `context-kit/` folder:

```bash
python3 skill/context-audit/context-audit.py example/before
```

```bash
python3 skill/context-audit/context-audit.py example/after
```
