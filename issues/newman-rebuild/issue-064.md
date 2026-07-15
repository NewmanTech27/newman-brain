# #64: Re-architect pipeline: pipeline.{twilio,consulta,mi_espacio} + raw_cfe.{consulta,mi_espacio} (pg_cron cascade)

- State: CLOSED
- Created: 2026-07-11T11:02:28Z  Closed: 2026-07-12T12:27:56Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/64

## Body

## Decision
Swap the single twilio.pipeline view for a proper 3-stage cascade with two schemas, driven by pg_cron. Supersedes twilio.pipeline (#49).

## Cascade
pipeline.twilio → pipeline.consulta → pipeline.mi_espacio. Each stage advances only on success and creates the next stage's row (FK back). raw CFDI XML lives in raw_cfe, deduped by content sha256.

## Confirmed choices
- **One pipeline.twilio row per RPU** (a multi-barcode photo → N sibling rows, each cascades independently 1:1 downstream).
- **XML stored in-table** (raw_cfe.*.xml_content text, sha256-deduped; recibo XMLs are small). No storage bucket.
- **Build AFTER #63** (barcode-authoritative extraction) lands.

## Schemas
**pipeline** (state machine) + **raw_cfe** (immutable raw XML, sha256-unique).

## Common orchestration columns (every pipeline.* row — the pg_cron monitoring set)
id, status(stage enum), created_at, updated_at(trigger), claimed_at, claimed_by, heartbeat_at, started_at, finished_at, attempts, next_attempt_at (backoff — cron claims where now()>=next_attempt_at), last_error, error_class(enum), needs_human_review, human_confirmed_at, confirmed_by, priority.

## Stage tables (domain cols on top of the common set)
- **pipeline.twilio**: message_sid, media_sid, media_url, from_number, mime_type; rpu(barcode), barcode_ok, receptor_name(OCR seed); consulta_id. status: received→extracting→extracted→needs_review→failed (barcode_unreadable→needs_review).
- **pipeline.consulta**: twilio_id FK; rpu; razon_social(from XML), adeudo(latest, from XML LineaDeReferencia), latest_period(YYYYMM); raw_consulta_id FK; adeudo_refreshed_at; mi_espacio_id. status: pending→fetching→derived→refreshing→needs_review→failed.
- **pipeline.mi_espacio**: consulta_id FK; rpu, razon, amount; account_id, harvest_job_id; xml_count, pdf_count, bill_count, months_covered, leaked. status: pending→harvesting→harvested→partial→failed.

## raw_cfe (sha256 dedup, identical shape)
raw_cfe.consulta + raw_cfe.mi_espacio: id, sha256 UNIQUE (insert..on conflict do nothing), rpu, period(YYYYMM), serie_folio, uuid(CFDI TFD), xml_content(text), source_stage_id FK, created_at. → latest per (rpu,period) for consulta; N historical for mi_espacio; sha256 makes the monthly refresh + re-harvests idempotent.

## Monitoring view pipeline.flow
One row/invoice across all 3 stages: rpu, razon, adeudo, overall_status (intake→consulted→harvesting→done / blocked:<stage> / review:<stage>), each stage's status/attempts/last_error/updated_at, raw-XML counts.

## pg_cron jobs (5-min, pg_net→executors)
1. twilio-extract (barcode RPU + OCR name → advance / barcode_unreadable→review)
2. consulta-derive (Consulta → upsert raw_cfe.consulta sha256 → derive razon+adeudo → advance)
3. miespacio-harvest (mini /harvest → raw_cfe.mi_espacio sha256 → advance)
4. adeudo-refresh MONTHLY (0 6 1 * *): re-run Consulta for active services, update adeudo+latest_period from newest XML
5. reaper (5-min): stale claimed_at → release + backoff; hard-fail past max attempts

## Migration path
twilio.pipeline → this structure; move rpc_sync_enqueue targets to pipeline.twilio; wire the existing edge/mini executors to write stage rows; keep intake.upload/cfe.harvest_job data or migrate. Relates: #49 (epic), #57 (review gate reused as human_confirmed_at), #61 (telemetry), #63 (barcode-authoritative).

## Comment by NewmanTech27 (2026-07-11T11:05:18Z)

## Refinement: claim-ONE-per-tick (endpoint throttle)

Each pg_cron STAGE job must NOT batch — it claims exactly ONE row per 5-min tick, processes it, updates, and the next row waits for the next tick. This keeps CFE-facing endpoints (Consulta, MiEspacio/Imperva) cool and also dodges the edge WORKER_RESOURCE_LIMIT (one media per invocation).

Claim SQL per stage (atomic, concurrency-safe):
```sql
-- e.g. consulta-derive tick
with nxt as (
  select id from pipeline.consulta
  where status in ('pending','refreshing')
    and (next_attempt_at is null or next_attempt_at <= now())
    and coalesce(needs_human_review,false) = false
  order by priority desc, created_at asc
  limit 1
  for update skip locked
)
update pipeline.consulta c set status='fetching', claimed_at=now(),
  claimed_by='cron', started_at=now(), attempts=attempts+1
from nxt where c.id = nxt.id
returning c.*;   -- pg_net → executor for THIS one row only; empty result = idle tick
```
- LIMIT 1 + FOR UPDATE SKIP LOCKED → never two workers on the same row, never more than one CFE call per tick.
- Ordering: priority desc, then oldest first. Respects next_attempt_at (backoff) + skips needs_human_review.
- Throughput = 1 item/stage/5min (~12/hr/stage). A backlog drains slowly but WAF-safe — correct tradeoff. If a stage ever needs more, raise via a per-stage BATCH cap env (default 1), not by removing the throttle.
- The reaper stays: a row stuck 'fetching'/'harvesting' past a stage timeout → released (status back to pending, next_attempt_at backoff) so the single-slot never wedges the whole stage.
- The three CFE-facing stages each have their OWN independent 5-min slot, so twilio/consulta/miespacio can each advance one row per tick in parallel across stages (but serially within a stage).

## Comment by NewmanTech27 (2026-07-11T11:05:54Z)

## Add timing columns (to tune the pg_cron cadence later)

Every stage records seconds taken, so we can measure real durations and set each stage's cron interval empirically instead of a blanket 5 min.

**Common (every pipeline.* row):**
- `duration_s numeric` — total stage execution seconds (finished_at − started_at, stored explicitly for easy aggregation).
- `queue_wait_s numeric` — created_at/next_attempt_at → claimed_at (how long it sat waiting for a slot; tells us if the throttle is the bottleneck vs the endpoint).

**Per-stage sub-phase seconds (the optimization detail):**
- `pipeline.twilio`: `barcode_s`, `ocr_s`.
- `pipeline.consulta`: `fetch_s` (Consulta round-trip), `derive_s` (XML parse), `recibos_in_window` int.
- `pipeline.mi_espacio`: `login_s`, `consulta_s`, `agregar_s`, `drain_s`, `eliminar_s` — the exact phase breakdown already instrumented in #50 (measured live: consulta ~74s, login ~20s, census ~1s, agregar ~8s, drain = the long/variable one). Feeds the drain-timeout tuning too.

**Timing view — `pipeline.timing`:** per stage (+ sub-phase): count, avg / p50 / p95 / max `duration_s` and `queue_wait_s` over a trailing window. That's the dashboard for choosing each stage's cron interval: if p95 drain is 8 min, that stage's tick can't be 5 min; if consulta p95 is 90s, it could run more often. Complements the extraction telemetry in #61 (which captures accuracy/source); this captures latency.

The executor returns its phase timings in the stage-advance payload (mini /harvest already computes them), and the RPC writes them onto the row + into pipeline.timing on finish.

## Comment by NewmanTech27 (2026-07-12T12:27:56Z)

Closing per INT-1. Artifact: `bb03b46` (pipeline.{twilio,consulta,mi_espacio} + raw_cfe schema) + `abc2357` (pg_cron staggered claim-one heartbeats), branch `pipeline/schema`. Branch → main merge tracked in #101.
