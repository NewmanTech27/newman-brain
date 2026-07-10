---
title: "Design-engine input-mapping wall: the live pipeline cannot feed the golden engine"
type: analysis
tags: [design-engine, ppa, finding, input-mapping, cfdi, gate0]
created: 2026-07-10
updated: 2026-07-10
sources: []
status: vigente
rpu: "780881200029"
---

# Design-engine input-mapping wall

**Question:** Step 2 of CTO-V-002 requires mapping pipeline-shaped per-RPU data
into the golden engine's bill schema so `sizing.optimize` can delegate to
`optimize_sizing.sweep`/`calc_core.compute`. Can the current production pipeline
data actually feed that engine? **No.** This page records why, with evidence.

## Answer — three independent blockers, in order of severity

### 1. The CFDI source has no horaria (base/intermedio/punta) split — the engine's core requirement
`calc_core.compute` reads, **flat and period-split**, per bill:
`b["kwh_base"], b["kwh_inter"], b["kwh_punta"]`, `b["kw_base"], b["kw_inter"], b["kw_punta"]`,
`b["gen_base"], b["gen_inter"], b["gen_punta"], b["capacidad"]`, and `b["year"], b["month"], b["days"]`
(`vault/tools/calc_core.py` `compute`, lines ~95–140). The umbral, the capacidad
basis, and the punta arbitrage/shave — 90%+ of the golden savings — are all
computed from that split.

The production bill blob is built by the collector from **CFDI XML**, which does
not carry the period split. `agents/cfe-collector/enrich.py:349` maps the CFDI's
single total into base: `"kwh_base": bill.get("kwh_period")`. There is **no
`kwh_inter`, no `kwh_punta`, no `kw_base/kw_inter/kw_punta`** in the payload
(`build_payload`, `enrich.py:344-366`), and the money buckets are nested under
`"importes"` (`enrich.py:354`) rather than flat where `calc_core` reads them.
Fed this blob, the engine sees all energy as base, zero punta kWh, zero punta
demand → BESS lever = 0, umbral on all-base → **structurally wrong output**, not
a tolerance issue. You cannot map a period split that was never captured; only
the **PDF recibo** ("Desglose del consumo") carries it, and the collector parses
CFDI XML, not the recibo breakdown. Connects to
[[pdf-intake-titular-extraction-fails-real-bill]].

### 2. `main.py` already does not match the live RPC shapes (independent of sizing.py)
- `get_consumption(rpu)` returns a jsonb **object** `{rpu, invoices[], fields[]}`
  (Postgres `pg_get_functiondef`), but `main.py:62` iterates it as a list of
  monthly rows (`for row in consumption`).
- `get_bill_series(rpu)` returns a **summarized** array
  (`period, kwh_total, facturacion, efectivo, p_base, p_punta, capacidad`) with
  **no `importes`**, but `derive_tariff` (`main.py:100-106`) reads
  `b.get("importes")` / `gen_base` / `capacidad`.
So `design_rpu` cannot run against the current contract regardless of the sizing
fix. The engine-shaped raw blob IS reachable — `get_bulk_bills(rpu)` returns
`jsonb_agg(bill)` from `client.bulk_bill where reconciled` — but see blocker 1:
that blob is period-collapsed, and see blocker 3: it is empty.

### 3. Zero live data exists
`select count(*)`: `client.invoice` = **0 rows**, `client.bulk_bill` = **0 rows**
(0 distinct RPUs each). Meanwhile `client.design` = **58 rows** (latest
2026-07-06). The 58 designs therefore predate the current schema/data and cannot
be reproduced from the live warehouse today. No RPU can be sized end-to-end
against live data right now.

## Consequence for Step 2
The engine-delegation half (replace `sizing.optimize`'s inline physics with a
call to the golden engine, adapt output back to `Candidate`/`SizingResult`) is
unambiguously correct and should proceed. But the **input-mapping half cannot be
proven against the live path** — the live path carries neither the horaria split
the engine needs nor any data at all. A pipeline-shaped test must therefore feed
**recibo-extracted engine-shaped bills** (what a corrected collector *would*
produce, == the golden fixture's `extract_folder` output), and the mapper must
**refuse** period-collapsed CFDI blobs rather than fabricate a split.

The real unblock is upstream and cross-agent: the collector must capture the
horaria split from the **recibo PDF** (cfe-bill-parser territory) and land it in
`bulk_bill.bill` in the flat engine schema, and the RPC layer (supabase-devops)
must surface it. Only then does a live RPU size correctly.

## Sources consulted
- `vault/tools/calc_core.py` (`compute`, flat split-field reads)
- `agents/cfe-collector/enrich.py:344-366` (`build_payload`, CFDI collapse)
- `agents/design-engine/main.py:52-132` (`build_load`, `derive_tariff`)
- Postgres `pg_get_functiondef` for `get_consumption`, `get_bill_series`, `get_bulk_bills`
- row counts on `client.invoice`, `client.bulk_bill`, `client.design`

## Confidence
High. Engine field reads, the CFDI collapse (`enrich.py:349`), the RPC
definitions, and the row counts are all directly evidenced. The one item read
from live prod (row counts, function defs) is reproducible via the queries above.

Related: [[2026-07-09-cfe-ppa-bess-cleanroom-divergences]],
[[2026-07-09-sizing-py-golden-ingest-materiality]], [[edge-function-maximalist]].
