---
title: CRM RLS final state is set by migration ordering (RBAC drops+recreates all policies)
service: tuesday-inputs
kind: finding
sources: ["newman-architecture/supabase/migrations/20260708240000_crm_rbac.sql:53", "newman-architecture/supabase/migrations/20260708232625_crm_user_roles_ownership_rls.sql", "newman-architecture/supabase/migrations/20260708115000_crm_role_helpers_early.sql:9"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# CRM RLS final state is set by migration ordering

**Severity: MEDIUM (fragile, currently correct).** RLS on the CRM "card" tables evolved through three overwriting layers; **migration timestamp ordering decides the final effective policy**:

1. `..._crm_schema.sql` seeds blanket `using(true)` policies.
2. `20260708232625_crm_user_roles_ownership_rls.sql` narrows `contact`/`deal` to **owner-scoped** policies.
3. `20260708240000_crm_rbac.sql:53–74` runs a **dynamic block that DROPS every existing `crm.*` policy** and recreates a single blanket **`crm_staff_all` (`crm.my_role() IS NOT NULL`)** for `account, contact, deal, deal_event, deal_rpu, todo, huddle_run`.

Because `240000 > 232625`, the RBAC migration **supersedes** the owner-scoping — the effective policy on those tables is the **staff gate, NOT owner-scoped**. No later migration re-adds owner RLS. Exceptions written *after* RBAC survive: `notification` is per-recipient (`recipient_email = auth.jwt()->>'email'`), and `comms_outbox`/`ai_draft`/`ai_prompt_log` are staff-gated. `service_role` (edge functions/agents) bypasses RLS entirely.

`crm.my_role()` = `select role from crm.app_user where auth_uid=auth.uid() and active` (`20260708115000_crm_role_helpers_early.sql:9–13`).

The trap: anyone adding an owner-scoping migration with a timestamp **before** `240000`, or expecting owner-scoping to be in force, will be wrong. The staff gate is the DB-side guarantee the input-handling spec relies on. See [[tuesday-newman-re-is-the-crm]].
