# #71: extract: image (JPEG) support + pdfplumber-first name + sharper OCR prompt (board feedback)

- State: OPEN
- Created: 2026-07-11T12:32:59Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/71

## Body

Three board directives on the extract stage (all shipped in one commit on `pipeline/executors`):

1. **JPEG → try the barcode + OCR the name, stronger model if needed.**
   `barcode_identify.extract` now content-sniffs magic bytes (the endpoint writes every blob as `.pdf`) and decodes CODE128 from JPEG/PNG/WEBP directly (PIL+pyzbar) with photo passes (grayscale/autocontrast/2x). Vision now sends raw image bytes and uses `gemini-2.5-pro` for images (`NEWMAN_VISION_MODEL_IMAGE`). RPU stays barcode-authoritative — digits are never OCR'd.

2. **PDF with a text layer → pdfplumber first for the razón social.**
   A COMPLETE pdfplumber name is now trusted and skips the vision call entirely (was cross-checking every PDF against vision). Vision only runs for scans/images or truncated names. Side benefit: PDF extract drops from ~11s → ~3s (no needless vision).

3. **Improve the OCR prompt: topmost text under the CFE logo, razón social always big caps.**
   Prompt now localizes the name as the TOP block directly below the green CFE logo, ALWAYS bold ALL-CAPS; read verbatim, keep all-caps, never truncate.

## Verified live
- JPEG (tid 5): name now extracted (all-caps, top-left), parked `needs_review` with the name filled (photo carries no machine-readable CODE128 → correct to park, RPU only from barcode).
- pdfplumber-first: unit-tested — 0 vision calls on a complete name, vision on truncated/missing.
- barcodeless PDF (tid 23): name filled via vision, parked for review.

Result: the 2 previously name-less `NO_BARCODE` rows now carry a razón social for human review; RPU authority unchanged.
