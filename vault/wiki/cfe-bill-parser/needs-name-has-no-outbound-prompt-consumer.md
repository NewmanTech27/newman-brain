---
title: needs_name / needs_ocr bulk_pdf states have no outbound-prompt consumer — silent dead-end
type: analysis
service: cfe-bill-parser
kind: finding
tags: [cfe-bill-parser, whatsapp, intake, edge-function, wired-consumer]
created: 2026-07-09
updated: 2026-07-09
sources: ["newman-architecture/agents/cfe-collector/main.py:847-876 — nameless branch marks bulk_pdf needs_name (:871) but never calls send_whatsapp (only the named branch does, :864)", "whatsapp-intake edge fn: synchronous PDF ack promises 'te confirmaremos los RPUs'", "public.cfe_deadletter_watchdog (migration 012_deadletter_watchdog_split_bad_download.sql) — counts needs_ocr/needs_name/pending >2h, logs client.cfe_health only", "prod observation 2026-07-09: crm.comms_outbox empty, 0 outbound ever to the sender phone; bulk_pdf id=2 stuck at needs_name with confirm_phone set"]
verified_at: 2026-07-09
verified_against: 74809d0
confidence: verified
---

# needs_name / needs_ocr bulk_pdf states have no outbound-prompt consumer

## The finding

When a CFE bill forwarded over WhatsApp is a **PDF**, the edge intake stores it,
enqueues a `client.bulk_pdf` job, and **synchronously replies to the sender
promising a follow-up** ("PDF recibido… te confirmaremos los RPUs"), capturing
the sender's number as `bulk_pdf.confirm_phone`.

The mini splitter then parses the PDF. If a service yields an **RPU but no
readable titular** (see [[pdf-intake-titular-extraction-fails-real-bill]]), the
splitter routes it to `status='needs_name'` (`cfe-collector/main.py:871`) — and
that is where the flow **silently dies**:

- The **nameless branch sends nothing.** `send_whatsapp` is called **only** on
  the *named* branch (`main.py:864`, the "¿es correcto?" confirmation). The
  nameless branch only prints to stderr and marks the status.
- **No cron or function consumes `needs_name`** to prompt the sender for the
  titular. The *only* consumer is `cfe_deadletter_watchdog` (migration 012),
  which merely **counts** `needs_ocr/needs_name/pending` rows older than 2 h and
  inserts an internal `client.cfe_health` ops alert — it never messages the
  sender.
- The same silence applies to **`needs_ocr`** (scanned/no-text-layer PDFs).

**Net effect:** a nameless (or scanned) bulk PDF is a **silent dead-end**. The
sender is promised a follow-up that never arrives, `confirm_phone` is captured
but never used, and the bill can never reach CFE **Consulta** — which requires
the exact registered titular, so a nameless row is deliberately not enqueued.

## Evidence (prod, 2026-07-09)

A real invoice forwarded over WhatsApp landed as `bulk_pdf` id=2. After the
`bulk_pdf_status_chk` fix (which let `needs_name` be written at all), it settled
at `status='needs_name'` with `confirm_phone` set — and **`crm.comms_outbox` was
empty; zero outbound messages were ever queued to the sender.** No RPU/client
identifier is recorded here (none was persisted; PII withheld by policy).

## Why this is a [[edge-function-maximalist]] "wired-consumer" gap

[[edge-function-maximalist]] puts **`collection_request` orchestration + status**
on the edge layer. A status value that is *written but has no consumer wired to
act on it* is exactly the failure mode that decision must guard against:
orchestration states are only real if something advances them. It also matches
constraint #3 (every edge function/RPC ships with a test): a per-path test that
drove a nameless PDF end-to-end would have caught that `needs_name` has no exit.

The upstream cause is [[pdf-intake-titular-extraction-fails-real-bill]]; this
page is the downstream consequence — the state a failed titular lands in has no
way out.

## Fix direction (NOT applied — knowledge only)

Wire a consumer for `needs_name`/`needs_ocr`: on the nameless branch (or a cron
over `needs_name` rows carrying `confirm_phone`) send a WhatsApp asking the
sender for the exact titular, and accept the reply to release the parked
request. No schema change is required — this is a missing code hop.

## Related

- [[pdf-intake-titular-extraction-fails-real-bill]] — the upstream extraction failure that produces the nameless state
- [[edge-function-maximalist]] — the decision this gap is an instance of (unwired orchestration state; untested per-path hop)
