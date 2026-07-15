# monday.com MCP Reorg Attempt + CRM Seat Audit

**Summary**: Tried to reorganize monday.com boards via MCP but hit a hard CRM-seat wall — jesus has no paid CRM seat and there is no API path to assign one.
**Tags**: #newman #monday #crm #mcp
**Created**: 2026-07-07
**Source**: newman-vps session 228ab755-09e8-4dda-ab9e-6a52cd7d5c28.jsonl, user jesus

---

## Content
- Goal: reorg all monday boards; auto-create a Deal (with researched description) when invoice data is collected.
- monday MCP connector flaky (repeated disconnect/reconnect until re-auth succeeded).
- Seat reality: 3 active CRM members (Mario, Jonathan, Chandel — all active daily); "Newman Admin" idle since Apr 29 but view-only, not reclaimable.
- jesus is `core`-only: board/workspace subscriber adds succeeded but writes still 403 — monday does NOT auto-provision paid CRM seats via API, and there is no API to assign one; billing UI only.
- Recommendation recorded: have Mario (admin, board owner) run writes rather than pay for/steal a seat.
- Side effect: probes added jesus as subscriber to CRM workspace + Deals board.
- This cost/usage frustration seeded the next-day decision to clean-room replace monday with the "Tuesday" Supabase CRM.

## Related Notes
- [[2026-07-08-tuesday-crm-committee-loop]]
