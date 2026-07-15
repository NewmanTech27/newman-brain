# GEPP — BESS Carga Solar + Autoconsumo Max (NR)

Mirror of `~/CFE Brain/work/gepp-carga-solar/` (2026-07-15). The solar-charge dispatch model
(rev4) and the "Autoconsumo Max / sin restricción de superficie" (NR) scenario for GEPP —
the pre-formalization prototype of the engine's future solar-charge mode
(`cfe-ppa-bess` / `calc_core` still charge the BESS from grid-base only).

## What this is

- **`dispatch_cs.py`** — hourly solar-charge dispatch simulator: BESS charges FIRST from
  same-day midday PV surplus (power-capped), grid-base tops up the shortfall; discharge =
  flat-top punta shave unchanged. Self-basis accounting anchored to the delivered rev3 books.
- **`sweep_cs.py` / `sweep_cs_ext.py` / `solve_k_cs.py`** — kWp sweeps with the PPA
  multiplier `k` re-solved at every point for combined investor TIR 14.0%.
- **`build_nr.py` / `verify_nr.py`** — the NR scenario (each site at its standalone optimum,
  single joint `k` over SITES4; k_NR = 0.949527) + its gate suite. Numbers: `NUMBERS_NR.md`.
- **`probe_peak.py` / `probe_bess_scale.py` / `probe_umbral.py` / `probe_verdict.py`** —
  the 2026-07-15 analysis answering *why the Autoconsumo Max optimum peaks*:
  marginal a/b/c decomposition (daytime self-consumption / BESS solar charge fixed at N/RTE
  by the discharge side / excedente @ texc≈0), BESS ×1.5/×2/×3 co-optimization (savings fall),
  umbral audit vs golden `calc_core` (book is ~3% conservative on demand savings), and the
  CON-vs-SIN BESS verdict under solar charge (+$268.2M VAN portfolio, CON wins all 4 sites).
  Findings: `ANALYSIS_PEAK.md` + `peak_analysis.json`.
- **`build_deck_cs.py` / `build_deck_nr.py`** — deck builders (v8 "Carga Solar" and the live
  v9 "…+ Autoconsumo Max" incl. the `#optimo` page). Gates: `domstub_*.js`, `shots_*.py`.
- **`QA_FACTS.md`** — fact pack behind "GEPP - Preguntas Anticipadas (2026-07-15)"
  (in `entregables/propuestas/`): per-site supplier/baseline doctrine (CFE pleno at
  autoabasto sites; TALA/ENEL exit does not move the reported PV+BESS savings).

## Running

```sh
cd tools/gepp-carga-solar
BOOKS_DATA=$PWD/books_data.json python3 dispatch_cs.py     # or any probe/build script
```

Notes:
- `books_data.json` (rev3 book extract) is included; always run with `BOOKS_DATA` pointing at it
  (the in-code default is a stale scratchpad path).
- `load_curves.py` is a snapshot of `~/CFE Brain/tools/load_curves.py` (canonical copy lives
  in the vault); scripts `sys.path`-insert the vault path first and fall back to this dir.
- Deliverables (deck HTMLs, Q&A, rev4 xlsx books) live in this repo under `entregables/`;
  the live Drive copies are the client-facing truth (deck file id `1b42OnSxhVUrRHm4XCDMqaBF5fV3kL_PO`).
- Prefeasibility grade: monthly B/I/P data + synthetic intraday curves (no 15-min HM),
  no site visit. `tools/cfe_savings` golden engine untouched.
