# #175: docs: sync stale golden numbers in CFE Brain cfe_savings/README (mario's vault)

- State: OPEN
- Created: 2026-07-15T08:47:33Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/175

## Body

`/home/mario/CFE Brain/tools/cfe_savings/README.md` (droplet) still documents the PRE-rebaseline golden: TOTAL Ahorro $7,593,969 (25.2%). CLAUDE.md + calc_core + test_golden were re-baselined 2026-06-11 to $7,083,252 / 23.5% (18 checks). Anyone rehydrating from the README will chase a phantom 500k diff.

One-line fix in mario's vault — his working space, so either he applies it or we coordinate. Also worth adding there: Python ≥3.12 `sum()` is Neumaier-compensated — cross-language ports diverge ~1e-8 on aggregates unless reproduced (bit us twice in #161 and the #160 cross-check; peso-exactness unaffected).
Effort: 5 min + a message to mario. Prio: LOW but cheap.
