# Context audit: `before`

| | Tokens (est.) |
|---|---:|
| Loaded every session | 3,224 |
| Reachable by the agent | 29,384 |
| Blocked by deny rules | 0 |

## Largest reachable files (top 6)

| File | Tokens | Note |
|---|---:|---|
| `pos-sync.log` | 14,784 | big |
| `pos-export-2026.csv` | 7,452 | big |
| `memo-draft-v1.md` | 3,832 |  |
| `CLAUDE.md` | 3,224 | every session |
| `brief.md` | 52 |  |
| `status.md` | 40 |  |

## Suggestions

- CLAUDE.md is loaded every session and is ~3,224 tokens. Aim for under 1,500: keep rules and pointers, move reference material into docs/.
- pos-sync.log looks like a data dump (~14,784 tokens). Keep a short sample or summary and archive the full file.
- pos-export-2026.csv looks like a data dump (~7,452 tokens). Keep a short sample or summary and archive the full file.

_No Read deny rules found in `.claude/settings.json`._
