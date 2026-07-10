---
title: "Multi-repo branch audit — post-fetch divergence across all Newman repos"
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, gate-0, branch-audit, reconciliation, fork, multi-repo, read-only]
created: 2026-07-10
updated: 2026-07-10
status: vigente
verified_at: 2026-07-10
confidence: verified
---

# Multi-repo branch audit (READ-ONLY)

**Purpose.** Jesus authorized a background, read-only branch audit across every Newman repo and
worktree. This page records per-repo divergence, stranded files, and which branch feeds which
live surface. It authorizes **no execution**: nothing was merged, reset, rebased, deleted,
force-pushed, or committed; no prod schema was touched. It is a snapshot for the canonicity
ruling still owed on the `newman-architecture` fork ([[2026-07-09-gate0-reconciliation-report]]).

**Method.** `git fetch --all --prune` was run in each of the three real git repos **before** any
comparison. All ahead/behind counts below are computed against fresh `origin/*` refs, never
against the droplet's local branches (local `newman-architecture/main` was 71 behind `origin/main`
at audit time — a stale local ref would have mis-stated the fork).

**Measured** 2026-07-10 against `origin/*` post-fetch.

---

## 0. What is and isn't a git repo

Of the ten named targets, **three are not git repositories** — they are unversioned deploy/config
directories on the box, and are one disk failure from gone (same risk class as
`/home/mario/CFE Brain`):

| Path | State | Contents |
|---|---|---|
| `~/newman-sso` | **not versioned** | SSO auth-shell: `apply.sh`, `validator.py`, `login/`, `nginx/`, `cloudflared.config.yml`, systemd unit + env |
| `~/excalidraw-auth` | **not versioned** | Excalidraw auth shell: `validator.py`, `login/`, nginx, systemd unit + env |
| `~/supabase` | **not a repo** | only a `.temp/` dir — Supabase CLI scratch, no project |

The four `wt-*` paths are **not separate repos** — they are `git worktree` checkouts of the single
`newman-architecture` repo (one shared `.git`), each holding a different branch. They are covered
under newman-architecture below.

---

## 1. Per-repo divergence

### `cfe-brain` (this repo — the knowledge vault)
- Branches: `main` only (local and `origin/main`).
- Divergence: local `main` == `origin/main` (ahead 0 / behind 0). Clean.
- Live surface: none — this is the compiled wiki, not a deployed product.
- Stranded files: none.

### `newman-architecture` (the fork — confirmed still current)
- Branches on origin: `main`, `dev`, `staging`, `crm-platform`, `spec/supabase-devops`.
- **Fork confirmed unchanged post-fetch:** merge-base of `dev` and `main` is `origin/staging`
  (`d28ae6b`), sitting exactly on the fork point (0 either way).
  - `origin/dev` = base **+102 / −0**
  - `origin/main` = base **+55 / −0**
  - The two arms share no commit since `d28ae6b`. Diverged both ways — a fork, not drift.
- `origin/crm-platform` (`14b539f`) is an **ancestor of `dev`** (0 ahead / 100 behind) — a subset,
  safe to ignore for canonicity.
- `origin/spec/supabase-devops` (`59c752a`) = `dev` **+1** (the 28/100 spec commit); pushed.

### `newman-landing`
- Branches on origin: `dev`, `main`.
- `origin/dev` = `origin/main` **+2 / −0**. `main` is an **ancestor of `dev`** (merge-base =
  `main` `ac75166`) — fast-forwardable, not a fork.
- The two dev-only commits: `bf13c21` (wire lead capture to Supabase + auth shell) and `787c574`
  (CI: deploy `dev` to newman-vps via tunnel).

---

## 2. Live surface → branch mapping

The recurring pattern across both product repos: **`main` is not the live branch.**

| Live surface | Repo | Fed by branch | Mechanism |
|---|---|---|---|
| `tuesday.newman.re` (CRM) | newman-architecture | **`origin/dev`** | `deploy-crm.yml`, push to `dev`, paths `apps/crm-web/**` — **workflow exists on `dev` only** |
| newman-vps + mini (cfe-collector, agents) | newman-architecture | **`origin/main`** | `deploy.yml` + `deploy-mini.yml`, `workflow_run` after CI on `main` |
| newman-landing site | newman-landing | **`origin/dev`** | `deploy.yml`, push to `dev`, via tunnel — **workflow exists on `dev` only; `main` cannot deploy it** |

Consequence for newman-architecture: the **two production surfaces are fed by two different arms of
the fork** — CRM from `dev`, collector from `main`. Neither branch alone can rebuild production.
Prod DB `bwudgrwfwjdbvqhgbwty` remains the hand-applied union of both (see
[[2026-07-09-gate0-reconciliation-report]] §4; [[migration-git-prod-drift]], DEL-4 at 5/75).

---

## 3. Stranded files (present on one arm, absent on the other)

### newman-architecture — `main`-only (10 files, invisible from `dev`)
```
agents/cfe-collector/pdf_intake.py          (+ test_pdf_intake.py)
supabase/functions/send-whatsapp/index.ts
docs/cfe-collection.md
db/migrations/010_intake_upserts_client.sql
db/migrations/011_crm_deal_from_intake.sql
db/migrations/012_deadletter_watchdog_split_bad_download.sql
db/migrations/013_claim_collection_reclaim_cap_and_backoff.sql
db/migrations/014_whatsapp_rpu_confirmation_gate.sql
db/migrations/015_bulk_pdf_confirm_phone.sql
```
`docs/cfe-collection.md` is the file the charter flagged — and it is **not alone**: the entire
cfe-collector hardening arm (`pdf_intake`, `send-whatsapp`, migrations 010–015) is stranded on
`main`, unreachable from `dev` where the sibling sessions work.

**Structural note:** `main` numbers migrations in `db/migrations/010–015`; `dev` uses timestamped
`supabase/migrations/**` (75 files). The two arms disagree on the migration *directory and naming
scheme* — a carry-over is not a plain `git mv`, it is a re-home.

### newman-architecture — `dev`-only (246 files)
The whole CRM product: `apps/crm-web/**` (Next.js, ~115 files), `agents/{crm-mcp,crm-migrate,
crm-contacts-migrate,huddle-sync}`, `deploy/crm-web/**`, `deploy/sso-gateway/**`,
`.github/workflows/{deploy-crm.yml,db-tests.yml}`, `supabase/functions/{ai-copilot,comms-dispatch,
lead-intake,push-dispatch}`, `supabase/migrations/**`, and the CRM docs.

### newman-landing — `dev`-only (5 files)
```
.github/workflows/deploy.yml   app/auth.js   app/index.html   app/login.html   config.js
```
The auth shell + lead-capture wiring + the deploy pipeline all live on `dev`; `main` has none of
it. `main` here is stale, not a rival.

---

## 4. Worktree branches (newman-architecture, one shared `.git`)

All four are checkouts of newman-architecture. Divergence vs `origin/dev`; "unpushed" = the branch
exists only on the droplet, not on origin — losable if the box dies.

| Worktree | Branch | HEAD | vs origin/dev | On origin? |
|---|---|---|---|---|
| (main checkout) | `spec/cfe-bill-parser` | `a81c43c` | +0 / −0 (== dev) | **no (unpushed)** |
| `wt-gate0` | `integration/gate0` | `38ebff0` | **+57 / −0** | **no (unpushed)** |
| `wt-cfe-ppa-bess` | `spec/cfe-ppa-bess` | `19bc966` | +2 / −0 | **no (unpushed)** |
| `wt-supabase-devops` | `spec/supabase-devops` | `59c752a` | +1 / −0 | yes (`origin/spec/supabase-devops`) |
| `wt-tuesday-inputs` | `spec/tuesday-inputs` | `5f6f804` | +1 / −0 | **no (unpushed)** |

`integration/gate0` is the reconciliation branch (authors the 016/017/freeze prod-only patches —
[[prod-only-drift-register]]). It is **+57 over `origin/dev` and +104 over `origin/main`, behind 0
on both** — i.e. it already carries dev's line plus reconciliation work, but it exists **only on
the droplet**. Four unpushed branches (gate0, cfe-ppa-bess, tuesday-inputs, cfe-bill-parser) are a
standing loss risk: a box failure erases them. Flag, do not act.

---

## 5. Findings / recommendations (no execution)

1. The `newman-architecture` dev/main fork is **real and current** post-fetch (dev +102 / main +55,
   both off `staging@d28ae6b`). Prior GATE-0 report stands; canonicity ruling still owed to Jesus.
2. **`main` is the live branch for nothing that matters on its own** and the wrong mental default:
   CRM ships from `dev`, landing ships from `dev`, only the collector ships from `main`. "Merge to
   main" is not "deploy" here.
3. **Three deploy/auth directories are unversioned** (`newman-sso`, `excalidraw-auth`, and the
   `supabase` CLI scratch). `newman-sso` and `excalidraw-auth` hold real auth-shell logic
   (`validator.py`, login pages, nginx, systemd units) and should be brought into a repo — escalate
   to Jesus; do not commit them without his say-so (same class as the unbacked `/home/mario` PDFs).
4. **Four unpushed local branches** on newman-architecture (incl. `integration/gate0`, the
   reconciliation work) exist only on the droplet — push or accept the loss risk. Not my call to
   push unilaterally; flag for the canonicity decision.
5. `newman-landing` is a clean fast-forward (`main`→`dev`, +2), not a fork — trivially reconciled
   once someone owns it.

See also: [[2026-07-09-gate0-reconciliation-report]], [[prod-only-drift-register]],
[[canonicity-prod-is-truth]], [[main-dev-fork]], [[migration-git-prod-drift]].
