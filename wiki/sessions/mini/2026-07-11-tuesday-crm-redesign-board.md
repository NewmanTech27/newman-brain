# Tuesday CRM redesign planned: 33-issue migration board with replica workspace for clients/salesmen

**Summary**: Turned "improve tuesday CRM + expose a safe replica to clients and salesmen" into a 6-phase, 33-issue Monday board (CRM Redesign — Migration), after multi-agent audit of the existing boards found duplicates, missing owners, and no true DB replication in Monday.

**Tags**: #newman #crm #monday #migration #planning
**Created**: 2026-07-11
**Source**: mini session 84da500d-7512-4280-a980-b39903b94857.jsonl, user jesus

---

## Content
- Ask (part of newman-redesign): improve Newman's CRM "tuesday", migrate/structure client data better, and expose a replicated dataset to clients and salesmen **without exposing the main database**; improve the prompt, plan, and generate issues via several agents.
- Deliverable: Monday board **CRM Redesign — Migration** → https://newman-re.monday.com/boards/18421500142 — 33 issues in 6 phase groups with columns Priority / Owner / Estimate(days) / Acceptance Criteria / Dependencies.
- P0 Audit & Freeze (5): resolve canonical Deals board, full column export, automation inventory, backup, freeze.
- P1 Canonical Model (7): ER model, standardize stages, dedupe solar columns, fix Contacts Type, add Owner column, naming/SSOT, Quotes schema.
- P2 Migration & Dedupe (9): staging + field map, merge 3 duplicate boards, reconcile NPA, relocate Accounts, dedupe Contacts, fix broken relations, backfill owners.
- P3 Replica Workspace & Access (5): isolated client workspace, safe-column mirror boards, salesman row-level perms, client guest scoping, access matrix.
- P4 Automations & Sync (4): one-way master→replica sync, rebuild legacy automations, data-quality guards, drift/leakage validation.
- P5 Cutover & Governance (3): archive legacy, governance doc, 30-day audit.
- Key finding: Monday has **no real DB replication** — the "replica" must be a separate workspace with one-way-synced, safe-column mirror boards.
- Plan saved to project memory.

## Related Notes
- [[newman-rebuild-project]]
- [[2026-07-11-invoice-review-ui-and-cosecha]]
