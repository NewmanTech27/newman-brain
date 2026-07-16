# Newman CRM ("Tuesday") — Executive Comparison & Roadmap

> Produced by a 10-agent review committee (2026-07-08): a repo scout, three
> researchers (Twenty, OSS CRMs, energy-PF/EPC/due-diligence domain), five expert
> reviewers (CRM parity, project-finance underwriting, EPC delivery, KYB/due
> diligence, data/AI architecture), and a synthesizing chair. Focus: what an energy
> company that **finances and EPCs** commercial solar/BESS in Mexico needs, with
> **company due diligence** as the priority.

## Verdict

Newman is not a horizontal CRM — it is a deep, defensible vertical slice that already beats Twenty and every OSS peer on the things that matter to a Mexican solar/BESS financier-EPC: live CFE Consulta RPU validation, WhatsApp+OpenRouter bill OCR, a to-the-cent financial model baked into `crm.deal_line_item_calc`, and full `crm.*` schema/RLS control. But it is a **pre-signature sales CRM with no counterparty golden record, no KYB/credit gate, no post-signature EPC lifecycle, and org-wide `using(true)` RLS** — meaning today a deal can travel `lead → in_signing → closed` against an unverified RFC with confidential VPN/NPV figures readable by every authenticated user. The strategic move is not to chase Twenty's breadth; it is to build the **entity-risk graph + stage-gate engine** on the existing Supabase stack, because Company Due Diligence is the single control that governs whether capital is safe to deploy.

## Capability Matrix — Newman vs Twenty vs EspoCRM (best OSS peer)

| Capability area | Newman ("Tuesday") | Twenty v2.1 | EspoCRM |
|---|---|---|---|
| Custom objects / relations | ❌ (custom *fields* on Contacts + jsonb only) | ✅ (unlimited, no-code) | ✅ (Entity Manager) |
| Views / reporting | 🟡 (1 Kanban + regex filter; no saved/table views) | ✅ (table+Kanban, filter/sort/group, saved) | ✅ |
| Automation / workflow | ❌ (hand-wired integrations) | ✅ (record/schedule/webhook triggers) | 🟡 (approval BPM) |
| API / webhooks | 🟡 (hand-built RPCs; PostgREST/pg_graphql latent) | ✅ (auto GraphQL+REST + signed webhooks) | 🟡 (REST) |
| Permissions | ❌ (org-wide `using(true)`; role enum unused) | ✅ (RBAC, field+row level, SSO, 2FA) | ✅ (per-record roles + portal) |
| Document / data-room | 🟡 (flat Storage attachments, signed URLs) | ❌ (no portal/versioning) | ✅ (versioned + partner portal) |
| KYB / due-diligence | ❌ (free-text `account.rfc` only) | ❌ | ❌ (all require Sumsub/ComplyAdvantage API) |
| Project / EPC mgmt | ❌ (pipeline dead-ends at `closed`) | ❌ (Kanban only) | 🟡 (custom module) / Odoo ✅ |
| Energy underwriting | 🟡 (EPC value + partial NPV; no IRR/DSCR/LCOE) | ❌ | ❌ |
| AI / OCR | ✅ (CFE bill OCR, invoice scan, AI research) | 🟡 (agents, no doc-RAG) | ❌ |
| Mobile | 🟡 (responsive web) | 🟡 (responsive web) | 🟡 |

Newman leads on the four domain-specific rows no competitor touches; it trails on the five generic-platform rows Twenty gives for free.

## What Newman Is Missing, by Theme

**Trust & access control (blocking, high).** Org-wide `using(true)` RLS with an unused admin/member/guest enum. Nothing external — lender, investor, client — can be let in, and every VPN/NPV figure is globally readable. This gates the entire roadmap.

**The entity-risk graph (high).** No first-class Counterparty/SPV/Asset/Permit objects, no UBO chain, no risk score. Everything downstream (DD, underwriting, EPC supplier, data-room) needs one golden record that today can only be a hand-written migration per entity.

**Due diligence & compliance (high).** No RFC/SAT validation, no Lista 69-B/69 screening, no sanctions/PEP, no credit pull, no DD checklist that hard-blocks stage progression — the most important control in a financing business is entirely absent.

**Underwriting depth (high).** The model computes EPC value + a partial NPV from **hardcoded SQL constants** (including a live 12%-vs-10% discount-rate bug), no IRR/DSCR/LCOE, no scenario/sensitivity versioning, no debt sizing. Validated CFE consumption (`rpu_coverage`) — Newman's moat — is never wired into the model.

**EPC delivery (high).** Pipeline ends at `closed`; `ops_report/expense/budget_line` are UI-less Monday stubs. No project entity, milestone/Gantt, CFE interconnection tracker, permit board, BOM/serials, or commissioning sign-off.

**Automation & collaboration (medium).** No workflow engine, no tasks/@mentions/notifications, no re-screening scheduler, read-only assistant.

**Platform hygiene (medium).** Dual `deal.rpu` vs `deal_rpu` source of truth; no auto-API/webhooks; no doc store/embeddings/RAG; no persisted, sourced enrichment records for audit.

## Deep Dive — Company Due Diligence

### Proposed DD data model (`crm.dd_*`)

- **`crm.counterparty`** (golden record, supersedes free-text `account.rfc`): `legal_name` (razón_social), `rfc`, `entity_type` (persona_moral/fisica), `roles[]` (client|offtaker|supplier|epc_sub|investor|spv), `folio_mercantil`, `notario_ref`, `incorporation_date`, `domicilio_fiscal`, `scian_code`, `dd_status` (not_started|in_progress|cleared|blocked), `risk_score` (0–100), `risk_tier` (A/B/C/D), `last_screened_at`, `next_review_at`.
- **`crm.dd_representative`** (poderes): `name`, `curp`, `poder_type` (general|pleitos_cobranzas|actos_admin|dominio), `notario_ref`, `verified`, `evidence_doc_id`.
- **`crm.dd_ubo`** (self-referential ≥25% graph): `owner_person|owner_counterparty_id`, `pct_ownership`, `control_type`, `is_pep`, `screening_id`.
- **`crm.dd_check`** (the gating checklist row): `check_type` (rfc_sat|efos_69b|firmes_69|sanctions_ofac|un_eu|pep|adverse_media|credit_bureau|litigation|ubo|acta_review|poder_review|esg), `status` (pending|pass|fail|waived|manual_review), `blocks_stage`, `source`, `evidence_doc_id`, `performed_by`, `performed_at`, `expires_at`.
- **`crm.dd_screening_hit`**: `list_name`, `matched_name`, `match_score`, `category`, `disposition` (true_match|false_positive|discounted), `reviewed_by`.
- **`crm.dd_credit_report`**: `bureau` (buro|circulo|dnb), `consent_id`, `score`, `dscr_inputs jsonb`, `report_doc_id`.
- **`crm.dd_consent`** (legally mandatory — MX entity pulls its own report): `purpose`, `signed_by`, `method` (mifiel|docusign), `obtained_at`.
- **`crm.dd_document`** (versioned/permissioned data-room): `doc_type` (acta|poder|constancia_rfc|estados_financieros|ppa|permit|insurance), `version`, `storage_path`, `expiry_date`, `classification`, `role_scope`.
- **`crm.dd_event`** (immutable append-only audit, separate from `deal_event`): `actor`, `action`, `before/after jsonb`, `at` — for auditor/lender defensibility.

### Workflow — stages, checks, scoring, audit

Onboarding creates a `counterparty` → mandatory `dd_check` rows are auto-generated by role. **Stage-gate rule:** `crm_web_change_deal_stage` (the existing audited RPC) refuses to advance a deal past `docs`/`in_signing` unless every mandatory `dd_check` for the linked counterparty is `pass`/`waived` **and** no undisposed `true_match` `screening_hit` exists **and** an `ic_decision` is approved. Scoring: a weighted aggregation edge function rolls check results into `risk_score`→`risk_tier`; `pg_cron` re-runs sanctions/EFOS/credit per tier cadence (CNBV Art. 115 continuous monitoring), writing fresh `dd_check` rows and firing expiry tasks on `dd_document.expiry_date`. Every mutation appends to `dd_event`.

### Named data sources / APIs

- **SAT:** Verificación masiva de RFC (bulk ≤5,000 IDs) + **Lista 69-B EFOS** + **Lista 69** debtors (free CSV via DOF), wrapped through Apify "Verificador RFC Mexico" or Signzy KYB.
- **Corporate existence:** Registro Público de Comercio / SIGER (folio mercantil), RUG (liens), DOF publications, RENAPO/CURP.
- **Credit (consent-gated):** Buró de Crédito (TransUnion MX), Círculo de Crédito (FICO), D&B México.
- **Sanctions/PEP/adverse-media:** ComplyAdvantage or Dow Jones Risk & Compliance, LexisNexis WorldCompliance, Sumsub, OpenSanctions (OFAC SDN, UN, EU, UIF/SAT PPE).
- **Litigation:** state Tribunales Superiores boletines, federal CJF/PJF, SISET.
- **Offtaker validation:** CFE Consulta (already wired) for RPU/tariff feeding underwriting.
- **e-sign:** Mifiel (firma electrónica MX) / DocuSign for consent and poderes.

### Wiring into the current stack

Each provider becomes a Supabase **edge function** invoked by an authenticated `crm_web_run_dd_check(counterparty_id, check_type)` SECURITY DEFINER RPC — mirroring the `crm_web_validate_rpu` → `request_collection` pattern. The function calls the provider REST API, writes the `dd_check` + `dd_screening_hit` rows, uploads evidence to Supabase Storage, and appends to `dd_event`. **OpenRouter** (already in `whatsapp-intake` and `assistant`) OCRs actas/poderes/financials into structured `dd_document.ocr_json` and, extended with **pgvector**, powers "ask across all contracts." Every LLM/API pull routes through an `enrichment` record (`model`, `prompt_hash`, `source`, `confidence`, `retrieved_at`) so IC/lender audit trails are provable. Read views (`crm_dd_*`, `security_invoker`) inherit the new per-role RLS.

## Roadmap

**NOW (foundation — nothing external is safe until these land)**
- Per-owner/role RLS replacing `using(true)`, keyed on the existing enum + `owner_id`; read-only guest/investor scope. **[L]**
- `crm.counterparty` golden record; migrate `account.rfc` into it; collapse `deal.rpu` into `deal_rpu`. **[M]**
- SAT RFC + Lista 69-B/69 as the first `dd_check` (cheapest, highest-leverage MX control). **[M]**
- `crm.deal_financials` assumptions table replacing hardcoded constants (fixes the 12%-vs-10% bug); IRR/DSCR/LCOE metrics engine writing back to the deal. **[M–L]**
- Deal table view with multi-condition filter/sort/group + saved views (reuse `crm_pipeline`). **[M]**

**NEXT (the differentiators)**
- `dd_check` engine + hard stage-gate on the audited RPC; sanctions/PEP + UBO graph + consent-gated credit pull. **[L]**
- CFE tariff/consumption model (GDMTH kW, Base/Intermedio/Punta, factor de potencia) populated from `rpu_coverage` + bill OCR → underwriting inputs. **[M]**
- `crm.project` EPC lifecycle entity + CFE interconnection status board. **[M]**
- Declarative workflow engine (stage-gate/schedule/expiry) + tasks/@mentions on `deal_comment`/`deal_event`. **[M–L]**
- Expose `crm.*` via PostgREST/pg_graphql + signed webhooks (post-RBAC). **[M]**

**LATER**
- Permissioned data-room with versioning/expiry + Mifiel e-sign; milestone/Gantt + commissioning sign-off gate; debt-sizing module; `pg_cron` re-screening; litigation worker; Metabase portfolio dashboards; PWA field capture. **[S–L]**

## Build on Twenty vs Keep Bespoke — Recommendation

**Keep bespoke.** Newman's entire value — CFE Consulta integration, the reconciled financial model, WhatsApp+OpenRouter OCR, RFC/69-B/credit connectors, and the stage-gate that hard-blocks on failed KYB — is exactly what Twenty and every OSS peer *do not* ship and would force you to build anyway, while adopting Twenty means inheriting its metadata model and AGPL and giving up direct control of the Supabase `crm.*` system of record. Twenty's real advantages — custom objects, saved views, RBAC, auto-API/webhooks — are all cheaply replicable on the stack you already run (a lite metadata layer, PostgREST/pg_graphql, enum-keyed RLS). The one defensible option is a **thin spike**: evaluate Twenty purely as an object/API/RBAC *backbone* federated behind Supabase-as-financial-system-of-record — but only if the custom-object framework proves expensive to hand-roll. Default to bespoke; the moat is the energy-PF entity-risk graph, and that is yours to own.
