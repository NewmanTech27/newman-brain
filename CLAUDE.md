# cfe-brain — schema

The compiled knowledge base for Newman Energy. Four agent sessions feed it; no human writes it by hand.
Obsidian is the IDE. This file is the schema. The wiki is the codebase.

## Structure

- `raw/` — unprocessed sources: transcripts, exported code, commit logs, schema dumps, PDFs, screenshots
- `raw/processed/` — sources already compiled into the wiki
- `wiki/` — atomic pages, one idea each, densely `[[linked]]`
  - `wiki/cfe-bill-parser/`, `wiki/cfe-ppa-bess/`, `wiki/supabase-devops/`, `wiki/tuesday-inputs/` — per-service
  - `wiki/concepts/` — cross-cutting ideas belonging to no single service (punta, DSCR, CFDI, RLS, WAF)
- `index.md` — catalog of every page
- `log.md` — chronological ingest history

## This is an ENGINEERING wiki, not a research wiki

Karpathy's original compiles papers and articles. Those do not change underneath you. **Code does.**

So every factual claim about the system carries provenance and a freshness stamp, or it is not a claim.

### Page frontmatter (required)

```yaml
---
title: <page title>
service: cfe-bill-parser | cfe-ppa-bess | supabase-devops | tuesday-inputs | concept
kind: descriptive | normative | decision | finding | question
sources: ["newman-architecture/agents/design-engine/sizing.py:41", "commit a81c43c"]
verified_at: <ISO date>
verified_against: <commit SHA of newman-architecture when written>
confidence: verified | inferred | unverified
---
```

- `descriptive` — what the code does today. Cites `file:line`. Rots when code changes.
- `normative` — what the system MUST do. Sourced from OUTSIDE the implementation: regulation, the SAT CFDI schema, the monday.com reconciliation contract, physics, textbook finance definitions, or Jesus. Does not rot.
- `decision` — a choice made, why, and the alternative rejected. Never rots. The most valuable kind, and the kind that is always lost.
- `finding` — a defect, gap, or contradiction discovered.
- `question` — something nobody knows yet. Legitimate. File them.

**A `descriptive` page can never justify a `normative` one.** Code is not its own requirement. This is the single most important rule in this repo.

## What to preserve

**Everything worth preserving feeds the graph.** If a session learns something that would be expensive to rediscover, it becomes a page. Before a session ends, it files what it learned.

Preserve:

- **Decisions and their rejected alternatives.** Why `finance.ts` is deliberately separate from the monday-reconciled view. Why the 10%-vs-12% discount-rate quirk is kept. This is what dies first and costs most.
- **Hard-won operational knowledge.** The CFE WAF, the captcha path, the >10-recibo block, the exact-name-match requirement. Anything that took an afternoon to discover.
- **Invariants and constraints.** `kWp_DC <= 839.41`. PV cannot shave punta. `subtotal * 1.16 ≈ total`.
- **Findings and defects**, including ones not yet fixed.
- **Dead ends.** What was tried and did not work, and why. Nothing is re-attempted more often than a documented failure that was never documented.
- **Open questions.**

Do not preserve: secrets, client PII, real RPUs, transient chatter, anything reconstructible in seconds from `git log`.

## INGEST — on "ingest this", or a file appearing in `raw/`

1. Read the source completely.
2. Extract core ideas as separate atomic pages — one idea per page.
3. Each page: title, one-sentence summary, the idea in plain words, full attribution, frontmatter above.
4. Link each new page to related existing pages with `[[wikilinks]]`. Search the whole wiki first — connecting to what is already there is the entire point.
5. A page linked from 3+ pages is a hub. Flag it.
6. Add to `index.md`. Append to `log.md` with date and source.
7. Move the source to `raw/processed/`.

## QUERY — when asked a question

- Search all of `wiki/` before answering.
- Cite the pages supporting the answer.
- **If pages conflict, surface the conflict. Never silently pick one.** A `descriptive` page contradicting a `normative` page is a defect in the code — file it as a `finding`.
- File a worthwhile answer back as a new page. The output becomes input.

## LINT — on "lint the wiki". Weekly.

- Contradictions between pages
- **Stale `descriptive` pages**: `verified_against` no longer matches `git rev-parse HEAD`. Re-verify, or mark `confidence: unverified`. This is the engineering-specific lint, and the one that matters most here.
- Claims superseded by newer commits
- Orphan pages with no inbound links
- Gaps: topics referenced in `[[links]]` but never written
- `unverified` pages that have sat unverified too long

Report everything. Never auto-delete.

## Rules

- One idea per page.
- Write plainly and directly. Not in the source's voice.
- Never lose attribution. A claim without a source is a rumour.
- Surface non-obvious connections aggressively.
- Prefer a `question` page over a confident guess.
- Secrets never enter this repo: no PATs, no service-role keys, no client PII, no real RPUs.
