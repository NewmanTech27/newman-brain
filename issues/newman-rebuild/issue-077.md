# #77: extract/consulta: OCR razón social mismatches CFE registered name → CONSULTA_NAME_MISMATCH

- State: OPEN
- Created: 2026-07-11T17:05:23Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/77

## Body

## Problem
Consulta requires the razón social to match CFE's registered name exactly (grid renders only on a match, else "El nombre no coincide"). The OCR'd name from the invoice sometimes doesn't match.

Observed live: RPU `096240956737` — consulta `id 5` and `id 8` both `CONSULTA_NAME_MISMATCH` across 2 name candidates. The extract stage OCR'd a razón social that CFE's Consulta rejects.

## Likely causes
- OCR read the name slightly off (accent, abbreviation, extra/missing word, entity-suffix form).
- The `_consulta_name_candidates` canonicalization ladder (raw + punctuation-stripped upper) doesn't cover CFE's exact stored form.
- The bill's printed razón social ≠ CFE's *account* registered name (they can differ).

## Directions
- Add more name candidates: the barcode has no name, but the recibo XML (once we have any recibo) carries `<NOMBRE>` (CFE authoritative) + Receptor razón — feed those back as candidates. For the FIRST consulta we only have the OCR name, so improve OCR: stronger model already used for images; consider a targeted re-read of just the razón social region.
- Expand the canonical ladder: try dropping/normalizing entity suffixes (S.A. DE C.V. ↔ SA DE CV ↔ SADECV), collapse accents, try first-N-words.
- When all candidates fail, park `needs_human_review` with the OCR name so a human can correct it (don't just fail).

## Scope
`cfe_driver._consulta_name_candidates` (canonical ladder) + `ocr_identify` (name read) + consulta failure → `needs_review` instead of terminal `failed`.
