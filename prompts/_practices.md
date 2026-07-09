# Behavioral guidelines

Reduce common LLM coding mistakes. These bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask: "Would a senior engineer call this overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line traces directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Shared Working Tree

Three sibling Claude sessions run on this VPS, in the same repos, right now.

- Run `git status` before you edit. The tree changes under you.
- Work on a branch off `dev`. Never force-push. Never rewrite a shared branch.
- Uncommitted change exists: `deploy/curvas/current/index.html`. Do not discard it.
- Coordinate merges through the `supabase-devops` session. It is the last gate.
- Never reboot the box. It kills every session.
- A GitHub PAT sits in `~/.config/gh/hosts.yml`. Never print, echo, or commit it.

## 6. Feed the Knowledge Graph

`~/cfe-brain` is the compiled knowledge base. Read its `CLAUDE.md` for the schema.

**Everything worth preserving feeds the graph.** Something that would be expensive to rediscover becomes a page — decisions and their rejected alternatives, hard-won operational knowledge, invariants, findings, dead ends, open questions.

- Before you start: query the wiki. Do not rediscover what is already known.
- As you work: file `decision` pages when you make a choice, `finding` pages when you find a defect.
- Before your session ends: ingest what you learned. An un-filed insight is a lost one.
- Never file secrets, client PII, or real RPUs.

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites from overcomplication, and clarifying questions arrive before implementation rather than after mistakes.
