# imported/ — bill records reinterpreted from client workbooks

Derived, machine-readable bill records produced by **`tools/import_perfil_xlsx.py`**
from client "Perfil de Consumo" workbooks (e.g. the GEPP 2025-26 portfolio Excel).
This folder is **not** `raw/` — it holds reconstructions, regenerable at any time:

```
python tools/import_perfil_xlsx.py "raw/Perfil de Consumo Eléctrico GEPP 2025-26 (1).xlsx"
```

## What each service folder contains

```
imported/<slug>/
├── bills.json    list of monthly bill dicts — the SAME schema cfe_savings.extract
│                 produces from a PDF/CFDI recibo. The engine reads this directly.
├── inputs.json   calc_core inputs scaffold (cliente / division / demanda_contratada /
│                 municipio / giro). Sizing + financials are left blank for the
│                 cfe-savings-analyst to propose.
└── meta.json     provenance + per-month QA: how close the CFE reconstruction lands
                  to the client's own printed workbook total.
```

## How it works (and why the numbers are trustworthy)

The workbook gives, per plant per month: kWh by period (base/intermedia/punta),
demanda máxima by period, kWMax año móvil, kVArh, FP — plus a `Tarifas` sheet with
the per-plant monthly CFE rates by concepto. The importer **reconstructs** the
disaggregated MEM components (Generación B/I/P, Capacidad, Distribución, Suministro)
as `quantity × Tarifas rate`, applying the wiki's GDMTH demand logic (umbral
FC=0.57, capacidad on punta-coincident demand, distribución on measured max — both
capped by the umbral; see [[demanda-facturable]]).

It does **not** invent numbers. Validation against the client's own printed totals:

| Site (sheet) | vs client total | reading |
|---|---|---|
| Cancún (CAN) | **+0.12%** | faithful CFE recibo (residual = billing-days) |
| Acapulco (ACA) | +1.35% | ~CFE recibo (billing-days / 2% BT) |
| Ixtlahuacán (IXT) | +22.3% | full load @ CFE rates — **autoabasto Tala discount** |
| Proplasa PR1 | +45.0% | full load @ CFE rates — **ENEL discount** |
| Proplasa PR2 | +2.1% | mostly CFE |
| Proplasa TAP | +33.5% | full load @ CFE rates — **ENEL discount** |

Cancún's energy reconstructs to **0.000%** — proof the methodology is exact when the
client's charges were computed at CFE rates. For autoabasto sites (IXT, Proplasa) the
divergence **is** the Tala/ENEL discount: the reconstruction values the **full load at
CFE GDMTH rates**, which is the correct basis for sizing PV/BESS against the whole
consumption (the [[gepp]] brief: "combine autoabasto with on-site PV").

## Modeling an imported service

Any OS consumer that takes a bills folder works unchanged — `cfe_savings.extract.
extract_folder` reads `bills.json` when present:

```bash
# baseline + scenarios for one service (analyst proposes sizing)
python tools/portfolio.py --bills-root imported            # all imported services
```

```python
from cfe_savings.extract import extract_folder
import calc_core
bills = extract_folder("imported/gepp-cancun")
res = calc_core.compute({**inputs, "kwp": 700, "bess_kwh": 1700, "bess_kw": 850}, bills)
```

## Caveats

- **Coverage:** the workbook's plant detail is **2026 Ene–Abr only** (4 months). A
  bankable savings case wants ≥12 months — flag seasonality on any analysis built
  from this (consistent with CLAUDE.md load-shape doctrine).
- **No 15-min data:** load shape is modeled, not metered.
- These are **prefeasibility** inputs (client-Excel-derived), not CFE-bill-validated.
  When real recibos arrive, model from `raw/bills/<RPU>/` instead.

Source page: [[2026-06-10-perfil-consumo-gepp-2025-26]]. Engagement: [[gepp]],
[[2026-06-10-gepp-portfolio-project-check]].
