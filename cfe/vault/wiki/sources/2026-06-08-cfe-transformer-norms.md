---
title: "Transformer Norms — CFE K0000-07 & NMX-J-351-3-ANCE-2016"
type: source
tags: [standard, transformer, mv]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-cfe-transformer-norms]
---

# Transformer Norms — CFE K0000-07 & NMX-J-351-3-ANCE-2016

**Type:** technical standards (two documents)
**Raw files:**
`raw/pdfs/2025-07-01 - Norma de transformadores trifasicos K0000-07.pdf`,
`raw/pdfs/2025-07-01 - Norma de transformadores y autotransformadores ... tipo seco NMJ-J-531.pdf`
*(the second's actual designation is **NMX-J-351-3-ANCE-2016**, not "NMJ-J-531" — filename misnomer)*

## Summary
Two transformer specs that govern the **MV step-down / distribution transformer** between
the CFE network and a GDMTH/GDMTO load — the equipment just upstream of the AC breakers in
[[protection-bos]] and downstream of the [[interconexion-cre|interconnection point]].
Relevant whenever a project's PV/BESS AC output (typically 480 V) must tie into the site's
MT service, and for the hosting-capacity math in
[[2026-06-08-manual-interconexion-500kw]] (which is expressed as "% of transformer capacity").

### CFE K0000-07 (May 2015)
CFE's own specification for **three-phase pad-mounted (tipo pedestal) transformers, 300 kVA
& 500 kVA, for underground distribution**. Covers construction, sectionalizer, protection
(internal fuses), insulating liquid, bushings, switchgear ratings, nameplate/marking, and
expected service life. This is the transformer class for medium commercial services fed
underground (hotel/resort campuses like Posadas).

### NMX-J-351-3-ANCE-2016
Mexican standard (adopts IEC 60076-5) for **dry-type distribution & power transformers and
autotransformers — ability to withstand short circuit**. Dry-type units are used indoors /
where fire-safe (no oil) transformers are required. Defines short-circuit withstand
capability and test methods.

## Key claims
- K0000-07 standardizes pad-mount transformers at **300 / 500 kVA**, underground feed — the practical MT interface size for mid-C&I sites.
- The interconnection hosting limits ("80% of transformer capacity") are sized against exactly these transformer ratings.
- NMX-J-351-3 dry-type units = indoor/fire-sensitive installs (e.g. inside hotels), aligned with IEC 60076-5 short-circuit withstand.

## Entities mentioned
- [[cfe]] — issues K0000-07 (CFE equipment spec)
- ANCE — issues NMX-J-351-3-ANCE-2016 (Mexican standardization body)

## Concepts mentioned
- [[interconexion-cre]] — hosting capacity is expressed as % of these transformers
- [[protection-bos]] — the AC breakers sit between the inverter and this transformer
- [[gdmth-bill-structure]] — the MT service these transformers feed

## Contradictions / tensions
None identified.

## Questions raised
- Which dry-type vs pad-mount class applies at the Posadas/Fiesta Inn sites? (drives whether K0000-07 or NMX-J-351-3 is the governing transformer spec for a given project).
