---
title: "Interconnection Procedure (Centrales <0.5 MW)"
type: concept
tags: [interconnection, dg, process]
created: 2026-06-08
updated: 2026-06-09
sources: [2026-06-08-manual-interconexion-500kw, 2026-06-09-autoconsumo-cne-2025]
---

# Interconnection Procedure (Centrales <0.5 MW)

The administrative path a distributed-generation plant follows to legally connect to and
export onto CFE's distribution network, set by the [[2026-06-08-manual-interconexion-500kw|Manual de Interconexión <0.5 MW]].
This is the **process gate** between "system installed" and "exporting under
[[medicion-neta]]" — distinct from the *physical* install rules
([[instalacion-pv-interconectada]], NOM-001-SEDE) and from the *compensation* rules
([[2026-06-04-res142-2017-gen-dist]]).

## How it works
1. **Solicitud de Interconexión** — applicant files (via the Suministrador) the form,
   single-line diagram, inverter datasheet + certificate, location sketch, last paid bill.
2. **Evaluation** — the Distribuidor checks circuit hosting capacity; decides if a study
   is needed.
3. **Estudio (if required)** — CRE-authorized cost; may surface need for *Infraestructura
   requerida* (network reinforcement) or *Obra específica* (applicant-side connection work).
4. **Contrato de Interconexión** — signed with the Distribuidor.
5. **Unidad de Inspección** — certifies the install (Tipo MT1/MT2; **BT exempt**).
6. **Sincronización** — CENACE orders physical connection + sync tests; generation joins the RGD.

## Classification (capacity × voltage)

| Class | Voltage | Net generation capacity |
|---|---|---|
| Tipo BT | BT (≤1 kV) | <50 kW trifásico / <30 kW monofásico |
| Tipo MT1 | MT (1–35 kV) | ≤250 kW |
| Tipo MT2 | MT | >250 kW, <500 kW |

## Hosting-capacity rule of thumb
- **BT**: aggregate DG on a transformer/feeder ≤ **80% of its capacity**.
- **MT**: feeder caps 4/8/10 MW at 13.8/23/34.5 kV; 80% of each power transformer (0.95 pf).
- All <0.5 MW plants are *presumed* to meet the high-load-concentration criteria unless a CENACE study says otherwise.

## Timelines & shortcuts
- **13 business days** (no study) / **18** (with study), excluding construction.
- **Positiva ficta** for typical BT schemes if the utility misses the deadline.

## The parallel track: Autoconsumo interconnection (≥ 0.7 MW)

The procedure above is the **exempt‑tier** track (< 0.7 MW, no permit). A plant **≥ 0.7 MW** interconnects under the **[[autoconsumo]]** regime instead: the [[cne|CNE]] permit (simplified for 0.7–20 MW) plus **CENACE interconnection Estudios under the MIC** (Manual de Interconexión, DOF 09‑II‑2018 — a *different* instrument from the <0.5 MW manual here), formalized in a Contrato de Interconexión‑Conexión (DACG Num. 4.1). In the simplified track the studies are **scoped to the point of interconnection**; in the ordinary track (>20 MW) they cover the full SEN. So the wiki now holds two interconnection tracks split at 0.7 MW: this CFE‑Distribución exempt path, and the CNE/CENACE autoconsumo path in [[2026-06-09-autoconsumo-cne-2025]].

## Related concepts
- [[generador-exento]] — the <0.7 MW (no-permit) status that uses this track
- [[autoconsumo]] — the ≥0.7 MW figure with its own CNE/CENACE interconnection track
- [[generacion-distribuida]] — the regime; **ceiling raised to <0.7 MW in 2025**
- [[medicion-neta]] — what you can do once interconnected
- [[scheme-comparison]] — medición neta vs autoconsumo eligibility
- [[instalacion-pv-interconectada]] — the physical/NOM layer that the Unidad de Inspección checks

## Open questions
- Post-2025 (0.7 MW ceiling): do the BT/MT1/MT2 boundaries and the 0.5 MW gate of *this* manual shift? The autoconsumo line is now 0.7 MW (DACG), but the <0.5 MW manual's class boundaries are unrevised. See tension on [[2026-06-08-manual-interconexion-500kw]].
