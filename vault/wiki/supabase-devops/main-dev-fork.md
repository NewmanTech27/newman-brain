---
title: newman-architecture main/dev is a two-way fork, not drift
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, git, fork]
created: 2026-07-09
updated: 2026-07-09
sources: ["git rev-list origin/main..origin/dev", "git merge-base origin/main origin/dev = d28ae6b", "commit log both arms"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# newman-architecture main/dev is a two-way fork, not drift

Measured after `git fetch --all` on 2026-07-09: `origin/dev` is **+102 / −0** relative
to the merge-base, and `origin/main` is **+55 / −0**. They share **no commits** since the
fork. The merge-base is `origin/staging` (`d28ae6b`), which sits exactly on the fork point
(0 commits past it in either direction) — staging is **frozen**, not a promotion target.
`crm-platform` is an ancestor of `dev`.

This is a fork because the two arms are **two different products**, not competing versions
of one:

- **`dev` arm (+102): the Newman CRM** — `apps/crm-web` (Next.js), SSO gateway,
  huddle-sync, AML/KYC/credit underwriting. 250 files, +68,787 lines. Deploys crm-web to
  `tuesday.newman.re` (auto on push to `dev`). Migrations in `supabase/migrations/`
  (75, timestamped).
- **`main` arm (+55): the cfe-collector / bill-parser** — CFE extraction hardening,
  WhatsApp RPU-confirmation gate, CFDI ETL. 22 files, +4,133 lines. Deploys to
  `newman-vps` + `mini` (gated on green CI). Migrations in `db/migrations/` (numbered,
  through `015`).

Neither branch is a superset of the other, so **neither is globally canonical**. The
reconciliation is not "pick a winner" — the production database already holds the union
of both (see [[migration-git-prod-drift]]) — it is to **unify both arms into one trunk**
that reproduces production. Direction ruled by Jesus:
[[canonicity-prod-is-truth|production is truth]].

Additional hazard: `dev`'s `supabase/migrations/` is **CRM-only**; it contains none of
the cfe-collector schema (doc_pipeline, collection_queue, deadletter, cfe_account_pool,
RPU-gate) that lives in `main`'s `db/migrations/010–015` and in production. A from-scratch
`dev` database is therefore a strict subset of prod. Unifying the fork must fold the
cfe-collector schema into the canonical `supabase/migrations/` lineage.
