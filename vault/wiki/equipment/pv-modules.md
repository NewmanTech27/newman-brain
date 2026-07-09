---
title: "PV Modules"
type: concept
tags: [equipment, pv]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# PV Modules

The PV panels we hold datasheets for. All four are **210 mm-format, N-type bifacial
dual-glass** modules in the **705–720 Wp** class — the current C&I/utility mainstream.
Bifaciality (80–90%) means rear-side gain on reflective roofs adds 5–30% depending on
albedo. These feed the [[pv-savings-model]]; nameplate Wp × count × yield (per
[[solar-yield-lookup]]) sets generation, derated over time per [[pv-degradation]].

## Comparison (front-side STC)

| Spec | Trina Vertex TSM-NEG21C.20 (720) | Trina Vertex TSM-NEG21C.20 (710) | Seraphim SRP-720-BHC-BG | Tongwei 720 |
|---|---|---|---|---|
| Cell tech | N-type i-TOPCon | N-type i-TOPCon | HJT | N-type (bifacial) |
| Pmax (Wp) | 720 | 710 | 720 | 720 |
| Efficiency | 23.2% | 22.9% | 23.18% | ~23% |
| Vmp / Imp | 41.3 V / 17.44 A | 40.9 V / 17.36 A | 42.78 V / 16.88 A | — |
| Voc / Isc | 49.4 V / 18.49 A | 49.0 V / 18.40 A | 50.80 V / 17.68 A | — |
| Cells | 132 (i-TOPCon) | 132 | 132 (HJT 210×105) | 132 |
| Dimensions | 2384×1303×33 mm | 2384×1303×33 mm | 2384×1303×33 mm | ~2384×1303 mm |
| Weight | 38.3 kg | 38.3 kg | 38.5 kg | ~38 kg |
| Temp coeff Pmax | −0.29 %/°C | −0.29 %/°C | −0.258 %/°C | low (HJT-class) |
| Bifaciality | 80±5% | 80±5% | 90±5% | high |
| Max system V | 1500 V DC | 1500 V DC | 1500 V DC | 1500 V DC |
| Max series fuse | 35 A | 35 A | 35 A | 35 A |
| Product warranty | 12 yr | 12 yr | 15 yr | — |
| Power warranty | 30 yr (1% yr1, 0.40%/yr) | 30 yr (1% yr1, 0.40%/yr) | 30 yr (linear) | — |

Raw datasheets: `raw/pdfs/2025-07-02 - Panel solar trina 720.pdf`,
`raw/pdfs/2025-07-02 - Panel solar trina 710.pdf`,
`raw/pdfs/2025-06-30 - Panel solar Modulo fotovoltaico SERAPHIM 720w.pdf`,
`raw/pdfs/2025-06-30 - 720w TONGWEI.pdf` (image-only; `raw/pdfs/2025-07-04 - TW Solar.pdf` is the white paper).

## Selection notes
- **Seraphim HJT** has the best temperature coefficient (−0.258 %/°C) and highest bifaciality (90%) — favors hot Yucatán/Cancún rooftops (lower thermal derate) and reflective membrane roofs.
- **Trina i-TOPCon** is the volume default; near-identical electricals at slightly higher temp coefficient.
- All share **1500 V DC** system voltage and **35 A** max series fuse — string sizing and DC protection (see [[protection-bos]]) are interchangeable across them.
- 33 mm frame, ~38 kg, 1500 V → standard C&I racking; mechanical install governed by [[2026-06-08-nom-009-stps-2011]] (trabajos en altura) and [[instalacion-pv-interconectada]].

## Related
- [[string-inverters]] / [[hybrid-inverters]] — DC side these modules wire into
- [[pv-degradation]] — why the 0.4%/yr warranty derate matters for 20-yr savings
- [[pv-savings-model]] — how nameplate → generation → bill reduction
- [[solar-resource-data]] — irradiance/yield inputs behind the energy estimate

## Open questions
- Tongwei exact model + full electricals (datasheet is image-only).
