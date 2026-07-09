---
title: "Microinverters"
type: concept
tags: [equipment, inverter, mlpe]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Microinverters

Module-level power electronics (MLPE): one small inverter per 2–4 panels, AC output
trunked on the roof. Used on small C&I / residential jobs and shade-prone or
multi-orientation roofs where per-module MPPT beats a [[string-inverters|string inverter]].
Each pairs with a vendor gateway in [[monitoring]] (APsystems → ECU-R, Hoymiles → DTU).
Rapid-shutdown / arc-fault compliance is inherent (NEC 690.11/690.12), aligning with
[[instalacion-pv-interconectada]].

## Comparison

| Spec | APsystems YC600 | APsystems DS3D | Hoymiles HMS-2000-4T |
|---|---|---|---|
| Modules per unit | 2 | 2 (→4 panels) | 4-in-1 |
| Module power range | 200–365 Wp | 315–670 Wp+ | 400–625 Wp+ |
| Max output (AC) | 548 VA | 2000 W | 2000 VA |
| Nominal AC voltage | 240 V | 240 V | 220/230/240 V |
| Max input current | 12 A × 2 | 20 A × 2 | 4 × 14 A |
| MPPTs | 2 | 2 | 4 |
| Peak efficiency | 96.5% | 97% | 96.5% (CEC) |
| Comms | Zigbee → ECU | Zigbee → ECU | Sub-1G → DTU |
| Max units/branch | 7 | 3 | 3–4 (10AWG) |
| Enclosure | NEMA6 / IP | Type 6 | IP67 / NEMA6 |
| Temp range | −40…+65 °C | −40…+65 °C | −40…+65 °C |
| Compliance | UL1741 SA, CA Rule 21, IEEE1547 | UL1741, NOM-001 | EN50549, VDE-AR-N4105, UL1741 |

Raw: `raw/pdfs/2025-06-30 - APS YC600-Microinversor.pdf`,
`...Micro inversor APS DS3D-2000-220.pdf`,
`...microinversor HMS-2000 DE 2000W 220V.pdf`
(+ `...microinversor HMS - AC Trunk Connector.pdf` for the AC trunk cabling).

## Selection notes
- **DS3D / HMS-2000** (2000 W) match today's 500–625 Wp panels ([[pv-modules]]); the older **YC600** (548 VA) is sized for ≤365 Wp modules — undersized for our 720 Wp stock, so YC600 is legacy/repower only.
- Microinverters carry a per-watt premium over [[string-inverters]] — justify them on shade, complex roofs, or module-level monitoring needs, not on Posadas-scale flat rooftops.
- DS3D explicitly lists **NOM-001** compliance (Mexico).

## Related
- [[pv-modules]] — DC source (watch the module-power ceiling per micro)
- [[monitoring]] — ECU-R (APsystems) / DTU-Lite-S (Hoymiles) gateways
- [[string-inverters]] — the alternative for large uniform arrays
- [[instalacion-pv-interconectada]] — rapid shutdown & anti-islanding
