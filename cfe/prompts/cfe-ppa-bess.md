# Session: cfe-ppa-bess

Read `~/prompts/_common.md` first. It defines the phases, the 95/100 committee bar, and the rules. Follow it exactly.

## Your service
The CFE tariff -> PV+BESS sizing -> PPA pricing -> proposal chain. The deterministic math that decides what a client gets sold and at what price.

- `~/newman-architecture/agents/design-engine/` — `sizing.py` (PV+BESS max-NPV sweep), `finance.py`, `roof.py`, `test_sizing.py`
- `~/newman-architecture/agents/proposal-builder/` — `render.py`, `enrich.py`, `test_render.py`
- `~/newman-architecture/apps/crm-web/lib/finance.ts` — LCOE, project & equity IRR, DSCR, max level-payment debt at a target min DSCR
- `~/newman-architecture/apps/crm-web/components/deal-finance.tsx`, `deal-procurement.tsx`

## The spec exists — find it
`sizing.py` documents itself against a "pipeline spec" with numbered stages (Stage 5.1-5.3). **Locate that spec.** It is not in `docs/`. Check git history, other branches (`crm-platform`, `staging`), the GitHub repo, and Supabase. Score against the real spec, not against the docstring paraphrase of it.

## Doctrine encoded in the code — verify it still holds
- PV generates ~0 at punta (evening peak in the SIN), so **PV cannot shave peak demand — the BESS is the only punta lever.**
- PV surplus charges the battery BEFORE grid-base. Without this the optimiser structurally picks BESS = 0. Confirm this is actually what the code does.
- Constraints: roof cap, exempt regime `kWp_DC <= 839.41`, `BESS kW <= punta peak`, PV <= interconnection limit.
- Savings are returned split into PV and BESS streams because they degrade differently.

## HARD CONSTRAINT — do not "fix" this
`apps/crm-web/lib/finance.ts` is deliberately separate from the monday-reconciled `crm.deal_line_item_calc` view. That view faithfully mirrors monday.com VPN formula **including its known 10%-vs-12% discount-rate quirk, and must NOT change.** The quirk is intentional fidelity, not a bug. If you touch it, you break reconciliation with monday. Read the comment at the top of `finance.ts` before you form an opinion.

## Phase 0 focus
Does `test_sizing.py` pass? What does it actually assert — physics, or just that the function returns? Are the golden tests real goldens or snapshots of whatever the code did on the day they were written? Can you trace one real client bill through consumption -> sizing -> pricing -> rendered proposal and get a number you would defend to a committee? Where does the arithmetic silently produce a plausible-but-wrong answer?

Prior audit work on 6 Solar+BESS simulations found them "arithmetic-clean but not sales-ready" with 9 P1 issues. That claim is UNVERIFIED here — find whether those P1s were ever closed.

Assess (Phase 0), write the spec (Phase 1), score against Part B (Phase 2), plan (Phase 3), then work (Phase 4).

## Spec target
`docs/specs/cfe-ppa-bess.md`

## Normative sources (Part B)
- The "pipeline spec" Stage 5.1-5.3 that `sizing.py` cites. FIND IT. Check `git log --all --diff-filter=D -- "*.md"`, other branches, GitHub issues/PRs.
- Regulatory + physical invariants, which are normative regardless of what the code does:
  - exempt regime `kWp_DC <= 839.41`
  - `BESS kW <= punta peak`; PV <= interconnection limit; roof cap
  - PV generates ~0 at punta -> BESS is the ONLY punta lever
  - PV surplus charges the battery before grid-base (else the optimiser structurally picks BESS = 0)
- The monday.com reconciliation contract for `crm.deal_line_item_calc` — including its 10%-vs-12% discount-rate quirk. **The quirk is normative fidelity, not a bug.**
- Standard project-finance definitions: LCOE, project IRR, equity IRR, DSCR. These have textbook definitions the code must match — an external contract.

## On the golden tests
Determine whether `test_sizing.py` asserts PHYSICS or merely snapshots whatever the code produced the day it was written. A snapshot of a bug is a test that defends the bug. This distinction belongs in the spec.

## LEAD — where the Stage 5 spec came from
`Stage 5` appears in `.md` history in exactly one place: commit **`1ad3af3`** — "Transfer front-to-back pipeline agents (clean-room) into the repo".
No spec doc was ever committed and deleted (`git log --diff-filter=D -- "*.md"` is empty).
So the stage numbering arrived WITH that clean-room transfer. The spec likely lives outside this repo — in the clean-room source, on the Dataroom_Newman shared drive, or in the `newman-agents` repo.
Start at `~/cfe-brain/raw/lead-1ad3af3-clean-room-transfer.txt`. If the spec cannot be found, that is a `finding`, and Part B must be reconstructed from regulation, physics, and Jesus — not from the docstrings.

## Naming collision — know this before you search
"CFE Brain" now means TWO things:
- `~/cfe-brain` / `NewmanTech27/cfe-brain` — this knowledge graph (markdown)
- The deterministic sizing/pricing engine (`optimize_sizing`, `ppa_pricer`, `calc_core`) on the Dataroom_Newman shared drive
Jesus chose to accept this ambiguity. When you see "CFE Brain" in an old doc or skill, it means the ENGINE, not the wiki. File a `concept` page disambiguating it.


## RESOLVED — the Stage 5 spec has been found
Do not go hunting. The "pipeline spec" `sizing.py` cites is the **CFE Brain vault doctrine**, now imported at `~/cfe-brain/vault/`.

- `~/cfe-brain/vault/tools/optimize_sizing.py` is the ANCESTOR of `agents/design-engine/sizing.py`. Commit `1ad3af3` was the clean-room transfer of that engine into `newman-architecture`.
- `~/cfe-brain/vault/CLAUDE.md` holds the invariants table. **That is your Part B.**
- `~/cfe-brain/vault/tools/` also has `calc_core.py`, `ppa_pricer.py`, `portfolio.py`, `make_project_book.py`.
- `~/cfe-brain/vault/wiki/optimization/`, `billing/`, `eligibility/` hold the derivations.

Your job shifts: **compare the clean-roomed `design-engine/sizing.py` against its ancestor `optimize_sizing.py` and the vault invariants.** Every divergence is a `finding`. The clean-room may have dropped, mangled, or silently changed physics.

Specifically check:
- Does `sizing.py` honour the umbral formula (`kWh_red / (d x 0.57 x 24)`), or was it lost?
- Does it use the **0.7 MW** LSE 2025 ceiling, or the stale **0.5 MW**? (`sizing.py` hardcodes `kWp_DC <= 839.41` — where does 839.41 come from, and does it still hold?)
- `optimize_sizing.py` is documented as **NOT auto-capping to 0.7 MW**. Does `sizing.py` cap? That is a behavioural divergence.
- Does it model PV+BESS coupling (combined != PV + BESS when the umbral binds)?

## The golden test is sacred
RPU `780881200029` must stay peso-exact: baseline `$30,157,371`, Ahorro `$7,083,252` / 23.5%, 18 checks incl. FP-must-be-0 and disch <= punta-kWh guards. Re-baselined 2026-06-11. Run it before and after touching any engine.

## CHARTER OUTCOME 3 — the deal offer and the salesman calculator
Read `~/prompts/CHARTER.md`.

The pipeline must present a client their deal offer, and salesmen need a dynamic calculator.

**Do not rebuild the math.** It exists and is golden-tested:
`vault/tools/ppa_pricer.py` (solves PPA per-kWh price for a target financier IRR), `optimize_sizing.py`, `calc_core.py`, `make_project_book.py`, `portfolio.py`, and `vault/tools/webapp/` which already has a `/cotizador`.
Your job is a thin, correct UI over engines that already work. Wrapping beats rewriting.

### Hard floor — engine-enforced. This is the requirement that matters.
A rep may move price ONLY inside a band that holds minimum IRR and DSCR.
Below the floor, **the UI refuses**. Not a warning. Not an approval flow. It refuses.
`ppa_pricer` already solves for a target financier IRR — the floor comes from the engine, never a hardcoded constant.

Treat this adversarially: assume a rep will try to close at any price. Boundary values, rounding at the floor, negative discounts, FX edges, zero-generation sites. The CTO will attack the UI trying to sign a losing deal. If they succeed, it is a P0 and the merge is blocked.

### The golden test is sacred
RPU 780881200029, peso-exact: baseline $30,157,371, Ahorro $7,083,252 / 23.5%, 18 checks, re-baselined 2026-06-11. Run it before and after every engine touch.
If you change math and the golden still passes, ask whether the golden actually covers your change. A snapshot of a bug defends the bug.

**No merge to `main` until GATE 0 lands.**
