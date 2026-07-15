# PV+BESS sizing agent: CFE Brain optimizer, divisions catalog, BESS-charging bug

**Summary**: Built the newman-solar-bess sizing capability — first live CFE Brain optimize_sizing run, authoritative CFE division catalog from the DOF, geographic solar-yield lookup, and diagnosis of the uncredited PV-surplus BESS charging bug.
**Tags**: #newman #bess #solar #cfe #agents #cfe-brain
**Created**: 2026-07-04
**Source**: macbook session 8987e572-e69b-4412-8142-d422f0bcad4b.jsonl (Downloads dir), user jesus

---

## Content
- Goal: an agent that takes a client's 12-month bill consumption + CFE Brain on Drive and finds the optimal PV+BESS strategy, with roof-area (m²) estimated from the CFDI address; evaluated open-source alternatives to Google Solar API (incl. detecting already-installed panels).
- First live optimizer run: RPU 671071116338, Alimentos y Franquicias de Chiapas, GDMTH, División Sureste (DK), Tuxtla Gutiérrez CP 29000 — `python3 optimize_sizing.py <client_dir> --area 626 --division Sureste --giro Otro` over bills.json + inputs.json.
- Division question resolved authoritatively: Estatuto Orgánico de CFE Distribución, DOF 2018-01-04 (nota 5510072, fetched via sidof.segob.gob.mx from the mini's Mexican IP) — enumerates the 16 Gerencias Divisionales de Distribución.
- Yield fix: CFE Brain sync now pulls the engine's real reference CSVs from Drive (`Dataroom_Newman/CFE brain/CFE Brain/raw/assets/`): `codigo_postal.csv` (157k rows) + `Solar_index_geografico.csv`; yield resolves geographically instead of flat PVGIS fallback.
- BESS bug diagnosed: two identical dispatch copies (`cfe_savings/engine.py` golden-tested, and `calc_core.py` driven by optimize_sizing) both left PV-surplus charging uncredited — battery always charged from grid. Confirmed by synthetic run.
- Planned the automation of this session's work into cascading Newman agents chained off the invoice agents (the "safe path" chosen).
- Session tail: es-MX pitch (PR #5, `feat/offer-template`) audited 10 pages defect-free — KFC/Pizza Hut offers + portfolio aggregate in `00_Leads`, brand SVG icons, stock library in Drive, secrets in Vault.

## Related Notes
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-07-whatsapp-intake-cutover]]
