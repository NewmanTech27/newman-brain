# #80: reaper recycles COMPLETED consulta rows — 'derived' in stale predicate + advance never clears claimed_at

- State: CLOSED
- Created: 2026-07-11T18:13:34Z  Closed: 2026-07-12T12:28:23Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/80

## Body

## Problem (found by the drain loop)
Consulta stalls at 2 `derived` while `pending` grows — completed consulta rows get recycled back to `pending`:

1. `rpc_advance_consulta` sets `status='derived'` but **never clears `claimed_at`/`claimed_by`** — a terminal row still looks "claimed".
2. `rpc_reap_stale_pipeline`'s consulta predicate is `status in ('fetching','derived')` — so after the 15-min timeout it releases the **terminal `derived`** row back to `pending`.

Together: every derived consulta reverts to pending at ~15 min → re-runs → re-derives → reverts again. Infinite churn; the pipeline can never reach "flawless". (twilio/mi_espacio reapers correctly only touch the in-progress states 'extracting'/'harvesting', so only consulta is affected.)

Confirmed: derived ids 4,5 carry claimed_at aged 639s/339s, heading for the 900s reaper.

## Fix
- reaper consulta predicate → `status = 'fetching'` only (never recycle terminal 'derived').
- `rpc_advance_consulta` → clear `claimed_at`/`claimed_by` on success.
- Backfill: clear claimed_at on existing derived rows.

## Comment by NewmanTech27 (2026-07-12T12:28:23Z)

Closing per INT-1. Artifact: `1bb5faf` — reaper no longer recycles completed consulta rows. Branch → main merge tracked in #101.
