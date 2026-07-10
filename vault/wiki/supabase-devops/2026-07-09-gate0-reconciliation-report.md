---
title: "GATE-0 reconciliation report — main/dev fork, for Jesus's canonicity ruling"
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, gate-0, reconciliation, fork, del-4, canonicity, preserve-both]
created: 2026-07-09
updated: 2026-07-09
status: vigente
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# GATE-0 reconciliation report — main/dev fork

**Purpose.** Give Jesus the evidence to rule canonicity FROM. This report authorizes **no
execution**: no branch touched, no prod schema changed, no merge, no reset. It recommends a
direction and specifies *preserve-both* mechanics so **nothing on either arm is discarded**.

**Measured** after `git fetch --all` on 2026-07-09 against `origin/dev@a81c43c`,
`origin/main@8151003`, `origin/staging@d28ae6b`, and prod project `bwudgrwfwjdbvqhgbwty`.

---

## 0. Shape of the fork
`origin/staging` (`d28ae6b`) is the **merge-base**; it sits exactly on the fork point (0
commits past it either way) — frozen. `origin/dev` = base **+102 / −0**; `origin/main` = base
**+55 / −0**; they share no commit since the fork. `crm-platform` is an ancestor of `dev`. Two
arms, disjoint feature sets, one shared origin.

---

## 1. What is unique to each arm — and what is actually DEPLOYED

### `origin/dev` (+102): the Newman CRM product
`apps/crm-web` (Next.js, 115 files), `supabase/migrations/*` (75 timestamped, CRM+huddle+todos),
`supabase/functions/{ai-copilot,comms-dispatch,lead-intake,push-dispatch}`, the SSO gateway
(`deploy/sso-gateway/*`), `deploy/crm-web`, `deploy/curvas/*`, `agents/{crm-mcp,crm-migrate,
crm-contacts-migrate,huddle-sync}`, `.github/workflows/{db-tests.yml,deploy-crm.yml}`,
`supabase/config.toml`, `supabase/tests/newman_crm_test.sql`, `docs/{crm-platform,crm-cutover,
crm-competitive-analysis, diagrams/*}`.
**Deployed:** `deploy-crm.yml` ships `apps/crm-web` to the **newman-crm droplet → tuesday.newman.re**
on push to `dev`. The curvas static site and the SSO gateway also originate here.

### `origin/main` (+55): the cfe-collector / bill-parser hardening
Files unique to main (present on main, absent on dev): `agents/cfe-collector/pdf_intake.py`
(+ its test), `supabase/functions/send-whatsapp/index.ts`, `docs/cfe-collection.md`, and
`db/migrations/010–015` (6 numbered migrations). **Most of main's 55 commits are divergent
*content* on files that also exist on dev** (the cfe-collector modules), not new files — the
extraction-hardening committee rounds rewrote shared files.
**Deployed:** `deploy.yml` ships to **newman-vps + mini** (`/opt/newman-architecture`), gated on
green CI, on push to `main`. The systemd `newman-agent@*` units on newman-vps (verified running:
proposal-builder, design-engine, intake-worker, cfe-collector, …) run **main's** code.

### Prod database
Project `bwudgrwfwjdbvqhgbwty` is the **hand-applied union of both arms** (§4). It is neither
branch's `supabase/migrations` replayed — it was built cumulatively via MCP.

**Net:** the two live production surfaces are fed by **two different branches**. `main`→newman-vps
(collector), `dev`→newman-crm (CRM). **Neither branch alone can rebuild both surfaces**, and the
DB is a third thing (the union). That is the whole problem in one sentence.

---

## 2. Live vs dead code on each side
- **main's cfe-collector = LIVE** (newman-vps). main has **no `apps/crm-web`**, so main cannot
  serve the CRM at all.
- **dev's crm-web = LIVE** (newman-crm). But **dev also carries a full copy of
  `agents/cfe-collector`** inherited from the staging base — **stale (pre-hardening) and never
  deployed** (deploy-crm ships only `apps/crm-web`; newman-vps deploys from main). On dev that
  collector copy is **dead, superseded by main's**.
- Therefore, for every shared cfe-collector file, **main's content is the live one and dev's is
  the dead twin.** This is the key resolution rule for §6.
- Both arms' non-overlapping features (crm-web, sso-gateway, curvas on dev; pdf_intake +
  send-whatsapp on main) are each live/needed on their own surface — nothing here is dead-on-both.

---

## 3. Stranded files (present on only one branch)
Sibling sessions cannot see these across the fork.

**main-only (stranded):** `docs/cfe-collection.md`, `agents/cfe-collector/pdf_intake.py`,
`agents/cfe-collector/test_pdf_intake.py`, `supabase/functions/send-whatsapp/index.ts`,
`db/migrations/010–015`.

**dev-only (stranded, non-crm-web highlights):** `docs/{crm-platform,crm-cutover,
crm-competitive-analysis}.md`, `docs/diagrams/*`, the entire `deploy/sso-gateway/*` and
`deploy/curvas/*` (incl. `deploy/curvas/current/index.html` — the file under the standing
"do-not-discard" uncommitted edit), `deploy/systemd/newman-crm-web.service`,
`agents/{crm-mcp,crm-migrate,crm-contacts-migrate,huddle-sync}`, `.github/workflows/{db-tests,
deploy-crm}.yml`, `supabase/config.toml`, `supabase/tests/newman_crm_test.sql`, and the four
CRM `supabase/functions`.

`docs/cfe-collection.md` was the canary; the stranded set is far larger and spans docs, deploy
infra, agents, CI, and edge functions on **both** sides. Any reconciliation must union these, not
choose between them.

---

## 4. The git↔prod migration gap (DEL-4)
**Prod ledger = 119 migrations** (was 117; +2 today), all hand-applied via MCP with timestamped
versions. Composition: 31 `crm_*`, the rest cfe-collector/whatsapp/doc-pipeline/client-schema.

- **dev's `supabase/migrations` (75 files): only 5 versions match the prod ledger.** 70 dev files
  carry versions prod never saw; the other ~112 prod migrations have no dev file. dev's set is
  also **CRM-only** — it contains none of the cfe-collector schema that is in prod.
- **main's `db/migrations/001–015` (numbered)** are not in the Supabase ledger *format* at all;
  they map to prod migrations by name/content only (e.g. `014_whatsapp_rpu_confirmation_gate`
  ↔ prod `20260709065500 whatsapp_rpu_confirmation_gate`). Double-recorded, never the apply path.
- **Today's out-of-band applies (from [[prod-only-drift-register]]), all on prod, NOT in any
  committed branch:**
  - `20260709124613 fix_claim_media_boolean_int` (016) — in ledger.
  - `20260709132040 widen_bulk_pdf_status_chk` (017) — in ledger.
  - **3 freeze REVOKEs** (crm_web_send_proposal FROM authenticated; crm_proposal_public,
    crm_sign_proposal FROM anon) — applied via `execute_sql`, **ledger-invisible**.
- Net: `supabase db push` from dev would treat ~70 versions as pending and diverge; the Supabase
  `dev`/`staging` preview branches already read `MIGRATIONS_FAILED`. **Git does not describe the
  database.** The canonical trunk must reproduce all 119 ledger migrations + fold the 3 owed
  patches (016, 017, freeze) so `db push --dry-run` = 0 pending.

---

## 5. Recommended canonical direction (with evidence)
**Build ONE integration trunk = `dev` with `main` merged in, reconciled to the prod ledger.**
Use **`dev` as the base**, merge `main` on top. Evidence for dev-as-base:
1. The org already chose `supabase/migrations/` as the migration home — commit `14b539f`
   ("move migrations to supabase/migrations for the GitHub integration"). main's `db/migrations`
   numbering is the legacy path.
2. The from-scratch schema-test infra (`db-tests.yml` + pgTAP `supabase/tests`) exists **only on
   dev**; it is the gate that proves the union reproduces.
3. dev auto-deploys and is the newer/larger surface (102 vs 55; 68k vs 4k lines); prod's 31 crm
   migrations originate here.
4. main contributes a **smaller, well-bounded** delta (mostly cfe-collector content + 4 stranded
   files), cheaper to merge onto dev than the reverse.

This matches the earlier ruling ([[canonicity-prod-is-truth]]): **prod is truth; reconcile git to
it; unify — do not pick a winner that discards the other.** The recommendation is a *base choice
for the merge*, **not** a decision to drop main.

---

## 6. PRESERVE-BOTH mechanics (specified, NOT executed)
The requirement: **every** unique commit on **both** arms stays reachable. That rules out
`git reset --hard` / re-baseline (orphans one arm) and rules out rebasing a shared branch
(rewrites SHAs, forbidden). The only preserve-both primitive is a **true merge + fast-forward**.

**Step A — integration branch (isolated).** In a fresh worktree: create `integration/gate0` from
`origin/dev`. Touches no shared branch.

**Step B — merge main in.** `git merge origin/main` → a merge commit **reachable from all 102 dev
+ 55 main commits**. No history rewritten, nothing orphaned.

**Step C — conflict resolution policy (by class):**
- `agents/cfe-collector/**` (shared, diverged): **take main** — it is the live prod code (§2).
  Add main-only `pdf_intake.py`, its test, and `supabase/functions/send-whatsapp` as-is.
- `apps/crm-web/**`, sso-gateway, curvas, crm agents: **dev-only, keep** (no conflict).
- `.github/workflows/**`: **union** — keep dev's `db-tests`+`deploy-crm` AND main's `deploy.yml`
  (both deploy targets stay). Reconcile any shared file to keep both surfaces deploying.
- `supabase/functions/**`: **union** — main's `send-whatsapp` + dev's four; for
  `whatsapp-intake`/`bill-rename` (on both) take the **prod-deployed** version.
- `docs/**`: **union** — keep cfe-collection.md AND the crm-* docs + diagrams.
- Migration dirs: `db/migrations/010–015` (main) and `supabase/migrations/*` (dev) live in
  different paths → no textual conflict; both retained pending Step D. **Nothing deleted.**

**Step D — reconcile git migrations to the prod ledger (the DEL-4 close).** Align
`supabase/migrations` to the 119-row prod ledger (`supabase migration repair` / `db pull`) so
`db push --dry-run` = 0 pending; add migration files for the owed patches **016**
(`20260709124613`), **017** (`20260709132040`), and the **freeze** (either as a migration if kept
or reverted per the golden-fix decision). Port main's `db/migrations/010–015` content into the
`supabase/migrations` lineage (or archive as legacy) — **without dropping** the SQL. End state:
git ledger == prod ledger.

**Step E — verification gates (all green before any promotion):** pgTAP `db-tests` builds the
**union** schema from scratch; `CI` green (fix the `lint-test` 15m timeout first); `db push
--dry-run` = 0 pending vs prod; the merged `agents/cfe-collector/**` byte-matches what runs on
newman-vps; `apps/crm-web` builds. **Golden test invariant (below).**

**Step F — promotion without reset (preserve-both).** Once `integration/gate0` is verified,
**fast-forward** `staging` → it, then `main` and `dev` both fast-forward to the same commit. The
fork closes with **zero orphaned commits** — because it is a merge, both arms remain ancestors of
the trunk; every original SHA stays reachable. Never force-push; shared branches only
fast-forward.

**Why not the tempting shortcut:** `git checkout main && git reset --hard dev` (or the reverse)
would orphan 55 (or 102) real commits and the deployed code behind them. That is precisely the
outcome this report exists to prevent.

---

## Golden-test invariant (sacred throughout)
RPU **780881200029** stays peso-exact (baseline $30,157,371; Ahorro $7,083,252 / 23.5%; 18 checks)
across the entire reconciliation. The engine (`tools/cfe_savings`) lives in **cfe-brain, not
newman-architecture**, so the code merge does not touch it — but the CRM's `crm-web/lib/finance.ts`
**diverges from that golden engine** (filed separately) and must not be blessed as canonical until
it is golden-wrapped. No merge step may alter savings math.

---

## What this authorizes
**Nothing to execute.** It is the written basis for Jesus's canonicity ruling. On his direction,
Step A–F run in order, each behind the verification gate, with the golden test sacred and
[[prod-only-drift-register]] items folded in at Step D.

## Related
- [[canonicity-prod-is-truth]] · [[main-dev-fork]] · [[migration-git-prod-drift]] ·
  [[prod-only-drift-register]] · [[graph-filing-two-roots-failure]]
