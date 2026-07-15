# #171: calculo P8: roof-cap the PV sweep via the Helioscope route (address → kWp cap)

- State: OPEN
- Created: 2026-07-15T08:46:28Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/171

## Body

The sweep's kWp grid is capped only by annual energy — no physical roof constraint. newman-brain `tools/helioscope/` already does CFE address → verified roof polygons → usable-roof kWp (57-site packs done, HOUSE_STYLE v1).

- CFDI carries the service address; store on `crm.rpu.address` at parse time
- batch job (mini or manual per client) runs the helioscope route → writes `crm.rpu_config.superficie_m2` / `pv_kwp_override` (#170's table)
- sweep cap = min(energy cap, roof cap); offer records which bound
- NOT in the hourly cron (Google/Esri API cost + latency) — on-demand per prospect

Gate: one dev RPU with a real roof pack caps its offer correctly.
Effort ~1-2d wiring (route itself exists). Depends: #170. Prio: MEDIUM — required before offers go client-facing.
