# cfe_savings — GDMTH PV+BESS yearly savings engine

Deterministic Python engine that turns a folder of CFE GDMTH bill PDFs into a
yearly PV+BESS savings table (matching the client Excel's `RESUMEN MENSUAL`) plus
a financial view. **Raw bill bytes never enter an LLM context** — the engine
parses locally and emits only the compact summary. All tariff logic mirrors the
CFE Brain wiki (the single source of truth); see citations in `engine.py`.

## Run

The project's default `python` is a pip-less venv. Use the interpreter that has
`pdfplumber`/`openpyxl`:

```
PY="C:/Users/vidan/AppData/Local/Programs/Python/Python314/python.exe"
cd "C:/Users/vidan/Desktop/CFE Brain/tools"
"$PY" -m cfe_savings "../raw/bills/<RPU>" [--inputs <inputs.json>] [--net] [--saas-share 0.48] [--json out.json]
```

Install deps once: `"$PY" -m pip install -r cfe_savings/requirements.txt`

## Inputs

`raw/bills/<RPU>/inputs.json` (see the `780881200029` example). Anything omitted
falls back to `defaults.py`. Key fields: `division`, `system.pv_kwp`,
`system.pv_monthly_kwh` (Helioscope; else `pv_yield_kwh_per_kwp` → flat shape),
`system.bess_nominal_kwh`, `system.bess_power_kw`, `system.availability_factor`,
and a `finance` block (CAPEX, WACC, escalations, O&M).

## What it computes

- **Baseline (Bill ANTES, sin IVA, no FP bonus)** = Σ MEM importes per bill — matches the Excel.
- **Validation** — `(Σ importes + bonif_FP) × 1.16` vs printed `Facturacion del Periodo`; flags any bill that doesn't foot (catches CFE errors).
- **Savings** — per month, three scenarios (PV-only / BESS-only / combined):
  - capacidad shave = `nominal·DoD·√RTE / punta_hours(division, season)` (SIN: 2h summer / 4h winter)
  - arbitrage = `disch·bundled_punta − charge·bundled_base`
  - PV = `gen · bundled_inter` (SIN: PV lands in intermedio, ~0 in punta)
  - umbral cap (FC=0.57); distribución on `max(B,I,P)`, **not** KWMax
- **Finance** — unlevered project NPV/IRR/payback + an optional `--saas-share`
  financier view.

## Scope boundary (read this)

The engine reproduces **savings to the peso**. The reference Excel's financier
return ("Flujo Newman", ~19% TIR) embeds a **bespoke debt + PPA + savings-share**
structure (its `ActiveLeasing` tabs). That is **parameterized** here via
`--saas-share` (at 0.482 the financier IRR ≈ 19.5%, payback ≈ 6 yr, matching the
Excel), **not** hardcoded. Supply real financing terms per deal for an exact
financier return. The unlevered project view (TIR ~37%, payback ~3 yr) is the
"is it worth building" number.

## Regression (golden test)

`python -m cfe_savings raw/bills/780881200029` must reproduce: baseline
$30,157,371; TOTAL Ahorro $7,593,969 (25.2%); Generación 350,116 kWh; BESS desc
1,009,362 kWh; and all 12 monthly Ahorro values within $1 of the Excel
`RESUMEN MENSUAL`.

## Modules

`extract.py` (PDF→data) · `engine.py` (tariff+savings math) · `sizing.py`
(auto-propose PV/BESS) · `finance.py` (NPV/IRR/payback) · `report.py` (tables) ·
`defaults.py` (constants + region schedules) · `__main__.py` (CLI).
