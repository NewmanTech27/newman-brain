# Newman Energy Academy: EU energy sales course on GitHub Pages

**Summary**: Built a full 7-track / 28-lesson EU energy sales curriculum (PPA, solar, BESS, financial models, exit-to-funds, EU funding) with Czechia as the worked example, deployed with the Newman v3 UI.
**Tags**: #newman #ui #ppa #bess #education #eu
**Created**: 2026-06-27
**Source**: macbook session a35cb2c6-4cde-4ac9-be38-5d1613d0fac4.jsonl, user jesus

---

## Content
- Goal: sales course so a businessman entering the EU energy market understands why it's a business, the financial models, and exit strategy (selling projects to funds at discounted present value); Czechia as example but Europe-wide.
- Built at `~/newman-energy-academy`, deployed to lopezpalacios.github.io/newman-energy-academy; 7 tracks × 4 lessons written by parallel agents, each cloning the reference template (`exit-npv-dcf.html`) verbatim for nav/head/footer.
- Fixed lesson shape: objective callout, keyterm callouts, worked numeric tables, sales `.script` line, 3 objections, 3-question quiz, pager chain; 4 embedded JS calculators (LCOE, exit/NPV, savings, etc.).
- Content anchors: OTE day-ahead + EU SDAC coupling, ČEPS/ERÚ institutions, €140/MWh Czech industrial tariff decomposition, 1 MWp Brno rooftop worked at ~€62/MWh LCOE, yield-compression math (funds accept 6–8% vs developer 10–13%), EU funding landscape (Modernisation Fund, Innovation Fund, RRF, InvestEU, EIB).
- Expanded to DACH + EU-level callouts via research agents; correction caught: EU-CH electricity agreement (Bilaterals III) signed 2 March 2026 but not in force (~2030 realistic).
- Country deep-dives added: Austria, Switzerland, Poland (URE/PSE/TGE; coal ~52% in 2025, renewables ~29%).
- Also: glossary/wiki of abbreviations with animations, downloadable assets (except model pack), no lead forms.
- Brand-drift audit vs newman-brand-ui v3: swapped Montserrat → Space Grotesk 300 across all 45 pages, removed magenta keyterm border and drop shadows; academy now tracks brand-ui v3 in lockstep.

## Related Notes
- [[2026-06-26-competitor-intel-research]]
