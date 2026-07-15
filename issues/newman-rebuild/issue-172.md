# #172: rates P1: automate CFE published GDMTH cuotas (mini-side monthly scrape) — nobody has this today

- State: OPEN
- Created: 2026-07-15T08:47:08Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/172

## Body

Verified 2026-07-15: NO automation exists anywhere for CFE published tariff rates — the only store is the CFE Brain wiki page `billing/rate-inputs.md`, manually transcribed from bills (12 months SIN only, other divisions pending). The engine sidesteps it by deriving unit rates from each bill, so this is NOT needed for savings on billed months — it buys:
(a) misbilling detection: bill importes vs published cuotas (CFE errors are a known failure mode; footing check can't catch a wrong published rate)
(b) real near-term rates for projections instead of pure esc_cfe=5%
(c) auto-fill of mario's pending non-SIN divisions

Design:
- CFE SSB publishes GDMTH cuotas monthly (~5 business days before the month) on app.cfe.mx — WAF-blocked from droplet/CI, reachable from the MINI (residential IP, same constraint as harvest)
- mini launchd monthly job → POST rates to a new `cfe.tarifa_rate` table (division, month, concepto, cuota) via RPC; pg_cron alert if a month is missing by the 1st
- backfill: mario's rate-inputs 12-month SIN table as seed

Gate: current month's SIN GDMTH cuotas in the table matching the bill-derived rates within tolerance.
Effort ~1-1.5d. Prio: MEDIUM. DOF/CENACE fallback if the page moves behind harder WAF.

## Comment by NewmanTech27 (2026-07-15T08:50:49Z)

RE-SCOPED per CEO 2026-07-15: prior work located = manual clippings of the tariff pages in CFE Brain vault (raw/articles/GDMTH.md etc., 2026-06-04) — page structure known, zero automation, cuota tables empty (ASP.NET postback form at app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx, month/region selectors).

New scope: REBUILD as automated scraper + Supabase-tracked HISTORICAL price store:
- `cfe.tarifa_cuota` table: (tarifa, region, anio, mes, cargo, unidad, cuota) unique-keyed, append-only history
- scraper iterates every (month, region) the form offers → full historical backfill, then monthly cron for new publications
- runs mini-side (app.cfe.mx WAF blocks datacenter; mini residential IP passes — same constraint as harvest)
- work starting now on branch calculo/tarifa-cuotas

## Comment by NewmanTech27 (2026-07-15T10:32:52Z)

Backfill v2 live on develop: 14 divisiones × 6 cargos/month (Fijo $/mes, Base/Intermedia/Punta $/kWh, Capacidad/Distribución $/kW — the full GDMTH rate card), ~5 min/month after the #179 speedup, walking 2026→2024 (extend to 2017 next run). Demand charges cross-validate against real bills (see #180 comment).
