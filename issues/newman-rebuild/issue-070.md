# #70: pipeline/extract executor: LIVE on the mini — 23 twilio rows drained (21 barcode → consulta, 2 needs_review)

- State: CLOSED
- Created: 2026-07-11T12:20:10Z  Closed: 2026-07-12T12:28:10Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/70

## Body

## Done — extract stage validated end-to-end (real invoices)

Ran `/pipeline/extract` (claim-one-per-tick) on the mini against the 23 seeded `pipeline.twilio` rows.

**Result:** 23/23 processed
- **21** `barcode_ok` → RPU (CODE128) + razón social (vision) → `rpc_advance_twilio` → **21 `pipeline.consulta` rows** (all with rpu + razon_social + twilio_id FK), status `pending`.
- **2** `needs_review` (`NO_BARCODE`) → parked, **no consulta row** — correct per the barcode-authoritative contract (#63). No RPU ever sourced from OCR.

**Timings** (for pg_cron tuning): avg total **11.2s**/row · barcode 3.1s · ocr(vision name) 4.7s · max ocr 14.4s. A 5-min tick is very comfortable.

## Architecture (per board: "secrets always in edge supabase secrets")
Chose **mini inline, vault-mirrored** (edge secret values aren't readable off-edge, and CODE128 only decodes in Python/pyzbar today — Deno barcode is #56):
- Extract runs on the mini; **edge secrets remain the canonical registry**.
- Mini sources the SAME values at runtime: `NR_SERVICE_ROLE_KEY` (rebuild project key via Supabase management API), `TWILIO_*`, `OPENROUTER_API_KEY` (droplet Vault mirror), `NEWMAN_SYNC_SECRET` (generated).
- Deps via nix devshell (`harvest/flake.nix`, committed): pyzbar/pdf2image/pdfplumber/zbar/poppler-utils.

## Media URL (ref #69)
Confirmed stored `api.twilio.com` MediaUrl 307-redirects to the signed `mms.twiliocdn.com` CDN URL; executor fetches with Basic auth + follows the redirect. Working.

## Remaining wiring
- [ ] Persist mini runtime env (`~/.newman-pipeline.env`, 600) + launchd/endpoint so extract runs unattended.
- [ ] Cloudflare route: tunnel passes `/newman/pipeline/*` → mini:8791 (currently `/newman/.*`→8790). Add ingress rule or merge routes.
- [ ] `pipeline.config` (newman_sync_secret, mini_base_url, functions_base_url).
- [ ] Smoke-test `/pipeline/consulta` + `/pipeline/harvest` — **LIVE CFE stages, CEO-run only**.
- [ ] Apply pg_cron migration `20260711230000` after the above.

## Follow-up
2 `NO_BARCODE` rows (tid 5, tid 23) — investigate whether non-recibo media or unreadable scan; they are safely parked for human review either way.

## Comment by NewmanTech27 (2026-07-12T12:28:10Z)

Closing per INT-1. Artifact: `6338c80` + live run evidence in body — 23/23 twilio rows drained (21 barcode_ok → consulta, 2 needs_review). Branch → main merge tracked in #101.
