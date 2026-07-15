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
