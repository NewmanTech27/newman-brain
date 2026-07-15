# #113: Harvest stores non-invoice CFDIs (Complemento de Pago, TipoDeComprobante≠I) — filter to invoices only

- State: OPEN
- Created: 2026-07-12T17:44:26Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/113

## Body

## Problem
The harvest/consulta path stores **every** CFDI XML it captures, not just electricity invoices. CFE also emits **Complemento de Pago** (payment receipts, `TipoDeComprobante="P"`) and potentially credit notes (`E`) etc. These are not invoices:
- A `P` doc has `SubTotal`/`Total="0"` in the header (the amount lives in the payment complement), so it pollutes `derive_from_recibos` ranking/total logic (`consulta.py`), and clutters `raw_cfe.*`.

## Fix
- Add `tipo_from_xml_string(xml)` to `consulta.py` (parse the `cfdi:Comprobante TipoDeComprobante` attribute).
- In `derive_from_recibos` (and wherever recibos are collected/stored), **keep only `TipoDeComprobante="I"`** (Ingreso = invoice); drop `P`/`E`/`N`/`T`. Keep XMLs with no CFDI type only if they're the CFE OCR-recibo format (verify).
- Apply the same filter before `rpc_store_raw_consulta` / `rpc_store_raw_mi_espacio` so `raw_cfe.*` holds invoices only.
- Backfill: purge existing non-`I` rows from `raw_cfe.consulta` / `raw_cfe.mi_espacio`.

## Verify
Count `TipoDeComprobante` distribution in `raw_cfe.*` before/after; confirm the newest-recibo total is derived from an `I` doc, never a `P`.

## Comment by NewmanTech27 (2026-07-13T00:20:33Z)

Confirmed live on RPU 053200453456 (30-month grid). The 81 drained XMLs split **29 invoices + 52 Complementos de Pago**.

**The series-prefix classifier is region-fragile.** `doc_taxonomy.classify_doc` hardcodes `KC`=recibo, `K9`/`KX`=pago (from RPU 679220758161). This account uses `PB`/`P9`/`PY`, so `classify_doc` returns UNKNOWN for every row here → the filter silently fails.

**Robust fix: classify on the CFDI `TipoDeComprobante` attribute** (region-independent):
| field | real invoice | complemento |
|---|---|---|
| `TipoDeComprobante` | `I` | `P` |
| `Total` | real $ | `0` |
| `Impuestos` element | present | absent |

Recommend filtering `TipoDeComprobante == "I"` in the parser/taxonomy instead of the folio series. That cleanly isolated the 29 real invoices here (see PR #120).
