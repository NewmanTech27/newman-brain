# #117: Extract stage reprocesses rows (re-claim loop) — needs attempt cap / dead-letter bound

- State: OPEN
- Created: 2026-07-12T17:52:48Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/117

## Body

## Observed (dev re-extract)
Driving the extract stage in a claim-one loop, `pipeline.twilio` rows kept getting re-claimed and re-processed instead of settling — 37 inputs produced **324 consulta rows** (× multiple passes), and some rows stayed stuck in `received`/`extracting`. Before the unique-RPU fix (#114) each reprocess inserted a fresh duplicate consulta row.

## Likely cause
- A row that errors mid-extract (media fetch, OCR, transient) returns to a claimable state, and there's no visible **attempt cap / dead-letter** on the twilio stage — so it can be reprocessed indefinitely (each pg_cron tick or manual drive).
- Successful rows shouldn't be re-claimable; need to confirm `rpc_advance_twilio*` reliably lands `status='extracted'` and that `rpc_claim_twilio` respects `next_attempt_at` + an attempts ceiling.

## Fix direction
- Add an attempts ceiling on `pipeline.twilio` (like the other stages) → route to `needs_review`/dead-letter after N tries instead of looping.
- Verify `rpc_claim_twilio` honors `next_attempt_at` backoff so a transient failure isn't re-claimed on the very next tick.
- The unique index from #114 already prevents the *duplicate rows*; this issue is about the wasted reprocessing + stuck rows themselves.

## Note
Partly a test-harness artifact (a tight manual claim loop), but the underlying "no bound on twilio-stage retries" is real and worth closing.
