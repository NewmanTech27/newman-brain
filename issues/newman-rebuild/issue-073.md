# #73: twilio-sync LIVE → pipeline.twilio: automatic WhatsApp ingestion wired (non-CFE)

- State: CLOSED
- Created: 2026-07-11T14:31:34Z  Closed: 2026-07-12T12:28:15Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/73

## Body

## Done — new WhatsApp invoices now auto-flow into the pipeline

Board: "wire twilio-sync" + "deploy + enable cron".

### Changes
- **Repointed** `twilio-sync` edge fn from `rpc_sync_enqueue` (→ intake.upload) to **`rpc_enqueue_twilio`** (→ `pipeline.twilio`, status=received). Dedup moved from filename to the globally-unique Twilio **media SID**. Params: `p_message_sid, p_media_sid, p_media_url, p_from_number, p_mime_type`.
- **`rpc_enqueue_twilio`** persisted as a migration (was applied ad-hoc): `20260711260000`.
- **Edge secret aligned**: set `NEWMAN_SYNC_SECRET` = the canonical value shared by `pipeline.config` + the mini. Verified no live caller used the old value (only twilio-sync + the unwired extract edge fn reference it). Done via `--env-file` (value never in argv).
- **Deployed** twilio-sync (`--use-api`; the Docker eszip bundler errored, server-side bundler worked). `--no-verify-jwt`.
- **Cron enabled**: `pipeline-twilio-sync` (`*/5` at :00). Migration `20260711270000` (applied); trimmed out of the phase-2 CFE hold (`20260711250000`).

### Verified
- Direct POST: `messages:21, media:21, enqueued:0, skipped:21, errors:[]` — Twilio pull + dedup + enqueue path all work (existing rows dedup on media SID; a new invoice would enqueue).
- Full pg_cron path: `pipeline.invoke(functions_base_url||'/twilio-sync')` → pg_net `status_code 200`.

### Live cron topology (all non-CFE)
| job | schedule | does |
|---|---|---|
| pipeline-twilio-sync | */5 :00 | Twilio pull → pipeline.twilio |
| pipeline-extract | :01 | barcode RPU + OCR name → pipeline.consulta |
| pipeline-reaper | :04 | release stale claims |

Ingestion is now hands-off end-to-end up to `pipeline.consulta (pending)`. Live-CFE stages (consulta/harvest) remain CEO-gated (`20260711250000`, held).

Commits: `pipeline/orchestrator` (fn repoint + rpc migration), `pipeline/schema` (cron migration + phase-2 trim). All pushed.

## Comment by NewmanTech27 (2026-07-12T12:28:14Z)

Closing per INT-1. Artifacts: `64490d8` (twilio-sync cron live) + `b144171` (rpc_enqueue_twilio, dedup on media SID). Caveat stays tracked in #93: the deployed edge function source is still not in the repo. Branch → main merge tracked in #101.
