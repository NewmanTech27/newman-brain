# Resume Intersolar board insert + dedupe (monday MCP 403-blocked)

**Summary**: Resumed the Intersolar monday.com bulk-insert to full 2,629 contacts, but the follow-up dedupe was blocked by a persistent monday MCP 403 requiring an /mcp reconnect.
**Tags**: #newman #crm #agents
**Created**: 2026-07-05
**Source**: macbook session 22b8bb76-12dc-4993-a201-0784f0b5d9cb.jsonl, user jesus

---

## Content
- Continuation of the debfaa17 session (prior process exited mid-insert, in-process state lost).
- Resume agent confirmed all 2,629 source contacts present on Intersolar board 5099737762.
- Board had 2,693 items vs 2,629 unique names → 64 duplicate-name rows to delete (keep one per name, target items_count 2,629).
- Dedupe repeatedly failed: monday API returned persistent **403 (`mcp_request_blocked`)** for 2+ hours — a connector block, not a passing throttle.
- Retries backed off then stopped; action needed from user: `/mcp` reconnect claude.ai monday.com, then finish dedupe. The 64 dups are cosmetic; board fully usable.

## Related Notes
- [[2026-07-05-monday-intersolar-board-contacts]]
