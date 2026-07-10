---
title: "design-engine/sizing.py is a live, divergent engine — CTO verification + blast radius"
type: analysis
tags: [cfe-ppa-bess, cto-finding, sizing, umbral, pv-bess-coupling, del-5, live-path]
created: 2026-07-09
updated: 2026-07-09
status: vigente
rpu: "780881200029"
sources: [newman-architecture/agents/design-engine/sizing.py, newman-architecture/agents/design-engine/main.py, newman-architecture/scripts/deploy.sh, newman-architecture/agents/proposal-builder/main.py, cfe-brain/vault/tools/calc_core.py]
---

# design-engine/sizing.py is a live, divergent engine — CTO verification + blast radius

**Question (CEO, 2026-07-09):** the `cfe-ppa-bess` session reported three P0 divergences
between the clean-roomed `agents/design-engine/sizing.py` and the golden
`vault/tools/calc_core.py`/`optimize_sizing.py`. Are they real? Is the divergent engine on
a live path serving real clients? And does any consumer auto-send its output to a client?

## Answer

### 1. The three divergences are real (CTO read both engines line-by-line)

1. **Umbral dropped.** `sizing.py:128-130` shaves punta demand as flat
   `min(bess_kw, kw_punta) × demand_charge`; `sizing.py:143-148` (`baseline_cost`) charges
   demand as flat `kw_punta × demand_charge`. No umbral, no cross-period max. Golden
   `calc_core.py:87` computes `umbral = kwh_tot/(days×24×0.57)`, `:88` caps the basis by it,
   `:178` uses `max(kw_base, kw_inter, kw_punta)`. Violates [[demanda-facturable]].
2. **PV→BESS charging inverted.** `sizing.py:135-137` charges the battery from PV surplus
   first (grid pays only the remainder), so midday surplus charges the battery for free;
   golden `calc_core.py:119` charges the full `carga = desc/rte` from grid-base. The two
   value BESS arbitrage differently and cannot both reconcile to the golden RPU. Contradicts
   [[pv-bess-combined]]. The clean-room's own justification ("else the optimiser picks
   BESS=0") is false: `s_arb = desc·(p_punta − p_base/rte) > 0` regardless.
3. **Never golden-tested.** `grep 780881200029 agents/design-engine/` → 0 hits.
   `test_sizing.py` asserts sanity ranges only and one test defends divergence #2.

### 2. It is LIVE, on a production path serving real client RPUs — YES

- `agents/design-engine/main.py:34` imports `sizing`; `:12-13` runs `sizing.optimize` and
  persists via `insert_design`; `:128,:169` build `sizing.TariffCells`/`sizing.Limits`.
- Work queue: `main.py:17-18` pulls RPUs at pipeline_stage `verified` via
  `claim_design_requests`, then `insert_design` advances them to `designed`
  (`db/migrations/002_insert_design_advances_stage.sql:30`). Real RPUs.
- Deployed as a production systemd worker on **newman-vps**: `scripts/deploy.sh:31`
  `AGENTS=(… design-engine proposal-builder …)`; `deploy.sh:2` "run ON newman-vps by the CD
  workflow"; `deploy/systemd/newman-agent@.service`; `Makefile:58` `main.py --loop`.

### 3. Blast radius — does it AUTO-SEND to clients? NO. Human-in-the-loop.

The **only** consumer of design-engine output is `proposal-builder` (crm-web does **not**
read it — `grep get_latest_design|insert_design|design` over `apps/crm-web/**/*.ts{,x}`
returns zero). And proposal-builder is **internal-only**:

- `agents/proposal-builder/main.py:145-151` renders a PDF and uploads it to a Google
  **Drive** folder (`proposals_folder`).
- `main.py:162-172` `_notify()` emails `SALES_NOTIFY` (default **agents@newman.re**,
  `:48`) the subject `"[Newman] Propuesta lista - {client}"`. Recipient is the **internal
  sales team**, not the client. `main.py:16-17` docstring confirms: "Notifies the sales
  team by email."

So the divergent numbers land in an **internal PDF + internal email**. No client email,
WhatsApp, or PDF-to-client is automated on this path. A human must retrieve the proposal
from Drive and choose to send it. **Blast radius = internal artifacts, one human forward
from a client.** "Contained" means not-auto-sent, not "cannot reach a client."

## Two caveats that keep this a P0-adjacent, not a false-alarm

- **A separate client-facing auto-send path exists — on a different engine.** crm-web's
  `/p/[token]` proposal page (financiamiento/capex/ahorro + e-signature,
  `app/p/[token]/page.tsx`, `components/proposal-sign.tsx`), `crm_web_send_proposal`
  (`app/actions.ts:350`), and `sendFromDrawer` outbound email/WhatsApp via comms-dispatch
  (`actions.ts:676`) **do** reach clients — but they run on crm-web's own `lib/finance.ts`
  (`computeFinance`, `actions.ts:6,192`), a **third** engine unreconciled to golden or to
  design-engine. That is a distinct exposure worth its own finding, not the design-engine one.
- Three parallel savings engines now exist: golden `calc_core`, design-engine `sizing.py`,
  crm-web `lib/finance.ts`. Only the first is golden-tested. The charter says wrap the first.

## Recommended action

- Quarantine or fix `design-engine/sizing.py` before it writes more designs; it should call
  the golden engine, not reimplement billing physics.
- Open a separate finding on `lib/finance.ts` (the engine that actually reaches clients).
- CTO to verify by attack, when the salesman calculator lands, that no UI path reaches
  either non-golden engine.

## Confidence
High. Every claim verified by reading the code at the cited `file:line` on 2026-07-09
against `newman-architecture @ a81c43c`.

## Related
- [[2026-07-09-cfe-ppa-bess-cleanroom-divergences]] — the ppa session's originating analysis
- [[demanda-facturable]], [[pv-bess-combined]] — invariants violated
