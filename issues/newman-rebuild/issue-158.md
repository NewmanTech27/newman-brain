# #158: calculo P2: migration — extend crm.bill + new calculo schema (oferta per RPU)

- State: OPEN
- Created: 2026-07-15T06:08:52Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/158

## Body

`crm.bill` today: kWh/kW bands + amount_mxn only — engine needs more. Extend (additive): days, tarifa, division_code, division, demanda_contratada, kvarh, fp, 9 MEM importes, bonif_fp, cargo_fp_penalty, subtotal_recibo, facturacion_recibo, valid, valid_diff, raw_mi_espacio_id FK, UNIQUE(rpu_id, period).

New schema `calculo` (NOT PostgREST-exposed, service-role only; decision: NOT `client.*` — collides with crm.client semantics and mario's abandoned old-world client schema on bwud):
- `calculo.rpu_config` — per-RPU non-bill inputs (giro, division override, superficie_m2, pv/finance overrides jsonb); optional row, defaults apply.
- `calculo.oferta` — ONE current offer per RPU: rpu_id UNIQUE, engine_version, meses, anualizado, inputs jsonb, bills_hash, pv_kwp, bess_kw, bess_kwh, regimen, ahorro_{pv,bess,hibrido,pct}, capex, tir, payback, van, monthly/finance/alerts jsonb, status (ok|fuera_de_alcance|datos_insuficientes|caveat_bcs).
- `calculo.oferta_hist` — append-only on every recompute.

**Gate:** migration green through GH Actions on develop; `calculo` absent from exposed schemas; RLS asserted.

## Comment by NewmanTech27 (2026-07-15T06:19:41Z)

Decision revised during implementation: NO new `calculo` schema — `design.design` already is the offer table (append-only via rpc_insert_design → history free; current offer = new `design.current_offer` view). PR incoming implements crm.bill extension + parser RPCs instead. `client.calculo` rejected as originally analyzed.
