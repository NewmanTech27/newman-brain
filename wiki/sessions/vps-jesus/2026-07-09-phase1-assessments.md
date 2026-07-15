# Phase -1/0 Boot Assessments: cfe-bill-parser and cfe-ppa-bess Seats

**Summary**: First-boot assessment sessions for the parser and ppa seats — key find: enrich.py's CFDI "reconciliation" is a near-tautology (checks the SAT fiscal identity, not the MEM breakdown), so reconciled=true never validates the data feeding the sizing engine.
**Tags**: #newman #agent-org #cfe #assessment #findings
**Created**: 2026-07-09
**Source**: newman-vps sessions a3189b76-9e43-4c63-b53d-87ad39135a86.jsonl (cfe-bill-parser assess) and e28daf5f-2726-4ccb-b3e1-b51ace859ac9.jsonl (cfe-ppa-bess assess), user jesus; consolidated near-duplicate boot runs

---

## Content
- cfe-bill-parser assess: HANDOFF.md shows the collector pipeline proven end-to-end on Consulta (validated on RPU 780020900569 UNIV ANAHUAC → 3 CFDIs); the >12-month MiEspacio branch is the one unfinished piece; mac mini remains central (launchd always-on, NordVPN Mexico IP).
- Real CFDI fixture on disk: `dl/965951103875/latest/LA-000324371498.xml`; a second Python extraction path exists in `intake-worker/`.
- KEY FINDING: `enrich.py:279-297` reconciliation checks `SubTotal − Descuento + IVA − Retenidos == Total` — the fiscal identity every SAT-stamped CFDI satisfies by construction — not the docstring's advertised `(ΣMEM)×(1+IVA)+untaxed == Total` completeness check. `reconciled=true` on the CFDI lane is therefore nearly meaningless for validating the MEM breakdown feeding sizing.
- cfe-ppa-bess assess: knowledge graph empty at boot (wiki/cfe-ppa-bess/ and concepts/ empty, index/log stubs); agents were brought in clean-room at commit 1ad3af3 (Jul 7) from newman-pipeline (spec) + newman-agents (reference); Stage 5 spec lived outside the repo.

## Related Notes
- [[2026-07-09-sizing-materiality]]
- [[newman-invoice-collector]]
