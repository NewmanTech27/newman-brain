---
title: "PV + BESS Combined Model — Interaction Effects and Optimal Strategy"
type: concept
tags: [cfe, gdmth, solar, bess, umbral, savings-model, combined]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024]
---

# PV + BESS Combined Model — Interaction Effects and Optimal Strategy

> **Purpose:** Models how PV and BESS interact when installed together on a GDMTH site. The key insight is that PV can reduce the umbral cap, which changes (and sometimes neutralizes) the demand savings available to BESS. The calculator must account for this interaction to give accurate combined savings.

---

## The core interaction: PV lowers the umbral, constraining BESS

> **Status:** ⚠ Logical consequence of the umbral formula — not explicitly stated in any regulation, but follows directly from A/158/2024 §5.1 and the definition of kWh_red in net metering.

When PV is installed under medición neta, `kWh_red` = net consumption after solar offsets. Every kWh of solar applied reduces `kWh_red`, which reduces the umbral:

```
umbral_with_PV = (kWh_red_without_PV - kWh_solar_applied) / (d × 0.57 × 24)
              = umbral_without_PV - kWh_solar_applied / (d × 0.57 × 24)
```

Simultaneously, BESS reduces `Dmax_punta`:
```
Dmax_punta_with_BESS = Dmax_punta_without_BESS - P_bess_effective
```

The combined billed demand is:
```
billed_capacidad = min(Dmax_punta_with_BESS, umbral_with_PV)
                 = min(Dmax_punta - P_bess_effective, umbral - ΔUmbral_PV)
```

---

## Four scenarios for combined PV+BESS

**Setup variables:**
- `D` = Dmax_punta without any technology
- `U` = umbral without any technology
- `ΔU_pv` = reduction in umbral due to PV (= kWh_solar_applied / 410.4 for a 30-day month with FC=0.57)
- `B` = P_bess_effective (kW reduction from battery)

| Scenario | Condition | Billed demand | BESS effective? | PV demand effect? |
|---|---|---|---|---|
| 1. Demand binds, no tech | D < U | D | — | — |
| 2. Umbral binds, no tech | D > U | U | BESS must push D below U to save | PV lowers U → more savings |
| 3. PV + BESS, D < U | D - B < U - ΔU_pv | D - B | ✓ Full BESS savings | None (demand binding) |
| 4. PV makes umbral bind harder | D - B > U - ΔU_pv | U - ΔU_pv | Partially effective | ✓ PV contributes |

**The dangerous scenario — PV neutralizes BESS:**

If initially D > U (umbral binds), and BESS alone would have brought D below U, but PV simultaneously lowers U below the new D-B:

```
Before any tech: billed = U
With BESS only: billed = min(D-B, U) = D-B (if D-B < U; demand now binds)  → BESS saves (U - (D-B))
With PV only: billed = U - ΔU_pv  → PV saves ΔU_pv × r_capacidad
With PV+BESS: billed = min(D-B, U-ΔU_pv)
  If D-B < U-ΔU_pv: billed = D-B  → same as BESS only; PV adds zero demand savings
  If D-B > U-ΔU_pv: billed = U-ΔU_pv → same as PV only; BESS adds zero demand savings beyond PV
```

**Practical implication:** Installing both PV and BESS does NOT simply add their individual demand savings. The combined savings are `max(savings_PV_alone, savings_BESS_alone)` in many cases — not the sum.

---

## Combined demand savings formula

```
billed_before = min(D, U)

billed_after_combined = min(D - B, U - ΔU_pv)

ΔCapacidad_combined = max(0, billed_before - billed_after_combined) × r_capacidad
```

**Decomposing the savings:**
```
ΔCapacidad_PV_only    = max(0, billed_before - min(D, U - ΔU_pv)) × r_capacidad
ΔCapacidad_BESS_only  = max(0, billed_before - min(D - B, U))     × r_capacidad
ΔCapacidad_combined   = max(0, billed_before - min(D - B, U - ΔU_pv)) × r_capacidad

Interaction_effect = ΔCapacidad_combined - (ΔCapacidad_PV_only + ΔCapacidad_BESS_only)
```

The interaction effect is **negative** (reduces combined savings) when both technologies would independently bring billed demand below the same binding constraint.

---

## Energy savings: fully additive

Unlike demand savings, energy savings from PV (reduced kWh × energy rates) are additive with any BESS effects. BESS shifts when energy is consumed, not how much. PV reduces total energy consumed from the grid.

```
ΔEnergy_combined = ΔEnergy_PV + ΔEnergy_BESS_charging_cost_savings
```

BESS can also be charged from solar (via DC coupling or inverter) during peak solar hours, then discharged during evening punta — this allows the battery to save both the punta energy rate AND the charging cost from the grid.

**Solar-charged BESS cycle:**
```
value_of_cycle = kWh_discharged × r_capacidad × (kW_reduction_per_kWh)
              + kWh_discharged × r_punta           (displaced punta energy from storage)
              - kWh_solar_to_battery × r_intermedio  (opportunity cost of not exporting)
```

---

## Optimal strategy summary by constraint type

| Site type | Condition | Recommended strategy |
|---|---|---|
| **Demand-bound** | Dmax_punta < U (umbral not binding) | BESS is fully effective. PV helps with energy savings but minimal demand benefit. Add BESS first. |
| **Umbral-bound** | Dmax_punta > U | Either PV or BESS can reduce billed demand, but they compete for the same cap reduction. Analyze which has better ROI per peso invested. |
| **Heavily cap-bound** | D >> U | Reducing kWh_red (PV) lowers U and saves demand charges without any peak shaving. Large PV can be the demand reduction lever. |
| **BCS summer** | 10h punta, large BESS needed | Very large battery required for full punta coverage. PV during punta (midday) is highly valuable; solar-charged BESS is optimal. |
| **SIN winter** | 4h evening punta | BESS charged during morning base hours, discharged 18:00–22:00. PV helps with energy but not demand (solar ends before punta). |

---

## Complete combined bill impact

```
Bill_combined = Bill_baseline
  - ΔEnergy_PV                           (energy charge reduction from solar)
  - ΔCapacidad_combined × r_capacidad    (demand savings, capped by interaction)
  - ΔDistribucion_combined × r_distribucion
  + Charging_cost_BESS                   (added grid consumption for charging if no solar)
```

---

## Related pages

- [[pv-savings-model]] — PV savings in detail
- [[bess-savings-model]] — BESS savings in detail
- [[demanda-facturable]] — the umbral formula that creates the interaction
- [[medicion-neta]] — how net metering changes kWh_red (the key input to the umbral)
- [[scheme-comparison]] — PV+BESS economics under medición neta vs. autoconsumo
