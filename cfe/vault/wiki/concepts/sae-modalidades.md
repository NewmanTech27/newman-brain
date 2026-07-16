---
title: "SAE Modalidades — Tipos de Integración de Almacenamiento"
type: concept
tags: [sae, almacenamiento, modalidades, cre, a113-2024]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-dacg-sae-a113-2024]
---

# SAE Modalidades — Tipos de Integración de Almacenamiento

The four modalities under which energy storage systems (SAE) can be integrated into Mexico's electricity system, as defined by **Acuerdo A/113/2024**.

## Quick reference

| Modality | Associated with | Grid injection | Permit | Key use case |
|---|---|---|---|---|
| **SAE-CE** | Intermittent generation plant (solar, wind) | Yes (through CE) | Yes (or modify) | Stabilize variable renewables |
| **SAE-CC** | Load center only | No | No (SSB) | Commercial/industrial demand reduction |
| **SAE-AA** | Isolated supply scheme | Isolated only | Yes | Off-grid or autoabastecimiento |
| **SAE-GE** | Exempt generator (DG < 0.7 MW, 2025) | Via DG rules | Via RES/142/2017 | Solar + storage at DG scale |
| **SAE no Asociado** | Standalone (no CE or CC) | Yes | Yes | Utility-scale grid storage |

## SAE-CE — Battery at Intermittent Generation Plant

- Battery and solar/wind plant share one interconnection point
- Battery charges primarily from the plant; grid charging requires separate studies
- CENACE can require battery charging/discharging for grid stability
- Must meet 3-hour continuous discharge requirement for "firm" capacity accreditation
- New plants with SAE: need single permit; existing plants adding SAE: need permit modification
- Cannot earn additional CEL for stored energy

## SAE-CC — Battery at Load Center *(most relevant for GDMTH users)*

See [[sae-cc]] for full details.

- No injection; charges from grid; discharges to serve own load
- No permit required under SSB
- Battery power counts as contracted demand
- Reduces peak demand charges under [[gdmth]]

## SAE-AA — Battery at Isolated Supply

- Combined with a Central Eléctrica in autoabastecimiento (self-supply) or import/export
- Energy stays within the isolated system (no public grid injection for own consumption)
- Requires generation permit; must follow isolated supply regulations
- Exempt from MEM participant registration when serving own load only

## SAE-GE — Battery at Exempt Generator (DG < 0.7 MW)

- Governed by RES/142/2017 ([[generacion-distribuida]]) plus A/113/2024
- Combined solar + battery at small scale
- Storage capacity cannot increase the plant's registered capacity for CEL purposes
- Output to grid cannot exceed the contractual capacity in the interconnection contract

## SAE no Asociado — Standalone Grid Battery

- Connected independently to RNT or RGD
- Participates in MEM as a "Central Eléctrica firme" (firm generation unit)
- Must register as a market participant (Generador)
- Can offer ancillary services (frequency regulation, spinning reserves, etc.)
- Must demonstrate 3-hour continuous discharge for firm capacity accreditation
- No CEL obligations or rights (energy was generated elsewhere)
- Cannot hold Financial Transmission Rights (DFT)

## Related concepts

- [[sae-cc]] — the load-center modality in depth
- [[generacion-distribuida]] — framework governing SAE-GE
- [[gdmth]] — the tariff most directly impacted by SAE-CC

## How sources treat this

- [[2026-06-04-dacg-sae-a113-2024]]: defines all modalities in Chapters II–VI
