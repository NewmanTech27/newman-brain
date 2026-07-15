# #142: Cross-env cron duplication: develop/staging clones drive the same mini as prod

- State: OPEN
- Created: 2026-07-14T12:51:01Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/142

## Body

develop + staging are with_data clones of prod, so they inherit ACTIVE pg_cron pipeline
jobs and the same pipeline.config (mini_base_url=api.kameloso.com/newman,
functions_base_url → prod). Every 5 minutes THREE databases invoke the one mini executor,
which is pinned to prod via NR_URL — nonprod heartbeats triple the invoke rate, can hold
the single-flight lock, and make env attribution in logs impossible.

Fix options: (a) disable pipeline-% cron jobs as part of branch clone provisioning,
(b) env-stamp the heartbeat payload and have the endpoint reject non-matching envs,
(c) per-env mini_base_url (nonprod → 404 sink). At minimum (a)+(b).

## Comment by NewmanTech27 (2026-07-14T14:41:43Z)

Partially resolved / re-scoped after inspection. The mini-CALLING crons (pipeline-consulta/extract/harvest/twilio-sync/reaper) are already `active=false` on both the develop and staging clones — branch provisioning disables them, so nonprod does NOT hit the prod mini. The only live leak was pipeline-leak-requeue (added today in 20260714090000), which came up active on the clones because a fresh cron.schedule defaults active=true; it's pure SQL (no mini call) but I unscheduled it on both clones for consistency. Remaining durable gap: the post-clone provisioning step that disables pipeline-% must also catch NEW pipeline jobs (any future cron.schedule in a migration will re-arm on the clones). Options: (a) provisioning greps pipeline-% and disables all, or (b) migrations gate cron.schedule on a prod-only guard. Leaving open for (a)/(b).

## Comment by NewmanTech27 (2026-07-15T06:42:36Z)

Data point while wiring #159: develop's `pipeline.config functions_base_url` was the PROD URL (clone artifact) — a develop cron with that value invokes prod functions. Fixed on develop (now per-env URL). New `cfe-calculo-offers` cron additionally gates on `calculo_enabled` config key, default absent=off, so clones can't fire it until an operator enables that env explicitly. Staging value should be checked at promotion.

## Comment by NewmanTech27 (2026-07-15T10:04:28Z)

Pattern now proven for new crons: cfe-calculo-offers fires only where pipeline.config `calculo_enabled='true'` (default absent=off), and develop/staging `functions_base_url` are fixed per-env. Closing the remaining exposure means retrofitting the same config-gate onto the 5 pipeline-* jobs — mechanical but touches the LIVE prod cascade, so deferring to an operator-reviewed change rather than autonomous merge.
