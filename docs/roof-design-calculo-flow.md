# Roof → Design → Calculo → Presentation flow (2026-07-15)

End-to-end chain the CRM is assembling, and how each stage's tooling reconciles
with what shipped in Tuesday (tuesday.newman.re, repo newman-architecture).

```
/roof (Tuesday, bwud)  ──►  design.roof_fit + crm.rpu_config (oioy)  ──►  cfe-calculo (hourly cron, oioy)
   manual polygons             helioscope-grade module fit                design.design / current_offer
                                                                                   │
                                                                                   ▼
                                                                  solucion-deck (presentation, Drive HTML)
```

## Stage 1 — Roof measurement (`/roof` in Tuesday)

- Candidates pre-loaded from pipeline client data (`crm_web_roof_candidates` in
  bwud: `client.rpu` ∪ `client.doc_pipeline`, CP from latest `client.bill`).
  Pendientes vs Medidos; saves stamp `reviewed_by/reviewed_at` ("Revisado
  manualmente").
- Zones stored as GeoJSON in `crm.roof_zone` (bwud); allowed (green) /
  forbidden (red).

## Stage 2 — Design (helioscope-grade fit → `design.*` in oioy)

**Tool of record**: `tools/helioscope/` in this repo (keyless mode — the only
key that exists is `GOOGLE_MAPS_API_KEY` in mario's gitignored `.env` on
newman-vps; there is **no HELIOSCOPE_API_KEY** anywhere, so the API leg of
`helioscope_client.py` stays dormant and everything runs on Esri imagery +
digitized polygons).

**Constants (single source of truth, `roof_polygon.py` / `design_pack.py`)**:
Tongwei TWMNF-66HD715 — 715 Wp, 2.384×1.303 m = 3.106 m²; PACKING **0.75** on
a digitized clear plane (0.55 on gross roof); sanity 0.75×715/3.106 = 172.6
W/m² ≈ the 0.173 kWp/m² heuristic. Fit = modules **floored per plane**.

**Gap measured** (reference traced roof RPU 016040800020, 4 planes, 501.1 m²):

| method | modules | kWp |
|---|---|---|
| per-plane module fit (helioscope) | 119 | **85.1** |
| whole-net single floor | 120 | 85.8 (+0.85%) |
| flat net×0.173 (old /roof push) | — | 86.7 (**+1.9%** over) |

**Shipped**: `apps/crm-web/lib/roof-fit.ts` ports the packing math (per allowed
plane minus forbidden overlap, turf). `/api/roof/engine-sync` now sends zones;
`public.rpc_roof_measured(...)` (oioy) writes **both**:
- `design.roof_fit` (new table: rpu_id, source manual|helioscope, polygon
  FeatureCollection, net_m2, modules_fit, kwp_fit, kwp_flat, reviewed_by,
  generated_at — append-only, latest wins), and
- `crm.rpu_config.pv_kwp_override = kwp_fit` (fallback = flat net×0.173 when
  no polygons / fit fails). Unknown RPUs / no measurement → engine defaults,
  unchanged.

## Stage 3 — Calculo (oioy `cfe-calculo` hourly cron)

Re-queue trigger: `rpc_calculo_offer_work()` folds `crm.rpu_config.updated_at`
into its bills_hash, so any roof save re-computes the RPU's offer on the next
tick (proven by queue-flip dry-runs).

**Reconciliation vs `tools/solar-charge-bess-calculator/` (mario's rev4 GEPP
dispatch engine)** — engine source: `supabase/functions/cfe-calculo/index.ts`
(newman-rebuild) + vendored `engine.js` pinned to a newman-brain commit.

Material gaps (adopt-from-solar-charge), rated:

1. **Solar-charge dispatch value of the BESS — BIG.** engine.js prices all BESS
   charging at grid base (`bnd_b`); dispatch_cs charges first from same-day PV
   excess at opportunity cost ≈ texc ≈ 0 (Op1). Worth ~$954k/yr on GEPP; lifts
   BESS TIR ~1 pp; explains why current_offer picks BESS=0 on 3 of 4 RPUs.
   Plan: port `sim_month`'s excess split as `solar_charge_split(...)`; change
   the arb line to `desc·bnd_p − (carga_base·bnd_b + carga_solar·c_oport)`;
   enforce the three-bucket no-double-count; exclude BESS-absorbed excess from
   the 5% excedente reject; gate on golden RPU 780881200029 reproducing
   bit-for-bit with solar-charge disabled, then re-pin ENGINE.commit.
2. **BESS sizing sweep 1-D/coarse — bounded.** Widen `bess_grid` and add a
   `bess_hours` axis {1,2,4} h in `engine/sizing.mjs` (~10 lines).
3. **Objective: financier IRR at fixed PPA vs deal-solved — BIG.** Port
   `solve_k_union`'s bisection as `solve_ppa(...)`; new objective
   `client_ahorro_at_target_irr` (target 14%); keep `irr` default until
   golden-validated.
4. **Superficie sweep output — bounded.** Emit `sizing_params.sweep` from the
   ranking optimizeSizing already computes + `kwp_opt_unconstrained` when the
   roof cap binds ("faltan N m²" for sales).
5. **Per-period PV credit — bounded but golden-moving.** Hourly frame from
   gap 1 gives B/I/P self-consumption splits; replace `aprov=min(usable,ki)`
   behind a flag, same golden-re-pin release as gap 1.

None of these were wired now: gaps 1/3 are engine-economics changes that must
ride mario's golden-test discipline, and all of them require redeploying the
oioy edge function (deploy token not available to Tuesday tooling). The roof
cap (this doc's stage 2) is live and engine-consumable today.

## Stage 4 — Presentation (`skills/solucion-deck/`)

Turns "rev2 calculadora" xlsx workbooks into one self-contained interactive
"Solución Energética" HTML (Newman v3 tokens, inline-SVG charts, Op1/Op2
selector, invierno/verano dispatch, 20-yr projection), uploaded back to the
client Drive folder.

**What the deck needs vs what design/calculo already provide** (verified
against `design.current_offer.engine_output`):

| deck input | source today | status |
|---|---|---|
| 12-mo consumo B/I/P, demanda, gasto | `crm.bill` (oioy) | available |
| PV kWp, BESS kW/kWh | `current_offer.pv_kwp/bess_kwh`, `engine_output.bess_kw` | available |
| ahorro año-1 $ / %, TIR/VPN/payback/capex | `ahorro_mxn/ahorro_pct/tir/payback_years`, `engine_output.finance.*` | available |
| modelo mensual | `engine_output.monthly[]` | available |
| régimen (Op1 vs Op2 selector) | `skills/solucion-deck/scripts/` dual-run (2× calc_core, single-option fallback <700 kWp) | built (#3) |
| PPA price/pago/participación | pricer port (`ppa_pricer` / book k-solve), target-TIR parameterized — 14 vs 19 OPEN | built (#3) |
| proyección 20 años | `scripts/` build-time (anchors + Supuestos escalations; golden vs rev4 deck) | built (#3) |
| despacho 24 h inv/ver | `scripts/` synthetic typical-day, footnoted "ilustrativo"; punta basis billing/calendar OPEN | built (#3) |
| superficie disponible | `crm.rpu_config.superficie_m2` — now populated by /roof saves | available (new) |

**"Generar propuesta" from Tuesday — adoption plan (bounded, ~2–4 d, not
implemented)**: button on the deal/RPU → endpoint (mini FastAPI or a Tuesday
route) → query oioy (client, bills 12 m, latest offer, roof_fit) → MODEL JSON →
inject into `assets/template_gepp_v2.html` → node+DOM-stub QA → upload to the
client Drive folder → link back. The four missing pieces (PPA-pricing port,
20-yr projection script, single-option fallback, synthetic despacho footnoted
as ilustrativo) shipped in `skills/solucion-deck/scripts/` (issue #3;
`build_deck_inputs.py` = offer JSON → MODEL fragment, `golden_test.py` = gates
vs the delivered GEPP rev3/rev4 books). Target TIR (14 vs 19) and punta-day
basis (billing vs calendar) stay parameterized — both required CLI flags, both
variants pinned in `scripts/baselines.json` for the decision-maker.

## Evidence / deploys

- oioy DDL (no branches → single verified transaction + dry-run + revert):
  `design.roof_fit` created; `rpc_roof_measured` extended (old 4-arg call
  shape still works → flat fallback; 8-arg writes fit). Dry-run: override
  85.085 kWp from 119-module fit, work queue 0→1→0 after revert.
- bwud (dev→staging→prod): roof tool migrations `crm_roof_tool*` applied via
  MCP + branch rebases.
- Tuesday PR #23 (helioscope fit), earlier #16 (engine feed), #21 (geocode +
  review dedupe); deploy workflow green each time.
