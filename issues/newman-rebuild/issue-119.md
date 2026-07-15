# #119: Harvest: back-to-back sequential drives trip CFE WAF (deep-history drain rejected, 0 recibos)

- State: OPEN
- Created: 2026-07-12T21:23:51Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/119

## Body

## Observed (dev harvest of 66 accounts, sequential, no pacing)
Running harvests back-to-back (6 in ~10 min) got the drain WAF-rejected on **every** account: `fetchDrain 1 file, 127 rejected`. Result: 0 recibos harvested (`raw_cfe.mi_espacio` stayed flat), mi_espacio rows cycled failed→pending→re-harvest→fail. The harvest *mechanism* is fine — login / AgregarServicio / eliminar / safe_cleanup all work, no stranded services — but CFE's Imperva WAF throttles the drain replay under the aggressive cadence.

## Why prod is fine
Prod drives one harvest per ~5 min via pg_cron (claim-one-per-tick), so it stays under the WAF rate limit and succeeds (11 harvested there). The failure is purely the **unpaced back-to-back rate**, likely compounded by the deep Yazaki/ARNECOM histories (many recibos per drain) on a shared IP + shared MiEspacio account.

## Fix direction
- Any bulk/backfill harvest must **pace** like pg_cron: a delay (e.g. 3-5 min) between accounts, or drive it *through* the pg_cron cadence rather than a tight loop.
- Consider a WAF-backoff: on `NN rejected`, cool down N minutes before the next account (module-level exponential backoff already exists in fetchDrain per-chunk; needs a per-*account* cooldown too).
- Deep accounts (100+ recibos) may need smaller drain chunks + longer inter-chunk gaps.

## Note
Not a regression in the fan-out / dedup / invoice-filter work — those are proven. This is an operational pacing constraint for bulk harvest.
