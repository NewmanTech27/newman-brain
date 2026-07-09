---
title: whatsapp-intake is fire-and-forget and drops data silently
service: tuesday-inputs
kind: finding
sources: ["newman-architecture/supabase/functions/whatsapp-intake/index.ts:153", "newman-architecture/supabase/functions/whatsapp-intake/index.ts:174", "newman-architecture/supabase/functions/whatsapp-intake/index.ts:207", "newman-architecture/supabase/functions/whatsapp-intake/index.ts:251"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# whatsapp-intake is fire-and-forget and drops data silently

**Severity: CRITICAL.** The `whatsapp-intake` edge function wraps its whole body in one `try/catch` that returns an empty TwiML **200** on any exception (`index.ts:251`), so **Twilio never retries**. Every downstream write is fire-and-forget — HTTP error statuses do **not** throw and are mostly not inspected:

- Storage PUT to bucket `bills` — response discarded (`:153`); a failed upload still lets `register_bill_file` record a row pointing at a non-existent object.
- `request_collection` — response never read, and the `"enqueued…"` log fires **unconditionally**, falsely asserting success (`:174–179`).
- `register_bill_file` — PostgREST error status logged as `"pipeline:"` but treated as success (`:170`).
- `crm_ingest_activity` — the response is **not read**, so an error *status* is swallowed with **no log** (`:207`, catch only logs network throws at `:217`). This is the **sole durable audit** of the raw inbound message; on a non-throwing error the message leaves **no trace anywhere** and the sender is not told.

A WhatsApp submission provably reaches durable storage **only if** the signature validates AND `crm_ingest_activity` succeeds. Everything else is best-effort. This defeats the never-drop intent behind the "unlinked tray" design (commit `3a5b34b`).

Related silent-403 trap: unset `TWILIO_AUTH_TOKEN` (defaults `""`, `:17`) or a `WEBHOOK_URL` mismatch makes every message fail the signature check silently — a misconfig is indistinguishable from "no inbound." Fix direction: inspect every HTTP status; return non-2xx (Twilio retries) or dead-letter when the audit write or storage fails; remove the unconditional success log. Tracked as GAP-01/GAP-04 in `docs/specs/tuesday-inputs.md`. See [[crm-rls-rbac-ordering-trap]].
