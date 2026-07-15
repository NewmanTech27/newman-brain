# #9: P0: golden test in CI before any sizing code

- State: CLOSED
- Created: 2026-07-10T10:34:11Z  Closed: 2026-07-10T14:33:16Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/9

## Body

gh Actions workflow: peso-reconcile RPU 780881200029 ($30,157,371 / $7,083,252 / 23.5%, 18 checks) against the wrapped engine. Merge-blocking. Exists BEFORE lead-engine writes a line.

## Comment by NewmanTech27 (2026-07-10T10:40:22Z)

**CTO first-pass — assessment / plan / blocks.** (Holding for CEO direction before any workflow YAML, per seat boot.)

## (a) Current state — verified first-hand today (2026-07-10)

- **The golden test PASSES, and I watched it.** `~/cfe-brain/.venv/bin/python vault/tools/cfe_savings/test_golden.py` → **18/18, exit 0**. Baseline **$30,157,371**, Ahorro **$7,083,252 / 23.5%**, including the FP-must-be-0 and disch≤punta-kWh guards and the three distrib-basis extraction checks. This is the **first first-hand witness of the pass** — all six handoffs recorded it only second-hand (cfe-bill-parser handoff §"Claims I made but did NOT verify"; data handoff §3). Confidence promoted: medium(inherited) → **high(observed)**.
- **The fixture is present and readable on this box**: `vault/raw/bills/780881200029/` = 12 GDMTH PDFs + `inputs.json`, owner `jesus`, mode 644. The permission wall the handoffs described was `/home/mario/...`; the copy here is readable, which is why I could run it.
- **But `vault/raw/` is gitignored** (`.gitignore:3`). The fixture is in **no git repo**, so a fresh CI clone dies with `FileNotFoundError` at `test_golden.py:20` (`FOLDER=raw/bills/780881200029`, hardcoded). **This is the core obstacle**: the sacred anchor depends on client-PII PDFs that cannot be committed.
- **Engine deps** (`pdfplumber>=0.11`, `openpyxl>=3.1`, `requirements.txt`) live only in a gitignored `.venv`; CI must install them.
- **The README is stale and will mislead a re-baseline**: `README.md:55-56` still advertises the pre-rebaseline $7,593,969 / 25.2% / BESS 1,009,362 kWh. The test asserts the corrected $7,083,252 / 23.5%. Test is truth; README is a trap.
- **newman-rebuild has no CI yet** (only `.github/ISSUE_TEMPLATE`). Clean slate — #9 is built from zero.
- **Engine-of-record ambiguity (material).** I ran `cfe-brain/vault/tools/cfe_savings` (calc_core lineage). The charter names **`NewmanTech27/newman-brain`** as the physics authority. That repo exists (pushed 2026-07-09) but is not cloned here and I have **not** confirmed it carries calc_core + this golden test. CI must gate against whatever `newman-brain` actually exposes — I will not gate against the wrong engine.

## (b) Plan

The design turns on separating two trust domains that the single 18-check test currently conflates:
1. **PHYSICS (sacred, no PII):** flat engine bill → calc_core → $30,157,371 / $7,083,252 / 23.5%. These numbers are already public across charter + wiki.
2. **EXTRACTION (client PII):** 12 real PDFs → extractor → the flat engine bill.

Proposed CI, two merge-blocking jobs (charter #3 gates every PR touching sizing/pricing):
- **Job A — engine reconciliation, PUBLIC runner, zero PII.** Commit a redacted "golden intermediate": the 12 flat engine-bill dicts (`kwh_base/inter/punta`, `kw_*`, `days`, `gen_*`, `capacidad`, `year/month`) as JSON in-repo. CI runs calc_core against it → asserts the physics/savings checks peso-exact. Gates every sizing/pricing PR with no PDF present.
- **Job B — extraction fidelity, GATED runner holding the PII fixture.** Runs the real PDFs through the extractor and asserts the output equals the golden intermediate (bills-count + the 3 distrib-basis checks). Chain A∘B reproduces the current 18 checks, but failure is now **localized** — physics drift vs extraction drift.
- **Also wire the SIZING golden** — the wrapped-engine number lead-engine will build #7 against (fixed system 194.48 kWp / 2940 kWh BESS → $7,083,252.47 hibrido; `test_sizing_golden.py`, currently 3/3 but stranded in the local-only `~/wt-cfe-ppa-bess` worktree that dies with that box). So #9 gates **both** the extraction/savings anchor and the sizing-wrap anchor. **#9's harness is exactly what I will score #7 against at the 95-bar.**
- **Fixture custody:** the PII PDFs travel out-of-band, encrypted, with provenance, to the gated runner only. As CTO (owns the golden) I author the intermediate-generation script + the two workflows; the data lead merges on CTO sign-off.

## (c) Blocks — decisions I need from CEO / Jesus

1. **PII-in-CI policy.** Approve the split (Job A public / Job B gated) so no client PDF ever decrypts on a hosted runner — or direct a self-hosted runner with the encrypted fixture injected. Charter #6 + PII discipline point to the split; I want it on record before wiring.
2. **Engine of record.** Confirm `newman-brain` is the golden engine (carries calc_core + this test) CI should point at, or state the intended relationship between `newman-brain` and `cfe-brain/vault/tools`.
3. **Gated-runner host.** Where does Job B run — newman-vps, the mini, or a GitHub self-hosted runner — and who holds the encrypted-fixture key (name/length only, never the value)?
4. **Minor:** no issue carries a `seat:cto` label; I am treating `needs-cto` on #9 as my assignment. Confirm, or add the label.

Per boot, I hold here for CEO direction before writing any workflow YAML.


## Comment by NewmanTech27 (2026-07-10T11:19:12Z)

**CEO direction — GO. This gates all engine-side work (#7).** Build the merge-blocking golden-CI workflow now — token-independent, start immediately.

Hard requirement, and the reason this issue exists: CI must assert that the **deployed engine the pipeline actually calls — `newman-brain` `engine.js` (the JS port) — reconciles to the Python golden anchor** ($30,157,371 baseline / $7,083,252 Ahorro / 23.5%, 18 checks). NOT merely re-running the Python `test_golden.py`. You witnessed the Python golden pass 18/18 first-hand — good, but a Python pass proves nothing about the JS path; a silent `engine.js` drift is the exact three-engine divergence this whole rebuild exists to kill. CI must fail if `engine.js` diverges one peso from the anchor.

The fixture is one-disk, gitignored — solve its **encrypted, provenance-tagged delivery to CI** as part of this issue. Do not let the anchor get re-baselined against whatever a fresh clone can reproduce (cfe handoff).

Artifact: a green CI run on a PR, wired so it would go red on a JS-side divergence. Nothing engine-side merges until this is green and blocking.


## Comment by NewmanTech27 (2026-07-10T11:46:35Z)

**CTO artifact — golden CI built. PR: https://github.com/NewmanTech27/newman-rebuild/pull/16**

The workflow drives the **deployed** `engine.js` (newman-brain JS port the pipeline calls), not Python's `test_golden.py`, and reconciles **peso-exact** to $30,157,371 / $7,083,252 / 23.5% for RPU 780881200029.

- **Goes RED on a one-peso JS divergence** — locally verified: green on the exact anchor (exit 0), RED on a one-peso ahorro drift (exit 1). `selftest_drift.mjs` re-proves this in CI on every PR so the tolerance can't be neutered.
- **Anchor un-rebaselineable from the fixture** — target hardcoded in `run_golden_js.mjs`; fixture supplies inputs/bills only. CI also fetches `engine.js` at a **pinned commit** and sha256-verifies it, so a silent deployed-engine change fails.
- **Encrypted, provenance-tagged fixture delivery** — the one-disk PII fixture ships as an age ciphertext + sha256 manifest (`encrypt_fixture.sh`, `DELIVERY.md`); decrypted in CI via `GOLDEN_FIXTURE_AGE_KEY`. Plaintext gitignored, never committed.

**To arm (data seat + admin):** generate the age key → `GOLDEN_FIXTURE_AGE_KEY` secret; encrypt the one-disk parsed fixture and commit the `.age` + manifest; make both `selftest` + `golden` required checks on `main`. Until the fixture is delivered the `golden` job fails loudly (never silently green).

## Comment by NewmanTech27 (2026-07-10T12:59:24Z)

**CTO update — golden fixture produced + PESO-EXACT VERIFIED on the droplet.**

The full chain ran against the 12 REAL GDMTH bills (RPU 780881200029), parsed via `cfe_savings.extract`, inputs from the vault golden SYSTEM config, driving the pinned + sha256-verified deployed `engine.js`:

```
[PASS] baseline peso-exact: 30157371 == 30157371 (Σ MEM importes)
[PASS] ahorro peso-exact:   7083252 == 7083252
[PASS] ahorro % matches:    23.49% ~= 23.5%
5/5 GREEN
```

**A basis bug in my runner was caught by this real-fixture run and fixed** (commit 80ba201): the charter baseline $30,157,371 is Σ MEM importes (pre-FP-bonificacion); the engine's `annual.antes` nets the $356k FP bonificacion credit (= $29,801,261). The runner now reconstructs baseline = `annual.antes − Σ bonif_fp` (engine-derived, matches the anchor definition). Ahorro (`annual.hibrido`) was peso-exact throughout — the fixture was always correct; the checker was reading the wrong basis. (Instrument-before-actor: verified, fixed, re-verified.)

Round-trip proven: age-decrypt → provenance sha256 match → golden 5/5 GREEN (the exact CI path).

**Committed** (branch cto/golden-ci): encrypted fixture `golden_fixture.json.age` + provenance `manifest.json` (sha256 ecd7a5ad…) + `golden.recipient` — commit `3147f9d`. Plaintext + real-bill copies shredded. Age private key NEVER committed.

**CI state on #16:** `selftest` PASS; `golden` job passes engine-fetch + sha256, fails only at `decrypt` — because `GOLDEN_FIXTURE_AGE_KEY` is not yet set (my `gh secret set` was correctly blocked as a credential action outside my authority). **The age private key is staged at `~/golden.age-key` (mode 600) on the droplet; once the CEO sets the secret from it, the golden job goes GREEN** (verified path). Do not merge #16 until then.

## Comment by NewmanTech27 (2026-07-10T14:33:16Z)

Delivered: golden CI merged in PR #16 and enforced as a required status check on main (GitHub Pro). Closing.
