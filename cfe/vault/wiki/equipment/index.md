---
title: "Equipment Catalog"
type: overview
tags: [equipment, bom]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Equipment Catalog

Vendor datasheets for the PV + BESS components we spec into CFE GDMTH/GDMTO projects.
Organized by **category roll-up** — one page per class, each comparing the models we hold
datasheets for. These pages are the **BOM component library**: a savings analysis
(e.g. [[2026-06-08-780881200029-yearly-savings]]) picks hardware from here, and the
installation/standards pages ([[instalacion-pv-interconectada]], [[instalacion-bess]],
[[2026-06-08-nom-009-stps-2011]]) govern how it goes in.

## Categories
- [[pv-modules]] — PV panels: Trina Vertex 710/720, Seraphim HJT 720, Tongwei 720 (all 210mm bifacial dual-glass, ~720 Wp)
- [[string-inverters]] — Huawei SUN2000 family, 20 kW → 150 kW (grid-tie, transformerless)
- [[microinverters]] — APsystems YC600 / DS3D, Hoymiles HMS-2000 (module-level, residential/small C&I)
- [[hybrid-inverters]] — Sigen Hybrid 50–125 kW (PV + battery, DC-coupled C&I)
- [[bess]] — battery storage: BYD MC Cube-T, Huawei LUNA2000-215, Sigen SigenStack
- [[monitoring]] — dataloggers / gateways: Huawei SmartLogger3000A, Hoymiles DTU-Lite-S, APsystems ECU-R
- [[protection-bos]] — breakers, DC protection, PV cable: ABB T5N/XT3N, Suntree SL7, Kibor FV cable

## How sizing maps to hardware
- **Large C&I rooftop / ground (Posadas scale, ~200 kW PV+):** [[pv-modules]] in strings → [[string-inverters]] (100–150 kW units) → [[bess]] container (LUNA2000 / MC Cube) for peak-shaving.
- **Small C&I / residential:** [[microinverters]] or [[hybrid-inverters]] + modular [[bess]] (SigenStack).
- Every DC/AC string lands on [[protection-bos]] (breaker + SPD + PV cable) sized per NOM-001-SEDE-2012 ([[instalacion-pv-interconectada]]).

## Open data gaps
- Tongwei module datasheet and the Suntree SL7 DC breaker / APsystems bus cable PDFs are **image-only** (no extractable specs) — values below are from the brochure/model number; confirm against the raw PDF before quoting.
