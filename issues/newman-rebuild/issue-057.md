# #57: Vision RPU confidence gate + DB-level human-review enforcement

- State: OPEN
- Created: 2026-07-11T07:52:10Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/57

## Body

Committee blocker (31 cites): vision RPU exact-match plateaus ~50% on scanned/image-only invoices (scan-quality, not model choice). Today needs_human_review is a blanket flag with no calibrated confidence, and the row's rpu is written before the gate; enforcement is app-code only (intake_worker blocks dispatch). Required: (a) calibrated per-field confidence (not blanket), (b) an audit-trail column proving a human verified the RPU, (c) a DB-level guard (constraint/RPC) that a needs_human_review row physically cannot reach dispatched/registered without a human-confirm timestamp. (#49/#52)

## Comment by NewmanTech27 (2026-07-11T08:54:41Z)

Committee (25 cites): all 5 vision models floor at ~50% RPU on SCANNED invoices — no model swap fixes it. So needs_human_review must HARD-BLOCK MiEspacio registration (DB-level, not just an app flag), the 0.75 confidence threshold must be calibrated via a ROC on real scans (currently arbitrary + model-self-reported), and a documented recovery flow is required (review queue / re-request-digital / salesman callback) so a scan-sourced RPU never auto-harvests into a wrong account.

## Comment by NewmanTech27 (2026-07-11T09:28:03Z)

DONE (branch extraction/quality, migration 20260711180000_review_gate.sql, UNAPPLIED): human_confirmed_at + confirmed_by columns; rpc_dispatch_upload now SELECT..FOR UPDATE then RAISES REVIEW_REQUIRED when needs_human_review AND human_confirmed_at IS NULL — a scan-sourced RPU physically cannot reach dispatched/harvest without rpc_confirm_review(upload_id, confirmed_by). Recovery flow documented (confirm / re-request-digital / reject). Hard DB-level gate, not app-only.
