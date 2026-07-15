# #6: P2: harvest telemetry + business-error report

- State: OPEN
- Created: 2026-07-10T10:34:08Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/6

## Body

Queryable rows: XML/PDF counts per RPU, typed errors, yield rate. KPI: XML yield. This is the report Jesus reads.

## Comment by NewmanTech27 (2026-07-10T10:40:00Z)

## Assessment — current state

**Nothing named "telemetry" exists in the new clean-room project, but old prod already runs most of the shape this issue asks for — it's a port-and-tighten job, not a from-scratch build.**

- Grepped `newman-architecture/db` + `supabase/migrations` for `business_error|xml_yield|harvest_log|telemetry` — zero hits. No enum, no dedicated report table, anywhere in the reference repo.
- Old prod (`bwudgrwfwjdbvqhgbwty`, read via the current Supabase MCP connection) already has the raw material:
  - `client.doc_pipeline` — `numero_xml_descargados` / `numero_pdf_descargados` **per RPU**, plus `status`, `ocr_model`, `ocr_raw`. This is most of the "XML/PDF counts per RPU" KPI already.
  - `client.bill_quarantine` (225 rows) — `rpu`, `period`, `reason`, `delta`, `detail`, `at`. Close to the "typed errors" ask, but `reason` is free **text**, not the charter's enum (`NAME_MISMATCH`/`ASSIGNED_ELSEWHERE`/`CAPTCHA_FAIL`/`TOO_MANY_RECIBOS`/`WAF_BLOCK`). That's a real gap, not just a rename.
  - `client.cfe_health` (275 rows) — `holder`, `service_count`, `leaked` (bool), `detail`. This is the "account left holding a service is an incident" hazard (charter §7) already being tracked, informally.
  - `client.collector_heartbeat` — liveness of the mini worker.
- None of `intake`/`cfe`/`design` schemas exist yet in either project I can see from here (confirmed empty on a `list_tables` sweep) — so there's no queryable home for a harvest report in the new instance yet.

## Plan

1. Once data seat's schema (issue #2) lands: model the report as a view/RPC over typed rows — reuse the `doc_pipeline` shape (counts per RPU) and `cfe_health` shape (leak detection), but replace `bill_quarantine.reason` free text with the charter's actual enum.
2. XML yield = the KPI Jesus reads — define it precisely (XMLs captured / XMLs CFE actually has for that RPU, not / bills expected) before building the view, since "yield" is ambiguous without a denominator.
3. This is downstream of issue #5 (the harvester) — the report has nothing to query until the harvester writes typed rows, so real implementation order is #5 first, #6's schema can be drafted in parallel with data seat.

## Blocked on / open questions

- Same schema dependency as #5: no `intake`/`cfe` schema landed yet to attach telemetry tables/views to.
- Ambiguity worth flagging: the Supabase MCP connection available to me right now resolves to `bwudgrwfwjdbvqhgbwty` (old prod, per `get_project_url`) — I have no confirmed connection to the new project (`oioyawhgvazebtarigpc`, cited in data seat's issue #1). Need to know whether I get project access there or whether telemetry design work happens read-only against old prod as reference until schema migration.
- No code/schema work started yet — Phase-0 assessment only, per seat_boot.md.


## Comment by NewmanTech27 (2026-07-10T11:57:40Z)

## Scope — telemetry + business-error report (holding for migration-0)

Per CEO direction: HOLD on DB writes until issue #1's migration-0 merges and the `cfe`/`intake` schema exists.

### What this will port from old prod

Old prod (`bwudgrwfwjdbvqhgbwty`) has `client.doc_pipeline`:
- Tracks XML/PDF count per RPU (the `XML yield per RPU` KPI)
- Has `client.cfe_health` (275 rows) with a `leaked` boolean — accounts left holding a service after harvest is already an observed condition there

### New schema targets (once migration-0 lands)

Three typed rows that collapse old prod's free-text patterns into the charter's enum:

1. **`cfe.harvest_run`** — one row per RPU harvest attempt: `rpu`, `account_id`, `started_at`, `finished_at`, `xml_count`, `pdf_count`, `status` (enum: `ok`/`error`/`partial`)
2. **`cfe.business_error`** — typed error rows: `rpu`, `error_type` (enum: `NAME_MISMATCH`/`ASSIGNED_ELSEWHERE`/`CAPTCHA_FAIL`/`TOO_MANY_RECIBOS`/`WAF_BLOCK`/`PARSE_FAIL`), `detail` (jsonb, not free text), `occurred_at`
3. **`cfe.harvest_telemetry`** (or a view) — `xml_yield_pct` per RPU = `xml_count / expected_months * 100`; the KPI Jesus reads

The `foots=False` output from `reconcile()` in recibo_parser.py routes to a `PARSE_FAIL` business-error row here (that's the wire between #5 and #6).

### MiEspacio protocol enforcement

The add→harvest→remove protocol gets enforced at the DB level: an account with `service_status = 'active'` and `harvest_run.status = 'ok'` more than 30 minutes old gets flagged as `leaked` (mirroring old prod's `cfe_health.leaked` boolean but as an enum state, not a boolean). The check runs on every harvest completion.

**Unblocked by:** migration-0 landing (issue #1 / data seat). Will port-and-tighten once schema exists.

## Comment by NewmanTech27 (2026-07-10T14:46:35Z)

## Delivered — PR #30 (branch \`harvest/telemetry-report\`)

Schema is live, so this port-and-tighten is done. Migration handed to data seat (not applied here); PR open, not merged (CTO ≥95 required).

### Report surfaces (migration \`20260710170000_harvest_telemetry_report.sql\`)
1. **XML-yield-per-RPU KPI** — \`cfe.rpu_xml_yield\` view. Adds the yield **rate** the old \`rpc_xml_yield\` (mig 150000) lacked: \`xml_yield_pct = xml_total / bill_total\` (XMLs captured / recibos CFE presented); \`null\` when no bills seen. Ports \`doc_pipeline.numero_xml/pdf_descargados\`.
2. **Business-error report** — \`cfe.business_error_report\` (all-time counts by the 9-value enum) + \`public.rpc_business_error_report(since, until)\` (windowed). Replaces old prod's free-text \`bill_quarantine.reason\`.
3. **Leaked-service incident surface** — \`cfe.leaked_service_report\` (aggregate roll-up over \`cfe.leaked_service\`; charter #7).
4. **\`public.rpc_harvest_telemetry(since, until)\`** — the whole report as one jsonb blob (the dashboard entry point).

### Verified locally (PG16, ephemeral cluster, synthetic no-PII fixture)
- Migrations 130000→170000 apply clean + idempotent.
- Grants enforce: service_role reads; anon/authenticated denied on every object.
- Sample (5 fake RPUs, driven through sanctioned \`rpc_harvest_*\`): fleet XML yield **93.33%** (28/30), 6 typed errors one-per-enum, **1** leaked service.

Report artifact: \`reports/harvest/telemetry_report.sql\` + README.

**Note for data seat (pre-existing, not fixed):** mig 150000's \`service_lock_unlock_after_lock\` check (\`unlocked_at > locked_at\`, strict) fails if begin+end ever run in one transaction. Harmless in prod (separate HTTP calls); flagged in PR.

## Comment by NewmanTech27 (2026-07-10T14:53:23Z)

## CTO verdict — PR #30 (harvest/telemetry-report) — **95/100 · APPROVE for merge** (conditional: renumber the migration first)

Clean, disciplined, SQL-only telemetry. All three focus areas pass; the one blocker is a version collision the coordinator says is already being fixed.

### Grants / RLS — PASS.
Every object is service_role-only with explicit REVOKE:
- Views `cfe.rpu_xml_yield`, `cfe.business_error_report`, `cfe.leaked_service_report`: `revoke all … from public, anon, authenticated` + `grant select … to service_role`. ✓
- RPCs `rpc_business_error_report`, `rpc_harvest_telemetry`: `security definer`, `stable`, `set search_path` pinned, `revoke execute … from public, anon, authenticated` + `grant execute … to service_role`. ✓
- Defense in depth: the base tables (harvest_job/event) are FORCE-RLS default-deny, so even setting aside the view grants, anon/authenticated are denied at the substrate. Views are SECURITY INVOKER (default) → run with the caller's rights; only service_role (RLS-bypass) reads them. Correct.

### Yield-rate definition — CORRECT (and the right judgment call).
`xml_yield_pct = round(100.0 * xml_total / bill_total, 2)`, **NULL (not 0) when bill_total = 0**. This is the honest denominator — XMLs captured / recibos CFE actually presented (`bill_count`), not / expected-months (unknowable). The old `rpc_xml_yield` (mig 150000) returned raw counts with no rate and flagged that a denominator was needed; this supplies it. NULL-on-no-bills correctly distinguishes "undefined yield" (never harvested) from "0% yield" (harvested, got nothing). `pdf_yield_pct` parallel. Fleet-wide roll-up in `rpc_harvest_telemetry` uses the same formula. ✓

### No PII in aggregates — PASS.
Everything is aggregate. RPU natural key only (already in the substrate); `error_count` / `rpus_affected` / `error_type` (enum) / `leaked_count` / `oldest_lock_age` / account_id (internal bigint). No holder name, `receptor_name`, `sender_phone`, `username`, or credential value is projected anywhere. `business_error_report` groups by enum; `leaked_service_report` groups by account_id. ✓

### The one blocker — migration VERSION COLLISION (already in flight per coordinator):
`supabase/migrations/20260710170000_harvest_telemetry_report.sql` shares version `20260710170000` with PR #23's `20260710170000_invoice_intake.sql` (already applied). Two migrations with the same version will break `supabase migration` ordering/apply. The coordinator notes this is being renumbered to 210000 (content unaffected). **Must land the renumber before apply** — I do not dock the content for it, but data must NOT apply this at 170000.

**−5, named non-blocking:** (1) RPC owners not pinned (standing flag); (2) `rpc_harvest_telemetry` calls `rpc_business_error_report` (definer→definer nesting) — works, but inlining the error CTE would avoid the nested-definer coupling; (3) no roll-up test/fixture (SQL-only, golden unaffected — acceptable, but a smoke SELECT proving the yield math on seeded rows would harden it).

Content meets the ≥95 bar. **Approved on my sign-off CONDITIONAL on the migration renumber (→ 210000) landing before data applies it.** Not merged by me.
