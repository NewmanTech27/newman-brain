# Fable→Opus Handoff Tooling (/handoff command)

**Summary**: Set up a reusable `/handoff` slash command so Fable 5's reasoning can be captured and handed to Opus for execution, plus guidance on model-switching and CLAUDE.md for durable rules.
**Tags**: #newman #tooling #fable #opus #handoff #orchestration #meta
**Created**: 2026-07-12
**Source**: newman-vps session 4362aa4d, user mario

---

## Content
- Ask: how to copy Fable 5's reasoning to Opus to get better use of it.
- Three mechanisms delivered, cheapest→most durable:
  1. **Switch models mid-session** — run hard thinking (planning/debug/architecture) on Fable 5, `/model` to Opus in the same session; Fable's analysis stays in context.
  2. **`/handoff` command** (created, available every session) — Fable distills decisions, the *why*, rejected alternatives, gotchas, and a verifiable step plan into a markdown; start an Opus session with "Read HANDOFF.md and execute the plan. Don't re-litigate the decisions in it."
  3. **CLAUDE.md / memory** — for recurring judgment Opus gets wrong (e.g. "never touch Supabase main", "check RPU→client map before querying"), one-line rules every session inherits regardless of model.
- Key principle: **conclusions are cheap for Opus to consume; rejected alternatives and gotchas are the expensive part of reasoning** — the handoff template emphasizes those.
- `/export` dumps the whole conversation (noisy); distilled handoff transfers better.
- This is the doctrine behind the "orchestrate in Fable, execute in Opus/Sonnet" pattern used across the GEPP, Pueblo Bonito, and solar-charge sessions.

## Related Notes
- [[2026-07-14-gepp-solar-charge-bess-dispatch]]
- [[2026-07-13-pueblo-bonito-desaladora]]
- [[newman-agent-org]]
