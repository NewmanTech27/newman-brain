# #78: harvest failures mask the real error_class (hardcoded DRAIN_TIMEOUT) + drop detail — undebugable

- State: CLOSED
- Created: 2026-07-11T17:51:34Z  Closed: 2026-07-12T12:28:21Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/78

## Body

## Problem
`rpc_advance_mi_espacio` sets `error_class = 'DRAIN_TIMEOUT'` for ANY failed state, and stores no `last_error`. So every harvest failure — LOGIN_FAILED, CENSUS_UNREADABLE, RPU_MISMATCH, NO_TOTAL, CONSULTA_FAILED, a real drain timeout — all look identical, and `harvest_one`'s `detail` (the real reason) is thrown away.

Observed (drain loop): RPU `008241003311` harvest `failed` at 119s, 0 bills, labelled `DRAIN_TIMEOUT` — but 119s is far under the ~510s drain deadline, so it's NOT a drain timeout. The real cause is hidden.

## Fix
- `rpc_advance_mi_espacio`: add `p_error_class text`, `p_last_error text`; on failure store the coerced error_class (fallback UNKNOWN) + the detail in `last_error`.
- `harvest_one` already emits `error_class` (business_error) + `detail`; `pipeline_endpoint._harvest_advance_args` should pass them through.

Then harvest failures are debuggable and the #76 retry classifier sees the true class.

## Comment by NewmanTech27 (2026-07-12T12:28:21Z)

Closing per INT-1. Artifacts: `6f11963`, `9736357` — real harvest error_class/detail stored, DRAIN_TIMEOUT hardcoding removed. Branch → main merge tracked in #101.
