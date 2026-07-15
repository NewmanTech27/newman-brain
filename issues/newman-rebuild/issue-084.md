# #84: reaper interrupts live deep harvests (15-min stale < 25-min harvest runtime) → risk of double-harvest

- State: CLOSED
- Created: 2026-07-11T19:47:13Z  Closed: 2026-07-12T12:28:28Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/84

## Body

## Problem (found verifying #83)
A deep harvest (grid=97) legitimately runs ~15-25 min (drain budget 1200s + phases, harvest_timeout 1500s). The reaper's 15-min stale timeout fired mid-drive and released the row `harvesting → pending` while the subprocess was still downloading (34 files in). Since single-flight (#82) only blocks a claim when a row is `'harvesting'`, the released `pending` row could be claimed by the cron → a SECOND concurrent harvest of the same RPU on the shared CFE account.

Caught it live: restored id 14 to `harvesting` before the cron re-claimed it.

## Fix (shipped)
`rpc_reap_stale_pipeline`: mi_espacio `'harvesting'` now uses a 30-min stale window (> harvest_timeout) so only a genuinely dead harvest is reaped. twilio/consulta keep 15 min.

## Deeper follow-up
Heartbeats would be more robust than a fixed timeout: the harvest thread updates `heartbeat_at` periodically so the reaper distinguishes a live-slow drive from a dead one regardless of total runtime (ties into #79 startup-reaper).

## Comment by NewmanTech27 (2026-07-12T12:28:27Z)

Closing per INT-1. Artifact: `db696b5` — 30-min timeout while harvesting; reaper no longer interrupts live deep harvests. Body confirms 'Fix (shipped)'. Branch → main merge tracked in #101.
