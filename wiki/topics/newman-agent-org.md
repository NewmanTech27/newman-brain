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

### The VPS flock (Jul 09–10)
- Seven tmux seats on newman-vps (ceo, cto, cfe, tuesday, data, ppa, research); CEO is sole router — the CTO never messages other agents directly. **GATE 0** froze all merges until Jesus's canonicity ruling: dev+main is a **fork not drift** (main = CFE collector on the VPS, dev = CRM on the newman-crm droplet), so the ruling was preserve-both merge on `integration/gate0`, never reset/discard ([[2026-07-09-ceo-org-real-invoice-gate0]], [[2026-07-09-supabase-devops-gate0]]).
- **Verify-claims-against-artifacts rule** (born from a P0: supabase-devops logged 3 wiki pages that didn't exist): ls every claimed file, git log every claimed commit, run every claimed-passing test — "a claimed artifact that does not exist means the self-score is unverifiable" ([[2026-07-09-cto-verification-freeze]]).
- Client-facing freeze mechanism: DB-level `REVOKE EXECUTE` on crm_web_send_proposal / crm_proposal_public / crm_sign_proposal — reversible, no deploy, but a runtime privilege change outside migrations (must not become silent drift).
- **Token audit baseline** ($2,475 bill, 431 transcripts): 66% of spend is cache_read; cache hit rate 98.3% — the cost driver is the **median 147k-token carried context × turn count**, not cache misses; one /loop session (tuesday CRM) = $1,587 = 64% of the bill. Dedupe transcript usage by message.id ([[2026-07-09-token-audit-baseline]]).
- Doctrine from Jesus: "edge function maximalist" — prefer Supabase edge functions for logic. Overnight main-effort produced the golden extraction proof 18/18 and the sizing.py fix; every agent drained a one-sentence handoff for the rebuild team ([[2026-07-10-flock-overnight-golden-proof]]).
- Next-gen pattern: **GitHub-issue-driven seats** (newman-rebuild data/cto/engine/harvest/crm) booting from seat_boot.md, taking CEO direction from issue comments, "Done = artifact link" ([[2026-07-10-newman-rebuild-seat-org]]).
- **Fable→Opus handoff doctrine** (Mario): orchestrate/reason in Fable, execute in Opus/Sonnet; `/handoff` command distills decisions + rejected alternatives + gotchas (the expensive parts) into a HANDOFF.md the executor must not re-litigate; CLAUDE.md one-liners for recurring judgment ([[2026-07-12-fable-opus-handoff-tooling]]).

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
- [[2026-07-09-ceo-org-real-invoice-gate0]]
- [[2026-07-09-cto-verification-freeze]]
- [[2026-07-09-supabase-devops-gate0]]
- [[2026-07-09-token-audit-baseline]]
- [[2026-07-09-tuesday-inputs-spec]]
- [[2026-07-10-flock-overnight-golden-proof]]
- [[2026-07-10-newman-rebuild-seat-org]]
- [[2026-07-12-fable-opus-handoff-tooling]]
