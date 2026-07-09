#!/usr/bin/env python3
"""Graph integrity checks. Exit 1 on failure, so this can gate a merge.

INT-2  every page named in a log.md exists on disk
INT-5  there is exactly one wiki root

INT-5 exists because a second wiki root once made INT-2 report phantom pages
for work that had actually been done. A checker blind to its own blind spot is
worse than no checker: it produced a false accusation against an agent.
"""
import pathlib
import sys

ROOT = pathlib.Path.home() / "cfe-brain"
VAULT = ROOT / "vault"
WIKI = VAULT / "wiki"
LOG = WIKI / "log.md"


def check_single_root():
    """INT-5: any wiki/ outside vault/ is a split-brain."""
    strays = [
        p for p in ROOT.glob("*/")
        if p.name == "wiki" or (p / "wiki").is_dir() and p.name != "vault"
    ]
    strays = [p for p in strays if p.resolve() != WIKI.resolve()]
    if strays:
        print("INT-5 FAIL — more than one wiki root:")
        for p in strays:
            print(f"  stray root: {p}")
        print(f"\nThe only wiki root is {WIKI}. Pages filed elsewhere are invisible to INT-2.")
        return False
    print(f"INT-5 pass — single wiki root at {WIKI}")
    return True


def check_logged_pages():
    """INT-2: every page named in the log exists."""
    if not LOG.exists():
        print(f"INT-2 skip — no log at {LOG}")
        return True

    on_disk = {p.stem for p in WIKI.rglob("*.md")}
    missing = []
    for line in LOG.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|---") or "pages created" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        for name in (n.strip().strip("[]") for n in cells[2].split(",")):
            if name and name not in on_disk:
                missing.append((cells[0], cells[3], name))

    if not missing:
        print(f"INT-2 pass — every logged page exists ({len(on_disk)} pages on disk)")
        return True

    print(f"INT-2 FAIL — {len(missing)} logged page(s) do not exist:\n")
    for date, agent, name in missing:
        print(f"  {date}  {agent:20s}  {name}")
    print("\nBefore blaming the agent: confirm there is only one wiki root (INT-5).")
    return False


if __name__ == "__main__":
    ok = check_single_root()
    ok = check_logged_pages() and ok
    sys.exit(0 if ok else 1)
