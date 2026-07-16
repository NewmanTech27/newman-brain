---
title: "Final handoff — cfe-ppa-bess (sizing / PPA / deal offer)"
type: analysis
kind: handoff
tags: [handoff, design-engine, sizing, ppa, cfdi, input-mapping]
created: 2026-07-10
updated: 2026-07-10
verified_against: 4a2f319  # spec/cfe-ppa-bess @ wt-cfe-ppa-bess (LOCAL ONLY, never pushed)
confidence: high (traps + code state); low where marked
sources:
  - "agents/cfe-collector/enrich.py:349"      # CFDI total dumped into kwh_base
  - "agents/design-engine/main.py:62,100"     # iterates get_consumption as list; derive_tariff reads importes
  - "agents/design-engine/sizing.py"          # step-2A adapter (rewritten @4a2f319)
  - "vault/tools/calc_core.py:14"             # golden hibrido anchor $7,083,252.47
  - "vault/tools/optimize_sizing.py:20-25"    # calc_core charges BESS from grid-base, not PV surplus
  - "vault/raw/bills/780881200029/"           # the only horaria-split fixture, single-disk
---

# Final handoff — cfe-ppa-bess

Role: CFE tariff → PV+BESS sizing → PPA price → proposal. Below is only what the
repos/wiki do NOT already say. See [[2026-07-10-design-engine-input-mapping-wall]]
and [[2026-07-10-design-savings-inverted-in-prod]] for the long forms.

## Traps documented nowhere (with evidence)

1. **The deterministic engine needs a horaria split the production data never
   captured.** `calc_core.compute` reads bills FLAT and period-SPLIT
   (`kwh_base/inter/punta`, `kw_*`, `gen_*`, `capacidad`, `year/month/days`). But
   the collector builds bills from **CFDI XML**, which has no base/intermedio/punta
   split: `enrich.py:349` dumps the CFDI total into `kwh_base`, leaves inter/punta
   absent, nests importes under `"importes"`. Only the **recibo PDF** ("Desglose
   del consumo") carries the split. Feed CFDI to the engine → all-base, zero-punta,
   BESS-lever-gone, structurally wrong (not a tolerance issue). **This is the trap.**

2. **`design-engine/main.py` cannot run against the live RPC contract** — before
   any sizing bug. `get_consumption` returns an OBJECT `{rpu,invoices[],fields[]}`
   but `main.py:62` iterates it as monthly rows; `get_bill_series` returns a
   SUMMARY with no `importes` but `derive_tariff` (`main.py:100`) reads them.
   (Evidence: `pg_get_functiondef`.) The engine-shaped blob is reachable via
   `get_bulk_bills` (returns raw `bulk_bill.bill` jsonb) — but see trap 1 and below.

3. **The 58 `client.design` rows have no reproducible provenance.**
   `client.invoice`=0 rows, `client.bulk_bill`=0 rows, yet `client.design`=58.
   design-engine's systemd unit is `disabled` and its journal is EMPTY — the worker
   never ran on this box. So the 58 designs cannot be regenerated and were not made
   here. Live hazard: **proposal-builder is ACTIVE (pid 1199)**; its only brake is
   an unset `PROPOSAL_RPUS` env. A brake that works by omission is not a brake.
   Quarantining the 58 is a prod write → Jesus decides; I never touched them.

4. **The `MonthLoad`/`TariffCells` abstraction can NEVER reconcile to the golden.**
   It holds blended per-kWh RATES (not MEM dollars), has no `days` (so no umbral),
   no kW split. Anyone wrapping the engine behind that abstraction fails. The only
   input that reconciles is the recibo-extracted FLAT engine bill.

5. **`sizing.optimize` is a SWEEP; it does not return the golden number.** The
   golden $7,083,252.47 is the FIXED golden system (194.48 kWp, 2940 kWh BESS) via
   `calc_core.compute(...)["annual"]["hibrido"]` (`calc_core.py:14`). The sweep
   picks a DIFFERENT max-NPV design. Reconcile a fixed system, not the sweep.

6. **The two engines disagreed on BESS charging direction.** Old design-engine
   `sizing.py` docstring claimed "PV surplus charges BESS before grid-base";
   `optimize_sizing.py:20-25` says calc_core charges BESS from grid-base. The
   golden engine (calc_core) is authoritative — the old docstring was wrong.

## Work in flight — exact state

- Branch **`spec/cfe-ppa-bess` @ `4a2f319`** in worktree `~/wt-cfe-ppa-bess`.
  **LOCAL ONLY — never pushed** (single-disk; dies with the box).
- `1253b6b` step 1: `golden_engine.py` — in-process bridge to `vault/tools` engine
  (`$CFE_ENGINE_PATH`, default `~/cfe-brain/vault/tools`), raises if absent (no
  inline fallback).
- `4a2f319` step 2A: `sizing.py` rewritten as a thin adapter. Inline divergent
  physics DELETED (`annual_savings` umbral-less flat demand + hand-rolled arbitrage,
  `baseline_cost`, `_better`, `PR/DOD/RTE`, finance import). Delegates to
  `optimize_sizing.propose`; `engine_bill_from_blob` maps `get_bulk_bills` shape →
  flat engine schema and RAISES `PeriodSplitMissing` on collapsed CFDI blobs.
  Tests green: extraction golden 18/18; bridge 3/3; integration 14/14 (golden
  hibrido reconciled through MAPPED pipeline bills + both collapse guards); legacy 2/2.
- **Next step (not done):** rewire `main.py` off `get_consumption`/`get_bill_series`
  onto recibo-extracted engine bills. BLOCKED on the horaria-capture track (a
  recibo-PDF parser that fills base/inter/punta into `bulk_bill.bill`). Deferred
  deliberately — wiring it now is GIGO.
- **Orphaned:** `design-engine/finance.py` (design-engine's own divergent finance;
  only the removed inline sweep used it). Left in place — deletion is a CTO call.
- **Not built:** the salesman price-floor UI (Outcome 3). Ruled **IRR-only**
  (ppa_pricer is all-equity, no DSCR). `crm-web/lib/finance.ts` holds a THIRD,
  un-reconciled DSCR engine (Part A7) — flagged, never reconciled.

## Claims I made but never verified (honest)

- The legacy `optimize(load,tariff,limits)` path delegates and doesn't crash, but
  its lossy reconstruction (days=30 assumed, adder folded into generation) yields
  engine-computed-but-**prefeasibility** numbers I never validated against a real
  client. **Confidence its numbers are correct: low.**
- I never verified where the 58 designs came from — only that the worker never ran.
- I never verified engine behaviour for **non-SIN divisions** (calc_core is
  calibrated SIN; PV partially generates in punta elsewhere = uncredited). Low.

## The one thing the rebuild team WILL get wrong unless told

They will feed the sizing/pricing engine from the **CFDI-XML** pipeline (that is
what the collector produces and the DB stores) and get silently wrong, all-base,
zero-punta designs — because **CFDI has no base/intermedio/punta split; only the
recibo PDF does.** Build recibo-split capture FIRST, or the deterministic engine
is garbage-in-garbage-out no matter how correct its math.
