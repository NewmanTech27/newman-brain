# #134: rpc_advance_twilio: unify conflict-safe insert (20260712110000) with dedup guard (20260712140100)

- State: OPEN
- Created: 2026-07-13T22:05:22Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/134

## Body

The two migrations each CREATE OR REPLACE rpc_advance_twilio with complementary behavior:

- 20260712110000_consulta_unique_rpu: `on conflict (rpu) do nothing` insert (conflict-safe), NO duplicate/ALREADY_ONBOARDED guard
- 20260712140100_pipeline_dedup_guard: duplicate/ALREADY_ONBOARDED intake guard, bare INSERT (no on-conflict)

Version order means 140100 wins everywhere (all 3 envs converged on it, 2026-07-13). Under consulta_rpu_uidx a guard-missed race now errors (RPC_FAIL, retried) instead of do-nothing. Low frequency, but the correct final RPC = guard + on-conflict insert. Ship as a new forward migration through the develop → staging → main workflow.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
