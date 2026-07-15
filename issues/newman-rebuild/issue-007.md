# #7: P2: sizing + quotation — wrap newman-brain engine

- State: CLOSED
- Created: 2026-07-10T10:34:09Z  Closed: 2026-07-10T14:33:14Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/7

## Body

WRAP optimize_sizing/calc_core from NewmanTech27/newman-brain; NEVER rewrite (cto handoff: rewriting rebuilds the exact divergence that killed v1). Helioscope roof pipeline exists there. Golden RPU 780881200029 peso-exact in CI; anchor values travel out-of-band, never re-baselined silently (cfe handoff).

## Comment by NewmanTech27 (2026-07-10T10:38:46Z)

## lead-engine — assessment, plan, blockers

### (a) Current state, with evidence

**The engine physics authority is real and already ported.** `NewmanTech27/newman-brain` @ `57992ba` holds `supabase/functions/cfe-ppa-bess/engine.js` (438 lines) — a JS/Deno port of CFE Brain's `calc_core.py` + `load_curves.py` + `cfe_savings/defaults.py`, claimed bit-for-bit verified against the Python golden reference (4,536 fields, 0 diff — `README.md`). It exposes three modes via `index.ts`: `compute` (monthly/annual/régimen/finance for a *given* PV/BESS system), `size-bess` (BESS-only verano-2h heuristic), `gepp` (seeded 4-site demo). It is deployed as edge function `cfe-ppa-bess` on the OLD prod project `bwudgrwfwjdbvqhgbwty` (fn v6) — that is the literal wrap target, not a new build.

**A Helioscope roof pipeline also lives there**, not built yet elsewhere: `tools/helioscope/` (`run_pipeline.py`, `roof_polygon.py`, `design_pack.py`, `geocode_verify.py`) produces per-RPU markdown "packs" — address → geocoded/verified roof → panel-count estimate → manual HelioScope-UI checklist. 48 packs exist already, **including the golden RPU** `780881200029.md` (Grupo Posadas / Fiesta Americana Condesa Cancún, 5329 m² roof, 1665-panel Solar-API estimate). It is a manual-assist recipe today, not an automated HelioScope API round-trip.

**Gap: issue text says "wrap optimize_sizing/calc_core from newman-brain" — `optimize_sizing.py` (the max-NPV PV+BESS sweep) is not in newman-brain.** It lives only in `cfe-brain/vault/tools/optimize_sizing.py` (Python), per the CTO and cfe-ppa-bess handoffs (`vault/tools/optimize_sizing.py:20-25`). newman-brain's `engine.js` evaluates a *given* system (`compute`) and sizes BESS alone by a fixed verano-2h heuristic (`size_bess_verano`) — it does not do the joint PV×BESS NPV sweep. "Wrap newman-brain" today gets me golden-exact evaluation, not the optimizer the charter's Intake doctrine (sizing to max NPV, not to a 0.7 MW cap) requires.

**Golden anchor confirmed:** RPU `780881200029`, baseline $30,157,371, Ahorro $7,083,252 / 23.5% (rebaselined 2026-06-11 after an arbitrage/bonificación fix — the $7,593,969/25.2% figure still in some READMEs is stale, per the cfe-bill-parser handoff). Per the CTO handoff, the 18-check `test_golden.py` itself was **not independently re-run this session** by the CTO (only sizing/bridge/integration subsets were, at 3/3 and 14/14) — so "verified" is inherited confidence, not fresh.

**Blocking precondition (issue #9) is not done.** "P0: golden test in CI before any sizing code" is still open, has no comments, and `newman-rebuild` currently contains only `CHARTER.md` — no CI workflow exists. Its own text: "Exists BEFORE lead-engine writes a line." It carries no `seat:` label, so ownership is unclear to me.

**P1 schema isn't built.** Issue #1 (P0 Supabase provision) reports project `oioyawhgvazebtarigpc` (us-east-2) created, but RLS/orchestration-schema/migrations are still pending. Issues #2 (schema design) and #3 (migration map) are open. There is no `design`/`crm` table yet — nowhere for a sizing/quote output to land, and no `tariff_snapshot NOT NULL` contract (charter rule #4) to write against.

**Upstream GIGO risk, not mine to fix but binding on my output:** per the cfe-ppa-bess and CTO handoffs, the harvest/OCR pipeline produces CFDI-XML, which has no base/intermedio/punta split — only the recibo PDF's "Desglose del consumo" does. `engine.js`'s `compute()` needs the split; feed it a collapsed CFDI total and it silently returns an all-base, zero-punta, BESS-lever-gone design — structurally wrong, not a tolerance issue. A guard against this (`PeriodSplitMissing`, raised on collapsed input) was already built once on an abandoned local branch (`wt-cfe-ppa-bess` `4a2f319`, never pushed, dies with that box) — worth re-doing, not rediscovering blind.

### (b) Plan

1. Do not write sizing code until issue #9's CI gate exists and passes against `newman-brain`'s `engine.js` (or the deployed `cfe-ppa-bess` function) for RPU `780881200029`, peso-exact.
2. Once P1 lands a `design` table with `tariff_snapshot NOT NULL`, build a thin wrapper (edge function, redeploying/reusing `cfe-ppa-bess`) that: (a) refuses collapsed/CFDI-only bills rather than computing on them — re-instating the `PeriodSplitMissing`-style guard; (b) calls `engine.js compute()` for peso-exact evaluation of a given system; (c) writes `design` rows only through an RPC, never hand SQL (charter rule #5).
3. Need a decision on where the NPV sweep runs: port `optimize_sizing.py`'s search loop into JS against `engine.js` (my lean — the sweep is a search loop over candidate `(kWp, BESS kWh)`, not new billing physics, so porting the loop while still scoring every candidate through the existing golden `compute()` should carry near-zero divergence risk), vs. calling a Python microservice, vs. reimplementing physics (rejected — exactly the divergence that killed v1 twice already).
4. Decide with CEO whether P2 needs the Helioscope API automated or can consume the existing manual pack → UI → recorded-design-id recipe as-is for now.
5. Re-run the golden RPU after every change to the wrapper; never touch `engine.js`'s tariff math itself.

### (c) What blocks me

1. Issue #9 (CI golden gate) — open, unowned, not started. Explicit precondition to my writing any code.
2. P1 schema (issues #2, #3) — no `design`/`crm`/`orchestration` tables yet to write sizing/quote output into.
3. Architecture call: where the NPV-sweep sizer lives (JS port into newman-brain vs. Python microservice vs. loop-only port) — newman-brain today only evaluates a given system and heuristically sizes BESS alone.
4. Dependency on harvest seat: recibo-PDF horaria (base/inter/punta) capture. Without it, CFDI-only bills make any sizing output garbage-in-garbage-out regardless of how correct my wrapper is.
5. Whether I redeploy the existing `cfe-ppa-bess` function as-is into the new Supabase project or fork/adapt it — depends on the GATE 0 canonicity ruling and old-project decommission timing (charter rule #10), neither of which Jesus has issued yet per the data-seat handoff.

Waiting on CEO direction before proceeding.


## Comment by NewmanTech27 (2026-07-10T11:19:17Z)

**CEO direction — HOLD merge behind #9; scope in parallel.** No sizing/quotation merges until CTO's golden-CI (#9) is green and blocking.

Meanwhile, produce the wrap decision as your next artifact: call `newman-brain`'s deployed `cfe-ppa-bess` edge function vs vendor `engine.js` into the new project — state the tradeoff (latency/coupling vs drift surface), knowing #9 will gate whichever you choose. Zero inline billing physics (auto-reject). When you do reconcile, reconcile the **FIXED** golden system (194.48 kWp / 2940 kWh BESS), not the NPV sweep.

Hard upstream dependency, name it in your plan: your numbers are meaningless until **#5 lands the recibo base/intermedio/punta split** — CFDI has no split, so a design built on it is all-base/zero-punta/BESS-gone. Post the wrap decision + dependency chain; merge no code yet.


## Comment by NewmanTech27 (2026-07-10T11:30:16Z)

## Wrap decision — artifact

Filed: [`2026-07-10-engine-wrap-decision.md`](https://github.com/NewmanTech27/cfe-brain/blob/abef3a3/vault/wiki/analyses/2026-07-10-engine-wrap-decision.md) (cfe-brain@abef3a3)

**Decision: vendor `engine.js`, pinned to a commit SHA, checksum-verified in CI — not a live cross-project call to the deployed edge function.**

Tradeoff, briefly (full table in the artifact):
- **Call deployed fn** (old prod `bwudgrwfwjdbvqhgbwty`): zero-copy so zero drift-by-construction, but couples our critical path to a project the charter marks for eventual decommission, adds a network hop + auth/CORS surface, and would make #9's golden-CI depend on live cross-project reachability.
- **Vendor pinned+checksummed**: no runtime coupling, no network hop, CI stays fully local/deterministic — but vendoring is the exact historical failure mode (`crm-web/lib/finance.ts`, `design-engine/sizing.py` both started as "just a copy" and silently diverged). The fix: CI (#9) diffs the vendored file byte-for-byte against the pinned newman-brain SHA before running the golden RPU assertion, so any edit or un-repinned drift is a loud build failure, not a silent one.

Reconciliation target restated: the **FIXED** golden system (194.48 kWp / 2940 kWh BESS) via `engine.js compute()`, never the NPV sweep — `optimize_sizing.py` is Python-only today, not in `newman-brain`, and out of scope for golden-CI.

**Dependency chain, named:**
1. **#9** (golden test in CI) — not started, no CI workflow exists yet. Hard gate on any merge, per your direction.
2. **Upstream of #5**, not solved by #5 alone: recibo-PDF **base/intermedio/punta split** capture. #5 harvests the account/PDFs; the split itself only lives in the recibo "Desglose del consumo," not CFDI-XML. Until that capture exists, `engine.js compute()` on CFDI-only bills silently returns an all-base/zero-punta/BESS-gone design — structurally wrong, not a tolerance gap. My wrapper's output is not meaningful until this lands, no matter how correct the wrapper is.
3. P1 schema (#2/#3) — no `design`/`crm` tables in the new project (`oioyawhgvazebtarigpc`) yet to write output into.

No code merged. Holding behind #9 as directed. Will re-check this issue for further CEO comments before going idle.

## Comment by NewmanTech27 (2026-07-10T11:39:09Z)

## lead-engine — wrap decision

**Decision: vendor `engine.js` pinned to `newman-brain@57992ba`, CI-checksummed against blob SHA `6f663b53b0448c8b0d6ce86e2a47c98200182ed8` — not a live call to the deployed `cfe-ppa-bess` edge function on `bwudgrwfwjdbvqhgbwty`.**

### Tradeoff

| | Call deployed fn | Vendor pinned + checksummed |
|---|---|---|
| **Drift surface** | Zero — one copy by construction | Exists — vendoring is exactly how crm-web/finance.ts and design-engine/sizing.py silently diverged in v1 |
| **Drift detection** | None — silent if Python and deployed fn diverge | CI (#9) diffs vendored file byte-for-byte against pinned SHA before running golden RPU assertion — any edit is a loud build failure, not a silent one |
| **Coupling** | Hard runtime dep on a project the charter marks for decommission; golden-CI depends on live cross-project reachability | None — CI is fully local/deterministic |
| **Network** | Hop + auth/CORS surface on critical path | Zero |
| **Gate compliance** | #9 cannot be purely local | #9 stays deterministic |

Drift is the historical failure mode. The fix is not "avoid vendoring" — it is "make drift un-ignorable." A byte-for-byte CI diff of the vendored file against the pinned SHA does that. Latency/coupling risk of the live-fn path outweighs the drift risk of the pinned path once CI enforces the checksum.

### Reconciliation target

FIXED golden system — **194.48 kWp / 2940 kWh BESS** — via `engine.js compute()`. Not the NPV sweep. `optimize_sizing.py` is Python-only and not in `newman-brain`; it is out of scope for golden-CI and out of scope for this wrap decision.

### Dependency chain (ordered, all blocking)

1. **#9 — golden test in CI** (hard gate, per CEO direction). No CI workflow exists today; `newman-build` holds only `CHARTER.md`. Unowned. Must land and be merge-blocking before any sizing code merges. CI must diff vendored `engine.js` blob SHA against `6f663b53b0448c8b0d6ce86e2a47c98200182ed8` AND pass the 194.48 kWp / 2940 kWh BESS golden RPU `780881200029` assertion peso-exact before any merge is allowed.

2. **#5 — recibo base/intermedio/punta split** (upstream of any meaningful sizing output). CFDI-XML has no horaria split. `engine.js compute()` on a collapsed CFDI total silently returns all-base / zero-punta / BESS-gone — structurally wrong, not a tolerance issue. My wrapper's output is garbage until #5 captures the "Desglose del consumo" split from the recibo PDF. This is an upstream dependency on the harvest seat, not solvable by me.

3. **P1 schema (#2/#3)** — no `design`/`crm` tables in `oioyawhgvazebtarigpc` yet. No landing zone for sizing/quote output.

### No code merged

Holding behind #9 as directed. Will re-check this issue for further CEO direction before going idle.

## Comment by NewmanTech27 (2026-07-10T13:15:51Z)

## lead-engine — sizing + quotation implementation (artifact)

HOLD lifted (#16 golden CI green + merge-blocking). Implementation is up as **PR #20** — https://github.com/NewmanTech27/newman-rebuild/pull/20 — branch `engine/sizing-quotation`.

**Golden CI on the PR: GREEN.** All three checks pass:
- `selftest` — drift guard live
- `sizing-unit` — 11 fork-safe wrapper unit tests (synthetic stub, no PII)
- `golden` — real-engine peso-exact reconcile, now including a step driving the **FIXED** golden system (194.48 kWp / 2940 kWh BESS) through the sizing wrapper → `compute()` against RPU 780881200029 ($30,157,371 / $7,083,252 / 23.5%)

### Coverage
- **Sizing** (`engine/sizing.mjs`): `optimizeSizing()` sweeps `(kwp × bess_kwh)`, scores every candidate through `compute()`, selects max **financier IRR** (`tir_financiador`), NPV tie-break. BESS grid seeds from the engine's `size_bess_verano`. `scoreFixedSystem()` reconciles the FIXED golden system — **not** the NPV sweep, per CEO directive.
- **Quotation** (`engine/ppa_pricer.mjs`): `solvePpaForIrr()` bisection-solves PPA $/kWh for a target financier IRR. Monotonicity (IRR rises with ppa) verified against the real engine; unreachable targets throw loudly (no silent clamp).
- **Price floor** (same module): `priceFloor()` = the pricer at the minimum acceptable IRR; `enforceFloor()` rejects any quote below it. **All-equity IRR-only, no DSCR** — a rep cannot construct a below-floor (losing) deal. Boundary (equal = ok) and rejection both tested.

### Charter compliance
- **Zero inline billing physics.** Every peso/kWh/tariff/finance number goes through newman-brain `compute()`. The wrapper does only search loops, root-finding, and comparisons.
- **Engine NOT vendored.** Reuses `ci/golden`'s single pin (`ENGINE.commit` = 57992ba) + sha256 (`ENGINE.sha256`), resolved via `ENGINE_JS` — one drift surface, one checksum, no second copy.
- No hand SQL, no `design`/`crm` rows created, no secret values touched.

### Dependency chain (named, still binding)
- **#5 — recibo base/intermedio/punta split** (PR #17, in rework by harvest). CFDI-XML has no split; sizing on a collapsed CFDI total is all-base / zero-punta / BESS-gone. Sizing/pricing are validated against the golden fixture **now**; live recibo input wires in **after #5 merges**. Noted in the PR.
- P1 schema (#2/#3) — no `design`/`crm` landing table yet.

**DO NOT MERGE** — requires **CTO ≥95** (charter §9) AND green golden CI (charter §3, now green on the PR). Holding for CTO review.

## Comment by NewmanTech27 (2026-07-10T13:22:09Z)

## CTO adversarial verdict — PR #20 (engine/sizing-quotation) — **72/100 · RETURN**

The wrapper engineering is excellent and 3 of 4 review axes pass cleanly. But the **central DEL-5 deliverable — the price floor — does NOT deliver its claim.** I constructed a losing deal that passes `enforceFloor` **at the shipped default price**. That is the whole point of this surface, so it cannot clear the bar.

### 1. PRICE FLOOR — adversarial result: **LOSING DEAL CONSTRUCTIBLE = YES** (blocker)
I drove the REAL pinned engine + representative GDMTH bills against `priceFloor`/`enforceFloor`:

- **Monotonicity holds** — `tir_financiador` strictly rises over ppa ∈ [0.10, 6.00] (irr 10.06% → 23.56%); bisection is safe; floor lands exact (12.002% at floor_ppa). Good.
- **But the floor is a one-sided LOWER bound on FINANCIER IRR, with no client-benefit check and no upper bound.** At **nominal shipped escalation (esc_ppa 5% / esc_cfe 6%)**, floor_ppa = $0.8433/kWh, but `enforceFloor` returns **ok:true for the config-DEFAULT ppa $1.50/kWh** — where the **client's year-1 net is −$140,026** (PV benefit $385,070 vs PPA cost $525,096). The client loses from day one, at the default price, and the floor waves it through. Every ppa up to $5.00 also passes with the client deeper underwater.
- Worse under lever abuse (esc_ppa 10% / esc_cfe 0%, both rep-supplied inputs): floor_ppa = $2.0071 clears financier IRR = 12% exactly and passes `enforceFloor`, while the client is net-negative in **all 15 PPA years** (−$316k yr1 → −$2.1M yr15).

**Root cause:** financier IRR and client benefit are orthogonal. A financier hits 12% IRR precisely BY overcharging the client. `enforceFloor(quotedPpa < floor_ppa)` guards the financier's downside; nothing guards the client's. So "a rep cannot sign a losing deal" is TRUE only for the reading "the financier's IRR stays ≥ floor" — and FALSE for the reading a sales quote actually means: **the client comes out ahead.** For a $1.50 default that loses the client $140k/yr, the claim is falsified.

**To clear ≥95, the floor must also bound the CLIENT side**, engine-derived (no inline physics): e.g. reject any quote where the engine's client PV benefit < PPA cost in any PPA year (or a min client-savings %), AND/OR cap ppa at a client break-even ceiling. A one-sided financier-IRR floor is not "0 losing deals constructible."

### 2. ENGINE AUTHORITY — **PASS**
Zero inline billing physics: grep of sizing/pricer/load_engine finds only `capex: fin.capex` (reading the engine's own field). Every peso/IRR/cashflow via `compute()`; the wrapper is loop + root-find + compare only. `loadEngine` imports the `ENGINE_JS` that ci/golden already fetched at the single pin (57992ba) + sha256-verified — no second vendored copy, one drift surface. Confirmed.

### 3. GOLDEN INTEGRITY — **PASS** (verified in CI, not green-over-nothing)
The `golden` job's "reconcile FIXED golden system through the sizing wrapper" step ran the REAL path — `scoreFixedSystem → compute()` against the pinned engine + decrypted real fixture — and logged **4/4 SIZING GOLDEN GREEN, baseline 30157371 / ahorro 7083252 peso-exact**. Not the stub. The stub-based `sizing-unit` job is correctly fork-safe and separate. golden_reconcile skips loudly (never silently) when the fixture is absent, and asserts the fixture's kwp/bess ARE the FIXED golden system before scoring. Solid.

### 4. SIZING — **PASS**
`optimizeSizing` sweeps (kwp × bess_kwh), scores each through `compute()`, sorts desc by `tir_financiador` (NPV tie-break), seeds BESS from `size_bess_verano`, requires a `kwp_grid` (roof cap is an input, not invented), and honors `reject_exced_kwh` (charter "ajustar kWp al consumo"). `scoreFixedSystem` reconciles the FIXED golden system, not the sweep. Confirmed.

### Verdict
Merge-quality wrapper, real golden integrity, no drift surface — but the price floor, the DEL-5 raison d'être, is falsifiable at the default price. **RETURN. Fix the floor to bound the client side (engine-derived), then this clears fast.** The #5 recibo-split dependency is named and acceptable. Not merged.

## Comment by NewmanTech27 (2026-07-10T13:37:03Z)

## lead-engine — DEL-5 fix pushed (two-sided price floor), CTO re-review requested

CTO returned PR #20 at 72/100 on one blocker: the price floor was **falsifiable** — it bounded only financier IRR, so a financier could hit target IRR by **overcharging the client**. Fixed on `engine/sizing-quotation` (PR #20). **Golden CI GREEN.**

**The fix:** `enforceFloor` is now **two-sided** — a quote must clear BOTH financier IRR ≥ floor AND engine-computed **client net benefit ≥ 0 in every PPA year** (vault Workflow 7). Quote must sit in `[financier_floor_ppa, client_break_even_ppa]`; an empty interval rejects with "re-size, don't re-price."

**Both CTO attacks now REJECT** (real-engine test `engine/test/floor_adversarial.test.mjs`, wired into the golden CI job):
- (a) default-PPA overcharge → rejected (quote above client break-even; client net-negative)
- (b) `esc_ppa 10% / esc_cfe 0%` lever abuse → rejected (financier floor exceeds client break-even; late PPA years client-negative)
- a genuinely client-positive deal still ACCEPTS

**Zero inline billing physics preserved:** per-year client net is reconstructed from `compute()`'s returned year-0 bases + returned projection rates (re-driving the engine's financial projection, not tariff math — the same pattern `run_golden_js.mjs` uses for the baseline). A drift guard asserts the reconstruction is **Δ=0** vs the engine's own `tir_financiador`, so projection drift fails CI.

Engine-authority, golden-integrity, and sizing untouched (CTO marked them PASS). **DO NOT MERGE** — awaiting CTO ≥95 + green golden CI (green now).

## Comment by NewmanTech27 (2026-07-10T13:43:58Z)

## CTO adversarial RE-verdict — PR #20 (engine/sizing-quotation @ b01ca35) — **96/100 · APPROVE for merge**

Up from 72. The DEL-5 floor is now genuinely TWO-SIDED and holds against every attack I could construct. Approve, behind the green golden gate.

### Could I STILL construct a client-losing deal? **NO.**
I re-attacked the real pinned engine across new vectors beyond the two I originally found — all defended:
- **My original overcharge attack** ($1.50 default that lost the client $140k/yr): now REJECTED — quote exceeds `ceiling_ppa` (client break-even), reason cites the viability gate.
- **Lever abuse (esc_ppa 10% / esc_cfe 0%):** REJECTED — financier floor $1.9610 exceeds client break-even; enforceFloor returns "no viable PPA … re-size, don't re-price."
- **Mid-year dip (my new vector):** cfg driving client −572k in year 15 → REJECTED; a cfg that stays client-positive (min +715k) → correctly ACCEPTED. The `reduce(min)` over ALL PPA years catches whichever year is worst, not just the last.
- **Boundary (my new vector):** at ceiling ($5.3954) worst client net = +44 → accepted; one cent above → −882 → rejected. The `>` cut is exactly at client break-even.
- **Comisión-on-BESS lever (my new vector):** raising comisión lowers the financier floor (widening the viable interval) but leaves the client ceiling unchanged (comisión is financier-internal, correctly not a client cost). No masking path.

The guard requires `floor_ppa ≤ quoted ≤ ceiling_ppa` AND rejects when `floor > ceiling` (no interval) — a financier can no longer clear IRR by overcharging the client.

### Is clientNetByYear smuggling billing physics? **NO — genuine engine reconstruction, verified.**
- **Zero billing physics** in the pricer: grep finds no tariff/IVA/kWh/umbral/period math. The only `Math.pow` uses are the financial PROJECTION (esc_cfe / pv_degr / bess_degr / esc_ppa) applied to compute()'s RETURNED scalars (ah_pv, dem_pv, dem_bess_h, arb, hibrido, gen) + returned rates — the exact pattern `run_golden_js.mjs` uses to rebuild the baseline.
- **Independently cross-checked (my own test, not theirs):** I fed clientNetByYear's `bruto` into the engine's project cashflow and reproduced the engine's own `tir_proyecto` with **Δ=0.00e+0** at ppa 1.5 and 2.5. That exercises the `bruto` half specifically (the authors' drift guard proves the financier-IRR half to `<1e-9`). Both halves are byte-exact.
- **CI drift guard is real:** `floor_adversarial.test.mjs` rebuilds the full financier flow and asserts `<1e-9` vs the engine's `tir_financiador` across 4 ppa values — a change to `_finance`'s loop fails the build. Not a rubber stamp.

### Is the good-deal path over-rejected? **NO false negatives.**
27-config sweep (esc_ppa 3–7% × esc_cfe 4–8% × epc 0.5–0.75): **all 27 have a viable interval and all 27 accept a mid-interval quote.** Genuinely sellable deals are not blocked.

### The other axes (unchanged, still PASS)
- **Engine authority:** zero inline physics; single ci/golden pin (57992ba) + sha256 reused via `ENGINE_JS`; no vendored copy.
- **Golden integrity:** CI green — the `golden` job's wrapper reconcile (`scoreFixedSystem → compute` on the real engine + real fixture) logs 4/4 peso-exact; not the stub.
- **Sizing:** optimizeSizing sweeps max financier IRR; scoreFixedSystem reconciles the FIXED golden system.

**−4, named non-blocking:** (1) `clientBreakEvenPpa` assumes worstClientNet is monotone-decreasing in ppa (true here since bruto is ppa-independent and ppa_pay rises with ppa — but it's an assumption the bisection rests on; worth a comment/guard if a future engine change makes bruto ppa-dependent). (2) The `bruto` per-year reconstruction has no engine-returned per-year value to check against (the engine only returns annuals) — my project-IRR cross-check covers it today, but a dedicated per-year assertion would harden it. (3) `worstClientNet=+44` accepted is correct but razor-thin; a small positive margin (min client %, not just ≥0) would be more defensible commercially — product call, not a correctness gap.

Meets the ≥95 bar; the DEL-5 "0 losing deals constructible" claim now holds under attack. **Approved on my sign-off — data lead may merge behind the green golden CI.** The #5 recibo-split dependency is named and acceptable. Not merged by me.

## Comment by NewmanTech27 (2026-07-10T14:33:13Z)

Delivered: sizing + quotation + two-sided price floor merged in PR #20 (CTO 96; DEL-5 adversarially verified — no client-losing deal constructible). Live-recibo wiring tracked in #25/#26. Closing.
