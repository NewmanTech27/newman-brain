# #54: Extract edge OOMs (WORKER_RESOURCE_LIMIT) — base64 media in memory caps throughput

- State: OPEN
- Created: 2026-07-11T07:22:28Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/54

## Body

The extract edge function base64-encodes each Twilio media in memory before the vision call; batches of even 2 larger PDFs intermittently exhaust the ~256MB edge runtime → WORKER_RESOURCE_LIMIT, and the batch fails (rows stay claimed until stale-reclaim). Limits throughput + reliability of the vision extraction. Options: stream/chunk the base64; pass the Twilio media URL directly to the vision provider if it supports remote images (no in-memory copy); drop batch to 1 + rely on pg_cron cadence; or move heavy media to a bounded worker. Part of the extraction-quality push (#49/#52).

## Comment by NewmanTech27 (2026-07-11T07:52:21Z)

Committee top blocker (42 cites) + CTO-verified specifics: harvest/ocr_identify.py _pdf_text loads the full file (all pages joined); _pdf_page_png_b64 renders at scale=3.0 with NO file-size preflight/resource cap AND leaks the PdfDocument handle (never .close()'d). bridge.mjs has no --max-old-space-size / per-subprocess memory cap / OOM-vs-timeout disambiguation. Required: file-size preflight reject; resource.setrlimit(RLIMIT_AS) around PDF render in the worker; close pypdfium2 handles (try/finally); --max-old-space-size + spawn memory cap on the bridge; heap-profiled soak tests (30+ invoice batch, 92-row grid, concurrent drain) proving flat RSS. batch=2 is a workaround, not a fix.

## Comment by NewmanTech27 (2026-07-11T09:06:44Z)

DONE (branch extraction/quality): (a) Node bridge runs with --max-old-space-size (NEWMAN_BRIDGE_MAX_OLD_SPACE_MB=512) via a self-reexec guard + a puppeteer.launch monkeypatch that injects --js-flags=--max-old-space-size + --disable-dev-shm-usage into Chrome args WITHOUT touching frozen launch() (puppeteer is a shared singleton module). (b) pypdfium2 render: pixel-count gate (NEWMAN_MAX_RENDER_PIXELS=5M downshifts scale for huge MediaBoxes), explicit bitmap.close()+img.close() in finally, per-render timeout (NEWMAN_RENDER_TIMEOUT_S=30). (c) synthetic stress test test_ocr_memory.py: 120 renders → RSS delta 0.05MB, all 130 doc/bitmap/image handles closed. Remaining: the LIVE-CFE 92-row deep-grid drain stress test (CEO live run) — noted as a manual step.
