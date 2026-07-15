# Monday.com stale-lead follow-up blocked on OAuth, no fabrication

**Summary**: Sales-ops drill ("three leads past follow-up SLA, one price objection") dispatched a monday-lead-followup agent that correctly refused to fabricate lead data when the Monday.com MCP connector was unauthorized.
**Tags**: #newman #crm #monday #agents #sales
**Created**: 2026-07-02
**Source**: macbook session cad8b968-c54e-47d0-892c-75b7e5c3cf4e.jsonl (newman-agents project), user jesus

---

## Content
- Scenario: 3 leads in Monday past the follow-up SLA, one raised a price objection; asked what the agent does.
- Orchestrator dispatched a monday-lead-followup background agent for the SLA sweep + objection-reply draft.
- Blocker: Monday.com MCP tools unavailable — OAuth authorization for the connector never completed in the session, so no board read possible.
- Agent explicitly refused to fabricate lead names, tariffs, savings figures, or objection text (Newman anti-fabrication doctrine: verified numbers only; outreach on fictional data worse than none).
- Two recovery paths offered: (1) user authorizes the Monday connector (claude.ai connector settings or /mcp) and the pull re-runs, or (2) user pastes the 3 lead records (stage/tariff/savings/objection) and drafts are produced without sending.
- Gotcha worth remembering: Monday MCP in newman-agents sessions needs OAuth per session/connector setup before any pipeline automation works.

## Related Notes
- [[2026-07-03-review-committee-judges]]
