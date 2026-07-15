# #118: Market data plane: CFE tariffs + CENACE PML (P3 backfill + live batch extraction via pg_cron)

- State: OPEN
- Created: 2026-07-12T17:59:48Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/118

## Body

## Context

Old prod (`bwudgrwfwjdbvqhgbwty`) holds the market-data plane the rebuild still lacks:

- `cenace.pml` — 18.2M rows, monthly partitions, 2016-02 → 2026-07 (zona-level MDA/MTR)
- `cenace.pml_nodo` — 807K rows, 2025-06 → (node-level)
- `cfe.tariff` — 27.6K rows, 2019-01 → 2026-06 (acuerdo tarifas, DOF/CENACE PDFs)
- `cfe_raw.tariff_rate_geo_legacy` — 14.4K rows, 2024 (app.cfe.mx state/municipio rates; scraper source lost)

`old_prod_migration_map.sql` explicitly deferred `cenace.*` to P3 — this issue is that P3, plus live batch extraction going forward.

Extraction logic to port: `newman-architecture/agents/market-loaders/{pml.py,tariffs.py}`. CENACE WS limits: ≤20 nodos, ≤7 days per request. WAF note: app.cfe.mx passes from the mini (residential IP); DOF/CENACE mirrors remain the source for anything not running on the mini.

## Design

Same proven pipeline pattern as `pipeline.*`: work-queue table `market.fetch_job` (dedup_key-idempotent seeders), claim via `FOR UPDATE SKIP LOCKED` (batch claim — HTTP fetches are cheap, unlike browser stages), advance/fail RPCs with backoff, reaper, mini executor route `POST /pipeline/market`, pg_cron driving ticks through the tunnel. Cron ships in a migration, gated per env by `pipeline.config` key `market_cron_enabled` (first cron-in-migration; pattern for #68).

## Phases

- [ ] **P3.1 schema** — `market.pml` + `market.pml_nodo` (monthly range partitions + ensure-partition fns), `market.nodo_zona`, `market.cfe_tariff`, `market.cfe_tariff_geo`, jsonb upsert RPCs
- [ ] **P3.2 queue** — `market.fetch_job` kinds `pml_zona|pml_nodo|tariff_month|tariff_geo|nodo_catalog`; claim/advance/fail (per-kind attempt caps: 8 general, 30 tariff_month w/ 1-day backoff), seeders (`rpc_seed_market_jobs`, `rpc_seed_market_daily`, `rpc_seed_tariff_month`, `rpc_seed_market_refresh`), `rpc_reap_stale_market`
- [ ] **P3.3 loader** — stdlib-only `harvest/market_loader.py` child (stdin job → stdout result): CENACE WS fetch + zona aggregation, DOF/CENACE tariff PDF parse (`pdftotext`), app.cfe.mx geo tariffs via cfe_bridge, NodosP CSV catalog
- [ ] **P3.4 executor** — `POST /pipeline/market` in `pipeline_endpoint.py` (batch claim, subprocess isolation, retry_in passthrough)
- [ ] **P3.5 cron** — migration: `market-tick` (3-58/5), `market-seed-daily` (07:15), `market-seed-tariff` (day 8), `market-refresh-hourly` (:45 — newest incoming hours), `market-reaper` (*/15); all flag-guarded
- [ ] **P3.6 tests** — manifest/parse golden tests, zona aggregation, chunking, endpoint claim/advance/fail
- [ ] **P3.7 backfill** — `supabase/market_backfill_map.sql`: FDW per-month bounded transactions with count assertions (18.2M + 807K + 27.6K + 14.4K rows), resumable
- [ ] **P3.8 rollout** — dev (full pipeline + 48h cron soak) → staging (schema only) → prod (backfill + flag flip)

## Post-merge ops (not in PR)

- Run backfill from droplet (`vault-env` psql, readonly_migrator FDW)
- Seed `pipeline.config` per env; flip `market_cron_enabled`
- One-shot `nodo_catalog` job (NODOSP_CATALOG CSV)

