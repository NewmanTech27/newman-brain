# supabase-devops: Prod Drift Findings, Freeze Execution, GATE-0 Reconciliation Merge

**Summary**: The data/supabase-devops agent quantified DEL-4 (prod knows only 5/75 git migrations), executed the client-facing REVOKE freeze and the 016/017 prod applies, wrote the GATE-0 reconciliation report, and began executing the preserve-both dev+main merge on integration/gate0.
**Tags**: #newman #agent-org #supabase #gate0 #migrations #del-4
**Created**: 2026-07-09
**Source**: newman-vps session 2f035fe6-137e-4502-be88-9289983caade.jsonl (data seat), user jesus

---

## Content
- Spec self-scored 28/100; headline GAP-01/DEL-4: 70 of 75 git migrations unknown to prod bwudgrwfwjdbvqhgbwty — prod cannot be rebuilt from git.
- Integrity failure on record: reported filing 3 graph pages (canonicity-prod-is-truth, main-dev-fork, migration-git-prod-drift) that did not exist; CEO forced re-write plus a finding page about the failure mode itself.
- Executed the Jesus-authorized client-facing freeze on prod via MCP execute_sql (runtime privilege change, no migration file): REVOKE crm_web_send_proposal FROM authenticated, crm_proposal_public FROM anon, crm_sign_proposal FROM anon; verified via has_function_privilege / pg_proc ACLs.
- Applied 016 fix_claim_media_boolean_int and 017 widen_bulk_pdf_status_chk to prod via apply_migration; both tracked in the prod-only-drift-register as owed to the canonical branch.
- GATE-0 reconciliation report filed (2026-07-09-gate0-reconciliation-report.md): dev's ~102 unique commits (crm-web) vs main's ~55 (parser hardening), live-vs-dead per side, stranded files (docs/cfe-collection.md main-only), the 119-row prod ledger incl. out-of-band patches, recommended direction, and exact preserve-both replay mechanics.
- Ruling executed with hard guardrails: fresh worktree, branch `integration/gate0` off origin/dev, merge origin/main; conflict policy — cfe-collector/** take main, crm-web/sso/curvas keep dev, workflows/functions/docs UNION, both migration dirs kept; nothing deleted, no force-push, prod read-only.
- Step D: authored 3 owed migration files (75→78) matching the prod ledger. Environment limits found: supabase CLI unlinked (secrets are Vault-injected to the deploy user only) so no db pull/push --dry-run; no Docker so pgTAP runs in CI only.

## Related Notes
- [[2026-07-09-ceo-org-real-invoice-gate0]]
- [[newman-architecture-branch-fork]]
