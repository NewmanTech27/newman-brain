# #66: pg_cron: per-stage timing columns + pipeline.timing view (cadence optimization)

- State: CLOSED
- Created: 2026-07-11T11:06:47Z  Closed: 2026-07-12T12:28:01Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/66

## Body

Operator directive. Record seconds-taken per stage/phase so cron intervals are set empirically, not a blanket 5 min.

Common per row: duration_s (finished_at-started_at), queue_wait_s (waited for a slot). Per stage: twilio barcode_s/ocr_s; consulta fetch_s/derive_s/recibos_in_window; mi_espacio login_s/consulta_s/agregar_s/drain_s/eliminar_s (the #50 phase breakdown — measured live: consulta ~74s, login ~20s, census ~1s, agregar ~8s, drain=long/variable). View pipeline.timing: count/avg/p50/p95/max of duration_s + queue_wait_s per stage+phase over a trailing window → the dashboard for choosing each stage's interval. Executor returns phase timings in the advance payload; the RPC writes them. Complements #61 (accuracy telemetry). Part of #64.

## Comment by NewmanTech27 (2026-07-12T12:28:00Z)

Closing per INT-1. Artifact: `bb03b46` (per-stage timing columns + pipeline.timing view); live timings recorded in #70/#74 bodies. Branch → main merge tracked in #101.
