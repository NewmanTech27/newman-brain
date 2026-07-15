# #55: Extraction accuracy harness: labeled ground-truth + precision/recall metric

- State: OPEN
- Created: 2026-07-11T07:22:30Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/55

## Body

Extraction quality is currently eyeballed, not measured. To credibly hit >=99, need a labeled set: a fixture of N real recibos (PII-scrubbed / synthetic) with known {rpu, razón social, adeudo}, and a test that runs the extractor and reports precision/recall per field (esp. RPU exactness and nombre-is-a-real-holder-name vs address). Gate the extraction on the metric. Prereq for a meaningful committee score. (#49/#52)

## Comment by NewmanTech27 (2026-07-11T08:07:15Z)

Harness built (branch extraction/accuracy-harness, 2055a61): 21 synthetic labeled cases, pure precision/recall metrics, weighted extraction_score (RPU-dominant: rpu_wrong 45, rpu_missing 20, address_leak 15, holder_f1 10, review_f1 7, adeudo 3). **Measured baseline (origin/main offline text path): extraction_score 79.6/100** — RPU exact-match 100%, wrong 0% (label-anchoring holds), but nombre address-leak 73.7% (the #52 defect: _name_from_text has no address guard, emits the NO. DE SERVICIO line / domicilio as the holder name). This is the number to improve from; the loop now measures each change against it.

## Comment by NewmanTech27 (2026-07-11T08:25:35Z)

extraction_score 96.3 → 97.0 (review F1 → 100%). 97.0 is the offline harness CEILING: every non-adeudo field is perfect (RPU 100%/0%, address-leak 0%, holder 100%, review 100%); the remaining 3.0 is the adeudo weight, and adeudo is NOT OCR'd by design (barcode LineaDeReferencia / Consulta-authoritative). To legitimately reach 99 the harness should score adeudo on the BARCODE path (barcode_identify returns adeudo) rather than the text path, or reweight — tracked; not gamed.

## Comment by NewmanTech27 (2026-07-11T08:54:43Z)

Committee (10 cites): the 21 synthetic cases are statistically under-powered for a 99% RPU target — need 100+ (ideally ~500) hand-labeled REAL invoices. TENSION: charter forbids real client RPUs/PII in the repo. Resolution: measure the vision path EPHEMERALLY on live media (the pipeline's own 'did Consulta accept the RPU?' signal is the real-world ground truth — Consulta unlocking IS RPU-correctness), emit it as telemetry (#61), and keep only synthetic fixtures committed. Also: reweight W_ADEUDO=0 (adeudo is barcode/Consulta-authoritative) + measure barcode adeudo separately, so the score reflects the real contract.

## Comment by NewmanTech27 (2026-07-11T09:06:46Z)

Adeudo reweighted: W_ADEUDO 3→0 (OCR path returns adeudo=None BY DESIGN — barcode/Consulta-authoritative; the penalty measured the wrong contract), redistributed RPU-dominant; NEW separate barcode_adeudo_match metric = 100% over synthetic CODE128 cases (reported alongside, not folded in). Harness extraction_score now 100.0/100 — every measured OCR field perfect (RPU 100%/0%, address-leak 0%, holder 100%, review 100%). Still open per committee: validate the VISION path on REAL invoices via live Consulta-acceptance telemetry (charter-safe, no committed PII).

## Comment by NewmanTech27 (2026-07-11T10:17:25Z)

REAL-invoice validation DONE (5d727ad, charter-safe via barcode-as-ground-truth on 53 real recibos, raw data gitignored): digital rpu_exact_match **94.2%**, overall 92.5%, **rpu_wrong 0.0% everywhere**, barcode decode 100%, address-leak 0% on real names. The 5.8% digital misses are image-only-RPU headers → correctly routed to needs_human_review, NEVER wrong (no wrong-account risk). Vision path marked requires OPENROUTER_API_KEY (text+barcode measured on real; not faked). Committed: harness + synthetic fixtures + aggregate REAL_ACCURACY_RESULT.md only. Also fixed a PRE-EXISTING real-RPU leak in ground_truth_labels.json → scrubbed to synthetic.
