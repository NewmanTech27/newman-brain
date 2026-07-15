# Solar + BESS Sizing (CFE Brain engine)

**Summary**: How Newman sizes PV+BESS systems — the deterministic CFE Brain max-NPV optimizer, its doctrine (PV⊥punta, BESS = demand/punta lever), the PV-surplus charging bug and fix, golden tests, and the geographic yield data.
**Tags**: #newman #bess #solar #cfe-brain #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Engine doctrine
- Deterministic max-NPV sweep over `(kWp, BESS_kW, BESS_kWh)`: `E_pv = kWp·Y(m)·PR` with PR = 0.80; **PV produces ≈0 at punta, so BESS is the sole punta lever**; PV surplus charges the BESS before grid; exempt-regime cap kWp_DC ≤ 839.41; inverter ≤ demanda contratada. Never re-derive the math — drive the golden-tested engine (`optimize_sizing.py`, `ppa_pricer`, `calc_core`).
- Invocation pattern: `python3 optimize_sizing.py <client_dir> --area 626 --division Sureste --giro Otro` over bills.json + inputs.json.
- Roof-area cap comes from the Google Solar API on the CFDI address (the one input the engine otherwise lacks).

### Tariff mechanics (engine.js / cfe-ppa-bess edge fn)
- **Capacidad** charge basis = `min(kW_punta, umbral)` (falls back to umbral when no kw_punta), umbral = `kWh / (days × 24 × FC)` with **FC = 0.57** for GDMTH capacidad but **0.55** for the GDMTO umbral; **distribución** billed on `max(kW_base, kW_inter, kW_punta)` (GDMTO: `min(Dmax, umbral)`). Engine never recomputes baseline capacidad — takes the real peso amount and derives the rate ([[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]).
- **GDMTO kills BESS value**: no punta → no arbitrage, capacidad = pure function of kWh (grid-charging *raises* it); only lever is distribución (~4:1 smaller), paying only when load factor > 0.55. A battery is barely worth it under GDMTO vs GDMTH ([[2026-07-11-gdmto-vs-gdmth-bess-value]]).
- **BCS gotcha (unfixed in calc_core)**: the motor is SIN-calibrated — credits PV only vs *intermedio*; in BCS winter (no punta, daytime = Base) it understates savings up to −53% and DIV/0s the capacidad formula when kw_punta=0 (the FibraHotel Médano 249-broken-cell bug). Patched only in client workbooks so far ([[2026-07-13-pueblo-bonito-desaladora]], [[2026-07-12-fibrahotel-proposals]]).
- **Solar-charge dispatch** (`dispatch_cs.py`, GEPP rev4): BESS charges from midday PV surplus first, grid-base second; real bonus +$954k/yr on the GEPP portfolio — only 18–31% of the charge is solar-coverable at design kWp, far below analytical ceilings ([[2026-07-14-gepp-solar-charge-bess-dispatch]]).

### Helioscope roof pipeline (`newman-brain/tools/helioscope/`)
- Geocode → roof polygon → module fit: Google Solar/Places/Geocoding key on GCP project `cfe-brain-geo`; `roof_polygon.py` --fetch/--layers/--export with a manual Claude visual-trace step; landmark-beats-brand scoring. 57-site run: 36 HIGH confidence, Solar API covered 37/57 = 12.3 MWp potential; no coverage in Tuxtla/Oaxaca (404, Esri z19 fallback).
- Module standard **Tongwei TWMNF-66HD715** (715 Wp, 3.106 m², bifacial): packing 0.75×715/3.106 = **0.173 kWp/m²**, independently confirming the CFE Brain 0.17 kWp/m² heuristic. `examples/HOUSE_STYLE.md` distills 30 reference HelioScope designs (DC:AC, tilt, racking, setbacks) ([[2026-07-09-helioscope-roof-sizing-pipeline]]).

### sizing.py divergence and fix (VPS flock, Jul 09–10)
- Clean-room `sizing.py` had lost the umbral, inverted PV→BESS charging, and its golden test never ran the golden RPU — net effect **overstates client savings** (capacidad shave ~2× over; FP claw-back omitted). Only `vault/tools/calc_core.py` is authoritative — finance.ts and sizing.py both silently overstate; **wrap, never rewrite** ([[2026-07-09-sizing-materiality]], [[2026-07-09-cto-verification-freeze]]).
- Fix: sizing.optimize now delegates to optimize_sizing.sweep/calc_core via a golden_engine bridge; the test pinning the inverted behavior was removed; golden proof re-run 18/18 exit 0 on RPU 780881200029 with peso anchors $30,157,371 / $7,083,252 / 23.5% ([[2026-07-10-flock-overnight-golden-proof]]).

### Bug fixed (2026-07-07)
Both dispatch copies (`cfe_savings/engine.py` golden-tested, and `calc_core.py` under optimize_sizing) left **PV-surplus BESS charging uncredited** — battery always charged from grid. Both engines aligned; golden 18/18 PASS after the fix (fixture: Grupo Posadas hotel, RPU 780881200029, recovered from Drive).

### Golden tests / CI
- newman-rebuild golden CI (PR #16) drives the deployed `newman-brain/.../cfe-ppa-bess/engine.js` via `compute()` and asserts peso-exact: baseline **$30,157,371**, ahorro **$7,083,252**, **23.5%** (tol <1 peso); proven RED on one-peso drift.
- XML label gotcha caught by CTO review: `CONSUMO1F=104467` was punta but extract.py labeled it base.

### Reference data
- CFE divisions: the 16 Gerencias Divisionales come authoritatively from the Estatuto Orgánico de CFE Distribución, DOF 2018-01-04 (nota 5510072).
- Geographic yield: `codigo_postal.csv` (157k rows) + `Solar_index_geografico.csv` in `Dataroom_Newman/CFE brain/CFE Brain/raw/assets/` — yield resolves geographically, not flat PVGIS.
- BESS procurement context: China ~90% of LFP cells; CATL (Tener/EnerOne/EnerC), BYD (Blade/MC Cube — FinDreams contact li.kexin12@fdbatt.com), EVE (314Ah), Hithium; Anáhuac RFQ = 1.25 MW / 2.5 MWh, 1 cycle/day, CIF Progreso.

## Related Notes
- [[2026-07-04-solar-bess-sizing-agent]]
- [[2026-07-07-whatsapp-intake-cutover]]
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-06-24-byd-bess-rfq-anahuac]]
- [[2026-06-24-bess-intersolar-exhibitor-scraper]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-15-mario-engine-client-calculo]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[2026-07-09-helioscope-roof-sizing-pipeline]]
- [[2026-07-11-gdmto-vs-gdmth-bess-value]]
- [[2026-07-09-sizing-materiality]]
- [[2026-07-10-flock-overnight-golden-proof]]
- [[2026-07-14-gepp-solar-charge-bess-dispatch]]
- [[2026-07-13-pueblo-bonito-desaladora]]
