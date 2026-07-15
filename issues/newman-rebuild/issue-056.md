# #56: Deterministic barcode (CODE128) RPU cross-check in edge extract

- State: OPEN
- Created: 2026-07-11T07:22:32Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/56

## Body

The CFE payment barcode encodes the RPU deterministically (first 12 digits of the CODE128, ~100% when the barcode is present) — far more reliable than a vision read for the ONE critical field. The harvest-side Python decoder already does this; the edge extract path relies solely on the vision model. Add a WASM CODE128 decode (image media) / a barcode read in edge and CROSS-CHECK the vision RPU against it; on disagreement prefer the barcode + flag. Biggest single lever for RPU accuracy. (#49/#52)

## Comment by NewmanTech27 (2026-07-11T07:52:22Z)

Committee reinforces this as the single biggest RPU-accuracy lever (ties to the ~50% vision ceiling, blocker #57/#58): when the barcode is present it gives the RPU deterministically — cross-check the vision/OCR RPU against it and prefer the barcode on disagreement.
