# cfe-bill-parser: Real Invoice Trace, claim_media Bug (016) and bulk_pdf Status Widening (017)

**Summary**: Traced Jesus's real WhatsApp invoice through the live pipeline, found and drafted fixes for two prod bugs — claim_media's boolean/int type bug and the bulk_pdf_status_chk constraint missing needs_name/needs_ocr/pending — plus two filed findings on the nameless-bill dead-end.
**Tags**: #newman #cfe #whatsapp-intake #migrations #findings
**Created**: 2026-07-09
**Source**: newman-vps session 134584bd-8eea-4471-bfb1-5e61748e0c6a.jsonl (cfe seat), user jesus

---

## Content
- Channel under test: Twilio WhatsApp → gateway-webhook → Drive → `note_whatsapp_intake` RPC → intake-worker/extract.py. Planned synthetic test scrapped when Jesus forwarded a REAL invoice (SID MM8f713f35855a73).
- Bug 1 (016): `public.claim_media` declared `v_inserted` as boolean while holding ROW_COUNT (integer) → silent loss; processed_message stuck 'processing' so Twilio redeliveries re-failed identically. Introduced by migration `claim_media_atomic` (2026-07-08 21:59), NOT 014/015 as first drafted — header corrected before git. Fix: one-line boolean→integer, applied to prod by data seat, verified via pg_get_functiondef.
- Bug 2 (017): pdf_intake splitter sets `bulk_pdf.status='needs_name'` on titular-extraction failure but `bulk_pdf_status_chk` only allowed [new, processing, done, failed] → 23514 → row fell to 'failed'. CTO review widened it: code actually writes pending(:829,:834), needs_ocr(:839), needs_name(:871), done(:874), failed(:880) in agents/cfe-collector/main.py. Constraint widened to all 7; 'awaiting_confirmation' ruled out (belongs to collection_request).
- Re-forwarded invoice landed as bulk_pdf id=2 → id=3 after 017; RPU parsed but titular OCR failed 3× on the real bill.
- Filed findings (vault/wiki/cfe-bill-parser/): `needs-name-has-no-outbound-prompt-consumer` — intake acks "Te confirmaremos los RPUs" and stores confirm_phone but nothing ever prompts the sender for the titular (main.py:871 never calls send_whatsapp; only the named branch :864 does; watchdog only logs at ~2h); and `pdf-intake-titular-extraction-fails-real-bill`. Both linked to [[edge-function-maximalist]].
- Process discipline throughout: draft-only, CTO reviews, Jesus approves each prod apply; both patches recorded in the prod-only-drift-register as owed to the canonical branch; real RPU/titular values never written to wiki/repo.

## Related Notes
- [[2026-07-09-ceo-org-real-invoice-gate0]]
- [[2026-07-09-cto-verification-freeze]]
- [[newman-architecture-project]]
