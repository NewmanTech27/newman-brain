# #61: Extraction telemetry: RPU accuracy/drift SLA + regression gate

- State: OPEN
- Created: 2026-07-11T07:52:17Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/61

## Body

Committee major (10 cites): no measured end-to-end harvest success rate, RPU mismatch/drift rate, field-level precision/recall on the immutable RPU key, reconcile variance, or memory/latency SLOs — silent extraction regressions surface only downstream. Required: emit per-run extraction metrics, define an RPU-accuracy SLA, and a CI regression gate on a labeled set (depends on #55 harness). (#49)
