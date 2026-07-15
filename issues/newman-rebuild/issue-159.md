# #159: calculo P3: cfe-calculo edge function + pg_cron (raw XML → crm.bill → oferta per RPU)

- State: OPEN
- Created: 2026-07-15T06:09:19Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/159

## Body

New edge function `cfe-calculo`, two stages in one invocation:
1. **parse**: raw_cfe.mi_espacio (tipo I, unparsed) → parse_cfdi (#157) → upsert crm.bill (+auto-create crm.rpu); footing check; failures flagged per-row, never block batch.
2. **compute**: RPUs with new/changed bills (bills_hash) → latest ≤12 GDMTH bills → size_bess_verano → PV sizing via existing `engine/sizing.mjs` optimizeSizing doctrine (financier IRR objective, NPV tie-break) → compute() → upsert calculo.oferta + append oferta_hist.

**Engine sourcing:** NO vendoring — materialize engine.js at deploy from pinned commit `ci/golden/ENGINE.commit`, sha256-verify vs `ci/golden/ENGINE.sha256` (same pattern as golden CI / load_engine.mjs).

**Cron:** `cfe-calculo-offers`, hourly `7 * * * *`, via pipeline.invoke(functions_base_url). MUST respect #142: active only where env=prod (config-gated), inactive on develop/staging clones like sibling jobs.

**Guards:** kw_punta=0 winter DIV/0; BCS → status=caveat_bcs (engine understates savings up to −53%, SIN credit logic); non-GDMTH → fuera_de_alcance; <12 months → engine annualizes, store meses/anualizado.

**Gate:** manual invoke on develop (seeded w/ 323 prod rows): 194→crm.bill, 12 offers; 1 offer peso-exact vs local Python calc_core run; second invoke = no-op (idempotent).
