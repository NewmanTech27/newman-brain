---
title: "GDMTO — Gran Demanda en Media Tensión Ordinaria"
type: concept
tags: [cfe, tarifa, gdmto, media-tension, demanda, umbral]
created: 2026-06-07
updated: 2026-06-07
sources: [2026-06-07-gdmto]
---

# GDMTO — Gran Demanda en Media Tensión Ordinaria

The CFE electricity tariff for medium-voltage commercial and industrial consumers with contracted demand **below 100 kW**. It is the non-time-of-use (flat-rate) counterpart to [[gdmth]]: structurally similar billing logic, but no hourly pricing periods.

---

## Application criteria

| Criterion | Requirement |
|---|---|
| Voltage level | Media tensión |
| Demand range | < 100 kW |
| Use | Any (commercial, industrial, services) |

---

## Billing structure

GDMTO bills energy at a **single flat rate** (no punta/intermedio/base split). Demand is billed via the same two charges as GDMTH, but with important differences in how each is computed.

### Cargo por Capacidad

Because GDMTO has no time-of-use periods, there is no Dmax_punta to measure. The billed demand for capacidad is simply the umbral:

```
billed_demand_capacidad = Qmensual / (d × FC × 24)
```

This applies to all GDMTO users. (The same fallback formula applies to GDMTH on days/regions with no punta period — here it is the universal case.)

### Cargo por Distribución

```
billed_demand_distribucion = min( Dmax_mensual , umbral )

where: umbral = Qmensual / (d × FC × 24)
```

Same two-component logic as GDMTH. `Dmax_mensual` is the peak 15-min demand in any interval during the billing period.

### FC value

| Category | FC |
|---|---|
| **GDMTO** | **0.55** |
| GDMTH | 0.57 |

Source: A/158/2024, §3.1.2. GDMTO's slightly lower FC makes its umbral somewhat tighter than GDMTH at the same consumption level.

---

## Contracted demand rules

- Minimum: the greatest of: **60% of total connected load**, **10 kW**, or **capacity of the largest installed motor/device**
- If 60% of connected load exceeds substation capacity: contracted demand = substation capacity (kVA) × 90%
- Security deposit: 2× (capacity charge rate × contracted demand kW)

---

## Demand measurement

Measured with 15-minute interval meters. Highest 15-min average demand in the billing period = billed Dmax_mensual. Any fractional kW rounded up to the next full kW.

---

## 100 kW migration trigger

> **Critical rule:** If measured demand equals or exceeds 100 kW, the user **must request migration to [[gdmth]]**.
> After 3 consecutive months at ≥100 kW without migrating, CFE may rescind the supply contract.

This means GDMTO users approaching 100 kW should proactively monitor and consider GDMTH enrollment — or install BESS/load management to stay below the threshold.

---

## Autoabastecimiento users

For users receiving electricity under an autoabastecimiento CRE permit, `Qmensual` in the umbral formula uses **only CFE SSB-supplied kWh** (self-generated excluded). See [[autoconsumo]] and [[demanda-facturable]] §6.

---

## Related concepts

- [[pdbt]] — the low-voltage ≤25 kW tariff below GDMTO on the commercial ladder
- [[gdmth]] — the ≥100 kW TOU successor tariff; migration target when demand crosses threshold
- [[demanda-facturable]] — shared umbral cap formula; FC table includes GDMTO (0.55) vs GDMTH (0.57)
- [[autoconsumo]] — autoabastecimiento treatment of Qmensual
- [[scheme-comparison]] — eligibility decisions for PV/BESS (currently GDMTH-focused; GDMTO rules not yet confirmed)

---

## How sources treat this

- [[2026-06-07-gdmto]]: official CFE tariff page. Defines formulas and application rules. **Missing: actual numeric rate values** (images not extractable from web clip).

---

## Open questions

- What are the current $/kWh and $/kW-mes rates for GDMTO?
- Is GDMTO eligible for medición neta (generador exento) and SAE-CC under the same rules as GDMTH, or do separate conditions apply?
- What is the energy rate premium of GDMTH over GDMTO — does TOU metering cost justify the rate spread for a typical <100 kW user?
