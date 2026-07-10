---
title: "Prod-only drift owed to the canonical branch (reconciliation register)"
type: analysis
service: supabase-devops
kind: finding
tags: [supabase-devops, prod-drift, del-4, reconciliation, owed, revoke, migration]
created: 2026-07-09
updated: 2026-07-09
status: vigente
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Prod-only drift owed to the canonical branch (reconciliation register)

Live changes applied to prod `bwudgrwfwjdbvqhgbwty` by `supabase-devops` that are **not yet
reflected in any committed branch**. Each is intentional and authorized, but each widens the
git↔prod gap ([[migration-git-prod-drift]], DEL-4). This page is the standing record until
each is reconciled once canonicity is ruled ([[canonicity-prod-is-truth]]).

## 1. Client-facing proposal freeze — three EXECUTE revokes
- **Applied:** 2026-07-09 11:47:06 UTC, via `execute_sql` (runtime ACL change, **not** in the
  migration ledger, no migration file).
- **What:** `REVOKE EXECUTE` on `crm_web_send_proposal(uuid,text,text)` FROM `authenticated`;
  on `crm_proposal_public(text)` FROM `anon`; on `crm_sign_proposal(text,text,text,text)` FROM
  `anon`. `service_role`/`postgres` retain EXECUTE.
- **Record of record:** [[2026-07-09-crmweb-client-facing-freeze-gates-decision]].
- **Owed:** when the golden-wrapped client-proposal fix lands, either roll back (the GRANTs in
  that runbook) or fold into `supabase/migrations/*.sql` if kept. Ledger-invisible → easy to
  forget; do not let it become permanent silent drift.

## 2. claim_media boolean→integer type fix
- **Applied:** 2026-07-09 12:46 UTC, via `apply_migration` name `fix_claim_media_boolean_int`
  → **in the prod ledger** as version `20260709124613`.
- **What:** `CREATE OR REPLACE FUNCTION public.claim_media(text,integer,text)` — declares
  `v_inserted integer` (was `boolean`), fixing `operator does not exist: boolean = integer`
  that 500'd `whatsapp-intake` on every inbound bill after migrations 014/015. Type-only; body
  otherwise byte-identical to the captured live definition.
- **Source file (not yet committed):** another session's scratchpad
  `xchannel/016_fix_claim_media_boolean_int.sql`. `claim_media` itself was created via MCP with
  014/015 and is in no committed migration file.
- **Owed:** commit the migration file to the canonical branch once canonicity is ruled, aligned
  to ledger version `20260709124613`. Unlike item 1 this IS in the ledger, but the **file** is
  missing from git — the mirror image of the same DEL-4 gap.

## 3. bulk_pdf_status_chk widened (4 → 7 values)
- **Applied:** 2026-07-09 13:20 UTC, via `apply_migration` name `widen_bulk_pdf_status_chk`
  → **in the prod ledger** as version `20260709132040`.
- **What:** `ALTER TABLE client.bulk_pdf DROP/ADD CONSTRAINT bulk_pdf_status_chk` — widened from
  `{new, processing, done, failed}` to add `pending, needs_ocr, needs_name` (strict superset).
  Unblocks the bulk-PDF splitter, which wrote those three states and 23514'd on the old
  constraint (surfaced on bulk_pdf id=2, `bulk_8edd057514c2.pdf`, 2026-07-09 13:00:11Z → fell
  back to `failed`, no collection_request/bill).
- **Source file (not yet committed):** `xchannel/017_bulk_pdf_status_needs_name.sql`. The
  constraint was created out-of-band on prod with the bulk-PDF/whatsapp work; no committed
  `db/migrations/` file reproduces it.
- **Owed:** commit the migration file to the canonical branch once canonicity is ruled, aligned
  to ledger version `20260709132040`. Same shape as item 2 (in-ledger, file-missing).

## Reconciliation invariant
All items must end in the state where **git and the prod ledger agree**: item 1 either reverted
or migrated; items 2 and 3's files committed to the canonical branch. Track to closure; none is
done until git describes prod.
