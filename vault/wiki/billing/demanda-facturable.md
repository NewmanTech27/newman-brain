---
title: "Demanda Facturable — Cargo por Capacidad y Distribución"
type: concept
tags: [cfe, gdmth, demanda, factor-de-carga, umbral, capacidad, distribucion]
created: 2026-06-04
updated: 2026-06-08
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024, 2026-06-07-gdmto, 2026-06-08-cfe-bills-780881200029-fy25-26]
---

# Demanda Facturable — Cargo por Capacidad y Distribución

> **Purpose:** Defines exactly how CFE computes the billed demand for each of the two demand charges on a GDMTH bill. This page is the authoritative reference for the umbral cap logic used in the billing calculator.

GDMTH has **two separate demand charges**. Each uses a different measured demand as its base, but both are subject to the same upper cap (the umbral energético). Understanding the interplay between measured demand and the cap is essential for modeling any PV or BESS scenario.

---

## 1. Cargo por Capacidad — billed demand

> **Citation:** GDMTH tariff page §7.1; confirmed in Acuerdo A/158/2024 Annexo §5.1 (DOF 2025-01-08)  
> **Status:** ✓ Cited directly

**Formula:**
```
billed_demand_capacidad = min( Dmax_punta , umbral )

where: umbral = kWh_red / (d × FC × 24)
```

**Inputs:**

| Variable | Description | Unit | How obtained | Source |
|---|---|---|---|---|
| `Dmax_punta` | Maximum 15-min average demand coincident with any punta hour in the billing period | kW | HM interval meter | Measured |
| `kWh_red` | Total kWh drawn from the CFE grid in the billing period | kWh | HM meter sum | Measured |
| `d` | Days in billing period | days | Bill header | Measured |
| `FC` | Load factor for GDMTH category | dimensionless | **0.57** | A/158/2024 Table 2 §3.1.2 |

**Logic notes:**
- The umbral converts total monthly consumption into an equivalent "reference demand," scaled by FC. It is an upper bound on billed demand regardless of how spiky the actual load profile is.
- If `Dmax_punta ≤ umbral`: the measured peak demand is billed in full.
- If `Dmax_punta > umbral`: only the umbral is billed — the user is capped.
- **If there is no punta period** (e.g., Baja California in winter, or any Sunday in any region): the formula collapses to `billed_demand_capacidad = umbral` only.

**Example (30-day month, 100,000 kWh_red, Dmax_punta = 350 kW):**
```
umbral = 100,000 / (30 × 0.57 × 24) = 243.7 kW
billed_demand_capacidad = min(350, 243.7) = 243.7 kW   ← cap binds
```

**Example (same month, Dmax_punta = 200 kW):**
```
umbral = 243.7 kW
billed_demand_capacidad = min(200, 243.7) = 200 kW   ← measured demand binds
```

---

## 2. Cargo por Distribución — billed demand

> **Citation:** GDMTH tariff page §7.2; confirmed in Acuerdo A/158/2024 Annexo §5.2  
> **Status:** ✓ Cited directly

**Formula:**
```
billed_demand_distribucion = min( max(D_base, D_inter, D_punta) , umbral )

where: umbral = kWh_red / (d × FC × 24)    ← same formula as capacidad
```

> **⚠ Correction (2026-06-08) — empirically verified, supersedes the earlier "Dmax_mensual = KWMax" claim.** The distribución charge is billed on the **maximum of the three per-period registered demands** (`kW base`, `kW intermedia`, `kW punta`), **not** on the bill's separately-printed `KWMax` register. On 3 of 12 [[2026-06-08-cfe-bills-780881200029-fy25-26|Grupo Posadas Cancún bills]] the printed `KWMax` exceeded `max(period demands)`, and in every case CFE billed distribución on the lower `max(period demands)` (verified: importe ÷ unit rate):
>
> | Month | KWMax (printed) | max(B,I,P) | CFE billed distribución on |
> |---|---|---|---|
> | ABR 25 | 2,077 | 1,664 | **1,664** |
> | OCT 25 | 1,608 | 1,399 | **1,399** |
> | DIC 25 | 2,078 | 1,591 | **1,591** |
>
> `KWMax` appears to be an informational absolute-peak register (possibly capturing sub-15-min or out-of-period transients) and is **not** the billing base. Use `max(D_base, D_inter, D_punta)`.

**Inputs:**

| Variable | Description | Unit | How obtained | Source |
|---|---|---|---|---|
| `max(D_base, D_inter, D_punta)` | Highest of the three per-period maximum demands registered in the billing period | kW | HM interval meter (per-period registers on the bill) | Measured |
| `kWh_red`, `d`, `FC` | Same as above | — | Same | Same |

**Logic notes:**
- `max(period demands) ≥ Dmax_punta` always, because it is unconstrained to the punta window.
- Both charges share the same umbral formula and the same FC value.
- A user whose highest period peak occurs outside punta hours still has a distribution charge based on that off-peak peak — but it is also capped by the same umbral.
- ⚠ Do **not** use the bill's `KWMax` field as the distribución base — see correction box above.

---

## 3. Demand measurement method

> **Citation:** GDMTH tariff page §7.3  
> **Status:** ✓ Cited

- Measured by HM (hourly metering) interval meter recording average kW over every 15-minute window.
- The highest 15-minute average in the billing period is the billed demand for each category.
- **Any fraction of a kW is rounded up to the next whole kW.**
- Billing period = calendar month.

---

## 4. FC values — all GDMTH categories

> **Citation:** Acuerdo A/158/2024, Annexo Único Table 2, §3.1.2  
> **Status:** ✓ Cited

| Tariff category | FC | Notes |
|---|---|---|
| DB1, DB2 | 0.59 | Domestic |
| PDBT | 0.58 | Small demand, low tension |
| GDBT | 0.49 | Large demand, low tension |
| APBT, RABT, APMT, RAMT | 0.50 | Public lighting, irrigation |
| GDMTO | 0.55 | Medium tension, <100 kW, non-hourly |
| **GDMTH** | **0.57** | **This wiki's primary tariff** |
| DIST | 0.74 | Industrial, subtransmission |
| DIT | 0.71 | Industrial, transmission |

The FC for GDMTH of **0.57** is stable in the 2025 Acuerdo (A/158/2024). Whether it was the same in prior years requires checking A/073/2023 (2024) — not yet ingested.

> **GDMTO note:** [[gdmto]] uses FC = **0.55** and the same umbral formula. However, because GDMTO has no TOU periods, the Cargo por Capacidad collapses to `umbral` only (no Dmax_punta). The Cargo por Distribución retains `min(Dmax_mensual, umbral)`. See [[gdmto]] for the full comparison.

---

## 5. The umbral and its implications for PV/BESS

> **Status:** ⚠ Logical consequence of the formula — not explicitly named "umbral" in the regulation, but the formula is cited. The term "umbral energético" is commonly used in industry analysis.

The umbral cap creates a counterintuitive interaction when PV is added:

**PV reduces kWh_red → umbral decreases → billed demand cap tightens**

This means:
- If the cap was already binding (Dmax > umbral), adding PV lowers the cap further and saves demand charges — but not by reducing the measured peak.
- If the cap was not binding (Dmax < umbral), adding PV may NOT reduce demand charges at all (the measured Dmax still binds, and the lower umbral doesn't matter until it drops below Dmax).
- BESS reduces Dmax_punta — but if the umbral is already lower than Dmax_punta, BESS only saves down to the umbral level. Further BESS reduction below the umbral has no demand savings.

**See:** [[pv-bess-combined]] for the full interaction model with formulas.

---

## 6. Autoabastecimiento users — special treatment

> **Citation:** GDMTH tariff page §7.1 and §7.2  
> **Status:** ✓ Cited

Users who receive electricity under an **autoabastecimiento** CRE permit use only the CFE-supplied quantities:

```
Dmax_punta   → only the peak demand drawn from CFE (not total site demand)
kWh_red      → only kWh supplied by CFE (not total site consumption)
```

This means the umbral is also calculated on CFE-supplied consumption only. A large self-supply generator significantly reduces kWh_red and therefore also lowers the umbral.

---

## Related pages

- [[gdmth-bill-structure]] — full bill calculation using these demand values
- [[horarios-y-divisiones]] — which hours are "punta" (required to compute Dmax_punta)
- [[pv-bess-combined]] — the umbral interaction when both PV and BESS are present
- [[rate-inputs]] — current $/kW-mes values for capacidad and distribución
