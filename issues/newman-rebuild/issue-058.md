# #58: Enforce ^[0-9]{12}$ on the OCR-path RPU + disambiguate multiple 12-digit runs

- State: OPEN
- Created: 2026-07-11T07:52:12Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/58

## Body

Committee blocker (12 cites), CTO-verified: barcode_identify has ^\\d{12}$ but the OCR path (ocr_identify _RPU_BARE = \\b(\\d{12})\\b) has NO format gate and can grab the WRONG 12-digit run (invoice #, serie-folio, tax id) — the same class of bug cfe_driver already documents for folios. Required: enforce exactly-12-digits on the OCR RPU, cross-check against the barcode when both present (#56), and reject/flag when multiple distinct 12-digit runs appear on the page. (CTO note: leading-zero truncation claim was overstated — group(1) preserves zeros.) (#49)

## Comment by NewmanTech27 (2026-07-11T09:28:05Z)

DONE (5266375): edge RPU rigor ported to the live Deno fn (invoice-intake) via _shared/rpu_extract.ts — label-anchoring (RPU/NO.DE SERVICIO-adjacent over bare), rejects non-12-digit, multi-candidate→needs_human_review+candidates (no silent pick), replacing the old \b(\d{12})\b substring match. + _shared/size_guard.ts NEWMAN_MAX_MEDIA_BYTES preflight (413+dead-letter instead of edge OOM). 18 Deno tests + 26 Node assertions. Barcode CODE128→edge left as a NOTE (#56, larger Deno lift).
