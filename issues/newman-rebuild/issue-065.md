# #65: pg_cron: claim ONE row per tick (endpoint/WAF throttle)

- State: CLOSED
- Created: 2026-07-11T11:06:45Z  Closed: 2026-07-12T12:27:58Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/65

## Body

Operator directive. Each pipeline stage's pg_cron job must NOT batch — claim exactly ONE row per 5-min tick, process it, advance, and the next row waits for the next tick. Serializes all CFE-facing work (Consulta/MiEspacio/Imperva stays cool) and dodges the edge WORKER_RESOURCE_LIMIT (one media per invocation).

Claim SQL: SELECT ... WHERE status in (ready states) AND (next_attempt_at IS NULL OR next_attempt_at<=now()) AND NOT needs_human_review ORDER BY priority DESC, created_at ASC LIMIT 1 FOR UPDATE SKIP LOCKED → update to in-progress + claimed_at + attempts+1 → pg_net to executor for THAT row only. Empty result = idle tick. Throughput 1/stage/5min (~12/hr/stage) — WAF-safe over fast; per-stage BATCH cap env (default 1) if ever raised. Reaper releases stuck single-slot rows so a stage never wedges. Part of #64.

## Comment by NewmanTech27 (2026-07-12T12:27:58Z)

Closing per INT-1. Artifact: `abc2357` (claim ONE row per tick). Note: later intentionally relaxed to tunable parallelism — `ec94211` (consulta) + `4398a5d` (extract, default 5 invokes/tick). Branch → main merge tracked in #101.
