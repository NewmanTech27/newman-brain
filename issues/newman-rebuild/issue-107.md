# #107: No backup/DR strategy evidenced: raw CFE harvest corpus and pipeline state exist only in one Supabase project

- State: OPEN
- Created: 2026-07-12T12:19:43Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/107

## Body

**Severity: p2**

`grep -ri "backup|pg_dump|pitr|restore"` across the repo matches only nginx `.bak` swaps in `newman-sso/apply.sh` and a comment in `old_prod_migration_map.sql`. No backup doc, script, or schedule on any branch; nothing documents the mini's `~/.newman-pipeline.env` backup either.

`raw_cfe.*` is the immutable, expensive-to-reacquire asset — each re-harvest burns a CFE register/eliminar cycle against an Imperva-guarded portal — and per #90 the migrations cannot rebuild prod either.

**Fix:** confirm PITR/backup tier on the Supabase project; add a periodic `pg_dump` of `raw_cfe` + `pipeline` to off-site storage; write the restore runbook.

## Comment by NewmanTech27 (2026-07-13T22:06:08Z)

Partial mitigation via env convergence (2026-07-14): the full collected corpus (pipeline.twilio/consulta/mi_espacio + raw_cfe.consulta/mi_espacio + intake/cfe legacy rows) is now replicated across all 3 Supabase projects, so a single-project loss no longer destroys the raw CFE corpus. Not a real backup strategy (no PITR/exports/retention policy) — keeping open.
