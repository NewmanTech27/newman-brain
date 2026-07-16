---
title: "Second Brain Use Cases — What CFE Brain Can Be Used For"
type: analysis
tags: [meta, strategy]
created: 2026-06-10
updated: 2026-06-10
sources: []
status: vigente
---

# Second Brain Use Cases — What CFE Brain Can Be Used For

**Question:** Brainstorm — what can this second brain do today, and what capabilities is the user not yet considering?

## Framing

CFE Brain is not just a savings calculator. It is a **deterministic underwriting engine + regulatory brain with an audit trail** (`tools/cfe_savings` + the wiki). The unexplored value lies in pointing it at the *whole deal lifecycle* — pre-sale, post-sale, and the compounding data asset — not just the pre-sale analysis.

## Answer

### Runnable today, as-is
1. **Proposal factory** — bills in → validated baseline → sized system → Spanish client one-pager (proven loop: [[2026-06-09-456220800389-propuesta]]). Every prospect in under an hour, peso-traceable.
2. **CFE bill auditing as lead-gen** — the engine foots every bill; "we check if CFE overcharges you" is a free door-opener that surfaces FP penalties and anomalies as a byproduct.
3. **FP correction as a standalone product** — highest-ROI lever found to date (~$875k/yr at [[2026-06-09-456220800389-yearly-savings|Tototlán]], 3–4 month capacitor payback). Near-zero marginal cost to scan any bill stack for FP < 90%.
4. **Competitor quote audits** (CLAUDE.md Workflow 6) — re-run a rival vendor's numbers through the engine under their own assumptions; classic SIN error to catch: PV credited in punta ([[pv-savings-model]]).
5. **Feasibility pre-checks** (Workflow 5) — permit tier, interconnection class, 80% hosting, 120% bus rule, storage mandate ([[autoconsumo]], [[interconexion-cre]], [[instalacion-pv-interconectada]]).
6. **Demand-anomaly diagnostics** — bills reveal operational problems (e.g. the [[fideicomiso-f1596]] 106→12 kW demand collapse); a consulting conversation hiding in data already held.

### Post-sale — the biggest blind spot
7. **Savings M&V** — the SaaS model bills a share of savings, so savings must be *proven monthly*: keep ingesting client bills post-install; engine computes counterfactual vs actual. Invoicing backbone + dispute defense.
8. **Compliance calendar per client** — Registro de Usuarias (1T), min-use 50%/30%, permit conditions ([[autoconsumo]]) as a retainer service.
9. **Threshold watching** — warn clients drifting toward the 100 kW gate ([[gdmto]]/[[gdmth]]) or the 0.7 MW line ([[generador-exento]]) before they cross.

### Compounding assets
10. **Proprietary benchmark database** — every RPU adds rates by división, load factors by industry, savings %, FP incidence; market intelligence no one else holds.
11. **Financier/bankability packets** — golden-tested deterministic engine + footed bills + audit trail = a diligence story that lowers cost of capital.
12. **Multi-site portfolio ranking** — run all of a chain's RPUs (e.g. [[grupo-posadas]]), rank by IRR → portfolio deals instead of site deals.
13. **Regulatory impact analysis** — cross-links let a new DACG be mapped to exposed pipeline projects in minutes.
14. **Sales enablement / training** — generate client explainers and onboarding material from the wiki itself.

### Extensions worth building (ROI order)
15. **15-min HM interval data ingestion** — single highest-value engine upgrade: metered load shapes, honest big-PV sizing, bankability.
16. **GDMTO/PDBT engine support** — wiki pages exist; opens the small-commercial long tail.
17. **DOF watcher** — periodic check for new CNE DACGs → ingest pipeline; the 2025 regime will keep moving.
18. **BOM auto-quoting** — sizing → [[equipment/index|Equipment Catalog]] → preliminary hardware list.
19. **Interconnection paperwork tracker** — checklists + deadline tracking (13/18 days, positiva ficta).
20. **PV-EV charging adjacency** — [[2026-06-08-iea-pvps-t17-pv-ev-charging]]; natural hotel upsell.

### Honest limits
- Rates captured for SIN only; go stale monthly ([[rate-inputs]])
- Engine assumes 100% self-consumption — can't price exports or oversized PV
- Regulatory *analysis*, not legal opinion — lawyer in the loop for filings

## Sources consulted
- [[index]], [[overview]], [[2026-06-09-456220800389-yearly-savings]], [[2026-06-08-780881200029-yearly-savings]], CLAUDE.md workflows

## Confidence
High for "runnable today" items (proven in past analyses); Medium for extensions (effort estimates are judgment, not engineering scoped).
