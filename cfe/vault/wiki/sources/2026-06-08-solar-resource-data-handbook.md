---
title: "IEA-PVPS T16-6:2024 — Solar Resource Data Best Practices Handbook (4th ed.)"
type: source
tags: [report, irradiance, yield, bankability]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-solar-resource-data-handbook]
---

# IEA-PVPS T16-6:2024 — Best Practices Handbook for Solar Resource Data (4th ed.)

**Type:** research handbook (IEA PVPS Task 16; NREL/DLR/Fraunhofer/Meteotest et al.)
**Date:** September 2024 (ISBN 978-3-907281-66-6)
**Author:** Sengupta, Habte, Wilbert, Gueymard, Remund, Lorenz, van Sark, Jensen
**Raw file:** `raw/pdfs/2025-07-02 - Best-Practices-Handbook-for-the-Collection-and-Use-of-Solar-Resource-Data-for-Solar-Energy-Applications-Fourth-Edition-.pdf` (516 pp)

## Summary
The authoritative reference (516 pp) on measuring, modeling, and applying **solar resource
data** for PV projects — irradiance components, measurement instruments, data quality,
variability, satellite/NWP models, forecasting, **uncertainty quantification**, and how to
apply resource data across project stages (prefeasibility → feasibility → due diligence →
operations). Underpins the [[solar-resource-data]] concept and contextualizes the
prefeasibility-grade [[solar-yield-lookup]] we use today.

## Key claims
- Irradiance has distinct components (GHI/DNI/DHI) + **rear POA + albedo** for bifacial — all needed for an accurate yield model.
- **Resource uncertainty propagates** to yield → P50/P90 → financing; bankable projects need site-adapted (measured + satellite) data, not just a lookup.
- **Stage-appropriate fidelity** (ch. 11): a TMY/lookup is fine for prefeasibility; due diligence needs more.
- **Soiling**, spectral effects, and variability are explicit derate/uncertainty contributors.

## Entities mentioned
- IEA PVPS Task 16; NREL and European research institutes — authoring bodies

## Concepts mentioned
- [[solar-resource-data]] — the concept page this anchors
- [[solar-yield-lookup]] — our practical (prefeasibility-grade) yield chain
- [[pv-savings-model]] — consumes the yield number
- [[pv-degradation]] — soiling/derate overlap

## Contradictions / tensions
None — but it frames our municipio-lookup yield as **prefeasibility-grade**, a caveat to carry into bankable savings cases.

## Questions raised
- Define the threshold (project size / financing type) at which we move from lookup to measured/satellite resource data.
