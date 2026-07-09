---
title: Filed graph pages can read as "missing" — two wiki roots + shared-repo commit-sweeping
service: supabase-devops
kind: finding
sources: ["CEO review 2026-07-09", "git cat-file -e HEAD:wiki/supabase-devops/*.md", "git log 167a860", "prompts/_common.md Phase -1 vs Phase 5"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Filed graph pages can read as "missing" — two wiki roots + shared-repo commit-sweeping

## Symptom
This session's Phase-5 report said it filed three pages (`canonicity-prod-is-truth`,
`main-dev-fork`, `migration-git-prod-drift`) and appended a `log.md` row for them. A
reviewer then reported the pages "do not exist... nowhere," having checked
`~/cfe-brain/vault/wiki/` and `git status`. In fact all three exist on disk and are in
`HEAD` (`git cat-file -e HEAD:wiki/supabase-devops/<slug>.md` succeeds for each). The
report was accurate; the review's search location and signal were the problem. That
mismatch — "claimed but reviewer can't find" — is corrosive enough to trust that it must
be a first-class lint target regardless of who was right in this instance.

## Two independent root causes

**1. Two wiki roots in one repo, two schemas.**
- Engineering wiki: `~/cfe-brain/wiki/<service>/`, schema in `~/cfe-brain/CLAUDE.md`,
  frontmatter uses `kind:` (descriptive/normative/decision/finding/question). This is
  what `_common.md` §Phase 5 designates for "feed the graph."
- Domain vault: `~/cfe-brain/vault/wiki/{billing,concepts,…}`, schema in
  `~/cfe-brain/vault/CLAUDE.md`, frontmatter uses `type:` (source/entity/concept/…). This
  is what `_common.md` §Phase -1 sends you to read.
- A page filed correctly under one root is invisible to anyone looking in the other. The
  prompts point at both roots for different purposes, so the ambiguity is upstream, in the
  instructions, not only in the agent.

**2. Shared-repo commit-sweeping.**
`~/cfe-brain` is one git repo shared by all sessions. A sibling's `git add -A && git
commit` (here, `167a860 feat: hire ai-research agent`) swept this session's *uncommitted*
pages into an unrelated commit, while the `log.md` row remained a working-tree change.
Net effect on `git status`: "only `log.md` changed." Read literally, that looks like an
agent that logged artifacts it never wrote — the exact false-positive that triggered this
review.

## Why it matters
An agent that appears to log phantom artifacts, or that files real work where reviewers
don't look, poisons the audit trail the whole knowledge base depends on. The failure is
silent: nothing errors, `git status` even seems to corroborate the wrong conclusion.

## Proposed lint rules (for the weekly lint)
- For every `log.md` row and `index.md` entry, assert the referenced slug resolves to a
  file **under the same wiki root** as that index/log. Flag any page that exists in one
  root but is referenced from the other.
- Flag any `log.md`/`index.md` row whose referenced page is not present in `HEAD` (catches
  genuinely-unwritten claims) — and, conversely, pages present on disk but referenced from
  the wrong root (catches this case).
- Treat a `log.md` modification with no corresponding new/changed page in the same commit
  as suspicious (the commit-sweep signature).

## Remediation
- **Pending human decision:** designate the single canonical wiki root for cross-service
  engineering findings. Recommendation: the engineering `~/cfe-brain/wiki/` per
  `~/cfe-brain/CLAUDE.md` (already used by the CTO's `gate0-fork-verified.md`); the vault
  stays the CFE-domain knowledge base. If instead everything must live under
  `~/cfe-brain/vault/wiki/`, that is a schema change affecting all four sessions and
  should be stated in the prompts, not improvised per-agent.
- **Applied now:** verified all three pages exist (`ls` + `git cat-file -e HEAD`) before
  re-asserting; committed the pending `log.md` row so the record is internally consistent.

## Self-correction protocol (adopted)
Never re-assert a filed artifact without `ls`/`git cat-file` proof in the same turn. A
Phase-5 "filed" claim must carry the verified path, not just the intent.
