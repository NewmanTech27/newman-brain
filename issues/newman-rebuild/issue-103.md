# #103: No alerting when the pipeline stalls: pg_cron → pg_net is fire-and-forget, responses discarded, no watchdog

- State: OPEN
- Created: 2026-07-12T12:19:37Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/103

## Body

**Severity: p1**

`supabase/migrations/20260711230000_pipeline_cron.sql:42-48` — `pipeline.invoke` returns the `net.http_post` request id and comments "pg_net is fire-and-forget". Nothing anywhere reads `net._http_response`; grep across migrations + harvest for alert/notify/webhook = zero hits.

If the cloudflared tunnel, the mini, or NordVPN goes down, every cron tick still "succeeds" (the POST is queued), `cron.job_run_details` stays green, and rows accumulate in received/pending forever with nothing paging the operator. `pipeline.invoke` also builds the `X-Newman-Secret` header from a nullable config lookup — a missing `newman_sync_secret` row degrades to silent 401s.

**Fix:** stall-detector cron (oldest unclaimed row age > threshold → notification via pg_net to a webhook) + have `invoke` raise on missing secret. Distinct from #61 (harvest telemetry SLA report) — this is liveness alerting for the whole cascade.
