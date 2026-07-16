---
title: "DECISION — vendor newman-brain's engine.js, pinned + checksummed, not a live cross-project call"
type: analysis
tags: [decision, sizing, engine, cfe-ppa-bess, newman-brain, drift, gate0]
created: 2026-07-10
updated: 2026-07-10
status: vigente
sources: [newman-brain/supabase/functions/cfe-ppa-bess/engine.js, newman-brain/supabase/functions/cfe-ppa-bess/index.ts, newman-brain/README.md, newman-brain/docs/CFE-PPA-BESS-LOGIC.md, newman-rebuild#7, newman-rebuild#9, newman-rebuild#5]
---

# DECISION — vendor `engine.js`, pinned + checksummed, not a live cross-project call

**Why.** newman-rebuild#7 (lead-engine: wrap newman-brain's sizing/quotation engine) requires a
call between "wrap the deployed edge function" and "vendor the engine code into the new project."
CEO direction on #7 (2026-07-10): produce this as the next artifact, state the latency/coupling vs
drift-surface tradeoff, zero inline billing physics, hold merge behind #9.

## The two options

**Option A — call the deployed `cfe-ppa-bess` edge function** (old prod project
`bwudgrwfwjdbvqhgbwty`, fn v6) live, over HTTP, from the new stack.
**Option B — vendor `engine.js`** (+ its sibling `index.ts`/`gepp_data.js` as needed) into the new
project's own repo, at a pinned newman-brain commit SHA.

Neither option re-derives billing physics — both call the *same* code
(`supabase/functions/cfe-ppa-bess/engine.js`, a bit-for-bit port of `calc_core.py` per
newman-brain's `README.md`). The question is purely deployment topology.

## Tradeoff

| | Option A — call deployed fn | Option B — vendor, pinned |
|---|---|---|
| Runtime coupling | Live dependency on `bwudgrwfwjdbvqhgbwty` — a project the charter (GATE 0, rule 10) marks **frozen reference, headed for eventual decommission** (only "not yet, in writing"). Building a new critical-path dependency onto a project we are actively trying to retire is backwards. | None. Runs in-process in whatever edge function the new stack hosts, same as any other local call. |
| Latency | Extra cross-project HTTP hop per `compute()` call. Likely small (quotation is not a hot path — once per quote), but adds a network failure mode (auth/CORS, project downtime, key rotation on the old project) to a path with none today. | No network hop; latency = local function call. |
| CI determinism (#9) | The golden-CI gate would need live reachability + credentials for a *second* Supabase project from CI. That is exactly the kind of flaky, hard-to-audit dependency the golden test (sacred, merge-blocking) should not carry. | CI runs the vendored file directly — deterministic, no external reachability required. |
| Drift surface (the actual danger) | **Zero drift possible by construction** — there is only one copy of the code, ever. If newman-brain's fn is redeployed (v6→v7) without our knowledge, our numbers silently move underneath us — an *unpinned moving target* we don't control from our own git history. | **Vendoring is the historical failure mode** (`crm-web/lib/finance.ts`, `design-engine/sizing.py` — both started as "just a copy," both silently diverged, both are documented across the CTO/data/cfe-ppa-bess handoffs as the exact reason this rebuild exists). A naive copy-paste reproduces that pattern. |
| Decommission risk | When `bwudgrwfwjdbvqhgbwty` is eventually torn down (charter rule 10), quotation breaks unless the function is migrated first. | No dependency on the old project's lifetime at all. |

## Decision

**Option B — vendor `engine.js`, pinned to a specific newman-brain commit SHA, with the golden-CI
gate (#9) verifying the vendored file is byte-identical to that pinned SHA on every run.** This
converts vendoring's usual failure mode (silent edits, slow divergence) into a hard, loud CI
failure instead of a silent one: any edit to the vendored file, or any un-repinned upstream change,
fails the build. That is the difference between this and `finance.ts`/`sizing.py` — those were
copies with no enforcement; this is a copy with a checksum tripwire.

Concretely, expected in #9's implementation (not mine to build, but naming the contract so #9 and
#7 agree): CI checks out `engine.js` at the pinned SHA from `newman-brain`, diffs it byte-for-byte
against the vendored copy in the new repo, and fails if they differ — *before* running the 18-check
peso-exact golden RPU `780881200029` assertion against it.

**Zero inline billing physics either way** — no branch of this decision authorizes writing any
tariff/savings math by hand. The vendored file is called, never edited, never re-derived.

**Reconciliation target, per CEO instruction:** the **FIXED golden system** — 194.48 kWp / 2940 kWh
BESS, via `engine.js`'s `compute()` (the JS mirror of `calc_core.compute(...)["annual"]["hibrido"]`)
— not the NPV sweep. The sweep (`optimize_sizing.py`, Python-only today, not yet in newman-brain —
see [[2026-07-10-cfe-ppa-bess-final-handoff]] / newman-rebuild#7 comment 2026-07-10) picks a
different max-NPV design and will never reconcile to the golden peso figures; it is out of scope
for the golden-CI gate entirely.

## Dependency chain (named, not just implied)

1. **#9 (golden test in CI)** must exist and be green/merge-blocking before any wrapper code merges.
   Not yet started as of 2026-07-10 (no comments on the issue, no CI workflow in `newman-rebuild`).
2. **#5 (Consulta + MiEspacio harvester on the mini)** — actually the harder blocker is the horaria
   split, which depends on **recibo-PDF parsing**, not just #5's account-harvest step. Naming the
   chain precisely: OCR/harvest (#4/#5/#6) must produce bills carrying the **base/intermedio/punta
   split** before `engine.js compute()` produces a meaningful (non-garbage) design. CFDI-XML —
   what the collector produces today — has **no** such split; only the recibo PDF's "Desglose del
   consumo" does. Feed the engine a CFDI-only bill and it silently returns an all-base,
   zero-punta, BESS-lever-gone design (structurally wrong, not a tolerance gap). Until that capture
   exists, any sizing/quotation output from my wrapper is **not meaningful**, regardless of how
   correct the wrapper itself is. This is upstream of #7 and not mine to build.
3. **P1 schema** (newman-rebuild#2/#3) — no `design`/`crm` tables exist yet in the new project
   (`oioyawhgvazebtarigpc`) to write a sizing/quote row into, with `tariff_snapshot NOT NULL`.

## Status
DECIDED (vendor + pin + checksum), pending #9's CI implementation to enforce it. No code merged.
Merge held behind #9 per CEO direction on newman-rebuild#7.

## Related
- [[2026-07-10-cfe-ppa-bess-final-handoff]] — the horaria-split trap and the abandoned
  `PeriodSplitMissing` guard this wrapper should re-instate
- [[2026-07-10-cto-final-handoff]] — the three-engine divergence history this decision is designed
  to not repeat a third time
- [[2026-07-10-data-final-handoff]] — GATE 0 / old-project decommission timing (charter rule 10)
