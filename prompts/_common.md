# Operating contract (all sessions)

## Read these first
1. `~/prompts/_practices.md` — behavioral guidelines. Think before coding; simplicity first; surgical changes; goal-driven execution. **These are binding.**
2. `~/cfe-brain/vault/CLAUDE.md` — the vault schema and domain invariants. **Authoritative.** (`~/cfe-brain/CLAUDE.md` is a thinner scaffold schema; where they differ, the vault wins.)

## Phase -1 — QUERY THE GRAPH. The graph is NOT empty.
`~/cfe-brain/vault/` is an imported, mature knowledge vault: **91 wiki pages** compiled by a prior agent working out of `/home/mario/CFE Brain`.

**Read `~/cfe-brain/vault/CLAUDE.md` before anything else.** It carries:
- a **domain invariants table** (GDMTH umbral 0.57, GDMTO FC 0.55, SIN punta 20:00-22:00 summer / 18:00-22:00 winter, 22:00-24:00 = Intermedio NOT Base, BC/BCS no Base in summer, DG permit-free ceiling **< 0.7 MW** under LSE 2025 — any doc citing 0.5 MW is stale)
- the **deterministic doctrine**: numbers come from the engine, logic comes from the wiki, never from training memory
- the **sacred golden test**: RPU 780881200029, peso-exact, baseline $30,157,371, Ahorro $7,083,252 / 23.5%, 18 checks
- **fact tiers**: say whether each claim is (a) confirmed by primary source, (b) engine-derived, or (c) an assumption

Also read `~/cfe-brain/vault/wiki/overview.md` (thesis + open gaps) and `~/cfe-brain/vault/wiki/index.md` (catalog).

These invariants are **normative**. They are your Part B, already written, already sourced. Do not re-derive them; cite them.

Do not rediscover what has been filed. Search `~/cfe-brain/vault/wiki/` first, every time.

## Phase 0 — ASSESS. Do not write code yet.
Establish the TRUE current state of your service.

1. Read any prior transcripts/context you can find.
2. Inventory the code: `~/newman-architecture` (branches main/dev/staging/crm-platform, currently `dev`) and `~/newman-landing`.
3. Inventory GitHub: `gh` is authed as NewmanTech27. Open issues, recent PRs, CI status, `main` vs `dev` drift. **Read commit messages and PR descriptions — they are the richest surviving record of INTENT.**
4. Inventory Supabase: `supabase` CLI installed; `~/newman-architecture/supabase` holds migrations + edge functions.
5. Hunt for existing specs. Check `docs/`, git history (`git log --all --diff-filter=D -- "*.md"` for deleted docs), other branches, the GitHub repo wiki/issues. If a doc is referenced but missing, say so explicitly.

Output: a written STATUS REPORT — what exists, what works, what is broken, what is undocumented, what contradicts what.

## Phase 1 — WRITE THE SPEC
There is no usable spec for your service. You are writing it. Land it at `docs/specs/<your-service>.md` on a branch off `dev`.

**The spec has two strictly separated halves. Do not blur them.**

### Part A — DESCRIPTIVE (derived from code)
What the system does today. Reverse-specced from the implementation. Every claim cites `file:line`.
This half is **non-normative**. It is documentation, not a requirement. It CANNOT be used to score the code — code always satisfies a spec written from itself. Mark it clearly.

### Part B — NORMATIVE (derived from intent)
What the system MUST do. **Sources must be independent of the implementation:**
- commit messages and PR descriptions (why a change was made)
- external contracts: the monday.com reconciliation, CFE tariff rules and regulation, Supabase schema constraints
- physical/regulatory invariants: e.g. exempt regime `kWp_DC <= 839.41`, PV cannot shave punta
- business requirements you can evidence
- Jesus, when you cannot source it otherwise — ASK, do not guess

Each normative requirement gets: a stable ID (`NRM-01`), the requirement, its source, and how it is VERIFIED (a test, a query, a command). A requirement with no verification method is not a requirement — it is a wish. Say so.

### Part C — GAPS
Where Part A and Part B disagree. **This is the deliverable.** Each gap is a defect with a severity.

## Phase 2 — SCORE (committee rubric)
Score the CURRENT state out of 100 as a skeptical committee would, **against Part B only**. Never against Part A.
Named criteria, weights, and concrete evidence per criterion (file paths, commit SHAs, failing commands, missing tests). A criterion you cannot evidence scores LOW, not high.

The bar is 95/100. An inflated score is a failure of the exercise. If the current state is a 42, say 42. Expect a low first score — that is the point.

## Phase 3 — PLAN
Only after the score exists. Ordered steps, each with: what changes, why, which files, how it is verified, which `NRM-xx` it closes, and the score gain. Identify risks and anything needing a human decision.

## Phase 4 — WORK
Only after the plan is written. Execute in order. Re-score after each meaningful chunk, against Part B.

## Rules
- Assess before you assert. Verify against the repo; do not trust memory or these prompts.
- If these instructions conflict with what you find on disk, the disk wins. Report the conflict.
- Refactoring for the spec must be BEHAVIOUR-PRESERVING unless a `NRM-xx` gap justifies the change. Never silently change math.
- Never force-push. Never rewrite shared branches. Work on a branch off `dev`, open a PR.
- Uncommitted change exists: `deploy/curvas/current/index.html` in newman-architecture. Do not blow it away — ask.
- Three sibling Claude sessions share this working tree. Run `git status` before you edit. Coordinate through `supabase-devops`.
- A GitHub PAT lives in `~/.config/gh/hosts.yml`. Never print, echo, or commit it.
- The VPS has pending security updates and requires a restart. Do NOT reboot — it kills every session.
- State plainly when uncertain. "I could not verify X" is a valid and valued output.

## Phase 5 — FEED THE GRAPH
Everything worth preserving feeds `~/cfe-brain`. Follow its `CLAUDE.md` schema.

Do this continuously, not only at the end:
- A choice made, with the alternative rejected -> `kind: decision`
- A defect, gap, or contradiction -> `kind: finding`
- An invariant or external constraint -> `kind: normative`
- What the code does today, cited `file:line` -> `kind: descriptive`
- Something nobody knows -> `kind: question`
- A dead end and why it failed -> `kind: decision`

**Your Part B normative requirements and Part C gaps from Phase 1 are graph pages.** The spec in `docs/specs/` and the graph are the same knowledge in two shapes: the spec is the contract, the graph is the memory.

Before your session ends, ingest what you learned. An un-filed insight is a lost one.
Never file secrets, client PII, or real RPUs.
