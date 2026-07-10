---
title: "GATE 0 reconciliation: reset-vs-merge hazard"
type: analysis
kind: finding
tags: [gate-0, canonicity, supabase-devops, branch-fork, del-4, hazard]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "git rev-list d28ae6b..origin/dev = 102; d28ae6b..origin/main = 55 (newman-architecture, fetched 2026-07-10)"
  - "newman-architecture git ls-tree origin/main docs/cfe-collection.md (present); origin/dev (absent)"
  - "prompts/ceo.md:61; prompts/CHARTER.md:44-55"
verified_against: "newman-architecture merge-base d28ae6b (=origin/staging); tips origin/dev, origin/main @ 2026-07-10 fetch"
confidence: high (commit counts re-derived post-fetch); medium (that reconciliation would be *executed as a reset* is an inference about method, not an observed plan)
---

# GATE 0 reconciliation: reset-vs-merge hazard

**Finding:** The GATE 0 canonicity reconciliation must be executed as a **merge that
preserves both arms**, never as a `git reset` / re-baseline / branch-truth swap. Executed
as a reset, it silently orphans an entire product. This page names the counts, the executor,
and the precondition that makes it safe — so a future session cannot re-derive the danger too
late.

## The fork (verified 2026-07-10, post-`git fetch --all`)

- `origin/dev` is **+102** commits over the merge-base; `origin/main` is **+55**. They share
  no history since the fork. The merge-base is `d28ae6b`, which **is** `origin/staging`
  (0 ahead). This is a **bidirectional fork, not drift** — neither branch is a superset of the
  other, so a fast-forward in either direction is impossible.
- The two arms are **disjoint products**: `origin/dev` = the Newman CRM (246 dev-only files —
  `apps/crm-web/**`, CRM agents, sso-gateway); `origin/main` = the cfe-collector / bill-parser.
- **Stranded file:** `docs/cfe-collection.md` exists on `origin/main` **only** (verified by
  `git ls-tree`). It is the canary — whatever else lives only on main dies with main.

## Why a reset orphans a product

Because the arms are disjoint, "make branch X canonical" executed as a hard reset / force to
the winner **discards the loser's commits wholesale**:

- **dev-as-truth, reset main →** orphans main's 55 commits: the entire collector/bill-parser
  product and `docs/cfe-collection.md`.
- **main-as-truth, reset dev →** orphans dev's 102 commits: the **entire CRM**.

There is a second, database-side face of the same hazard. Production was built by hand: the
prod Supabase ledger holds **117** applied migrations, but of `dev`'s 75 `supabase/migrations`
only **5** exist in the ledger — **70 diverge** (board KPI `DEL-4` = **5/75**). A
`supabase db reset` / native-branch rebuild **cannot reproduce prod**. So a git-side reset and
a Supabase-side reset are both destructive here, for the same root reason: no single artifact
describes the whole live system.

## Who would execute it, with what permissions

`supabase-devops` (tmux `data`) is the only session that executes merges (per
`prompts/CHARTER.md`). It holds the Supabase MCP write surface — `merge_branch`,
`reset_branch`, `rebase_branch`, `apply_migration`, `execute_sql` — and runs with
`--dangerously-skip-permissions`. It will not prompt before acting. A single mis-scoped
`reset_branch` or a `git reset --hard` to the "winner" is therefore one command from orphaning
an arm. `data` itself recommends **preserve-both, no arm discarded** — trust that instinct.

## Precondition that makes it safe

1. **Jesus's explicit canonicity ruling first.** Nobody reconciles before he rules.
2. **Reconcile by MERGE, preserve both arms.** The output `main` must contain both the CRM and
   the collector. No arm is reset away. (`git merge`/integration branch, not `reset`.)
3. **Honor the standing constraints:** no force-push, no branch deletion, no history rewrite.
4. **Close `DEL-4` before any environment rebuild:** generate a git baseline migration
   **from the prod ledger** so git can rebuild prod. Until that exists, GATE 4 (dev/staging/prod +
   Supabase branching) rests on a database git cannot reproduce.

## Related
- [[2026-07-09-gate0-fork-cto-verification]] — the independent CTO re-derivation of these counts.
- [[2026-07-10-multirepo-branch-audit]] — the multi-repo divergence audit.
- [[tonight-sizing-fix]], [[single-disk-risks]] — the unpushed `integration/gate0` (57 commits) is itself part of this.

## Confidence
High on the counts (re-derived post-fetch, 2026-07-10). Medium on the framing that the hazard
is specifically a *reset*: no one has proposed a reset in writing; the risk is that the
"make X canonical" instruction is **implemented** as one by an agent with reset tools and skip-permissions.
