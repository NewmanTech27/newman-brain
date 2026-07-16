---
title: Git migrations do not reproduce the production schema
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, migrations, drift]
created: 2026-07-09
updated: 2026-07-09
sources: ["supabase list_migrations (prod bwudgrwfwjdbvqhgbwty)", "origin/dev:supabase/migrations", "commit 14b539f"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Git migrations do not reproduce the production schema

The production Supabase project (`bwudgrwfwjdbvqhgbwty`, the `main` branch project)
carries **117 applied migrations** in its `supabase_migrations.schema_migrations`
ledger. The `dev` branch tracks **75** files under `supabase/migrations/`. Comparing the
two by `version` prefix, **only 5 of the 75 match**; 70 of dev's committed migrations
have versions production has never seen, and 112 of the 117 production migrations have no
corresponding file on `dev`.

The cause: production was migrated **by hand via the MCP `apply_migration` tool**, which
mints its own timestamped versions. The `supabase/migrations/` files are a separately
authored, re-timestamped narrative that was **never the actual apply path**. The
production ledger is the true, chronologically-interleaved union of both product lines
(CRM + cfe-collector); git holds a partial, renamed reconstruction of it.

Consequence: `supabase db push` (or the Supabase GitHub integration) from `dev` would
treat 70 versions as pending against production and attempt to re-apply them — duplicate
objects or errors — because the ledgers do not line up. Git has stopped being the source
of truth for the schema; the deployed database leads and git diverges. This inverts the
normative contract that [[canonicity-prod-is-truth|the migrations in git ARE the schema]].

Scope guard: the pgTAP `db-tests` job, which applies `supabase/migrations/` from an empty
database, **passed** on `dev@a81c43c` — so dev's 75 files are internally consistent and
replay cleanly *in isolation*. The drift is specifically **git-versions vs the hosted-prod
ledger**, not a broken local build. Related but distinct: [[main-dev-fork]] and the
CRM-only-schema gap.

**Remediation direction** (per [[canonicity-prod-is-truth]]): re-baseline the git
migration set to the production ledger (`supabase migration repair` / `db pull`) so
`db push --dry-run` reports zero pending, then keep them in lockstep.
