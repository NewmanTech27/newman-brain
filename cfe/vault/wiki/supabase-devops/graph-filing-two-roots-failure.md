---
title: Filed graph pages read as "phantom" — two wiki roots + shared-repo commit-sweeping
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, process, integrity, lint]
created: 2026-07-09
updated: 2026-07-09
sources: ["CEO review 2026-07-09", "vault/tools/integrity_check.py (INT-2)", "git log 167a860", "prompts/_common.md Phase -1 vs Phase 5"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Filed graph pages read as "phantom" — two wiki roots + shared-repo commit-sweeping

## Symptom
This session's Phase-5 report said it filed three pages (`canonicity-prod-is-truth`,
`main-dev-fork`, `migration-git-prod-drift`) and logged them. Review reported them
non-existent, and the enforced `INT-2` check (`vault/tools/integrity_check.py`) exited 1
naming all three. The pages *had* been written — but under `~/cfe-brain/wiki/<service>/`
(the engineering-wiki root in `~/cfe-brain/CLAUDE.md`), while `INT-2` and the reviewers
look under `~/cfe-brain/vault/wiki/`. Same repo, two wiki roots, two schemas. "Filed" was
true for the wrong root, which for provenance purposes is indistinguishable from not
filed at all.

## Two independent root causes

**1. Two wiki roots, one repo.**
- Engineering: `~/cfe-brain/wiki/<service>/`, schema `~/cfe-brain/CLAUDE.md`, `kind:`
  frontmatter — where `_common.md` §Phase 5 sends "feed the graph."
- Vault: `~/cfe-brain/vault/wiki/…`, schema `~/cfe-brain/vault/CLAUDE.md`, `type:`
  frontmatter — where `_common.md` §Phase -1 sends you to read, and where `INT-2`
  enforces. **`INT-2` (`vault/tools/integrity_check.py`) is the tie-breaker: the canonical
  graph root is `vault/wiki/`.** Pages filed under the engineering root are invisible to
  it.

**2. Shared-repo commit-sweeping.**
`~/cfe-brain` is one git repo shared by all sessions. A sibling's `git add -A && git
commit` (`167a860`) swept this session's uncommitted pages into an unrelated commit while
the `log.md` row stayed a working-tree change — so `git status` showed "only log.md
changed," reinforcing the false "logged an artifact it never wrote" reading.

## Resolution applied
- Wrote all three pages (real content) under `~/cfe-brain/vault/wiki/supabase-devops/`;
  verified each with `ls` and re-ran `INT-2` to exit 0 before re-asserting.
- Canonical root for engineering findings is now taken to be `vault/wiki/` (INT-2's
  domain). The engineering-root copies are duplicates pending a consolidation decision.

## Standing rules adopted
- **Never re-assert a filed artifact without `ls` / `git cat-file` proof in the same turn**,
  and prefer running `INT-2` as the proof.
- A `log.md` "pages created" entry is a promise checked by `INT-2`; write the page under
  `vault/wiki/` **before** logging it.
- `INT-2` already gates on log-vs-disk. Worth adding: flag a page that exists under the
  engineering root but not under `vault/wiki/` (this exact case), and flag a `log.md` row
  committed with no matching page in the same commit (the sweep signature).
