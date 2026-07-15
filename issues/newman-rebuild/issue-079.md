# #79: pipeline: endpoint restart/crash orphans in-flight rows as 'fetching'/'harvesting' zombies (no startup reaper)

- State: OPEN
- Created: 2026-07-11T18:07:38Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/79

## Body

## Problem
The mini executor runs consulta/harvest drives in background threads. When the endpoint restarts (redeploy, crash, launchd relaunch), those threads die but their rows stay `fetching`/`harvesting` — the drive never advances them. The stale-claim reaper only frees them after its 15-min timeout, so a row can sit stuck ~15 min per restart.

Observed (drain loop): consulta id 6 (008221101813) stuck `fetching` 561s after a redeploy, no live drive/bridge proc. Requeued manually.

## Fix directions
- **Startup reaper** (the #50 idea, generalized to all stages): on endpoint boot, release any `fetching`/`harvesting` row claimed by this host (`claimed_by='cron'`) back to the entry state — nothing is draining at boot, so any in-progress row is orphaned. For harvest, run safe_cleanup for its RPU first (a mid-drive restart may have left a registered service).
- Or shorten the reaper stale timeout (15 min → ~5 min) for `fetching` (consulta is ~74s; a >5-min fetch is dead).
- Heartbeats: the drive threads could update `heartbeat_at` so the reaper distinguishes a live-slow drive from a dead one.

## Severity
Low in steady state (rare restarts) but a production crash mid-harvest could orphan + briefly strand a service until the next harvest's safe_cleanup. Belongs with the #50 hardening.
