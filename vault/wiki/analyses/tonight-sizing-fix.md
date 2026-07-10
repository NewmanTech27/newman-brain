---
title: "Tonight's sizing.py fix — decision, commit, and what still gates deploy"
type: analysis
kind: decision
tags: [design-engine, sizing, cfe-ppa-bess, cto-verdict, gate-0, decision]
created: 2026-07-10
updated: 2026-07-10
rpu: "780881200029"
sources:
  - "wt-cfe-ppa-bess branch spec/cfe-ppa-bess @ 4a2f319 (parent 1253b6b); off dev"
  - "agents/design-engine/{golden_engine.py (new), sizing.py (rewired), test_sizing_golden.py, test_sizing_integration.py, test_sizing.py}"
  - "cto-verdict-log.jsonl CTO-V-001/002/003"
  - "sizing.py:186 residual inline umbral (FC=0.57) in _bills_from_monthload"
verified_against: "spec/cfe-ppa-bess @ 4a2f319; tests re-run by CEO 2026-07-10"
confidence: high (commit-cited; all three tests personally re-run to exit 0)
---

# Tonight's sizing.py fix — decision

**Context (drain):** I said "tonight's fix changed no prod." This records what was fixed, where,
and what still gates its deploy — because the commit lives on an unpushed local branch and would
otherwise vanish with the disk.

## Decision: fix on-branch, wrap-not-rebuild, no prod change

`agents/design-engine/sizing.py` was rewired to **delegate** its sizing to the authoritative,
golden-tested engine (`optimize_sizing.sweep` / `calc_core.compute`) via a new **`golden_engine.py`**
bridge. The **divergent inline physics was removed** — the umbral-less flat demand and the
inverted PV→BESS charge order are gone; the engine now computes them. A test that had *pinned*
the inverted behaviour was deleted, and **refuse-guards** were added so a period-collapsed CFDI
blob / a `MonthLoad` lacking the punta split **raises** rather than silently emitting all-base,
zero-punta sizing.

## Branch & commit — LOCAL ONLY

- Branch `spec/cfe-ppa-bess` @ **`4a2f319`** ("fix(design-engine): delegate sizing to the golden
  engine, remove divergent physics (step 2A, CTO-V-002)"), parent `1253b6b` (step 1 bridge).
- Worktree `~/wt-cfe-ppa-bess`, branched off `dev`.
- **`4a2f319` is on no remote** (`git branch -r --contains` → none). If this disk dies, tonight's
  fix is gone. See [[single-disk-risks]].

## Verification (re-run by the CEO session, not merely reported)

- `test_golden.py` → **18/18, exit 0** (`calc_core` untouched, so the sacred golden RPU
  `780881200029` = $30,157,371 / $7,083,252 / 23.5% cannot regress).
- `test_sizing_golden.py` → **3/3, exit 0**.
- `test_sizing_integration.py` → **14/14, exit 0**, including both refuse-guards.

## CTO verdicts (machine-readable, `cto-verdict-log.jsonl`)

- **CTO-V-001** — the three divergences CONFIRMED; `safe_to_fix=true`.
- **CTO-V-002** — GO for step 2; flagged input-mapping as where divergence can re-enter.
- **CTO-V-003** — GO on-branch, divergence removed; **NOT 95/100.** Gap to 95 is **step 3**.

## What still gates deploy

1. **Step 3** (the gap to 95): rewire `main.py` to real blobs + `size_from_bills`, retire the
   lossy `_bills_from_monthload` bridge, delete the now-orphaned `finance.py`, **source `FC` from
   the engine** (a residual inline `umbral = kwh_tot/(days*24*FC)` with `FC=0.57` remains at
   `sizing.py:186` in the lossy bridge — CTO's flagged drift-vector), and add a **peso-reconciled
   test on the live path**. Step 3 is **upstream-blocked** on the horaria-capture track (the
   collector must read the PDF recibo period split — see [[design-engine-input-mapping-wall]]).
   It is blocked, not foot-dragging.
2. **CTO ≥ 95/100** — merge bar; not yet met, and cannot be until the live path is golden-exact.
3. **GATE 0 + Jesus's canonicity ruling** — nothing merges to `main` first (see
   [[reset-vs-merge-hazard]]).
4. **A Jesus-approved deploy** — prod `/opt/newman-architecture/.../sizing.py` still runs the
   **OLD divergent** file; this commit changed no prod ([[design-engine-live-or-orphan]]).

## Related
- [[design-engine-live-or-orphan]] · [[the-58-designs]] · [[design-engine-input-mapping-wall]] · [[reset-vs-merge-hazard]] · [[2026-07-09-cleanroom-sizing-live-path-verified]]

## Confidence
High. Every claim is commit-cited and the three tests were personally re-run to exit 0.
