# PPA Pricing & Financial Model

**Summary**: The Newman PPA commercial structure (28% discount on generation, 144-month term, year-12/13 asset transfer), the finance-rigor rules the review committees hammered in, and real deal economics (KFC, AFCH, COVESTRO, FibraHotel).
**Tags**: #newman #ppa #finance #cfe #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Standard structure
- Newman flat tariff = CFE blended × (1 − discount, target 25–30%); savings billed on kWh **GENERATED** (not autoconsumo); **144-month (12-yr) term** with asset transfer at end of year 12 (year-13 savings jump). Escalators: CFE +7%/yr (alto) / +5.5%/yr (base conservador), Newman +4%/yr.
- Open business question from the KFC deal: with PPA-on-generation at 28% and 82% coverage, yr1 savings mathematically cap ~24% — the Anáhuac PDF's 35–55% band implies a different structure (>40% discount, oversized generation with net billing, or PPA on autoconsumo).
- Reference deal shape (KFC portfolio): 405.4 kWp + 186.4 kWh BESS, 82.2% coverage, yr1 savings $617,856 MXN, 20-yr $62.2M MXN, Newman reference investment $437,341 USD.

### Finance-rigor standing rules (from committee evals, scores 4–8/10)
- No headline IRR/DSCR without a year-by-year FCF table; DSCR must be **derived**, not asserted; a DSCR stress breach must resolve to one re-sized fix.
- Every number tagged `[ASSUMED]` vs `[SOURCED: doc+date]`; if >3 core inputs (CAPEX/busbar/porteo/OPEX) are unsourced, cap output at a qualitative "structural read".
- State real-vs-nominal and IVA convention (pre-VAT, IVA creditable for C&I, MXN); model FX (USD CAPEX vs MXN debt) and the 10-yr-debt-vs-15-yr-PPA tenor mismatch explicitly; demand charges (capacidad/distribución) must enter the savings math, not just kWh.
- Solar CF for Central fixed-tilt is ~19–20% real (22% is too high); punta timing claims need a DOF/CENACE cite; CELs always cited with current regime status + DOF date.
- Query the warehouse/tariff DB first before declaring inputs "not in hand" (CHARTER mandate for sourced figures).

### Verified deal data points
- **COVESTRO** Ecatepec (Valle de México Norte), GDMTH, Feb-26: 570,075 kWh (base 33,286 / intermedio 347,276 / punta 189,513), 1,138 kW demand, MXN 1,701,443.51; one outlier month 101,636 kWh in the 12-mo history.
- **FibraHotel** portfolio: $4.56M MXN/yr net savings on $43.2M billing across 6 RPUs (061950755457 = 46.7%; 780881200029 = $2.08M / 6.9%).
- GDMTH deals need kWh base/intermedio/punta, FRI-weighted billed demand, tariff division, and 12-mo history; missing input → flag, never guess.
- Mario's engine (newman-brain/cfe-brain) now runs as a pg_cron job writing one offer per RPU toward a `client.calculo` schema.

## Related Notes
- [[2026-06-20-pepsico-ppa-proposal]]
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-05-afch-ppa-offer-dataroom]]
- [[2026-07-02-agent-org-restructure-fibrahotel]]
- [[2026-07-03-review-finance-covestro-deal]]
- [[2026-07-03-review-finance-gdmth-walkthrough]]
- [[2026-07-03-review-consultant-gdmth-method]]
- [[2026-07-03-agent-committee-reviews-ppa-cfe]]
- [[2026-07-03-review-committee-judges]]
- [[2026-07-15-mario-engine-client-calculo]]
