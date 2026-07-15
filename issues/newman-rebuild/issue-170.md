# #170: calculo P7: per-RPU config (giro, overrides) — graduate offers past prefeasibility

- State: OPEN
- Created: 2026-07-15T08:46:27Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/170

## Body

Offers assume giro='Otro' (0.75 pct_autoconsumo, generic load curve). Giro is not derivable from the CFDI — it's a CRM fact.

- new table `crm.rpu_config` (rpu_id PK/FK, giro, division_override, superficie_m2, pv_kwp_override, finance jsonb) — service-role only, one row optional per RPU
- `rpc_calculo_offer_work` joins it; `cfe-calculo` merges overrides into engine inputs; config change bumps the work-hash so offers recompute automatically
- assumptions block drops each key the config supplies; when giro+yield+división are all real, tier flips prefeasibility → configured
- entry path for sales: Monday sync or review UI later; psql insert is fine for v1

Gate: setting giro on one dev RPU triggers recompute on next cron tick with the curve applied.
Effort ~1d. Depends: #168/#169 land first (shared assumption plumbing). Prio: MEDIUM.
