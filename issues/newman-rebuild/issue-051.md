# #51: CONSULTA_FAILED: add to business_error enum + route bad-name uploads to human review (no retry-loop)

- State: OPEN
- Created: 2026-07-11T00:27:21Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/51

## Body

When Consulta can't unlock (bad/absent seed name), the harvest returns business_error=CONSULTA_FAILED. Two gaps: (1) 'CONSULTA_FAILED' is not a value in cfe.business_error, so rpc_harvest_event 400s on it (harvest_end still closes the job, but the event is lost). (2) The upload stays ocr_done='ready' and rpc_claim_harvest re-claims it (failed jobs are retryable) → a live-attempt retry loop that can never succeed until the name is fixed. Fix: add CONSULTA_FAILED (+ NO_TOTAL) to the enum; on CONSULTA_FAILED set the upload(s) needs_human_review=true (terminal) so the claim skips them (claim already excludes needs_human_review as of 20260711160000).
