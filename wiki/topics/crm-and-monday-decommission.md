# CRM & the Monday.com Decommission

**Summary**: The arc of Newman's CRM — Intersolar contacts loaded into Monday/Google directory, the OAuth/403 pain, the "tuesday" CRM rebuild, and the final decision to decommission Monday.com and export everything into newman-brain.
**Tags**: #newman #crm #monday #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Monday.com history
- Intersolar 2,629 exhibitor contacts loaded into a dedicated **Intersolar board** (id 5099737762) in the CRM workspace — kept separate so the legacy Contacts board wasn't diluted. Board ended with 2,693 items vs 2,629 unique (64 dup-name rows to prune).
- **Monday MCP is fragile**: needs per-session OAuth; a stale-lead follow-up drill was blocked when the connector was unauthorized (agent correctly refused to fabricate leads); the dedupe was blocked 2+ hours by a persistent **403 `mcp_request_blocked`** connector block (not a throttle) requiring an `/mcp` reconnect.
- Monday has **no real DB replication** — a "replica for clients/salesmen" must be a separate workspace with one-way-synced, safe-column mirror boards. Captured in the 33-issue, 6-phase "CRM Redesign — Migration" board (P0 Audit/Freeze → P5 Cutover/Governance).

### tuesday CRM (the rebuild)
- Self-hosted CRM at tuesday.newman.re, SSO-gated via newman-sso; invoice review UI at **review.newman.re** (image/PDF left, extracted data right, confirm/correct CRUD on `pipeline.twilio`); **/cosecha** RPU-harvest monitoring page backed by `public.crm_web_rpu_harvest()` SECURITY DEFINER (13 RPUs at ship).
- Bug learned: `psql -c` does not interpolate `:'var'` — the `/api/confirm` path had never actually worked (500).

### Decommission (2026-07-15)
- Monday.com decommissioned as the CRM tool. Full export pushed to newman-brain (`355d9bd`): **70 boards, 3,138 items**, zero failures, into `crm/monday-export/` with README + SUMMARY (pipeline by stage, Yazaki 48 MWp portfolio, migration plan). newman-rebuild's 123 issues also mirrored into the repo (`22c3ccc`). newman-brain becomes the durable knowledge store for all future Claude sessions.

## Related Notes
- [[2026-07-05-monday-intersolar-board-contacts]]
- [[2026-07-05-monday-intersolar-dedupe-blocked]]
- [[2026-07-02-monday-stale-leads-blocked]]
- [[2026-07-11-tuesday-crm-redesign-board]]
- [[2026-07-11-invoice-review-ui-and-cosecha]]
- [[2026-07-15-monday-decommission-newman-brain]]
- [[2026-07-03-gws-auth-intersolar-contacts]]
