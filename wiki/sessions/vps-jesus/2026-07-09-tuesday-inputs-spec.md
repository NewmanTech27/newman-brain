# tuesday-inputs Spec: CRM Input-Surface Audit (56/100, WhatsApp Silent Drop)

**Summary**: The tuesday seat resolved what tuesday.newman.re is and specced its input surface — strong on idempotency/access-control but the WhatsApp edge can silently drop a scarce lead (GAP-01), making it the top revenue leak.
**Tags**: #newman #tuesday-crm #agent-org #spec #whatsapp-intake
**Created**: 2026-07-09
**Source**: newman-vps sessions 8dcab40b-07d5-4fb9-a602-0ac44a9009d8.jsonl (main) and 7f5d1792-a32c-48bc-832e-cc2d42bd0a47.jsonl (earlier boot, same contract), user jesus; consolidated

---

## Content
- Contract: Phase -1 query the knowledge graph first (wiki was empty; three raw sources + commit log resolved that tuesday.newman.re = the CRM), then Phase 0 assess; stop at spec, no code.
- Deliverable: `docs/specs/tuesday-inputs.md` — Part A descriptive with file:line, Part B 13 NRMs, Part C 9 gaps, score 56/100, 6-step plan; commit 5f6f804 on isolated worktree branch `spec/tuesday-inputs` off dev@a81c43c, deliberately not pushed.
- Verdict: idempotency 14/15 and access control 13/15 strong; durability 10/30 and observability 1/5 weak — WhatsApp edge fn can drop a lead silently with no retry and no trace; anonymous proposal endpoints lack expiry/rate-limit/identity guards.
- NRM-13 sourced from Jesus ("leads are scarce" → High) pins GAP-01 (whatsapp-intake hardening) as top Phase-4 fix.
- 3 wiki pages filed: tuesday-newman-re-is-the-crm, whatsapp-intake-silent-drop, crm-rls-rbac-ordering-trap — hit the "two wiki roots" bug (repo-root wiki/ vs authoritative vault/wiki/) that also bit supabase-devops; pages relocated by the single-root fix.
- Token discipline directive recorded (practices §7): attack INPUT tokens; query index.md, never read the tree; grep before read; caveman for chatter only, never for specs/verdicts/evidence.

## Related Notes
- [[2026-07-09-cfe-real-invoice-claim-media]]
- [[2026-07-08-tuesday-crm-committee-loop]]
