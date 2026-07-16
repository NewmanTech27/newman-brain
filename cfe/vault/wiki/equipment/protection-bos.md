---
title: "Protection & Balance-of-System"
type: concept
tags: [equipment, protection, bos]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Protection & Balance-of-System

Breakers, DC protection and PV cable — the BOS that ties modules and inverters to the
point of interconnection. Sizing and ratings are governed by **NOM-001-SEDE-2012**
(Art. 690/705: overcurrent, conductor ampacity, disconnects) — see
[[instalacion-pv-interconectada]] and [[instalacion-bess]].

## AC moulded-case circuit breakers (ABB Tmax)

| Spec | ABB T5N 400 (TMA) | ABB XT3N 250 (TMD) |
|---|---|---|
| Frame / In | T5, 400 A | XT3, 250 A |
| Release | TMA thermomagnetic (I3 = 2000–4000 A) | TMD thermomagnetic (250–2500 A) |
| Poles | 3 | 3 |
| Icu @400 V AC | 36 kA | (N-class) |
| Rated op. voltage | 690 V AC / 750 V DC | up to 690 V AC |
| Dimensions | 140×205×103.5 mm | 105×150×70 mm |
| Standard | IEC | IEC |
| Use | main/feeder AC breaker on inverter output or MT panel | feeder/branch AC breaker |

Raw: `raw/pdfs/2025-06-30 - Interruptor ABB T5N 400 TMA 400.pdf`,
`...Interruptor ABB XT3N TMD 250.pdf`.

## DC protection
- **Suntree SL7 PV DC breaker** — DC polarity / circuit breaker for the PV array DC side. *(Datasheet PDF is image-only — model SL7-PV; confirm V/A rating against `raw/pdfs/2025-06-30 - DC polarity circuit breaker SUNTREE SL7 PV.pdf`.)*

## PV cable (Kibor H1Z2Z2-K)

| Spec | Value |
|---|---|
| Type | H1Z2Z2-K, IEC 62930 / EN 50618, tinned copper, halogen-free |
| Size | 10 mm² (also stocked: black & red) |
| Voltage rating | AC 1000/1000 V; **DC max 1500 V** |
| Current capacity @30 °C | 98 A |
| Temp range | −40…+90 °C |
| Conductor resistance @20 °C | ≤1.95 Ω/km |
| Insulation | XLPE double (white + black) |
| Standards | IEC 60332-1-2 (flame), IEC 61034 (low smoke), UV/ozone resistant |

Raw: `raw/pdfs/2025-06-30 - KIBOR CABLE FV 10 NEGRO.pdf` / `... ROJO.pdf`
(+ `2025-06-30 - APS BusCable-10AWG.pdf` for the microinverter AC bus cable — image-only).

## Selection notes
- **1500 V DC** cable rating matches the modules' 1500 V system voltage ([[pv-modules]]) and the inverters' 1100 V max input ([[string-inverters]]) — adequate with margin.
- ABB **T5N 400** is the AC breaker class for ~100–150 kW inverter outputs (the 100KTL draws ~120–134 A @480 V, 150K up to ~253 A — a 400 A frame covers a paralleled pair); **XT3N 250** for ~30–40 kW feeders.
- DC string fusing follows the modules' **35 A max series fuse** rating; DC disconnect + Type II SPD per NOM-001-SEDE Art. 690.
- Conductor ampacity/derating and the 120% bus rule are detailed in [[instalacion-pv-interconectada]].

## Related
- [[instalacion-pv-interconectada]] — NOM-001-SEDE Art. 690/705 sizing rules
- [[instalacion-bess]] — DC/AC protection on the battery side
- [[string-inverters]] / [[hybrid-inverters]] — what these breakers protect
- [[2026-06-08-cfe-transformer-norms]] — MT side beyond the AC breaker

## Open questions
- Suntree SL7 and APsystems BusCable exact ratings (datasheets image-only).
