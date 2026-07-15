# Token Audit Baseline: $2,475 Bill, Cache-Read Is 66%, One Session Is 64%

**Summary**: The research agent measured all 431 VPS transcripts with a new token_audit.py — the spend driver is per-turn carried context (median ~147k tokens), not cache misses, and the tuesday /loop session alone cost $1,587.
**Tags**: #newman #agent-org #tokens #cost #claude-code
**Created**: 2026-07-09
**Source**: newman-vps session 0d508933-d6a9-4d32-9f80-daf69f4e83fa.jsonl (research seat), user jesus

---

## Content
- Tool: `~/cfe-brain/vault/tools/token_audit.py`; finding page `2026-07-09-token-audit-baseline` in the vault wiki.
- Measurement bug caught: the harness re-logs each API message on 1–8 transcript lines with identical usage — naive counting doubles totals; dedupe by message.id → 4,168 real assistant turns.
- Spend split ($2,475 at Opus 4.8 rates): cache_read 1.098B tokens = $1,647 (66%); cache_creation 1h $340 (14%); output $308 (12%); cache_creation 5m $151 (6%); fresh input $30 (1%).
- Cache hit rate 98.3% — prefix churn is NOT the problem; the waste is context size × turn count (median 146,800-token context per turn).
- Session 81cef301 (the tuesday CRM /loop) = $1,587, 1,751 turns, 988M cache_read — 64% of the whole bill.
- Punchline (from the flock drain): a rebuild on Opus/high-effort with fat per-turn context reproduces the bill regardless of writing style — attack the median 147k carried context or you've optimized nothing.
- Also surfaced a pre-existing INT-2 P0: tuesday-inputs' crm-rls-rbac-ordering-trap was logged but never written.

## Related Notes
- [[2026-07-08-tuesday-crm-committee-loop]]
- [[2026-07-10-flock-overnight-golden-proof]]
