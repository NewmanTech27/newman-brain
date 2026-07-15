# Overnight Flock Run: Golden Extraction Proof (18/18), sizing.py Fix, Org-Wide Drain

**Summary**: After the reboot, the relaunched seven-session flock proved extraction end-to-end on golden RPU 780881200029 (test_golden.py 18/18 exit 0), fixed sizing.py by delegating to the golden engine, and executed a synchronized wiki drain — each agent leaving one sentence for the rebuild team.
**Tags**: #newman #agent-org #cfe-brain #golden-test #sizing #handoff
**Created**: 2026-07-10
**Source**: newman-vps sessions (consolidated, all user jesus, dir -home-jesus-cfe-brain): 5d578eaf (ceo), dbda3534 (cto), 5efd6e5c (cfe), a9a07f56 (ppa), 9b082c4d (data), b1590b21 (tuesday), 91e173ce (research)

---

## Content
- Board directive: VPS reboot killed the flock; all seven sessions relaunched. CEO collected readiness, published org chart, and Jesus authorized the GATE-0 branch audit (read-only, git fetch first; newman-architecture dev+102/main+55 is a fork not drift).
- MAIN EFFORT override: cfe seat made sole priority — extraction must run flawlessly end-to-end on golden RPU 780881200029, proven by a command exiting 0.
- Baseline blockers: pdfplumber missing (venv provisioned with pdfplumber>=0.11 + openpyxl>=3.1) and the golden fixture Jesus-only under /home/mario. Critical pre-fix: vault/raw/bills/ was NOT gitignored — `vault/raw/` line added and verified with git check-ignore before any real PDF touched the tree.
- Fixture landed via Jesus-authorized sudo copy to `vault/raw/bills/780881200029/` (12 PDFs + inputs.json, gitignored). Proof: `~/cfe-brain/.venv/bin/python vault/tools/cfe_savings/test_golden.py` → 18/18, exit 0, independently re-run by Jesus. Peso anchors: $30,157,371 baseline / $7,083,252 Ahorro / 23.5%.
- Scope honesty forced: the green exercises vault/tools/cfe_savings only — 1 RPU, 1 layout, happy path; NOT the live pipeline (WhatsApp intake, work queue, design-engine, proposal-builder) and NOT sizing.py. Coverage-scope page written.
- sizing.py fix (ppa, background, CTO-gated via verdict log CTO-V-001/002 on wt-cfe-ppa-bess off dev): step 1 commit 1253b6b = golden_engine.py bridge + removed test_sizing.py:50-68 (which PINNED the inverted PV→BESS behavior) + test_sizing_golden.py (3/3); step 2A commit 4a2f319 = sizing.optimize delegates to optimize_sizing.sweep/calc_core, divergent inline physics removed, test_sizing_integration.py 14/14 incl. refuse-guards for collapsed CFDI blobs.
- Input-mapping wall finding: CFDI XML has NO base/intermedio/punta split — enrich.py:349 dumps the CFDI total into kwh_base, so feeding the golden engine from the pipeline is GIGO until the recibo PDF's "Desglose del consumo" is captured. Option A chosen: fix physics + refuse-on-bad-input guard; do NOT rewire main.py live until horaria capture exists.
- Drain (~/drain.md / ~/flock_drain.md): every agent wrote a final handoff page under vault/wiki/handoffs/ and pushed; shared-tree race — CTO's `git add -A` commit 0114a269 swept all siblings' pages (research pushed separately as f2760bd); integrity_check exits 1 only on the 10 pre-existing 2026-06-04 gaps.
- Rebuild-team one-liners worth keeping: only `vault/tools/calc_core.py` is authoritative (both finance.ts and sizing.py silently overstate savings; wrap, never rewrite); prod bwudgrwfwjdbvqhgbwty cannot be rebuilt from git (DEL-4 5/75) — dump live schema + ACLs incl. ledger-invisible freeze REVOKEs before dropping it; the golden fixture is gitignored real PII on one disk so a fresh clone FileNotFoundErrors and the peso anchor must travel out-of-band; ~/newman-sso dies with the box and validates email suffix instead of the Google `hd` claim; capture the recibo horaria split or the engine is GIGO.
- CEO's five analysis pages committed at 3ba0f054: reset-vs-merge-hazard, design-engine-live-or-orphan, the-58-designs, tonight-sizing-fix, single-disk-risks.

## Related Notes
- [[2026-07-09-vps-reboot-cleanup]]
- [[2026-07-09-sizing-materiality]]
- [[2026-07-10-newman-rebuild-seat-org]]
- [[cfe-brain-vault]]
