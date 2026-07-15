# newman-rebuild: Twilio→Consulta→MiEspacio harvest phases + auto-deploy

**Summary**: Reviewed and hardened the newman-rebuild schema pipeline for the Twilio→Consulta→MiEspacio 30-XML harvest, fixed the WAF-reach "agregar" blocker live in prod, and shipped a launchd auto-deploy poller on the mini.
**Tags**: #newman #cfe #scraper #warehouse #agents
**Created**: 2026-07-14
**Source**: macbook session 1e0e264d-1359-4636-8583-9b6b185a59ef.jsonl, user jesus

---

## Content
- Only fully-clean flow: **RPU 965951103875** — twilio extracted → consulta derived → mi_espacio harvested; drain pulled 73 XMLs, invoice-only filter + (rpu, period) dedup → 30 unique XML invoices in `raw_cfe.mi_espacio`, 2024-01 → 2026-06, one attempt, 317 s, no leak.
- Gotcha: Consulta failed for many RPUs because it needs the razón social (name), not just RPU. On MiEspacio the número de servicio can be left in the account (deleted in later rounds).
- Blocker fixed: WAF-reach on the "agregar" step — earlier failures were selector timeouts (`#ctl00_MainContent_txtRpu`), later proven cleared live (RPU 780020900569 went pending→harvesting→partial "SUCCESS past agregar → drain reached").
- Considered WAF-reach + remote-download best practices; option to copy XML as a string dump into raw_cfe.
- Strategic answer: **SAT descarga masiva can't replace the harvest** — the needed data lives in CFE's CFDI Addenda, not SAT — saving a wrong rebuild.
- Shipped ~6 PRs dev→staging→prod, all verified. #141 auto-deploy closed & live (`ffcefad`): launchd poller `com.newman.pipeline-deploy` every 180s fast-forwards the executor worktree to origin/main and restarts the endpoint, **deferring if a harvest is in flight** (leak-safe); `/pipeline/health` exposes running rev. #142 cross-env crons re-scoped/fixed.
- System now self-heals: auto-deploy (no more 51-commit drift), leak requeue, non-fatal consulta-refresh. 12 RPUs harvested with real CFDI data.

## Related Notes
- [[2026-07-07-cfe-miespacio-harvest-pseudo-api]]
- [[2026-06-26-cfe-warehouse-schema-supabase]]
