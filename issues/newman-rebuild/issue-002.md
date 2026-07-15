# #2: P1: schema design — intake/cfe/design/crm

- State: CLOSED
- Created: 2026-07-10T10:34:03Z  Closed: 2026-07-10T12:05:56Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/2

## Body

Constraints ARE the spec: design.tariff_snapshot NOT NULL; business_error enum (NAME_MISMATCH, ASSIGNED_ELSEWHERE, CAPTCHA_FAIL, TOO_MANY_RECIBOS, WAF_BLOCK); client-facing writes via RPC only, RPC advances pipeline state. Spec source: prod-is-truth ledger + cfe-brain wiki, NOT old code. MUST include recibo base/intermedio/punta split columns — see ppa final handoff: enrich.py:349 dumped CFDI total into kwh_base and the split was never captured.

## Comment by NewmanTech27 (2026-07-10T10:40:19Z)

**Assessment — current state (evidence cited)**

Per GATE 0 the old prod (`bwudgrwfwjdbvqhgbwty`) is the behavioral spec, not old code, so I queried it directly rather than reading `newman-architecture`.

- `client.design.tariff_snapshot` already exists as a column (text) but is **nullable today**, not enforced. I confirmed this is exactly how the 58 quarantined designs failed: all 58 I sampled have `tariff_snapshot IS NULL` as part of their disqualifying reason (`quarantine_reason` text, verbatim, includes "tariff_snapshot NULL so not reproducible"). The new schema needs `NOT NULL` from the table's creation, not a later `ALTER`.
- No `business_error` enum exists anywhere in old prod — I checked `pg_enum` for any type named like `%error%`/`%business%`, zero rows. `NAME_MISMATCH` / `ASSIGNED_ELSEWHERE` / `CAPTCHA_FAIL` / `TOO_MANY_RECIBOS` / `WAF_BLOCK` are genuinely new. This needs a home — most likely a `cfe.harvest_event`-shaped table — and lead-harvest is the primary writer, so the exact attach point should be a two-way call, not something I finalize alone.
- The recibo base/intermedio/punta split columns the issue calls out (citing `enrich.py:349`) **already exist at the schema level** in old prod's `client.bill`: `kwh_base/kwh_inter/kwh_punta` + `kw_base/kw_inter/kw_punta`. But they're sparsely populated — of 847 `client.bill` rows (726 tagged GDMTH), only 243 (≈33%) have `kwh_inter`/`kwh_punta` populated at all; `kwh_base` is populated in 846/847. This matches what the cfe-ppa-bess and data handoffs both flag: CFDI-sourced bills collapse to all-base. I'll carry these columns forward in the new schema (the shape is right), but populating them is lead-harvest/lead-engine's blocked dependency, not something I can unblock alone.
- RPC-only writes for client-facing tables is already the dominant pattern on old prod (`lock_rpcs_to_service_role`, `crm_rpc_lock_service_role_only`, `enable_rls_reference_schemas`, etc. — real migration names in the ledger) — I can carry the pattern forward as a design principle rather than invent it from scratch.
- I have a full table inventory of old prod's `client` schema (22 tables, row counts captured) as the primary input for `intake`/`cfe`/most of `design`. I have **not yet** inventoried the `crm` schema (referenced by many migration names: `crm_schema`, `crm_rbac`, `crm_rpc_contract`, etc.) or the `cenace` schema — that read pass is still open.

**Plan**

1. Finish the read-only inventory (`crm`, `cenace`, full RPC/ACL surface) — no external blocker, just unstarted.
2. Map old prod's tables onto the charter's five-schema split (`intake`/`cfe`/`design`/`crm`/`orchestration`), table by table — e.g. `doc_pipeline`/`bulk_pdf`/`bill_file` → `intake`; `cfe_account`/`cfe_lock`/`cfe_health` → `cfe`; `design` stays `design` with `tariff_snapshot NOT NULL` added and a `business_error` enum attached somewhere in the `cfe` harvest path.
3. Draft the `business_error` enum's attach point with lead-harvest, and the design-write RPC contract with lead-engine, before finalizing — both are the primary callers.
4. Write it as migrations in `newman-rebuild/supabase/migrations/`, RLS-enabled from creation, no client-facing hand-SQL writes.
5. I can draft and review this SQL today without new-project access; I can't apply or test it until issue #1 is unblocked.

**Blocked on**

- Same new-project access gap as #1 — blocks apply/test, not the design work itself.
- Input from lead-harvest (business_error attach point) and lead-engine (design RPC contract) before I finalize those two pieces.
- My own unfinished inventory of `crm`/`cenace` schemas on old prod (self-imposed, in progress).


## Comment by NewmanTech27 (2026-07-10T11:45:37Z)

**Artifact — migration 1 shipped, PR open**

- PR: https://github.com/NewmanTech27/newman-rebuild/pull/14
- Branch: `data/schema-core` commit `7ce5759`
- File: `supabase/migrations/20260710130000_core_schemas.sql` (506 lines)

**Charter non-negotiables met:**

| Requirement | Implementation |
|---|---|
| `design.tariff_snapshot NOT NULL` | Column-level `jsonb not null` line 384; `rpc_insert_design` raises exception if caller passes null |
| `business_error` enum | `cfe.business_error` with all 5 values; attached to `cfe.harvest_event.business_error` |
| Client-facing writes via RPC only | `intake.rpc_upload_invoice`, `design.rpc_insert_design` — both SECURITY DEFINER; `REVOKE EXECUTE from public, anon, authenticated` on both; tables also service_role-only |
| RLS default-deny from creation | ENABLE + FORCE on all 14 tables; schema-level REVOKE + `ALTER DEFAULT PRIVILEGES` makes it hereditary |
| Deterministic RLS (no drop+recreate trap) | No policies in this migration; RLS state = table-level grant only; future policy ADD is additive, not destructive |

**Old-prod RLS gaps fixed:**
- `client.ocr_retry` → `intake.ocr_retry` (RLS now enabled+forced)
- `client.collector_heartbeat` → `cfe.collector_heartbeat` (RLS now enabled+forced)
- `client.processed_media` → `cfe.processed_media` (RLS now enabled+forced)

**Old-prod schema queried live 2026-07-10** — confirmed via full inventory:
- `cfe` on old prod = tariff reference data, not harvest jobs (harvest was in `client.*`). New `cfe` schema owns both: reference data (populated from copy) + harvest operations.
- `crm` on old prod = 70+ function CRM system (not ported in P1). Clean-room `crm` schema = client/RPU/bill — the pipeline-relevant slice only.

NOT applied yet — waiting on CTO sign-off before `supabase db push`. Not merged.

## Comment by NewmanTech27 (2026-07-10T11:54:30Z)

## CTO verdict — PR #14 (data/schema-core) — **95/100 · APPROVE for merge**

Reviewed `supabase/migrations/20260710130000_core_schemas.sql` (506 lines) line-by-line against #2 Part-B. Every hard non-negotiable is met; gaps below are named and non-blocking for P1.

**Non-negotiables — all PASS (cited):**
- **`design.tariff_snapshot jsonb NOT NULL`** on `design.design`, AND `rpc_insert_design` raises `'tariff_snapshot required (charter #4)'` before insert. Belt and suspenders. ✓
- **`cfe.business_error` enum — all 5 values** (`NAME_MISMATCH, ASSIGNED_ELSEWHERE, CAPTCHA_FAIL, TOO_MANY_RECIBOS, WAF_BLOCK`), attached to `cfe.harvest_event.business_error` as a typed column, not a log line (charter #7). ✓
- **RPC-only client-facing writes**: `intake.rpc_upload_invoice` + `design.rpc_insert_design`, both `SECURITY DEFINER`, both `revoke execute ... from public, anon, authenticated` + grant to service_role only; the tables are also service_role-only so dashboard hand-SQL is blocked too. ✓
- **RLS ENABLE+FORCE, deterministic**: verified all **15** tables get both `enable` and `force row level security` from creation, zero policies; schema-level `revoke all from public, anon, authenticated` + `alter default privileges ... grant ... to service_role`. Grant-ordering trap cannot recur — new tables inherit the service_role grant, and Postgres grants nothing to anon/authenticated by default. ✓
- **Recibo split columns present** (the enrich.py:349 lesson): `crm.bill` carries `kwh_base/inter/punta` + `kw_base/inter/punta` + `kwh_total`. ✓
- Old-prod RLS-disabled tables (`ocr_retry`, `collector_heartbeat`, `processed_media`) all enabled+forced in new schema. ✓

**crm-scope ruling — the narrow P1 scope is CORRECT.**
Old prod's 70+ functions / 100+ web-layer RPCs are the FROZEN CRM being clean-room-replaced (charter: "newman-crm frozen read-only"; DEALS front-end + salesman flow are P2, lead-crm's remit). P1's job is the data foundation, and `crm.client / crm.rpu / crm.bill` is exactly the client/RPU/bill core the pipeline needs to land an offer. Porting the old RPC surface would re-import the measured debt the rebuild exists to shed. **Nothing is missing from crm for P1.** One thing to note, not add now: `design.deal_id` and `salesman_id` are free `text` with no `crm.deal` / `crm.app_user` table or FK — correct to defer (deals are P2/CRM scope), but they are dangling references until then; wire the FKs when the DEALS schema lands.

**−5, named (must-fix before P2 writes, not before merge):**
1. **RPC ownership unpinned.** `SECURITY DEFINER` runs as the function *owner*; the migration never `ALTER FUNCTION ... OWNER TO`. RLS-bypass correctness depends on who runs the migration. Pin the owner explicitly.
2. **RPCs don't emit a pipeline/orchestration trail.** Charter #5 = "writes go through RPCs that *advance pipeline state*"; `inserted_via_rpc=true` + a state bump is the local trail, but no `task_event`/audit row is written. The "row with no pipeline trail is a defect" guard is by-column, not by-event.
3. **`intake.bulk_pdf.status` is free `text`+CHECK** while every other state is a proper enum — inconsistent (acceptable, mirrors old-prod widening).
4. RPC stubs only (acknowledged in the PR) — the OCR-enqueue / crm.client-create paths are TODO; fine for a schema migration, but #2 is closed on schema, so track the RPC bodies as their own issue.

Meets the ≥95 bar. **Approved on my sign-off — data lead may merge and apply as migration 1.** (I have not applied it; new project still shows only migration 0.)
