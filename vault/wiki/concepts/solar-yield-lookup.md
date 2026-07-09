---
title: "Solar Yield Lookup — CP to Municipality to kWh/kWp"
type: concept
tags: [solar, lookup, codigo-postal, municipio, rendimiento-pv, flujo-de-trabajo, cfe-bill]
created: 2026-06-07
updated: 2026-06-07
sources: [2026-06-07-codigo-postal, 2026-06-07-solar-index-geografico]
---

# Solar Yield Lookup — CP to Municipality to kWh/kWp

The workflow that converts a street address (from a CFE bill) into a local PV yield figure. This is the geographic data layer that feeds the [[pv-savings-model]]: before calculating how much a solar system saves, you need to know how much it produces.

---

## The lookup chain

```
CFE bill address
    → extract Código Postal (5-digit CP)
    → codigo_postal.csv: CP → (d_estado, D_mnpio)
    → Solar_index_geografico.csv: (estado, ciudad) → kWh/kWp values
    → use in PV output calculation
```

---

## Step-by-step

### Step 1 — Extract CP from bill address

CFE bills include a service address. Parse the 5-digit CP from that address.
- CP is zero-padded (e.g., `01000`, not `1000`)
- If the bill shows only the municipality name without a CP, skip to Step 3 using the municipality directly

### Step 2 — Resolve CP to municipality

Query `raw/assets/codigo_postal.csv`:

```
filter: d_codigo == CP
take first matching row
read: D_mnpio, d_estado
```

**Why first row is sufficient:** All rows sharing the same `d_codigo` belong to the same municipality and state. `D_mnpio` and `d_estado` are identical across all asentamientos in a CP.

> **Do NOT use `d_ciudad`** — it is blank for 65.3% of rows (102,915 / 157,521). `D_mnpio` is always populated and is the correct join key to the solar data.

### Step 3 — Look up solar yield

Query `raw/assets/Solar_index_geografico.csv`:

```
filter: estado == d_estado AND ciudad == D_mnpio
read: kWh/kWp_anual, kWh/kWp_Jan … kWh/kWp_Dec
```

**Match is case- and accent-sensitive** — normalize both strings (strip whitespace, consistent accent marks) before matching.

### Step 4 — Compute PV output

```
PV_output_annual (kWh) = system_kWp × kWh/kWp_anual
PV_output_month  (kWh) = system_kWp × kWh/kWp_[Month]
```

Feed monthly output into [[pv-savings-model]] Step 1 (classify solar generation by period).

---

## Data files

| File | Rows | Key columns | Role |
|---|---|---|---|
| `raw/assets/codigo_postal.csv` | 157,521 | `d_codigo`, `D_mnpio`, `d_estado` | CP → municipality bridge |
| `raw/assets/Solar_index_geografico.csv` | 2,369 | `estado`, `ciudad`, `kWh/kWp_*` | Municipality → yield data |

---

## Edge cases

| Situation | Handling |
|---|---|
| CP not found in catalog | Rare (invalid CP on bill). Fall back to reading municipality from bill directly. |
| Municipality not found in solar index | Very rare. Use the state capital or nearest listed municipality as proxy. Flag in analysis. |
| Same municipality name in two states | Always match on both `estado` AND `ciudad`. The estado from the CP lookup is authoritative. |
| CDMX alcaldías (Álvaro Obregón, Benito Juárez, etc.) | These are the D_mnpio in CDMX CPs. Confirm they appear as `ciudad` in the solar index under `Ciudad de México`. |

---

## Yield interpretation

- **Units:** kWh produced per kWp of installed capacity
- **Annual range in Mexico:** ~1,355 (cloudy/north) to ~1,912 (desert south) kWh/kWp
- **Typical SIN commercial site:** ~1,600–1,800 kWh/kWp annually
- **Performance ratio note:** Unclear if values are raw irradiance-derived or PR-adjusted. If raw, apply PR ≈ 0.75–0.80 before using in output calculations. See [[2026-06-07-solar-index-geografico]] open questions.
- Monthly values matter for medición neta modeling — solar production is uneven across the year, and period credit values vary by season

---

## Related pages

- [[pv-savings-model]] — consumes the kWh/kWp output from this lookup
- [[2026-06-07-codigo-postal]] — the CP catalog source
- [[2026-06-07-solar-index-geografico]] — the yield data source
- [[horarios-y-divisiones]] — needed to allocate monthly solar output to punta/intermedio/base periods
