---
title: "PV Degradation & Failure Modes"
type: concept
tags: [pv, reliability, degradation]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-iea-pvps-t13-degradation, 2026-06-08-iea-pvps-t13-32-climate]
---

# PV Degradation & Failure Modes

Why a PV array produces less every year, and how it can fail outright — the physical basis
for the **derate factor** in a savings model. Module power warranties (e.g. **1% year-1 +
0.40%/yr** on the Trina/Seraphim modules in [[pv-modules]]) are vendor *guarantees*; actual
field degradation and failure risk is what the [[pv-savings-model]] and 20-year financials
must assume. Underestimating it overstates late-year generation and IRR.

## How it works
**Gradual degradation (performance loss rate, PLR)** — the slow annual decline:
- **LID** (light-induced degradation) — early loss in first hours/weeks.
- **PID** (potential-induced degradation) — voltage-stress leakage; recoverable on many of our inverters (Huawei SUN2000 "PID recovery", see [[string-inverters]]).
- **LeTID** — light- and elevated-temperature-induced degradation.
- **Encapsulation degradation** (browning, delamination) — accelerated by heat + humidity.
- **TOPCon / SHJ-specific modes** — the new N-type cells in our [[pv-modules|module stock]] (Trina i-TOPCon, Seraphim HJT) have **material-specific degradation** the 2025 IEA report calls out as still maturing (e.g. UV-induced, metallization, moisture sensitivity).

**Outright failures (per the PV Failure Fact Sheets)** — categorized by **component**
(module/junction box, cables & interconnectors, mounting, inverter) and rated by
**safety** (fire/shock/physical) and **performance** severity:
- Cell cracking (handling/multi-wire), bypass-diode failure, front delamination, connector/cable failures, mounting/clamp issues, inverter faults.

## Climate dependence (Cancún = hot & humid)
The [[2026-06-08-iea-pvps-t13-32-climate|IEA T13-32]] climate-optimisation report shows PLR
and dominant stressors are **climate-specific**. Our core market (Cancún/Yucatán/Carmen) is
**hot & humid**: elevated encapsulation degradation, corrosion, and PID risk; lower thermal
losses favor **low temp-coefficient / HJT** modules (Seraphim −0.258 %/°C). This argues for
a **climate-appropriate derate** rather than a generic 0.5%/yr in the savings model.

## Related concepts
- [[pv-modules]] — the modules whose warranties this contextualizes
- [[pv-savings-model]] — where the derate factor enters generation over 20 yr
- [[solar-resource-data]] — the irradiance side of the yield equation
- [[2026-06-08-780881200029-yearly-savings]] — a 20-yr financial case sensitive to derate assumptions

## Open questions
- What annual PLR should we standardize for hot-humid Mexican coastal sites with TOPCon/HJT modules? (T13-32 case studies suggest higher than the 0.4% warranty slope in practice.)
