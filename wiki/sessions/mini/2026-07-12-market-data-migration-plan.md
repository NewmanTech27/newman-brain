# CFE tariff + CENACE PML market-data extraction migrated into newman-rebuild with pg_cron batching

**Summary**: Planned and started implementing the migration of the legacy CFE price/PML scraping logic (legacy Supabase bwudgrwfwjdbvqhgbwty) into newman-rebuild on the mini — new `market.pml` / `market.pml_nodo` tables reusing old-prod column names for 1:1 FDW backfill, pg_cron batch extraction, loader + endpoint tests (41 passing).

**Tags**: #newman #rebuild #cfe #pml #cenace #scraper #supabase #pg_cron #migration
**Created**: 2026-07-12
**Source**: mini session 783fb9e5-5d1c-47b1-963e-dac7dec4d7ee.jsonl, user jesus

---

## Content
- Ask: migrate the legacy CFE price-extraction logic ("cfe-scrapper" repo) from the legacy Supabase project **bwudgrwfwjdbvqhgbwty** into the mini/newman-rebuild, covering both PML and CFE tariffs; revise the cfe schema, plan the redesign, and batch extraction with **pg_cron**.
- Gotcha: `NewmanTech27/cfe-scrapper` does not exist on GitHub — the actual reference is **isaacasancheza/cfe-scraper** (Python 3.13 CFE tariff scraper, created 2024-04-22); a second reference, cfe-gd-scraper (Python 3.11+, pandas/requests/playwright-for-API-rediscovery), was also analyzed.
- Working copy of the rebuild repo: `/Users/jesuslopez/newman-rebuild-wt-drive` (worktree); key dirs: engine/, harvest/ (pipeline executor + intake worker), supabase migrations, CHARTER.md, CI.
- New-prod connection found at `/home/jesus/newman-review-build/newman-review.env` on the droplet: `postgresql://postgres.oioyawhgvazebtarigpc@aws-1-us-east-2.pooler.supabase.com:5432/postgres`.
- Legacy old-prod schema inventory (bwudgrwfwjdbvqhgbwty): `app`, `bess_raw` (23K+ documents), `cenace` (partitioned MEM data), `cfe`, `cfe_raw` (scrape logs + legacy tariff rates), `cre`, plus auth.
- Plan decision D1: reuse old-prod column names exactly — `market.pml` (sistema, zona, market, fecha, hora, pml_mxn, comp_energia, comp_perdidas, comp_congestion, fetched_at) and `market.pml_nodo` (clave_nodo, sistema, market, fecha, hora, pml, pml_ene, pml_per, pml_cng) — enabling a 1:1 insert-select FDW backfill.
- Jesus also asked to file the migration as a GitHub issue and PR the code.
- Implementation started in-session: loader tests + endpoint additions (TestMarket class) following the existing `_run_*` direct-call test pattern; **41 tests passing**; pg_cron bootstrap migration next.

## Related Notes
- [[newman-rebuild-project]]
- [[newman-warehouse-project]]
- [[cfe-tariff-backend-feed]]
- [[2026-07-15-mario-engine-client-calculo]]
