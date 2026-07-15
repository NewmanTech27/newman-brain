# #82: harvest has no single-flight guard — concurrent harvests mutate the shared CFE account

- State: CLOSED
- Created: 2026-07-11T18:50:42Z  Closed: 2026-07-12T12:28:26Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/82

## Body

## Problem (found in the drain loop)
Two harvests ran concurrently — id 14 (manual trigger) + id 15 (the :03 cron tick claimed a second pending row). `rpc_claim_mi_espacio` claims one *pending* row per call but does NOT check whether another harvest is already in-flight, so multiple invokes (manual + cron, or any future fan-out) start concurrent harvests.

Harvest register/eliminars on the ONE shared CFE account, so concurrency risks the grid-context leak + cross-eliminar. The F1 (grid row-1 RPU verify) + F2 (fresh-tab eliminar) gates prevent *data corruption* (a mis-served grid → RPU_MISMATCH → drains nothing), but it's wasted work and racy.

## Fix
Single-flight the harvest claim: `rpc_claim_mi_espacio` only claims a pending row when NO row is currently 'harvesting'. The 15-min reaper releases a dead 'harvesting' row so a crashed harvest can't wedge the queue forever. (Consulta stays parallel — it's read-only.)

## Comment by NewmanTech27 (2026-07-12T12:28:25Z)

Closing per INT-1. Artifact: `75e6070` — single-flight harvest claim; no concurrent mutation of the shared CFE account. Branch → main merge tracked in #101.
