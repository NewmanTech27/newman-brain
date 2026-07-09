---
title: "String Inverters"
type: concept
tags: [equipment, inverter]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# String Inverters

Grid-tie **Huawei SUN2000** smart string inverters, transformerless, the workhorse for
CFE-interconnected C&I PV. All are pure PV inverters (no battery port except the L1
residential unit) — for PV+storage in one box see [[hybrid-inverters]]; to add a battery
to these, pair with a separate [[bess]] PCS. Anti-islanding + Type II SPD on every model
satisfies the grid-tie safety requirements in [[instalacion-pv-interconectada]].

## Comparison

| Spec | SUN2000-20KTL-M3 | SUN2000-30/36/40KTL-M3 | SUN2000-100KTL-M1 | SUN2000-150K-MG0 | SUN2000-2–6KTL-L1 |
|---|---|---|---|---|---|
| Class | small C&I | C&I | large C&I/utility | large C&I/utility | residential (1-φ, hybrid) |
| Rated AC | 20 kW | 30/36/40 kW | 100 kW | 150 kW | 2–6 kW |
| Max apparent | 22 kVA | 33/40/44 kVA | 110 kVA | 165 kVA | 2.2–6 kVA |
| Max efficiency | 97.6% | 98.7% | 98.8% @480 V | 98.8% @480 V | 98.4% |
| Euro efficiency | 97.2% | 98.4% | 98.6% | 98.4% | 96.7–97.8% |
| MPPTs / inputs | 4 / 8 | 4 / 8 | 10 / 20 | 7 / 21 | 2 / 2 |
| Max DC voltage | 1100 V¹ | 1100 V | 1100 V | 1100 V | 600 V |
| MPPT range | 200–1000 V | 200–1000 V | 200–1000 V | 200–1000 V | 90–560 V |
| AC voltage | 208/220 V 3W | 400/480 V 3W | 380/400/480 V | 380/400/480 V | 220/230/240 V 1-φ |
| Battery port | no | no | no | no | **yes** (LG / Huawei ESS) |
| Dimensions | 640×530×270 | 640×530×270 | 1035×700×365 | 1000×710×395 | 365×365×156 |
| Weight | 43 kg | 43 kg | 90 kg | 102 kg | 12 kg |
| IP / cooling | IP66 / natural | IP66 / natural | IP66 / smart air | IP66 / smart air | IP65 / natural |
| Protections | AFCI, anti-isla, Type II SPD, RCMU, PID recovery | same | same + I-V diag | same + ground-fault, terminal-temp | same + arc, reverse-charge |

¹ The 20KTL-M3 LATAM sheet lists 1100 V max input (one variant prints 1000 V — confirm by nameplate).

Raw: `raw/pdfs/2025-06-30 - Inversor HUAWEI_SUN2000-20KTL-M3.pdf`,
`...30-36-40KTL-M3_MX.pdf`, `2025-07-02 - Inversor Huawei SUN2000-100KTL-M1.pdf`,
`...Inversro Huawei 150 SUN2000-150-MG0.pdf` (preliminary),
`2025-06-30 - smart energy center HUAWEI-SUN2000-2-6KTL-L1.pdf`.

## Selection notes
- **100KTL / 150K** are the units for Posadas-scale rooftops (≥100 kW PV): 10/7 MPPTs handle many sub-arrays, smart air cooling, 480 V output matches MT step-down.
- **20–40KTL-M3** suit 20–250 kW jobs; identical footprint, natural convection (quiet, no fan maintenance).
- **2–6KTL-L1** is really a single-phase hybrid for homes/very small loads — carries a battery port (LG RESU / Huawei ESS); don't use on 3-phase GDMTH.
- DC strings: with 1100 V max input and ~49 V Voc modules ([[pv-modules]]), keep strings ≤ ~20 modules cold. Each string protected per [[protection-bos]].

## Related
- [[pv-modules]] — DC source
- [[hybrid-inverters]] — when one box must do PV + battery
- [[bess]] — external PCS/battery to pair with these PV-only units
- [[monitoring]] — SmartLogger3000A ([[monitoring]]) is the matching datalogger
- [[instalacion-pv-interconectada]] — anti-islanding / interconnection rules

## Open questions
- 20KTL-M3 max DC input (1000 vs 1100 V) — variant-dependent.
