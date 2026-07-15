# ppa Seat: sizing.py Divergence Materiality — Net Oversell, Fixture Unreachable

**Summary**: The ppa agent quantified how wrong the clean-room sizing.py engine is versus the golden calc_core baseline: net OVERSTATES client savings, and the "sacred" golden fixture is unreproducible because it lives only on one operator's disk.
**Tags**: #newman #cfe-brain #sizing #golden-test #findings
**Created**: 2026-07-09
**Source**: newman-vps sessions 5037617e-95b7-425f-8c89-ad81d7d14b42.jsonl (main) with phase-1 boot duplicates e28daf5f, a3189b76 context, user jesus

---

## Content
- Charter: own deal offer + salesman calculator; wrap vault/tools/ppa_pricer.py, never rebuild the math; engine-enforced price floor (below min IRR/DSCR the UI refuses).
- Core finding trio (the org's highest-value item): sizing.py lost the umbral, inverted PV→BESS charging, and its golden test never runs RPU 780881200029 — "a golden test that does not exercise the golden RPU is a snapshot defending the bug."
- Materiality run refused to fabricate a single peso delta: golden fixture raw/bills/780881200029/ absent from vault and permission-denied under /home/mario/CFE Brain; sizing.py's MonthLoad/TariffCells can't even represent the three mechanics producing 90%+ of golden savings.
- Direction established with hard anchors: capacidad demand (79% of the golden $7.08M) OVERSTATED — sizing.py shaves summer kW in winter too, ~2× over across 5 months (sizing.py:129); arbitrage UNDERSTATED ~19× (34,560 vs 670,200 kWh/yr, sizing.py:133) but only 11% of savings; FP claw-back (−$84,528) omitted. Net = oversell.
- Governance flag parked as a board decision for Jesus (not routable to data): landing real RPU bills into the repo collides with the no-real-RPU/PII rule.
- Golden anchors restated: baseline $30,157,371; Ahorro $7,083,252 / 23.5%.

## Related Notes
- [[2026-07-09-cto-verification-freeze]]
- [[2026-07-10-flock-overnight-golden-proof]]
- [[cfe-brain-vault]]
