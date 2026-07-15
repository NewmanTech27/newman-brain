# #45: F1 leak-gate false-positive: factura FOLIO read as grid RPU → aborted every drain

- State: CLOSED
- Created: 2026-07-10T21:26:35Z  Closed: 2026-07-10T22:11:39Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/45

## Body

`grid_first_row_rpu` scanned the OtrasFacturas facturas grid for any 12-digit number, but those rows are invoices whose serie-folio (e.g. 000038544895) is ~12 digits — grabbed as the 'RPU', mismatched the target → RPU_MISMATCH, 0 drained on EVERY run. The RPU actually lives in the `ddlServicios` SELECTED option ('ACME RESORTS SA - 999999999999'). Cross-RPU leak is already prevented by fresh-session-per-RPU. Fix: new bridge `selected_service_rpu` op; the F1 verify reads the selected-service RPU (fake adapters fall back to the grid so unit tests hold). Proof: dropdown value=999999999999, drain then pulled 13 XMLs. Fixed in bridge.mjs/cfe_playwright.py/cfe_driver.py (uncommitted → this PR).


## Comment by NewmanTech27 (2026-07-10T22:11:39Z)

Resolved in main via #47 squash (e80c98f).
