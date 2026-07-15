# Tuesday CRM backup — 2026-07-15

Full backup of the `crm` schema (Tuesday CRM) taken BEFORE the 2026-07-15 reset (truncate of all CRM data tables).
Source: Supabase project bwudgrwfwjdbvqhgbwty (prod) and its persistent branches dev/staging.

Per environment directory:
- `crm-schema.sql` — schema-only DDL (pg_dump 17)
- `crm-full.dump` — pg_dump custom-format dump (schema + data); restore with `pg_restore --schema=crm`
- `csv/<table>.csv` — per-table CSV with header (`sanctions_entry.csv` is gzipped: >100MB GitHub limit)
- `rowcounts.csv` — table,row_count (CSV line counts, exact)

Environments:
- `prod-bwudgrwfwjdbvqhgbwty/` — prod (bwudgrwfwjdbvqhgbwty, main branch)
- `staging-ytknnpxeyikttzyboysz/` — staging (Supabase branch ytknnpxeyikttzyboysz)
- `dev-crmrhsvsowjdnjmjbley/` — dev (Supabase branch crmrhsvsowjdnjmjbley)

## Row counts (non-empty tables)

| table | prod | staging | dev |
|---|---|---|---|
| ai_draft | 6 | 6 | 6 |
| aml_control | 8 | 8 | 8 |
| aml_rule | 6 | 6 | 6 |
| app_user | 13 | 13 | 13 |
| automation_event | 11 | 11 | 11 |
| bulk_action_log | 4 | 4 | 4 |
| capital_config | 1 | 1 | 1 |
| collateral_haircut | 6 | 6 | 6 |
| comms_identity | 4552 | 4552 | 4552 |
| company | 12 | 12 | 12 |
| concentration_cap | 6 | 6 | 6 |
| concentration_limit | 4 | 4 | 4 |
| contact | 2585 | 2585 | 2585 |
| contact_enrich | 2583 | 2583 | 2583 |
| counterparty | 17 | 15 | 15 |
| coverage_covenant | 4 | 4 | 4 |
| dd_operation | 1 | 1 | 1 |
| deal | 194 | 194 | 194 |
| deal_comment | 12 | 12 | 12 |
| deal_event | 16 | 16 | 16 |
| deal_financials | 3 | 3 | 3 |
| deal_line_item | 214 | 214 | 214 |
| deal_rpu | 6 | 6 | 6 |
| delegated_authority | 3 | 3 | 3 |
| ebr_factor | 7 | 7 | 7 |
| efos_69b | 12146 | 12146 | 12146 |
| huddle_run | 10 | 8 | 8 |
| limit_breach | 20 | 12 | 12 |
| macro_scenario | 3 | 3 | 3 |
| macro_scenario_set | 1 | 1 | 1 |
| notification | 109 | 109 | 109 |
| pd_scorecard_factor | 6 | 6 | 6 |
| sanctions_entry | 281606 | 281606 | 281606 |
| screening_list_version | 3 | 3 | 3 |
| stage_probability | 8 | 8 | 8 |
| todo | 48 | 35 | 35 |
| training_completion | 6 | 6 | 6 |
| training_course | 2 | 2 | 2 |
| uma_config | 1 | 1 | 1 |

147 tables per environment; 108 empty in all three.
Total rows: prod=304243, staging=304218, dev=304218
