---
title: "Solar Resource Data"
type: concept
tags: [pv, irradiance, yield, bankability]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-solar-resource-data-handbook]
---

# Solar Resource Data

The irradiance inputs behind any PV yield estimate — and how good they need to be at each
project stage. This is the *quality* layer under our [[solar-yield-lookup]] workflow: that
lookup returns a single kWh/kWp number per municipio, but the
[[2026-06-08-solar-resource-data-handbook|IEA Task 16 handbook]] explains what that number
hides (irradiance components, variability, uncertainty) and when a lookup is enough vs. when
a project needs measured/satellite data to be **bankable**.

## How it works
- **Irradiance components**: GHI (global horizontal), DNI (direct normal), DHI (diffuse) — plus **rear plane-of-array** irradiance and **albedo** for the bifacial modules in [[pv-modules]] (rear gain depends on surface albedo).
- **Data sources**: ground stations (most accurate, sparse), **satellite-derived** datasets (TMY / long-term), numerical weather prediction (for forecasting).
- **Uncertainty compounds**: resource uncertainty → yield uncertainty → P50/P90 → financing terms.
- **Stage-appropriate fidelity** (handbook ch. 11): prefeasibility (lookup/satellite TMY) → feasibility → **due diligence / bankability** (site-adapted, measured) → operations (monitoring).

## Relevance to our work
- Our [[solar-yield-lookup]] (municipio → kWh/kWp from `Solar_index_geografico.csv`) is a **prefeasibility-grade** input — fine for first-pass [[pv-savings-model]] sizing, not for a bankable P90.
- The Posadas analysis flagged the same gap on the *load* side (modeled vs metered); on the *generation* side, a Helioscope/satellite TMY beats the geographic lookup for a defensible number — see PV-yield-source intake in the savings workflow.
- **Soiling** (handbook ch. 5.9) matters in dusty/coastal sites — a recurring derate alongside [[pv-degradation]].

## Related concepts
- [[solar-yield-lookup]] — the practical CP → kWh/kWp chain this underpins
- [[pv-savings-model]] — consumes the yield figure
- [[pv-degradation]] — the other half of long-term generation uncertainty
- [[2026-06-07-solar-index-geografico]] — our geographic yield dataset

## Open questions
- At what project size/stage do we mandate satellite TMY or measured data over the municipio lookup?
