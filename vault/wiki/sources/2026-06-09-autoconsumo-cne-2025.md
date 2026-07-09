---
title: "Autoconsumo CNE 2025 — DACG + companion instruments (regulatory package)"
type: source
tags: [autoconsumo, cne, lse, rlse, dacg, generacion, 2025, regulacion]
created: 2026-06-09
updated: 2026-06-09
sources: []
---

# Autoconsumo CNE 2025 — DACG + companion instruments

**Type:** regulation (package of 4 DOF instruments)
**Emisor:** [[cne|Comisión Nacional de Energía]] (sectorizada a [[sener]])
**Raw files:** `raw/pdfs/(DOF 2025-12-12 SENER) Acuerdo CNE DACG Autoconsumo Energia Electrica.pdf` (+ `_extracted.txt`), `raw/articles/DOF 06 08 2025.md`, `raw/pdfs/(DOF 2025-10-07 SENER) Acuerdo CNE Formato Autoconsumo 0.7-20MW.pdf` (+ `_extracted.txt`), `raw/articles/DOF - 03 10 2025.md`

> This page consolidates the **primary instruments** of Mexico's 2025 Autoconsumo regime. The analytical companion (comparative tables, project roadmap) is the user-authored brief at [[2026-06-09-dacg-nota-juridico-comercial]].

## Marco normativo (the package)

| # | Instrument | DOF | Code | Role |
|---|---|---|---|---|
| 1 | **DACG para regular la figura de Autoconsumo de Energía Eléctrica** | 12‑XII‑2025 | — | Master regulation (CNE Acuerdo CT/11.SO/43‑2025) |
| 2 | **Acuerdo CNE — Requisitos permiso Autoconsumo interconectado 0.7–20 MW** (trámite simplificado) | 06‑VIII‑2025 | 5764827 | The simplified-permit requirements list (full text captured) |
| 3 | **Acuerdo CNE — Formato de solicitud Autoconsumo 0.7–20 MW** | 07‑X‑2025 | — | The application form for the simplified trámite |
| 4 | **Reglamento de la Ley del Sector Eléctrico (RLSE)** | 03‑X‑2025 | 5769155 | Implementing regulation (arts. 50–61 = autoconsumo) |
| — | *Ley del Sector Eléctrico (LSE)* + *Ley de la CNE (LCNE)* | vigente 2025 | — | The enabling statutes (arts. 17–19, 30–34 LSE) |
| — | *Disposiciones de Permisos (gen. + almacenamiento)* | 23‑X‑2025 | — | Ordinary permit track (>20 MW / aislado), referenced by the DACG |

## Summary

The 2025 Ley del Sector Eléctrico replaces the LIE‑2014 framework and creates **Autoconsumo** as a *formal* generation figure: a Central Eléctrica **with capacity ≥ 0.7 MW** that supplies, through a **Red Particular**, the on‑site Necesidades Propias of the permit holder (and any other Usuarias in its **Grupo de Autoconsumo**). The DACG (12‑XII‑2025) operationalizes arts. 30–34 LSE and arts. 50–61 RLSE. Permitting authority is now the [[cne]] (not [[cre]]). See [[autoconsumo]] for the synthesized concept.

Two structural splits define the figure:

- **Aislado vs. interconectado** (LSE art. 31 vs. 32; DACG Cap. III vs. IV). *Aislado* is not connected to the RNT/RGD, devotes all output to on‑site use, and needs no Estudios/registro/MEM representation. *Interconectado* synchronizes with the SEN and may draw **Faltantes** and inject **Excedentes** (with or without contraprestación).
- **Capacity tier** sets the permit track (Cap. II):

| Tier | Track | Authority / basis |
|---|---|---|
| **< 0.7 MW** | Outside the Autoconsumo figure — no permit (stays [[generador-exento]] / [[generacion-distribuida]]) | Art. 30 LSE; Num. 1.7‑I DACG |
| **0.7–20 MW interconectado** | **Simplified** permit | Num. 2.2 DACG + Acuerdo 06‑VIII‑2025 |
| **>20 MW, or ≥0.7 MW aislado** | **Ordinary** permit | Num. 2.3 DACG + Disposiciones de Permisos (23‑X‑2025) |

## Key claims

- **Autoconsumo ≥ 0.7 MW.** The figure is *defined* at capacity ≥ 0.7 MW (DACG Num. 1.7‑I; LSE art. 30). Below that there is no permit, no registro, no CNE obligation — the old [[generacion-distribuida|DG]]/[[generador-exento|generador exento]] path.
- **Excedentes sold only to CFE.** Interconnected surplus may be injected without contraprestación, or sold **exclusively to the Empresa Pública del Estado** ([[cfe]]) under the *Contrato de venta de Excedentes de Autoconsumo y Productos Asociados* (Anexo 1). No third‑party commercialization. (LSE art. 32‑II; DACG Num. 4.6.)
- **Backup mandate for intermittent generation.** An intermittent (PV/eólico) autoconsumo plant **must** carry *respaldo propio* — a **[[sae-cc|SAE]] (battery)** or a contracted ramp/intermittency/variability service from CFE (LSE art. 32‑III; RLSE art. 59; DACG Num. 4.5). This is a direct regulatory driver for storage attach on ≥0.7 MW PV. See [[bess-savings-model]].
- **Two interconnected sub‑modes** (DACG Num. 4.2): *sin venta de excedentes* (reverse‑power/under‑consumption protection + carta de renuncia; MEM registration only to buy Faltantes) and *con venta de excedentes* (full MEM registration; CENACE studies on more scenarios).
- **CENACE limited‑scope studies (simplified track).** Interconnection studies are scoped to the point of interconnection per the MIC (Manual de Interconexión, DOF 09‑II‑2018), lighter than the full‑SEN studies of the ordinary track.
- **Continuous‑compliance obligations:** annual *Registro de Autoconsumo* in 1T each year (RLSE art. 52; DACG Cap. VII); **min‑use** — demanda máxima de Usuarias / Capacidad Instalada ≥ 50% (convencional) / ≥ 30% (renovable) over any 12 continuous months, else the permit's object disappears and it terminates (DACG Num. 1.6‑I; LSE art. 152‑IV); **Redes Particulares independence** — cannot interconnect to other Redes Particulares (Num. 2.8).
- **Productos Asociados** the interconnected plant can sell to CFE are limited to **CEL and Potencia** (Num. 4.10).
- **Permit requirements (0.7–20 MW simplified, Acuerdo 06‑VIII‑2025, Primero):** CNE form; legal personality; technology + AC/DC capacity + annual generation estimate; georeferenced location; intermittent‑backup statement; CENACE study oficio (Resultados del Estudio de Impacto per the MIC); simplified single‑line diagram; works program (start/finish/COD); business plan (if not yet built); 2 yrs financials + experience; shareholding diagram; payment of derechos. Entry into force gated on the RLSE + Ley de Planeación reglamentos being in force.

## Entities mentioned
- [[cne]] — issues the permits and the DACG; órgano desconcentrado of [[sener]] with technical independence (LCNE)
- [[cfe]] — Empresa Pública del Estado; sole buyer of excedentes; provider of backup service
- [[cenace]] — runs the interconnection Estudios and confirms Confiabilidad of excedentes injection
- [[cre]] — its LIE‑2014 generation‑permit role is superseded by CNE under this regime
- [[sener]] — the secretariat CNE is sectorized under; issued the LSE/RLSE framework

## Concepts mentioned
- [[autoconsumo]] — the synthesized concept page (three tiers, obligations, roadmap)
- [[generacion-distribuida]] / [[generador-exento]] — the <0.7 MW exempt path the figure sits above
- [[sae-cc]] / [[bess-savings-model]] — storage as the intermittency‑backup vehicle
- [[interconexion-cre]] — the interconnection procedure (now CNE/CENACE, MIC 2018)
- [[medicion-neta]] — the <0.7 MW compensation scheme, distinct from this ≥0.7 MW venta‑de‑excedentes regime

## Contradictions / tensions
- **0.5 MW → 0.7 MW** definitively supersedes [[2026-06-04-res142-2017-gen-dist|RES/142/2017]]'s 0.5 MW exempt ceiling. Noted on [[generacion-distribuida]].
- **CRE → CNE** for generation permits supersedes the LIE‑2014 autoabastecimiento/permit role described on [[cre]] and the old [[autoconsumo]] page. Flagged on both.
- The DACG references the **MIC published 09‑II‑2018**, whereas the wiki's [[2026-06-08-manual-interconexion-500kw|Manual <0.5 MW]] is the DOF‑2016 small‑scale manual — different instruments for different tiers.

## Questions raised
- Does medición neta (period netting + 12‑mo PML credit) survive for the <0.7 MW exempt path under the 2025 Ley, or is it folded into a new compensation model? The DACG governs only ≥0.7 MW; the <0.7 MW credit mechanics are not addressed here.
- Tariff‑methodology authority: does [[2026-06-04-acuerdo-a158-2024|A/158/2024]] (CRE) remain valid, or migrate to CNE? (CNE already owns tariff‑adjustment methodology per the GDMTH page.)
