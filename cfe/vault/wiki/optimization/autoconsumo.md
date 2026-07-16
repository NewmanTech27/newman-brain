---
title: "Autoconsumo — la figura legal de generación propia (régimen 2025)"
type: concept
tags: [cfe, gdmth, autoconsumo, generacion, cne, lse, venta-excedentes, compensacion, 2025]
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-09-autoconsumo-cne-2025, 2026-06-09-dacg-nota-juridico-comercial, 2026-06-04-gdmth, 2026-06-04-res142-2017-gen-dist]
---

# Autoconsumo — la figura legal de generación propia (régimen 2025)

> **Purpose:** What "Autoconsumo" formally means after the 2025 Ley del Sector Eléctrico, the three capacity tiers and their permit tracks, the compliance obligations, and how it relates to the < 0.7 MW [[medicion-neta]] path a typical GDMTH user uses. Anchored on [[2026-06-09-dacg-nota-juridico-comercial]] and the primary instruments in [[2026-06-09-autoconsumo-cne-2025]].

> **⚠ Major update (2025 regime).** "Autoconsumo" is now a **formal legal figure** (LSE arts. 30–34), not the colloquial "consume your own solar" sense. It is **defined at capacity ≥ 0.7 MW**, the permitting authority is the [[cne]] (no longer [[cre]]), and it replaces the old LIE‑2014 *autoabastecimiento* permit. The pre‑2025 framing is preserved at the bottom under **Historical**.

---

## What Autoconsumo is

A **Central Eléctrica with capacity ≥ 0.7 MW** that supplies, through a **Red Particular**, the on‑site *Necesidades Propias* of the permit holder — and optionally of other *Usuarias de Autoconsumo* grouped under a **Grupo de Autoconsumo**. It can be **aislado** (off‑grid) or **interconectado** (synchronized to the SEN, able to draw *Faltantes* and inject *Excedentes*). Defined in LSE art. 30 and DACG Num. 1.7‑I.

> **The 0.7 MW line is a definition, not just a permit threshold.** A plant **< 0.7 MW is *outside* the Autoconsumo figure entirely** — it stays a [[generador-exento]] under [[generacion-distribuida]] with **no permit, no registro, no CNE obligation**. So a typical GDMTH rooftop project (well under 0.7 MW) does *not* enter this regime; it stays on [[medicion-neta]].

---

## The three capacity tiers

| Tier | Permit track | Authority / basis | Studies | Est. timeline |
|---|---|---|---|---|
| **< 0.7 MW** | **None** — Generador Exento / [[generacion-distribuida|GD]] | Art. 30 LSE; Num. 1.7‑I DACG | n/a | weeks–months ([[interconexion-cre]]) |
| **0.7–20 MW interconectado** | **Simplified** permit (CNE) | Num. 2.2 DACG + Acuerdo 06‑VIII‑2025 | CENACE, **scoped to point of interconnection** | ~6–12 mo |
| **> 20 MW, or ≥ 0.7 MW aislado** | **Ordinary** permit (CNE) | Num. 2.3 DACG + Disposiciones de Permisos (23‑X‑2025) | CENACE, **full‑SEN** | ~12–24 mo |

Ventanilla for the simplified/ordinary tracks: **OPE** — ope.cne.gob.mx.

---

## Aislado vs. interconectado (LSE art. 31 vs. 32)

| | **Aislado** | **Interconectado** |
|---|---|---|
| Grid tie | Not connected to RNT/RGD; not synchronized to SEN | Synchronized to the SEN |
| Output | 100% on‑site, exclusively within the Red Particular | On‑site + may inject **Excedentes** / draw **Faltantes** |
| Studies / registro / MEM | None required (DACG 3.1) | Interconnection contract + CENACE studies; MEM representation |
| Permit | Required ≥ 0.7 MW (ordinary track) | Required ≥ 0.7 MW (simplified 0.7–20 MW; ordinary >20 MW) |

A plant can later convert aislado → interconectado by modifying the permit (DACG 3.3, RLSE art. 55).

---

## Excedentes — sale only to CFE

Interconnected surplus can be **injected without contraprestación** (renounce payment via *carta de renuncia*), or **sold exclusively to the Empresa Pública del Estado ([[cfe]])** under the *Contrato de venta de Excedentes de Autoconsumo y Productos Asociados* (DACG Anexo 1). **No sale to third parties** (LSE art. 32‑II; DACG Num. 4.6). The only *Productos Asociados* that can be transferred are **CEL and Potencia** (Num. 4.10).

Two interconnected sub‑modes (DACG Num. 4.2):
- **Sin venta de excedentes** — reverse‑power / under‑consumption protection device + *carta de renuncia*; MEM registration only to buy Faltantes.
- **Con venta de excedentes** — full MEM registration; CENACE studies on additional scenarios; excedentes liquidated at the Mercado de Energía de Corto Plazo, financial responsibility transferred 100% to CFE.

---

## The intermittency‑backup mandate → storage driver

An **intermittent** (PV / eólico) autoconsumo plant **must carry *respaldo propio*** — either a **[[sae-cc|SAE]] (battery)** or a contracted ramp/intermittency/variability backup service from CFE (LSE art. 32‑III; RLSE art. 59; DACG Num. 4.5). This makes storage attach a **regulatory requirement**, not just an economic choice, for any PV ≥ 0.7 MW going interconnected. See [[bess-savings-model]] for how the same battery also shaves demand. Excedentes themselves may be stored in a SAE before injection (Num. 4.4).

---

## Continuous‑compliance obligations (0.7–20 MW and up)

| Obligation | Rule | Source |
|---|---|---|
| **Min‑use of the plant** | demanda máx. de Usuarias / Capacidad Instalada ≥ 50% (convencional) / ≥ 30% (renovable) over any **12 continuous months**, else the permit's object disappears → termination (técnica‑justification window applies) | Num. 1.6‑I DACG; LSE art. 152‑IV |
| **Excedentes exclusivity** | sell only to CFE (Anexo 1 contract); no third parties | Art. 32‑II LSE; Num. 4.6 DACG |
| **Intermittent backup** | SAE or CFE coverage for ramp/intermittency/variability | Num. 4.5 DACG; Art. 59 RLSE |
| **Annual Registro de Autoconsumo** | update before CNE in **1T each year** (and on any change to the Grupo) | Art. 52 RLSE; Cap. VII DACG |
| **Redes Particulares independence** | a Red Particular cannot interconnect to another Red Particular | Num. 2.8 DACG |

---

## Project roadmap (simplified regime, from the nota)

1. **Diagnóstico energético** — consumption audit + regulatory classification against the 0.7 MW line (2–4 wk).
2. **Estructuración jurídico‑comercial** — EPC / PPA / arrendamiento / autodesarrollo; constitute the Grupo de Autoconsumo (1–2 mo).
3. **Solicitud de permiso CNE** — via OPE, per Acuerdo 06‑VIII‑2025 + Num. 2.2 DACG (3–6 mo).
4. **Estudios CENACE + Contrato de Interconexión** — per the MIC; run in parallel with step 3.
5. **Construcción + COD** — EPC build + Declaración de Entrada en Operación Comercial before CENACE (POC).
6. **Operación y cumplimiento** — annual Registro (1T), min‑use monitoring, excedentes via CFE.

---

## How this relates to a typical GDMTH PV/BESS project

Most commercial rooftop projects in the savings analyses sit **well below 0.7 MW**, so they stay on the **[[generador-exento]] + [[medicion-neta]]** path — no CNE permit, no autoconsumo obligations. The Autoconsumo regime becomes relevant when a site wants to **scale PV past 0.7 MW** (e.g. large industrial load like [[2026-06-09-456220800389-autoconsumo|Tototlán]]): above the line, the project must take a CNE permit, can only sell surplus to CFE, and must carry SAE/CFE backup. The scheme decision is mapped in [[scheme-comparison]].

---

## Related pages
- [[generacion-distribuida]] — the < 0.7 MW exempt tier this figure sits above
- [[generador-exento]] — the legal status for < 0.7 MW
- [[medicion-neta]] — the < 0.7 MW compensation scheme (distinct from venta de excedentes)
- [[scheme-comparison]] — eligibility decision tree across all tiers
- [[sae-cc]] / [[bess-savings-model]] — storage as the intermittency‑backup vehicle
- [[interconexion-cre]] — the interconnection procedure (now CNE/CENACE, MIC 2018)
- [[cne]] / [[cfe]] / [[cenace]] — the authorities and counterparties
- [[2026-06-09-autoconsumo-cne-2025]] — the primary regulatory package
- [[2026-06-09-dacg-nota-juridico-comercial]] — the commercial synthesis (anchor)

---

## Historical — autoabastecimiento under LIE 2014 (superseded)

> Retained for context. Under the **LIE 2014** framework (pre‑2025), large self‑supply ran through a **CRE *autoabastecimiento* permit** (no explicit size ceiling), and the Generador Exento medición‑neta path capped at **≤ 500 kW**. The 2025 Ley del Sector Eléctrico replaced this: "autoabastecimiento" as a permit modality gives way to the formal **Autoconsumo** figure above, the exempt ceiling rose **500 kW → 0.7 MW**, and permit authority moved **CRE → [[cne]]**. Existing autoabastecimiento permits' transition is governed by the LSE transitorios (not yet read in full).

Under that old scheme the distinctive billing feature was that demand formulas used **only CFE‑supplied quantities**:

```
Dmax_punta_facturable = min( Dmax_punta_CFE , kWh_CFE / (d × FC × 24) )
```

so a site self‑supplying part of its load showed proportionally lower measured demand *and* a lower [[demanda-facturable|umbral]]. Whether the new Autoconsumo regime preserves this CFE‑only demand netting for interconnected ≥0.7 MW plants is an open question (the DACG governs MEM settlement of Faltantes/Excedentes, not GDMTH demand‑charge mechanics). The old "facturación neta / venta de excedentes" choice for < 500 kW maps onto today's [[medicion-neta]] vs. facturación‑neta options for the < 0.7 MW exempt tier.
