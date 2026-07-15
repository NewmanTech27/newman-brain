# #174: calculo P10: GDMTO/PDBT flat-tariff support — 8 of 12 prod RPUs have no offer

- State: OPEN
- Created: 2026-07-15T08:47:11Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/174

## Body

Engine is GDMTH-only. Prod raw data: 7 RPUs on tarifa 1C + 1 on 03 (domestic/agro) → excluded by design, plus any future GDMTO clients. CFE Brain has `tools/tarifa_flat.py` (GDMTO/PDBT flat model, prefeasibility, FC=0.55 umbral) — never ported to JS.

- port tarifa_flat to the engine repo (newman-brain) first — same authority rules (golden anchor from a real GDMTO bill, parity harness)
- then cfe-calculo routes by tariff: GDMTH→compute, GDMTO/PDBT→flat model, else fuera_de_alcance
- NOTE: 1C is a DOMESTIC agricultural tariff — solar economics differ (subsidized rates); confirm with sales whether these RPUs are even prospects before porting

Effort ~2-3d incl. golden. Prio: LOW until a real GDMTO prospect needs an auto-offer. Blocked on: prospect validation.
