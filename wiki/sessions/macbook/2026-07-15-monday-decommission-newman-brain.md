# Monday decommission: full export to newman-brain + session-mining kickoff

**Summary**: Decommissioned monday.com as the CRM tool — exported all 70 boards / 3,138 items into the newman-brain repo, mirrored newman-rebuild issues, and launched the Karpathy-style wiki distillation of 117 Newman sessions.
**Tags**: #newman #crm #monday #newman-brain #wiki #knowledge-base
**Created**: 2026-07-15
**Source**: macbook session bf5241e4-50a1-4a9e-9e2b-7ca2649b3708.jsonl, user jesus

---

## Content
- Decision: decommission monday.com ("tuesday" CRM work reviewed on dev/staging/prod first); newman-brain becomes the durable knowledge store, accessible to all future Claude sessions.
- Monday export pushed (`355d9bd`): 70 boards, 3,138 items, zero failures, into `crm/monday-export/` with README index + SUMMARY.md (pipeline by stage, Yazaki 48 MWp portfolio, migration plan).
- newman-rebuild issues mirrored (`22c3ccc`): 123 issues into `issues/newman-rebuild/`.
- Session mining: 1,338 raw matches on the MacBook filtered to 117 sessions with real Newman content; 6 agents distilling them into Karpathy-style notes under `wiki/sessions/macbook/` (template `wiki/_templates/note.md`: Title, Summary, Tags, Created, Source, [[links]]); topic synthesis planned after.
- Wiki structure follows Andrej Karpathy's LLM-wiki idea: plain markdown personal knowledge base an LLM can reason over.
- Blocked at session time: mini + newman-vps unreachable (tailscale re-auth needed) — mario's sessions on those hosts pending harvest.

## Related Notes
- [[2026-07-09-agent-org-ceo-cto]]
