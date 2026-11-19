#!/usr/bin/env python3
"""
context-audit: see which files in a project cost you tokens with an AI agent.

Every time an agent like Claude Code starts a session, it loads your
instruction file (CLAUDE.md) and then reads whatever files it decides it
needs. You pay for those tokens every session. This script walks a folder,
estimates the token cost of each file, and tells you what to trim, archive
or block.

No installs needed. Python 3.8+.

    python3 context-audit.py path/to/project
    python3 context-audit.py path/to/project --md > audit.md
    python3 context-audit.py path/to/project --top 30 --big 3000

Token counts are estimates (about 4 characters per token for English text and
code). They are good for spotting what is big, not for billing to the cent.
"""

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4

# Files the agent loads automatically at the start of every session.
ALWAYS_LOADED = {"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md"}

# Folders that almost never help an agent and are often huge.
NOISY_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", ".cache", "coverage", "logs", "exports", "tmp",
}

# File types that are usually data dumps rather than something to read.
NOISY_EXTS = {".log", ".csv", ".tsv", ".jsonl", ".sql", ".lock", ".map", ".min.js"}

# Folders that are meant to be cold storage.
ARCHIVE_DIRS = {"archive", "_archive", "old", "backup", "backups"}

SKIP_DIRS = {".git"}


def est_tokens(n_chars):
    return max(1, round(n_chars / CHARS_PER_TOKEN))


def is_binary(path):
    try:
        with open(path, "rb") as f:
            return b"\0" in f.read(4096)
    except OSError:
        return True


def load_deny_globs(root):
    """Read Read(...) deny rules from .claude/settings.json and settings.local.json.

    These are the rules that actually stop Claude Code opening a file.
    A rule like  Read(./archive/**)  becomes the glob  archive/**
    """
    globs = []
    for name in ("settings.json", "settings.local.json"):
        p = root / ".claude" / name
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print(f"warning: could not parse {p}", file=sys.stderr)
            continue
        for rule in data.get("permissions", {}).get("deny", []):
            if isinstance(rule, str) and rule.startswith("Read(") and rule.endswith(")"):
                g = rule[5:-1].strip()
                if g.startswith("./"):
                    g = g[2:]
                globs.append(g)
    return globs


def is_denied(rel, globs):
    for g in globs:
        if fnmatch.fnmatch(rel, g):
            return True
        # "folder/**" should also match the folder's direct children
        if g.endswith("/**") and rel.startswith(g[:-3] + "/"):
            return True
    return False


def scan(root):
    deny = load_deny_globs(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            full = Path(dirpath) / fn
            rel = full.relative_to(root).as_posix()
            if rel.startswith(".claude/"):
                continue
            if is_binary(full):
                continue
            try:
                n = len(full.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            parts = rel.split("/")
            files.append({
                "path": rel,
                "tokens": est_tokens(n),
                "always": fn in ALWAYS_LOADED,
                "denied": is_denied(rel, deny),
                "noisy_dir": next((p for p in parts[:-1] if p in NOISY_DIRS), None),
                "archive_dir": next((p for p in parts[:-1] if p.lower() in ARCHIVE_DIRS), None),
                "noisy_ext": any(fn.endswith(e) for e in NOISY_EXTS),
            })
    return files, deny


def folder_of(path, name):
    """The path up to and including the first folder called `name`."""
    parts = path.split("/")
    return "/".join(parts[: parts.index(name) + 1])


def advise(files, big):
    tips = []      # (weight, text): biggest savings first
    folders = {}   # folder -> [tokens, file count, kind]
    for f in files:
        if f["always"] and f["tokens"] > 1500:
            tips.append((f["tokens"] * 10, f"{f['path']} is loaded every session and is "
                         f"~{f['tokens']:,} tokens. Aim for under 1,500: keep rules and "
                         f"pointers, move reference material into docs/."))
        if f["denied"]:
            continue
        kind = "archive" if f["archive_dir"] else "noisy" if f["noisy_dir"] else None
        if kind:
            d = folder_of(f["path"], f["archive_dir"] or f["noisy_dir"])
            agg = folders.setdefault(d, [0, 0, kind])
            agg[0] += f["tokens"]
            agg[1] += 1
        elif f["noisy_ext"] and f["tokens"] > big // 2:
            tips.append((f["tokens"], f"{f['path']} looks like a data dump (~{f['tokens']:,} "
                         f"tokens). Keep a short sample or summary and archive the full file."))
        elif f["tokens"] > big:
            tips.append((f["tokens"], f"{f['path']} is ~{f['tokens']:,} tokens. If the agent "
                         f"reads it often, split it or add a summary at the top."))
    for d, (tok, n, kind) in folders.items():
        files_word = "file" if n == 1 else "files"
        why = ("is cold storage but is not blocked" if kind == "archive"
               else "rarely helps an agent")
        tips.append((tok, f"{d}/ holds ~{tok:,} tokens in {n} {files_word} and {why}. "
                          f"Add Read(./{d}/**) to your deny rules."))
    return [t for _, t in sorted(tips, key=lambda x: -x[0])]


def report(root, files, deny, top, big, md):
    always = sum(f["tokens"] for f in files if f["always"])
    reachable = sum(f["tokens"] for f in files if not f["denied"])
    blocked = sum(f["tokens"] for f in files if f["denied"])
    ranked = sorted((f for f in files if not f["denied"]), key=lambda f: -f["tokens"])[:top]
    tips = advise(files, big)

    def status(f):
        if f["always"]:
            return "every session"
        if f["tokens"] > big:
            return "big"
        return ""

    lines = []
    if md:
        lines += [f"# Context audit: `{root.name}`", "",
                  "| | Tokens (est.) |", "|---|---:|",
                  f"| Loaded every session | {always:,} |",
                  f"| Reachable by the agent | {reachable:,} |",
                  f"| Blocked by deny rules | {blocked:,} |", "",
                  f"## Largest reachable files (top {len(ranked)})", "",
                  "| File | Tokens | Note |", "|---|---:|---|"]
        lines += [f"| `{f['path']}` | {f['tokens']:,} | {status(f)} |" for f in ranked]
        lines += ["", "## Suggestions", ""]
        lines += [f"- {t}" for t in tips] or ["- Nothing obvious. This project is lean."]
        if not deny:
            lines += ["", "_No Read deny rules found in `.claude/settings.json`._"]
    else:
        lines += [f"Context audit: {root}", "",
                  f"  Loaded every session    {always:>10,} tokens",
                  f"  Reachable by the agent  {reachable:>10,} tokens",
                  f"  Blocked by deny rules   {blocked:>10,} tokens", "",
                  f"Largest reachable files (top {len(ranked)}):"]
        w = max([len(f["path"]) for f in ranked] + [4])
        lines += [f"  {f['path']:<{w}}  {f['tokens']:>8,}  {status(f)}" for f in ranked]
        lines += ["", "Suggestions:"]
        lines += [f"  - {t}" for t in tips] or ["  Nothing obvious. This project is lean."]
        if not deny:
            lines += ["", "  (No Read deny rules found in .claude/settings.json.)"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Estimate the token cost of a project folder.")
    ap.add_argument("path", nargs="?", default=".", help="project folder (default: current)")
    ap.add_argument("--top", type=int, default=15, help="how many files to list (default 15)")
    ap.add_argument("--big", type=int, default=5000,
                    help="flag files over this many tokens (default 5000)")
    ap.add_argument("--md", action="store_true", help="output a markdown report")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        sys.exit(f"not a folder: {root}")
    files, deny = scan(root)
    print(report(root, files, deny, args.top, args.big, args.md))


if __name__ == "__main__":
    main()
