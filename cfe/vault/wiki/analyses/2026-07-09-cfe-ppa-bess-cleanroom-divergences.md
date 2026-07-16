---
title: "cfe-ppa-bess — clean-room sizing divergences + IRR-only floor decision"
type: analysis
tags: [cfe-ppa-bess, clean-room, sizing, ppa-floor, finding, decision, umbral, pv-bess-coupling]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [newman-architecture/agents/design-engine/sizing.py, newman-architecture/agents/design-engine/finance.py, newman-architecture/agents/design-engine/test_sizing.py]
---

# cfe-ppa-bess — clean-room sizing divergences + IRR-only floor decision

**Question:** Charter Outcome 3 asks for a client deal offer + salesman calculator wrapping the
golden engines. Diffing the clean-roomed `agents/design-engine/sizing.py` (commit `1ad3af3`) against
its ancestor `tools/optimize_sizing.py` + `calc_core.py`: what physics survived, and can the
engine-enforced price floor actually be built?

## Answer

### Three engines — only one is golden
- **Vault pricing stack** `ppa_pricer.price()` → `calc_core.compute()` → `optimize_sizing.propose()`: golden-anchored, umbral ✓, all-equity (no DSCR), has a `/cotizador` webapp + `/api/ppa`. **This is what the charter says to wrap.**
- **Clean-room** `design-engine/sizing.py` + `finance.py`: reimplements billing physics inline, **never calls `calc_core`/`ppa_pricer`**, no umbral, no DSCR, tested only against itself. Diverges (below).
- **Underwriting model** `crm-web/lib/finance.ts`: full **levered** project finance — LCOE, project/equity/after-tax IRR, and a **DSCR credit gate** (`gateDecision` APPROVE/REFER/DECLINE, `finance.ts:241-262`). Its revenue physics is also flat (no umbral, `finance.ts:294-307`) and **un-reconciled** to `calc_core`.

Three engines model the same deal with three different revenue bases, none reconciled to each other.

### P0 divergences (clean-room vs golden engine)
1. **Umbral lost.** `sizing.py:143-149` charges flat `kw_punta × demand_charge` — no `kWh_red/(d×0.57×24)`, no `max(kW B,I,P)`. `calc_core:87,178` applies both. Violates [[demanda-facturable]]. Any clean-room savings number fails to reconcile to golden when the umbral binds.
2. **PV→BESS coupling inverted.** `sizing.py:135-137` credits *PV-surplus-charges-BESS-first*; `calc_core:119-120` charges the battery from **grid-base**. The two engines value BESS differently — they cannot both reproduce the golden RPU. Contradicts [[pv-bess-combined]] (SIN is typically **additive**). The clean-room docstring's justification ("without it the optimiser picks BESS=0") is arithmetically false: `s_arb = desc·(p_punta − p_base/RTE) > 0` regardless, and demand-shave is always positive.
3. **"Golden-tested" is false for the clean-room.** `test_sizing.py` never touches RPU 780881200029; asserts only sanity ranges; and `test_pv_surplus_charges_bess_first` *defends* divergence #2. A snapshot of a divergence, not a golden.

### Lesser divergences
- Autoconsumo handicaps dropped (mandatory backup per [[autoconsumo]], permit lag, 2% guard) → over-recommends crossing 0.7 MW.
- No availability factor in `finance.py` (headline not net-of-availability).
- RTE accounting differs: `sqrt(rte)` on delivery (`calc_core:58`) vs full `rte` on charge (`sizing.py:133`).

### Preserved correctly
- Exempt ceiling `kWp_DC ≤ 839.41` (0.7 MW AC × 1.199) — **not** stale 0.5 MW ([[generador-exento]]). ✓
- No hard auto-cap at 0.7 MW; `BESS kW ≤ punta peak`; `PV ≤ interconnection`; roof cap. ✓
- Finance param table faithful (WACC 12%, PV degr 0.5%/yr, BESS 1.25%/yr, split streams). ✓

### The floor — DECISION (Jesus, 2026-07-09): IRR-only
The pricing engine computes **financier IRR** but has **no DSCR** — it models an all-equity financier
(`ppa_pricer.deal_flows`, no debt tranche). DSCR is **not missing from the org** — it lives in the
levered underwriting model `crm-web/lib/finance.ts` (`gateDecision`, `target_dscr`), but that engine
is un-reconciled to the golden pricing path and uses its own non-umbral revenue. Enforcing IRR (from
`ppa_pricer`) and DSCR (from `finance.ts`) as one floor would join two engines that disagree on the
underlying cashflow. **Decision: the salesman floor enforces the IRR floor only.** Floor price =
`solve_ppa_rate(target_irr)` (the lowest PPA $/kWh meeting target financier IRR); below it the UI
refuses by recomputing `financier_irr` at the rep's price. DSCR is deferred as a scoped follow-on;
re-opens only if deals are levered at point of sale. Rejected alternative: build/reconcile a DSCR
layer now — larger scope, blocks the calculator, and unsupported by the current engine.

## Sources consulted
- Spec: `newman-architecture/docs/specs/cfe-ppa-bess.md` (Part B/C, GAP-01..11)
- [[demanda-facturable]], [[pv-bess-combined]], [[bess-savings-model]], [[pv-savings-model]], [[generador-exento]], [[autoconsumo]]

## Confidence
High on the divergences (verified by reading both engines + `calc_core` line-by-line). The
`ppa_pricer` 1e-9 match to `calc_core._finance` is a docstring claim **not yet independently
re-verified** — the floor's correctness rests on it (spec GAP-11). Prior "6-sim / 9-P1" audit
closure remains unverified (spec GAP-10).
