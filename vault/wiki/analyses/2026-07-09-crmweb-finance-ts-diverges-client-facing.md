---
title: "crm-web lib/finance.ts diverges from golden — live client-facing exposure"
type: analysis
tags: [tuesday-inputs, cfe-ppa-bess, cto-finding, finance-ts, umbral, del-5, client-facing, live]
created: 2026-07-09
updated: 2026-07-09
status: vigente
rpu: "780881200029"
sources: [newman-architecture/apps/crm-web/lib/finance.ts:294-307, newman-architecture/apps/crm-web/app/actions.ts, cfe-brain/vault/tools/calc_core.py:58,87-88,119,178]
---

# crm-web lib/finance.ts diverges from golden — live client-facing exposure

**Question (CEO, 2026-07-09):** `crm-web/lib/finance.ts` (`computeFinance`) is the engine
that actually faces clients. Does it reproduce the golden RPU `780881200029` (baseline
$30,157,371; Ahorro $7,083,252 / 23.5%), or does it diverge from `calc_core` the way
`sizing.py` did? Read-only.

## Answer — NO, it diverges. Verdict: NO-reconciles.

### Not golden-anchored
`grep 780881200029 | 30,157,371 | 7,083,252 | 23.5` over `apps/crm-web/**/*.{ts,tsx,json}`
→ **0 hits**. Same failure mode as `sizing.py`: no test ties it to the golden RPU. It
therefore cannot be asserted to reproduce $30,157,371 / $7,083,252 / 23.5%.

### Divergent billing physics — `groundedRevenue()` (`finance.ts:294-307`)
The savings the client sees come from `groundedRevenue`, used whenever real GDMTH TOU prices
are injected (`finance.ts:99`, fed by `crm_web_deal_baseline` via `actions.ts:173-178`):

1. **Umbral dropped.** `finance.ts:303-304`:
   `demandRatePerKw = demand_mxn / kw_max; bessDemand = min(bess_peak_shave_kw, kw_max) ×
   demandRatePerKw`. A flat demand shave on the **printed `kw_max`** — no
   `umbral = kwh/(d×24×0.57)`, no cap, no `max(kw_base,kw_inter,kw_punta)`. Golden
   `calc_core.py:87-88,178` applies all three. Same class of defect as `sizing.py`.
   Violates [[demanda-facturable]].
2. **RTE ignored on arbitrage.** `finance.ts:305`:
   `bessArb = bess_arbitrage_kwh × max(0, price_punta − price_base)`. No round-trip loss on
   the charge. Golden `calc_core.py:119` charges `carga = desc/rte`, so
   `s_arb = desc·(p_punta − p_base/rte)`. finance.ts **over-values** arbitrage. (Different
   from `sizing.py`'s PV-surplus-first inversion — here BESS arb kWh is a free decoupled
   input, no PV coupling and no RTE.)
3. **PV punta credit permitted.** `finance.ts:302`:
   `disp(solar_share_punta, kwh_punta) × price_punta` credits solar in punta whenever
   `solar_share_punta > 0`. In SIN, PV generates ~0 at punta ([[pv-savings-model]]); the
   golden engine treats punta PV as ~0 (conservative). Input-dependent over-credit.
4. **No baseline reconstruction.** finance.ts never computes the ANTES bill; it consumes
   bill-derived TOU aggregates. There is no $30,157,371 to reproduce here — so the headline
   Ahorro rests on the divergent levers above.

Fallback path is cruder still: with no TOU prices, `finance.ts:106` values savings as
`generation × tariff_mxn_kwh` — a flat blended rate, no billing physics at all.

## Why this is a live client-facing exposure (unlike design-engine)
`computeFinance`/`groundedRevenue` is the engine behind the **client-facing** proposal:
`app/p/[token]/page.tsx` (public token URL, ahorro/capex) + `components/proposal-sign.tsx`
(e-signature) + `crm_web_send_proposal` (`actions.ts:350`) + `sendFromDrawer` outbound
email/WhatsApp via comms-dispatch (`actions.ts:676`). A client can **view and e-sign** a
proposal whose Ahorro was computed by an un-golden engine that drops the umbral and
over-values BESS. This path can leave the building **without a human** — unlike
design-engine, whose output stops at an internal PDF.

## Recommendation
Escalate as a live DEL-5 client-facing exposure. Reconcile the client proposal to the golden
engine (wrap `calc_core`/`ppa_pricer`) or gate `crm_web_send_proposal` until reconciled.

## Confidence
High. Verified read-only against `newman-architecture @ a81c43c`; `finance.ts` not modified.

## Related
- [[2026-07-09-cleanroom-sizing-live-path-verified]] — the design-engine finding (internal-only)
- [[demanda-facturable]], [[pv-savings-model]], [[bess-savings-model]]
