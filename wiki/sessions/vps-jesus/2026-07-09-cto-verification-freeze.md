# CTO Session: Verify-Claims-Against-Artifacts, sizing.py Live Exposure, Client-Facing Freeze Spec

**Summary**: The CTO agent instituted artifact verification after supabase-devops claimed pages it never wrote, confirmed sizing.py is LIVE (DEL-5), found finance.ts also diverges, and spec'd the reversible DB-level REVOKE freeze of client-facing proposal sends — then verified migrations 016/017.
**Tags**: #newman #agent-org #cto #del-5 #finance #verification
**Created**: 2026-07-09
**Source**: newman-vps session 03010584-a7b0-47de-bd19-ae91774487b4.jsonl (cto seat), user jesus

---

## Content
- Standing rule created after a P0 integrity failure: supabase-devops logged 3 wiki pages in log.md that did not exist. New dimension for every agent: ls every claimed file, git log every claimed commit, run every claimed-passing test. "A claimed artifact that does not exist means the self-score is unverifiable."
- Priority trace: design-engine/sizing.py IS wired into a live path (YES with file:line) → live DEL-5 exposure (engine dropped umbral + inverted PV→BESS charging while pricing real deals).
- Blast radius: checked whether proposal-builder auto-sends to clients or a human approves.
- finance.ts check: crm-web/lib/finance.ts (computeFinance) verified against golden RPU 780881200029 (baseline $30,157,371 / Ahorro $7,083,252 / 23.5%) → diverges like sizing.py → client-facing exposure escalated.
- Containment: Jesus authorized gating crm_web_send_proposal. Least-invasive reversible mechanism = DB-level `REVOKE EXECUTE` (no deploy, one-step GRANT rollback): crm_web_send_proposal FROM authenticated, crm_proposal_public FROM anon, crm_sign_proposal FROM anon (e-sign RPC from proposal-sign.tsx:125). Decision page filed noting these are runtime privilege changes NOT in supabase/migrations — must not become silent drift.
- Independently verified cfe's diagnoses and reviewed 016 (confirmed exact/safe; flagged wrong cause attribution in header) and 017 (APPROVED: strict superset [new,processing,done,failed]+[pending,needs_ocr,needs_name]; re-derived the full status vocabulary from pg_proc functions + mark_bulk_pdf call sites; ruled out 'awaiting_confirmation' as collection_request's).
- Coordination discipline: CTO never messages other agents directly — everything routes through the CEO; token discipline (attack input tokens, grep before read, caveman for chatter only, never for verdicts/specs).

## Related Notes
- [[2026-07-09-cfe-real-invoice-claim-media]]
- [[2026-07-09-sizing-materiality]]
- [[cfe-brain-vault]]
