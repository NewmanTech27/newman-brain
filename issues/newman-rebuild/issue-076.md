# #76: pipeline: no auto-retry for failed rows — transient DRAIN_TIMEOUT/WAF sit failed forever

- State: CLOSED
- Created: 2026-07-11T17:05:22Z  Closed: 2026-07-12T12:28:19Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/76

## Body

## Problem
`rpc_claim_{twilio,consulta,mi_espacio}` claim only `pending` rows. A `failed` row sets `next_attempt_at` (via `retry_backoff`) but **nothing ever re-claims it**, so transient failures never retry.

Observed live:
- harvest `id 7` (008221101813) → `DRAIN_TIMEOUT` (bridge wedged; #50 caught it, service removed, `leaked=false`) — a transient wedge that SHOULD retry, stuck `failed`.
- consulta `id 5,8` (096240956737) → `CONSULTA_NAME_MISMATCH` — not transient (see the name-accuracy issue), correctly terminal.

## Fix
Distinguish transient vs terminal error classes and requeue the transient ones:
- Transient (retry): `DRAIN_TIMEOUT`, `WAF_BLOCK`, `CONSULTA_EMPTY`, `UNKNOWN`, `HARVEST_EXCEPTION`, `LOGIN_FAILED`.
- Terminal (needs human / data): `CONSULTA_NAME_MISMATCH`, `NO_BARCODE`, `RPU_MISMATCH`.
- Either: `rpc_claim_*` also picks `failed` rows whose `error_class` is transient AND `next_attempt_at <= now()` AND `attempts < N`; or the reaper flips due transient `failed` → `pending`.
- Cap attempts; after N, mark terminal/needs_human_review.

## Scope
`rpc_claim_*` or `rpc_reap_stale_pipeline` + a `retryable(error_class)` helper. Keep claim-one-per-tick.

## Comment by NewmanTech27 (2026-07-12T12:28:18Z)

Closing per INT-1. Artifact: `7046f40` — reaper requeues transient failures (auto-retry). Branch → main merge tracked in #101.
