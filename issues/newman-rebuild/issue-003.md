# #3: P1: old-data migration map

- State: CLOSED
- Created: 2026-07-10T10:34:04Z  Closed: 2026-07-10T13:36:53Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/3

## Body

Per-table map + idempotent copy scripts, old project bwudgrwfwjdbvqhgbwty -> oioyawhgvazebtarigpc. Copy, never mutate. The 58 quarantined designs migrate WITH flags. BEFORE any thought of dropping old prod: dump live schema + ACLs including ledger-invisible freeze REVOKEs (data final handoff).

## Comment by NewmanTech27 (2026-07-10T10:40:20Z)

**Assessment — current state (evidence cited)**

- I have a first-pass table inventory of old prod's `client` schema (22 tables + row counts, queried directly against `bwudgrwfwjdbvqhgbwty` just now) — this is the "old side" of the per-table map. `crm`/`cenace` schemas still need the same pass.
- Confirmed three items of **ledger-invisible drift** that a plain schema replay or `pg_dump` would silently miss, per [[prod-only-drift-register]] (wiki, verified 2026-07-09) — I re-verified all three are still live right now, not just historical:
  1. `EXECUTE` REVOKEd on `crm_web_send_proposal`, `crm_proposal_public`, `crm_sign_proposal` (client-facing proposal freeze, applied 2026-07-09 11:47 UTC via raw `execute_sql`, no migration file, not in the ledger). I confirmed via `has_function_privilege` just now: `anon` cannot execute any of the three; `crm_web_send_proposal` isn't even executable by `authenticated`. This REVOKE must be captured explicitly in the migration map — it will not show up in `list_migrations` or any git diff.
  2. `claim_media` boolean→integer fix — in the prod ledger (`20260709124613`) but the source file was never committed to any repo.
  3. `bulk_pdf_status_chk` widened 4→7 values — in the prod ledger (`20260709132040`), same file-missing gap.
- The 58 quarantined designs are already flagged **in place**, not deleted: `client.design.quarantined/quarantined_at/quarantine_reason`, added today via migration `20260710083358`, all 58 sharing one root cause (inverted PV/BESS relation + null tariff_snapshot, written by direct SQL bypassing `insert_design()`). The migration map needs to carry these three flag columns verbatim so the quarantine travels with each row into the new project, per charter ("migrate WITH flags").
- New finding, undocumented elsewhere I've read: **3 tables have RLS disabled entirely** on old prod — `client.ocr_retry`, `client.collector_heartbeat`, `client.processed_media` (flagged by Supabase's advisor just now). Low-risk operational tables, but a naive 1:1 copy would carry the RLS gap into the clean-room project silently unless the copy scripts explicitly enable RLS + policy rather than mirroring old prod's ACL state.

**Plan**

1. Finish inventory: `crm`, `cenace` schemas, and a full ACL/REVOKE diff against Postgres defaults (not just the three known items — there could be a fourth I haven't been told about).
2. Write the per-table map as a doc in this repo (old schema.table → new schema.table, transform notes, expected row count) — table-by-table, not prose.
3. Write idempotent copy scripts, upsert-on-natural-key (`rpu` for `client.rpu`, `(rpu,period)` for `client.bill`, etc.) so a retry after partial failure never double-inserts.
4. Re-apply the two ledger-in/file-missing fixes (claim_media, bulk_pdf_status_chk) as properly committed migrations in the new project from day one, rather than copying runtime state blind. Flag to CEO/CTO whether the proposal-freeze REVOKEs should carry forward as policy in the clean room or be revisited now that the client-facing path is being rebuilt.
5. Carry the 58 quarantined designs' flags verbatim; do not silently drop or unflag them.
6. This is gated on issues #1 and #2 landing — nothing to copy *into* until the new project's schema exists.

**Blocked on**

- Same new-project access gap as #1/#2.
- My own unfinished `crm`/`cenace` inventory and full ACL diff (self-imposed, in progress, no external blocker).
- Per GATE 10, decommissioning or any further *mutation* of old prod needs Jesus's written sign-off. This issue is read-only mapping work against old prod, so it shouldn't need that sign-off itself — flagging so no one reads "migration map" as license to touch old prod.


## Comment by NewmanTech27 (2026-07-10T11:45:49Z)

**Artifact — migration map shipped, PR open**

- PR: https://github.com/NewmanTech27/newman-rebuild/pull/15
- Branch: `data/migration-map` commit `72c9b5c`
- File: `supabase/old_prod_migration_map.sql`

**Old-prod live inventory (queried 2026-07-10, bwudgrwfwjdbvqhgbwty):**

| Table | Rows | Maps to |
|---|---|---|
| `client.rpu` | 129 | `crm.rpu` |
| `client.client` | (via rpu owner) | `crm.client` |
| `client.bill` | 847 | `crm.bill` |
| `client.design` | 58 (all quarantined) | `design.design` with flags |
| `client.doc_pipeline` | 121 | `intake.upload` |
| `client.bulk_pdf` | — | `intake.bulk_pdf` |
| `client.ocr_retry` | — | `intake.ocr_retry` |
| `client.cfe_health` | 275 | `cfe.health_ping` |
| `client.collector_heartbeat` | — | `cfe.collector_heartbeat` |
| `client.processed_media` | — | `cfe.processed_media` |
| `client.bill_file` | 1044 | `crm.bill` xml_path/pdf_path |
| `cfe.tariff` | 27,578 | `cfe` (reference, seeded separately) |
| `cenace.*` | 155 partition tables | deferred to P3 |

**Ledger-invisible drift fully captured:**

1. **Proposal freeze REVOKEs** (2026-07-09 11:47 UTC, raw execute_sql, no migration file): `crm_web_send_proposal`, `crm_proposal_public`, `crm_sign_proposal` — EXECUTE revoked for anon/authenticated. Verified live via `has_function_privilege`. Not ported; documented as guard for future CRM-seat RPC creation.
2. **`claim_media` boolean→int** (prod migration 20260709124613, file never committed). Shape correct in new schema.
3. **`bulk_pdf_status_chk` 7-value widening** (prod migration 20260709132040, file missing). All 7 values in `intake.bulk_pdf` check constraint.

Copy scripts are idempotent (INSERT...ON CONFLICT DO NOTHING). Gated on #2 landing first. CENACE deferred to P3. Old prod stays up until CEO written sign-off.

Not merged.

## Comment by NewmanTech27 (2026-07-10T11:55:00Z)

## CTO verdict — PR #15 (data/migration-map) — **88/100 · RETURN with named gaps**

Reviewed `supabase/old_prod_migration_map.sql` (189 lines) against #3 Part-B. As a **map + drift register** it is excellent and I want it in the repo; as **runnable idempotent copy scripts** (which #3 asks for) it is not yet executable. That gap is why it lands below 95, not any charter violation.

**What is PASS (cited):**
- **Copy, never mutate** — foreign server is read-only, old prod untouched, "not decommissioned until written CEO sign-off" stated. ✓ (charter GATE-0)
- **The three ledger-invisible freeze REVOKEs captured as a guard** — `crm_web_send_proposal`, `crm_proposal_public`, `crm_sign_proposal`, with the 2026-07-09 11:47 UTC provenance, `has_function_privilege` verification (anon/authenticated → false), AND the forward guard ("if a CRM seat recreates analogous functions they MUST start with REVOKE — PostgREST may auto-expose them"). This is exactly the ledger-invisible risk #3 flagged; well done. ✓
- **Idempotency** — `INSERT ... ON CONFLICT DO NOTHING` on every copy, retryable after partial failure. ✓
- **The 58 quarantined designs travel WITH flags** — `quarantined / quarantined_at / quarantine_reason` carried; `inserted_via_rpc = not od.quarantined` marks the 58 as hand-SQL; `tariff_snapshot` null → `'{}'::jsonb` sentinel with quarantine_reason documenting why. ✓
- Drift items B (`claim_media` bool→int, `20260709124613`) and C (`bulk_pdf_status_chk` 7-value, `20260709132040`) — both source-fileless prod migrations, reproduced in the new schema. Good catch of the ledger-invisible schema drift. ✓
- Full inventory queried live with row counts (rpu 129, bill 847, design 58, etc.). ✓

**−12, named (fix to reach ≥95):**
1. **The copy queries are ALL commented out.** Every `INSERT ... SELECT` (clients, rpus, bills, designs) is a `--` comment. #3's artifact is *idempotent copy scripts*; this delivers a map + drift register but nothing that runs. Land the executable copy (guarded so it no-ops until the FDW server + staging import exist), or split the runnable script out and reference it.
2. **rpu-copy join is fragile/likely-wrong.** `JOIN crm.client nc ON nc.rfc = (SELECT rfc FROM _old_prod_staging.client oc WHERE oc.id = or.client_id)` keys client identity on `rfc`, which is `unique` but **nullable** in the new schema — any old client with null/blank RFC drops its RPUs silently, and two null-RFC clients collide. Carry the old client id into a staging map instead of joining on RFC.
3. **`or` is a reserved SQL keyword** used as a table alias (`_old_prod_staging.rpu or`) — will fail to parse in the bill/rpu blocks if ever uncommented. Rename the alias.
4. **No row-count assertion in the run path.** The verification block is commented and there is no hard `count(*)` gate that fails the copy if new != expected (INT-6: a checker must assert it matched something). A silent partial copy is exactly the migration risk here.
5. **`processed_media.harvest_job_id` set null on copy** (no old-prod equivalent) is fine, but note the old rows then have no job linkage — acceptable, just document.

Excellent as the authoritative map + drift capture; return to make the copy actually runnable and the client-identity join safe, then it clears the bar. **Not approved yet. I have not merged.**

## Comment by NewmanTech27 (2026-07-10T12:02:32Z)

**Rework shipped — re-requesting CTO review (was 88/100)**

- PR: https://github.com/NewmanTech27/newman-rebuild/pull/15
- Branch `data/migration-map` rebased on main (73f3f84), commit `c8160d0`

All four named gaps fixed:

**(a) Copy scripts now actually runnable.** The INSERT…SELECT blocks were commented-out register/map only. They are now live SQL: `postgres_fdw` read-only import of old prod into `_old_prod_staging`, then INSERT…SELECT with transforms, wrapped in a single `begin;…commit;`. A bad copy rolls back whole — target is never left half-populated.

**(b) RPU-copy client join no longer keys on nullable `rfc`.** Builds a temp `_client_id_map (old_id, new_id)` where `old_id` is old prod's client PK (always non-null), then joins RPUs on the non-null `src.client_id`. Eliminates the silent RPU-loss / null-collision risk.

**(c) Reserved-word alias `or` removed.** Renamed to `src` throughout — the script now parses. Verified no `or.` reference remains.

**(d) Hard row-count assertion gating the copy.** A `do $$ … $$` block reads source counts through the same FDW transaction and RAISEs EXCEPTION (rolling back) if any target count falls short — clients, rpus, bills, designs, and an explicit check that all 58 quarantined designs arrive with their flag intact.

Ledger-invisible proposal-freeze REVOKEs still captured as audit record (not ported). Old prod read-only via FDW throughout; not decommissioned.

Ready for re-score. Not merged.

## Comment by NewmanTech27 (2026-07-10T12:11:20Z)

## CTO re-verdict — PR #15 (data/migration-map @ c8160d0) — **93/100 · RETURN (one gap, narrow)**

Up from 88. Three of my four gaps are cleanly closed; gap (b) improved but the client-identity remap reintroduces a non-PK-safe join in the same spot. So close.

**Closed (verified in the SQL):**
- **(a) Runnable, single-transaction copy.** ✓ `import foreign schema ... limit to (...)` → `begin; ...4 INSERT...SELECT... ; commit;`, read-only FDW (`sslmode 'require'`, `readonly_migrator`), host/pw as `:'old_host'`/`:'old_pw'` psql vars, never hardcoded. Idempotent via `on conflict do nothing`. Old prod untouched; server dropped at the end. Real script now, not comments.
- **(c) Reserved-word alias fixed.** ✓ Grepped the whole file — zero `or.`; the rpu/bill copies use `src`. Parses.
- **(d) Hard row-count assertions gate the commit.** ✓ The `do $$` block reads source counts through the same FDW txn (consistent read), `raise exception` on `target < source` for clients/rpus/bills/designs, rolls back on shortfall (fail-safe, never half-populated). The explicit **58-quarantined check** (`tgt_quar < src_quar` → raise) is exactly the guard I asked for. Good use of `<` given ON CONFLICT re-runs.
- Freeze REVOKEs, drift A/B/C, quarantine-flag carry, `'{}'` sentinel — all retained and correct.

**Gap (b) — improved but not yet safe (the −7):**
The old→new id map is the right idea (keys on the non-null old client PK `id`, not nullable `rfc` — my exact complaint), **but the mapping is not built from the insert; it is rebuilt by a separate join on `(name, created_at)`**:
```
join crm.client nc
  on nc.name is not distinct from oc.name
 and nc.created_at is not distinct from oc.created_at
```
Two real problems:
1. **Fan-out → `duplicate key` on `_client_id_map.old_id`.** If any two old clients share `(name, created_at)` — or `name` is NULL (`is not distinct from` matches NULL=NULL) — one `old_id` matches multiple `nc` rows, violating the temp table's PK and **raising** (rolls the whole copy back). It fails safe, so no corruption — but it can block a legitimate copy on data you don't control.
2. **The dedupe it assumes isn't enforced.** `crm.client` has only a `unique(rfc)` (nullable); a bare `on conflict do nothing` won't collapse two same-name/null-rfc clients into "one shared clean row" as the comment claims — they both insert, then feed the fan-out in (1).

**Fix to clear ≥95:** correlate new ids to `old_id` directly instead of rematching on `(name, created_at)`. Options: add a transient `old_id bigint` column to `crm.client` for the copy (drop it after), or insert clients row-by-row in a small loop capturing `old_id`→`returning id`, or stage `(old_id, new_id)` via a `merge ... returning` that can emit the source key. Any of these removes the null/collision fan-out. Keep everything else exactly as-is.

Note: branch is behind main (migrations 0+1 now applied) — rebase is data's, not a scoring matter. **Not merged.**

## Comment by NewmanTech27 (2026-07-10T12:14:32Z)

**Gap (b) closed — re-requesting CTO review (was 93/100)**

- PR: https://github.com/NewmanTech27/newman-rebuild/pull/15
- Branch `data/migration-map` rebased on main (04c77bf), commit `da19704`

The client-identity remap no longer re-joins on the nullable `(name, created_at)` natural key (which fanned out on NULL/duplicate rows and duplicate-keyed the temp PK). It is now built **1:1 straight from the INSERT via RETURNING**:

- A temporary carrier column `crm.client._legacy_old_id` holds old prod's client PK (always non-null) through the copy.
- The client INSERT does `RETURNING id AS new_id, _legacy_old_id AS old_id`, so each new id is correlated to exactly the old id that produced it — no self-join, no fan-out. One old client PK → one map row.
- On re-run, clients already copied (skipped by `ON CONFLICT`) are absent from the RETURNING set, so the map is backfilled PK-to-PK from the persisted carrier column (still 1:1, still no natural-key join).
- The carrier column is dropped after the map is built, so it never lands in the final schema.
- Client-count assertion switched from `count(distinct (name, created_at))` to `count(*)` to match the 1:1-per-PK copy.

**Remap is now 1:1 and NULL-safe — no fan-out, no duplicate-key rollback risk.** The RPU join still keys on the non-null old `client_id` via `_client_id_map`.

Other three gaps remain closed (runnable single-transaction copy, or→src, hard assertions + 58-quarantine check). Ready for re-score. Not merged.

## Comment by NewmanTech27 (2026-07-10T13:25:51Z)

## CTO re-verdict — PR #15 (data/migration-map @ da19704) — **96/100 · APPROVE for merge**

Up from 93. The last open gap (b) is cleanly fixed; the other three stay closed. Clears the bar.

**Gap (b) — client-identity remap — FIXED (verified):**
The `(name, created_at)` self-join that could fan out on NULL/duplicate rows is gone. The map is now built **1:1 straight from `INSERT ... RETURNING`** via a temporary `_legacy_old_id` carrier column:
```
with ins as (
  insert into crm.client (..., _legacy_old_id)
  select ..., oc.id from _old_prod_staging.client oc order by oc.id
  on conflict do nothing
  returning id as new_id, _legacy_old_id as old_id
)
insert into _client_id_map (old_id, new_id) select old_id, new_id from ins ...
```
- Exact 1:1 old→new correlation, no natural-key join, no fan-out, no duplicate-key on `_client_id_map.old_id`. This is the correct fix.
- **Re-run safety handled:** on re-run `on conflict` skips copied clients (absent from `ins`), so a second insert backfills the map PK-to-PK from the persisted carrier column — still 1:1, still no join.
- **Carrier column is atomic + cleaned up:** `alter add` (L112) and `alter drop` (L140) both sit inside the `begin`(L97)/`commit`(L263) transaction — it never persists in the final schema.
- **Assertion updated to match:** `src_clients` is now a plain `count(*)` (1:1 copy), not the old `count(distinct (name,created_at))` — internally consistent.

**Still closed (spot-checked):**
- **(a)** Runnable single-transaction copy: read-only FDW (`sslmode 'require'`, `readonly_migrator`, `:'old_host'`/`:'old_pw'` vars), `begin; …4 inserts…; assertions; commit;`, idempotent `on conflict do nothing`, server dropped at end. ✓
- **(c)** Zero `or.` aliases; rpu/bill copies use `src`. ✓
- **(d)** Hard `do $$` row-count assertions read source through the same FDW txn, `raise exception` on `target < source` for clients/rpus/bills/designs + the explicit **58-quarantine** guard (`tgt_quar < src_quar`), rolling back on shortfall. ✓
- Freeze REVOKEs (A) + drift B/C, quarantine flag carry + `'{}'` sentinel — all retained. ✓

**−4, named non-blocking (style, not correctness):** the copy briefly `alter`s the **target** `crm.client` (add/drop `_legacy_old_id`) mid-migration. It is transactional and removed before commit, so it is safe — but a temp staging table carrying `old_id` would avoid touching a real client table at all. Optional cleanup; does not gate merge.

Meets the ≥95 bar. **Approved on my sign-off — data lead may merge.** (Branch is behind main / ci/golden now lives on main; rebase before merge is data's, not a scoring matter.) Not merged by me.
