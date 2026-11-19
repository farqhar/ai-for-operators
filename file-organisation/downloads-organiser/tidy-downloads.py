#!/usr/bin/env python3
"""
tidy-downloads: sort a messy Downloads folder by filename rules. Safely.

    python3 tidy-downloads.py               # show the plan, change nothing
    python3 tidy-downloads.py --apply       # do it
    python3 tidy-downloads.py --undo-last   # put the last run back exactly
    python3 tidy-downloads.py --stale 90    # also list files untouched for 90+ days

Guarantees:
  - Never deletes. It only moves, and every move is written to a journal
    (.tidy-journal.json) so --undo-last can reverse a whole run.
  - Duplicates are proven by MD5 content hash, never guessed from names.
  - A .zip is only called redundant when every file inside it already exists
    on disk at the right size.
  - Folders are never merged. If a folder's destination already exists, it's
    flagged for you to compare.
  - Anything the rules can't place goes to the Inbox for you to file by hand.

Rules live in a JSON config (see tidy-config.example.json). No installs needed.
Python 3.8+.
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

JOURNAL = ".tidy-journal.json"
DEFAULT_CONFIG = Path("~/.config/tidy-downloads/config.json").expanduser()
VERSION_RE = re.compile(r"^(?P<base>.*?)[ _-]v(?P<n>\d+)$", re.IGNORECASE)


# ---------- matching ----------

def tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def keyword_hit(name_tokens, keyword):
    """True if the keyword's tokens appear as a run inside the filename's tokens.

    Token matching (not substring) means "cv" matches "My_CV.pdf" but not "data.csv".
    """
    kw = tokens(keyword)
    if not kw:
        return False
    n = len(kw)
    return any(name_tokens[i:i + n] == kw for i in range(len(name_tokens) - n + 1))


def match_rule(path, rules):
    """First matching rule wins. Returns (destination, rule label) or (None, None)."""
    name = path.name
    name_tokens = tokens(path.stem if path.is_file() else name)
    ext = path.suffix.lower() if path.is_file() else ""
    for rule in rules:
        if "ext" in rule and ext not in [e.lower() for e in rule["ext"]]:
            continue
        hit = None
        if "match" in rule:
            hit = next((k for k in rule["match"] if keyword_hit(name_tokens, k)), None)
            if hit is None:
                continue
        if "match" not in rule and "ext" not in rule:
            continue
        dest = rule["to"].replace("{match}", hit or "")
        return dest, (hit or ext)
    return None, None


def split_version(stem):
    m = VERSION_RE.match(stem)
    if m:
        return m.group("base"), int(m.group("n"))
    return stem, None


# ---------- hashing ----------

def md5(path, _cache={}):
    key = (str(path), path.stat().st_size, path.stat().st_mtime)
    if key not in _cache:
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        _cache[key] = h.hexdigest()
    return _cache[key]


def zip_is_redundant(zpath, root):
    """True only if every file in the zip exists, at the same size, in an
    extracted copy: a folder named after the zip, or the zip's own layout
    unpacked into the Downloads root or any folder named after the zip."""
    try:
        with zipfile.ZipFile(zpath) as z:
            members = [i for i in z.infolist() if not i.is_dir()]
    except (zipfile.BadZipFile, OSError):
        return False
    if not members:
        return False
    bases = [root] + [p for p in root.rglob(zpath.stem) if p.is_dir()]
    for base in bases:
        ok = True
        for m in members:
            target = base / m.filename
            if not (target.is_file() and target.stat().st_size == m.file_size):
                ok = False
                break
        if ok:
            return True
    return False


# ---------- planning ----------

class Plan:
    def __init__(self):
        self.moves = []    # (src, dst, reason)
        self.flags = []    # (path, message)
        self.secrets = []  # dst paths to chmod 600

    def move(self, src, dst, reason):
        self.moves.append((src, dst, reason))


def unique_target(dst, taken):
    """Avoid overwriting: Report.pdf -> Report (1).pdf if needed."""
    if not dst.exists() and dst not in taken:
        return dst
    i = 1
    while True:
        cand = dst.with_name(f"{dst.stem} ({i}){dst.suffix}")
        if not cand.exists() and cand not in taken:
            return cand
        i += 1


def build_plan(root, cfg):
    rules = cfg.get("rules", [])
    inbox = cfg.get("inbox", "00-Inbox")
    quarantine = cfg.get("quarantine", "99-Quarantine")
    secrets_to = cfg.get("secrets_to")
    secret_patterns = [p.lower() for p in cfg.get("secret_patterns", [])]
    junk_ext = [e.lower() for e in cfg.get("junk_ext", [])]

    managed = {inbox, quarantine} | {r["to"].split("/")[0] for r in rules}
    if secrets_to:
        managed.add(secrets_to.split("/")[0])

    # Index existing sorted files by size, so duplicates can be proven cheaply.
    by_size = {}
    for top in managed:
        d = root / top
        if d.is_dir():
            for p in d.rglob("*"):
                if p.is_file() and not p.is_symlink():
                    by_size.setdefault(p.stat().st_size, []).append(p)

    plan = Plan()
    taken = set()
    placed = []  # (dst) of files going to rule destinations, for version handling

    def wanted(p):
        if p.name in managed or p.name == JOURNAL:
            return False
        if p.name.startswith("."):  # hidden: only touch it if it looks like a secret
            return bool(secrets_to) and any(fnmatch.fnmatch(p.name.lower(), s)
                                            for s in secret_patterns)
        return True

    items = sorted(p for p in root.iterdir() if wanted(p))

    for p in items:
        if p.is_symlink():
            plan.flags.append((p, "symlink, left alone"))
            continue

        if p.is_dir():
            dest, why = match_rule(p, rules)
            target = root / (dest or inbox) / p.name
            if target.exists():
                plan.flags.append((p, f"a folder called {p.name} already exists in "
                                      f"{dest or inbox}/. Compare them by hand."))
                continue
            plan.move(p, target, f"folder rule: {why}" if dest else "folder, unsorted")
            continue

        name_l = p.name.lower()
        size = p.stat().st_size

        # 1. Likely secrets: keep them together, lock permissions, warn.
        if secrets_to and any(fnmatch.fnmatch(name_l, pat) for pat in secret_patterns):
            t = unique_target(root / secrets_to / p.name, taken)
            taken.add(t)
            plan.move(p, t, "looks like a secret or key")
            plan.secrets.append(t)
            continue

        # 2. Exact duplicate of something already sorted (or earlier in this run).
        dup_of = next((q for q in by_size.get(size, [])
                       if q != p and q.exists() and md5(q) == md5(p)), None)
        if dup_of is not None and size > 0:
            t = unique_target(root / quarantine / p.name, taken)
            taken.add(t)
            plan.move(p, t, f"identical to {dup_of.relative_to(root)}")
            continue

        # 3. Zip already fully extracted.
        if p.suffix.lower() == ".zip" and zip_is_redundant(p, root):
            t = unique_target(root / quarantine / p.name, taken)
            taken.add(t)
            plan.move(p, t, "zip contents already on disk")
            continue

        # 4. Junk (installers, partial downloads).
        if p.suffix.lower() in junk_ext:
            t = unique_target(root / quarantine / p.name, taken)
            taken.add(t)
            plan.move(p, t, f"junk type {p.suffix.lower()}")
            continue

        # 5. Rules.
        dest, why = match_rule(p, rules)
        if dest:
            t = unique_target(root / dest / p.name, taken)
            taken.add(t)
            plan.move(p, t, f"rule: {why}")
            placed.append(t)
        else:
            t = unique_target(root / inbox / p.name, taken)
            taken.add(t)
            plan.move(p, t, "no rule matched")
        # Later files in this run can be duplicates of this one.
        by_size.setdefault(size, []).append(p)

    archive_old_versions(plan, placed, taken)
    return plan


def archive_old_versions(plan, placed, taken):
    """Where several _vN files share a name in one folder, keep the highest
    version in place and send the others to that folder's _archive/."""
    groups = {}
    # Files arriving this run (by planned destination) plus files already there.
    candidates = {t: None for t in placed}
    for t in placed:
        if t.parent.is_dir():
            for q in t.parent.iterdir():
                if q.is_file():
                    candidates.setdefault(q, None)
    for path in candidates:
        base, n = split_version(path.stem)
        if n is not None:
            groups.setdefault((path.parent, base.lower(), path.suffix.lower()), []).append((n, path))

    redirect = {}
    for (folder, _, _), versions in groups.items():
        if len(versions) < 2:
            continue
        versions.sort()
        for _, old in versions[:-1]:
            redirect[old] = unique_target(folder / "_archive" / old.name, taken)
            taken.add(redirect[old])

    new_moves = []
    for src, dst, why in plan.moves:
        if dst in redirect:
            new_moves.append((src, redirect.pop(dst), why + ", older version"))
        else:
            new_moves.append((src, dst, why))
    # Files already sitting in the folder that are now superseded.
    for old, target in redirect.items():
        new_moves.append((old, target, "older version"))
    plan.moves = new_moves


# ---------- doing ----------

def show(plan, root):
    if not plan.moves and not plan.flags:
        print("Nothing to do. Downloads is tidy.")
        return
    by_dest = {}
    for src, dst, why in plan.moves:
        by_dest.setdefault(str(dst.parent.relative_to(root)), []).append((src, why))
    for dest in sorted(by_dest):
        print(f"\n{dest}/")
        for src, why in by_dest[dest]:
            print(f"  <- {src.relative_to(root)}   ({why})")
    if plan.flags:
        print("\nNeeds a human:")
        for p, msg in plan.flags:
            print(f"  ! {p.relative_to(root)}: {msg}")
    if plan.secrets:
        print("\nPossible secrets found. These will be locked to owner-only (chmod 600).")
        print("A synced Downloads folder is the wrong home for them: move each one to a")
        print("password manager, rotate the key if it may have leaked, then delete the file.")
    print(f"\n{len(plan.moves)} move(s) planned.")


def apply(plan, root, quarantine):
    done = []
    manifest = []
    try:
        for src, dst, why in plan.moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                raise RuntimeError(f"refusing to overwrite {dst}")
            shutil.move(str(src), str(dst))
            done.append([str(src), str(dst)])
            if dst.parent == root / quarantine:
                manifest.append(f"| `{dst.name}` | {why} | `{src.relative_to(root)}` |")
        for s in plan.secrets:
            os.chmod(s, stat.S_IRUSR | stat.S_IWUSR)
    finally:
        write_journal(root, done)
        if manifest:
            write_manifest(root / quarantine, manifest)
    print(f"Moved {len(done)} item(s). Undo with --undo-last.")


def write_manifest(qdir, rows):
    m = qdir / "MANIFEST.md"
    new = not m.exists()
    with open(m, "a", encoding="utf-8") as f:
        if new:
            f.write("# Quarantine\n\nNothing here has been deleted. Review, then delete what "
                    "you don't need.\n\n")
        f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M}\n\n| File | Why | Came from |\n|---|---|---|\n")
        f.write("\n".join(rows) + "\n")


def read_journal(root):
    j = root / JOURNAL
    if j.exists():
        return json.loads(j.read_text(encoding="utf-8"))
    return []


def write_journal(root, moves):
    if not moves:
        return
    runs = read_journal(root)
    runs.append({"at": datetime.now().isoformat(timespec="seconds"), "moves": moves})
    (root / JOURNAL).write_text(json.dumps(runs, indent=2), encoding="utf-8")


def undo_last(root, really):
    runs = read_journal(root)
    if not runs:
        print("No runs in the journal. Nothing to undo.")
        return
    last = runs[-1]
    print(f"Undoing run from {last['at']} ({len(last['moves'])} moves)"
          + ("" if really else ". Dry run: add --apply to do it."))
    problems = 0
    for src, dst in reversed(last["moves"]):
        s, d = Path(src), Path(dst)
        if not d.exists() or s.exists():
            print(f"  ! skip {d.name}: {'missing' if not d.exists() else 'original spot is taken'}")
            problems += 1
            continue
        print(f"  {Path(dst).relative_to(root)} -> {Path(src).relative_to(root)}")
        if really:
            s.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), str(s))
    if really:
        runs.pop()
        (root / JOURNAL).write_text(json.dumps(runs, indent=2), encoding="utf-8")
        print("Done." + (f" {problems} item(s) skipped, see above." if problems else ""))


def stale(root, days, inbox):
    cutoff = time.time() - days * 86400
    old = []
    for p in [root, root / inbox]:
        if p.is_dir():
            old += [q for q in p.iterdir()
                    if q.is_file() and not q.name.startswith(".") and q.stat().st_mtime < cutoff]
    if old:
        print(f"\nUntouched for {days}+ days (flag only, nothing moved):")
        for q in sorted(old, key=lambda q: q.stat().st_mtime):
            print(f"  {datetime.fromtimestamp(q.stat().st_mtime):%Y-%m-%d}  {q.relative_to(root)}")


def main():
    ap = argparse.ArgumentParser(description="Sort a Downloads folder by filename rules.")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                    help=f"rules file (default {DEFAULT_CONFIG})")
    ap.add_argument("--downloads", type=Path, help="folder to sort (overrides config)")
    ap.add_argument("--apply", action="store_true", help="actually move files")
    ap.add_argument("--undo-last", action="store_true", help="reverse the previous run")
    ap.add_argument("--stale", type=int, metavar="DAYS", help="flag files untouched for DAYS+")
    args = ap.parse_args()

    if not args.config.exists():
        sys.exit(f"No config at {args.config}.\nCopy tidy-config.example.json there and edit it, "
                 f"or pass --config path/to/config.json")
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    root = (args.downloads or Path(cfg.get("downloads", "~/Downloads"))).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")

    if args.undo_last:
        undo_last(root, args.apply)
        return

    plan = build_plan(root, cfg)
    show(plan, root)
    if args.stale:
        stale(root, args.stale, cfg.get("inbox", "00-Inbox"))
    if args.apply and plan.moves:
        apply(plan, root, cfg.get("quarantine", "99-Quarantine"))
    elif plan.moves:
        print("Dry run. Nothing changed. Re-run with --apply to do it.")


if __name__ == "__main__":
    main()
