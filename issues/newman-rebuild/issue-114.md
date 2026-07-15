# #114: pipeline.consulta: enforce unique RPU (dedup + unique index + conflict-safe advance RPCs)

- State: CLOSED
- Created: 2026-07-12T17:44:28Z  Closed: 2026-07-13T22:05:48Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/114

## Body

## Ask
`pipeline.consulta.rpu` should be **unique** — one consulta (one account lookup) per RPU. Today the same RPU can get many rows.

## Root cause (observed on dev)
`rpc_advance_twilio` (single-invoice path) does a bare `insert into pipeline.consulta` with **no dedup**. When a twilio row is re-claimed (reaper requeue, transient error, or a re-run), each pass inserts another consulta row for the same RPU. On a dev re-extract this produced 324 rows for 88 distinct RPUs (×4-×8 dupes). Also affects cross-upload dupes (same invoice sent twice) — see #92.

## Fix
1. Dedup existing: keep the lowest `id` per `rpu`, delete the rest (respect the `mi_espacio.consulta_id` FK — repoint or delete children first).
2. Add `unique index on pipeline.consulta(rpu)`.
3. Make the inserts conflict-safe: `rpc_advance_twilio` and `rpc_advance_twilio_multi` → `insert … on conflict (rpu) do nothing`, and resolve `twilio.consulta_id` to the existing row on conflict (so the parent still links).

## Note
The multi-invoice fan-out (#88) creates one row per **distinct** RPU, so it's compatible — the unique index just also blocks the cross-upload / re-claim dupes.
Closes the dedup half of #92.

## Comment by NewmanTech27 (2026-07-13T22:05:47Z)

consulta_rpu_uidx + one-time dedup applied to all 3 envs (staging+prod 33→13, develop seeded post-dedup; prod losing rows preserved in pipeline._consulta_dedup_backup_20260713; 0 mi_espacio children pointed at losers, so no FK repoint needed). Conflict-safe RPC semantics continue in #134.
