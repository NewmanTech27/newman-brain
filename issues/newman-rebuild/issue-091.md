# #91: Committed rpc_advance_twilio is stale vs live: single-invoice path does not seed razon_social into pipeline.consulta

- State: OPEN
- Created: 2026-07-12T10:12:37Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/91

## Body

## Problem

The LIVE `rpc_advance_twilio` on prod seeds the OCR `receptor_name` into `pipeline.consulta.razon_social` (hot-patched via direct psql). The committed file does not:

`supabase/migrations/20260711220000_pipeline_advance_rpcs.sql:154-156`
```sql
    -- barcode good → create the next stage row FIRST so we can link it back.
    insert into pipeline.consulta (status, twilio_id, rpu)
    values ('pending', p_id, p_rpu)
    returning id into v_consulta_id;
```

Meanwhile the NEW multi-invoice RPC in `20260712100000_pipeline_twilio_multi_invoice.sql:66-67` DOES seed it:
```sql
        insert into pipeline.consulta (status, twilio_id, rpu, razon_social)
        values ('pending', p_id, v_rpu, v_name)
```

## Consequence

- Any environment built from the repo (dev/staging branches, CI preview branches, disaster recovery) gets a consulta stage whose single-invoice rows have NULL `razon_social` — but the CFE Consulta drive is **name-gated** (`consulta_latest` needs a name candidate), so behavior diverges from prod exactly where it matters.
- Single-invoice and multi-invoice paths are inconsistent within the repo itself.

## Fix

Commit the live definition as a new timestamped migration (e.g. `create or replace function pipeline.rpc_advance_twilio` with the `razon_social` seed), matching the live signature exactly. Do not edit the already-applied `20260711220000` file. Sub-case of the ledger-drift repair (#90) but independently actionable and the highest-risk single divergence.
