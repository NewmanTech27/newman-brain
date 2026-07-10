---
title: "Final Handoff — cfe-bill-parser (extraction)"
type: analysis
kind: handoff
tags: [handoff, extraction, cfe-bill-parser, golden-test, rebuild]
created: 2026-07-10
updated: 2026-07-10
verified_against: 0f0166911bd23efd416a0f5bec09e00a671c2512
confidence: high (except where marked)
sources:
  - "vault/tools/cfe_savings/test_golden.py:19-20,28 (fixture path hardcoded)"
  - "vault/tools/cfe_savings/README.md:54-56 (stale golden numbers)"
  - "vault/tools/cfe_savings/requirements.txt:1-2 (deps)"
  - "newman-architecture/agents/cfe-collector/main.py:847,864,871 (enqueue/needs_name)"
---

# Final Handoff — cfe-bill-parser (extraction)

Owner of Charter Outcome 2: RPU invoice extraction + `extraction.newman.re`. Retiring. Only what a successor could NOT reconstruct from repos + wiki follows.

## The one thing the rebuild WILL get wrong if nobody says it
**The sacred golden test is NOT self-contained. Its fixture exists on exactly one operator's disk and is gitignored — a fresh clone cannot run it.** `test_golden.py:19-20` hardcodes `FOLDER = <vault>/raw/bills/780881200029`; `.gitignore` now excludes `vault/raw/` (real CFE PDFs = client PII, must never be tracked). The 12 real GDMTH PDFs + `inputs.json` were sudo-copied by Jesus from `/home/mario/CFE Brain/raw/bills/780881200029/` (mode `drwxr-x---`, unreadable to every agent). On any new machine the test dies with `FileNotFoundError`. **Risk: the rebuild team re-baselines the golden numbers against whatever they *can* reproduce, silently corrupting the peso-exact anchor.** The fixture must travel out-of-band, encrypted, with provenance — it is not in git and never will be.

## Traps documented nowhere (with evidence)
1. **Two divergent "golden" numbers.** `README.md:54-56` still advertises the PRE-rebaseline figures — Ahorro **$7,593,969 / 25.2%**, BESS desc **1,009,362 kWh**. The live test (`test_golden.py:42-44`) asserts the CORRECTED **$7,083,252 / 23.5%**, BESS desc **670,200 kWh** (2026-06-11 arbitrage/bonif rebaseline, [[2026-06-11-780881200029-calculadora-audit]]). A successor trusting the README chases a dead number. The README is stale; the test is truth.
2. **Two engines, same name, opposite trust.** The VAULT engine `vault/tools/cfe_savings` is golden/peso-exact. The clean-room `newman-architecture/agents/design-engine/sizing.py` is a *different* code path that dropped the umbral, inverted PV→BESS coupling, and never touches RPU 780881200029 — it OVERSTATES savings. Do not conflate. Rebuild the calculator by WRAPPING the vault engine, never porting sizing.py. [[2026-07-09-sizing-py-golden-ingest-materiality]], [[2026-07-09-cleanroom-sizing-live-path-verified]].
3. **Engine needs deps not in system python.** `pdfplumber>=0.11` + `openpyxl>=3.1` (`requirements.txt`). Box python3 (3.12.3) has neither; I made a gitignored `~/cfe-brain/.venv`. No venv is committed — expect ModuleNotFoundError before FileNotFoundError on first run.
4. **The vault engine validates on `(Σ importes + bonif_FP)×1.16`, NOT `subtotal×1.16`** (`engine.py:63`). My role prompt gave the wrong formula; the vault won. Don't reintroduce the plain-subtotal check.

## Work in flight — exact state
- **My Phase-1 spec was NEVER delivered.** Branch `spec/cfe-bill-parser` exists (worktree `~/newman-architecture` @ `a81c43c`) but `docs/specs/cfe-bill-parser.md` does not exist in the tree or in `git log --all` for that path. Treat the spec as unstarted. Next step was Phase 0→1: prove ONE real RPU intake→stored→arithmetic-checked, then write Part A/B/C.
- **Proven this session:** extraction of the 12 golden PDFs → engine → 18/18 peso-exact, exit 0. Scope boundaries: [[2026-07-10-extraction-golden-proof-scope]].

## Claims I made but did NOT verify (honest)
- **I never watched the golden test PASS myself** — I reproduced only the two FAILURE modes (import, fixture). The 18/18 pass was Jesus's run, reported to me. *Confidence on the pass: medium (second-hand).*
- **The reported CFE-portal gotchas are still UNVERIFIED against code**: exact `receptor_nombre` match, PDF bulk-split, `ASSIGNED_ELSEWHERE`/Consulta drain, 2captcha + WAF, the >10-recibo block, and whether the mac-mini `pg_cron` drain dependency still exists/is healthy. I never confirmed any. *Confidence: low.*
- My findings [[needs-name-has-no-outbound-prompt-consumer]] and [[pdf-intake-titular-extraction-fails-real-bill]] are from READING code (`main.py:847/864/871`), not a live re-run. The defects are real in the code; whether current prod still behaves so is unretested. *Confidence: medium.*

## For the rebuild, concretely
Extraction works today for ONE RPU / GDMTH / SIN on ONE offline path. Untested: every other CFE layout, the CFDI-XML branch (`extract.py:194`), all failure paths, and the entire live pipeline (WhatsApp intake → DB queue → cfe-collector → design-engine → proposal/dashboard). Prove a real RPU end-to-end before building any dashboard. Never deploy `extraction.newman.re` unauthenticated — client RPUs/invoices behind the `newman.re` `hd` gate, server-side.
