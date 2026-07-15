# #169: calculo P6: DIVISION code → división map (SIN/BC/BCS) + BCS caveat flag

- State: OPEN
- Created: 2026-07-15T08:46:03Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/169

## Body

Offers hardcode división='SIN'. Every CFDI carries `DIVISION` (dev codes seen: DW, DL, DN, DC, DA — all likely SIN, but unverified). Engine needs SIN/BC/BCS (punta windows differ; BCS is mis-modeled by SIN credit logic — understates savings up to −53% per CFE Brain).

- build the CFE division-code → división map (verify vs CP state; document source)
- parser/RPC already store `division_code`; fill `crm.bill.division` from the map
- `cfe-calculo` uses bill división; BC/BCS RPUs get offer status `caveat` + assumption flag instead of silently wrong numbers
- unknown code → SIN + flag (never block)

Gate: dev's 5 codes mapped + asserted; a synthetic BCS bill produces flagged offer.
Effort ~0.5d. Prio: HIGH (correctness guard — cheap insurance before non-SIN clients land).
