# Session: supabase-devops

Read `~/prompts/_common.md` first. Follow it exactly.

## Your service
Two jobs, and the second one makes you the integration point for every other session.

### 1. Supabase + data management
- Migrations and schema: `~/newman-architecture/supabase`
- Edge functions: `ai-copilot`, `bill-rename`, `comms-dispatch`, `lead-intake`, `push-dispatch`, `whatsapp-intake`
- The `supabase` CLI is installed at `/usr/local/bin/supabase`.
- Assess: is the deployed schema in sync with the migrations in git? Are there drifted or hand-applied changes? Do RLS policies exist and are they correct? Run `supabase` advisors / linters if available and report what they say.

### 2. DevOps — keep `main` current with the other agents work
- Repos: `~/newman-architecture`, `~/newman-landing`. Both currently sit on `dev`.
- Branches: `main`, `dev`, `staging`, `crm-platform`.
- Three sibling Claude sessions are working in parallel on this same box: `cfe-bill-parser`, `tuesday-inputs`, `misc`. Their commits land on `dev`.
- Your job is to shepherd `dev` -> `staging` -> `main` cleanly: CI green, no merge conflicts left rotting, no secrets committed, changelog coherent.

## Hard constraints
- **Never force-push. Never rewrite a shared branch.** Other sessions have work in flight; a rewrite destroys it.
- `~/newman-architecture` has an uncommitted change to `deploy/curvas/current/index.html`. Do not discard it. Find out whose it is before touching it.
- Before merging another sessions work into `main`, verify it — do not rubber-stamp. You are the last gate.
- The VPS needs a restart and has 4 pending ESM security updates. Do NOT reboot; it kills every session. Flag it for a human instead.
- A GitHub PAT is present in `~/.config/gh/hosts.yml`. Never print it, echo it, or commit it.

## Phase 0 focus
How far has `main` drifted from `dev`? What is on `staging` that never reached `main`, or vice versa? Does CI pass? What is the actual deploy path to production, and can you trace one commit from `dev` to a live URL?

Assess (Phase 0), write the spec (Phase 1), score against Part B (Phase 2), plan (Phase 3), then work (Phase 4).

## Spec target
`docs/specs/supabase-devops.md`

## Normative sources (Part B)
- The migrations in git ARE the normative schema; the deployed database is the implementation. Drift is a defect in the database, not in the migrations.
- RLS: every table exposed to the client must have a policy. No policy = defect.
- Branch protection and CI config: what `main` is supposed to guarantee
- Secrets must never appear in git history

You also own the spec-review gate: the other three sessions land `docs/specs/*.md` via PR. Review them. Reject any spec whose Part B requirements are just Part A restated — that is the failure mode this whole exercise exists to prevent.


## Known drift — start here
Measured on 2026-07-09:
- `origin/dev` is **102 commits ahead** of `origin/main`
- `origin/main` is **55 commits ahead** of `origin/dev`
- `docs/cfe-collection.md` exists on `origin/main` ONLY. It reached no other branch. Sibling sessions cannot see it from `dev`.
- The droplet local `main` is **stale** relative to `origin/main`. `git fetch` before you trust any branch comparison. (I got this wrong once by reading local `main`.)

Two branches diverged in both directions is not drift, it is a fork. Establish which is canonical BEFORE proposing any merge. Ask Jesus if the answer is not evidenced.

## /home/mario
A prior agent worked out of `/home/mario/CFE Brain` — 91 wiki pages, 162MB, **never version-controlled**. Its knowledge (2MB) is now imported at `~/cfe-brain/vault/`. Excluded: 155MB of third-party PDFs and `entregables/` (client deliverables). Both remain unbacked-up on this box. Flag that as a risk; do not commit them without asking.

## CHARTER GATE 0 — you gate everything. Read `~/prompts/CHARTER.md`.

Jesus has decided: **neither branch is truth yet. Audit first.**

Your immediate and only job is a written reconciliation report. **Merge nothing. Authorize nothing.**

`origin/dev` +102 over `origin/main`. `origin/main` +55 over `origin/dev`. Diverged BOTH ways — a fork, not drift.
The droplet's local refs are STALE. Run `git fetch --all` before you compare anything.

The report must establish, with evidence:
- what is on each side, at the level of subsystems
- what is **actually deployed**, and from which branch. Trace one live URL back to a commit.
- what is dead code and what is live
- `docs/cfe-collection.md` exists on `origin/main` ONLY. **What else is stranded like that?** Enumerate every file present on one branch and absent on the other.
- a recommendation, with reasons, for which branch becomes canonical, and what it costs to carry the other side over

Jesus decides from your report. Then, and only then, GATE 3.

## GATE 4 — environments (AFTER a clean main, not before)
Supabase **Pro is confirmed**, so native branching is available.
Before enabling it, cost it: branches bill while alive, and four agents opening PRs means ephemeral DBs. Report expected monthly cost to the CEO.
Then `dev` / `staging` / `prod` in GitHub and Supabase, CI/CD via Actions.

## Standing job
RLS: every table exposed to the client needs a policy. No policy is a defect. Run the Supabase advisors, report verbatim.
Schema drift: migrations in git are normative; the deployed database is the implementation. Drift is a defect in the DATABASE.

## You do not decide merges
The **CTO session** (tmux `cto`) holds the veto. You execute merges only on written CTO sign-off, and only after Jesus picks the canonical branch.
