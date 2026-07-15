# #168: calculo P5: real PV yield from bill CODIGO_POSTAL (kill the flat-1800 assumption)

- State: OPEN
- Created: 2026-07-15T08:46:02Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/168

## Body

Every raw CFDI carries `CODIGO_POSTAL` (166/166 on develop) but offers use a flat 1800 kWh/kWp/yr yield.

Wire mario's prefeasibility chain (CFE Brain `tools/solar_lookup.py` + `raw/assets` CSVs: CP → codigo_postal.csv (municipio+estado) → Solar_index_geografico.csv (kWh/kWp)):
- store `cp` on `crm.bill` (parser already extracts it; column missing)
- ship the two CSVs as data (small, public-data derived) or a generated lookup module
- `cfe-calculo` builds `yield_monthly` from the lookup; falls back to flat 1800 + assumption flag when CP unmapped
- offer `sizing_params.assumptions.yield` reflects source (indexed vs flat)

Gate: offers recompute on develop with indexed yield; RPU with known municipio matches mario's engine yield for the same CP; assumption tier upgraded only where lookup hit.
Effort ~0.5d. Depends: none. Prio: HIGH (biggest accuracy lever, zero new inputs).
