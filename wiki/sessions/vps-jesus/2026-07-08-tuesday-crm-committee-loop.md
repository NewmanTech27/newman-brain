# Tuesday CRM: /loop Build to Replace monday.com (Committee-Scored)

**Summary**: Autonomous /loop built and deployed "Tuesday" — a self-hosted Supabase CRM replacing monday.com at tuesday.newman.re — iterating features under a multi-agent committee score (31→45→85→88/100 toward a 99 target).
**Tags**: #newman #tuesday-crm #supabase #loop #ci-cd #due-diligence
**Created**: 2026-07-08
**Source**: newman-vps sessions 81cef301-3585-40f2-b7a5-cd5a6f7c2cd6.jsonl (main, 26 MB) and 0ee769c2-e549-4531-9800-7d8de02d1dba.jsonl (resume helper), user jesus; consolidated

---

## Content
- Origin: audit of monday.com usage/cost → decision to clean-room a Supabase CRM ("Tuesday — the CRM after monday") with Newman UI/UX + shadcn, full monday parity, MCP + in-app assistant.
- Deployment constraints from Jesus: NOT Vercel — Cloudflare + GitHub Actions; dedicated droplet `newman-crm` (167.172.142.136); repo = newman-architecture, deploys from `dev` branch; assistant uses OpenRouter, not Anthropic.
- Auth: Google OAuth via Supabase restricted to @newman.re; login-loop bug (`login.newman.re/null` after second login) fixed; SSO unified so all *.newman.re reverse proxies redirect to login.newman.re.
- Feature stream (mid-loop asks): kanban card drag between columns, smaller cards + one-finger drag/two-finger scroll, live regex search on pipeline, Google Contacts migration, two contact tables, custom columns, full deal-detail page, ToDo subtasks, left-sidebar nav.
- Committee mechanism: multi-agent committee compares Tuesday vs Twenty/open-source CRMs for an energy financing/EPC company (heavy due-diligence lens), names the highest-impact gap; each iteration builds+deploys it, re-scores.
- Iterations 1–5 (per resume session): DD foundation → underwriting → UBO/sanctions → DD adjudication → RBAC (31→45). Later run: it-45 problem-loan workout (IFRS9), it-46 embedded AI copilot, it-47 AML 3-lines-of-defense, it-48 unified inbox /bandeja, it-49 RAROC + concentration hard gate /limites, it-50 transaction monitoring /monitoreo (85→88).
- CI: pgTAP suite, 31 assertions / 13 synthetic use cases guarding every push; DB migrations applied direct to prod Supabase (bwudgrwfwjdbvqhgbwty) via psql/MCP; web deploys via git push dev → Actions → droplet.
- Gotcha: GitHub runner backlog cancels queued deploy jobs — re-trigger, not a code failure.
- Iteration 6 (never committed): replace blended-tariff underwriting proxy with CFE-consumption-grounded after-tax savings (real client.bill actuals + ISR/depreciación inmediata).
- Resume command recorded: `claude --resume 81cef301-...` from /home/jesus.
- Cost note (from token audit): this single session cost ~$1,587 — 64% of the org's $2,475 bill.

## Related Notes
- [[2026-07-07-monday-mcp-seat-audit]]
- [[2026-07-08-excalidraw-sso-crm-prod]]
- [[2026-07-09-token-audit-baseline]]
