---
title: "tuesday-inputs final handoff — what the rebuild cannot reconstruct"
type: analysis
kind: handoff
tags: [handoff, tuesday-inputs, crm, auth-gate, newman-sso, whatsapp-intake, gate0]
created: 2026-07-10
updated: 2026-07-10
status: vigente
confidence: see per-claim tags below
verified_against:
  - newman-architecture@a81c43c        # dev head; CRM source + migrations read here
  - newman-architecture spec/tuesday-inputs@5f6f804  # my spec branch, off dev, UNMERGED
  - ~/newman-sso (on-box only, staged 2026-07-08/09, NOT in git anywhere)
  - cfe-brain wiki @ HEAD (this commit)
sources:
  - ~/newman-sso/validator.py:44-49 (email-suffix gate, NOT the Google hd claim)
  - ~/newman-sso/cloudflared.config.yml:1-11 (tunnel b7cefd82…, no login.newman.re DNS yet)
  - ~/newman-sso/INSTALL.md:1-30 (staged in home; ORDER MATTERS; not applied to /opt|/etc)
  - newman-architecture/supabase/functions/whatsapp-intake/index.ts:118,153,174,207,251
  - newman-architecture/supabase/migrations/20260708240000_crm_rbac.sql:53 (drops+recreates ALL policies)
  - newman-architecture/docs/specs/tuesday-inputs.md@5f6f804 (13 NRM, 9 GAP, self-score 56/100)
---

# tuesday-inputs final handoff — what the rebuild cannot reconstruct

I own the CRM input surface (`tuesday.newman.re`) and the shared `*.newman.re` auth gate.
Below is only what dies with my context / this box — not what the repos or wiki carry.

## 1. Traps documented nowhere

- **A WORKING AUTH GATE ALREADY EXISTS — staged on the box only, at `~/newman-sso`, in
  NO git repo.** It is a real nginx `auth_request` → Python validator (`validator.py`) →
  Supabase `/auth/v1/user` design, with systemd unit, cloudflared ingress, and a central
  `login.newman.re` page. It is derived from an "excalidraw-auth" setup (`excalidraw.newman.re`
  is already gated by it). **It is STAGED, not applied** — files sit in `~/newman-sso/`, not
  `/opt/newman-sso` or `/etc/nginx` (INSTALL.md §"ORDER MATTERS"). It retires with this box.
  Confidence: **high** (read today). **Copy this directory into the rebuild before the box dies.**
- **That validator does NOT verify the Google `hd` claim — it matches email suffix.**
  `validator.py:44-49` allows the request iff `email.endswith("@newman.re")` from the Supabase
  user record. The CHARTER requires the **`hd` claim verified server-side**. Email-suffix ≠ `hd`:
  magic-link auth admits anyone who can *receive* mail at an `@newman.re` address, and any
  Supabase identity whose `email` ends in the domain — it never inspects Google's domain-owned
  `hd` token. It fails closed on network error (401) — that part is correct. **Decide whether
  suffix-matching satisfies the charter; do not assume it does.** Confidence: **high**.
- **`login.newman.re` DNS was never created.** `cloudflared.config.yml` lists the ingress but
  INSTALL.md §1 says the proxied CNAME must be added in the Cloudflare dashboard (no `cert.pem`
  on the box → `cloudflared tunnel route dns` can't do it here). Until that CNAME exists the gate
  cannot serve. Confidence: **high** (config read; live DNS not curled).
- **CRM RLS final state is decided by MIGRATION ORDER, not by per-table migrations.**
  `20260708240000_crm_rbac.sql:53` **drops and recreates every policy**. Reorder the migrations
  in the rebuild and you silently change who can read what. Filed: [[crm-rls-rbac-ordering-trap]].
  Confidence: **high**.
- **`whatsapp-intake` acks Twilio with 200 on downstream write failure → silent lead loss.**
  Fire-and-forget on ≥5 branches (`index.ts:153,174,207,251`); non-POST also returns "ok"
  (`:118`). Always-2xx means Twilio never retries; the one audit write swallows its error.
  A happy-path test passes; the drop is invisible until a real lead vanishes. Filed:
  [[whatsapp-intake-silent-drop]]. Confidence: **high**.

## 2. Work in flight — exact state

- **Spec branch `spec/tuesday-inputs` @ `5f6f804`** (off `dev`@`a81c43c`, worktree, **UNMERGED**,
  GATE 0 blocks `main`). `docs/specs/tuesday-inputs.md`: Part A/B/C, 13 NRM, 9 GAP,
  **self-score 56/100**. Never CTO re-scored (GATE 2 never ran for this service).
- **Next step was unstarted Phase 4 — GAP-01:** make `whatsapp-intake` return non-2xx (or write
  a `crm.intake_deadletter` row) when a downstream write fails, and delete the unconditional
  "enqueued…" success log. Nothing was coded.
- **Auth gate: never investigated during my Phase 0** (I only confirmed the directory exists).
  This handoff is the first time I read `~/newman-sso` — hence its prominence in §1.

## 3. Claims I made but did NOT verify myself (honest)

- **Every "Met" verdict in the spec is CODE-READ, not test-executed.** I asserted NRM-02/03/04
  idempotency etc. by reading the SQL, not by running the tests. I ran no test in this service.
  Confidence on the "Met"s: **medium** (static read only).
- **`tuesday.newman.re` = the CRM** is inferred from `.env.example`, the systemd unit, the
  deploy README, and `deploy-crm.yml` — **I never curled live DNS.** Filed as verified in
  [[tuesday-newman-re-is-the-crm]], but the evidence is config, not a live 200. Confidence: **medium**.
- **Score 56/100 is my own claim**, uncontested by any independent re-score. Treat as a first-pass
  self-assessment, not a board number.

## 4. The one thing the rebuild WILL get wrong unless told

**You will rebuild the `*.newman.re` auth gate from scratch — and either duplicate the working
scaffold already sitting in `~/newman-sso` (which will be deleted with this box), or, worse,
copy it and inherit its email-suffix check believing it satisfies the charter's "verify the
Google `hd` claim server-side."** It does not. Capture `~/newman-sso` into the rebuild repo NOW,
then replace the suffix match in `validator.py` with a real server-side `hd`-claim verification
before `ceo.newman.re` or `extraction.newman.re` — which expose client RPUs, invoices, and
margins — ever deploy. An unauthenticated (or under-authenticated) deploy of those pages is a P0.
