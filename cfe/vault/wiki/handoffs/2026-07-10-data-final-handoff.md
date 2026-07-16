---
title: "Final handoff — agent data (supabase-devops) → newman-rebuild clean-room team"
type: analysis
service: supabase-devops
kind: finding
tags: [handoff, supabase-devops, gate-0, reconciliation, del-4, clean-room, final-drain]
created: 2026-07-10
updated: 2026-07-10
verified_against: "cfe-brain@0f01669; newman-architecture origin/dev@a81c43c, origin/main@74809d0, origin/staging@d28ae6b"
confidence: mixed (per-item marked below)
sources:
  - ".github/workflows/deploy-crm.yml (origin/dev) — on: push branches:[dev]"
  - ".github/workflows/deploy.yml + deploy-mini.yml (origin/main) — workflow_run after CI@main"
  - "agents/cfe-collector/main.py:864,871 — named vs nameless bulk-PDF branch"
  - "vault/wiki/supabase-devops/2026-07-10-multirepo-branch-audit.md"
  - "vault/wiki/supabase-devops/prod-only-drift-register.md"
  - "vault/wiki/supabase-devops/2026-07-09-gate0-reconciliation-report.md"
---

# Final handoff — agent data (supabase-devops)

Only what a successor **cannot** reconstruct from the repos + wiki. Everything else is in
[[2026-07-10-multirepo-branch-audit]], [[2026-07-09-gate0-reconciliation-report]],
[[prod-only-drift-register]]. Confidence marked per claim; **low = I never ran it myself**.

## 1. Traps documented nowhere

- **"Merge to main" ≠ deploy, and it's backwards from every other repo.** In `newman-architecture`
  the CRM ships from **`dev`** (`.github/workflows/deploy-crm.yml`, `on: push branches:[dev]`, exists
  on `dev` ONLY) → `tuesday.newman.re`; the cfe-collector ships from **`main`** (`deploy.yml` +
  `deploy-mini.yml`, `workflow_run` after CI@main) → newman-vps + mini. `newman-landing` also
  deploys from **`dev`** (`main` has no `deploy.yml`). A rebuild team that treats `main` as "the
  live truth" loses the entire CRM. **Confidence: high** (read the YAML triggers; did NOT curl the
  live URLs to confirm what is physically serving — that step is unverified, medium).
- **The freeze REVOKEs are invisible to `supabase migration list`.** 2026-07-09 11:47 UTC I revoked
  EXECUTE on `crm_web_send_proposal`, `crm_proposal_public`, `crm_sign_proposal` via `execute_sql`
  (runtime ACL, **no migration file, not in the ledger**). Any schema replay silently re-GRANTs them
  and re-opens the client-facing proposal path. They live only in [[prod-only-drift-register]].
  **Confidence: high** (I applied them).
- **The golden fixture is not in the knowledge base.** `raw/bills/780881200029/` is absent from the
  vault and permission-denied under `/home/mario/CFE Brain`. The "sacred" 18-check golden test
  (baseline $30,157,371) **cannot be run from git or the wiki by anyone but the operator on that one
  disk.** I never executed it. Every golden-divergence claim below is inherited, not re-run.
  **Confidence: high on inaccessibility; low on any downstream golden number.**
- **`claim_media` boolean=int bug is in `claim_media_atomic`, not migrations 014/015** (original
  misattribution). Fixed in prod ledger as `20260709124613`; the fix source file is uncommitted
  (another session's scratchpad). See [[2026-07-09-claim-media-boolean-bug-verified]].
- **Migration scheme is split across the fork.** `main` numbers `db/migrations/010–015`; `dev` uses
  timestamped `supabase/migrations/**` (75). Carrying one arm over is a re-home, not a `git mv`.

## 2. Work in flight (exact state)

- **`integration/gate0` @ `38ebff0`** in worktree `~/wt-gate0`: **+57 over origin/dev, UNPUSHED.**
  It authors the three prod-only reconciliation patches (016 claim_media, 017 bulk_pdf, freeze).
  **Next step was:** await Jesus's canonicity ruling on the dev/main fork → GATE 3 (execute
  reconciliation, make one clean `main`) → GATE 4 (dev/staging/prod + Supabase branching, costed
  first). Nothing was merged/reset/pushed — I was holding at the gate.
- **Four unpushed local branches** die with the box: `integration/gate0`, `spec/cfe-ppa-bess`,
  `spec/tuesday-inputs`, `spec/cfe-bill-parser`. Only `spec/supabase-devops` is on origin.
- **Prod patches owed to the canonical branch:** 3 freeze REVOKEs (ledger-invisible), 016
  `20260709124613`, 017 `20260709132040`. Standing register: [[prod-only-drift-register]].

## 3. Claims I made but never verified (honest)

- **"Prod DB is the hand-applied union of both arms" / "119-migration ledger" / "DEL-4 5/75."**
  Inherited from [[2026-07-09-gate0-reconciliation-report]] §4. I did **not** re-query the prod
  ledger in my 2026-07-10 audit. **Confidence: medium.**
- **`integration/gate0` "+104 over main, carries dev + reconciliation."** I verified commit
  **counts** only — never inspected what those 57 commits actually contain. **Confidence: low.**
- **finance.ts / sizing.py "silently overstate savings."** From CTO findings
  ([[2026-07-09-crmweb-finance-ts-diverges-client-facing]], [[2026-07-09-sizing-py-golden-ingest-materiality]]),
  not re-executed by me (fixture inaccessible). **Confidence: low that I personally proved it.**

## 4. The one thing the rebuild team will get wrong

They will **re-implement the billing math** in the new stack (TS / edge functions). It has already
happened twice — `crm-web/lib/finance.ts` and `design-engine/sizing.py` are both clean-room
re-writes and **both silently diverge from RPU 780881200029 and net-OVERSTATE savings** (a rep
could sign a losing deal). `tools/calc_core.py` is the **only** engine golden-anchored to the
sacred RPU. **Wrap it as a called worker; never port it.** And before decommissioning prod
`bwudgrwfwjdbvqhgbwty`, **dump its live schema + ACLs** (including the ledger-invisible freeze
REVOKEs) — git cannot rebuild it (DEL-4), so the reconciliation truth dies with the old project if
nobody exports it. See [[edge-function-maximalist]]: edge-for-glue, python-engine-authoritative.
