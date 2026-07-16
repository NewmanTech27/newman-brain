---
title: "IEA-PVPS T13-30:2025 — PV Degradation & Failure (Fact Sheets + New Tech)"
type: source
tags: [report, reliability, degradation, pv]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-iea-pvps-t13-degradation]
---

# IEA-PVPS T13-30:2025 — PV Degradation & Failure

**Type:** research report (two companion documents, IEA PVPS Task 13)
**Date:** February 2025
**Author:** IEA PVPS Task 13 (Köntges, Lin, Friesen, Hacke, et al.)
**Raw files:**
`raw/pdfs/2025-07-02 - IEA-PVPS-T13-30-2025-PVFS-ANNEX-PV Degradation-and-Failure fact sheets.pdf`,
`raw/pdfs/2025-07-02 - IEA-PVPS-T13-30-2025-REPORT-Degradation-and-Failure in new module technologies.pdf`

## Summary
Two 2025 IEA PVPS Task 13 deliverables on **how PV modules degrade and fail**:
1. **PV Failure Fact Sheets (PVFS)** — a catalog of single failure modes for PV planners,
   installers, investors and insurers, each rated by **safety** (fire/shock/physical) and
   **performance** severity, organized by component (module/J-box, cables &
   interconnectors, mounting, inverter).
2. **Degradation and Failure Modes in New PV Cell and Module Technologies** — focuses on the
   **TOPCon / SHJ (HJT)** generation now dominant (exactly our [[pv-modules]] stock) plus
   future perovskite tech: cell cracking, LID, **PID**, substring/bypass-diode protection,
   encapsulation degradation, and material modes specific to the new N-type cells.

These ground the [[pv-degradation]] concept and the derate assumptions in
[[pv-savings-model]] / the 20-year financials.

## Key claims
- Failure severity is two-axis: **safety** (no effect → can directly cause fire/shock) and **performance** (none → catastrophic) — useful for prioritizing O&M and insurance.
- New N-type cells (TOPCon, SHJ) have **technology-specific degradation modes** still maturing in field data — reliability is not yet as characterized as legacy PERC.
- **PID is recoverable** via inverter function — aligns with the "PID recovery" feature on Huawei SUN2000 ([[string-inverters]]).
- Audience explicitly includes **investors and insurers** — i.e., these modes drive bankability and warranty risk.

## Entities mentioned
- IEA PVPS Task 13 — issuing body; contributors from ISFH, NREL, Fraunhofer, SUPSI, Sandia, etc.

## Concepts mentioned
- [[pv-degradation]] — the concept this report anchors
- [[pv-modules]] — the TOPCon/HJT modules these modes apply to
- [[pv-savings-model]] — derate factor consumer

## Contradictions / tensions
- Tension with vendor warranties: module sheets promise **0.40%/yr**; the report's emphasis on under-characterized new-tech modes suggests **real-world PLR may exceed warranty slope** in harsh climates → use a conservative derate. (See [[pv-degradation]] open question.)

## Questions raised
- Which specific TOPCon/HJT modes are most material for hot-humid coastal Mexico?
