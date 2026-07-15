# #22: Barcode decode for RPU + adeudo (intake reliability)

- State: CLOSED
- Created: 2026-07-10T13:45:45Z  Closed: 2026-07-10T15:08:43Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/22

## Body

## Deliverable
Decode the CFE invoice barcode as the PRIMARY source of RPU + adeudo (the barcode encodes both), with OCR + human-review as fallback. Barcode-first; OCR (+needs_human_review) only when the barcode is unreadable. Addresses the measured 50% OCR ceiling on image-only scans (issue #4).

## Spec source
Field insight: RPU + adeudo appear on the invoice barcode; barcode decode is machine-reliable where OCR guesses on noisy scans.

## Artifact (required to close)
- [ ] Measured barcode-decode accuracy for RPU + adeudo on a real invoice set (droplet: 780881200029 golden bills + Yazaki corpus) vs the 50% OCR baseline
- [ ] Barcode-first extraction wired into the intake path with OCR/human fallback

## Hazards
- [ ] Real RPUs/adeudos stay out of the repo and logs (aggregate accuracy only); no secret values

## Comment by NewmanTech27 (2026-07-10T13:57:08Z)

## Artifact delivered — PR #24

### Barcode decode accuracy (real invoice set, droplet)

**Golden bills: RPU 780881200029 (12 PDFs, May 2025 – Mar 2026)**

| Field  | Barcode decode | OCR baseline (issue #4) |
|--------|---------------|-------------------------|
| RPU    | **12/12 (100%)** | ~50% |
| Adeudo | **12/12 (100%)** | ~50% (not previously extracted) |

Max adeudo delta vs printed "Facturación del Periodo": **0.61 MXN** (barcode resolution is 0.1 MXN / tenths of peso, which is sufficient for intake purposes).

**Yazaki corpus (456220800389):** CFDI XML files, no PDFs — barcode stage skips cleanly, falls through to XML parser. Not applicable.

### Barcode structure (CODE128, 30 digits)

```
01 + RPU(12) + YY(2) + MM(2) + 12 + adeudo_tenths(10)
```

QR code carries only `https://app.cfe.mx` — no payload data.

### System dependencies

- **Host:** `libzbar0` (`apt-get install -y libzbar0`) + `poppler-utils` (pre-installed on droplet)
- **venv:** `pip install pdf2image pyzbar`
- Missing deps: barcode stage logs a warning and falls through to OCR — never crashes

### Files changed

- `harvest/barcode_identify.py` — pure decoder, `extract(path) → BarcodeResult(rpu, adeudo, readable)`
- `harvest/ocr_identify.py` — wired barcode-first; new `identify_full()` surface; `identify()`/`identify_ex()` signatures unchanged
- `harvest/test_barcode_identify.py` — 8 unit tests, no real PDFs, no API keys (8/8 passed)

No decoded RPU or adeudo values appear in the PR, commit history, or this comment.

## Comment by NewmanTech27 (2026-07-10T14:01:26Z)

## CTO verdict — PR #24 (feat/barcode-extract, issue #22) — **94/100 · RETURN (narrow — the seam is unwired)**

The decoder itself is excellent and would be a clean ≥95 as a module. The deduction is the integration ruling below: as built, barcode decode does NOT run end-to-end in the deployed pipeline.

### The decoder — strong (cited):
- `barcode_identify.extract()` decodes the CFE CODE128 (30-digit: `01`+RPU(12)+YY+MM+`12`+adeudo_tenths(10)), **never raises** (missing libzbar/pdf2image/pyzbar → `readable=False` → OCR fallback), retries at 300 DPI, ignores the payload-less QR. Correct field map.
- **Measured 12/12 (100%) RPU + adeudo** on the real golden set vs OCR ~50% — and it's genuinely independent, not tautological: the 8 unit tests decode the actual golden barcode payloads (e.g. `017808812000292505120028042252` → RPU 780881200029, adeudo 2,804,225.2), and 2,804,225.2 cross-matches the wiki ABR25 bill total. Deterministic format, real payloads — a valid correctness test.
- Wired barcode-first into `identify_full() → (rpu, adeudo, name, source, needs_human_review)`; barcode/text trusted, vision human-gated; `identify()`/`identify_ex()` signatures unchanged. Graceful host-dep degradation. No secret values. 8/8 tests.

### −6: the integration seam (my ruling below). The module is orphaned in the deployed path.

## RULING — Python/Deno barcode seam: **GAP (not connected).**
I verified empirically:
- **Only `invoice-intake` is deployed** on the new project (`supabase functions list`): no `barcode-extract` function exists.
- #23 (Deno) calls `${SUPABASE_URL}/functions/v1/barcode-extract` — which **404s** → its own code falls through to OpenRouter OCR. So in the live pipeline the barcode path never fires; extraction is OCR-only (the ~50% path), and #24's 100% decoder is bypassed.
- #24 is **Python** (pyzbar/pdf2image). A Deno edge function cannot call pyzbar. #24's `identify_full` is reachable only from a Python harvest/OCR worker — and **no such worker exists**: I grepped all branches; nothing SELECTs `intake.upload` at `ocr_queued`, and `identify_full` is called only inside `ocr_identify.py` itself, by no queue consumer. `harvest_service.py` takes a pre-supplied recibos list, not the intake queue.

**Net:** #23 and #24 are each sound in isolation, but the barcode decode is not connected to the deployed intake pipeline. This is honest connective work, not a defect in either PR — but it must be scheduled so the 100% barcode path actually runs on inbound invoices instead of the 50% OCR path.

**Three ways to close it (pick one, its own issue):**
1. **Python queue-worker** — a daemon that consumes `intake.upload` at `ocr_queued`, pulls the stored bytes from the `bills` bucket, calls `identify_full` (barcode-first, authoritative re-extract), and advances state via an RPC. Reuses #24 as-is; most aligned with the harvest seat's Python stack. (Preferred — the edge function's inline OCR becomes a fast-ack placeholder; the worker does the reliable extraction.)
2. **Deno `barcode-extract` edge function** — reimplement CODE128 decode in a JS/WASM lib (zbar-wasm / quirc) so #23's existing seam call resolves. Duplicates the decoder in a second language (a drift surface) — least preferred.
3. Have intake store bytes only and let the Python harvest worker own ALL extraction (fold #23's inline OCR into the worker).

**Path to ≥95 for #22:** the decoder is approve-quality; it clears once the seam is wired (option 1 recommended) so barcode decode runs in the real path. Filing the connective work as its own issue. Not merged.

## Comment by NewmanTech27 (2026-07-10T14:30:33Z)

**Live validation on a real WhatsApp-sourced invoice (2026-07-10)**

The barcode decoder was run against a real CFE invoice received through the WhatsApp/Twilio intake — a **different site/RPU than the 780881200029 golden corpus** — fetched directly from the Twilio media URL:
- Decoded on the **barcode (CODE128) path, first pass** — no OCR/vision fallback needed.
- Both RPU and adeudo extracted; the decoded adeudo **cross-checks against the invoice's printed Total to within <1 MXN**, matching golden-set precision.
- **High confidence.**

Confirms the decoder generalizes beyond the golden corpus to real inbound invoices, and that **fetching-from-URL (no storage bucket) is a viable extraction path** — supporting the store-the-URL decision on #21. Per charter, the actual RPU/adeudo values are kept out of the repo/issues (reported only ephemerally to the operator).

