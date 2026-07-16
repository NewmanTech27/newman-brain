# cfe-brain

**The schema lives at [`vault/CLAUDE.md`](vault/CLAUDE.md). Read that. It is authoritative.**

There is exactly **one** wiki root: `vault/wiki/`. File every page there.

## Why this file is a pointer and not a schema

This repo originally carried a second, thinner schema here, with its own `wiki/` at the repo root. When mario's vault was imported under `vault/`, that created **two wiki roots** — and agents dutifully filed pages into the root this file named, while `vault/tools/integrity_check.py` scanned only the vault root.

The result: `supabase-devops` was accused of logging three pages it never wrote. It had written all three. They were in the other root. The bug was in the schema, not the agent.

That failure is filed at [[graph-filing-two-roots-failure]].

**Never reintroduce a second wiki root.** `integrity_check.py` now fails loudly if one appears.

## Layout

- `vault/` — the knowledge base. Schema, wiki, tools. Authoritative.
- `prompts/` — charter, KPIs, and the per-agent prompts, version-controlled.
- `raw/` — sources awaiting compilation.
