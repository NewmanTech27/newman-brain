---
title: "GDMTH — Gran Demanda en Media Tensión Horaria"
type: concept
tags: [cfe, tarifa, electricidad, media-tension, gran-demanda, tiempo-de-uso]
created: 2026-06-04
updated: 2026-06-07
sources: [2026-06-04-gdmth, 2026-06-07-gdmto]
---

# GDMTH — Gran Demanda en Media Tensión Horaria

The CFE electricity tariff applied to medium-voltage commercial and industrial consumers with contracted demand ≥ 100 kW. It is a **time-of-use (TOU) tariff**: energy consumption is billed at different rates depending on the time period (punta, intermedio, or base) in which it is consumed. Demand is billed via two separate charges.

## Application criteria

| Criterion | Requirement |
|---|---|
| Voltage level | Media tensión |
| Minimum demand | 100 kW |
| Use | Any (commercial, industrial, services) |

## Billing components

GDMTH bills **6 components** in total:

| Component | Unit | Based on |
|---|---|---|
| Energía punta | $/kWh | Consumption during punta hours |
| Energía intermedia | $/kWh | Consumption during intermedio hours |
| Energía base | $/kWh | Consumption during base hours |
| Cargo por Capacidad | $/kW-mes | [[demanda-facturable\|Capacity demand]] |
| Cargo por Distribución | $/kW-mes | [[demanda-facturable\|Distribution demand]] |
| Operación del Suministrador Básico | $/mes | Fixed monthly minimum |

Additionally: Transmisión, operación del [[cenace]], Servicios Conexos No MEM, and Energía y Capacidad components are integrated into the final consumer charges.

## Contracted demand rules

- Minimum: the **greatest** of: 60% of total connected load, 100 kW, or capacity of the largest installed motor/device
- If 60% of connected load exceeds substation capacity: contracted demand = substation capacity (kVA) × 90%
- Security deposit: 2× (capacity charge rate × contracted demand kW)

## Demand measurement

Measured with 15-minute interval meters. The highest average demand in any 15-minute window in the billing period is the measured demand. Fractional kW rounded up to the next full kW. See [[demanda-facturable]].

## Time periods

Three periods — **punta**, **intermedio**, **base** — defined by region and season. See [[horarios-y-divisiones]] for the full schedule matrix.

Key insight: the number of daily punta hours varies enormously by region:
- Most of Mexico (Central, Norte, Noreste, etc.): **2 hours/day** in summer (20:00–22:00)
- Baja California Sur: **10 hours/day** in summer (12:00–22:00 weekdays)

## Relationship to GDMTO

[[gdmto]] is the non-TOU sister tariff for medium-voltage loads **below 100 kW**. The relationship is bidirectional:

- **GDMTH → GDMTO:** If a GDMTH user maintains measured demand below 100 kW for 12 consecutive months, they may request reclassification to GDMTO via a new supply contract.
- **GDMTO → GDMTH:** If a GDMTO user's measured demand reaches or exceeds 100 kW, they must request GDMTH migration. After 3 consecutive months at ≥100 kW without migrating, CFE may rescind the contract.

Key structural differences:
| Feature | GDMTO | GDMTH |
|---|---|---|
| TOU periods | None (flat rate) | Punta / Intermedio / Base |
| Capacidad demand base | Umbral only (no Dmax_punta) | min(Dmax_punta, umbral) |
| FC | 0.55 | 0.57 |
| Demand threshold | < 100 kW | ≥ 100 kW |

## Regulatory references

- **Acuerdo A/158/2024** (Annex sections 3.1.2 and 3.1.5): defines load factors and period schedules by region
- Regulator for methodology questions: [[cne]]

## Related concepts

- [[horarios-y-divisiones]] — full punta/intermedio/base schedule and the 17 divisions, by season
- [[demanda-facturable]] — how demand values for capacity and distribution charges are calculated (incl. the factor de carga / umbral)

## How sources treat this

- [[2026-06-04-gdmth]]: defines the full tariff structure, period schedules, and demand methodology. **Missing: actual numeric rate values.**
- [[2026-06-07-gdmto]]: GDMTO tariff page — confirms structural comparison; establishes 100 kW migration rules in both directions.

## Open questions

- What are the numeric rates for June 2026 (both GDMTH and GDMTO)?
- What is the energy rate premium of GDMTH over GDMTO — does TOU metering cost justify the rate spread for a typical user?
- What is the typical bill breakdown by component for a 500 kW industrial user?
