---
title: "Manual de Interconexión de Centrales <0.5 MW (SENER, DOF 15/12/2016)"
type: source
tags: [regulation, interconnection, dg]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-manual-interconexion-500kw]
---

# Manual de Interconexión de Centrales de Generación <0.5 MW

**Type:** regulation (Acuerdo SENER)
**Date:** DOF 15 December 2016 (in force 30 days after)
**Author:** Secretaría de Energía (Pedro Joaquín Coldwell)
**Raw file:** `raw/pdfs/2025-06-30 - Manual de Interconexión de Centrales de Generación con capacidad menor a 500 kW.pdf`

## Summary
The SENER manual that sets the **administrative procedure and infrastructure rules** for
interconnecting generation plants <0.5 MW to the Redes Generales de Distribución (RGD).
It develops Base 3.3.7 of the Bases del Mercado Eléctrico and is the operational
companion to the CRE net-metering rules ([[2026-06-04-res142-2017-gen-dist]]) — RES/142
defines the **contract/compensation** schemes; this manual defines the **how-to-connect
process**, timelines, responsibilities, and circuit-capacity limits. It governs the
[[generacion-distribuida]] / [[generador-exento]] regime under arts. 17, 68–70 of the LIE.

This is the process layer behind every project we model: a Posadas-scale or Fiesta Inn PV
plant must run this gauntlet (solicitud → estudio → contrato → inspección → sincronización)
before it can legally export under [[medicion-neta]].

## Key claims
- **Plant classification by capacity & voltage** (Tabla 2.1):
  - **Tipo BT** — BT (≤1 kV): <50 kW trifásico / <30 kW monofásico.
  - **Tipo MT1** — MT (1–35 kV): ≤250 kW.
  - **Tipo MT2** — MT: >250 kW and <500 kW.
- **Circuit hosting-capacity limits** (when no specific study exists):
  - BT: aggregate DG ≤ **80% of the feeding transformer/feeder** capacity.
  - MT (Tabla 2.2): feeder caps **4 MW @13.8 kV / 8 MW @23 kV / 10 MW @34.5 kV**; at power transformers, **80% of each transformer's capacity** (at 0.95 pf lagging).
- **Timelines** (Tabla 5.1): max **13 business days** without study, **18** with study (excludes construction of Obra específica / aportaciones).
- **Positiva ficta**: a BT request using typical interconnection schemes is deemed **approved** if the utility blows the deadline (and it's not the applicant's fault).
- **Inspection**: Tipo MT1/MT2 require a CRE-approved Unidad de Inspección before sync; **Tipo BT is exempt** (optional).
- **Solicitud requires**: interconnection form (Anexo 2), location sketch, single-line diagram, generation tech datasheet, **inverter datasheet + certificate**, and last paid CFE bill if sharing the meter.
- Modalities: consumo de centros de carga, **venta de excedentes**, venta total; Generadores Exentos sell only via a Suministrador or use Abasto Aislado.

## Entities mentioned
- [[cenace]] — orders physical interconnection, runs sync tests; can override a stalling Distribuidor
- [[cfe]] / [[cfe-ssb]] — the Suministrador receives the solicitud
- [[cre]] — approves study costs, inspection units, can sanction the Distribuidor
- the Distribuidor (CFE Distribución) — evaluates circuit capacity, runs studies, signs the Contrato de Interconexión

## Concepts mentioned
- [[interconexion-cre]] — the procedure documented here (concept page)
- [[generacion-distribuida]] / [[generador-exento]] — the legal regime this implements
- [[medicion-neta]] — the compensation scheme that follows interconnection

## Contradictions / tensions
- **Capacity ceiling now 0.5 → <0.7 MW.** This 2016 manual is built around the **0.5 MW**
  threshold. The 2025 Ley del Sector Eléctrico raised the DG ceiling to **<0.7 MW**
  (art. 25 — see [[2026-06-08-pdse-2025-2039]], [[generacion-distribuida]]). The manual's
  Transitorio Segundo says it stays in force until CRE issues replacing DACGs, so the
  *procedure* still applies but the **0.5 MW class boundaries (BT/MT1/MT2) are stale** and
  must be re-read against the 0.7 MW ceiling. Flag on [[generacion-distribuida]] too.

## Questions raised
- Has CRE issued the replacement DACG that updates the BT/MT1/MT2 thresholds to 0.7 MW?
- For a >0.5 MW (but <0.7 MW) plant, which interconnection track applies today — this manual or the large-scale (CENACE MEM) process?
