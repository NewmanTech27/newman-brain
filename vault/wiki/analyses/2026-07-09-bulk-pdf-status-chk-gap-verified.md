---
title: "bulk_pdf_status_chk missing status values — CTO verification (CONFIRMED; fix scope too narrow)"
type: analysis
tags: [cfe-bill-parser, cto-finding, bulk-pdf, check-constraint, whatsapp-intake, verified]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [prod bwudgrwfwjdbvqhgbwty pg_get_constraintdef client.bulk_pdf_status_chk, newman-architecture origin/main agents/cfe-collector/main.py, db/migrations/012_deadletter_watchdog_split_bad_download.sql]
---

# bulk_pdf_status_chk missing status values — CTO verification

cfe reported that `bulk_pdf` id=2 fell to `'failed'` because the splitter sets
`status='needs_name'` on titular-extraction fail, which `bulk_pdf_status_chk` rejects.
Verified read-only against prod `bwudgrwfwjdbvqhgbwty` on 2026-07-09.

## (1) Splitter sets status='needs_name' on name-fail — CONFIRMED
`agents/cfe-collector/main.py:868-871`: when `nameless` rows exist (RPU-known / name-missing),
`supa.mark_bulk_pdf(jid, "needs_name", len(named), …)`. `mark_bulk_pdf` is an RPC that updates
`client.bulk_pdf.status` (`agents/_shared/newman_common/supa.py:174-176`).

## (2) Constraint lacks 'needs_name' — CONFIRMED
Live def: `CHECK ((status = ANY (ARRAY['new','processing','done','failed'])))`. `'needs_name'`
is absent → the update raises `23514`, and the caller's except path marks the row `'failed'`
(`main.py:880`). Prod `bulk_pdf` currently holds only `failed`(1) + `done`(1) — consistent.

## (3) Adding 'needs_name' via ALTER is additive & safe — CONFIRMED
- **No existing row violates:** current values are `failed`/`done`, both already allowed; a
  DROP+ADD with a superset array validates cleanly.
- **No triggers:** `pg_trigger` on `client.bulk_pdf` returns none.
- **No other caller breaks:** widening an allowed-value set only ever permits more.
- **Zero golden/proposal/finance overlap:** `bulk_pdf` is the WhatsApp bulk-PDF intake queue;
  unrelated to `calc_core`/`ppa_pricer`/proposal/`finance.ts`/the golden test.

## ⚠️ FLAG — a 'needs_name'-only fix is INCOMPLETE (two sibling bugs stay live)
The same collector sets **two more statuses the constraint also forbids**, via the identical
mechanism:
- `main.py:839` → `mark_bulk_pdf(jid, "needs_ocr", …)` (scanned PDF, no text layer)
- `main.py:829,834` → `mark_bulk_pdf(jid, "pending", …)` (pdftotext missing / timeout)

Both are absent from the constraint, so **every scanned bill and every pdftotext-failure bill
hits the same `23514` → `'failed'`**. Migration `012_deadletter_watchdog_split_bad_download.sql:18`
confirms intent: it reclaims `status in ('needs_ocr','needs_name','pending')` — a WHERE clause
that is currently **dead**, because the constraint forbids all three from ever being written.

**The correct additive fix adds all three: `needs_name`, `needs_ocr`, `pending`.** Adding only
`needs_name` fixes id=2 but leaves scanned-PDF and pdftotext-failure intake silently broken.

## Verdict
(1)(2) CONFIRMED. (3) The ALTER is additive & safe — but the fix must add **`needs_name`,
`needs_ocr`, and `pending`**, not `needs_name` alone. Review the 017 draft against this.

## Related
- [[2026-07-09-claim-media-boolean-bug-verified]] — sibling WhatsApp-intake prod-only-drift bug
