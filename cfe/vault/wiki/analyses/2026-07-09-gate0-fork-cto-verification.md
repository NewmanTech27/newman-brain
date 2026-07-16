---
title: "GATE 0 branch fork — independent CTO verification"
type: analysis
tags: [supabase-devops, cto-finding, gate-0, branch-fork, migrations, git-prod-drift]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [git rev-list origin/main..origin/dev, supabase list_migrations bwudgrwfwjdbvqhgbwty, newman-architecture@a81c43c]
---

# GATE 0 branch fork — independent CTO verification

**Question:** the `supabase-devops` branch audit gates every merge. Is it real, or asserted?

## Answer — real. Every number re-derived from artifacts on 2026-07-09.

- **Bidirectional fork.** `origin/dev` is +102 vs the merge-base; `origin/main` is +55; they
  share no commits since the fork. `origin/staging` (`d28ae6b`) *is* the merge-base (0 ahead).
  Not drift — a fork.
- **Two products.** `dev` = the Newman CRM; `main` = the cfe-collector/bill-parser. Disjoint.
- **Stranded file.** `docs/cfe-collection.md` exists on `origin/main` only.
- **Two migration ledgers.** `main` carries 16 `db/migrations/*.sql`; `dev` carries 10
  `db/migrations/` + 75 `supabase/migrations/`. Different sets, no containment.
- **Git cannot reproduce prod.** The prod ledger holds **117** applied migrations (the
  hand-applied union). Of `dev`'s 75 `supabase/migrations` versions, only **5 exist in the
  prod ledger; 70 diverge** (verified by intersecting the git version prefixes with
  `list_migrations`). This is board KPI DEL-4 = 5/75 — the single worst number in the company.
- **One spec-header defect:** the spec cites `origin/main @ 8151003`; the live tip is
  `74809d0` (8151003 is 71 commits behind). Provenance nit; does not change the gaps.

## Why it matters
Prod is a hand-applied union of two divergent ledgers, so **neither git branch is a
replayable description of the live database**. No `supabase db reset` / native-branch rebuild
reproduces prod today. Everything at GATE 4 (Supabase branching, CI/CD) depends on closing
this. The golden test guards the savings engine, not the schema — it will not catch schema
drift. Canonicity ruling (Jesus, 2026-07-09): prod DB = truth, reconcile git to it.

## Confidence
High. Numbers re-derived from git and the live Supabase ledger at `a81c43c`.

## Related
- [[2026-07-09-cleanroom-sizing-live-path-verified]] — the other CTO finding of the day
