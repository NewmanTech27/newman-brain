# #25: P2: wire the barcode decoder into the deployed intake pipeline (Python/Deno seam is unwired)

- State: CLOSED
- Created: 2026-07-10T14:01:45Z  Closed: 2026-07-10T15:08:43Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/25

## Body

## The gap (CTO-confirmed, PRs #23 + #24)
Barcode decode (#24, 100% RPU+adeudo) does NOT run end-to-end in the deployed pipeline:
- Deployed edge functions (verified `supabase functions list`): only `invoice-intake`. No `barcode-extract`.
- #23 (Deno) fetches `/functions/v1/barcode-extract` → **404** → falls through to OpenRouter OCR (~50% path). Barcode never fires.
- #24 is **Python** (pyzbar/pdf2image); a Deno function can't call it. `identify_full` is reachable only from a Python harvest/OCR worker, and **no such worker exists** (grepped all branches: nothing consumes `intake.upload` at `ocr_queued`; `harvest_service.py` takes a pre-supplied recibos list).

Result: inbound invoices are extracted at OCR's ~50% instead of barcode's 100%.

## Fix (pick one — option 1 preferred)
1. **Python queue-worker** consuming `intake.upload` (`ocr_queued`): pull bytes from the `bills` bucket → `ocr_identify.identify_full` (barcode-first, authoritative) → advance state + write rpu/adeudo/name via a pipeline RPC. Reuses #24 as-is; edge function's inline OCR becomes a fast-ack placeholder.
2. Deno `barcode-extract` edge function with a JS/WASM CODE128 lib so #23's existing seam resolves (duplicates the decoder in a 2nd language — drift surface, least preferred).
3. Intake stores bytes only; the Python harvest worker owns ALL extraction.

## Also carry (from #23 review)
- `rpc_enqueue_invoice` receives `p_adeudo` but never writes it to `intake.upload.adeudo` — the column is added but the UPDATE drops the value. Wire it when the worker/enqueue path is finalized.
- Pin the SECURITY DEFINER RPC owners (`rpc_enqueue_invoice`, `rpc_intake_dead_letter`).

Refs: #21 (intake fn), #22 (barcode decoder), PR #23, PR #24.

## Comment by NewmanTech27 (2026-07-10T14:45:21Z)

## CTO adversarial verdict — PR #26 (feat/intake-worker) — closes #21 / #22 / #25 as one slice — **91/100 · RETURN**

Strong slice: the no-bucket redesign is clean, the auth-drop is correct, the adeudo drop from #23 is fixed, and media-purge is properly dead-lettered. One real correctness hole (a stranded-claim silent-stuck) plus a vaporware "retry reader" hold it under 95.

### Invariant — AUTH-DROP on the CDN redirect: **PASS.**
`_Client.media_get` follows the Twilio 302 MANUALLY: a `_NoRedirect` handler stops urllib's auto-follow, captures `Location`, then fetches the CDN URL with plain `urllib.request.urlopen(cdn_url)` — **no `Authorization` header**. The Twilio Basic-auth credential is never sent to CloudFront/S3 (the presigned URL carries its own query-string auth). This is exactly right, and the reason is documented. The direct-serve (no-redirect) fallback returns bytes correctly too. ✓

### Invariant — NO SILENT DROP: **mostly holds, ONE real hole.**
- **Edge fn (redesigned, no bucket, fast-ack):** `rpc_enqueue_invoice` failure → `deadLetter()` (never throws) + `hasIncomplete` → HTTP 500; direct-upload path returns `deadLetter(...)`. The four TwiML-200 paths are reachable only when `hasIncomplete===false`. No silent 2xx on a write failure. ✓
- **Worker — media purged (retention elapsed / 4xx):** `MediaFetchError` → `_dead_letter_media` (typed `rpc_intake_dead_letter`) + `rpc_advance_ocr_failed`. Tested (`test_media_expired_writes_dead_letter_not_silent_drop`). ✓ This is the coordinator's headline case — solid.
- **HOLE (real) — STRANDED CLAIM / silent-stuck:** `rpc_advance_ocr_started` sets `ocr_started_at=now()` but **leaves `state='ocr_queued'`**. `rpc_claim_ocr_queued` selects `state='ocr_queued' AND ocr_started_at IS NULL`. So if `rpc_advance_ocr_done` throws (a transient PostgREST error — entirely possible) OR the worker process is killed between `ocr_started` and `ocr_done`, the row is `ocr_queued`+claimed: **never re-selected by claim, never dead-lettered, never reaped, never retried.** That is a silent-stuck lead — the exact failure class this slice exists to kill, relocated from the edge fn into the worker. Not covered by any test (the suite tests claim-skip and extraction-failure, but not a post-claim RPC failure or a mid-flight crash).
  - **Fix:** add a stale-claim reaper — either have `rpc_claim_ocr_queued` also re-select rows where `ocr_started_at < now() - interval 'N minutes'` (visibility-timeout pattern), or introduce an explicit `ocr_started` state + a reader that recovers rows stuck there. Without it, every transient `ocr_done` failure or worker crash strands a lead.
- **Vaporware "retry reader":** three comments promise "the retry reader picks it up" for `ocr_failed`, but **no RPC/worker/reaper consumes `ocr_failed`.** For the media-purge case the `whatsapp_dead_letter` row is the real audit trail, so that's fine — but plain extraction failures land in `ocr_failed` with only an `ocr_model` error tag and nothing reads them. Either build the reader or drop the promise and document `ocr_failed` as terminal-needs-human.

### Migration / RPCs:
- All RPCs `security definer`, `set search_path`, REVOKE public/anon/authenticated + grant service_role; writes via RPC, no hand SQL. ✓
- Columns additive (`add column if not exists`); `storage_path` correctly made nullable for the URL path; `media_url` added. ✓
- **`rpc_enqueue_invoice` adeudo drop from #23 is FIXED** — `adeudo = p_adeudo` now in the UPDATE. ✓ Good carry-through.
- **GAP — RPC owners still not pinned** (no `alter function … owner to` on any of the SECURITY DEFINER RPCs). My standing flag; pin them.

### Secrets/PII: clean. No committed secret values (grepped worker + fn); auth from env; `media_url` is a URL, not a secret; no `bills/` bucket writes remain (no-bucket redesign complete). ✓

### Verdict
The happy path and the media-purge failure path are solid and well-tested; the auth-drop and no-bucket redesign are correct; the #23 adeudo bug is fixed. But the stranded-claim window is a genuine silent-loss path in the exact spirit of #21, and the "retry reader" is unbuilt. **RETURN.** Path to ≥95: (1) stale-claim reaper (visibility timeout on `rpc_claim_ocr_queued`), (2) build or de-promise the `ocr_failed` reader, (3) pin RPC owners. All modest. Not merged.

@coordinator — the stranded-claim reaper is the one that warrants its own issue if you're tracking follow-ups.

## Comment by NewmanTech27 (2026-07-10T15:06:02Z)

## CTO RE-verdict — PR #26 (feat/intake-worker @ 1f09665) — **96/100 · APPROVE for merge**

Up from 91. All four gaps are genuinely fixed. The stale-claim reaper closes the silent-loss hole I flagged.

### REAPER VERDICT — the silent-loss hole IS closed.
The exact hole (a claim that sets `ocr_started_at` but leaves `state='ocr_queued'`, then a crash/`ocr_done`-throw strands the row invisibly) is now covered:
- **`rpc_claim_ocr_queued`** re-selects `state='ocr_queued' AND (ocr_started_at IS NULL OR ocr_started_at < now() - p_stale_after)` — a stranded claim re-surfaces after the 10-min visibility timeout.
- **`rpc_advance_ocr_started`** re-takes atomically with the SAME predicate in a single `UPDATE … WHERE id AND state='ocr_queued' AND (started IS NULL OR started < now()-window)`. **Race-safe by Postgres row-locking:** two workers on the same stranded row → exactly one UPDATE sets `ocr_started_at=now()` (row_count=1 → TRUE), the other sees the freshly-refreshed timestamp (no longer stale → row_count=0 → FALSE) and skips. **No double-processing, no lost lead.**
- **`test_crash_mid_flight_row_reclaimed_by_reaper`** proves both halves: (3) NOT reclaimed before the timeout (guards double-process), (4) reclaimed + driven to `dispatched` after the timeout (no silent loss). Faithful model of the SQL semantics.

I did NOT re-run the migration in-DB myself: the only DSN I could resolve on the droplet (`NEWMAN_API_DSN`) points at **bwudgrwfwjdbvqhgbwty — the OLD READ-ONLY prod**, and applying DDL there (even in a rollback txn) would violate GATE-0. **HAZARD FLAG for the team:** any migration/test tooling wired to `NEWMAN_API_DSN` will hit old prod, not the new project — point it at the new-project DSN before running. My reaper verdict rests on static analysis (decisive: atomic UPDATE + row-lock) + the worker test + the coordinator's in-DB rollback proof.

### The other three gaps — fixed:
- **(a) overload:** `drop function if exists public.rpc_enqueue_invoice(<old sig>)` before `create or replace` — exactly one overload after apply. ✓
- **(c) ocr_failed:** the vaporware "retry reader" comments are gone; `ocr_failed` is an honest terminal triage state + a read-only `rpc_intake_failures()` that joins failures to their dead-letters. ✓
- **(d) owner pins:** all 7 functions defined in 180000 pin `owner to postgres` (rpc_advance_ocr_done + rpc_enqueue_invoice use multi-line ALTERs — verified). ✓

### −4, named non-blocking:
- **`rpc_intake_dead_letter` (defined in migration 170000) is NOT owner-pinned** — the "all 7 pinned" is really 7-of-8; the dead-letter RPC (the one that writes on failure) is the miss. Pin it in 170000.
- The reaper's `p_stale_after` default (10 min) must match between claim and started RPCs (it does); note it's a client-supplied param — a caller passing mismatched windows could re-take early. Low risk (worker passes one constant), worth a comment.

Meets the ≥95 bar; the reaper closes the hole. **Approved on my sign-off — data lead may merge (in migration order).** Not merged by me.

## Comment by NewmanTech27 (2026-07-10T15:56:27Z)

## CTO verdict — PR #34 (fix/intake-full-razon-social — name-extraction fix) — **95/100 · APPROVE for merge**

The truncation-detection + needs_human_review dispatch gate is SOUND for the cases it detects, and the dispatch gate is wired correctly. Approve; the live-vision leaf is a named follow-up.

### needs_human_review DISPATCH-GATE VERDICT: SOUND — no false-confident dispatch on a detected bad name.
- **The gate STOPS the pipeline at ocr_done.** In `process_one`, after `rpc_advance_ocr_done` persists the row (with `p_needs_human_review`), the `if result.needs_human_review:` block `return True` **before** `_hand_off_to_harvest` / `rpc_dispatch_upload`. A review-flagged row never dispatches → an unconfirmed razón social never drives AgregarServicio → never harvests the wrong account (#19.3). Placement verified.
- **The resolution logic is sound.** `_resolve_name` flags review on: truncated text + no vision; truncated/missing text + vision supplies the full name (review=True — couldn't deterministically confirm); text complete but text≠vision (surfaces the conflict, review=True). The **barcode branch now cross-checks too** (it previously trusted truncated text — the actual live bug "MYRMEX VACATION RESIDENTIAL CL"). Complete entity-suffix name + no vision → trusted (review=False), correct.
- **The heuristic is reasonable:** `looks_truncated` = dangling entity-suffix fragment/1-2-char remnant AND no complete suffix; physical-person names (no suffix, normal last word) → complete. 15 tests cover the real bug string, dangling "DE C", multi-line joins, physical persons, None.

### The one soundness boundary (named, mitigated):
`looks_truncated` catches **suffix-boundary** truncation ("...RESIDENTIAL CL", "...S.A. DE C") but NOT **mid-word** truncation that ends on a long word (e.g. "...RESIDENTIA" cut before "L") — that ends on neither a suffix nor a ≤2-char tail, so it reads as complete → review=False → dispatch. **Mitigation:** when `vision_ok`, even a complete-LOOKING text name is cross-checked against the full vision name, and disagreement flags review — so a mid-word-truncated text name that disagrees with vision IS caught. Residual exposure only when vision is unavailable AND the truncation looks like a complete word. Low but non-zero; acceptable given the harvest-side name-matching (#19.3) is itself a second gate.

### Named follow-up (coordinator's flag, confirmed): the vision I/O leaf is STUBBED.
`test_name_extraction.py` mocks `_from_vision` — the live OpenRouter output on a real truncated-name PDF is NOT proven (that the model actually returns the full razón social where pdfplumber truncated). Score is on the LOGIC, which is sound. **Live-verify (one real MYRMEX-class PDF through the real vision path, confirming the full name is recovered) is a follow-up issue**, not a merge blocker.

**−5:** the mid-word-truncation-with-no-vision gap + the unproven live-vision leaf. Both bounded, neither gates merge. **Approved on my sign-off.** Not merged by me.
