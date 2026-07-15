# Committee audit and fix loop across 11 NewmanTech27 repos

**Summary**: A 7-expert committee scored all 11 NewmanTech27 repos, then multiple fix rounds on a committee-fixes branch added tests, CI, and hardening, re-scoring toward a 9.5/10 target.
**Tags**: #newman #agents #code-quality #ci #cfe
**Created**: 2026-07-03
**Source**: macbook session f5953d57-d81f-4dac-bed4-2f141ffc013c.jsonl, user jesus

---

## Content
- Confirmed tech@newman.re = the NewmanTech27 GitHub account (11 private repos), then convened a committee of experts (tech, marketing, energy, law/regulation) to assess repo content quality.
- Round-1 verdict: code small, readable, well-commented (real gotchas documented: WAF workarounds, division-casing, NULL-in-unique-index) but "one person's laptop-shaped estate" — only 2/11 repos had CI, tests in 2 places (one depending on a /tmp fixture), hardcoded personal paths/nix hashes, duplicated truths (tariff data, brand CSS, tariff API) across repos.
- Fix round 1 (committee-fixes branch): README/reality drift fixed (10 dirs, 21-agent flock documented), real Sept-2025 CFE PDF committed as test fixture, CI workflows added, health_sweep psql from PATH.
- Fix round 2: `test_savings.py` with 12 tests pinning ppa_vs_cfe; usuario calificado eligibility gate added (QUALIFIED_USER_MIN_KW=1000, Spanish note routing <1 MW clients to aggregation/on-site DG).
- Fix round 3: rate-limiter hard cap in newman-data-api (`_MAX_TRACKED_CLIENTS`, deliberate fail-open documented + test-pinned), dep pinning, atomic manifest writes.
- Re-scores confirmed the fixes were "real, not cosmetic" — all suites executed locally green; residuals were polish-level drift. Session ended hitting the usage limit mid round-3 scoring.

## Related Notes
- [[2026-07-02-agent-org-restructure-fibrahotel]]
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
