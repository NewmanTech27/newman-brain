# #157: calculo P1: CFDI XML parser (parse_bill_xml port) + Python↔JS parity harness

- State: OPEN
- Created: 2026-07-15T06:08:50Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/157

## Body

Port CFE Brain's `cfe_savings/extract.py::parse_bill_xml` (droplet, mario) to JS/TS so the pipeline can turn `raw_cfe.mi_espacio.xml_content` (CFDI ingreso XMLs) into engine-ready bill dicts.

**Verified facts (2026-07-15 investigation):**
- Prod has 323 raw XMLs / 12 RPUs / 31 periods; 194 are tipo `I` with full detail (CONSUMO1F/2F/3F, DEMANDA1P/2P/3P, MOTIVO_REG_i/IMPTE_TOT_REG_i, SubTotal, FacPot, TARIFA, DIVISION, CARGA_CONTRATADA, CP); 128 are `P` payment complements (skip); 1 anomalous `I` (characterize).
- Python golden: 18/18 pass. calc_core↔engine.js: 0 diffs (Ixtlahuacán full tree).

**Gate:** parity harness runs Python parse_bill_xml vs JS port over all 194 prod XMLs → 0 field diffs. XMLs never committed to git (export to scratch, .gitignore).

**Doctrine:** port, don't rewrite semantics; MEM code map ES1/ED1/ETB/ECB/EGB/EGI/EGP/EID/EMB; bonif_fp = SubTotal − ΣMEM; footing check ±0.5%.
