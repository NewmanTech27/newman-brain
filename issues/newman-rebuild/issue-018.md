# #18: P2: extract.py XML CONSUMO period-split MISLABELED per division (DW inverted) — CONFIRMED vault engine bug

- State: OPEN
- Created: 2026-07-10T12:03:05Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/18

## Body

## The bug (CTO-confirmed against ground truth)
`cfe_savings/extract.py` `parse_bill_xml` maps CFDI CONSUMO fields as `CONSUMO1F=base, 2F=inter, 3F=punta` (comment claims "verified by EG* importes"). For **División DW (SIN Peninsular)** this is **inverted for base↔punta**.

**Evidence — RPU 780881200029, NOV 25, `WH-000552276133.xml`:**
- XML raw: `CONSUMO1F=104467`, `CONSUMO2F=440446`, `CONSUMO3F=268822`
- PDF-validated canonical split (wiki `2026-06-08-cfe-bills-780881200029-fy25-26.md`, peso-exact vs client Excel): base=268822, inter=440446, punta=104467
- Therefore actual: **CONSUMO1F = punta, CONSUMO2F = inter, CONSUMO3F = base** — opposite of extract.py for base/punta.
- Confirmed on 4/4 canonical-checked XMLs (harvest seat, PR #17). I re-verified CONSUMO1F=104467 / CONSUMO3F=268822 directly against the XML on this box.

This **refines** the old "CFDI has no split" claim: the split IS in the XML, but the CONSUMO→period mapping is wrong per-division-code. Fed to the engine, DW XMLs yield swapped base/punta — a garbage-in split, exactly the failure #5 exists to prevent.

## CTO ruling
**(a) Own tracked issue (this one), P2 hardening, GATED BEHIND golden CI #9.** Not folded into #5/#6. Rationale: this is a defect in the shared **vault/newman-brain engine**, not in harvest's wrapper — it must be fixed at the authority (charter §2: drive the engine, fix it at source, never fork a corrected copy in harvest). The fix touches billing-split physics, so per charter §3 it may NOT merge until the golden CI (#9) is green and this change reconciles peso-exact — the golden must catch any regression the fix introduces. Do NOT hand-patch the mapping in harvest.

**(b) PDF path is SAFE to build the engine (#7) on now — YES.** The PDF `parse_bill` path reads text-labeled "kWh base / intermedia / punta" from the Desglose del consumo — unambiguous, division-independent, and it is the path validated 18/18 peso-exact on the golden and 28/39-foot-clean on Yazaki. #7 proceeds on the PDF split. The **XML path stays quarantined** (not used as a split source) until this issue is fixed per-division-code and re-greened against the golden.

## Fix scope (when it enters, in newman-brain / vault)
- Map CONSUMO1F/2F/3F to base/inter/punta **by division code**, not a fixed order. Derive the per-division mapping from the EG*/importe fields (the current comment's method was wrong for DW) or a division→order table validated against PDF ground truth.
- Add the canonical XML-ordering assertion (already written in harvest `test_recibo_parser.py`) to the engine's own test suite.
- Must land through golden CI #9 green + peso-exact.

Refs: PR #17, #5 (parser), #6 (telemetry), #7 (sizing engine), #9 (golden CI).

## Comment by NewmanTech27 (2026-07-10T14:45:42Z)

**Fix delivered — PR NewmanTech27/cfe-brain#1** (the vault engine lives in cfe-brain, so the fix lands there; not merged, CTO gate).

- `extract.py` now maps CFDI `CONSUMO1F/2F/3F` → base/inter/punta **by division** via a `_CONSUMO_ORDER_BY_DIVISION` table. Default is the byte-verified CFE convention `(punta, inter, base)` — the old fixed `1F=base` was inverted base↔punta.
- **DW and DB byte-verified** (RPU 780881200029 PDF-canon 4/4; a real DB XML reconciles to CONSUMO_R). **DX (Jalisco) left on the default and flagged UNVERIFIED** — `consumo_order_verified(division)` exposes the distinction; its only prior "check" used a discredited method. Tracked as a follow-up.
- **Reconciliation guard:** if `1F+2F+3F != CONSUMO_R` it raises (unknown layout) rather than emitting a garbage split — unverified divisions fail LOUD, not silent.
- Regression test 14/14 (`test_consumo_period_mapping.py`), ported from harvest's canonical ordering assertion.
- **Golden CI unaffected / no re-pin:** `engine.js` (the pipeline + golden-CI engine) consumes pre-split `kwh_base/inter/punta` and never parses CONSUMO (0 grep hits) — the bug is Python-only. Billing-math files byte-untouched → the peso-exact anchor cannot move.
- Flagged (out of scope, no corruption): `DEMANDA1P/2P/3P` carry the same inversion but feed an order-invariant `max(B,I,P)` demand basis.

