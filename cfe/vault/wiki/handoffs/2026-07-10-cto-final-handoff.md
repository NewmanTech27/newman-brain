---
title: "CTO final handoff — what the rebuild cannot reconstruct"
type: analysis
kind: handoff
tags: [handoff, cto, sizing, golden, finance-divergence, gate0]
created: 2026-07-10
updated: 2026-07-10
status: vigente
confidence: see per-claim tags below
verified_against:
  - newman-architecture@a81c43c   # live/deployed design-engine sizing path
  - wt-cfe-ppa-bess@4a2f319        # in-flight sizing fix (step 2A), branch spec/cfe-ppa-bess off dev
  - cfe-brain wiki @ HEAD (this commit)
sources:
  - newman-architecture/agents/design-engine/sizing.py:129-148 (a81c43c — the divergent live physics)
  - newman-architecture/agents/design-engine/main.py:171 (live worker still calls lossy optimize)
  - wt-cfe-ppa-bess/agents/design-engine/sizing.py:34,186 (fix: hand-rolled umbral + duplicated FC)
  - newman-architecture/scripts/deploy.sh:31 (design-engine is a deployed systemd worker)
  - vault/tools/calc_core.py:31,87 (golden engine; fc default + inline umbral)
  - vault/wiki/cto-verdict-log.jsonl (CTO-V-001..003, machine-readable verdicts)
---

# CTO final handoff — what the rebuild cannot reconstruct

I held the merge veto. I built nothing; I reviewed, re-scored, blocked. Below is only
what dies with my context — not what the repos or wiki already carry.

## 1. Traps documented nowhere (or only in scrollback)

- **THREE parallel savings engines exist; only one is authoritative.** `calc_core`
  (vault, golden-tested) vs `design-engine/sizing.py` vs `crm-web/lib/finance.ts`. The
  charter says *wrap calc_core, never rebuild*. Both others rebuilt it and diverged.
  **`crm-web/lib/finance.ts` is the dangerous one: it is on a client-facing AUTO-SEND
  path** (`/p/[token]` proposal + e-sign → `crm_web_send_proposal` → comms-dispatch
  email/WhatsApp), unreconciled to golden. design-engine is internal-only (Drive PDF +
  agents@newman.re). Confidence: **high** (read on 2026-07-09; not re-verified today).
- **A green test can DEFEND a bug.** `test_pv_surplus_charges_bess_first` pinned the
  *inverted* PV→BESS physics as the invariant — a snapshot protecting the divergence.
  Removed in 4a2f319. When you see a passing "golden," confirm it actually exercises the
  suspect path (grep the RPU); the extraction golden `test_golden.py` (18 checks) runs
  `calc_core`, NOT `sizing.py`. A pass there proves nothing about the sizing engine.
- **INPUT-synthesis vs SAVING is the line that decides wrap-vs-rebuild.** `sizing.py:186`
  computes `umbral` inline — I ruled it ACCEPTABLE because it rebuilds a *baseline input*
  the lossy abstraction discarded, not a saving (the engine computes savings). Rebuilding
  a *saving* inline is the sin; rebuilding an *input* faithfully is not. Subtle; get it
  wrong in either direction and you either drift or over-block. See CTO-V-003.
- **The droplet's git refs are stale** — `git fetch` before trusting any branch compare.

## 2. Work in flight — exact state

- **design-engine sizing fix, branch `spec/cfe-ppa-bess` @ `4a2f319`** (worktree
  `~/wt-cfe-ppa-bess`, off `dev`, NOT merged, NOT deployed). Step 2A landed: divergent
  inline physics removed, `sizing.optimize` delegates to `optimize_sizing.propose`/
  `calc_core.compute`. Tests I re-ran: integration 14/14, sizing-golden 3/3 (both exit 0).
- **Next step was STEP 3 (unstarted):** rewire `main.py:171` to build engine blobs and
  call `size_from_bills` (golden-EXACT); retire `_bills_from_monthload`; delete orphaned
  `design-engine/finance.py`; source `FC` from the engine (kill the `sizing.py:34` literal
  `0.57` duplicate). **Blocked upstream** on `cfe-collector` capturing the horaria
  (base/inter/punta) split — until then `optimize()` refuses collapsed input rather than
  emitting a design (the safety net).
- **GATE 0 unresolved.** `main`/`dev` are a two-way fork (+102/+55 as of 2026-07-09).
  My recommendation on record: **production DB is truth, reconcile git to it** (DEL-4 was
  5/75). Jesus never issued the canonicity ruling. Nothing was cleared to merge to `main`.

## 3. Claims I made but did NOT verify myself (honest)

- **The canonical 18-check `test_golden.py` — I never ran it this session.** I verified
  peso-reconciliation *only* through `test_sizing_golden.py` (3/3) and the integration
  test (14/14), which hit the same figures ($30,157,371 / $7,083,252 / 23.49%) via
  `calc_core`. I took ppa's "18/18" on trust. `calc_core` was byte-untouched, so risk is
  low — but I did not observe the 18-check pass. Confidence: **medium**.
- **GATE 0 fork counts (+102/+55)** are from 2026-07-09; branches may have moved.
  Confidence: **low today** (re-fetch before acting).
- **finance.ts client-facing divergence** — read 2026-07-09, not re-verified today.

## 4. The one thing the rebuild WILL get wrong unless told

**You will rewrite the CFE savings/pricing math instead of calling `vault/tools/calc_core.py`,
because writing fresh is easier than importing a vault engine — and that reproduces the exact
three-engine divergence this entire exercise existed to kill.** The golden RPU `780881200029`
must peso-reconcile ($30,157,371 baseline / $7,083,252 Ahorro / 23.49%) through **one** engine.
Any pricing surface — CRM, calculator, dashboard, proposal — must CALL calc_core, never
reimplement it. The umbral (`kwh/(days·24·0.57)`), the punta demand basis, and "PV generates
~0 at punta so BESS is the only punta lever" are where every rebuild silently diverges. And a
rep must never be able to sign a losing deal: the price floor is engine-enforced (IRR-only
today; no DSCR in the all-equity `ppa_pricer`).
