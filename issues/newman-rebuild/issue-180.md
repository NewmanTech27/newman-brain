# #180: rates P2: misbilling detector — bill-derived rates vs published cuotas

- State: OPEN
- Created: 2026-07-15T10:04:24Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/180

## Body

Once cfe.tarifa_cuota holds published GDMTH cuotas (#172), cross-check every crm.bill: derive the bill's implicit unit rates (gen_base/kwh_base, capacidad/basis, distribucion/kW — the engine's own derivation) and compare vs the published cuota for that (division, anio, mes). Divergence beyond tolerance → flag on the bill (new column or alert table). CFE billing errors are a known failure mode the footing check cannot catch (a wrong rate foots fine).

Design: pure-SQL check (view or pg_cron step after cfe-calculo parse stage); needs bill división (available since #169 via CP estado — but note published cuotas are per DIVISIÓN TARIFARIA, finer than SIN/BC/BCS: map bill CP → municipio → división tarifaria via a table from Acuerdo A/158/2024 Annexo 25–42, or match on the scraped division label by estado).
Depends: #172 backfill complete.

## Comment by NewmanTech27 (2026-07-15T10:32:51Z)

Early validation (develop, NORTE 2026-06 vs RPU 585880702961): distribución bill-derived 73.08 on the umbral-capped basis vs published 72.92 (+0.2%); capacidad 401.43 vs 394.26 (+1.8%). Two detector requirements confirmed: (1) use the ENGINE's basis rules (umbral cap!) not raw kW — naive max-kW gave −6.3% false divergence; (2) tolerance must absorb billing-period-vs-calendar-month blending (bills span two published months) — start ±3% warn / ±6% flag.
