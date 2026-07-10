---
title: "Materiality — can design-engine/sizing.py reproduce the golden RPU 780881200029?"
type: analysis
tags: [cfe-ppa-bess, clean-room, sizing, golden-test, finding, materiality, 780881200029]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [newman-architecture/agents/design-engine/sizing.py, 2026-06-11-780881200029-calculadora-audit, 2026-06-08-780881200029-yearly-savings]
---

# Materiality — can `design-engine/sizing.py` reproduce the golden RPU 780881200029?

**Question (board):** force the golden inputs through the clean-room `sizing.py` and quantify how far
its headline diverges from the golden `calc_core` result (baseline $30,157,371; Ahorro $7,083,252 / 23.5%).

## Answer: it cannot ingest the golden inputs. Two independent blockers.

**1 — Fixture unreachable.** `sizing.py.MonthLoad`/`TariffCells` need per-month period kWh + `kw_punta`
+ period $/kWh + a demand rate. These live in `raw/bills/780881200029/` (12 PDFs + inputs.json),
**absent from the vault** and **permission-denied under `/home/mario/CFE Brain`**. `calc_core` can't run
here either (`calc_core.py:14` reads the same missing folder). Only summed aggregates survive in the
filed analyses. **Governance finding: the "sacred" golden RPU is not reproducible from the knowledge
base — the fixture exists only on one operator's disk.**

**2 — Structurally lossy even with the data.** Golden $7,083,252 = PV $787,522 + capacidad $5,590,209
+ arbitrage $790,049 − FP claw-back $84,528. `sizing.py` misrepresents three of four:
- **Capacidad (79% of savings):** golden shave is energy-limited (1,411 kW summer / 705 kW winter);
  `sizing.py:129` uses `min(bess_kw, kw_punta)` — no ÷ punta-hours, no seasonal limit → **overstates**
  (winter ~2×, 5/12 months).
- **Two demand charges → one:** golden bills capacidad (BESS lever) *and* distribución on max(B,I,P)
  (BESS does not move it). `sizing.py` has a single `demand_charge` on `kw_punta` — cannot hold
  distribución out.
- **Arbitrage:** golden discharges 670,200 kWh/yr (~242 weekday cycles); `sizing.py:133`
  `min(bess_kwh·DOD, kwh_punta)` = one cycle/month ≈ 34,560 kWh/yr → **understates ~19×** (~$0.75M).
- **FP claw-back:** golden −$84,528; `sizing.py` has no FP → **overstates** +$84,528.
- PV intermedio offset ≈ match.

## Direction (what the board asked)
**Net OVERSTATE → oversell.** The dominant term (capacidad, 79%) is overstated; the understated
arbitrage stream is only 11%. A proposal built on the clean-room engine for this site most likely
oversells client savings. **No single peso delta is honest** — per-month `kw_punta` and the capacidad
$/kW rate are inaccessible, and the demand term's magnitude depends on which single `demand_charge` a
rep picks. Defensible anchors: arbitrage throughput 34,560 vs 670,200 kWh/yr (~19× under); winter
demand shave ~2× over.

## Confidence
High on direction and the two anchors (derived from `sizing.py` formulas + golden aggregates, no
reconstruction). No engine or test was run or modified. Ties to spec GAP-01/02/03 and
[[2026-07-09-cfe-ppa-bess-cleanroom-divergences]].
