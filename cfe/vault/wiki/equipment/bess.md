---
title: "BESS — Battery Storage"
type: concept
tags: [equipment, storage, bess]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# BESS — Battery Storage

Battery energy storage systems we hold datasheets for, spanning **modular cabinet**
(stackable, ~12–253 kWh) to **utility container** (~215 kWh → 6 MWh). All **LFP
(LiFePO4)** chemistry. In a GDMTH context the BESS is the dominant savings lever — it
shaves `Dmax_punta` and arbitrages energy ([[bess-savings-model]], [[sae-cc]]). For the
Posadas analysis the modeled system was **2940 kWh / 1503 kW**
([[2026-06-08-780881200029-yearly-savings]]) — BYD MC Cube-T MC12C class. Install per
[[instalacion-bess]] (Art. 480/690-H ventilation, disconnect, conduit).

## Comparison

| Spec | BYD MC Cube-T (MC12C-B6012) | Huawei LUNA2000-215-2S10 | Sigen SigenStack (BAT 12.0) |
|---|---|---|---|
| Form factor | utility container | smart string ESS cabinet | modular stack |
| Usable energy | 6012 kWh (also 501 / 5010 variants) | 215 kWh | 12.06 kWh/module → 48–84 kWh/stack, 253 kWh/system |
| Nominal power | 2×1503 kW | 108 kW (PCS2000-108K) | via [[hybrid-inverters]] (55–137 kW) |
| Cell / chemistry | LFP, 1P416S | LFP, 280 Ah, 240S1P, 4 packs | LFP, 314 Ah |
| RTE | (cell-level) | 91.3% incl. auxiliaries | 0.5C nominal, 1C max |
| DoD | — | 0–100% | — |
| Cycle life | long-life LFP | — | 10,000 cycles |
| Cooling | liquid | hybrid (liquid+air) | smart air |
| Battery voltage | 1081.6–1489.3 V DC | 648–864 V | 550–1100 V (BC) |
| Temp range | −30…+55 °C | −30…+55 °C | −20…+55 °C |
| IP / noise | IP55 / ≤75 dBA | IP55 / ≤65 dB | IP66 / <70 dB |
| Fire safety | fire alarm system, LFP | pack O2 barrier, gas exhaust, aerosol | aerosol, smoke sensor, exhaust |
| Comms | Modbus TCP/IP (CAN on 501) | Modbus TCP, Ethernet/fiber | CAN |
| PCS | external | **integrated** (PCS2000-108K-MB1) | external (Sigen hybrid) |

Raw: `raw/pdfs/2025-07-01 - Sistema almacenamiento BYD MC CUBE T ESS ...pdf`,
`2025-07-02 - Sistema de almacenamiento huawei Luna2000 215 2s10.pdf`,
`2025-07-02 - sistema de almacenamiento SigenStack 12 kWh Ficha Tecnica (1).pdf`.

## Selection notes
- **BYD MC Cube-T** — utility container, all-in-one (controller + HVAC + LFP + fire), liquid-cooled. The MC12C ≈ 6 MWh / 2×1503 kW; the **MC10C (5010 kWh / 2×1253 kW)** and **MC-B501 (501 kWh / 250 kW)** are the smaller siblings. The 1503 kW power rating is exactly the Posadas BESS power assumption — this is the reference container class for that analysis.
- **Huawei LUNA2000-215** — cabinet-scale "smart string ESS" with **integrated 108 kW PCS** and 91.3% round-trip; modular for stacking to a few MWh. Cleanest drop-in where 100–200 kW peak-shave is needed without a full container.
- **SigenStack** — modular 12 kWh blocks (4–21 pcs), DC-coupled to a Sigen [[hybrid-inverters|hybrid inverter]]; small/mid C&I, up to 253 kWh.
- Altitude derate (BYD <2000 m) and ambient derate (<-15/>+45 °C) matter for highland Mexican sites — Cancún (sea level, hot) is fine on energy but watch the >45 °C power derate.

## Related
- [[bess-savings-model]] — how kWh/kW translate to demand + arbitrage savings
- [[pv-bess-combined]] — combined PV+BESS additivity
- [[sae-cc]] — SAE-CC regulatory treatment (battery at load center, no permit)
- [[hybrid-inverters]] — Sigen PCS for SigenStack
- [[instalacion-bess]] — NOM-001-SEDE Art. 480/690-H install rules
- [[2026-06-08-780881200029-yearly-savings]] — BESS sizing in a real case

## Open questions
- BYD MC Cube cycle-life / RTE figures at system level (datasheet gives cell-level only).
