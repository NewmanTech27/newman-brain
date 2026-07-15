# #21: Invoice intake: WhatsApp/Twilio edge function on the new instance

- State: CLOSED
- Created: 2026-07-10T13:45:43Z  Closed: 2026-07-10T15:08:44Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/21

## Body

## Deliverable
A deployed edge function on the new project (oioyawhgvazebtarigpc) that receives an inbound CFE invoice (Twilio WhatsApp webhook + a direct upload path), extracts RPU + receptor name + adeudo, and enqueues a collection request via a pipeline-advancing RPC. This is the transport layer needed to test invoice-to-offer end to end. No edge functions are deployed on the new instance yet and none are in the repo (verified).

## Spec source
CHARTER v2 mission (invoice in -> OCR -> harvest). Old-prod whatsapp-intake is BEHAVIORAL reference only.

## Must fix (do NOT inherit)
The frozen whatsapp-intake acked Twilio 200 on downstream write failure -> silent lead loss. This function MUST return non-2xx OR write a typed intake dead-letter row on any downstream write failure. Never unconditional 2xx.

## Artifact (required to close)
- [ ] Deployed function slug + a test invoice reaching an enqueued collection row
- [ ] A forced downstream failure producing a dead-letter row, not a 200

## Hazards
- [ ] Twilio creds in Vault, names/lengths only; client-facing writes via RPC not hand SQL

## Comment by NewmanTech27 (2026-07-10T13:54:17Z)

## Artifact — invoice-intake edge function (PR #23)

**Deployed:** `invoice-intake` on `oioyawhgvazebtarigpc`
Dashboard: https://supabase.com/dashboard/project/oioyawhgvazebtarigpc/functions
PR: https://github.com/NewmanTech27/newman-rebuild/pull/23

---

### Enqueue RPC path

`POST /rest/v1/rpc/rpc_enqueue_invoice` (service_role only)

Pipeline advance: creates `intake.upload` row → state `ocr_queued` (no OCR yet) or `ocr_done` (OCR succeeded inline). Wraps `intake.rpc_upload_invoice` from migration 1.

---

### Dead-letter proof

The frozen `whatsapp-intake` returned 200 on downstream write failure → silent lead loss.

This function:
1. **On RPC write failure** (`rpc_enqueue_invoice` returns non-2xx or times out): calls `rpc_intake_dead_letter` → writes typed `intake.whatsapp_dead_letter` row with `error_type='write_fail'`, then returns HTTP **500** (never 200).
2. **On OCR transient failure** (OpenRouter 5xx/timeout): writes `error_type='ocr_transient'` dead-letter row → HTTP 500. Twilio redelivers.
3. **On permanent media 4xx** (Twilio CDN expired): writes `error_type='parse_fail'` dead-letter row, continues to next attachment (does not 500 — media is unrecoverable).
4. **Dead-letter write itself fails** (DB down): logs error + still returns 500 (non-2xx). Never silently 200.

To verify: with migration applied, revoke execute on `rpc_enqueue_invoice` from service_role → send any invoice → observe dead-letter row in `intake.whatsapp_dead_letter` + HTTP 500.

---

### Migration

`supabase/migrations/20260710170000_invoice_intake.sql`

**DO NOT APPLY from this seat — for lead-data only (charter #5).** Introduces:
- `intake.dead_letter_error` enum
- `intake.whatsapp_dead_letter` table (RLS default-deny, zero policies)
- `public.rpc_enqueue_invoice` (SECURITY DEFINER, service_role only)
- `public.rpc_intake_dead_letter` (SECURITY DEFINER, service_role only)
- `intake.upload.adeudo` column

---

### Secrets to set (names only — charter #6)

```
TWILIO_ACCOUNT_SID   — Twilio account identifier
TWILIO_AUTH_TOKEN    — HMAC-SHA1 sig key (~32 chars); function refuses without it (fail closed)
TWILIO_WEBHOOK_URL   — canonical URL Twilio signed; required (function refuses without it)
OPENROUTER_API_KEY   — vision OCR; function dead-letters ocr_transient if absent
```

`SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` auto-injected.

---

### Barcode seam (#22)

`barcode-extract` function called first if deployed. 404 = not yet deployed → silently falls through to OpenRouter vision. No code change needed when #22 ships.

## Comment by NewmanTech27 (2026-07-10T14:00:53Z)

## CTO verdict — PR #23 (feat/invoice-intake, issue #21) — **90/100 · RETURN (close)**

The critical anti-silent-loss fix is genuinely correct and I could not break it. Two real gaps (a silently-dropped adeudo + the unwired barcode seam) hold it just under 95.

### 1. THE critical fix (never unconditional 2xx on write failure) — **HOLDS. I traced every return path.**
- **`deadLetter()` never throws** and always returns non-2xx: it wraps `rpc_intake_dead_letter` in try/catch, and on its OWN failure logs + still `return new Response(..., {status: 500})`. ✓
- **Every write-failure path is covered:**
  - `rpc_enqueue_invoice` fail (Twilio) → `deadLetter(write_fail)` written + `hasIncomplete=true` → forces HTTP 500 at the end. ✓
  - OCR fail → `deadLetter(ocr_transient)` + `if(!dlResp.ok) hasIncomplete=true` (dlResp is always non-ok → always set) → 500. ✓
  - storage put fail → `hasIncomplete=true` → 500 (no dead-letter, correct: bytes not stored, nothing to reprocess). ✓
  - media 4xx-purge → `deadLetter(parse_fail)` written; may return a TwiML 200 — **acceptable**: issue #21's rule is "non-2xx OR a typed dead-letter row", and a purge is terminal (a 500 would trigger pointless redelivery of un-fetchable media). Compliant. ✓
  - Direct-upload path: storage/OCR/write failures all `return deadLetter(...)` (500). ✓
  - The four `twimlOk` (200) paths are reachable only when `hasIncomplete===false` — i.e. every failure was a dead-lettered terminal purge. No path returns 2xx on an un-dead-lettered write failure. The frozen bug is fixed.

### 2. Twilio signature verification — **CORRECT, fail-closed, no bypass.**
- `crypto.subtle.verify("HMAC","SHA-1", …)` — WebCrypto verify is constant-time by construction (better than a hand-rolled byte compare). ✓
- Fail-closed on: no token (`if(!token) return false`), bad base64 sig (try/catch → false), missing `TWILIO_WEBHOOK_URL` (refuses with 500 — closes the req.url-behind-proxy bypass where a proxied URL would mismatch the signed URL). Bad/absent sig → 403, no row written (correct anti-DoS). ✓
- One caveat, not a defect: Twilio's HMAC scheme has no timestamp/nonce, so it is **not replay-resistant** by design — "rejects replay" is inherently unattainable at this layer. Note it; mitigate downstream (sha1 dedupe on the upload) if replay matters.

### 3. Migration — mostly compliant, one real gap:
- RLS `enable`+`force` on `whatsapp_dead_letter`, zero policies, REVOKE public/anon/authenticated + grant service_role. ✓
- Both RPCs `security definer`, REVOKE anon/authenticated, grant service_role; writes via RPC not hand SQL. ✓ `adeudo` column additive (`add column if not exists`). ✓
- **GAP — RPC owner not pinned.** No `alter function … owner to` on either SECURITY DEFINER RPC (my standing flag from PR #14). Owner = whoever applies it; pin it explicitly.
- **GAP (functional, real) — the extracted `adeudo` is silently DROPPED.** `rpc_enqueue_invoice` takes `p_adeudo` and the migration adds `intake.upload.adeudo`, but the RPC body never writes `p_adeudo` into that column (only a comment "add the column below"). So the field #21/#22 exist to capture is lost on every enqueue. Wire `adeudo = p_adeudo` into the UPDATE.

### 4. Secrets — clean.
Names/lengths only in code+PR; values from `Deno.env.get`. Fails **500 (loud)** when `TWILIO_AUTH_TOKEN`/`TWILIO_WEBHOOK_URL` absent; OCR key absent → `ocr_transient` dead-letter, not silent. ✓

### Barcode seam — see the cross-PR ruling I'm posting on #22. In the DEPLOYED path it 404s → always OCR; the Python decoder isn't reachable. Named there.

**Path to ≥95:** (1) write `p_adeudo` into the column, (2) pin the RPC owner. Both small. The core deliverable — no silent lead loss — is solid. Not merged.

## Comment by NewmanTech27 (2026-07-10T14:30:31Z)

**Live test finding + design decision (real WhatsApp send, 2026-07-10)**

The deployed invoice-intake function (v23) was exercised with a real WhatsApp CFE invoice:
- ✅ **Twilio signature verification PASSES** — the request reached `handleTwilio` (account SID matches, `TWILIO_AUTH_TOKEN` + `TWILIO_WEBHOOK_URL` correct). The auth path is confirmed working end to end.
- ❌ It then threw on `storage put bills/... -> 404 Bucket not found` — the `bills` Storage bucket does not exist on `oioyawhgvazebtarigpc`, so nothing enqueued and no dead-letter (it threw before the enqueue/dead-letter path).

**Decision (Jesus): do NOT create a storage bucket / do NOT copy the media into storage — keep the Twilio media URL instead.** Rework (tracked on the intake-worker PR #26):
- Function: drop the `storagePut` to `bills`; on the WhatsApp path store the Twilio `MediaUrl` + content-type + filename + sender/sid into the intake record via `rpc_enqueue_invoice` (add a `media_url` column/param; migration to the data seat). No bucket write. Redeploy.
- Worker (#25/#26): fetch the media from the stored Twilio URL (Twilio Basic auth via the already-set secrets), then barcode-decode. No bucket read.
- Caveat: Twilio retains media only for a limited window → the worker must process promptly (barcode decode is instant), and a "media no longer fetchable" case must be a typed dead-letter, not a silent drop.

Rationale: barcode extraction is proven directly from the Twilio media URL (see #22), so persisting the PDF is unnecessary and avoids duplicating client PII into our storage.

