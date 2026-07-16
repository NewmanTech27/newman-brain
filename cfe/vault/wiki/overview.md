---
title: "Overview — CFE Brain"
type: overview
tags: []
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024, 2026-06-04-ley-sector-electrico-2025, 2026-06-04-dacg-sae-a113-2024, 2026-06-04-res142-2017-gen-dist, 2026-06-09-autoconsumo-cne-2025, 2026-06-09-dacg-nota-juridico-comercial]
---

# CFE Brain — Overview

*Living thesis document. Updated when the big picture shifts.*

## What this wiki is for

A structured knowledge base about **how CFE bills the GDMTH tariff** and how a PV or BESS installation changes that bill. It serves as the reasoning layer for two tools:

1. **GDMTH Billing Calculator** — reconstruct and validate any GDMTH bill from meter data
2. **PV/BESS Savings Engine** — compute savings under medición neta or autoconsumo; identify which scheme wins and why

---

## How the wiki is organized

```
billing/           ← GDMTH charge structure and bill reconstruction
optimization/      ← PV, BESS, and combined savings models; compensation schemes
eligibility/       ← Feasibility decisions: can we do X? which scheme applies?
regulatory/        ← Source documents, entities, background concepts
```

---

## The regulatory stack

```
Ley del Sector Eléctrico (LSE, March 2025) + Reglamento (RLSE, Oct 2025)   ← supreme framework; replaces LIE 2014
    ├── CNE — Comisión Nacional de Energía (sectorized under SENER)        ← 2025 regulator: permits + new DACGs
    │     └── DACG de Autoconsumo (12-XII-2025) + companions               ← the ≥0.7 MW figure (autoconsumo)
    │           ├── <0.7 MW            → no permit (Generador Exento / GD)
    │           ├── 0.7–20 MW interc.  → simplified CNE permit (Acuerdo 06-VIII-2025)
    │           └── >20 MW / aislado   → ordinary CNE permit (Disposiciones de Permisos 23-X-2025)
    └── Legacy CRE instruments (LIE-2014 era — content still used, authority migrating to CNE)
          ├── Tariff methodology: Acuerdo A/158/2024   ← FC=0.57, period schedules, demand formulas
          ├── Storage: Acuerdo A/113/2024              ← SAE-CC: no permit, no injection
          └── Distributed gen: RES/142/2017            ← Medición neta; Generadores Exentos (<0.7 MW)

NOM-001-SEDE-2012 (SENER)                       ← mandatory technical installation code
    ├── Art. 690: PV system installation          ← conductor sizing, max voltage, GFP, disconnects
    ├── Art. 480: Battery installation            ← ventilation, isolation, disconnect >50V
    └── Art. 705: Grid interconnection            ← 120% bus rule, anti-islanding, certified inverters

Process & safety layers
    ├── Manual de Interconexión <0.5 MW (SENER)   ← exempt-tier connect: solicitud→estudio→contrato→inspección→sync (interconexion-cre)
    ├── MIC (Manual de Interconexión, 2018)       ← ≥0.7 MW autoconsumo: CENACE studies, point-of-interconnection scope
    ├── NOM-009-STPS-2011                         ← work-at-height safety for rooftop installs
    └── CFE K0000-07 / NMX-J-351-3-ANCE           ← MV step-down transformer specs
```

The **CNE** (2025) is now the permitting/regulatory authority over generation; **CRE**'s LIE‑2014 instruments are still the wiki's rule *text* but their authority is migrating to CNE. The legal framework governs *whether and how* PV/BESS may be installed and billed; the NOM governs *how* the physical installation must be built; the process/safety layer governs *the steps to connect and the labor conditions*. All layers must be satisfied for any real project. The **0.7 MW line** is the pivot: below it a project is a permit‑free [[generador-exento]] on [[medicion-neta]]; at or above it the project enters the [[autoconsumo]] permit regime (CFE‑only excedentes, mandatory storage backup for intermittent plants).

---

## The equipment layer (BOM component library)

A new **[[equipment/index|Equipment Catalog]]** holds the vendor hardware we spec into projects, as category roll-ups: [[pv-modules]] (Trina/Seraphim/Tongwei ~720 Wp bifacial), [[string-inverters]] (Huawei SUN2000 20–150 kW), [[microinverters]], [[hybrid-inverters]] (Sigen 50–125 kW), [[bess]] (BYD MC Cube-T, Huawei LUNA2000, SigenStack), [[monitoring]], and [[protection-bos]]. A savings analysis picks hardware from here; the install/standards pages govern how it goes in; [[pv-degradation]] and [[solar-resource-data]] set the long-term generation assumptions (derate + yield bankability). Notably, the BYD MC Cube-T **2×1503 kW** rating matches the Posadas BESS power assumption in [[2026-06-08-780881200029-yearly-savings]].

---

## How a GDMTH bill works (in one paragraph)

A GDMTH bill has 9 components: energy charges (kWh × $/kWh, separately for punta/intermedio/base periods), flat per-kWh charges for transmisión, CENACE, and SCnMEM, two demand charges (capacidad based on punta-coincident peak, distribución based on monthly max peak), and a fixed monthly SSB charge. Both demand charges are capped by an **umbral** = kWh_total / (d × 0.57 × 24) — if your measured peak exceeds this cap, you pay the cap, not the peak. See [[gdmth-bill-structure]] for the full formula.

---

## How PV and BESS interact with that bill

- **PV reduces energy charges** (kWh × rate for each period), via medición neta credit netting
- **PV also reduces the umbral** (by lowering total kWh_red), which may reduce demand charges if the cap was binding
- **BESS reduces Dmax_punta** (peak shaving), which reduces the capacidad charge — but only if measured demand was below the umbral cap
- **The interaction:** PV lowering the umbral can neutralize BESS savings; combined savings ≠ PV savings + BESS savings. See [[pv-bess-combined]]

---

## Key confirmed parameters (calculator-ready)

| Parameter | Value | Source |
|---|---|---|
| GDMTH factor de carga (FC) | **0.57** | A/158/2024 Table 2 |
| Umbral formula | kWh_red / (d × FC × 24) | A/158/2024 §5.1 |
| SIN summer punta | 20:00–22:00 weekdays (2h) | CFE tariff page §6 |
| SIN winter punta | 18:00–22:00 weekdays (4h) | CFE tariff page §6 |
| BCS summer punta | 12:00–22:00 weekdays (10h) | CFE tariff page §6 |
| BC summer punta | 14:00–18:00 weekdays (4h) | CFE tariff page §6 |
| BC/BCS summer: Base period? | None — non-punta is Intermedio | CFE tariff page §6 |
| Max DG size (no permit) | **< 0.7 MW** (was 500 kW pre-2025) | LSE 2025 / DACG 12-XII-2025 Num. 1.7-I |
| Autoconsumo simplified permit | **0.7–20 MW** interconnected (CNE) | Num. 2.2 DACG + Acuerdo 06-VIII-2025 |
| Autoconsumo ordinary permit | **>20 MW**, or ≥0.7 MW aislado (CNE) | Num. 2.3 DACG + Disposiciones de Permisos |
| Autoconsumo excedentes buyer | **CFE only** (Empresa Pública del Estado) | LSE art. 32-II; DACG Num. 4.6 |
| Intermittent ≥0.7 MW backup | **SAE or contracted CFE** (mandatory) | LSE art. 32-III; DACG Num. 4.5; RLSE art. 59 |
| SAE-CC: grid injection? | Prohibited | A/113/2024 Ch.IV |
| SCnMEM rate | $0.0062/kWh (fixed for 2025) | A/158/2024 art. PRIMERO |

---

## Open gaps

1. **Monthly rate values** — partially closed: 12 months of SIN rates now captured from [[2026-06-08-cfe-bills-780881200029-fy25-26]]; other divisions still pending
2. ~~**RES/142/2017 post-2025 status**~~ — DG **ceiling raised to < 0.7 MW** and the **permit‑free status confirmed** by the [[2026-06-09-autoconsumo-cne-2025|CNE DACG (12‑XII‑2025)]]. Still open: the < 0.7 MW credit *mechanics* (netting, 12‑mo PML) — the DACG governs only the ≥0.7 MW figure, so medición neta is presumed intact but unconfirmed against the 2025 LSE/RLSE
3. ~~**Autoabastecimiento under new law**~~ — resolved as a **regime shift**: LIE‑2014 autoabastecimiento gives way to the formal **[[autoconsumo]]** figure (≥0.7 MW), authority **CRE → [[cne]]**. New open item: validity/migration of legacy CRE instruments (A/158/2024, A/113/2024, RES/142/2017) under the 2025 framework
4. **Ley del Sector Eléctrico / RLSE full text** — autoconsumo articles (30–34 LSE; 50–61 RLSE) now captured via the DACG; tariff‑authority articles and the < 0.7 MW compensation provisions still pending a direct read
5. **Legacy autoabasto porteo + on‑site DG coexistence** — can a load center under a legacy (LIE/LSP‑era) autoabasto porteo contract simultaneously hold a [[medicion-neta]] interconnection on the same meter? Raised by the [[gepp]] brief (Ixtlahuacán/[[tala-energy]], Proplasa/[[enel-mexico]]); no primary source either way. Related: is the **0.7 MW exempt ceiling read per meter/RPU or per centro de carga** when several meters share one predio (Proplasa: 3 meters)?
6. **Off‑site PPA / suministro calificado under the 2025 LSE** — no wiki page; the MEM supply route for >1 MW users (the natural reading of GEPP's "PPA" ask) is unresearched
7. ~~**Engine arbitrage fix pending (golden-test decision)**~~ — **RESOLVED 2026-06-11 (user-approved):** `engine.py` now limits BESS discharge to punta weekdays (Mon–Fri minus festivos) capped at the bill's punta kWh, and applies the FP-bonificación claw-back; golden test re-baselined peso-exact to the corrected reference (Ahorro $7,083,252 / 23.5%; 18 checks incl. the disch≤punta-kWh physics guard). Residual: the festivos list is the statutory 7 — confirm CFE's exact festivo calendar against a printed bill; **[[2026-06-09-456220800389-yearly-savings|Tototlán]] filed numbers are stale** (old engine; its negative arbitrage shrinks under the correction → slight upside) — re-run when convenient

---

*Last updated: 2026-06-09 — Ingested the **2025 Autoconsumo regime**: the CNE DACG (12‑XII‑2025) + companions ([[2026-06-09-autoconsumo-cne-2025]]) and the user's commercial synthesis ([[2026-06-09-dacg-nota-juridico-comercial]]). Reframed [[autoconsumo]] as the formal ≥0.7 MW figure (three tiers), moved permit authority **CRE → [[cne]]**, and added the **mandatory storage backup** for intermittent ≥0.7 MW plants. Prior (2026-06-08): equipment catalog, interconnection procedure, research reports → [[pv-degradation]]/[[solar-resource-data]].*
