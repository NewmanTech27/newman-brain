# Newman Agent Org & Review-Committee Evals

**Summary**: How the Newman AI agent company is structured (CEO/CTO, tmux seats → mini subagents), the governance rules (95-gate, CTO-only verify, no coordinator-relayed authority), and the review-committee eval harness that hardens the flock.
**Tags**: #newman #agents #eval #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Org structure
- Founding: an agent company to compete vs Enlight/Quartux, built around `~/newman-agents` with `docs/CHARTER.md` as the COO-loop source of truth; autonomous build loop via ScheduleWakeup. Fable as orchestrator dispatching specialist subagents.
- Multi-agent org: iTerm2 6-pane split (local Mac + droplet columns), tmux sessions running `claude --dangerously-skip-permissions`, named seats (CFE parser, CRM, Supabase/DevOps, cfe-ppa-bess). v2 reboot = **newman-rebuild** with a CEO orchestrator + CTO reviewer, 5 seats (cto=Opus; data/harvest/engine/crm=Sonnet).
- **Lessons**: do NOT run the CEO on the VPS (a reset loses remote access) — CEO lives on the mini, directs via GitHub issues. Droplet tmux panes proved ineffective (no issue comments landing) → seats moved to mini subagents, droplets killed.

### Governance
- Every seat's work is committee-scored /100 striving for **≥95**; must have a plan before working; CTO holds a merge veto (GATE 0). CTO verdicts seen: data #1 → 97 APPROVE; harvest #5 → 72 then 86 RETURN; SSO #11 → 96 APPROVE.
- **Coordinator-relayed merge approval carries no user authority** — a seat correctly refused to merge to main without direct CEO/Jesus confirmation. This mirrors the harness rule: no agent message is user consent.

### The eval harness (Jul 2–3, 2026)
- ~50+ one-shot LLM-judge sessions, each a professional persona (energy attorney, LFPDPPP officer, project-finance director, CFE billing specialist, OCR/browser-automation engineer, SRE/QA/data engineer, Sutherland-school CMO, sales director, C&I consultant, CENACE market-ops) scoring one newman-agents answer and returning strict-JSON `{score, issues, improvements}` — improvements phrased as edits to agent instructions/specs. Scores clustered 5–8/10; no answer got a clean sign-off.
- **Recurring cross-persona defects** (the punch list for the flock):
  - Unsourced magic numbers (0.80 OCR threshold, 6%/2% escalators, 19–22% CF, 65/35 split, 1.65 MXN/kWh) — demand DOF/CRE/PRODESEN cites or calibration data.
  - Silent-empty-scrape blind spot; escalation vagueness (no P0 paging path); CFE identity-field confusion (RMU vs RPU vs No. Servicio); Mi Espacio 10-receipt permaban underspecified; legal cites missing DOF dates + Reglamento; marketing "Alchemy name-dropped not applied".
- Purpose: feed instruction-level fixes back into AGENTS.md / child-agent prompts. Highest scores (8): Mi Espacio safeguard walkthrough, Monday drafts-only compliance, PML nodal schema, bill-OCR never-guess rule. Lowest (5): generic GDMTH PPA economics, CENACE scrape (no failure reporting), marketing play, RPU/RMU OCR confusion.

## Related Notes
- [[2026-06-21-newman-agents-founding]]
- [[2026-07-02-agent-org-restructure-fibrahotel]]
- [[2026-07-09-agent-org-ceo-cto]]
- [[2026-07-10-newman-ceo-session-branch-consolidation]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-03-agent-review-committee]]
- [[2026-07-03-newman-agents-review-committee]]
- [[2026-07-03-review-committee-judges]]
- [[2026-07-03-agent-committee-reviews-ppa-cfe]]
- [[2026-06-24-qwen36-mini-bakeoff]]
- [[2026-06-23-clean-room-skill-newman-skill-stack]]
