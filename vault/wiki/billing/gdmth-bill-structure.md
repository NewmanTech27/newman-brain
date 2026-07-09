---
title: "GDMTH Bill Structure — Complete Anatomy"
type: concept
tags: [cfe, gdmth, facturacion, calculo, billing-calculator]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024]
---

# GDMTH Bill Structure — Complete Anatomy

> **Purpose:** This page is the entry point for the billing calculator. It maps every line item on a real CFE GDMTH bill to its formula, inputs, and sources. Use it to reconstruct or validate any bill from raw meter data.

---

## Overview: what a GDMTH bill charges

A GDMTH bill has **9 billable components** grouped into three types:

| Type | Component | Unit | Driver |
|---|---|---|---|
| **Variable — energy** | Energía punta | $/kWh | kWh consumed during punta hours |
| **Variable — energy** | Energía intermedia | $/kWh | kWh consumed during intermedio hours |
| **Variable — energy** | Energía base | $/kWh | kWh consumed during base hours |
| **Variable — energy (flat rate)** | Transmisión | $/kWh | Total kWh consumed |
| **Variable — energy (flat rate)** | Operación CENACE | $/kWh | Total kWh consumed |
| **Variable — energy (flat rate)** | SCnMEM | $/kWh | Total kWh consumed |
| **Variable — demand** | Cargo por Capacidad | $/kW-mes | Demand facturable de capacidad (see below) |
| **Variable — demand** | Cargo por Distribución | $/kW-mes | Demand facturable de distribución (see below) |
| **Fixed** | Operación Suministrador Básico | $/mes | One charge per billing period regardless of consumption |

> **Citation:** Component structure defined in Acuerdo A/158/2024, Annexo Único §1.1 and §2.1–2.6 (DOF 2025-01-08). Also confirmed in CFE tariff page for GDMTH, section "Cuotas aplicables."

---

## Complete bill calculation formula

```
Bill = E_punta + E_intermedia + E_base + Transmisión + CENACE + SCnMEM + Capacidad + Distribución + SSB
```

### Step-by-step

**Step 1 — Collect meter readings (inputs):**

| Variable | Description | Unit | Source |
|---|---|---|---|
| `kWh_punta` | Energy consumed during punta hours this billing period | kWh | HM meter (hourly) |
| `kWh_inter` | Energy consumed during intermedio hours | kWh | HM meter |
| `kWh_base` | Energy consumed during base hours | kWh | HM meter |
| `kWh_red` | Total energy drawn from CFE grid = kWh_punta + kWh_inter + kWh_base | kWh | Sum |
| `Dmax_punta` | Peak 15-min average demand coincident with any punta hour this month | kW | HM meter |
| `Dmax_dist` | Max of the three per-period registered demands = max(kW base, kW inter, kW punta). **Not** the bill's `KWMax` register — see [[demanda-facturable]] | kW | HM meter |
| `d` | Days in the billing period | days | Bill header |

**Step 2 — Compute billed demands (demand facturable):**

> **See:** [[demanda-facturable]] for the full logic including the umbral cap.

```
umbral = kWh_red / (d × 0.57 × 24)

billed_demand_capacidad    = min(Dmax_punta,                       umbral)
billed_demand_distribucion = min(max(D_base, D_inter, D_punta),    umbral)
```

**Step 3 — Apply tariff rates (time-varying, see [[rate-inputs]]):**

```
E_punta      = kWh_punta  × r_punta       [$/kWh — punta energy rate]
E_intermedia = kWh_inter  × r_intermedio   [$/kWh — intermedio energy rate]
E_base       = kWh_base   × r_base         [$/kWh — base energy rate]
Transmisión  = kWh_red    × r_transmision  [$/kWh — flat transmission]
CENACE       = kWh_red    × r_cenace       [$/kWh — CENACE operation]
SCnMEM       = kWh_red    × 0.0062         [$/kWh — fixed; Acuerdo A/158/2024 art. PRIMERO]
Capacidad    = billed_demand_capacidad    × r_capacidad    [$/kW-mes]
Distribución = billed_demand_distribucion × r_distribucion [$/kW-mes]
SSB          = r_ssb                      [$/mes fixed]

Total = E_punta + E_intermedia + E_base + Transmisión + CENACE + SCnMEM + Capacidad + Distribución + SSB
```

> **Status:** ✓ Component structure cited. Rate formulas (multiply kWh × $/kWh) are inferred from tariff structure; the tariff page does not show an explicit multiplication formula but this is the definitional interpretation of a $/kWh charge.

---

## Which hours count as which period?

Period definitions vary by tariff division and season. All GDMTH users are in one of three systems:

| Your division | System | See |
|---|---|---|
| Baja California | BC | [[horarios-y-divisiones#baja-california]] |
| Baja California Sur | BCS | [[horarios-y-divisiones#baja-california-sur]] |
| Any other (Bajío, Jalisco, Norte, etc.) | SIN | [[horarios-y-divisiones#sin]] |

> **Citation:** CFE GDMTH tariff page §6; Acuerdo A/158/2024, Annexo Único Table 4–5.

---

## Minimum monthly charge

The minimum bill is the **Operación Suministrador Básico** charge — a fixed amount that applies even if consumption is zero.

> **Citation:** GDMTH tariff page §3: "El importe que resulta de aplicar el cargo por la operación del Suministrador de Servicios Básicos correspondiente a esta categoría tarifaria." Acuerdo A/158/2024, Annexo §2.3.

---

## For autoabastecimiento users

Users who receive electricity as part of a self-supply permit (autoabastecimiento) use only the **CFE-supplied** Dmax and kWh in the demand formulas — their own generation does not count as grid consumption:

```
billed_demand_capacidad    = min(Dmax_punta_CFE_only,    umbral_CFE_only)
billed_demand_distribucion = min(Dmax_mensual_CFE_only,  umbral_CFE_only)
```

> **Citation:** GDMTH tariff page §7.1 and §7.2: "Para los centros de carga que reciban energía eléctrica por ser parte de un permiso de generación de energía eléctrica bajo la modalidad de autoabastecimiento, la Dmax y Q_mensual serán la demanda máxima y el consumo mensual suministrados en el mes de facturación por CFE SSB."

---

## For solar DG users (Generador Exento / medición neta)

Under [[medicion-neta]], `kWh_red` is the **net** consumption after crediting solar generation:

```
kWh_red = kWh_consumed_from_grid - kWh_injected_to_grid (within billing period, by period)
```

See [[pv-savings-model]] for the impact on every bill component including the umbral effect.

---

## Validation checklist (bill reconstruction)

To verify a real CFE bill:
- [ ] Confirm kWh_punta + kWh_inter + kWh_base = kWh_red (total on bill)
- [ ] Recompute umbral = kWh_red / (d × 0.57 × 24); verify against billed demand
- [ ] Check which demand is billed: measured or umbral (whichever is lower)
- [ ] Verify energy charges: kWh × published rate for each period
- [ ] Verify SCnMEM = kWh_red × 0.0062
- [ ] Confirm SSB fixed charge matches the published monthly amount
- [ ] Sum all components; should match bill total before IVA

---

## Related pages

- [[demanda-facturable]] — the umbral cap formula in full
- [[horarios-y-divisiones]] — which hours are punta/intermedio/base by division
- [[rate-inputs]] — where to find current $/kWh and $/kW-mes values
- [[pv-savings-model]] — how this bill changes with solar
- [[bess-savings-model]] — how this bill changes with a battery
