# #181: rates P3: operationalize cuotas — monthly scrape job + promotion + prod cp backfill

- State: OPEN
- Created: 2026-07-15T10:04:26Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/181

## Body

Follow-ups to land #172 fully:
1. Monthly scrape: mini launchd job (or extend pipeline executor) runs `scrape_gdmth.mjs --anio <current> --mes <current>` after CFE publishes (~5 business days before month start); pg_cron alert if current month missing by the 1st.
2. Promote migrations 20260715170000/180000 + function redeploy + solar asset seeding (loader) to staging + prod.
3. Prod `crm.bill.cp` backfill (bills parsed before the cp column existed): same regexp UPDATE from raw_cfe used on develop, then bump `calculo_generation` → offers recompute with real yield/división.
4. Staging same.

## Comment by NewmanTech27 (2026-07-15T11:59:12Z)

Items 2–4 DONE (2026-07-15):
- migrations 170000–200000 promoted develop→staging→prod (#185, #186), applies green
- function redeployed + solar assets seeded (31,896 CPs + 2,369 municipios) on staging AND prod
- cp backfill + generation bump both envs; offers recomputed geo-real on both: staging byte-identical to develop; prod 4 offers incl. BCS caveat (ETG/Cabo) and Anáhuac flipping to BESS-only at real 1500 kWh/kWp QRoo yield (engine IRR-authoritative)

Remaining:
- item 1: monthly scrape launchd job on mini (after backfill completes)
- tarifa_cuota historical copy develop→staging/prod once 2017–2026 backfill finishes (running, per-card fix live, 16 divisiones)

## Comment by NewmanTech27 (2026-07-15T12:44:14Z)

Item 1 DONE: launchd `com.newman.tarifa-cuotas` registered on the mini (days 25 + 1, 09:15 local) → `harvest/tarifas/run-monthly-scrape.sh` (PR #188) scraping current+next month into PROD via ~/.newman-pipeline.env creds. Script reaches the auto-deployed wt-drive checkout at the next main promotion. Only remaining item: tarifa_cuota historical copy develop→staging/prod when the 2017–2026 backfill lands (currently at 2025-05, 1,404 rows, 16 divisiones).
