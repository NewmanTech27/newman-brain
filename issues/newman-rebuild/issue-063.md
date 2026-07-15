# #63: Extraction contract: barcode-authoritative RPU+adeudo, OCR only for receptor_name

- State: OPEN
- Created: 2026-07-11T10:49:27Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/63

## Body

## Product decision (operator)
The extraction must split responsibilities by reliability:
- **RPU + adeudo → the BARCODE scanner, ALWAYS.** OCR/vision must NEVER produce the RPU or adeudo. The CFE payment barcode (CODE128) decodes both deterministically — it decoded **100% on the 53 real recibos**. So the ONE critical field (RPU) becomes deterministic, not a vision guess.
- If the barcode does not decode (damaged / pure-scan): RPU+adeudo are UNAVAILABLE → the row is `needs_human_review` with disposition `barcode_unreadable` (recovery = re-request a digital copy). **No vision/OCR fallback for RPU/adeudo, ever.**
- **OCR/vision → `receptor_name` ONLY** — the razón social: the big bold ALL-CAPS black text at the top-left, directly below the green CFE logo. Low-stakes (Consulta re-derives the authoritative name at harvest), so null/needs_review here is fine.

## Why
This DISSOLVES the extraction committee's dominant blocker (vision RPU floors ~50% on scans, 68 cites): vision no longer touches the RPU, so there is zero wrong-RPU-from-vision risk. RPU accuracy == barcode decode rate (100% on real data); `rpu_wrong` = 0 by construction.

## Scope (in progress on branch extraction/quality)
- harvest/ocr_identify.py: RPU+adeudo from barcode_identify ONLY; vision step extracts only receptor_name; barcode-fail → needs_human_review / barcode_unreadable.
- Vision prompt (Python + edge supabase/functions/invoice-intake): ask ONLY for the razón social (big bold caps below the CFE logo), keep the not-an-address guard; do NOT ask vision for rpu/adeudo.
- Edge: the RPU/adeudo source is the barcode (Python worker decodes on the WhatsApp path); edge vision sets only receptor_name — deterministic CODE128 in Deno remains #56.
- harvest/real_accuracy.py + extraction_metrics.py: reframe — RPU metric = barcode_decode_rate; receptor_name scored via vision separately; adeudo via barcode.
- Then MEASURE the vision receptor_name path on the 53 real recibos using the OpenRouter key (present in Vault).

Supersedes the OCR-RPU-accuracy concerns in #58; relates to #52 (address vs razón social), #56 (barcode→edge), #55 (real accuracy), epic #49.

## Comment by NewmanTech27 (2026-07-11T11:16:02Z)

DONE (1bf3e7d, branch extraction/quality). ocr_identify: barcode decoded → RPU+adeudo from barcode ('barcode' source, high conf); barcode FAIL → rpu=None,adeudo=None,'barcode_unreadable',needs_review — NO vision RPU fallback (proven by test_rpu_never_sourced_from_vision; compute_metrics RAISES on any OCR-sourced rpu). Vision extracts ONLY receptor_name (prompt: 'big bold ALL-CAPS black text top-left below the green CFE logo'). Edge invoice-intake: OCR_PROMPT nombre-only, RPU/adeudo from barcode seam only, vision never sets rpu. Re-measured on 53 real recibos: **barcode_decode_rate 100% (=RPU availability/accuracy), rpu_wrong 0% by design, receptor_name digital 94.2% / overall 92.5% (text path; vision unkeyed), address_leak 0%**. Gate PASS, 9 suites green. The vision-RPU ~50% risk is gone by construction — RPU is deterministic.
