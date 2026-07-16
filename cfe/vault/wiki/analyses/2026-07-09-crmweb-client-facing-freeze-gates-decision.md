---
title: "DECISION — client-facing proposal freeze gates (REVOKE runbook, prep only)"
type: analysis
tags: [decision, tuesday-inputs, cfe-ppa-bess, containment, del-5, prod-drift, revoke, runbook]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [newman-architecture/supabase/migrations/20260709140000_crm_proposals.sql, newman-architecture/apps/crm-web/app/actions.ts, pg_proc ACL on prod bwudgrwfwjdbvqhgbwty]
---

# DECISION — client-facing proposal freeze gates (REVOKE runbook, prep only)

**Why.** `crm-web/lib/finance.ts` (`computeFinance`/`groundedRevenue`) computes the client-facing
proposal Ahorro and **diverges from the golden engine** — drops the GDMTH umbral, ignores RTE on
BESS arbitrage, permits PV punta credit; never reconciled to RPU `780881200029`
([[2026-07-09-crmweb-finance-ts-diverges-client-facing]]). This surface can put wrong savings into a
client's hands with no human in the loop.

**Authorization.** Jesus authorized gating `crm_web_send_proposal` (2026-07-09). Exact scope
(send-only vs full A+B+C freeze) pending his ruling. **This page is PREP ONLY — nothing has been
applied.** `supabase-devops` executes the REVOKEs via Supabase MCP on the CEO's word.

**Target project:** prod `bwudgrwfwjdbvqhgbwty` (Supabase, the `main`/prod database).

All three functions are `public`, `SECURITY DEFINER`, owner `postgres`, invoked via supabase-js
`.rpc()`. Gates are pure ACL toggles — no `CREATE OR REPLACE`, no DDL, no data touched. Each is a
one-statement change with a one-statement rollback.

## Gate A — block the client-facing SEND (authenticated path)
`crm_web_send_proposal(p_id uuid, p_to text, p_site text)` — body inserts into `crm.comms_outbox`
(the client email) and sets `proposal.status='sent'` (migration `:93-106`). Called as `authenticated`
by `actions.ts:351`. ACL: authenticated holds EXECUTE.

```sql
-- APPLY
REVOKE EXECUTE ON FUNCTION public.crm_web_send_proposal(uuid, text, text) FROM authenticated;
-- ROLLBACK
GRANT  EXECUTE ON FUNCTION public.crm_web_send_proposal(uuid, text, text) TO   authenticated;
```
Effect: the rep's Send returns permission-denied → no `comms_outbox` row → no client email.
`service_role`/`postgres` retain EXECUTE (backend intact). Staff can still generate/list/void.

## Gate B — block the public VIEW of the frozen Ahorro (anon path)
`crm_proposal_public(p_token text)` — anon-executable; returns the frozen snapshot + the `ahorro`
`proposal_line` to any token holder (migration `:109-120`). The Ahorro is frozen at *generate* time
(`:78`), so it is viewable **without a send** by anyone holding a token. ACL: anon holds EXECUTE.

```sql
-- APPLY
REVOKE EXECUTE ON FUNCTION public.crm_proposal_public(text) FROM anon;
-- ROLLBACK
GRANT  EXECUTE ON FUNCTION public.crm_proposal_public(text) TO   anon;
```
Effect: `app/p/[token]/page.tsx:15` gets null → renders "Propuesta no encontrada o expirada" (`:19`).

## Gate C — block the client E-SIGN (anon path)
`crm_sign_proposal(p_token text, p_name text, p_email text, p_signature text)` — anon-executable;
called by `components/proposal-sign.tsx:28`; records a signature and notifies compliance
(migration `:125-139`). ACL: anon holds EXECUTE.

```sql
-- APPLY
REVOKE EXECUTE ON FUNCTION public.crm_sign_proposal(text, text, text, text) FROM anon;
-- ROLLBACK
GRANT  EXECUTE ON FUNCTION public.crm_sign_proposal(text, text, text, text) TO   anon;
```
Effect: a client with a token can no longer e-sign a divergent proposal.

## Full freeze set (copy-paste)
```sql
-- APPLY (full client-facing freeze A+B+C)
REVOKE EXECUTE ON FUNCTION public.crm_web_send_proposal(uuid, text, text) FROM authenticated;
REVOKE EXECUTE ON FUNCTION public.crm_proposal_public(text)               FROM anon;
REVOKE EXECUTE ON FUNCTION public.crm_sign_proposal(text, text, text, text) FROM anon;

-- ROLLBACK (full restore)
GRANT  EXECUTE ON FUNCTION public.crm_web_send_proposal(uuid, text, text) TO   authenticated;
GRANT  EXECUTE ON FUNCTION public.crm_proposal_public(text)               TO   anon;
GRANT  EXECUTE ON FUNCTION public.crm_sign_proposal(text, text, text, text) TO   anon;
```

## ⚠️ NOTE — these are runtime privilege changes, NOT in supabase/migrations
These REVOKEs are applied live to prod via MCP and are **not captured in `supabase/migrations/`**.
By nature they are **new silent git↔prod drift** — exactly the class of problem GATE 0 exists to
close (DEL-4 is already 5/75; do not widen the gap unaccounted). Therefore:

- This page is the **record of record** for the change until it is reconciled.
- When the golden-wrapped fix lands (client proposal computes from `calc_core`/`ppa_pricer`), the
  gates MUST be either **rolled back** (GRANTs above) or **migrated** (folded into a
  `supabase/migrations/*.sql` if kept), so git and prod agree again.
- Do not let these ACL toggles become permanent undocumented drift.

## Status
PREP ONLY. Nothing applied. Awaiting Jesus's scope ruling; `supabase-devops` executes on the CEO's word.

## Related
- [[2026-07-09-crmweb-finance-ts-diverges-client-facing]] — the finding that motivates the gate
- [[2026-07-09-gate0-fork-cto-verification]] — why uncaptured prod ACL drift is costly right now
