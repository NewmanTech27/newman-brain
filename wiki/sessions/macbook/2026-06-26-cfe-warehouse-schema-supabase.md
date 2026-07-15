# CFE data warehouse: source-namespaced schema + Supabase + PML backfill

**Summary**: Did EDA on a CFE DB dump plus the mini scrapers, redesigned the warehouse into source-namespaced schemas (cfe/cenace/cre...), deployed to Supabase, and stood up a daily PML refresh + 9-year historical backfill.
**Tags**: #newman #cfe #warehouse #scraper
**Created**: 2026-06-26
**Source**: macbook session 6e48d473-8167-4676-a77a-bd3fadd374c6.jsonl, user jesus

---

## Content
- Read a `.gz` DB backup; ran professional-data-scientist EDA over the dump + existing mini scrapers.
- Restructured data into source-level schemas (cfe, cenace, cne, etc.) so data extracts by source; pruned faulty/useless tables.
- Phase 1 migration run on the mini Postgres (full warehouse migration completed in background).
- Deployed to Supabase project **bwudgrwfwjdbvqhgbwty** (publishable key sb_publishable_lWEw8BChPqmeqZlxU8q2pw_l8FhBBft); linked via CLI, db pwd provided.
- Discussed CFE tariff codes (GDMTH, GDMTO counts) and pulling exact official definitions from the acuerdo legend page.
- PML node pipeline:
  - **Daily cron** `pml_nodo_daily.sh` @ 8:15 AM — fetches last 3 days (MTR settles late), all nodes/markets → Postgres.
  - **Historical backfill** 2016-02 → 2025-06, both markets, all 2,603 nodes → compressed Parquet (zstd) at `~/newman-data/pml_nodo_history/*.parquet`, ~5GB full, resumable per-month.
- Gotcha: **CENACE throttles sustained automated load** — 6 workers @ higher rate triggered a throttle-stall (0% CPU, 0 network); restarted gentle at 3 workers @ 2/s (9.7% CPU, 3 TCP conns) for a stable multi-day grind.
- Dashboard: lopezpalacios.github.io/newman-warehouse-dashboard with a Historical-archive panel (rows/months/files/progress via mini 10-min cron + DuckDB).

## Related Notes
- [[2026-06-27-newman-data-api-fastapi-mini]]
- [[2026-07-07-cfe-miespacio-harvest-pseudo-api]]
