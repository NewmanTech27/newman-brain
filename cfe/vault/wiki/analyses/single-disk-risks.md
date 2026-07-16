---
title: "Single-disk risks — what exists on this box and nowhere else"
type: analysis
kind: finding
tags: [risk, backup, single-disk, loss-risk, infra, gate-0]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "du -sh: ~/.claude/projects/-home-jesus/ = 84M; ~/newman-sso = 92K (15 files, no .git); ~/excalidraw-auth = 36K (6 files, no .git)"
  - "git branch -r --contains: spec/cfe-ppa-bess@4a2f319 NONE; spec/tuesday-inputs@5f6f804 NONE; integration/gate0@38ebff0 NONE (57 commits ahead of origin/dev)"
  - "/home/mario/CFE Brain: Permission denied to jesus; ~155MB per prompts/CHARTER.md:84"
verified_against: "newman-architecture refs @ 2026-07-10 fetch; du/ls on this box 2026-07-10"
confidence: high (SHAs, dir sizes, git state personally verified); medium (/home/mario size — denied, taken from charter)
---

# Single-disk risks — inventory only, do not commit any of it

**Context (drain):** Jesus is replacing this box with two (agents + services). This session does
not survive it. This is an **inventory** of everything that exists on this disk and **nowhere
else** — so a disk failure or a botched migration has a checklist to recover against. Nothing
here is committed; several items **must not** be (client PII, secrets, transcripts).

## 1. `/home/mario/CFE Brain` — ~155MB, version-controlled nowhere

Reference PDFs plus `entregables/` (client deliverables: `propuestas/`, `calculadoras/`,
`reportes/`). **Permission-denied** to the `jesus` user, so size is the charter's ~155MB, not
personally stat-able (confidence: medium). **Contains the golden fixture**
`raw/bills/780881200029/` — the 12 real CFE bill PDFs + `inputs.json` that are the ONLY copy of
the "sacred" golden-test input. Tonight a **copy** was placed at
`~/cfe-brain/vault/raw/bills/780881200029/` (gitignored via `.gitignore` line `vault/raw/`,
**not committed**), but the source remains single-disk. **Lost if the disk dies:** the golden
fixture, every client deliverable, all reference PDFs.

## 2. `~/newman-sso` — 92K, 15 files, NOT a git repo

The reusable **Google-auth SSO gate shell** the charter's `ceo.` / `extraction.newman.re` pages
are meant to mount behind: `newman-sso.service`, `nginx/`, `cloudflared.config.yml`, `login/`,
`validator.py`, `apply.sh` / `repoint.sh` / `reclaim.sh`, `INSTALL.md`. **Lost:** the entire auth-
shell scaffolding and its install runbook. Should be put under version control (Jesus's call).

## 3. `~/excalidraw-auth` — 36K, 6 files, NOT a git repo

An auth-wrapper prototype (`excalidraw-auth.service`, `excalidraw.nginx`, `login/`,
`validator.py`, `INSTALL.md`) — same gate pattern applied to an Excalidraw instance. **Lost:** the
prototype. Should be versioned.

## 4. Local-only git branches (commits on no remote)

Verified with `git branch -r --contains <tip>` (empty = local-only):

- **`spec/cfe-ppa-bess` @ `4a2f319`** — **TONIGHT'S SIZING FIX** ([[tonight-sizing-fix]]). Lost if
  the disk dies.
- **`spec/tuesday-inputs` @ `5f6f804`** — tuesday-inputs' spec work.
- **`integration/gate0` @ `38ebff0`** — **57 commits ahead of `origin/dev`** (the GATE 0
  integration work; worktree `~/wt-gate0`).
- Note: `spec/cfe-bill-parser` has **no upstream set**, but its tip `a81c43c` **is already
  contained in `origin/dev`** — its committed history is not at commit-loss risk. Any
  **uncommitted** changes in that worktree are a separate, unquantified risk.
- Also uncommitted and charter-flagged: `deploy/curvas/current/index.html` — do not discard.

Pushing these is the mitigation, but pushing is **outward-facing = Jesus's call**; not done.

## 5. `~/.claude/projects/-home-jesus/` — 84MB of agent transcripts

The full working context of this flock's seven sessions (88MB across all of
`~/.claude/projects/`). Not version-controlled, **must not be committed** (contains reasoning over
client data). **Lost:** the entire evidence-and-reasoning trail behind every finding, verdict, and
number in this wiki — the *why* behind the *what*. The wiki pages survive; the derivation does not.

## Mitigations (all Jesus-only / outward-facing — flagged, not executed)

Push the three local-only branches; back up `/home/mario/CFE Brain`; version `~/newman-sso` and
`~/excalidraw-auth`; snapshot `~/.claude/projects/` off-box before the box is decommissioned.

## Related
- [[reset-vs-merge-hazard]] · [[tonight-sizing-fix]] · [[2026-07-10-multirepo-branch-audit]]

## Confidence
High on everything personally verified (branch SHAs, `git branch -r --contains`, dir sizes, git
state). Medium on the `/home/mario` size (Permission denied; taken from the charter).
