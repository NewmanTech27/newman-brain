---
title: Token audit baseline — cost is cache_read volume, not a low hit rate
type: analysis
service: ai-research
kind: finding
tags: [ai-research, token, cost, kpi, cache]
created: 2026-07-09
updated: 2026-07-09
sources: ["cfe-brain/vault/tools/token_audit.py", "~/.claude/projects/-home-jesus/ (431 transcripts, live snapshot 2026-07-09)"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# Token audit baseline — Phase 0 measurement

**Command:** `python3 ~/cfe-brain/vault/tools/token_audit.py`
**Corpus:** 431 `.jsonl` transcripts under `~/.claude/projects/-home-jesus/`, 382 with usage, **4,168 assistant turns** (deduped by `message.id` — the harness re-logs each API message on 1–8 lines with identical usage; naïve counting doubles every total).
**Snapshot:** 2026-07-09; transcripts are live (sibling sessions writing during the run), so totals drift ~0.1% between runs.

## The headline

| Token class | Tokens | % of context-in | Cost (Opus 4.8) |
|---|---:|---:|---:|
| cache_read | 1,098,126,018 | 98.1% | **$1,647 (66%)** |
| cache_creation (1h @ 2×) | 11,352,325 | 1.0% | $340 (14%) |
| output (gen + reasoning) | 4,116,234 | 0.4% | $308 (12%) |
| cache_creation (5m @ 1.25×) | 8,052,298 | 0.7% | $151 (6%) |
| input (fresh) | 1,998,232 | 0.2% | $30 (1%) |
| **total** | **1.118 B context-in** | | **≈ $2,475** |

## The three findings, with numbers

1. **Cost is cache_read volume, and the hit rate is already excellent (98.3%).** The lever the charter expected — a churning prefix — is *not* the problem. The problem is that every turn drags a **median 146,800 tokens** of context, and at 4,168 turns that is 1.1 B cache_read tokens = $1,647 = **66% of all spend**. You pay 0.1× on the whole context, every turn, even when it is a cache hit. The recoverable waste is *context size × turn count*, not miss rate.

2. **One session is 64% of the entire bill.** `tuesday` session `81cef301` = **$1,587 of $2,475**, 1,751 turns, 988 M cache_read tokens. The `tuesday` agent overall is $2,043 (83%). Any optimization that does not touch tuesday is rounding error.

3. **Output compression is confirmed a non-lever (charter's hypothesis holds, and generalises).** Output is 0.4% of all tokens billed. 209 turns (5.0%) spent ≥30k context-in to emit ≤50 output tokens — mean ratio **13,135 : 1**. The sampled 33,560→5 turn was not an outlier; it is the median shape. Cutting output text saves nothing. (Reasoning tokens at `--effort high` are the one part of output worth attacking — $308 total, data agent emits ~2,000 output/turn — but that is a Phase-1 experiment, not a Phase-0 claim.)

## Tier 3 Economics KPI baselines (KPIS.md)

Each computed by the command above, over the transcripts — no agent self-report.

| KPI | Baseline | How |
|---|---|---|
| `ECO-1` cache hit rate | **98.3%** | `cache_read / (cache_read + cache_creation)` |
| `ECO-2` input:output | **5.2 : 1** non-cached-input:output (attention-in:output = 270:1) | the charter's `33,560:5` was a cold turn (cache_read=0); its 33,560 = input + cache_creation, so the faithful fleet analog is non-cached-input : output |
| `ECO-3` tokens per merged point | **BLOCKED** | no machine-readable CTO verdict artifact exists to divide by |
| `ECO-4` rework rate | **BLOCKED** | no CTO submission/rejection log exists to count |

ECO-3 and ECO-4 cannot be reported honestly today: there is no queryable CTO verdict artifact (only prose scores — `41/100`, `80/100` — scattered in wiki pages). Per KPIS.md, a KPI with no command behind it is a hope, not a KPI. **Unblocking them requires the CTO to append verdicts to a structured log** (date, agent, submission, score, merge/reject) — then `ECO-3 = total_tokens / Σ points` and `ECO-4 = rejections / submissions` become one grep.

## What I would change first (to be measured in Phase 1, not asserted now)

- **Shrink the carried context in the tuesday session**, since it is 64% of spend. The question to answer with data: what is in tuesday's 147k-token median context every turn — system prompt, un-trimmed tool results, re-read files? That decomposition is the next measurement.
- Do **not** touch output/caveman for savings; confirmed worthless.
- The 1h cache (`ephemeral_1h`, $340, written at 2×) needs a reuse check: is the 2× premium earning its keep vs 5m?

No optimization applied. This is Phase 0. Numbers first.
