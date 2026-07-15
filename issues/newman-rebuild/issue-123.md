# #123: Harvest: download only invoice rows at the grid (skip Complementos de Pago during drain)

- State: OPEN
- Created: 2026-07-13T05:14:58Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/123

## Body

The incognito drain currently downloads **every** OtrasFacturas row (92 on RPU 053200453456 = 29 facturas + 63 complementos de pago), then #113/PR#120 classifies them post-hoc via `TipoDeComprobante`. Wasteful: ~3× the downloads, ~3× the session-cycles/logins, and it stores 52 junk `P` rows.

**The OtrasFacturas grid already has a document-type column.** Read it during the drain and click XML download **only on invoice (factura / `TipoDeComprobante=I`) rows**. On 053200453456 that cuts 92 → 29 downloads (~7 sessions instead of ~23) and eliminates the complemento contamination at the source.

Tasks:
- Add a grid-scan bridge op that returns per-row `{index, serie_folio, tipo}` from the visible grid cells.
- `download_row_range` (and the batch planner in `cfe_driver._drain`) skip non-invoice rows so only invoice rows consume the 4-per-session quota.
- Keep the post-hoc `tipo_comprobante` column (PR #120) as a backstop.
- Region-independent: prefer the grid's Tipo column / factura marker over the serie prefix.

Follow-up to PR #120 (deep-drain incognito session-cycle) and #113.
