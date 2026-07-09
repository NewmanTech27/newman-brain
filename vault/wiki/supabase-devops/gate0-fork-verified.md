---
title: GATE 0 fork — independently verified by CTO
service: supabase-devops
kind: finding
sources: ["git rev-list origin/main..origin/dev", "git ls-tree origin/main", "commit a81c43c"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# GATE 0 fork — independently verified by CTO

The branch audit `supabase-devops` reported is real, not asserted. On 2026-07-09 the CTO
fetched all refs and re-derived every number directly, rather than trust the pane. All three
core claims hold.

## Verified facts

- **Bidirectional divergence.** `origin/dev` is **102 commits ahead** of `origin/main`;
  `origin/main` is **55 commits ahead** of `origin/dev`. Both directions non-zero — this is a
  fork, not drift. (`git rev-list --count origin/main..origin/dev` = 102;
  `origin/dev..origin/main` = 55.)
- **Stranded file.** `docs/cfe-collection.md` exists on `origin/main` only — present in
  `git ls-tree origin/main`, absent from `origin/dev`. It documents the CFE collector flow
  (WhatsApp → edge fn → mini harvest → `client.bill`) and would be lost by a naive
  dev-wins merge.
- **Two migration ledgers, not a superset.** `origin/main` carries **16** SQL migrations;
  `origin/dev` carries **85**. Different sets. Neither branch's ledger is a superset of the
  other's.

## Why this is a finding, not just a status note

Prod DB is the **hand-applied union** of both ledgers (supabase-devops reports ~117 applied
migrations; Jesus's ruling: prod DB = truth, git reconciles to it). The consequence:
**neither git branch is a replayable description of the live database.** No `supabase db reset`
or native-branch rebuild currently reproduces prod from scratch.

This is the single biggest risk to a clean `main`. It is invisible next to the visible fork:
even after the branches are unified, GATE 4 (Supabase native branching) will rebuild
environments from git, and if the reconstructed migration lineage does not faithfully replay
to the current prod schema, environments diverge from prod silently. The golden test does not
guard this — it covers the savings engine, not the schema.

## What GATE 0 still owes before it is "landed"

Diagnosis is done. The written reconciliation report the charter requires is not filed yet.
It must show, with evidence: what is on each side, what is actually deployed, dead vs live,
every stranded file (`cfe-collection.md` is one — what else?), and a replayable path from a
clean git checkout to the current prod schema. Until that path exists and is proven, GATE 3
(clean main) cannot be signed off.

## Related

- [[gate0-reconciliation-report]] — the report supabase-devops still owes (not yet written)
