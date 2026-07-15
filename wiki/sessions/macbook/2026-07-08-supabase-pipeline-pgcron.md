# Supabase as orchestrator: pipeline table, pg_cron backfill drain, MiEspacio logic

**Summary**: Made Supabase the pipeline orchestrator — bucket-triggered pipeline table with OCR-derived idempotency key, pg_cron 5-min backfill monitor replacing the mini loop, Consulta+MiEspacio drain rules, and a clean bucket sanity sweep.
**Tags**: #newman #supabase #pgcron #cfe #pipeline #devops
**Created**: 2026-07-08
**Source**: macbook session d5eec5c6-b971-4612-93fb-c5667ea169cf.jsonl, user jesus

---

## Content
- POC confirmed: Supabase edge functions can call OpenRouter directly (openrouter-ping fn later deleted).
- Built a `pipeline` table triggered when a document lands in the bucket: upserts keyed on idempotency key = rpu + razon_social from OCR + numero_xml_descargados + numero_pdf_descargados; supports renaming the bucket document.
- Orchestration decision: NO polling loop on the mini — a pg_cron on Supabase every 5 min monitors invoices per RPU (<12 or zero) and triggers the mini one-shot drain (logic-bus pattern); mini deployed via the deploy-mini GitHub Action (PATH fix needed).
- Secrets moved from an `app_secrets` table to Supabase env/secrets function; user migrated them.
- Drain rules (PR #5, `fetchDrain` in harvest.js): both Consulta and MiEspacio drains use the pseudo-API postbacks; MiEspacio brings up to 12 invoices, but if ≤12 result, run the harvest on BOTH Consulta and MiEspacio.
- Referenced the CFE Consulta Drain clean-room spec: Imperva WAF needs headless Chrome with automation flags hidden + residential (mini) IP — datacenter IPs always dropped, so GitHub-hosted CI can't run it.
- Client-schema sanity check requested (pruning bucket + re-extracting from scratch acceptable).
- Sweep finding: suspicious 15.6MB `unidentified_MM8427...pdf` in the bucket turned out to be the fully-processed 168-page test statement (`bulk_pdf` id=1, status=done, 69 bills enqueued — the YAZAKI/ARNECOM/FIDEICOMISO seed); no data lost, all extraction surfaces clean.

## Related Notes
- [[2026-07-07-whatsapp-intake-cutover]]
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
- [[2026-07-06-pml-supabase-migration]]
