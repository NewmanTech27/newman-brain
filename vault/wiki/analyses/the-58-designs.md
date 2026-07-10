---
title: "The 58 designs in client.design — flawed, unreproducible, latent"
type: analysis
kind: finding
tags: [design-engine, client-design, quarantine, del-5, prod-data, cfe-ppa-bess]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "newman-architecture@a81c43c agents/design-engine/main.py:205 (supa.insert_design), :222 (pipeline_stage 'verified'->'designed')"
  - "ppa/data SQL: client.design = 58 rows, latest 2026-07-06; client.invoice = 0; client.bulk_bill = 0"
  - "cto-verdict-log.jsonl CTO-V-001 (three divergences CONFIRMED)"
verified_against: "prod Supabase project ledger reads via supabase-devops/cfe-ppa-bess, 2026-07-09/10"
confidence: medium — count (58) and latest date (2026-07-06) are from ppa/data SQL reads, not personally re-run by CEO; the causal chain (divergent engine -> insert_design -> client.design) is code-evidenced
---

# The 58 designs in client.design

**Context (drain):** "I do not know what the 58 designs are. Nobody outside your context does."
This page fixes that.

## What they are

`client.design` is a table in the **production** Supabase database. It holds **58 rows** (latest
`2026-07-06`). Each row is a persisted **PV/BESS sizing result** for one RPU — the output of
`design-engine/sizing.py`'s `optimize()`, written by `insert_design` (`main.py:205`) as the work
queue advances that RPU's `pipeline_stage` from `verified` to `designed` (`main.py:222`). In
plain terms: **58 stored answers to "how big a solar+battery system should this client buy, and
what will it save."**

## Where they live and who reads them

- **Table:** `client.design`, prod Supabase.
- **Consumer:** `proposal-builder` — it reads a design and renders a client-facing proposal PDF
  to an internal Google Drive folder (human-in-the-loop; not auto-sent). It renders **only** RPUs
  in its `PROPOSAL_RPUS` allowlist, which is currently **empty**.

## Why I proposed quarantining them

Two compounding defects:

1. **They are flawed.** All 58 were produced by the divergent engine that violates the three
   invariants (umbral dropped, PV→BESS inverted, never golden-tested — CTO-V-001). Their sizing
   and savings **overstate** (per [[2026-07-09-sizing-py-golden-ingest-materiality]]). See
   [[design-engine-live-or-orphan]].
2. **They are unreproducible.** They predate the current schema/data: `client.invoice` and
   `client.bulk_bill` are both **0 rows** today (see [[design-engine-input-mapping-wall]]). You
   **cannot regenerate or re-validate** these 58 from the live warehouse. They are orphaned
   artifacts of an older pipeline.

Together that makes them a **latent landmine**: the instant an RPU is added to `PROPOSAL_RPUS`
(or the worker is re-armed), the matching stale, wrong-physics design ships into a proposal PDF
**with no recompute** — flawed math reaches a salesperson and, from there, a client.

## What breaks if nobody quarantines them

Nothing **today** — the empty allowlist and disabled worker gate them. The failure is **silent
and future-dated**: a later allowlist entry, a worker re-arm, or a well-meaning "let's generate
proposals" step ships an overstated deal that a rep cannot tell is wrong. Quarantine means
marking the 58 rows invalid/superseded so no future allowlist entry can surface them, forcing a
recompute through the corrected engine once [[tonight-sizing-fix]] deploys.

## Status: NOT executed — Jesus's call

Quarantining is a **production write**, and the standing constraint is no prod mutation without
Jesus. It was **not** executed. The safe interim requires no write and already holds: **worker
disabled, allowlist empty.** Recommendation stands: **quarantine — yes.**

## Related
- [[design-engine-live-or-orphan]] · [[design-engine-input-mapping-wall]] · [[tonight-sizing-fix]]

## Confidence
Medium. The count (58) and latest date (2026-07-06) come from ppa/`data` SQL reads I did not
personally re-run; the causal chain from the divergent engine through `insert_design` into
`client.design` is code-evidenced and CTO-confirmed.
