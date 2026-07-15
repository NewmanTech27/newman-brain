# #132: Invoice = XML + PDF: only return/store recibos that have BOTH files

- State: OPEN
- Created: 2026-07-13T21:55:23Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/132

## Body

## Requirement
A recibo only counts as a real **invoice** when it has **both** its CFDI **XML** and its **PDF**. Rows with only one file (XML-only or PDF-only) are incomplete and must NOT be returned or stored as invoices.

## Current state
- `download_all_recibos(grid, xml_btn, pdf_btn)` (cfe_driver.py:407) downloads both XML+PDF per grid row, returns a flat `list[str]` of paths.
- `raw_cfe.mi_espacio` stores XML only (`xml_content`, sha256-keyed); PDF presence isn't tracked. `xml_count`/`pdf_count` are counted separately on the mi_espacio row but not paired.
- So a row can be stored as an invoice with an XML but no PDF (or vice-versa).

## Change
- Pair downloaded files by invoice key (serie_folio / UUID / filename stem).
- Only treat a recibo as a complete invoice when BOTH .xml and .pdf are present for that key; drop/flag the singletons.
- Apply the filter before `rpc_store_raw_mi_espacio` (and the analogous consulta path) so the pipeline + `pipeline.monitor` only reflect complete invoices.
- Surface dropped singletons in the result detail (don't silently discard — log count).

## Verify
- Harvest a deep account, confirm stored count == number of rows with both files, and that XML-only/PDF-only rows are excluded and logged.

Depends on the proxy-harvest path landing first (#130 / PR #129).
