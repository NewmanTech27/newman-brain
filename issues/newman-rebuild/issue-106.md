# #106: pipeline.* and raw_cfe.* tables ship with zero RLS, breaking the 'RLS from day one' charter rule every earlier schema follows

- State: OPEN
- Created: 2026-07-12T12:19:42Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/106

## Body

**Severity: p2**

`grep "row level security" supabase/migrations/*.sql` hits only `20260710120000`, `20260710130000`, `20260710170000`. `20260711210000_pipeline_schema.sql` — all `pipeline.*` + `raw_cfe.*` tables, including harvested CFDI XML with customer PII — contains none. CHARTER.md:85-86: "P1 — clean schema … RLS from day one."

Holds today only because the schemas aren't PostgREST-exposed; silently breaks the moment anyone adds the schema to the exposed list or grants usage to `authenticated`.

**Fix:** follow-up migration adding `ENABLE` + `FORCE ROW LEVEL SECURITY` to all pipeline/raw_cfe tables, matching the house convention.
