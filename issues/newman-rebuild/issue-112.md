# #112: Pipeline dev branch can't run standalone — orchestration points at prod

- State: OPEN
- Created: 2026-07-12T16:47:47Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/112

## Body

## Observed (on Supabase pipeline `develop` branch `ugjqqezqtnjkzxkcqujz`)
The branch is a full data clone (37 twilio / 33 consulta / 12 mi_espacio) **and** the pg_cron jobs (`pipeline-extract/consulta/harvest/reaper/twilio-sync`) are active + pg_net present. But they don't process dev's rows — they target prod:

- `pipeline.config.mini_base_url` = `https://api.kameloso.com/newman` → the **prod** mini endpoint (`pipeline_endpoint.py` runs with prod `NR_URL` + `NR_SERVICE_ROLE_KEY`, so it claims/advances **prod** rows regardless of caller).
- `pipeline.config.functions_base_url` = `https://oioyawhgvazebtarigpc.supabase.co/functions/v1` → **prod** project functions.
- `pipeline.invoke(p_url)` POSTs only `X-Newman-Secret` + `{}` — it passes no target DB/creds, so the endpoint has no way to act on the caller's branch.

Net: dev's crons are effectively no-ops for dev (and redundant triggers against prod). A "prune + fresh run on dev" can't work as-is, and risks operating on prod.

## To make dev runnable standalone
1. **Deploy pipeline edge functions to the dev branch** (invoice-intake, twilio-sync, extract) — branches start with 0 functions.
2. **Stand up a dev-pointed executor** — either a 2nd `pipeline_endpoint.py` instance with `NR_URL`=dev branch + its service key (new port + tunnel route), or make the endpoint multi-tenant (accept the target project in the request, keyed by `X-Newman-Secret`).
3. **Repoint dev `pipeline.config`**: `mini_base_url` → the dev endpoint, `functions_base_url` → `https://ugjqqezqtnjkzxkcqujz.supabase.co/functions/v1`.
4. Then prune dev pipeline tables and let the dev crons drive a fresh run through the new code (multi-invoice fan-out #88, drain fixes #98).

## Also worth deciding
Cloned branches inherit **active** crons pointing at prod — either pause them on new branches or repoint on creation, so a clone doesn't add redundant load/triggers to prod.

## Comment by NewmanTech27 (2026-07-13T22:06:07Z)

Interim mitigation applied 2026-07-13: all 5 pipeline-* pg_cron jobs DEACTIVATED in develop + staging (cron.alter_job active:=false — definitions kept). Their pipeline.config still points at prod executors (functions_base_url = prod edge, mini_base_url = live mini), so with data now seeded into lower envs an active cron would have fired real CFE drives. Lower envs are data parks until standalone per-env config lands; prod crons untouched. Re-enable per env: select cron.alter_job(jobid, active := true) from cron.job where jobname like 'pipeline-%';
