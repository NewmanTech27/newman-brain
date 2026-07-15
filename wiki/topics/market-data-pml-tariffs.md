# Market Data: CENACE PML + CFE Tariffs

**Summary**: The market-data layer — CFE tariff scraping from DOF/CENACE acuerdo PDFs, the decade-long CENACE PML backfill (18M zona / 45M nodo rows), schema doctrine (nodal grain + zona rollups), throttling gotchas, and the migration into newman-rebuild `market.*` tables.
**Tags**: #newman #cenace #pml #cfe #warehouse #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### CFE tariffs
- Source of truth = monthly DOF/CENACE acuerdo PDFs back to Dec 2018 (NOT app.cfe.mx, which is WAF-blocked); manifest → fetch → parse → load pipeline; ≤2023 PDFs have a different layout (parser variant pending). 98 PDFs parsed into mini Postgres `newman` (127.0.0.1:5433).
- Parser gotcha (2026-07-15): the VDM tariff page renders **3 labeled rate cards (Norte/Centro/Sur)** with distinct Fijo/B/I/P/Distribución but shared Capacidad — values must be attributed per card heading.
- Freshness watcher: domestic tariffs ahead (2026-12), business tariffs can lag (stuck at 2026-06 until the July acuerdo is harvested) — loud-flag staleness; add an explicit SLA (N days past expected DOF publish → escalate).

### CENACE PML
- Backfill: MDA+MTR, all 2,603 nodes, 2016-02 (MEM launch) → present; zona history ~18.2M rows, node history ~45.6M rows; Parquet (zstd) archive at `~/newman-data/pml_nodo_history/`.
- **CENACE throttles sustained load**: 6 workers stalled the job (0% CPU, 0 network); stable recipe = 3 workers @ 2/s for a multi-day grind. Chunk date loops ~31 days; MTR settles late, so the daily cron re-fetches the last 3 days.
- Scrape method: ASP.NET WebForms — GET for `__VIEWSTATE`/`__EVENTVALIDATION`, prefer direct CSV/ZIP endpoints, else POST the full form; save raw file stream, never parse HTML tables; select MDA vs MTR explicitly; validate node IDs against the NodosP catalog; handle hora 1–25 DST (codebase uses a 0–25 constraint, commit 4de998b).
- Schema doctrine (committee 8/10): store at **nodal grain** (~2,400 PNodos), roll up to zona de carga (~50) via MV — zona-only discards congestion signal that cannot be rebuilt. Enforce energia+perdidas+congestion=pml as a DB constraint; don't let clave_nodo double as nodo-or-zona without a grain discriminator.
- Silent-empty-scrape doctrine: 200 OK + zero rows is NOT success — post-load row-count/schema gates, baseline-deviation math, idempotent upsert on period key, checkpoint/resume.

### Homes
- Legacy: mini `newman_wh` → Supabase **bwudgrwfwjdbvqhgbwty** (`cenace.pml`, `cenace.pml_nodo` partitioned monthly). Migration was month-chunked + resumable (`migrate_pml_chunked.sh`); `PML_KEEP_HISTORY=1` avoids the partition-drop conflict.
- New: newman-rebuild `market.pml` / `market.pml_nodo` reuse the old-prod column names exactly for 1:1 FDW backfill; pg_cron batch extraction; 41 tests passing at migration start.
- Serving: FastAPI `newman-data-api` on the mini (docker, Cloudflare tunnel) at api.kameloso.com — e.g. `/v1/tariffs/by-cp/77710`.

## Related Notes
- [[2026-06-21-newman-agents-founding]]
- [[2026-06-26-cfe-warehouse-schema-supabase]]
- [[2026-07-06-pml-supabase-migration]]
- [[2026-07-12-market-data-migration-plan]]
- [[2026-06-27-newman-data-api-fastapi-mini]]
- [[2026-07-03-review-pml-storage-schema]]
- [[2026-07-03-review-cenace-webforms-scrape]]
- [[2026-07-15-mario-engine-client-calculo]]
