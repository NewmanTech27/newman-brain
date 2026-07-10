#!/usr/bin/env python3
"""Graph integrity checks. Exit 1 on failure, so this can gate a merge.

INT-5  there is exactly one wiki root
INT-2  every page named in log.md exists on disk
INT-6  the log format INT-2 parses is the format the log actually uses

INT-5 exists because a second wiki root once made INT-2 report phantom pages for
work that had actually been done. A checker blind to its own blind spot is worse
than no checker: it produced a false accusation against an agent.

INT-6 exists because INT-2 then went blind a second way. It parsed markdown
table rows. The log moved to '## heading' + '- Pages created: [[x]]' entries.
INT-2 kept passing -- on the 9 legacy table rows -- while ignoring 88 newer
entries. A green check over an empty set is not evidence of anything.

The lesson generalises: a checker must assert that it found something to check.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path.home() / "cfe-brain"
VAULT = ROOT / "vault"
WIKI = VAULT / "wiki"
LOG = WIKI / "log.md"

WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")


def link_target(raw: str) -> str:
    """Resolve an Obsidian wikilink to the page stem it names.

    [[a/b|Alias]] -> b     [[a#Heading]] -> a     [[ b ]] -> b
    Getting this wrong is how a checker invents missing pages.
    """
    target = raw.split("|", 1)[0]          # drop display alias
    target = target.split("#", 1)[0]       # drop heading anchor
    target = target.strip().strip("/")
    return target.rsplit("/", 1)[-1]       # folder note -> its stem


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


def logged_pages():
    """Every page name the log claims, from BOTH formats it has ever used.

    Returns (claims, table_rows_seen, bullet_rows_seen) where claims is a list
    of (context, page_name).
    """
    claims, table_rows, bullet_rows = [], 0, 0
    if not LOG.exists():
        return claims, table_rows, bullet_rows

    context = "?"
    for line in LOG.read_text().splitlines():
        stripped = line.strip()

        if stripped.startswith("## "):
            context = stripped[3:].strip()

        # legacy: | date | source | pages | agent |
        if stripped.startswith("|") and not stripped.startswith("|---") \
                and "pages created" not in stripped.lower():
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 4:
                table_rows += 1
                for name in (n.strip().strip("[]") for n in cells[2].split(",")):
                    if name:
                        claims.append((f"{cells[0]} {cells[3]}", name))

        # current: - Pages created: [[a]], [[b]]
        if stripped.lower().startswith("- pages created:"):
            found = WIKILINK.findall(stripped)
            if found:
                bullet_rows += 1
                for name in found:
                    claims.append((context, link_target(name)))

    return claims, table_rows, bullet_rows


def check_logged_pages():
    """INT-2: every page named in the log exists. INT-6: we parsed both formats."""
    if not LOG.exists():
        print(f"INT-2 skip — no log at {LOG}")
        return True

    claims, table_rows, bullet_rows = logged_pages()
    on_disk = {p.stem for p in WIKI.rglob("*.md")}

    # INT-6 -- coverage. A parser that matches nothing must not report success.
    heading_entries = sum(
        1 for l in LOG.read_text().splitlines() if l.strip().startswith("## ")
    )
    declared = sum(
        1 for l in LOG.read_text().splitlines()
        if l.strip().lower().startswith("- pages created:")
    )
    if declared and not bullet_rows:
        print(f"INT-6 FAIL — log has {declared} 'Pages created:' bullets but the "
              f"parser matched 0. INT-2 is reading a format the log no longer uses.")
        return False
    if not claims:
        print(f"INT-6 FAIL — the log has {heading_entries} entries and the parser "
              f"extracted 0 page claims. A green check over an empty set proves nothing.")
        return False
    print(f"INT-6 pass — parsed {len(claims)} page claims "
          f"({table_rows} table rows, {bullet_rows} bullet entries)")

    missing = [(ctx, name) for ctx, name in claims if name not in on_disk]
    if not missing:
        print(f"INT-2 pass — every logged page exists "
              f"({len(claims)} claims, {len(on_disk)} pages on disk)")
        return True

    print(f"INT-2 FAIL — {len(missing)} logged page(s) do not exist:\n")
    for ctx, name in missing:
        print(f"  {name:45s}  claimed by: {ctx}")
    print("\nBefore blaming the agent: confirm there is only one wiki root (INT-5),")
    print("and that the parser understands the log's current format (INT-6).")
    return False


if __name__ == "__main__":
    ok = check_single_root()
    ok = check_logged_pages() and ok
    sys.exit(0 if ok else 1)
