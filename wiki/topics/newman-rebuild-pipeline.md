# newman-rebuild Pipeline (clean-room v2)

**Summary**: The clean-room v2 rebuild — the Supabase-orchestrated invoice→PPA pipeline, its architecture (Twilio→OCR→Consulta→MiEspacio→engine→offer→CRM), the auto-deploy/self-heal machinery, and the repo/branch governance.
**Tags**: #newman #rebuild #cfe #supabase #pipeline #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Architecture
- End-to-end: invoice upload (WhatsApp/Twilio or direct) → OCR extraction → CFE Consulta → MiEspacio harvesting → sizing via the newman-brain engine → PPA quotation → DEALS CRM. **Every step is observable in Supabase; every failure is a typed row, not a log line.**
- Clean-roomed agents (newman-architecture): `cfe-collector` (Consulta lane detection, BÁSICO→`upsert_bill`, CALIFICADO→`store_bulk_bill`, `eliminar_servicio` cleanup), `market-loaders`, `design-engine` (deterministic max-NPV sweep).
- Harvest chain (traced via Graphify): scheduler `run_once()` claims dispatched RPUs (`rpc_claim_dispatched`, limit 5) → `CfeDriver` returns a plain `DriveResult` → `_apply_drive_to_job()` → `process_recibo` → `parse_recibo` → `reconcile` → `split_populated`. All writes funnel through one choke point `HarvestDB._rpc()` (callers: begin/event/end + parser hand-off). `recibo_parser.py` wraps the vault golden engine `cfe_savings.extract.parse_bill` (no math re-derivation) + a foot check `(Σ MEM importes + bonif_FP)×(1+IVA)` vs printed Facturación — unreconciling bills → typed `PARSE_FAIL` rows.

### Orchestration
- Supabase is the orchestrator: a bucket-triggered `pipeline` table with an OCR-derived idempotency key (rpu + razon_social + numero_xml/pdf_descargados); a **pg_cron every 5 min** monitors invoices per RPU (<12 or zero) and triggers the mini one-shot drain (logic-bus pattern — NO polling loop on the mini). Mario's savings engine also runs as pg_cron writing per-RPU offers toward `client.calculo`.
- Envs: dev / staging / prod on newman-rebuild; prod Supabase **oioyawhgvazebtarigpc** (us-east-2). Deploy staging-first, promote when green.

### Self-heal / deploy
- launchd poller `com.newman.pipeline-deploy` every 180s fast-forwards the executor worktree to origin/main and restarts the endpoint, **deferring if a harvest is in flight** (leak-safe); `/pipeline/health` exposes the running rev. Killed the old 51-commit drift.
- Golden gate (branch protection enforced) blocks merges below peso-exact baseline. #109 branch-stack merge unified a two-way fork (executor code on `pipeline/executors` vs live migrations on `pipeline/schema`).

### Repo state (3-day-old at audit)
75 issues (56 open/19 closed) 07-10→07-12; PRs 14 merged. Working worktree `/Users/jesuslopez/newman-rebuild-wt-drive`. Codebase graphed with Graphify (`~/newman-rebuild/graphify-out/`, `graphify query`/`update`).

## Related Notes
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
- [[2026-07-08-supabase-pipeline-pgcron]]
- [[2026-07-09-agent-org-ceo-cto]]
- [[2026-07-14-newman-rebuild-miespacio-phases]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-12-graphify-codebase-graph]]
- [[2026-07-12-rebuild-repo-audit-readme-issues]]
- [[2026-07-12-market-data-migration-plan]]
- [[2026-07-15-mario-engine-client-calculo]]
- [[2026-07-07-cfe-miespacio-harvest-pseudo-api]]
