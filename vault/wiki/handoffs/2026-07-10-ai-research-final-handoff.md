---
title: "ai-research final handoff — what dies with this session"
type: analysis
kind: finding
service: ai-research
tags: [handoff, ai-research, token, cost, kpi]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "vault/wiki/ai-research/2026-07-09-token-audit-baseline.md (Phase-0 audit, orphaned from index)"
  - "vault/wiki/index.md (grep 'token-audit-baseline' → 0 hits; 'ai-research' → 0 hits)"
  - "vault/tools/token_audit.py (dedup by message.id)"
  - "~/prompts/KPIS.md:52 (ECO-2 anchor 33,560:5)"
  - "vault/CLAUDE.md:130-141 (file-placement table — no ai-research/ folder)"
verified_against: 0f0166911bd23efd416a0f5bec09e00a671c2512
confidence: high (Phase-0 numbers); low where marked
---

# ai-research final handoff

Seat: token optimization + upskilling. Measures, never builds. Phase 0 done, Phase 1 never authorized. No product code touched, ever. Nothing uncommitted from me.

## Traps documented nowhere (file:line)

1. **My whole audit is invisible to the index.** `vault/wiki/ai-research/2026-07-09-token-audit-baseline.md` exists but is referenced **nowhere** in `vault/wiki/index.md` (grep → 0), and the `ai-research/` subfolder is off-schema — `vault/CLAUDE.md:130-141` file-placement table never lists it. A successor obeying the token rule ("query the index, don't read the tree", `_practices.md §7`) will never find the $2,475 audit. **Read `vault/wiki/ai-research/` directly or it's lost.**

2. **`token_audit.py` dedup trap.** The harness re-logs each API message on 1–8 jsonl lines with *identical* usage. My script dedups by `message.id`. This fact is in the baseline page but **not in the script's docstring** where a coder would look. A rebuild audit that counts per-line reports ~2× real spend. 431 transcripts → 4,168 *deduped* turns.

3. **The charter's ECO-2 anchor is a mismeasurement.** `KPIS.md:52` fixes ECO-2 at `33,560:5`. That was a **cold turn** (`cache_read=0`); its 33,560 = input+cache_creation, not attention. Fleet reality: **5.2:1** non-cached-input:output (attention-in:output ≈ 270:1). Anyone "improving" toward 33,560:5 chases a ghost.

## Work in flight — exact state

- **Phase 0 (measure): DONE.** Filed, reproducible: `python3 vault/tools/token_audit.py`.
- **Phase 1 (optimize): NOT STARTED.** CEO never tasked it. No branch. No experiment run.
- **Next step was:** decompose `tuesday` session `81cef301`'s **147k median per-turn context** (system prompt vs un-trimmed tool results vs re-read files), because tuesday is **64% of all spend** ($1,587 of $2,475). Never executed.
- **Queued, never measured:** `--exclude-dynamic-system-prompt-sections` prefix-reuse test; effort/model tiering on mechanical stages (git-heavy devops, React-heavy tuesday).

## Claims I made and never verified — honestly

- **"Shrink tuesday's context" is a direction, not a validated lever.** I measured the 147k median; I never decomposed *what's in it*. Unproven that any of it is recoverable.
- **The 1h ephemeral cache ($340, written at 2× premium) "may not earn its keep"** — asserted, **never measured. Confidence: low.**
- **All totals are a live snapshot,** not a close: sibling sessions were writing transcripts during the run, so ±0.1% drift. $2,475 / 98.3% hit / 64% tuesday are as-of 2026-07-09, not final.
- **ECO-3 / ECO-4 declared BLOCKED** (no machine-readable CTO verdict log to divide by). Verified-absent at snapshot; I never confirmed the CTO couldn't be asked to emit one. Unblocking = CTO appends a structured verdict log (date, agent, submission, score, merge/reject); then both become one grep.

## The one thing the rebuild team WILL get wrong

**Cost is context-size × turn-count — not output volume, not miss rate.** The hit rate is already 98.3%; there is no prefix-churn to fix and no output to compress (output is 0.4% of tokens; caveman saves ~nothing). A front-to-back rebuild that runs every agent on Opus at `--effort high` with fat system prompts and un-trimmed tool results per turn **will reproduce the ~$2,475 bill no matter how terse the writing.** The only real levers: **carry less context per turn**, and **tier effort/model on mechanical stages.** Attack the median 147k, or you have optimized nothing.
