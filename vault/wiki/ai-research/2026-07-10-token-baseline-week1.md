---
title: "Token-discipline baseline — week 1, and ECO-3/ECO-4 unblocked"
type: analysis
service: ai-research
kind: finding
tags: [ai-research, token, cost, kpi, cache, cto]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "cfe-brain/vault/tools/token_audit.py (dedup by message.id)"
  - "~/.claude/projects/-Users-jesuslopez/ (48 transcripts, live snapshot 2026-07-10)"
  - "cfe-brain/vault/wiki/cto-verdict-log.jsonl (3 entries CTO-V-001..003)"
  - "cfe-brain/vault/wiki/ai-research/2026-07-09-token-audit-baseline.md (predecessor Phase-0)"
  - "prompts/KPIS.md:50-53 (ECO-1..4 definitions; ECO-2 33,560:5 anchor)"
issue: "NewmanTech27/newman-rebuild#10"
confidence: verified (ECO-1/2/4); low-N (ECO-3, N=3 verdicts / 2 scored)
---

# Token-discipline baseline — week 1

Charter rule: every KPI is computable from an artifact by a command. Below, each ECO
number is followed by the exact command that produces it. No agent self-report.

**Corpus:** 48 `.jsonl` transcripts under `~/.claude/projects/-Users-jesuslopez/`,
45 with usage, **1,879 assistant turns** (deduped by `message.id` — the harness
re-logs each API message on 1–8 lines with identical usage; naïve counting ~2×'s
every total). Live snapshot 2026-07-10, ±0.1% drift between runs.

## What changed since the 2026-07-09 predecessor baseline

The predecessor filed **ECO-3 and ECO-4 as BLOCKED** — "no machine-readable CTO
verdict artifact exists to divide by." That artifact now exists:
`vault/wiki/cto-verdict-log.jsonl` (3 entries). **This baseline unblocks both** by
joining `token_audit.py` output to the verdict log. Caveats on the join are stated
inline — the log schema is freeform, not the `{date, agent, submission, score,
merge/reject}` KPIS.md assumed.

## Baseline table

| KPI | Value | Command |
|---|---|---|
| **ECO-1** cache hit rate | **97.8%** | `python3 vault/tools/token_audit.py ~/.claude/projects/-Users-jesuslopez/` → KPI block `ECO-1` |
| **ECO-2** non-cached-input : output | **6.6 : 1** (attention-in:output = 281:1) | same command → KPI block `ECO-2` |
| **ECO-3** tokens per merged CTO point | **≈1.99 M tokens/point** (360,508,302 ÷ 181) | `python3 eco34_join.py AUDIT.json cto-verdict-log.jsonl` |
| **ECO-4** rework rate | **0%** (0 rejections / 3 submissions) | same join command → `ECO-4` |

Supporting global totals (from the same audit run):

| Token class | Tokens | % context-in | Cost (Opus 4.8) |
|---|---:|---:|---:|
| cache_read | 352,100,866 | 97.7% | ~$528 (65%) |
| cache_creation | 8,103,512 | 2.2% | ~$247 (31%) |
| output (gen+reason) | 1,286,412 | 0.4% | ~$96 (12%) |
| input (fresh) | 303,924 | 0.1% | ~$5 (1%) |
| **total** | **360.5 M context-in** | | **≈ $808** |

(Cost-share rows sum >100% because output/input are outside context-in; exact
line costs are in `token_audit.py`'s cost model. Headline: **$808 total**, 65%
is cache_read volume.)

## ECO-2 — the 33,560:5 anchor is still a ghost (re-confirmed)

`KPIS.md:51` fixes ECO-2 at **33,560:5** "on one sampled turn." That was a **cold
turn** (`cache_read=0`): its 33,560 = input + cache_creation, i.e. all input-side
tokens paid at write price, not attention size. The faithful fleet analog is
non-cached-input : output = **6.6 : 1** (predecessor measured 5.2:1 on a larger,
different corpus — same order, same conclusion). Anyone "improving" toward 33,560:5
chases a mismeasurement.

## ECO-3 / ECO-4 — unblocked, with honest caveats

`eco34_join.py` reads the audit `--json` and the verdict log:

- **ECO-4 rework_rate = 0/3 = 0%.** All three verdicts open GO/CONFIRMED
  (CTO-V-001 CONFIRMED, -002 "GO for step 2", -003 "GO — divergence removed").
  Zero rejections in week 1. A "rejection" is defined as a verdict not opening
  `GO`/`CONFIRMED`. **N=3 — a rate, not yet a trend.**
- **ECO-3 tokens_per_point ≈ 1.99 M.** Numerator = fleet total context-in
  (360.5 M). Denominator = Σ numeric `*_score` fields in the log = **181**
  (CTO-V-002 `step1_scope_score`=93 + CTO-V-003 `part_b_score`=88). **1 of 3
  entries (CTO-V-001) carries no numeric score at all**, so the denominator
  under-counts merged work and ECO-3 is an *upper bound*. This is the load-bearing
  data-quality finding: **the log needs a canonical `score` field and an explicit
  `merge`/`reject` boolean**, or ECO-3/ECO-4 stay fragile.

### Schema gap the CTO should close (unblocks robust ECO-3/ECO-4)

The log is freeform. To make the join a one-grep KPI rather than a regex hunt,
every entry needs: `agent`, `submission`, a single canonical `score` (int),
`decision` ∈ {merge, reject}. Then `ECO-3 = total_tokens / Σ score` and
`ECO-4 = reject / all` are trivial and stable.

## Top levers — validated against this session's data

Prior finding: **cost = context-size × turn-count**; hit rate is already high, so
the levers are **carry less context per turn** and **effort/model-tiering on
mechanical stages**. Validated here:

1. **Hit rate is not the lever (97.8% fleet; 98.7% this session).** Nothing to
   recover from prefix churn. The bill is cache_read *volume*: **187,387 cache_read
   tokens fed per turn on average** (this session `d2ee23c8`: **355,278/turn**).
   You pay 0.1× on the whole carried context every turn, hit or not. Recoverable
   waste = context size × turns → **carry-less-context is lever #1.**
2. **Output compression is worthless (re-confirmed).** Output = 0.4% of tokens
   billed fleet-wide; **0.73% this session**. 36% of turns spend ≥30k context-in
   to emit ≤50 output (mean 29,171:1). Caveman/terseness saves ~nothing.
   Median context-in per turn = **140,475**.
3. **Effort/model-tiering on mechanical stages is lever #2 (candidate, not yet
   measured).** Reasoning tokens ride in output; the research/data agents emit
   ~2,000+ output/turn while devops/tuesday do git- and React-mechanical work that
   likely doesn't need Opus `--effort high`. Per-agent spend: cfe $246, unknown
   $232, ppa $119, research $159, cto $47. A Phase-1 experiment, not a Phase-0
   claim.

**The one thing a rebuild will get wrong:** running every agent on Opus `--effort
high` with fat system prompts + un-trimmed tool results per turn reproduces the
bill no matter how terse the prose. Attack the median ~140k carried context.

## Reproducibility

```
# ECO-1, ECO-2 (+ global totals, per-agent, top sessions):
python3 vault/tools/token_audit.py ~/.claude/projects/-Users-jesuslopez/ \
        --json /tmp/audit_main.json

# ECO-3, ECO-4 (join to CTO verdict log):
python3 eco34_join.py /tmp/audit_main.json vault/wiki/cto-verdict-log.jsonl
```

`eco34_join.py` is filed alongside this page (`vault/tools/eco34_join.py`).

## Confidence

- ECO-1/ECO-2: **verified** — exact API usage, deduped, reproducible.
- ECO-4: **verified count, low N** (3 submissions, 0 rejections).
- ECO-3: **low confidence** — denominator (181 pts) under-counts (1/3 entries
  unscored); it is an upper bound. Real fix is a canonical log score field.
- Levers 1–2: lever #1 (carry-less-context) evidenced fleet-wide and this
  session; lever #2 (tiering) is a candidate direction, unmeasured.
