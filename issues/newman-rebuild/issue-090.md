# #90: Migration-ledger drift: repo migrations cannot reproduce prod (pipeline schema + live RPCs applied via direct psql, unrecorded)

- State: CLOSED
- Created: 2026-07-12T10:12:21Z  Closed: 2026-07-12T14:52:36Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/90

## Body

## Problem

Prod's `supabase_migrations.schema_migrations` ledger records only the 8 migrations up to `20260710190000` — but prod actually runs the `pipeline` + `raw_cfe` schemas and their RPCs. `20260711210000_pipeline_schema.sql` and `20260711220000_pipeline_advance_rpcs.sql` were applied by **direct psql during the live bring-up and never recorded**, and several live objects were subsequently hot-patched the same way (see the companion issue on `rpc_advance_twilio`; the reaper adjustments from #84 are also live-only).

Additionally:
- **pg_cron job definitions exist only on live.** No migration contains a single `cron.schedule(...)` call — `20260711210000` explicitly defers them ("NO cron.schedule jobs … land in the executor-wiring step"), and that step was done via psql. The 5-stage schedule that drives the whole pipeline is unversioned.
- The charter §5 rule ("client-facing tables are never written by hand SQL") was exactly the lesson from the old repo (115 prod migrations git never saw — CHARTER.md "What this replaces"). The rebuild is re-accumulating the same class of debt, just earlier in its life.

## Why it bites now

dev/staging/prod Supabase branch CI/CD is being wired (2026-07-12). Branches created from prod carry the drifted schema but a stale ledger; `supabase db push` / GitHub-Actions migration apply will either report the pipeline migrations as pending against a database that already has the objects (idempotency failure) or silently diverge per environment. The repo is not a source of truth until this is repaired.

## Fix

1. Dump the LIVE definitions of every psql-applied object (pipeline/raw_cfe DDL, all `rpc_*` in the pipeline path, `cron.job` rows) and diff against `supabase/migrations/`.
2. Back-port every divergence into committed migration files (new timestamped migrations; never edit already-applied files).
3. `supabase migration repair` (or insert ledger rows) so the prod ledger lists exactly the committed set.
4. Add the pg_cron schedule as a migration (idempotent `cron.schedule` upserts).
5. Gate: `supabase db push --dry-run` against prod reports **zero pending** before the branch CI/CD is trusted.

## Evidence

- Committed migrations: `supabase/migrations/` (11 files, `20260710120000` … `20260712100000`).
- `supabase/migrations/20260711210000_pipeline_schema.sql:4-11` — comment deferring cron.schedule to a wiring step that was then done live.
- Operator session 2026-07-12: "Prod's migration ledger records only 8 migrations (up to …190000), but prod actually has the pipeline schema (4 tables) and RPCs — because 20260711210000/220000 were applied by direct psql, never recorded in the ledger."
