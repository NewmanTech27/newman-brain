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
