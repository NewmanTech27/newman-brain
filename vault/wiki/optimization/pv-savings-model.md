---
title: "PV Savings Model — How Solar Changes the GDMTH Bill"
type: concept
tags: [cfe, gdmth, solar, pv, medicion-neta, savings-model]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-gdmth, 2026-06-04-res142-2017-gen-dist, 2026-06-04-acuerdo-a158-2024]
---

# PV Savings Model — How Solar Changes the GDMTH Bill

> **Purpose:** Complete model for computing how a rooftop PV system reduces a GDMTH bill under medición neta. Covers energy savings by period, demand savings via the umbral effect, and the limits of PV alone.

---

## Assumptions / scope

- PV plant < 0.7 MW (Generador Exento, no CRE permit required — ceiling raised from 0.5 MW in 2025; see [[generacion-distribuida]])
- Compensation model: [[medicion-neta]] (default; net metering with period-by-period credits)
- No battery storage (PV only; see [[pv-bess-combined]] for PV+BESS)

> **Citation:** Generador Exento framework defined in RES/142/2017; medición neta rules in RES/142/2017 Annex I.

---

## Step 1 — Classify solar generation by period

Solar generation is time-stamped. Each kWh generated must be assigned to the period it falls in, per the [[horarios-y-divisiones]] schedule for the user's division and season.

**Define:**
- `kWh_solar_punta` — solar kWh generated during punta hours
- `kWh_solar_inter` — solar kWh generated during intermedio hours
- `kWh_solar_base` — solar kWh generated during base hours
- `kWh_solar_total` = sum of above

**Key insight — period allocation by system:**

| System | Summer solar (10:00–16:00) period | Winter solar (10:00–16:00) period |
|---|---|---|
| BC | Intermedio (0:00–14:00), then Punta (14:00–18:00) | Intermedio |
| BCS | Punta (12:00–22:00 on weekdays) | Intermedio |
| SIN | Intermedio (punta not until 20:00) | Intermedio |

For SIN users: virtually all solar generation during peak sun hours falls in intermedio, not punta. Punta solar is negligible unless the user operates evening loads with battery storage.

---

## Step 2 — Compute net energy consumption by period

Under medición neta, the meter records net flow per period:

```
kWh_red_punta = max(0, kWh_consumed_punta - kWh_solar_punta)
kWh_red_inter = max(0, kWh_consumed_inter - kWh_solar_inter)
kWh_red_base  = max(0, kWh_consumed_base  - kWh_solar_base)
```

When solar exceeds consumption in a period, the surplus is exported:
```
kWh_export_punta = max(0, kWh_solar_punta - kWh_consumed_punta)
kWh_export_inter = max(0, kWh_solar_inter - kWh_consumed_inter)
kWh_export_base  = max(0, kWh_solar_base  - kWh_consumed_base)
```

Exported energy becomes **credits** under medición neta, applied to future bills per the priority matrix in [[medicion-neta]].

> **Status:** ⚠ Inferred from net metering mechanics (RES/142/2017 Annex I); the per-period net formula is not explicit in the regulation but is the definitional meaning of "medición neta por periodo."

> **Citation:** RES/142/2017 Annex I: "La Medición Neta de Energía es la medición por periodo de la energía neta entendida como la diferencia entre la energía suministrada al usuario por el Suministrador (EES) y la energía recibida del usuario (ERG)."

---

## Step 3 — Compute energy charge savings

```
ΔE_punta     = kWh_solar_punta_applied × r_punta
ΔE_inter     = kWh_solar_inter_applied × r_intermedio
ΔE_base      = kWh_solar_base_applied  × r_base
ΔE_transmis  = kWh_solar_applied_total × r_transmision
ΔE_cenace    = kWh_solar_applied_total × r_cenace
ΔSCNMEM      = kWh_solar_applied_total × 0.0062

ΔEnergy_total = ΔE_punta + ΔE_inter + ΔE_base + ΔE_transmis + ΔE_cenace + ΔSCNMEM
```

Where `kWh_solar_applied` = kWh that offset consumption this period (not excess credited forward).

**Value per kWh of solar generation:**
- 1 kWh generated during punta hours: saves r_punta + r_transmision + r_cenace + 0.0062
- 1 kWh generated during intermedio: saves r_intermedio + r_transmision + r_cenace + 0.0062
- 1 kWh generated during base: saves r_base + r_transmision + r_cenace + 0.0062

> **This is why BC and BCS summer solar is more valuable than SIN solar** — in BC/BCS summer, midday solar falls in punta or covers punta consumption, while in SIN, midday solar is only intermedio value.

---

## Step 4 — Demand charge savings from PV (the umbral effect)

> **Status:** ⚠ Logical consequence of the demanda facturable formula — not stated explicitly in any regulation, but follows directly from the umbral formula.

PV reduces `kWh_red` (total grid consumption). Since the umbral depends on `kWh_red`:

```
umbral_without_PV = kWh_red_without_PV / (d × 0.57 × 24)
umbral_with_PV    = kWh_red_with_PV    / (d × 0.57 × 24)

Δumbral = umbral_without_PV - umbral_with_PV = kWh_solar_applied_total / (d × 0.57 × 24)
```

**Demand savings from PV depend on which constraint was binding:**

| Scenario | Before PV | After PV | Demand savings |
|---|---|---|---|
| Cap was already binding (Dmax > umbral) | Billed = umbral_old | Billed = umbral_new | Δumbral × r_capacidad and Δumbral × r_distribucion |
| Measured demand was binding (Dmax ≤ umbral) | Billed = Dmax | Billed = Dmax (unchanged) | 0 — PV does not reduce measured peak |
| PV brings umbral below Dmax (transition) | Billed = Dmax | Billed = new umbral < Dmax | Partial savings once umbral drops below Dmax |

**Example:**
```
Without PV:
  kWh_red = 100,000 kWh, Dmax_punta = 350 kW, d = 30
  umbral = 100,000/(30×0.57×24) = 243.7 kW  → cap binds → billed = 243.7 kW

With PV (20,000 kWh_solar applied):
  kWh_red = 80,000 kWh, Dmax_punta = 350 kW (unchanged — peak was at night)
  umbral = 80,000/410.4 = 195.0 kW  → cap still binds → billed = 195.0 kW
  Demand savings = (243.7 - 195.0) × r_capacidad = 48.7 kW × r_capacidad
```

---

## Step 5 — Total PV savings

```
ΔBill_PV = ΔEnergy_total + ΔCapacidad + ΔDistribucion

ΔCapacidad    = max(0, billed_capacidad_before    - billed_capacidad_after) × r_capacidad
ΔDistribucion = max(0, billed_distribucion_before - billed_distribucion_after) × r_distribucion
```

---

## Limits of PV alone

PV alone **cannot:**
- Reduce Dmax_punta directly (unless solar is generating precisely during the peak demand event)
- Reduce demand charges if measured demand is already below the umbral
- Provide demand savings in SIN winter evenings (punta is 18:00–22:00, after solar generation)

PV can **accidentally** reduce effective demand savings for BESS if it lowers the umbral below what BESS alone would achieve — see [[pv-bess-combined]] for the interaction.

---

## Related pages

- [[solar-yield-lookup]] — how to get kWh/kWp for a given CFE bill address (CP → municipality → yield)
- [[solar-resource-data]] — the quality/uncertainty behind the yield number (bankability)
- [[pv-degradation]] — the annual derate that lowers generation over the 20-yr horizon
- [[pv-modules]] — candidate modules and their nameplate/warranty
- [[medicion-neta]] — the net metering credit mechanism
- [[bess-savings-model]] — the demand savings component that PV alone misses
- [[pv-bess-combined]] — umbral interaction when both are present
- [[horarios-y-divisiones]] — which hours solar generation falls into by region
- [[demanda-facturable]] — the umbral formula used in demand savings calculation
