# #8: P2: DEALS front — HTML offer from design data

- State: OPEN
- Created: 2026-07-10T10:34:10Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/8

## Body

Deal row -> rendered offer, data injected. SECURITY GATE (tuesday handoff): existing SSO validator checks email suffix, NOT the Google hd claim — fix server-side hd verification before anything exposing RPUs/margins deploys.

## Comment by NewmanTech27 (2026-07-10T10:38:42Z)

## Seat: lead-crm — Phase 0 assessment on #8

### (a) Current state, with evidence

**The DEALS → offer pipeline already exists in the frozen reference (`newman-architecture`, `apps/crm-web`), not from scratch.** `tuesday.newman.re` is a live Next.js CRM (confirmed by the tuesday-inputs handoff: `curl` → 307 to `/login`). It already has:

- A deal detail page (`app/deals/[id]/page.tsx`) with a proposals panel (`components/deal-proposals.tsx`) that generates a `crm.proposal` row (`generateProposal(dealId)` → `app/actions.ts:342`) and exposes draft → sent → viewed → signed lifecycle with a public link.
- A public, unauthenticated offer render at `app/p/[token]/page.tsx`, reading via anon RPC `crm_proposal_public`, rendering a snapshot of line items grouped into `financiamiento` / `capex` / `ahorro` sections, plus a sign form (`components/proposal-sign.tsx`) that writes via `crm_sign_proposal`.
- This is functionally "Deal row → rendered offer, data injected" already built. Nothing here needs inventing; it needs judging against the charter and either wrapped or rebuilt clean-room per non-negotiable #2.

**The finance numbers behind that offer are a third, unreconciled savings/finance engine — confirmed by direct read today, not just inherited from the CTO/cfe-ppa-bess handoffs.** `apps/crm-web/lib/finance.ts` (307 lines) implements its own TOU-period revenue split (`groundedRevenue()`, lines 294-307: `solar_share_base/inter/punta`, `bess_peak_shave_kw`, `bess_arbitrage_kwh`) and its own project-finance stack (IRR/DSCR/LCOE/expected-loss risk pricing). It is wired live: `app/actions.ts:158-243` (`computeFinancials`) pulls real GDMTH TOU prices from `crm_web_deal_baseline` (base/inter/punta $/kWh, demand $/kW, measured kWh) and feeds them straight into `computeFinance()` in `finance.ts` — never into `calc_core`/`optimize_sizing`. This is exactly charter non-negotiable #2 ("inline reimplementation of billing physics is an auto-reject") and exactly what the CTO and cfe-ppa-bess handoffs warned about, and it sits directly upstream of the offer/proposal surface this seat owns — I can't build the DEALS front without first resolving what feeds it.

**The security gate flagged in this issue's own body is confirmed, and it's broader than one file.** `app/auth/callback/route.ts:39` — the *central* SSO callback served at `login.newman.re` that gates every `*.newman.re` app, including this CRM — checks `user.email.toLowerCase().endsWith("@newman.re")`, not the Google `hd` claim. This is the same class of defect the tuesday-inputs handoff found independently in `~/newman-sso/validator.py:44-49` (a separate, unapplied nginx `auth_request` gate). Two divergent implementations of the same wrong check exist right now. Any page this seat builds that renders RPUs, margins, or signed financing terms is exactly the kind of page the tuesday-inputs handoff calls a P0 if deployed before this is fixed.

**Unverified, inherited claims I'm flagging rather than asserting:** the data-seat handoff says `crm_web_send_proposal`, `crm_proposal_public`, `crm_sign_proposal` had EXECUTE revoked at runtime on 2026-07-09 (not in the migration ledger) as part of a freeze — I have not re-queried grants myself, so I don't know if those RPCs are currently callable at all. GATE 0 (dev/main two-way fork, canonicity ruling) is still open per the CTO handoff, so I don't know which branch or which Supabase project is "truth" to build against.

### (b) Plan

1. Treat `apps/crm-web`'s DEALS/proposal UX (page structure, draft→sent→viewed→signed lifecycle, public-token line-item render) as the **behavioral spec** to reproduce, per non-negotiable #2 the *math* behind it is not — that gets rebuilt to call the wrapped `newman-brain` engine, never `finance.ts`'s inline model.
2. Coordinate with lead-engine on the calling contract: what shape of sizing/savings/finance output the wrapped engine returns, so the offer renderer has a stable interface instead of guessing.
3. Fix (or get a ruling on who fixes) the `hd`-claim gap before wiring anything user-facing: this seat's own `auth/callback/route.ts:39` and the separate `~/newman-sso/validator.py:44-49` need one server-side `hd`-claim check, not two divergent suffix checks.
4. Design the offer surface against the tuesday-inputs Part B requirements already scored (56/100) rather than re-introducing the same gaps: expiry enforcement (GAP-02), rate-limiting on the public token endpoint (GAP-03), signer-identity binding (GAP-06) — all land on the exact RPCs (`crm_sign_proposal`, `crm_proposal_public`) this seat's offer page depends on.
5. Confirm with CEO/data-seat which Supabase project (old prod vs. new clean-room scaffold) this seat targets before writing any RPC or migration.

### (c) Blocked on

- No visible lead-engine interface yet to wrap — nothing to call instead of `finance.ts`.
- GATE 0 unresolved: unclear which branch/DB is canonical to build against.
- Ownership of the `hd`-claim fix is ambiguous across two repos (`newman-sso` vs. `crm-web`'s own callback) — risk of fixing it twice, divergently, if not assigned.
- Target Supabase project for this seat's work is undetermined.

Waiting for CEO direction before writing any code.


## Comment by NewmanTech27 (2026-07-10T14:44:36Z)

DEALS front built → PR #28 (feat/deals-front). DO NOT MERGE (data seat + CTO ≥95).

- **Offer render** `crm-deals/render/offer.mjs` — client-facing HTML from the engine-derived snapshot (6 KPI cards, price-gate banner, per-year client cashflow). Pure presentation, no finance.
- **Offer caller** `crm-deals/lib/offer.mjs` `buildOffer()` — CALLS the merged engine: `optimizeSizing` → `solvePpaForIrr` → `enforceFloor` → `clientNetByYear`. Zero inline finance (crm-web/lib/finance.ts NOT repeated).
- **Flow** `supabase/migrations/20260710170000_deals_proposals.sql` — `crm.deal`/`crm.proposal` + pipeline RPCs `rpc_open_deal` → `rpc_create_proposal` (FLOOR-GATED: hard-rejects unless enforceFloor cleared; schema `check(floor_ok=true)` too) → `rpc_publish_proposal` → `rpc_public_proposal(token)` (sole anon door for `/p/[token]`). Validated in a rollback-only txn against the rebuild DB.
- **Rendered-offer proof** committed: `crm-deals/proof/offer_proof.{html,png}`. Tests `node --test crm-deals/test/*.test.mjs` (6 pass) prove the gate rejects below-floor + above-ceiling overrides. Wired into the fork-safe CI job.
- **Security gate note (Tuesday handoff):** `/p/[token]` public link is anon by design (floor-cleared published snapshots only). Any internal page exposing RPUs/margins needs the **server-side Google hd-claim** verification — the existing SSO validator checks email suffix, not hd (`newman-sso/validator.py`). SSO seat's deliverable; hard precondition for deploy. Not built here.

## Comment by NewmanTech27 (2026-07-10T15:06:40Z)

## CTO adversarial verdict — PR #28 (feat/deals-front, DEALS front #8) — **88/100 · RETURN**

Genuinely good engine-driven design — zero inline finance, real RPC gate, a schema constraint as defense in depth. But three real gaps, one of them a commercially serious over-share on the anonymous client page. Returning.

### DEL-5 verdict — can a rep create/publish a below-floor or client-losing proposal?
Through the HAPPY path: **no.** `rpc_create_proposal` `raise`s when `p_floor_ok is not true`, and the schema `check (floor_ok = true)` blocks even a direct service_role insert. A below-floor rep override yields `floor.ok=false` (tested in offer.mjs) → rejected. Good.

**BUT the three layers all gate on the SAME un-cross-checked boolean.** `rpc_create_proposal` trusts the caller-supplied `p_floor_ok`; it never re-derives the floor, and — critically — it never asserts `p_ppa_price` sits within `[p_floor_ppa, p_ceiling_ppa]`. So a caller (anything holding service_role: a buggy offer build, a future rep-override path, a direct RPC call) that persists `floor_ok=true, ppa_price=$5.00, ceiling_ppa=$2.00` (client-losing, above ceiling) **passes all three layers.** The schema `check(floor_ok=true)` is not independent defense — it restates the same claim.
- **Fix (cheap, makes the DB an independent gate):** add `check ((floor_ppa is null or ppa_price >= floor_ppa) and (ceiling_ppa is null or ppa_price <= ceiling_ppa))`. Then a lying boolean with an out-of-band price is caught by the DB regardless of the caller. That is what turns "3 layers" into 3 *independent* layers.

### Anon `/p/[token]` door — SAFE re: only floor-cleared published snapshots, but it OVER-SHARES internal margin economics to the client (real gap).
- Access is correct: `rpc_public_proposal` returns a snapshot only for `state='published'` + non-expired; every base table stays default-deny; anon has EXECUTE on this ONE RPC. Since a proposal can only exist with `floor_ok=true`, a published one is floor-cleared. No table leak. ✓
- **But the snapshot CONTENT, rendered to the anonymous client, prints the financier's negotiation position.** `render/offer.mjs` shows the client: **"TIR financiador"** (financier IRR), **"Inversión CAPEX"**, and literally **"piso financiero $X/kWh y techo de beneficio del cliente $Y/kWh"** — i.e. the minimum price the financier accepts AND the client's break-even ceiling. Publishing the floor price and the client's max-tolerable price on a public link hands the client the entire markup range. This is a commercial disclosure, not a security bug, but on a *client-facing* offer it is serious.
- **Fix:** split the snapshot — a client-facing view (system, annual savings, PPA price, client net-benefit cashflow) vs an internal `pricing_gate`/financier-IRR/CAPEX/floor/ceiling view. `rpc_public_proposal` (anon) returns only the client view; the internal gate proof stays behind the SSO/service_role door. Keep `floor_ok` provenance internal.

### Owner pins — GAP.
All **4** DEALS RPCs (`rpc_open_deal`, `rpc_create_proposal`, `rpc_publish_proposal`, `rpc_public_proposal`) are SECURITY DEFINER with **zero** `alter function … owner to` — none pinned. `rpc_public_proposal` is especially important to pin (it's anon-callable). Pin all four.

### What's right (keep as-is):
- `offer.mjs` computes NO finance — drives the merged PR #20 wrapper (optimizeSizing/solvePpaForIrr/enforceFloor/clientNetByYear); every headline equals a direct `compute()` read (tested Δ<1e-9). No second finance engine. ✓
- Immutable snapshot, re-price = new proposal; deal/proposal states advanced only via RPC; tables REVOKE'd default-deny FORCE-RLS; unguessable 256-bit token. ✓
- The `ceil4` on the solved price (never rounds a hair below the floor) is a thoughtful touch.

### Path to ≥95:
1. Split the public snapshot so the anon page does NOT expose financier IRR / CAPEX / floor_ppa / ceiling_ppa.
2. Add the price-within-bounds CHECK so the 3 layers are actually independent.
3. Pin all 4 RPC owners.
All modest. Strong foundation; return for the client-facing over-share (the one I'd not ship). Not merged.

## Comment by NewmanTech27 (2026-07-10T15:56:55Z)

## CTO RE-verdict — PR #28 (feat/deals-front @ b3d9821) — **96/100 · APPROVE for merge**

Up from 88. Both of my blocking gaps are fixed, and fixed the right way. Approve.

### (a) Two INDEPENDENT price gates — the trusted boolean is GONE.
- **The `p_floor_ok` boolean is removed entirely.** `rpc_create_proposal` now takes `p_floor_ppa`, `p_ceiling_ppa`, `p_ppa_price` and hard-rejects on: any null, `floor_ppa > ceiling_ppa` (ill-formed bounds → "re-size, don't re-price"), `ppa_price < floor_ppa`, and `ppa_price > ceiling_ppa`. Gate #1.
- **Schema CHECK enforces the SAME band independently:** `floor_ppa`/`ceiling_ppa` are NOT NULL, plus `check (floor_ppa <= ceiling_ppa)` and `check (ppa_price between floor_ppa and ceiling_ppa)`. Gate #2 — fires even on a direct service_role INSERT that bypasses the RPC. These are two genuinely independent enforcement points on the engine-derived band (RPC logic + row constraint), not the same claim twice.

**Honest residual (named, non-blocking — inherent, not a defect):** neither gate can *re-derive* the bounds by calling the engine (SQL can't run the JS engine), so a caller that lies about BOTH bounds (`floor_ppa=0.01, ceiling_ppa=99`) still slips a bad price. But this is a real hardening over the boolean: the price must now be consistent with two persisted, correlated, audited numbers, and the bounds are stored for post-hoc reconciliation. Full independence would need a server-side engine call (out of scope for SQL). Consider a periodic reconciler that re-prices published proposals and flags any whose persisted bounds don't match the engine — a follow-up, not a blocker.

### (b) Anon over-share — FIXED.
- `offer_snapshot` is now the CLIENT-SAFE subset only (system, annual savings, PPA rate, client cashflow). The financier position (IRR, CAPEX, floor_ppa, ceiling_ppa) lives in SEPARATE internal columns, NEVER in `offer_snapshot`.
- `rpc_public_proposal` (anon) returns only `offer_snapshot`. Grep of `render/offer.mjs` for financier_irr/capex/floor/ceiling/pricing_gate = **0 real refs** (the one hit is a comment documenting the exclusion). The anon `/p/[token]` page no longer prints the financier's negotiation range to the client. Confirmed.

### (c) Owner pins — FIXED.
All **4** DEALS RPCs (incl. the anon-callable `rpc_public_proposal`) now `alter function … owner to postgres`. ✓

### Unchanged strengths: no inline finance (drives the merged PR #20 wrapper; headlines = compute() reads), immutable snapshots, RPC-only pipeline, default-deny FORCE-RLS tables, unguessable 256-bit token.

**−4:** the bounds-supplied-by-caller residual (inherent SQL limitation, mitigated by the two-number consistency + audit; reconciler as follow-up). Clears the ≥95 bar. **Approved on my sign-off — data lead may merge in migration order.** Not merged by me.
