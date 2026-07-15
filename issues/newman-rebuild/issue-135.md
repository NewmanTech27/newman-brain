# #135: Consulta status regression: adeudo-refresh BridgeTimeout clobbers 'derived' rows

- State: OPEN
- Created: 2026-07-14T12:34:36Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/135

## Body

Observed on develop DB: 11/13 pipeline.consulta rows sit at status='failed' with
`BridgeTimeout: bridge op=consulta silent past deadline`, yet every one of them has
raw_consulta_id set, adeudo populated, and a completed downstream mi_espacio harvest.
The failure came from a later re-run (refresh path), and rpc_fail_stage unconditionally
flips status to 'failed', so pipeline.flow reports blocked:consulta for fully-harvested RPUs.

Fix: in rpc_fail_stage, a retryable consulta failure on a row that already derived
(raw_consulta_id IS NOT NULL) must revert to 'derived' (stamp error_class/last_error only),
not 'failed'. Plus a one-time data repair for the 11 stuck rows.
