#!/usr/bin/env python3
"""
prioritise: rank candidate AI projects with a weighted matrix, and check
whether the ranking would survive a different set of weights.

    python3 prioritise.py criteria.csv projects.csv
    python3 prioritise.py criteria.csv projects.csv --md > ranking.md

criteria.csv   columns: key, criterion, weight            (weights sum to 100)
projects.csv   columns: project, owner, gates_passed (yes/no), confidence
               (high/medium/low), then one column per criterion key (scores 1-5)

Every criterion is phrased so that 5 is good (e.g. "low risk if wrong",
"easy to build"), so there is nothing to invert. The weighted score runs from
20 (all 1s) to 100 (all 5s).

No installs needed. Python 3.8+.
"""

import argparse
import csv
import sys

SHIFT = 10  # how many weight points to move when testing sensitivity


def read_criteria(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("key") or "").strip()]
    crit = [(r["key"].strip(), r["criterion"].strip(), float(r["weight"])) for r in rows]
    total = sum(w for _, _, w in crit)
    if abs(total - 100) > 0.01:
        sys.exit(f"Weights add up to {total:g}, not 100. Adjust criteria.csv.")
    return crit


def read_projects(path, crit):
    keys = [k for k, _, _ in crit]
    out = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for n, r in enumerate(csv.DictReader(f), start=2):
            name = (r.get("project") or "").strip()
            if not name:
                continue
            scores = {}
            for k in keys:
                v = (r.get(k) or "").strip()
                if v not in {"1", "2", "3", "4", "5"}:
                    sys.exit(f"{path} line {n} ({name}): '{k}' must be a whole number 1-5, got '{v}'.")
                scores[k] = int(v)
            out.append({
                "name": name,
                "owner": (r.get("owner") or "").strip(),
                "gates": (r.get("gates_passed") or "").strip().lower() in ("yes", "y", "true", "1"),
                "confidence": (r.get("confidence") or "").strip().lower() or "unknown",
                "scores": scores,
            })
    if not out:
        sys.exit(f"No projects found in {path}.")
    return out


def weighted(scores, weights):
    return sum(scores[k] * w for k, w in weights.items()) / 5


def rank(projects, weights):
    live = [p for p in projects if p["gates"]]
    return sorted(live, key=lambda p: -weighted(p["scores"], weights))


def shifted(weights, key, delta):
    """Move `delta` points onto `key`, taking them evenly from the others."""
    others = [k for k in weights if k != key]
    new = dict(weights)
    new[key] = max(0.0, weights[key] + delta)
    moved = new[key] - weights[key]
    for k in others:
        new[k] = weights[k] - moved / len(others)
    if min(new.values()) < 0:
        return None
    return new


def sensitivity(projects, weights, top):
    """Which single weight change of +/-SHIFT points would knock `top` off first place?"""
    flips = []
    for key in weights:
        for delta in (SHIFT, -SHIFT):
            w = shifted(weights, key, delta)
            if w is None:
                continue
            r = rank(projects, w)
            if r and r[0]["name"] != top:
                flips.append((key, delta, r[0]["name"]))
    return flips


def main():
    ap = argparse.ArgumentParser(description="Rank AI projects with a weighted matrix.")
    ap.add_argument("criteria")
    ap.add_argument("projects")
    ap.add_argument("--md", action="store_true", help="output markdown")
    args = ap.parse_args()

    crit = read_criteria(args.criteria)
    weights = {k: w for k, _, w in crit}
    names = {k: c for k, c, _ in crit}
    projects = read_projects(args.projects, crit)
    ranked = rank(projects, weights)
    parked = [p for p in projects if not p["gates"]]

    md = args.md
    out = []
    h = (lambda t: out.append(f"\n## {t}\n")) if md else (lambda t: out.append(f"\n{t}"))

    out.append("# Project ranking" if md else "Project ranking")
    if md:
        out += ["", "| Rank | Project | Score | Confidence | Owner |", "|---:|---|---:|---|---|"]
        out += [f"| {i} | {p['name']} | {weighted(p['scores'], weights):.0f} | {p['confidence']} | {p['owner']} |"
                for i, p in enumerate(ranked, 1)]
    else:
        w = max([len(p["name"]) for p in ranked] + [7])
        out += [f"  {i:>2}. {p['name']:<{w}}  {weighted(p['scores'], weights):>5.0f}  {p['confidence']}"
                for i, p in enumerate(ranked, 1)]

    if parked:
        h("Parked (failed a gate, not scored)")
        out += [f"{'- ' if md else '  - '}{p['name']}" for p in parked]

    if ranked:
        top = ranked[0]
        h("How solid is first place?")
        bullet = "- " if md else "  - "
        notes = []
        if len(ranked) > 1:
            gap = weighted(top["scores"], weights) - weighted(ranked[1]["scores"], weights)
            if gap < 5:
                notes.append(f"Close call: {top['name']} leads {ranked[1]['name']} by only {gap:.0f} "
                             f"points. Treat them as tied and decide on something the matrix doesn't capture.")
        flips = sensitivity(projects, weights, top["name"])
        if flips:
            for key, delta, winner in flips:
                verb = "mattered more" if delta > 0 else "mattered less"
                notes.append(f"If '{names[key]}' {verb} ({delta:+d} points), "
                             f"{winner} would come first instead.")
        else:
            notes.append(f"{top['name']} stays first even if any single weight moves "
                         f"{SHIFT} points either way. That's a robust lead.")
        if top["confidence"] in ("low", "unknown"):
            notes.append(f"{top['name']}'s scores are marked {top['confidence']} confidence. "
                         f"Check the guesses before committing.")
        out += [bullet + n for n in notes]

        h(f"What decides it for {top['name']}")
        by_score = sorted(weights, key=lambda k: (-top["scores"][k], -weights[k]))
        best = ", ".join(f"{names[k]} ({top['scores'][k]}/5)" for k in by_score[:3])
        weakest = by_score[-1]
        out.append(f"{bullet}Strongest on: {best}.")
        out.append(f"{bullet}Weakest on: {names[weakest]} ({top['scores'][weakest]}/5). "
                   f"That's the part most likely to disappoint, so test it early.")

    print("\n".join(out))


if __name__ == "__main__":
    main()
