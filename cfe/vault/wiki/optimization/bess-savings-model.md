---
title: "BESS Savings Model — How a Battery Changes the GDMTH Bill"
type: concept
tags: [cfe, gdmth, bess, sae-cc, demanda, peak-shaving, savings-model]
created: 2026-06-04
updated: 2026-07-07
sources: [2026-06-04-gdmth, 2026-06-04-dacg-sae-a113-2024, 2026-06-04-acuerdo-a158-2024, 2026-06-09-autoconsumo-cne-2025]
---

# BESS Savings Model — How a Battery Changes the GDMTH Bill

> **Purpose:** Complete model for computing how a SAE-CC battery reduces a GDMTH bill through peak demand shaving. Covers demand savings for both capacidad and distribución charges, operational constraints, and the limits of BESS alone.

---

## Scope and assumptions

- Battery installed as **SAE-CC** (Sistema de Almacenamiento en Centro de Carga)
- No grid injection — battery serves the site's own load only
- No CRE generation permit required
- Battery dispatches during punta hours to reduce Dmax_punta

> **Citation:** SAE-CC regulatory framework in Acuerdo A/113/2024, Chapter IV (DACG SAE). No grid injection requirement confirmed.

> **Two reasons a battery shows up on a project.** This model values storage as a **demand‑savings** lever (peak shaving) for a < 0.7 MW SAE‑CC. Separately, the **2025 [[autoconsumo]] regime makes storage a regulatory requirement**: an intermittent PV plant **≥ 0.7 MW** going interconnected must carry a SAE (or contracted CFE backup) to cover ramp/intermittency/variability (LSE art. 32‑III; DACG Num. 4.5; see [[sae-cc]], [[2026-06-09-autoconsumo-cne-2025]]). When sizing past the exempt line, the battery is therefore both a savings lever *and* a permit precondition.

---

## How peak shaving works on a GDMTH bill

The battery monitors the site's real-time demand. During punta hours, when demand approaches a target threshold, the battery discharges at power `P_bess` (kW), reducing the net demand drawn from the grid:

```
Dmax_punta_with_BESS = Dmax_punta_without_BESS - P_bess_effective
```

Where `P_bess_effective` is the actual average kW discharged during the 15-minute peak demand interval(s).

---

## Step 1 — Define BESS parameters

| Parameter | Description | Unit |
|---|---|---|
| `P_bess` | Rated power of battery (discharge) | kW |
| `E_bess` | Energy capacity | kWh |
| `η` | Round-trip efficiency (charge-discharge) | % |
| `P_bess_effective` | Actual peak reduction achieved in the worst 15-min window | kW |

**Constraint:** `P_bess ≤ contracted_demand - remaining_site_demand_after_shaving`  
The battery cannot cause the site to exceed contracted demand in any direction.

> **Citation:** A/113/2024 §IV: battery power counts toward contracted demand; grid withdrawal cannot exceed contracted demand.

---

## Step 2 — Compute demand savings

> **Status:** ⚠ Formula is inferred from billing mechanics. The interaction with the umbral is a logical consequence, not explicitly stated in regulation.

The savings depend on which constraint was binding before and after BESS:

```
umbral = kWh_red / (d × 0.57 × 24)

Dmax_after = Dmax_punta_without_BESS - P_bess_effective

billed_capacidad_before = min(Dmax_punta, umbral)
billed_capacidad_after  = min(Dmax_after,  umbral)

ΔCapacidad = (billed_capacidad_before - billed_capacidad_after) × r_capacidad
```

**Cases:**

| Scenario | Condition | Savings |
|---|---|---|
| Measured demand was binding; BESS reduces it below umbral | Dmax > umbral; Dmax_after < umbral | (Dmax - umbral) × r_capacidad — BESS only helps down to the cap |
| Measured demand was binding; BESS reduces it but stays above umbral | Dmax > umbral; Dmax_after > umbral | 0 — umbral still binds; no savings until Dmax drops below umbral |
| Measured demand was already below umbral | Dmax < umbral | 0 — cap doesn't bind; BESS reduces billed demand directly by P_bess_effective × r_capacidad |
| Cap was binding; BESS reduces measured demand | Dmax > umbral | 0 for capacidad — umbral already caps it. BESS has no effect unless it also reduces kWh_red |

**The critical insight:**

> **BESS only delivers demand savings when `Dmax_punta > umbral`.**  
> When the umbral is already binding (Dmax > umbral), the billed demand is the umbral regardless of BESS dispatch. BESS must first reduce Dmax_punta **below** the umbral to generate any savings.

**Example (cap-bound site, BESS cannot help):**
```
kWh_red = 100,000 kWh, d = 30, FC = 0.57
umbral = 100,000/(30×0.57×24) = 243.7 kW

Dmax_punta = 350 kW  →  billed = 243.7 kW (cap binds)
With BESS (200 kW): Dmax_after = 150 kW  →  billed = min(150, 243.7) = 150 kW
ΔCapacidad = (243.7 - 150) × r_capacidad = 93.7 kW × r_capacidad  ← BESS DOES help here!
```

Wait — in this example BESS pushes Dmax_after below umbral, so it DOES save. The key is:

**BESS saves: `min(P_bess_effective, Dmax_punta - umbral)` in demand reduction from the capacity charge, ONLY if `Dmax_punta > umbral` AND `P_bess_effective > Dmax_punta - umbral`.**

More precisely:
```
effective_demand_reduction_capacidad = max(0, billed_before - billed_after)
  = max(0, min(Dmax_punta, umbral) - min(Dmax_punta - P_bess_effective, umbral))
  = max(0, min(P_bess_effective, Dmax_punta - umbral))
```

When `Dmax_punta ≤ umbral`: demand binds; full `P_bess_effective` translates to savings.  
When `Dmax_punta > umbral` and BESS brings Dmax below umbral: savings = `Dmax_punta - umbral` only; BESS beyond that point has no additional demand savings.  
When `Dmax_punta > umbral` and BESS not enough to bring Dmax below umbral: zero savings.

---

## Step 3 — Distribution charge savings

Distribution is based on Dmax_mensual (peak in any 15-min interval, any hour):

```
billed_distribucion_before = min(Dmax_mensual, umbral)
billed_distribucion_after  = min(Dmax_mensual_after, umbral)
```

BESS dispatching only during punta hours may not reduce Dmax_mensual if the site's highest peak occurs outside punta hours. To reduce Dmax_mensual, the battery must be available during the actual monthly peak — which may require a different dispatch strategy.

---

## Step 4 — Energy cost of charging the battery

BESS must charge from the grid (or solar). Charging during off-peak hours has a cost:

```
kWh_charging = E_bess / η   [kWh drawn from grid per full cycle]
cost_charging = kWh_charging × rate_of_charging_period
```

Net savings per cycle = demand savings per cycle - charging cost

For a SIN winter user: charge in base hours (0:00–6:00, rate = r_base), discharge in punta (18:00–22:00, saves r_capacidad × kW_reduced). Net economics must be positive.

**Discharge volume constraint (calculator-grade, added 2026-06-11):** arbitrage energy is bounded by the punta calendar and by the load itself:

```
disch_month = min(usable_day × punta_weekdays, kWh_punta_bill)
```

- The battery only cycles on days with a punta window — **Mon–Fri minus festivos**; sábados, domingos and festivos run the domingo schedule ([[horarios-y-divisiones]]), so there is nothing to displace (~21, not 30, cycle-days/month).
- Monthly discharge can never exceed the bill's punta kWh — a SAE-CC cannot inject to the grid ([[sae-cc]]), so it cannot displace punta energy that doesn't exist.

This was found in the [[2026-06-11-780881200029-calculadora-audit]]: the reference Excel (and engine v1, diff-built against it) cycled 365 d/yr uncapped → SIN arbitrage overstated ~35%. The engine was corrected and golden re-baselined the same day.

---

## Step 5 — Minimum effective BESS size

For BESS to deliver any demand savings, the battery must be able to sustain `P_bess_effective` for the **full duration of the worst-case punta demand event**. The worst case is typically the longest consecutive punta window.

**Minimum energy needed:**
```
E_min = P_bess × punta_hours_to_cover / η

For SIN winter (4h punta): E_min = P_bess × 4 / η
For BCS summer (10h punta): E_min = P_bess × 10 / η
```

A 200 kW battery in SIN needs at minimum 200 kW × 4h / 0.85 = ~940 kWh to fully cover all punta hours in a winter day.

---

## Step 6 — Rasurado plano y dimensionado óptimo: la regla verano-2h (2026-07-07)

CFE factura capacidad sobre el **peor intervalo de punta del mes**, así que la energía limitada del BESS debe repartirse en **rasurado plano** sobre todo el bloque de punta — la descarga voraz "gasta" kWh en horas que CFE no cobra. La forma cerrada de la reducción facturable mensual (equivale a la simulación horaria a ±0.07%; verificada en los libros GEPP):

```
reducción_facturable = min(Dmax_punta, E_útil / horas_bloque, P_bess)
ΔCapacidad = r_capacidad × reducción_facturable        (con el cap del umbral de Step 2)

horas_bloque: 2h (verano, 20–22h) para may–sep · 4h (invierno, 18–22h) para oct–abr
              (un mes que CONTIENE días de punta 4h usa 4h — el peor día ata: oct y abr)
E_útil = E_nominal × DoD × √RTE
```

**El insight de dimensionado:** cada kWh útil recorta demanda a `r_capacidad/2` en verano pero solo `r_capacidad/4` en invierno — **el kWh de verano vale el doble por hora de bloque**. El kWh marginal que solo trabaja en invierno es el primero que muere financieramente. De ahí la **regla verano-2h**: `E_útil = 2h × demanda punta promedio de verano (may–sep)`, a 0.5C (P = E_nominal/2, con lo que P nunca ata ni en N ni en Q). En invierno esa misma energía se reparte en rasurado plano E_útil/4 — cobertura parcial pero honesta.

**Incentivos partidos (deal 50/50):** el cliente recibe 50% del ahorro gratis → siempre quiere el BESS más grande; el inversionista paga el CAPEX → su TIR marginal cae bajo el WACC mucho antes. A nivel PROYECTO el kWh marginal puede seguir rentando (~18% en GEPP tamaño actual) mientras el inversionista está en VAN negativo — **el split decide el tamaño óptimo, no la física**. Alternativa simétrica a recortar: renegociar el split y conservar el tamaño grande.

**Checks de sanidad (calculator-grade):**
- Cap físico: `ΔCapacidad ≤ r_capacidad × Dmax_punta` — la demanda facturada no baja de cero. Un motor prorrateado puede violarlo (Proplasa Preforma 1: −$0.62M/año al corregir).
- Consistencia de datos: debe cumplirse `kWh_punta/día ≤ Dmax_punta × horas_bloque`; si la carga media en punta excede la "demanda máxima", una de las dos series está mal (pedir recibos CFE).

Herramienta: `tools/gepp_bess_scenarios.py` (réplica paramétrica del motor de los libros, verificada a 0.000% en R72/TIR; escenarios actual / verano-2h / eficiente-WACC). Caso completo: [[2026-07-07-gepp-bess-verano-resizing]].

---

## Limits of BESS alone

BESS alone **cannot:**
- Reduce energy charges (it only shifts demand timing; charging cost replaces generation cost)
- Provide energy savings on its own; must be combined with PV for that

BESS **can:**
- Reduce Dmax_punta and potentially Dmax_mensual
- Work in all seasons and all division types
- Stack with PV savings (see [[pv-bess-combined]])

---

## Related pages

- [[pv-bess-combined]] — the critical umbral interaction when PV and BESS are combined
- [[demanda-facturable]] — the umbral cap formula and the min() mechanics
- [[sae-cc]] — regulatory treatment of SAE-CC under CFE
- [[horarios-y-divisiones]] — which hours BESS must target by region/season
- [[rate-inputs]] — r_capacidad and r_distribucion values needed for savings calculation
- [[instalacion-bess]] — NOM-001-SEDE-2012 physical installation constraints: ventilation, disconnect, conduit, 120% bus rule
- [[bess]] — battery hardware catalog (BYD MC Cube, Huawei LUNA2000, SigenStack) for sizing the kWh/kW in this model
