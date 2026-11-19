# Downloads organiser

Sorts a messy Downloads folder by reading filenames. It never deletes anything, shows you
the plan before it moves a single file, and can undo a whole run.

Python 3.8+ (already on macOS), no installs.

## What you end up with

| Folder | What goes here |
|---|---|
| `00-Inbox/` | Anything new, plus anything the rules couldn't confidently place. **The only folder you need to check regularly.** |
| `01-Clients/<name>/` | One folder per client or project, by name in the filename |
| `02-Finance/` | `Invoices/` `Statements/` `Contracts/` `Budgets/` |
| `03-Design-Assets/` | `Fonts/` `Mockups/` `Brand/` `Artwork/` |
| `04-Personal/` | `CVs/` `Photos/` |
| `05-Dev/` | `scripts/` `sql/` `data/` `secrets/` |
| `06-Study/<code>/` | One folder per course, by course code in the filename |
| `99-Quarantine/` | Duplicates, installers and already-extracted zips, waiting for **you** to delete them. See `MANIFEST.md` inside. |

`_archive/` inside any folder holds older versions. The newest `_vN` stays put and older
ones move into `_archive/`, out of the way but never lost.

All of this is set in one config file, so you can rename, add or remove anything.

## Setup (5 minutes)

**1. Put the config where the script looks for it**

```bash
mkdir -p ~/.config/tidy-downloads
```

```bash
cp tidy-config.example.json ~/.config/tidy-downloads/config.json
```

**2. Edit it.** Replace the example client names and course codes with yours. Rules run top to
bottom and the first match wins, so put specific rules (clients) above general ones (file types).
`{match}` in a destination becomes the keyword that matched, so `"01-Clients/{match}"` gives
each client its own folder.

**3. Make it a command** (optional)

```bash
echo "alias tidy-downloads='python3 $(pwd)/tidy-downloads.py'" >> ~/.zshrc && source ~/.zshrc
```

## The routine

Once a month, or whenever Downloads feels messy:

```bash
tidy-downloads
```

It prints what it *would* do and changes nothing. If the plan looks right:

```bash
tidy-downloads --apply
```

Then skim `00-Inbox/` and file the leftovers by hand. Those are the ones the rules
deliberately refused to guess at.

```bash
tidy-downloads --stale 90           # also list files untouched for 90+ days
```

```bash
tidy-downloads --undo-last          # preview undoing the previous run
```

```bash
tidy-downloads --undo-last --apply  # do it
```

## Naming that keeps it working

The sorter reads filenames, so the names do the work:

- **Lead with the client:** `Acme_Board_Update_June.pptx` files itself. `Board Update.pptx` lands in the Inbox.
- **Version with `_v2`, `_v3`:** `Proposal_v6.docx` beats `Proposal final FINAL (2).docx`. The sorter keeps the highest and archives the rest.
- **Say what it is:** include `invoice`, `statement`, `contract` or `CV` and the file routes itself.

Keywords match whole words, so `CV` catches `My_CV.pdf` but not `data.csv`.

## Guarantees

- **Never deletes.** It only moves, and every move is written to `.tidy-journal.json` in your
  Downloads folder, so `--undo-last` can put a whole run back.
- **Never overwrites.** If a name is taken, the file becomes `Report (1).pdf`.
- **Duplicates are proven, not guessed.** Files are compared by MD5 content hash, so two files with
  the same name but different contents are both kept.
- **Zips are checked file by file.** A `.zip` only counts as redundant once every file inside it is
  found on disk at the right size. A partly extracted archive is always kept.
- **Folders are never merged.** If a folder's destination already exists, it's flagged for you to
  compare, because two folders can differ in ways their names can't show.

## Secrets

Files that look like keys or credentials (`client_secret*.json`, `*.pem`, `*.key`, `.env`,
recovery codes and so on: see `secret_patterns` in the config) go to `05-Dev/secrets/` and are
locked to owner-only (`chmod 600`). That's a holding pen, not a home: Downloads is often
synced to the cloud. Move each one into a password manager, rotate any key that may have
leaked, then delete the file.

## Run it automatically (optional)

The point of the dry run is that you read it, so a monthly reminder to run it yourself is usually
better than automation. If you do want it scheduled, use a launchd job or cron with `--apply`
and keep `--undo-last` in mind.

## Notes

- Only the top level of Downloads is sorted. A loose folder moves as one piece (to a matching
  rule or the Inbox), and nothing inside it is ever rearranged.
- `--undo-last` moves files back but leaves any folders it created (empty) and keeps the
  `chmod 600` on secrets.
