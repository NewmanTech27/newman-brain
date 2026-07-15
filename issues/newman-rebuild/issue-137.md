# #137: Leaked MiEspacio services: auto-requeue eliminar in later rounds

- State: OPEN
- Created: 2026-07-14T12:34:38Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/137

## Body

Policy update from operator: a servicio left in the CFE account is acceptable short-term,
as long as later rounds delete it. Today a leaked row (e.g. RPU 780020900569, leaked=true,
status='failed' after eliminar selector timeout) is terminal — rpc_claim_mi_espacio only
claims 'pending', so nothing ever retries the eliminar.

Fix: pipeline.requeue_leaked_eliminar() flips failed+leaked rows back to 'pending' on a
daily cron so the harvest heartbeat retries add→drain→eliminar (drain is dedup-safe via
sha256 + (rpu, period)). Charter §7 wording can stay — leak is still an incident, but a
self-healing one.
