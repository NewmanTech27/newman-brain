# #87: Multi-invoice PDF bundles: fan out one consulta row per invoice

- State: OPEN
- Created: 2026-07-12T09:55:29Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/87

## Body

## Problem
A single WhatsApp PDF can be a **consolidated payment batch** — one document carrying many CFE recibos, each with its own CODE128 barcode. The twilio→consulta extract stage was 1:1: it decoded only the **first** barcode (page 1) and silently dropped every other invoice.

**Observed live:** `pipeline.twilio` id 37 is a **168-page bundle containing 76 distinct RPUs / ~79 invoices** (Grupo Yazaki + ARNECOM plants). The pipeline captured **1**, dropped **75**.

Root cause (three limits):
- `barcode_identify.extract` rendered page 1 only (`first_page=1, last_page=1`) and returned the first barcode.
- `pipeline_endpoint.extract` → `rpc_advance_twilio` creates exactly one consulta row.

## Fix (this PR)
- `barcode_identify.extract_all()` — scan **all** pages, dedupe by RPU, one `BarcodeHit(rpu, adeudo, page)` per invoice. Verified on the real 168-page bundle → **76 invoices in 22s**; first hit == legacy `extract()`.
- `ocr_identify.identify_all()` — one tuple per invoice; each razón social read from **its own page text** (no per-page vision), modal-name fallback for unreadable pages → 76/76 named on the live bundle.
- `pipeline_endpoint.extract()` — fan out to `rpc_advance_twilio_multi` when >1 invoice; **single-invoice path unchanged** (identify_all returns 1 == prior behaviour).
- migration `20260712100000_pipeline_twilio_multi_invoice.sql` — `rpc_advance_twilio_multi` mirrors the **live** `rpc_advance_twilio` (seeds `consulta.razon_social`) per invoice, **dedup-safe** within a twilio parent.

**Rollback-validated against live prod** (BEGIN…ROLLBACK, prod untouched): 3 invoices → 2 consulta rows (duplicate RPU deduped), idempotent re-call returns empty array, no rows persisted.

Tests: +5 barcode (13/13), +2 endpoint fan-out (19/19), self-contained (fake pyzbar/pdf2image, synthetic RPUs — no PII).

## Related finding: duplicate RPUs in pipeline.consulta
Separately confirmed live: consulta had 33 rows / 13 distinct RPUs. One RPU had **6 consulta rows from 6 different twilio uploads** — the same invoice sent 6×, each creating a consulta row, **all parked `needs_review`** because the razón social seed was an OCR payment-form dump (name mismatch). This is *cross-upload* duplication + the OCR-razón-social bug, not a retry bug. `rpc_advance_twilio_multi` is dedup-safe *within* a parent; **cross-upload** dedup is a separate policy decision — tracking here, not fixed in this PR.

## DATA seat action
Apply `20260712100000_pipeline_twilio_multi_invoice.sql` to prod (additive: new function only, does not alter `rpc_advance_twilio`). Note known migration-ledger drift (prod ahead of `supabase/migrations/`) — apply via the reconciled psql path, not a blind `db push`.
