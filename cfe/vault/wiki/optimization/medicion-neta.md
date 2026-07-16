---
title: "Medición Neta de Energía (Net Metering)"
type: concept
tags: [cfe, generacion-distribuida, compensacion, gdmth, solar]
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-04-res142-2017-gen-dist, 2026-06-08-pdse-2025-2039, 2026-06-09-autoconsumo-cne-2025]
---

# Medición Neta de Energía (Net Metering)

> **Purpose:** Defines the rules for how solar-generated energy is credited against GDMTH consumption under medición neta — the default compensation model for Generadores Exentos (now **< 700 kW**). Used by [[pv-savings-model]] for energy credit calculations.

The default compensation model for **[[generador-exento|Generadores Exentos]]** (distributed generation **< 0.7 MW**, updated 2025 — was ≤ 0.5 MW) in Mexico. Energy exported to the grid offsets energy consumed from the grid within the billing period. Surplus credits are carried forward for up to 12 months.

> **Citation:** RES/142/2017 (CRE, DOF 2017-03-07), Annex I — "Medición Neta de Energía."  
> **⚠ Capacity ceiling updated 2025:** Eligibility is now **< 0.7 MW** per Art. 25 de la Ley del Sector Eléctrico (DOF 18-mar-2025), confirmed in [[2026-06-08-pdse-2025-2039]] §2.2.3 — supersedes the 0.5 MW figure above. See [[generacion-distribuida]].  
> **⚠ Status:** The credit *mechanics* below (period netting, priority matrix, 12-month PML settlement) are from RES/142/2017 and not yet re-confirmed against the 2025 Ley. The [[2026-06-09-autoconsumo-cne-2025|CNE DACG (12‑XII‑2025)]] governs **only the ≥ 0.7 MW [[autoconsumo]] figure** (MEM settlement of Faltantes/Excedentes, CFE‑only sale) and is **silent on the < 0.7 MW exempt tier's credit mechanics** — so medición neta is *presumed intact* for the exempt path but unconfirmed against the 2025 LSE/RLSE. Verify before relying on the 12-month rule in a commercial proposal.

---

## Eligibility conditions

> **Citation:** RES/142/2017, main body and Annex II.

- User must be a **Generador Exento**: DG plant < 0.7 MW (updated 2025; was ≤ 0.5 MW)
- Must sign a **Contrato de Interconexión** with CFE Distribución
- Must sign a **Contrato de Contraprestación** with [[cfe-ssb]] selecting medición neta
- Must install bidirectional metering per CFE G0000-48 specification
- Plant connected at the same point as the supply contract

**Can a GDMTH user do this? Yes** — GDMTH is medium tension; special metering requirements apply (bidirectional meter; medium tension interconnection specs per Annex II).

---

## How the netting works (per billing period)

For each time-of-use period within the billing month:

```
EES = energy supplied by CFE to the user [kWh in this period]
ERG = energy received by CFE from the user [kWh in this period, i.e., exports]

Net_period = EES - ERG
```

- If `Net_period > 0` (net consumption): user is billed for `Net_period` kWh at the standard rate
- If `Net_period < 0` (net export): the `|Net_period|` kWh becomes an **energy credit** for that period

**Critical:** Netting happens **period by period** (punta vs. punta, intermedio vs. intermedio, etc.), not in aggregate across periods. You cannot net punta generation against base consumption in the same month — that happens only via the priority carry-forward system below.

---

## Credit carry-forward and priority application

Accumulated credits from previous periods are applied in the following strict priority order:

> **Citation:** RES/142/2017 Annex I, credit application matrix.

| Priority | Credit origin | Applied against | Rate conversion |
|---|---|---|---|
| 1 | Punta credit | Punta consumption | Same period — 1:1 |
| 2 | Punta credit | Intermedio consumption | Convert at r_punta/r_intermedio ratio |
| 3 | Punta credit | Base consumption | Convert at r_punta/r_base ratio |
| 4 | Intermedio credit | Punta consumption | Convert at r_intermedio/r_punta ratio |
| 5 | Intermedio credit | Intermedio consumption | Same period — 1:1 |
| 6 | Intermedio credit | Base consumption | Convert at r_intermedio/r_base ratio |
| 7 | Base credit | Punta consumption | Convert at r_base/r_punta ratio |
| 8 | Base credit | Intermedio consumption | Convert at r_base/r_intermedio ratio |
| 9 | Base credit | Base consumption | Same period — 1:1 |

**Cross-period conversion:** When a credit is applied to a different period, the kWh are converted to "equivalent kWh" using the ratio of the credit's origin rate to the current period's rate. This accounts for rate changes over time.

```
credit_kWh_equivalent = credit_kWh_original × (r_origin_period / r_current_period)
```

**Implication:** 1 kWh of punta credit is worth more than 1 kWh of base credit when applied across periods. Punta credits should be exhausted first.

---

## Credit expiration — 12-month rule

Credits not fully applied within **12 calendar months** from the month they were generated expire and are settled in cash:

```
Cash_settlement = expired_credit_kWh × PML_average
```

Where PML = Precio Marginal Local (average spot price at the node) for the interval the credit was created.

**In practice:** PML is typically well below the retail GDMTH rate. Expired credits are worth significantly less than credits applied against consumption. Oversizing the PV system relative to consumption leads to excess credits → expiration → low-value settlement.

> **Citation:** RES/142/2017 Annex I. PML settlement mechanism cited.

---

## Demand charges under medición neta

**Net metering does NOT reduce demand charges directly.** The demand charges (capacidad, distribución) are based on Dmax_punta and Dmax_mensual — the peak power drawn from the grid — not on energy consumption.

**Indirect effect:** By reducing `kWh_red` (net consumption), PV lowers the umbral cap. This can reduce billed demand if the site was cap-constrained. See [[pv-savings-model]] §Step 4.

---

## Comparison with other compensation models

| Feature | Medición Neta | Facturación Neta | Venta Total |
|---|---|---|---|
| Period netting | Within billing month | Within billing month | No netting |
| Surplus treatment | Credit forward 12 months | Cash settlement monthly | All generation sold |
| Settlement price | PML (at expiration) | PML monthly | PML monthly |
| Best for | Users with monthly net consumption | Users who regularly export | Users who want to maximize generation revenue |
| GDMTH most common? | ✓ Yes — default choice | Rare | Rare for rooftop |

> **Citation:** RES/142/2017, Annex I (medición neta), Annex II (facturación neta), Annex III (venta total).

---

## Related pages

- [[pv-savings-model]] — uses this credit mechanism to compute energy savings
- [[autoconsumo]] — the alternative scheme for larger or permit-based installations
- [[scheme-comparison]] — when medición neta beats autoconsumo and vice versa
- [[generador-exento]] — the legal status required to access medición neta
- [[horarios-y-divisiones]] — period definitions that determine which credits are generated
