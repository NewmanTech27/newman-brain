# Warehouse migration: 18.1M zona PML rows (and 45M node rows) mini → Supabase

**Summary**: Migrated the full CENACE zona PML history (18.2M rows, 2016-02→2026-07) from the mac mini to Supabase Pro via a resumable month-chunked stream, started the 45M-row node PML mirror, and stood up the daily freshness watcher.
**Tags**: #newman #warehouse #cenace #supabase #pml #migration
**Created**: 2026-07-06
**Source**: macbook session 2b570ab9-da26-4c25-87e5-50ab00068c5c.jsonl, user jesus

---

## Content
- Trigger: Supabase Pro subscription became available; migrate the mini warehouse (`newman_wh`) datasets and verify gdmth/gdmto/pml completeness/freshness.
- Zona PML: `migrate_pml_chunked.sh` (month-chunked, resumable, skips done months, re-run on FAILED) streamed ~18.2M rows into Supabase `cenace.pml`, span 2016-02 → 2026-07-06. DB size 3.3GB (Pro includes 8GB).
- Node PML: mirrored mini `newman.mx_pml_nodo` (45.58M rows) into Supabase `cenace.pml_nodo`, partitioned monthly with hot-year partitions, streamed via TARGET_DSN pooler using the same chunked pattern.
- Daily watcher live: single cron; zona mx_pml caught up Jun 23 → Jul 6 (66k rows); domestic tariffs at 2026-12 in both instances; business tariff stuck at 2026-06 (July acuerdo not harvested — loud-flagged).
- Gotcha fixed: partition-drop vs migration conflict (`PML_KEEP_HISTORY=1`).
- `client.contact` refactored to one-row-per-client with `rpus[]` (5 clients, 126 RPUs) — breaking rename from singular `contact.rpu`.
- Open decisions left: RLS policies on 5 anon-exposed `client.*` tables; grep newman-agents for old rpu usage; harvest the July business-tariff acuerdo.

## Related Notes
- [[2026-06-21-newman-agents-founding]]
- [[2026-07-08-supabase-pipeline-pgcron]]
