---
title: Clean-room design-engine/sizing.py diverges from the golden engine — CTO-verified
service: cfe-ppa-bess
kind: finding
sources: ["newman-architecture/agents/design-engine/sizing.py:120-149", "cfe-brain/vault/tools/calc_core.py:58,87-88,119,178", "grep 780881200029 design-engine/ = 0 hits"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Clean-room design-engine/sizing.py diverges from the golden engine — CTO-verified

`cfe-ppa-bess` reported three P0 divergences between the clean-roomed
`agents/design-engine/sizing.py` and the golden `vault/tools/calc_core.py` /
`optimize_sizing.py`. The CTO read both engines line-by-line on 2026-07-09 and
independently confirms all three. The clean-room reimplements the billing physics inline
and reproduces none of the three invariants that make the golden engine golden.

## Confirmed divergences

1. **The umbral is gone.** `sizing.py:128-130` shaves punta demand as flat
   `min(bess_kw, kw_punta) × demand_charge`; `sizing.py:143-148` (`baseline_cost`) charges
   demand as flat `kw_punta × demand_charge`. There is no umbral term and no cross-period
   max. The golden engine applies `umbral = kwh_tot / (days × 24 × 0.57)`
   (`calc_core.py:87`), caps the demand basis by it (`:88 basis_cap = min(kwp_, umbral)`),
   and uses `max(kw_base, kw_inter, kw_punta)` as the measured basis (`:178`). The
   clean-room uses `kw_punta` alone. Violates the [[demanda-facturable]] invariant
   (`kWh_red / (d × 0.57 × 24)`; basis = max(kW B,I,P) measured, capped by umbral).

2. **PV→BESS charging is inverted.** `sizing.py:132-137` charges the battery from PV
   surplus first (`pv_to_bess = min(surplus, charge)`) and bills only the remainder to the
   grid at `p_base`, so midday surplus charges the battery for free. The golden engine
   charges the full `carga = desc / rte` (`calc_core.py:119`) — grid-base, no
   surplus-first netting. The two value BESS arbitrage differently; they cannot both
   reconcile to the golden RPU. Contradicts [[pv-bess-combined]] (SIN case is typically
   additive). The clean-room's own justification ("without surplus-first the optimiser
   picks BESS=0") is false: `s_arb = desc·(p_punta − p_base/rte) > 0` regardless, since
   `p_punta ≫ p_base`.

3. **"Golden-tested" is false for the clean-room.** `grep 780881200029` over
   `agents/design-engine/` returns zero hits. `test_sizing.py` anchors to no golden RPU;
   it asserts sanity ranges only, and one test actively defends divergence #2. A snapshot
   of a divergence is not a golden test.

## Why this is the highest-value finding

Charter Outcome 3 is explicit: **wrap the golden engines (`ppa_pricer` → `calc_core`),
do not rebuild the math.** A second, wrong, self-tested billing engine already exists in
the tree. If the deal offer or the salesman calculator is ever powered by
`design-engine/sizing.py` instead of the golden stack, it will:

- fail to reconcile to the golden RPU `780881200029` (DEL-3);
- over-value BESS (free midday charging + no umbral cap on the demand basis), producing
  optimistic savings;
- and can therefore price a deal **below the true IRR floor** — a losing deal signed
  through the UI, which is the exact P0 the charter and DEL-5 exist to prevent.

## The decisive open question — is the clean-room on a live path?

Severity turns on one fact not yet established: **is `agents/design-engine/` wired into the
CRM deal flow / the calculator, or is it a dead experiment?**

- If live → this is an active P0; the deal offer is being computed by an engine that
  violates three invariants.
- If orphan → it is a latent trap that must be deleted or quarantined before the
  calculator is built, so no future wiring picks it up.

CTO action when the calculator lands: **verify by attack** that no code path from the
salesman UI reaches `design-engine/sizing.py`; only the golden `ppa_pricer`/`calc_core`
may compute a price or a floor.

## Related

- [[2026-07-09-cfe-ppa-bess-cleanroom-divergences]] — the ppa session's originating analysis
- [[demanda-facturable]], [[pv-bess-combined]] — the invariants violated
