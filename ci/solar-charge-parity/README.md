# solar-charge-parity — dispatch_cs.py vs engine.js `solar_charge` (issue #5)

Gate for enabling the rev4 solar-charge dispatch in prod (#1): proves the
prototype that produced the delivered GEPP numbers and the flag-gated engine
port compute the same dispatch, that the flag is inert when OFF, and pins what
each side currently says the $954,437/yr solar-charge bonus is.

```
python3 ci/solar-charge-parity/run_parity.py
```

Python side runs `tools/solar-charge-bess-calculator/dispatch_cs.py` in-process
(stdlib only; `cfe_savings` resolved from `cfe/vault/tools/`); JS side runs
`supabase/functions/cfe-ppa-bess/engine.js` under node (same as newman-rebuild
`ci/golden/run_golden_js.mjs`). Exit 0 = parity OK.

## Fixture provenance

Everything derives from **committed repo data** — no PII, no external files:

- `tools/solar-charge-bess-calculator/books_data.json` — the rev3-book extract
  behind the delivered GEPP rev3/rev4 books (7 sites: ixt/aca/can/pro/pr1/pr2/tap,
  op1). Supplies kWh B/I/P, bundled tariffs t_base/int/punta, yields, BESS
  C28/C30, billing-period dias_punta.
- rev4 kWp = `dispatch_cs.NEW_KWP_OP1` (ixt 5170 / aca 1748 / can 1270; others
  rev3 kWp) — the sizes in the delivered rev4 books.
- Engine bills are constructed so bill-derived rates equal book rates exactly
  (`gen_<per> = t_<per>·kwh_<per>`, flat adders 0 ⇒ `bnd_b/i/p = t_base/int/punta`);
  demand charges zeroed (parity scope = energy dispatch, not demand savings);
  `bess_kw = C28`, `bess_kwh = C30/(dod·√rte)` so `deliv = C30`.
- `baseline_off.json` — full `compute()` outputs (minus inputs echo) of the
  **pre-flag** engine at commit `b53ad23` on this fixture. Regenerate only in a
  reviewed PR:
  `git show b53ad23:supabase/functions/cfe-ppa-bess/engine.js > /tmp/engine_preflag.js`
  `ENGINE_JS=/tmp/engine_preflag.js python3 ci/solar-charge-parity/run_parity.py --write-baseline`

## Checks and tolerances

| # | Check | Tolerance | Result 2026-07-17 |
|---|-------|-----------|-------------------|
| A1 | `solar_charge_split()` vs `sim_month()` on identical args, 7×12 months | 1e-6 kWh | PASS (worst 8.6e-10 kWh — exact port) |
| A2 | HEAD `compute(solar_charge:false)` and no-flag default vs pre-flag `b53ad23` baseline | bit-for-bit | PASS (flag inert, 7/7 sites) |
| A3 | Each side reproduces its pinned `solar_charge_bonus`; gap attributed with zero residual | ±$2 MXN; 1e-6 kWh | PASS |

## Current numbers (A3 pins)

| Site | prototype (delivered) | engine.js `solar_charge:true` | Δ |
|------|----------------------:|------------------------------:|---:|
| ixt | $644,140 | $559,892 | −13.1% |
| aca | $143,202 | $121,613 | −15.1% |
| can | $167,095 | $150,385 | −10.0% |
| pro/pr1/pr2/tap | $0 | $0 | — |
| **portfolio** | **$954,436** (= the $954,437/yr claim) | **$831,891** | **−$122,546 (−12.8%)** |

**The gap is a single, fully-attributed term** (bridge check, residual 0.0 kWh):
the prototype charges the BESS over the rev3 book's **billing-period**
`dias_punta` (22–27 d/month, winter-heavy), the engine over **calendar**
`punta_weekdays(y,m)` (19–22 d). Same hourly sim, same tariffs, same caps — the
`exced` cap never binds. This is the same book-vs-calc_core conservatism family
already flagged in `ANALYSIS_PEAK.md` (probe_umbral, ~3% on demand). Deciding
which punta-day basis governs GEPP re-quotes is part of the #5/#1 TIR decision
(prototype PPA k solved at combined investor TIR 14.0%, `solve_k_cs.json`; prod
`pipeline.config ppa_target_irr` = 19%) — recorded open, not forced by this
harness.
