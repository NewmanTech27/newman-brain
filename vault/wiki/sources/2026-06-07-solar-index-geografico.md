---
title: "Índice Solar Geográfico por Municipio — México"
type: source
tags: [datos, solar, irradiacion, rendimiento-pv, municipio, kWh-kWp]
created: 2026-06-07
updated: 2026-06-07
sources: []
---

# Índice Solar Geográfico por Municipio — México

**Type:** data
**Date:** —
**Author:** —
**Raw file:** `raw/assets/Solar_index_geografico.csv`

---

## Summary

PV yield data for every municipality in Mexico. 2,369 rows — one per municipality — providing annual and monthly average yield in kWh per kWp of installed capacity. This is the terminal dataset in the bill-to-yield lookup chain: once a CFE bill's CP is resolved to a municipality via [[2026-06-07-codigo-postal]], this file provides the local solar resource for PV output estimation.

---

## Schema

| Column | Description | Unit |
|---|---|---|
| `estado` | State name | — |
| `ciudad` | Municipality name (join key from CP lookup) | — |
| `kWh/kWp_anual` | Annual PV yield | kWh per kWp installed |
| `kWh/kWp_Jan` … `kWh/kWp_Dec` | Monthly yield, Jan through Dec | kWh per kWp |

---

## Key facts

- **2,369 rows** — national municipality-level coverage
- **32 states**, 2,238 unique municipality names
- **Annual yield range: 1,355 – 1,912 kWh/kWp**
  - Low end (~1,355): cloudiest / most northern locations
  - High end (~1,912): desert / high-irradiance locations (likely Sonora/Chihuahua)
- Monthly columns enable seasonal PV output modeling (important for period-by-period medición neta credit calculations)

---

## Entities mentioned

- [[cfe]] — the utility whose bills trigger the yield lookup

## Concepts mentioned

- [[solar-yield-lookup]] — the workflow that uses this dataset
- [[pv-savings-model]] — consumes yield values to compute annual/monthly PV output

---

## Contradictions / tensions

None identified. Values appear consistent with published PVGIS/NASA SSE irradiance data for Mexico.

---

## Questions raised

- What is the source/methodology for these yield values? (PVGIS, NASA SSE, SOLARGIS, or proprietary?)
- Do values represent performance ratio-adjusted yield (real system output) or raw irradiance-derived values? A typical PR of 0.75–0.80 should be applied if these are raw values.
- Are values for fixed-tilt or optimal-tilt systems? Tracking systems?
