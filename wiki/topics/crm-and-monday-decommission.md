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

### Tuesday origin & hardening (VPS, Jul 07–09)
- Trigger: monday seat audit — jesus is core-only, no API path to a paid CRM seat (billing UI only), MCP writes 403 → next-day decision to clean-room replace monday with "Tuesday — the CRM after monday" ([[2026-07-07-monday-mcp-seat-audit]]).
- Built by an autonomous `/loop` under a multi-agent committee score (31→88/100, DD/underwriting/AML/RAROC iterations); deploys from `dev` to droplet newman-crm (167.172.142.136), pgTAP CI, OpenRouter assistant. This one session cost $1,587 — 64% of the org's token bill ([[2026-07-08-tuesday-crm-committee-loop]]).
- Daily-huddle agent: OpenRouter edge fn reads huddle minutes from Drive → kanban comments + a ToDos board with detail drawer ([[2026-07-08-huddle-todos-agent]]).
- Input-surface spec verdict (56/100): idempotency/access-control strong, but the WhatsApp edge fn can **silently drop a scarce lead** (no retry, no trace) — GAP-01, top revenue leak ([[2026-07-09-tuesday-inputs-spec]]).

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
- [[2026-07-07-monday-mcp-seat-audit]]
- [[2026-07-08-tuesday-crm-committee-loop]]
- [[2026-07-08-huddle-todos-agent]]
- [[2026-07-09-tuesday-inputs-spec]]
