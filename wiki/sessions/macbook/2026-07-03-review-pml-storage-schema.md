# Data-specialist review of CENACE PML storage design (7/10)

**Summary**: A power-market data persona endorsed nodal-grain storage with zona rollups but flagged missing DB-level invariants in the proposed mx_pml table.
**Tags**: #newman #cenace #pml #warehouse #eval
**Created**: 2026-07-03
**Source**: macbook session 30dc4972-c28c-464e-8d21-ae841d9708c6.jsonl, user jesus

---

## Content
- Design reviewed: store PML at nodal grain (~2,400 PNodos) and roll up to zona de carga (~50) via materialized view — zona-only discards congestion signal that cannot be rebuilt; site/savings use zona, analysts use nodal.
- Table shape: mx_pml(sistema SIN|BCA|BCS, clave_nodo, market MDA|MTR, fecha_op local date, hora, pml + energia/perdidas/congestion components).
- Issue: component-sum invariant (energia+perdidas+congestion=pml) only enforced in load code, not as a DB CHECK/trigger.
- Issue: clave_nodo doubles as nodo-or-zona id with no grain discriminator — unsafe if tables ever merge.
- Issue: hora comment says 1-24 (+25 DST) but the codebase already fixed this to a 0-25 constraint in commit 4de998b — new schema risks re-diverging.

## Related Notes
- [[newman-agents-review-committee]]
