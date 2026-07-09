---
title: "Hybrid Inverters"
type: concept
tags: [equipment, inverter, storage]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Hybrid Inverters

**Sigen Hybrid Inverter** — a single C&I unit that does PV MPPT **and** battery
charge/discharge (DC-coupled), 50–125 kW. This is the integrated alternative to a
[[string-inverters|PV string inverter]] + separate [[bess]] PCS: one box, battery-ready,
parallels to MW scale via the Sigen Energy Gateway. Pairs natively with the SigenStack
battery (see [[bess]]). Relevant where PV + peak-shaving BESS are deployed together —
the [[bess-savings-model]] / [[pv-bess-combined]] use case.

## Two variants

| Spec | Sigen 50–125 M1-HYA | Sigen 50–110 M1-HYB |
|---|---|---|
| Role | grid-tie hybrid (on-grid) | hybrid **with backup** (0 ms switchover) |
| Rated AC | 50/60/80/100/110/125 kW | 50/60/80/100/110 kW |
| Backup / off-grid | — | 0 ms disruption, 150% overload 10 s |
| Max efficiency | 98.6–98.8% | 98.3% |
| Dimensions | 918×640×340 mm | 1110×668×348 mm |
| Weight | 78 kg | 105 kg |

## Common platform specs

| Spec | Value |
|---|---|
| Max PV input | 100–220 kWp (by model) |
| Max DC voltage | 1100 V |
| Nominal DC | 600 V @380/400 Vac; 720 V @480 Vac |
| MPPT range | 160–1000 V |
| MPP trackers | 4–8 (by model), 2 strings/MPPT |
| Max input/short-circuit per MPPT | 40 A / 60 A |
| Battery | SigenStack BAT 12.0, 4–21 pcs (→ up to ~253 kWh) |
| Max charge/discharge | 55–137.5 kW (by model) |
| AC output | 380/400/480 V, 3W+(N)+PE, 50/60 Hz |
| Protections | AFCI, anti-islanding, Type II DC/AC SPD, insulation + RCM, AC OC/OV/SC |
| IP / cooling | IP66 / smart air |
| Comms | WLAN / Ethernet / RS485 / Sigen CommMod (4G) |
| Altitude | 5000 m (derate >4000 m) |

Raw: `raw/pdfs/2025-07-02 - Inversor hybrido Sigen PV 50_60_80_100_110_125M1 Datasheet (1).pdf`,
`...Sigen C&I Hybrid Inv Ficha Tecnica HYB (1).pdf`,
`...Sigen Hybrid Inverter TP HYA Ficha Tecnica (1).pdf`.

## Selection notes
- **HYA** = standard on-grid hybrid (PV + battery cycling for arbitrage/peak-shave, no UPS function). **HYB** = adds **0 ms backup** + 150% surge — choose it where the site needs ride-through, at a size/weight penalty.
- DC-coupled with SigenStack is the tidy small/mid-C&I PV+BESS package; for large container BESS (Posadas scale) the [[string-inverters|string PV]] + [[bess|standalone BESS]] (LUNA2000 / MC Cube) split is usually cheaper per kWh.
- 480 V output matches CFE MT step-down transformers (see [[2026-06-08-cfe-transformer-norms]]).

## Related
- [[bess]] — SigenStack battery modules this inverter drives
- [[bess-savings-model]] / [[pv-bess-combined]] — the savings rationale
- [[string-inverters]] — PV-only alternative (separate PCS for storage)
- [[instalacion-bess]] — battery-room install rules
