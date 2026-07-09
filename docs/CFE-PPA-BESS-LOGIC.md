# CFE PPA + BESS Engine — Step‑by‑Step Logic

> Source: Supabase Edge Function `cfe-ppa-bess` (project `bwudgrwfwjdbvqhgbwty`, version 6).
> Deterministic port of the CFE Brain Python engine (`tools/calc_core.py` + `load_curves.py` +
> `cfe_savings/defaults.py`). Verified bit‑for‑bit against the Python golden reference
> (4,536 fields, 0 diff). No external calls, no secrets — numbers only.

This document walks the logic end‑to‑end so a reader can follow *exactly* how a stack of monthly
CFE bills (tarifa **GDMTH**) is turned into PV / BESS / Hybrid savings, a regulatory régime, and a
project financial model.

> **This is a general‑purpose engine, not a GEPP‑specific one.** The logic below applies to **any**
> CFE **GDMTH** client — industrial, commercial, hotel, office — regardless of division or giro.
> The **GEPP 4‑sites dataset is only a worked proof of concept** used to validate the port; it is
> not the subject. To model a new project you supply that project's own bills and inputs and run the
> exact same `compute` / `size-bess` path (see **§11 — Applying the engine to a new project**). Every
> new project that arrives follows this same recipe.

---

## 0. Files & responsibilities

| File | Role |
|------|------|
| `index.ts` | HTTP handler (Deno). Routes the 3 modes, CORS, GEPP orchestration, JSON shaping. |
| `engine.js` | The deterministic engine — regulatory constants, load curves, `compute()`, `_regimen()`, `_finance()`, `size_bess_verano()`. Plain ESM so it runs unchanged under Node (tests) and Deno (edge). |
| `gepp_data.js` | Auto‑generated seed: the GEPP 4‑sites rev3 dataset (inputs + 12 monthly bills + rev3 verano‑2h BESS sizes per service). |

### The three modes (`index.ts`)

`POST` a JSON body with a `mode` field:

| Mode | Body | Returns |
|------|------|---------|
| `compute` | `{ inputs, bills[] }` | `{ inputs, monthly[], validacion[], annual, regimen, finance:{PV,BESS,Hibrido} }` |
| `size-bess` | `{ bills[], hours?, dod?, rte? }` | `{ bess_kw, bess_kwh, avg_summer_punta_kw, basis }` |
| `gepp` | `{ pv_kwp?, fp_correction? }` | Seeded GEPP rev3 run: per‑service + Proplasa rollup + portfolio totals |

`GET /` returns machine‑readable usage. `OPTIONS` handles CORS preflight.

---

## 1. The golden doctrine (the rules everything encodes)

Two regulatory constants drive every branch of the model:

- **`DG_CEILING_KW = 700`** — the distributed‑generation ceiling.
  - **PV `< 700 kWp`** → *Generador Exento / Medición Neta* (net metering). No permit. PV is
    credited against monthly consumption up to the **intermedio** kWh band.
  - **PV `≥ 700 kWp`** → *Autoconsumo*. Only the self‑consumed fraction (`pct_autoconsumo`) is
    credited; excedentes (surplus) are valued at `texc` (default **$0** — i.e. effectively lost).
- **BESS = SAE‑CC** (Sistema de Almacenamiento en Corriente Continua): discharges **only during
  the punta window on weekdays**, and the discharge is capped at the bill's actual punta kWh.

Tariff mechanics baked in:
- **Capacidad** charge is billed on `kW_punta`.
- **Distribución** charge is billed on `max(kW_base, kW_inter, kW_punta)`.
- The demand **umbral** (threshold) = `kWh / (days × 24 × FC)`, with load factor **`FC = 0.57`**.
- **`IVA = 0.16`** (VAT).

---

## 2. Regulatory calendar & tariff windows (`engine.js`)

Before any money is computed, the engine reconstructs the CFE time‑of‑use schedule for each
bill's `(year, month)`.

### 2.1 Punta hours per day — `punta_hours(division, month)`
Depends on **division** and **season**:
- **SIN** (national grid, the calibrated default): 2 h/day in summer (Apr–Oct), 4 h/day in winter.
- **BCS**: 10 h/day summer, 0 in winter.
- **BC**: 4 h/day (May–Oct), 0 otherwise.

### 2.2 Statutory holidays — `festivos(year)`
Mexican holidays that the tariff treats as *domingo*: Jan 1, 1st Mon of Feb, 3rd Mon of Mar,
May 1, Sep 16, 3rd Mon of Nov, Dec 25. `_nthMonday()` computes the movable ones.
> Weekday alignment is handled carefully: Python's `date.weekday()` (Mon=0) is reproduced from
> JS's `getUTCDay()` (Sun=0) via `pyWeekday()` so the port matches the reference day‑for‑day.

### 2.3 Day classification — `day_counts(year, month)`
Every calendar day is bucketed into **MF** (Mon–Fri), **SA** (Saturday), or **DO** (Sunday/holiday).
`punta_weekdays()` counts the Mon–Fri days minus holidays — these are the days a BESS can actually
discharge into punta.

### 2.4 Season & B/I/P windows — `WINDOWS`, `season()`
For each `division|season` and day‑type, a 24‑hour label vector marks each hour as
**B**ase / **I**ntermedio / **P**unta (`_lab()`). Example (SIN summer, Mon–Fri): base 00:00–06:00,
punta 20:00–22:00, everything else intermedio.

---

## 3. Industry load curves & giro fitting

### 3.1 Curves — `CURVES`
Six normalized 24‑h load shapes (per day‑type MF/SA/DO), each peaking at 1.0:
`Hotel/Turismo`, `Industrial 24/7`, `Industrial 1 turno`, `Comercial/Retail`, `Oficinas`, `Otro`.

### 3.2 Model split — `model_split(giro, division, year, month)`
Overlays the load curve on the B/I/P window labels, weighted by how many MF/SA/DO days the month
has, and returns the **fraction of energy** landing in each band `{B, I, P}` (normalized to 1).

### 3.3 Giro auto‑detection — `fit_bills(bills, division)`
For each candidate giro, compares the model's predicted `{B,I,P}` split against the **actual** split
from each bill's `kwh_base/inter/punta`, scores mean‑absolute‑error, and ranks. The best‑fitting
giro is surfaced (and used in alerts when the chosen curve fits poorly, MAE > 8%).

### 3.4 Autoconsumo % — `autoconsumo_pct(giro, year, month, kwh_month, gen_month)`
For PV ≥ 700 kWp, derives what fraction of solar generation is actually self‑consumed:
- Builds a **solar bell** `PV_BELL` = `max(0, sin(π·(h−7)/12))` over 24 h.
- Scales the load curve to the month's kWh and the bell to the month's generation.
- Hour‑by‑hour, self‑consumption = `min(load, solar)`; the credited fraction is
  `Σ min(load, solar) / gen_month`, capped at 1.0.

This is the "curva × campana solar" overlap. A manual `pct_autoconsumo` override bypasses it.

---

## 4. Inputs & derived economics — `merge_inputs(over)`

Merges caller inputs over `DEFAULT_INPUTS` (null/undefined ignored) and precomputes:

- `pct_mode` = `"manual"` if `pct_autoconsumo` given, else `"curva"`.
- `curva` defaults to the giro (or `"Otro"`); `pct_autoconsumo` defaults from `GIRO_PCT_AC`.
- `yield_monthly` keys coerced to integer months.
- O&M defaults: `om_pv = kwp × 310`, `om_bess = bess_kwh × 180` (MXN/yr) if not supplied.
- **CAPEX**: `capex_pv = kwp × 1000 × epc_usd_wp × fx`; `capex_bess = bess_kwh × epc_bess × fx`.
- **Deliverable BESS energy**: `deliv = bess_kwh × dod × √rte` (round‑trip‑adjusted usable energy).
- **Availability factor**: `falla = (12 − falla_meses) / 12` (months the BESS is expected offline).

Defaults worth noting: `fc = 0.57`, `epc_usd_wp = 0.75`, `fx = 17.55`, `ppa = 1.5`, `esc_cfe/esc_ppa = 0.05`,
`dod = rte = 0.96`, `epc_bess = 280`, `comision = 0.5`, `wacc = 0.12`, `horizon = 20`, `fianza = 0.139`.

---

## 5. Bill validation — `validate_bill(b)`

Independent sanity check that a transcribed CFE bill reconstructs its own total. Sums the MEM
line items (`suministro, distribucion, transmision, cenace, gen_base, gen_inter, gen_punta,
capacidad, scnmem`), adds `bonif_fp`, applies **×1.16 IVA**, and compares to `facturacion_recibo`.
It's **OK** only if `|calc/recibo − 1| < 0.5%`. Failures raise a blocking alert (§8) — you don't
trust savings computed on bills that don't foot.

---

## 6. The monthly compute loop — `compute(inputs, bills)`

`autoc = kwp ≥ 700`. For **each bill** the engine derives, in order:

1. **Validate** the bill (§5) → `validacion[]`.
2. **Energy & demand**: `kwh_tot = base+inter+punta`; `kw_punta`; days (default 30).
3. **Demand threshold** `umbral = kwh_tot / (days·24·fc)`; **capacity basis**
   `basis_cap = min(kw_punta, umbral)` (or `umbral` if no punta demand). Capacity unit rate
   `r_cap = capacidad / basis_cap`.
4. **Energy band prices** ($/kWh), each with the flat per‑kWh adder
   `flat = (transmision + cenace + scnmem) / kwh_tot`:
   - `bnd_i = gen_inter/kwh_inter + flat` (intermedio),
   - `bnd_b = gen_base/kwh_base + flat` (base; falls back to `bnd_i`),
   - `bnd_p = gen_punta/kwh_punta + flat` (punta).
5. **PV generation** `gen = kwp × yield_monthly[m]`.
6. **Self‑consumption fraction** `pct_m`:
   - net‑metering (`!autoc`) → `1.0`;
   - autoconsumo manual → `pct_autoconsumo`;
   - autoconsumo curva → `autoconsumo_pct(...)` (§3.4).
7. **PV energy credit**:
   - `usable = gen × pct_m`; `aprov = min(usable, kwh_inter)` (credited only up to the intermedio band);
   - `exced = gen − aprov` (surplus, valued at `texc`);
   - `ah_pv = aprov × bnd_i + exced × texc`.
8. **PV demand reduction** (`dem_pv`): recomputes the post‑PV threshold
   `umb_post = (kwh_tot − aprov)/(days·24·fc)` and credits the capacity delta
   `(basis_cap − min(kw_punta, umb_post)) × r_cap`.
9. **BESS peak shaving** (hybrid):
   - `shave = min(bess_kw, deliv/ph)` kW shaved off punta demand (`ph` = punta hours/day);
   - residual punta demand `resid = max(0, kw_punta − shave)`;
   - `dem_bess_h = (min(kw_punta,umb_post) − min(resid, umb_post)) × r_cap`.
10. **BESS energy arbitrage** (`arb`): discharge `desc = min(deliv × punta_weekdays, kwh_punta)`;
    charge energy `carga = desc / rte`. Value = `desc × bnd_p − carga × bnd_b` (sell at punta,
    buy back at base).
11. **Three savings scenarios** for the month:
    - `pv_only = ah_pv + dem_pv + clawback`
    - `bess_only = dem_bess_o + arb + clawback` (uses the pre‑PV threshold)
    - `hibrido = ah_pv + dem_pv + dem_bess_h + arb + clawback`
12. **FP‑bonus clawback**: if `bonif_fp < 0` (a power‑factor *bonus* on the bill), reducing the
    bill proportionally erodes that bonus. `share = −bonif/mem`; `claw(s) = −s × share` recovers
    the lost bonus so savings aren't overstated.
13. `antes = mem + bonif` (the true baseline bill excl. IVA).

---

## 7. Annual aggregation & availability derating

- If fewer than 12 months are supplied, results are **annualized** by `factor = 12/n_meses`
  (`anualizado = true`, surfaced in output).
- `annual` sums every monthly line (`antes, gen, exced, pv_only, bess_only, hibrido, ah_pv,
  dem_pv, dem_bess_h, arb, fp_cargo`) × the annualization factor.
- `pct_ac_avg` = generation‑weighted average self‑consumption fraction.
- **`fp_lever`** = the FP penalty recoverable via power‑factor correction (only if `fp_correction`).
- **Availability‑derated savings** `neto_disp` applies `falla` (§4) to the BESS portion only:
  - `pv = pv_only` (PV unaffected),
  - `bess = bess_only × falla`,
  - `hibrido = hibrido − (dem_bess_h + arb)·(1 − falla)`.

---

## 8. Régime classification & alerts — `_regimen()`

Picks the regulatory régime string from `kwp`:
- `< 700 kWp` → **Generador Exento — Medición Neta** (Art. 30 LSE; RES/142/2017).
- `0.7–20 MW` → **Autoconsumo — permiso SIMPLIFICADO CNE** (Núm. 2.2 DACG).
- `> 20 MW` → **Autoconsumo — permiso ORDINARIO CNE** (Núm. 2.3 DACG).

Then raises typed alerts (`error` / `warn` / `opp` / `info`), including:
- **error** — any bill fails validation (>0.5%); BESS kW > demanda contratada (violates SAE‑CC);
  PV ≥ 0.7 MW intermitente with **no** BESS/backup (required by Núm. 4.5 DACG).
- **warn** — max demand < 110 kW (near the 100 kW GDMTO gate); surplus kWh valued at `texc`
  (net‑metering credits expire to PML in 12 months); non‑SIN division (model calibrated for SIN);
  chosen curve fits bills poorly (MAE > 8%); fewer than 12 months of bills.
- **opp** — FP penalty charges present (power‑factor correction is usually the highest ROI and is
  orthogonal to PV/BESS).
- **info** — autoconsumo active (% credited + permit/registration reminders); BESS satisfies the
  mandatory intermittency backup.

---

## 9. Finance model — `_finance(p, annual, esc)`

Runs independently for `esc ∈ {PV, BESS, Hibrido}`. Builds a `horizon`‑year (default 20) cash flow
from **two perspectives**:

- **Proyecto** (`fl_proj`): the raw savings stream net of O&M — the asset's own economics.
- **Financiador** (`fl_new`): the financier/ESCO view — PPA payments + BESS success commission,
  net of O&M and `fianza` (bond) — i.e. what the money party actually receives.

Each year `yy` escalates and degrades the streams:
- CFE escalation `e = (1+esc_cfe)^yy`; PV degradation `(1−pv_degr)^yy`; BESS degradation `(1−bess_degr)^yy`.
- `sav_pv = base_pv·e·dpv`; `sav_bess = base_bess·e·dbe·falla`; clawback averaged over both degradations.
- `ppa_pay = gen·dpv·ppa·(1+esc_ppa)^(yy−1)` while `yy ≤ ppa_yrs`.
- `com = sav_bess·comision` while `yy ≤ bess_yrs`; O&M streams escalate at `esc_cfe`.

Then computes, for each perspective:
- **TIR** (IRR) via bisection on the discounted‑flow sign change (`irr()`),
- **VPN** (NPV) at `wacc`,
- **Payback** = first year cumulative flow turns non‑negative,
- plus `capex` and `bruto_anio0` (year‑0 gross savings).

---

## 10. BESS verano‑2h sizing rule — `size_bess_verano(bills, opts)`

The rev3 doctrine (`sizing.py propose_bess` / `gepp_bess_scenarios.tam_B`):

1. Take the **summer** bills (default months **May–Sep**; falls back to all bills if none).
2. `avg_punta` = average `kw_punta` across those months.
3. **Usable energy target** `E_util = hours × avg_punta` (default `hours = 2` — "verano 2h").
4. **Nominal capacity** `nominal = round( E_util / (dod·√rte) / 100 ) × 100` kWh (rounded to 100 kWh).
5. **Power** `power = round(nominal / 2)` kW — i.e. a **0.5C** battery (2‑hour duration).

> Doctrine string: *"energía = 2h × demanda punta verano; 0.5C; dispatch punta weekdays;
> medición neta < 0.7 MWp / autoconsumo ≥ 0.7 MWp."*

---

## 11. Applying the engine to a new project (the replicable recipe)

Everything above is client‑agnostic. To model **any** new CFE **GDMTH** project, you never touch the
engine — you only supply that project's data and call the same functions. GEPP (§12) is just this
recipe run once, with its numbers baked into `gepp_data.js`.

**Step 1 — Parse the bills.** Transcribe each monthly CFE receipt into a bill object. The engine
reads these fields (missing numerics default to 0; see `compute()` / `validate_bill()`):

| Field | Meaning |
|-------|---------|
| `year`, `month`, `days` | Billing period (days defaults to 30). |
| `kwh_base`, `kwh_inter`, `kwh_punta` | Energy per tariff band. |
| `kw_base`, `kw_inter`, `kw_punta` | Measured demand per band. |
| `capacidad` | Capacidad charge (MXN) — the engine derives its unit rate from this. |
| `gen_base`, `gen_inter`, `gen_punta` | Energy charges per band (MXN). |
| `transmision`, `cenace`, `scnmem` | Flat per‑kWh MEM adders (MXN). |
| `suministro`, `distribucion` | Fixed + distribution charges (validation only). |
| `bonif_fp`, `cargo_fp_penalty` | Power‑factor bonus (negative) / penalty. |
| `facturacion_recibo` | The receipt's own printed total — used to **validate** the transcription. |

Aim for **12 months** (seasonality); fewer works but the result is annualized and flagged (§7).

**Step 2 — Set the project inputs.** Anything not supplied falls back to `DEFAULT_INPUTS` (§4). The
ones that matter per project:

- `division` — `SIN` (default, calibrated), `BC`, or `BCS`. Non‑SIN is flagged as conservative (§8).
- `giro` — one of the six curves, or let **`fit_bills()`** (§3.3) pick the best fit from the bills.
- `demanda_contratada` — contracted demand (used to sanity‑check BESS size).
- `kwp` + `yield_monthly` — PV size and monthly yield (kWh/kWp). `kwp = 0` ⇒ **BESS‑only**.
- `bess_kw`, `bess_kwh` — battery size (or derive it in Step 3).
- Commercial terms — `ppa`, `epc_usd_wp`, `epc_bess`, `fx`, `comision`, `wacc`, escalations, etc.

**Step 3 — (Optional) size the BESS.** Call `mode: "size-bess"` with the bills to get the rev3
verano‑2h size (§10); feed the returned `bess_kw` / `bess_kwh` back into Step 2.

**Step 4 — Compute.** Call `mode: "compute"` with `{ inputs, bills }`. You get back:

- `validacion[]` — did every bill foot? (fix transcription before trusting anything);
- `monthly[]` — the per‑bill breakdown (§6);
- `annual` + `neto_disp` — annual savings, availability‑derated (§7);
- `regimen` — the regulatory régime + typed **alerts** to act on (§8);
- `finance{PV,BESS,Hibrido}` — TIR / VPN / payback from both perspectives (§9).

That's the whole loop. A new project is *only* new bills + new inputs; the doctrine, curves,
tariff windows, and finance math are shared and fixed.

---

## 12. Worked example (proof of concept) — GEPP — `runGepp()` + `gepp_data.js`

`mode: "gepp"` is **§11 pre‑applied to one real portfolio**: it runs the seeded
**"GEPP — Propuesta PV+BESS 4 Sitios rev3 — BESS verano 2h"** design. It exists to prove the engine
against real bills end‑to‑end — treat it as a reference example, not a special code path (it calls
the same `compute()` every new project uses).

For each of the **6 services** (4 physical sites), it builds standardized inputs (EPC $0.65/Wp PV,
$280/kWh BESS, PPA $1.20, comisión 0.5, fx 17.55, 15‑yr terms, verano‑2h BESS size from `meta`),
spreads the annual yield flat across 12 months, and calls `compute()`. The financed scenario is
**Hibrido** when PV kWp is layered on, else **BESS**‑only (the default — PV off unless `pv_kwp` given).

Seeded services:

| Slug | Site | BESS kW / kWh | Yield (kWh/kWp·yr) | Proplasa |
|------|------|---------------|--------------------|----------|
| `gepp-ixtlahuacan` | Ixtlahuacán (Jalisco) | 3450 / 6900 | 1783 | no |
| `gepp-acapulco` | Acapulco (Centro Sur) | 1200 / 2400 | 1869 | no |
| `gepp-cancun` | Cancún (Peninsular) | 750 / 1500 | 1500 | no |
| `gepp-proplasa-pr1` | Proplasa (VdM Norte) | 2020 / 4040 | 1660 | yes |
| `gepp-proplasa-pr2` | Proplasa (VdM Norte) | 5670 / 11340 | 1660 | yes |
| `gepp-proplasa-tap` | Proplasa (VdM Norte) | 3760 / 7520 | 1660 | yes |

All are `division: SIN`, `giro: Industrial 24/7`, each with **12 monthly bills (2025)**.

The handler then produces:
- **`services{}`** — per‑service diseño, résumé (`money()`), finance, and alerts.
- **`proplasa_rollup`** — subtotal across the three Proplasa services (antes, ahorro, capex, BESS kW/kWh).
- **`portfolio`** — 4 sites / 6 services totals: `bill_antes_anual`, `ahorro_anual`, `ahorro_pct`,
  `capex_total_mxn`, `pv_gen_anual_kwh`.

---

## 13. End‑to‑end flow (summary)

```
POST {mode}
  │
  ├─ compute ──▶ merge_inputs ─▶ for each bill:
  │                                validate ─▶ bands/umbral ─▶ PV credit ─▶ PV demand ─▶
  │                                BESS shave ─▶ arbitrage ─▶ clawback ─▶ {pv,bess,hibrido}
  │                              ─▶ annualize ─▶ neto_disp (falla) ─▶ regimen+alerts
  │                              ─▶ finance{PV,BESS,Hibrido}: cashflows ─▶ TIR/VPN/payback
  │
  ├─ size-bess ▶ summer avg punta ─▶ E_util=2h·kW ─▶ nominal(÷DoD√RTE, round 100) ─▶ 0.5C power
  │
  └─ gepp ─────▶ seed 6 services ─▶ compute each ─▶ per-service + Proplasa rollup + portfolio
```

Everything is deterministic and pure: the same inputs always yield the same numbers, which is why
the port could be verified field‑for‑field against the Python golden engine.
