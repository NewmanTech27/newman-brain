# #72: pipeline extract stage WIRED unattended (pg_cron → tunnel → mini) — Model B live

- State: CLOSED
- Created: 2026-07-11T14:05:07Z  Closed: 2026-07-12T12:28:12Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/72

## Body

## Done — extract runs unattended, full Model B loop proven

The Supabase-orchestrated extract stage is deployed and self-driving. Non-CFE only; consulta/harvest remain CEO-run.

### What's live
- **Persistent executor**: `com.newman.pipeline-endpoint` (launchd, KeepAlive) runs `pipeline_endpoint.py` under the nix devshell on `:8791`, secrets from `~/.newman-pipeline.env` (600, vault-mirrored). `run-pipeline-endpoint.sh` + plist committed as deploy reference.
- **Cloudflare route**: `api.kameloso.com/newman/pipeline/.*` → `mini:8791`, ordered before the `/newman/.*` → 8790 catch-all. Endpoint accepts the `/newman` prefix.
- **pipeline.config**: `newman_sync_secret`, `mini_base_url=https://api.kameloso.com/newman`, `functions_base_url`.
- **pg_cron (phase 1, applied)**: `pipeline-extract` (`1-59/5`) + `pipeline-reaper` (`4-59/5`), both active.

### End-to-end proof
`select pipeline.invoke(mini_base_url||'/pipeline/extract')` → pg_net `status_code 200`, body `{"claimed":1,...}`, row `claimed_by=cron`. i.e. pg_cron → pipeline.invoke → pg_net → Cloudflare → mini → barcode/OCR → rpc_advance_twilio, fully unattended.

### Held for CEO greenlight (phase 2, `20260711250000`, NOT applied)
- `pipeline-twilio-sync` (edge — needs re-point at `rpc_enqueue_twilio` → `pipeline.twilio` first)
- `pipeline-consulta`, `pipeline-harvest` (live CFE)
- `pipeline-adeudo-refresh` (monthly)

### Note
Executor path is the worktree (`~/newman-rebuild-wt-drive/harvest`); repoint launchd to `~/newman-rebuild/harvest` after the pipeline branches merge to main.

Commits: `pipeline/executors` (endpoint prefix, run script, plist), `pipeline/schema` (cron phase-1/2). Both pushed.

## Comment by NewmanTech27 (2026-07-12T12:28:12Z)

Closing per INT-1. Artifacts: `6322b7a`, `7c267e3`, `1c669b1` — extract stage wired unattended (pg_cron → tunnel → mini), Model B live. Branch → main merge tracked in #101.
