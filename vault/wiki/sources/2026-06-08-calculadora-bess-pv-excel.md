---
title: "Calculadora BESS+PV (Excel) — Service 780881200029"
type: source
tags: [excel, calculadora, bess, solar, gdmth, modelo-financiero, savings]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Calculadora BESS+PV (Excel) — Service 780881200029

**Type:** data / external model (Excel workbook)
**Title in file:** "Calculadora BESS PV Sharde savings — México GDMTH (BCS / SIN)"
**Analysis date:** 2026-05-18
**Raw file:** `raw/data/780881200029.xlsx`

## Summary

A manually-built financial savings model for a PV + BESS installation at the Grupo Posadas Cancún site ([[2026-06-08-cfe-bills-780881200029-fy25-26]]). It is the **comparison target** for the wiki's savings analysis ([[2026-06-08-780881200029-yearly-savings]]). The model is well-structured: it transcribes the 12 bills, reconstructs each (validating to ~1.2%), builds hourly load/PV/BESS dispatch, and projects 20-year cash flows including a PPA/leasing structure.

## Workbook structure (8 sheets)

| Sheet | Role |
|---|---|
| `PROJECT_INPUTS` | System config + key indicators + monthly summary + 20-yr financial projection |
| `TARIFF_RATES` | Bill inputs (kWh/kW per month), MEM importes, derived unit rates |
| `BASELINE_COST` | Reconstructs each bill from formula; compares to receipt (Δ ~1.2%, all "OK <2%") |
| `CONSUMPTION_PROFILE` | Hourly load curves by industry × real client kWh (summer/winter) |
| `DISPATCH` / `DISPATCH_ISLAND` | Hourly PV+BESS dispatch (grid-tied / island modes) |
| `ActiveLeasing 1ra/2da Etapa` | Lease/PPA finance schedules |

## Key inputs

- **PV:** 194.48 kWp · yield 1,800.27 kWh/kWp/yr · 350,116 kWh/yr · 0.5%/yr degradation · EPC 0.75 USD/Wp · cost MXN 2,559,843
- **BESS:** 2,940 kWh nominal · 1,503 kW · RTE 0.96 · DoD 0.96 · usable 2,822.4 kWh · 1.25%/yr degradation · discharges 1,009,362 kWh/yr (~357 cycles)
- **PPA to client:** 1.50 MXN/kWh, 15 yr · CFE escalation 6%/yr · PPA escalation 5%/yr · WACC 12% · horizon 20 yr

## Key claims (outputs)

- **Annual baseline (Bill ANTES, sin IVA): $30,157,371** ✅ independently validated against the 12 PDFs (peso-exact transcription).
- **Ahorro Bruto Año 1: $7,593,969 (25.2%)** — gross/ideal monthly resumen.
- **Split:** BESS ≈ 87% of savings, PV ≈ 13% (PV ≈ $0.83–1.0M; BESS ≈ $4.95–6.6M).
- **Financial projection applies a 0.75 "Factor BESS falla" derate** → realistic Year-1 ≈ $5.78M.
- **Indicators:** TIR 19.0% · VPN@12% $7.83M · Payback 6 yr · CAPEX $17,007,003.

## Entities mentioned

- [[grupo-posadas]] — the client site modeled

## Concepts mentioned

- [[gdmth-bill-structure]] — the model's BASELINE_COST replicates this formula
- [[demanda-facturable]] — model correctly bills capacidad on kW punta, distribución on max(B,I,P)
- [[bess-savings-model]] — model's DISPATCH is the detailed version of this
- [[pv-bess-combined]] — model treats PV+BESS as additive (valid here; see analysis)

## Contradictions / tensions

- ~~**+1.2% systematic overshoot** in BASELINE_COST reconstruction — unexplained.~~ **SOLVED (2026-06-11 audit):** it is the **FP bonificación** (site FP 99.5–100%, ~−$29k/month) that column M of `TARIFF_RATES` never transcribed — matches peso-exact ×12. See [[2026-06-11-780881200029-calculadora-audit]].
- **The 0.75 BESS derate** converts $7.59M gross → $5.78M net. Confirmed (2026-06-08) as a business availability assumption, independent of the dispatch energy limit.
- **Arbitrage flaw found (2026-06-11 audit):** battery cycled 365 d/yr, uncapped vs the bill's punta energy → arbitrage overstated ~35% ($1,216,238 → $790,049 corrected). Plus an O&M-PV escalation exponent bug and the falla factor erroneously waiving 25% of BESS O&M. Full findings + corrected modular rebuild: [[2026-06-11-780881200029-calculadora-audit]] / `780881200029 - Calculadora v2.xlsx`.

## Questions raised

- ~~Does `DISPATCH` enforce the 2,822 kWh usable limit against the **4-hour winter punta** window?~~ Yes (resolved 2026-06-08).
- PV is only 3.4% of load and sized at 194 kWp on a 5,115 kW site — why so small? (No credit-expiry risk since always self-consumed → room to scale.)
