#!/usr/bin/env python3
"""INT-2: every page named in log.md must exist under wiki/.

An agent that logs an artifact it never wrote has corrupted the graph's
provenance. Exit 1 so this can gate a merge.
"""
import pathlib
import sys

ROOT = pathlib.Path.home() / "cfe-brain"
VAULT = ROOT / "vault"
WIKI = VAULT / "wiki"
LOGS = [ROOT / "log.md", WIKI / "log.md"]


def pages_on_disk():
    return {p.stem for p in WIKI.rglob("*.md")}


def pages_claimed():
    claims = []
    lines = []
    for log in LOGS:
        if log.exists():
            lines += log.read_text().splitlines()
    for line in lines:
        if not line.startswith("|") or line.startswith("|---") or "pages created" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        date, source, pages, agent = cells[0], cells[1], cells[2], cells[3]
        for name in (p.strip() for p in pages.split(",")):
            if name:
                claims.append((date, agent, name))
    return claims


def main():
    if not any(l.exists() for l in LOGS):
        print("no log.md found")
        return 0
    on_disk = pages_on_disk()
    missing = [(d, a, n) for d, a, n in pages_claimed() if n not in on_disk]

    if not missing:
        print(f"INT-2 pass — every logged page exists ({len(on_disk)} pages on disk)")
        return 0

    print(f"INT-2 FAIL — {len(missing)} logged page(s) do not exist:\n")
    for date, agent, name in missing:
        print(f"  {date}  {agent:20s}  {name}")
    print("\nAn agent logged an artifact it never wrote. Treat as P0.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
