---
title: "Catálogo de Códigos Postales de México (SEPOMEX)"
type: source
tags: [datos, codigo-postal, municipio, estado, lookup, geografia]
created: 2026-06-07
updated: 2026-06-07
sources: []
---

# Catálogo de Códigos Postales de México (SEPOMEX)

**Type:** data
**Date:** —
**Author:** SEPOMEX (Servicio Postal Mexicano)
**Raw file:** `raw/assets/codigo_postal.csv`

---

## Summary

Full national catalog of Mexican postal codes (códigos postales). 157,521 rows — one row per asentamiento (neighborhood, colony, pueblo, barrio). Each row maps a CP to its administrative hierarchy: estado, municipio, and optionally a named city.

The dataset is used as the geographic bridge in the CFE bill analysis workflow: a CP extracted from a bill address is looked up here to resolve the municipality, which is then matched against [[solar-yield-lookup]] data.

---

## Schema

| Column | Description | Notes |
|---|---|---|
| `d_codigo` | Código postal (5-digit) | The CP on the CFE bill address |
| `d_asenta` | Asentamiento name (colony, barrio, pueblo) | Not needed for yield lookup |
| `d_tipo_asenta` | Settlement type (Colonia, Pueblo, Barrio…) | — |
| `D_mnpio` | **Municipality name** | Primary join key to solar yield data |
| `d_estado` | **State name** | Secondary join key (disambiguates same-name municipalities) |
| `d_ciudad` | Named city (if applicable) | **Blank for 65% of rows** — not reliable as join key |
| `d_CP` | Head post office CP for the area | — |
| `c_estado` | Numeric state code | — |
| `c_mnpio` | Numeric municipality code | — |

---

## Key facts

- **157,521 rows** — every asentamiento in Mexico
- **33 states** covered (includes Ciudad de México as separate entry)
- **65.3% of rows have blank `d_ciudad`** — `D_mnpio` is the reliable lookup column
- Multiple rows share the same `d_codigo` (one CP can have many asentamientos within it); all rows for a given CP share the same `D_mnpio` and `d_estado`
- `d_codigo` is zero-padded to 5 characters (e.g., `01000` for CDMX)

---

## Join key for solar yield lookup

> Use `(d_estado, D_mnpio)` — NOT `d_ciudad` — to match against `(estado, ciudad)` in [[2026-06-07-solar-index-geografico]].

**Why:** Solar yield data is at the municipality level. `d_ciudad` is a city name present only for major urban centers; `D_mnpio` is always populated and matches the `ciudad` column in the solar dataset.

---

## Contradictions / tensions

None identified. Standard SEPOMEX catalog format.

---

## Questions raised

- When looking up a CP from a CFE bill, multiple rows may have the same CP (different asentamientos, same municipality). This is fine — all rows for a given CP share the same `D_mnpio` and `d_estado`, so taking the first match is sufficient.
- Edge case: municipalities that cross state boundaries (very rare) — `d_estado` disambiguates.
