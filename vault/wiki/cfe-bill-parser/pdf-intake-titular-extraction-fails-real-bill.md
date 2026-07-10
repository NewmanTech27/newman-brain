---
title: pdf_intake extracts the RPU but not the titular on a real CFE bulk PDF
type: analysis
service: cfe-bill-parser
kind: finding
tags: [cfe-bill-parser, pdf-intake, ocr, extraction, whatsapp]
created: 2026-07-09
updated: 2026-07-09
sources: ["newman-architecture/agents/cfe-collector/pdf_intake.py — parse_pdf_bills reads RPU (NO. DE SERVICIO label) + account name off the 'TOTAL A PAGAR' line, no OCR (text layer only)", "newman-architecture/agents/cfe-collector/main.py:847-848 — only rows with BOTH rpu and nombre are enqueued; nameless rows routed to needs_name", "prod observation 2026-07-09: a real CFE bulk PDF forwarded over WhatsApp (bulk_pdf id=2) parsed RPU but no titular on all three forwards — detail 'enqueued 0, 1 missing name'"]
verified_at: 2026-07-09
verified_against: 74809d0
confidence: verified
---

# pdf_intake extracts the RPU but not the titular on a real CFE bulk PDF

## The finding

`pdf_intake.parse_pdf_bills` splits a bulk CFE statement per service and, for
each, reads two things from the pdftotext layer: the **RPU** (from the
`NO. DE SERVICIO` label) and the **account titular** (the name printed off the
`TOTAL A PAGAR` line). On a **real CFE bill forwarded over WhatsApp** on
2026-07-09 (`bulk_pdf` id=2), the **RPU parsed but the titular did not** —
observed **three times** across three separate re-forwards of the same document
(`detail: "enqueued 0, 1 missing name"`).

This is load-bearing because CFE **Consulta requires the exact registered
titular** (char-exact match). The splitter therefore enqueues only rows that
have **both** RPU and name (`main.py:847`); a name-missing row is routed to
`needs_name` and **cannot proceed to CFE**. So an RPU-only parse is not a
partial success — it is a full stop for that bill.

No RPU digits or client name are recorded on this page (PII withheld by policy);
the point is the *extraction reliability*, not the specific values.

## Why it matters for [[edge-function-maximalist]]

[[edge-function-maximalist]] constraint #2 states that a forwarded WhatsApp
image/PDF is "used **only** to read the RPU + titular and archive a copy" — the
authoritative bill fields come later from the collector. If the titular half of
that single job is unreliable on real bills, the stated purpose of the intake
hop is not met, and everything downstream stalls. It is also the
per-function-test gap (constraint #3): there is **no test exercising a real bill
end-to-end** through `pdf_intake`, so titular-extraction failures surface only in
production, one forwarded invoice at a time.

## Consequence

A failed titular lands the job in `needs_name`, which is itself a silent
dead-end — see [[needs-name-has-no-outbound-prompt-consumer]]. Together the two
findings mean a real bulk PDF whose titular doesn't parse is **lost with no user
recourse**: never enqueued, never re-prompted.

## Open questions / fix directions (NOT applied — knowledge only)

- Is the failure a layout mismatch (titular not adjacent to `TOTAL A PAGAR` on
  this bill format) or a missing text layer for the name block? Needs a look at
  the real PDF's extracted text (out of scope here; PII).
- Options: broaden the titular heuristic in `pdf_intake`; add an OCR fallback for
  the name block; and/or fall back to prompting the sender for the titular (which
  also requires closing [[needs-name-has-no-outbound-prompt-consumer]]).
- Add a fixture test that runs a real (redacted) bulk PDF through `parse_pdf_bills`
  and asserts both RPU and titular are read.

## Related

- [[needs-name-has-no-outbound-prompt-consumer]] — the dead-end state a nameless parse falls into
- [[edge-function-maximalist]] — constraints #2 (image only reads RPU+titular) and #3 (per-function tests) this finding stresses
