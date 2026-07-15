# #46: Dedup Consulta ∪ MiEspacio recibos (+ cross-run) by CFDI UUID

- State: CLOSED
- Created: 2026-07-10T21:26:38Z  Closed: 2026-07-10T22:11:42Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/46

## Body

Consulta's recent window overlaps the MiEspacio history — live, 7/9 Consulta folios were also in the MiEspacio drain (combined 22 → 14 unique). Board request: don't store the duplicate; and skip invoices already harvested in a prior run. Fix: consulta.recibo_key (CFDI TimbreFiscalDigital UUID > Serie+Folio > filename folio) + dedup_recibos(paths, seen); harvest_rpu returns recibos_unique + recibo_keys (feed keys back as `seen` next run for cross-run dedup). Fixed in consulta.py/cfe_driver.py (uncommitted → this PR).

## Comment by NewmanTech27 (2026-07-10T22:11:41Z)

Resolved in main via #47 squash (e80c98f).
