# Example: Harbour Cafe group (fictional)

A five-store cafe group with six AI ideas on the table. Scores and evidence are in
[`projects.csv`](projects.csv), and the ranking with its robustness check is in [`ranking.md`](ranking.md).
The same data is on the **Example** tab of the spreadsheet.

Re-run it from the `prioritisation-matrix/` folder:

```bash
python3 skill/prioritisation-matrix/prioritise.py criteria.csv example/projects.csv
```

Try changing a weight in `criteria.csv` (keep the total at 100) and running it again to see what
moves.
