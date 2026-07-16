---
title: "Generación Distribuida (GD)"
type: concept
tags: [cfe, generacion-distribuida, solar, interconexion, gdmth]
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-04-res142-2017-gen-dist, 2026-06-08-pdse-2025-2039, 2026-06-09-autoconsumo-cne-2025]
---

# Generación Distribuida (GD)

Electricity generation at or near the point of consumption, typically from renewable sources, interconnected to the local distribution network (RGD). In Mexico's regulatory framework, "Generación Distribuida" specifically refers to plants with capacity **< 0.7 MW (700 kW)** that operate as **Generadores Exentos** — exempt from the full market participation requirements of larger generators.

> **⚠ Threshold updated 2025 — supersedes the old 0.5 MW.** Under the **Ley del Sector Eléctrico (LSE, DOF 18‑mar‑2025)**, the GD/exempt ceiling is now **less than 0.7 MW**. The earlier **0.5 MW (500 kW)** limit from [[2026-06-04-res142-2017-gen-dist|RES/142/2017]] is the *prior* value, now obsolete for sizing. Confirmed two ways: the [[2026-06-08-pdse-2025-2039|PDSE 2025‑2039]] §2.2.3 (*"capacidad máxima de menos de 0.7 MW, artículo 25 LSE"*), and — **definitively** — by the **CNE DACG de Autoconsumo (DOF 12‑XII‑2025)**, which *defines* the [[autoconsumo]] figure as capacity **≥ 0.7 MW** (Num. 1.7‑I). Anything **< 0.7 MW therefore sits outside the permit regime entirely**: no permit, no registro, no CNE obligation (Art. 30 LSE; Num. 2.1 DACG).

> **The rung above:** generation **≥ 0.7 MW** leaves GD and enters the formal **[[autoconsumo]]** figure — a [[cne|CNE]] permit (simplified for 0.7–20 MW interconnected, ordinary above), excedentes sold only to [[cfe]], and a mandatory storage/backup for intermittent plants. See [[2026-06-09-autoconsumo-cne-2025]].

Governed by [[2026-06-04-res142-2017-gen-dist|RES/142/2017]] (interconnection process and compensation models), with the capacity ceiling now set by the 2025 LSE and the permit‑free status confirmed by the 2025 DACG.

## Scope

- Capacity < 0.7 MW per plant (was ≤ 0.5 MW pre-2025)
- Connected to the Redes Generales de Distribución (RGD)
- Typically solar photovoltaic, but technology-neutral
- Operated by the load-center user (the same user who has a CFE supply contract)

## Regulatory path

1. User signs a **Contrato de Interconexión** with CFE Distribución
2. User (now a **[[generador-exento]]**) signs a **Contrato de Contraprestación** with [[cfe-ssb]]
3. User selects a compensation model: [[medicion-neta]] (default), facturación neta, or venta total
4. No interconnection study required in most typical cases

## Relevance to GDMTH users

A commercial or industrial user on the [[gdmth]] tariff can install a DG plant < 0.7 MW and:
- Offset energy consumption by period under net metering
- Reduce energy charges (punta, intermedio, base kWh billed)
- **Does not directly reduce demand charges** (Cargo por Capacidad, Cargo por Distribución) since DG production during off-peak hours doesn't affect Dmax_punta

For demand charge reduction, a [[sae-cc]] battery is more effective — it can discharge during the punta period to lower the peak demand reading.

**Combination strategy:** DG (solar) + SAE-CC battery can address both energy and demand components simultaneously.

## Mexico's DG integration stage

Per RES/142/2017 (2017): Mexico was at ~151 MW DG, 0.22% of installed capacity — classified as Stage 1 (low penetration). The review trigger was 5% of installed capacity or 1 year.

Per [[2026-06-08-pdse-2025-2039|PDSE 2025-2039]]: by **2024, cumulative GD reached 4,449.79 MW** (>99.4% solar PV) across >405,000 contracts producing 6,777 GWh — roughly a 30× increase since 2017. The 0.5 MW → 0.7 MW ceiling change is part of the 2025 legal overhaul accompanying this growth.

## Related concepts

- [[interconexion-cre]] — the administrative procedure to connect a DG plant (per the [[2026-06-08-manual-interconexion-500kw|Manual de Interconexión]])
- [[medicion-neta]] — the default compensation model for Generadores Exentos
- [[generador-exento]] — the legal status of DG users
- [[sae-cc]] — battery storage; complementary technology for demand reduction
- [[gdmth]] — the tariff under which GD users receive time-of-use net metering credits
- [[horarios-y-divisiones]] — determines which period credits are generated in

## How sources treat this

- [[2026-06-04-res142-2017-gen-dist]]: defines the full framework — interconnection process, compensation models, technical specs
- [[2026-06-08-pdse-2025-2039]]: confirms the **< 0.7 MW** ceiling (art. 25 Ley del Sector Eléctrico) and 2024 GD capacity (4,449.79 MW)
- [[2026-06-09-autoconsumo-cne-2025]]: defines [[autoconsumo]] at **≥ 0.7 MW**, confirming that **< 0.7 MW is permit‑free** (no permit, registro or CNE obligation)

## Open questions

- ✅ **Resolved:** GD/exempt ceiling is **< 0.7 MW** (LSE 2025), up from 0.5 MW — and **< 0.7 MW is permit‑free** (DACG 12‑XII‑2025, Num. 1.7‑I/2.1).
- ⚠ **Narrowed:** Does the 2025 Ley keep RES/142/2017's compensation models (medición neta / facturación neta / venta total) for the < 0.7 MW tier? The DACG governs only the **≥ 0.7 MW** [[autoconsumo]] figure (MEM settlement, CFE‑only excedentes); it does **not** address < 0.7 MW credit mechanics, so the medición‑neta path is presumed intact but unconfirmed against the 2025 LSE/RLSE. See [[medicion-neta]].
- What is Mexico's total DG capacity now vs the 5% trigger (2024: 4,449.79 MW)?
