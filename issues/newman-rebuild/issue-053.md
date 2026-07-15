# #53: Phase 4b: wire the 3 pg_cron jobs (twilio-sync / extract / harvest) + SQL stale-claim reaper

- State: OPEN
- Created: 2026-07-11T00:27:25Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/53

## Body

Once the endpoint daemon-crash bug is fixed, wire Supabase to drive the pipeline automatically every 5 min: cron.schedule 3 jobs using net.http_post (pg_net) → edge twilio-sync, edge extract (limit=2), mini /harvest (cap=1, via api.kameloso.com/newman/harvest) — each with the X-Newman-Secret header (store the secret in supabase_vault so cron can read it). Plus a pure-SQL reaper: any cfe.harvest_job 'running' past a timeout → failed + release its lock (belt for the endpoint watchdog). Start harvest cap at 1 and raise once stable.
