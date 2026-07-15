# #96: ocr_identify: payment-form layout dumps whole-page text as receptor_name → guaranteed CONSULTA_NAME_MISMATCH

- State: OPEN
- Created: 2026-07-12T10:14:10Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/96

## Body

## Problem

A specific, reproducing root cause behind part of the #77 needs_review pile: on CFE payment-form style layouts (the doc types `doc_taxonomy.py` classes as payment docs when they come from the drain, but which also arrive as WhatsApp uploads), the text-first name extraction in `harvest/ocr_identify.py` does not find a clean razón-social anchor and ends up storing an essentially whole-page text dump as `receptor_name`.

Observed live (2026-07-12): every consulta row seeded from one such upload carried the page-dump as its name → the Consulta drive's name gate can never match → `CONSULTA_NAME_MISMATCH`, parked `needs_review`. Combined with cross-upload duplication (#92), a single re-sent payment-form invoice manufactured six human-review rows at once. The barcode-side RPU + adeudo were correct throughout — only the name path fails.

## Fix

In `ocr_identify.py`:
1. Detect the payment-form layout (its text signature is distinctive) and branch: pull the client entity from its known position, or
2. If no confident name is found, fall back to **barcode-only + `needs_review` with NULL name** instead of storing the page dump — a NULL seed is honest; garbage poisons the name-candidate ladder and pollutes `pipeline.consulta.razon_social`.
3. Add a sanity cap regardless of layout: a receptor_name candidate longer than a plausible razón social (say > 120 chars or > 8 words) is never stored as a name.
4. Regression test with a synthetic payment-form fixture (ACME / 999999999999).

Related: #77 (name-candidate ladder / mismatch parking), #52 (vision grabs service address), #58 (12-digit enforcement on the OCR path).
