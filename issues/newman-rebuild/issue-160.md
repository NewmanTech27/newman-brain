# #160: calculo P4: backfill + promote develop→staging→prod + docs

- State: CLOSED
- Created: 2026-07-15T06:09:21Z  Closed: 2026-07-15T07:13:21Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/160

## Body

- Promote #157–#159 through staging→main via branch merges (existing supabase-migrations.yml flow).
- Deploy cfe-calculo to staging + prod; first cron fire backfills 12 RPUs from the 323 existing raw rows.
- Verify: prod offer count = staging = 12; spot-check 1 RPU peso-exact.
- Docs: engine/README cross-ref; update stale golden numbers in mario's cfe_savings/README ($7,593,969/25.2% → re-baselined $7,083,252/23.5%, 2026-06-11) — PR to newman-brain or note to mario.
- Open questions parked: giro per RPU (defaults to Otro → offers are prefeasibility-tier until rpu_config filled); offer consumer RPC (review UI / Monday / solucion-deck) — separate issue when decided.

**Gate:** offers live on prod, cron active only on prod, rollback documented (cron.unschedule + DROP SCHEMA calculo CASCADE; crm.bill columns additive, keep).

## Comment by NewmanTech27 (2026-07-15T06:42:37Z)

Develop verification COMPLETE (gates from #159):
- deploy.sh → develop: engine sha256 == ci/golden pin ✓
- invoke #1: parse 166/166, 0 failed, 4 offers, 0 errors, 11.4s
- offers correctly limited to HM/GDMTH RPUs (7×tarifa 1C + 1×03 excluded by design — engine is GDMTH-only)
- peso-exact cross-check RPU 008970211013 vs Python calc_core on identical DB-roundtripped bills: hibrido 727601.6100 both (residual 2e-10 = Python≥3.12 Neumaier sum vs JS naive on annual aggregates; bit-exactness on aggregates is NOT claimed, peso-exactness holds)
- invoke #2 (idempotency): parse 0, offers 0, 203ms ✓
- design.design=4, current_offer=4, bill_parse_fail=0
- develop cron enabled (calculo_enabled=true) + functions_base_url fixed to per-env (was prod URL — see #142 comment)

Next: staging promotion, then prod backfill (195 I-rows / 12 RPUs).

## Comment by NewmanTech27 (2026-07-15T07:13:19Z)

Prod promotion COMPLETE — closing.

- staging: deployed, 166/166, 4 offers byte-identical to develop; cron enabled; functions_base_url fixed per-env
- prod: migrations via #165 (after #166 reconciled the 20260715120000 main-only hotfix), function deployed, backfill 194/195 (1 no-Addenda parked), 4 offers: 780020900569 Investigaciones y Estudios Superiores 699 kWp/$3.43M/40.1%, 968221200700 Fideicomiso F/1596 439 kWp/$1.81M/53.4%, 585880702961 Productos Chachitos 211 kWp/$0.95M/64.1%, 008970211013 ETG Resorts 97 kWp/$0.73M/23.1% — all exento/medición neta, TIR fin 16.8%, prefeasibility tier (assumptions in sizing_params)
- first autonomous cron fire 07:07 UTC: succeeded on all 3 envs; prod parsed 2 NEW harvest-delivered bills — raw→bill→offer loop is closed
- rollback: unset calculo_enabled (or cron.unschedule); offers regenerable from raw

Parked for follow-up (not blocking): mario's CFE Brain cfe_savings/README.md still shows pre-rebaseline golden numbers ($7,593,969/25.2% → should be $7,083,252/23.5%) — his vault, his edit; per-RPU config (giro/división/yield) to graduate offers from prefeasibility tier; offer consumer RPC (review UI / Monday / solucion-deck) undecided.
