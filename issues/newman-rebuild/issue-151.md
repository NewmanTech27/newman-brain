# #151: Source-of-truth: SAT Descarga Masiva can't replace the CFE harvest (sizing data is in CFE's Addenda)

- State: OPEN
- Created: 2026-07-14T14:25:11Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/151

## Body

Investigated whether SAT Descarga Masiva could replace the WAF-gated CFE MiEspacio
harvest for pulling client invoice history. **Conclusion: no — keep the CFE
harvester as the primary source.** Do not rebuild onboarding around SAT.

Evidence (traced end-to-end on a real stored CFDI, RPU 965951103875, TARIFA_REG=GDBT):
- The PV+BESS sizer consumes parse_bill_xml (cfe-brain vault golden engine).
- Everything it needs lives in CFE's proprietary <cfdi:Addenda>, NOT the fiscal
  CFDI body:
    <DEMANDA>, <DEMANDA_CAPACIDAD>, <DEMANDA_DISTRIBUCION>  (BESS demand levers)
    <DEMANDAR01..R13>                                       (13 months demand history)
    <KWH_ESCALON..>, <IMPTE_KWH_REG_1..10>, <IMPTE_KW_REG..> (kWh + per-concept importes)
- The standard cfdi:Concepto block is just "Energia" + "DAP" — a flat total,
  which is exactly the all-base/zero-split bug parse_bill_xml exists to avoid.

Why SAT doesn't cover it:
1. Addenda is a NON-FISCAL extension, outside the TFD seal. SAT Descarga Masiva
   returns the timbrado fiscal CFDI; addendas are routinely stripped / not stored.
   So SAT gives the RFC-stamped total, not the demanda/kWh breakdown.
2. SAT only has CFDIs stamped to the client RFC — nothing for público-en-general
   (XAXX010101000) accounts, and nothing before the RFC was registered with CFE.

Where SAT DOES help: fiscal reconciliation for RFC-registered C&I clients (the
receptor RFC on our stored CFDIs is the real client RFC, e.g. PCA8402024P8, not
genérico — so the fiscal CFDIs are retrievable). Use it as a cross-check/backup,
not the consumption source.

Deciding experiment (needs a client e.firma, not currently available): pull one of
these RFCs from SAT Descarga Masiva and diff the XML vs the harvested copy. If
SAT's copy retains the Addenda -> SAT wins for C&I and most scraping can retire.
Strong prior: it won't.

Refs #147 (browser-API/remote-download), #136 (WAF-reach, now fixed).
