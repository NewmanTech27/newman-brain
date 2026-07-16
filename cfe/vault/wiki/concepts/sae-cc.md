---
title: "SAE-CC — Almacenamiento en Centro de Carga"
type: concept
tags: [sae, almacenamiento, gdmth, demanda, centro-de-carga]
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-04-dacg-sae-a113-2024, 2026-06-09-autoconsumo-cne-2025]
---

# SAE-CC — Sistema de Almacenamiento de Energía en Centro de Carga

The battery storage modality most relevant to commercial and industrial users on the [[gdmth]] tariff. A SAE-CC is a battery system installed at a **load center** (Centro de Carga) — no associated generation plant, no grid injection. The battery charges from the grid and discharges to serve the site's own demand.

Defined in **Acuerdo A/113/2024** (DACG SAE), Chapter IV.

## Key regulatory features

| Feature | Rule |
|---|---|
| Grid injection | Prohibited — energy stored serves only the site's own load |
| Generation permit | Not required (under CFE SSB / Suministro Básico) |
| Battery power (Potencia SAE) | Counts as part of contracted demand or maximum demand |
| Maximum demand constraint | Grid withdrawal cannot exceed contracted demand; if it does, Distribución requests connection studies |
| CRE notification | Required within **90 business days** of installation (medium/high tension only) |
| CEL obligations | Not affected — SAE-CC neither earns nor owes Certificados de Energías Limpias |

## Billing impact on GDMTH

Under [[gdmth]], demand charges are calculated from:
- **Capacity charge**: based on Dmax_punta (peak demand coincident with punta period)
- **Distribution charge**: based on Dmax_mensual (monthly maximum demand in any 15-min interval)

A SAE-CC battery, discharged strategically during [[horarios-y-divisiones|punta hours]], **directly reduces Dmax_punta** and potentially Dmax_mensual, reducing both demand charge components.

**Example logic:**
- Without battery: user draws 500 kW during punta → Dmax_punta = 500 kW
- With 200 kW battery discharging during punta: user draws 300 kW from grid → Dmax_punta = 300 kW
- Capacity charge savings = 200 kW × capacity rate ($/kW-mes)

The value depends on:
1. The regional punta window duration (2h/day in most of Mexico → limited charge/discharge cycles needed; 10h/day in BCS → requires larger battery)
2. The capacity charge rate ($/kW-mes) — not yet in this wiki
3. The user's demand profile (flat vs. peaky)

## Operational requirements

Per the regulation:
- Battery power must not exceed contracted demand at any moment
- If maximum demand exceeds contracted demand in any billing period, CENACE/Distribución will trigger connection studies
- If adding a large battery would push contracted demand higher, the user must adjust their contract with CFE SSB

## CRE notification (medium/high tension users)

Required information for the 90-day notification:
- User identification data
- Technical spec sheet: storage technology, Potencia SAE (kW/MW), Energía Disponible (kWh/MWh), dimensions, weight, temperature ranges, efficiency, communications, protections
- Battery location
- Single-line diagram
- Connection point
- Statement confirming no grid injection

## New 2025 role: mandatory backup for intermittent Autoconsumo (≥ 0.7 MW)

Beyond the demand‑savings case, the **2025 [[autoconsumo]] regime gives SAE a regulatory mandate**. An intermittent (PV/eólico) Autoconsumo plant **≥ 0.7 MW** going interconnected **must** carry *respaldo propio* — a **SAE** or a contracted ramp/intermittency/variability backup service from [[cfe]] (LSE art. 32‑III; RLSE art. 59; DACG Num. 4.5, via [[2026-06-09-autoconsumo-cne-2025]]). For projects scaling PV past the exempt line, storage is therefore **required, not just economic**. (This SAE is a storage *figure* under LSE art. 3‑L; the A/113/2024 SAE‑CC *load‑center* modality below is the no‑injection, no‑permit form most GDMTH users use under 0.7 MW.) The same battery that satisfies the backup mandate also shaves Dmax_punta — see [[bess-savings-model]].

## SAE-CC + Solar DG combination

A [[generacion-distribuida|solar DG]] plant (net metering) combined with a SAE-CC battery:
- Solar + [[medicion-neta|net metering]] reduces energy charges (kWh billed)
- SAE-CC battery (charged from solar or off-peak grid) reduces demand charges (kW billed)
- Together they address both major cost components of a GDMTH bill

See [[2026-06-04-dacg-sae-a113-2024]] section 2.1 for the regulatory treatment of combined systems.

## Technical installation requirements

The regulatory modality (A/113/2024) defines *what* a SAE-CC is and how it is billed. The physical installation is governed by:

- **Art. 480** (stationary batteries): ventilation required for vented cells; disconnect mandatory for >50V systems, within sight; rigid conduit required in battery room; lead-acid >48V must use non-conductive enclosures
- **Art. 690 Part H** (batteries in PV systems, if combined with solar): charge control required; for residential, max 48V battery; >48V requires ground-fault monitoring
- **Art. 705** (grid interconnection): certified inverter required; 120% bus rule applies; anti-islanding (705-40) required

See [[instalacion-bess]] and [[instalacion-pv-interconectada]] for the full technical layer.

## Related concepts

- [[sae-modalidades]] — all four SAE integration modalities
- [[autoconsumo]] — the ≥ 0.7 MW figure where SAE is a *mandatory* intermittency backup
- [[bess-savings-model]] — how the same battery shaves demand charges
- [[gdmth]] — the tariff where demand charge reduction is most directly applicable
- [[demanda-facturable]] — the formulas that determine which demand value is billed
- [[generacion-distribuida]] — complementary technology for energy charge reduction
- [[medicion-neta]] — the compensation model for solar DG, works alongside SAE-CC
- [[instalacion-bess]] — NOM-001-SEDE-2012 Art. 480 + 690-H: physical installation requirements for BESS
- [[instalacion-pv-interconectada]] — NOM-001-SEDE-2012 Art. 690 + 705: PV and grid-tie installation rules

## How sources treat this

- [[2026-06-04-dacg-sae-a113-2024]]: Chapter IV defines the full SAE-CC framework; key point is no injection and no permit under SSB

## Open questions

- What are the typical investment economics for a SAE-CC battery at a 500 kW GDMTH user in Mexico (2025)?
- Is there a minimum battery capacity that makes economic sense given the 2-hour punta window in most regions?
- How does the SAE-CC interact with the GDMTH minimum monthly charge (the basic supplier operation charge)?
