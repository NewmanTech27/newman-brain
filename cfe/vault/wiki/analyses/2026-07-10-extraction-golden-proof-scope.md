---
title: "Extraction Golden Proof — What It Covers and What It Does Not"
type: analysis
tags: [extraction, golden-test, scope, cfe-bill-parser, gate5]
created: 2026-07-10
updated: 2026-07-10
sources: [2026-06-08-cfe-bills-780881200029-fy25-26]
rpu: "780881200029"
status: vigente
---

# Extraction Golden Proof — What It Covers and What It Does Not

**Question:** On 2026-07-10 the sacred golden test passed (`18/18`, exit 0) on RPU 780881200029. Jesus needs the honest scope: passing one golden RPU is **not** the same claim as "extraction is flawless in production." This page draws that line precisely so the claim is not overstated.

**Proving command (re-run by Jesus himself):**
```
cd ~/cfe-brain/vault && ~/cfe-brain/.venv/bin/python tools/cfe_savings/test_golden.py
→ 18/18 checks passed   EXIT=0
```
Prerequisites now in place: local venv `~/cfe-brain/.venv` (`pdfplumber 0.11.10`, `openpyxl 3.1.5`); fixture `vault/raw/bills/780881200029/` (12 real GDMTH PDFs + `inputs.json`), gitignored so no real CFE PDF can be committed.

---

## (A) What the proof covers

**Exact code path exercised** (all in `vault/tools/cfe_savings/`):

1. `extract_folder(vault/raw/bills/780881200029/)` — `extract.py:265`. Globs `*.pdf` (`extract.py:271`), sorted, and calls `parse_bill` (`extract.py:76`) on each. **pdfplumber reads the 12 real bill PDFs** into structured per-month dicts (kWh by period, kW by period, importes MEM, bonif_FP, printed facturación, KWMax, etc.).
2. `run_scenarios(bills, sys, pv)` — `engine.py:154`. Runs PV-only / BESS-only / combined tariff+savings math.
3. Arithmetic validation `receipt_check` — `engine.py:63`: `(Σ importes + bonif_fp) × 1.16` vs the bill's printed `Facturación del Periodo` (the vault-canonical foot check, per [[2026-06-11-780881200029-calculadora-audit]] and the deterministic doctrine — **not** the plain `subtotal×1.16`).
4. `baseline_month` (`engine.py:54`) and `derive_rates` (`engine.py:29`) — distribución billed on `max(B,I,P)`, capped by umbral, **not** on printed KWMax ([[demanda-facturable]]).

**The 18 checks** (peso-exact tolerances): `bills count == 12`; baseline `$30,157,371`; kWh consumo `10,414,208`; PV gen `350,116`; BESS desc `670,200`; Bill ANTES `$30,157,371`; Bill DESPUÉS `$23,074,119`; Ahorro `$7,083,252`; Ahorro % `23.49%`; capacidad savings; arbitraje savings (weekday + punta-capped); bonif FP claw-back; the physics guard `disch ≤ punta kWh` every month; `FP penalty == 0`; `FP correction off by default`; and **3 distribución-basis checks** (months 4/10/12: billed on `max(B,I,P)`, and KWMax strictly greater — proving the engine ignores KWMax).

**The single subject:** RPU **780881200029**, tariff **GDMTH**, división **SIN (Peninsular)**, Cancún, Quintana Roo — a stable ~700k–1,000k kWh/month Grupo Posadas load, 12 monthly bills ([[2026-06-08-cfe-bills-780881200029-fy25-26]]). Fact tier: **engine-derived**, anchored to a **source-confirmed** audited reference ([[2026-06-11-780881200029-calculadora-audit]]).

---

## (B) What the proof does NOT cover

Be rigorous — none of the following is demonstrated by this passing test:

**1. One RPU, one bill layout.** The parse succeeds on exactly one CFE PDF template (GDMTH / SIN / this issuer). pdfplumber extraction is layout-sensitive; a different región's layout, a redesigned CFE template, or an older/newer format may break `parse_bill` silently or loudly. **Untested.** Note `extract_folder` also handles `*.xml` via `parse_bill_xml` (`extract.py:194`) — the **CFDI-XML path is NOT exercised** here (the fixture is PDFs).

**2. Happy path only.** Every one of the 12 PDFs is present, well-formed, and foots. The test never sees: a missing or corrupt PDF, a **nameless / needs-name** bill, an **image/OCR-scanned** bill, or a **bulk multi-RPU split** PDF. These are the real failure modes of intake, and none is covered.

**3. It tests extract→arithmetic→savings math, NOT the live production pipeline.** Untested by this test, entirely: WhatsApp intake (`supabase/functions/whatsapp-intake`), `pdf_intake` bulk-split, the DB work queue, the `cfe-collector` portal harvest (2captcha, WAF on app.cfe.mx, the >10-recibo block, Consulta exact-titular match), the design-engine, and the proposal-builder. This is a **local, offline extract+compute proof**, not an end-to-end production run.

**4. It does not touch the divergent live design-engine.** The proven engine is the **vault** engine (`cfe_savings`). The `newman-architecture/agents/design-engine/sizing.py` clean-room is a **different code path** that cannot even reproduce this RPU and is **still broken** per the backgrounded CTO finding — see [[2026-07-09-sizing-py-golden-ingest-materiality]] and [[2026-07-09-cleanroom-sizing-live-path-verified]]. This proof says nothing good about that path.

**5. No dashboard, no deploy, no auth.** `extraction.newman.re` is not built, not deployed, not gated. Nothing was deployed.

**Related live-pipeline gaps this test structurally cannot catch** (they live upstream of the clean local PDFs it starts from):
- [[needs-name-has-no-outbound-prompt-consumer]] — a nameless bulk PDF is a silent dead-end; sender promised a follow-up that never fires.
- [[pdf-intake-titular-extraction-fails-real-bill]] — real-bill titular extraction read the RPU but not the titular 3× on a live invoice; RPU-only rows can't reach CFE Consulta.
- Architecture frame: [[edge-function-maximalist]].

---

## The one-line honest claim (repeatable)

**Proven:** the vault savings engine extracts the 12 real GDMTH PDFs of golden RPU 780881200029 and reproduces the audited bill and savings to the peso (18/18, exit 0). **Not yet proven:** any other bill format or failure path, and the entire live production pipeline (WhatsApp intake → DB queue → CFE collection → design-engine → proposal/dashboard). **Extraction is proven for one RPU on one offline code path — not flawless in production.**

## Confidence
High. The proof is a deterministic, peso-exact, re-run-by-Jesus command; the scope boundaries are read directly from the code (`extract.py`, `engine.py`, `test_golden.py`) and from the backgrounded findings cited above.

## Sources consulted
- [[2026-06-08-cfe-bills-780881200029-fy25-26]]
- [[2026-06-11-780881200029-calculadora-audit]]
- [[needs-name-has-no-outbound-prompt-consumer]]
- [[pdf-intake-titular-extraction-fails-real-bill]]
- [[2026-07-09-sizing-py-golden-ingest-materiality]]
