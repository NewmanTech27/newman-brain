---
title: Canonicity ruling — production DB is truth, reconcile git to it
type: analysis
service: supabase-devops
kind: decision
tags: [supabase-devops, decision, migrations]
created: 2026-07-09
updated: 2026-07-09
sources: ["Jesus, 2026-07-09", "prompts/supabase-devops.md §Normative + §Known drift"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Canonicity ruling — production DB is truth, reconcile git to it

**Decision (Jesus, 2026-07-09):** given the two-way [[main-dev-fork]] and the
[[migration-git-prod-drift|git↔prod migration divergence]], the **production database is
the source of truth**. Git is to be reconciled to it, and the `main`/`dev` fork unified
into a single trunk that reproduces production from scratch.

**Alternatives rejected:**
- *"`dev` is the trunk going forward."* Rejected as insufficient: dev's migration files
  do not match the production ledger, so making dev canonical would not by itself restore
  from-scratch reproducibility — the git↔prod drift would persist.
- *"`main` is the trunk."* Rejected as the heaviest lift: it would require porting the
  entire 102-commit / +68k-line CRM onto `main`'s numbered `db/migrations/` structure.
- *"Hold and investigate first."* Not chosen; the evidence already established that
  production is the union of both arms and that the fork is a git-bookkeeping failure, so
  the direction was decidable without further digging.

**Why this direction:** production is healthy (FUNCTIONS_DEPLOYED) and already holds the
union of both product lines; the divergence is entirely in git's record of how it got
there. Reconciling git to the deployed reality is the smallest correct move and directly
fixes the `db push` / preview-branch hazards.

**Consequences (drives the Phase 3 plan):**
1. Re-baseline `supabase/migrations/` to the production ledger so `db push --dry-run` is a
   no-op.
2. Fold `main`'s cfe-collector schema (`db/migrations/010–015`) into the canonical
   `supabase/migrations/` lineage so the trunk is a superset of both arms.
3. No merge to `main` until the reconciliation is agreed and CI is green.

Normative anchor: `prompts/supabase-devops.md` — "the migrations in git ARE the normative
schema; the deployed database is the implementation. Drift is a defect in the database."
This ruling restores that contract by making git faithfully describe the database again.
