---
title: "Scheme Comparison — Medición Neta vs. Autoconsumo: When Each Applies and Which Wins"
type: analysis
tags: [cfe, gdmth, solar, bess, medicion-neta, autoconsumo, cne, eligibility, comparacion, 2025]
created: 2026-06-04
updated: 2026-06-09
sources: [2026-06-09-autoconsumo-cne-2025, 2026-06-09-dacg-nota-juridico-comercial, 2026-06-04-gdmth, 2026-06-04-res142-2017-gen-dist, 2026-06-04-dacg-sae-a113-2024]
---

# Scheme Comparison — Medición Neta vs. Autoconsumo

> **Purpose:** Decision reference for choosing a compensation/regulatory scheme for a GDMTH user installing PV, BESS, or both. Answers "can we do X?" with yes/no/conditional and cites the governing rule.

> **⚠ Updated for the 2025 regime.** The exempt ceiling rose **500 kW → 0.7 MW**, permit authority moved **CRE → [[cne]]**, and large self‑supply is now the formal **[[autoconsumo]]** figure (≥ 0.7 MW), replacing LIE‑2014 *autoabastecimiento*. The numbers and authorities below reflect the new regime.

---

## The capacity line that decides everything

```
PV / generator capacity?
  < 0.7 MW  → Generador Exento / GD — NO permit, NO CNE obligation
             └── compensation: medición neta (default) or facturación neta
             └── battery: SAE-CC (no injection), no permit
  ≥ 0.7 MW  → Autoconsumo figure (LSE arts. 30–34) — CNE permit required
             ├── 0.7–20 MW interconnected → SIMPLIFIED permit (Num. 2.2 DACG + Acuerdo 06-VIII-2025)
             └── > 20 MW / aislado ≥0.7 MW → ORDINARY permit (Num. 2.3 DACG + Disposiciones de Permisos)
```

See [[autoconsumo]] for the full tier table and obligations; [[generacion-distribuida]] / [[generador-exento]] for the exempt path.

---

## Quick eligibility checker

| Question | Answer | Governing rule |
|---|---|---|
| Can a GDMTH user install rooftop solar without a CNE permit? | **Yes**, up to **< 0.7 MW** | Art. 30 LSE; Num. 1.7‑I DACG (was 500 kW under RES/142/2017) |
| Can a GDMTH user install a battery without any permit? | **Yes** (SAE‑CC, no injection) | A/113/2024, Ch. IV |
| Can a battery inject electricity into the CFE grid? | **No** under SAE‑CC | A/113/2024 — injection prohibited |
| Can a GDMTH user with 300 kW solar do medición neta? | **Yes** | RES/142/2017 |
| Can a GDMTH user with 800 kW solar do medición neta? | **No** — exceeds the < 0.7 MW exempt cap | Art. 30 LSE |
| Can a GDMTH user with 800 kW solar generate at all? | **Yes, with a CNE Autoconsumo permit** (0.7–20 MW simplified) | Num. 2.2 DACG + Acuerdo 06‑VIII‑2025 |
| Can an Autoconsumo plant sell its surplus? | **Only to CFE** (Empresa Pública del Estado) | Art. 32‑II LSE; Num. 4.6 DACG |
| Must a ≥0.7 MW intermittent PV plant carry storage? | **Yes** — SAE or contracted CFE backup | Art. 32‑III LSE; Num. 4.5 DACG; Art. 59 RLSE |
| Do solar credits under medición neta reduce demand charges? | **Indirectly** — via umbral effect only | A/158/2024 §5.1 + umbral interaction |
| Does BESS reduce energy charges? | **No directly** — shifts demand timing | Inferred from billing mechanics |
| Can PV and BESS be installed together (< 0.7 MW)? | **Yes** | RES/142/2017 + A/113/2024 |
| Do expired net metering credits settle at retail rates? | **No** — at PML (spot price) | RES/142/2017 Annex I |

---

## Feasibility conditions by technology

### PV — exempt path (< 0.7 MW, medición neta)

**Requirements:**
1. PV plant **< 0.7 MW** at a single interconnection point
2. Contrato de Interconexión with CFE Distribución
3. Contrato de Contraprestación with [[cfe-ssb|CFE SSB]] (medición neta)
4. Bidirectional meter per CFE spec

**Verdict:** Straightforward for most GDMTH users. No permit. Process takes weeks to months. See [[medicion-neta]].

> **Citation:** RES/142/2017 (compensation models); 0.7 MW ceiling per Art. 30 LSE 2025.

### BESS — SAE‑CC path (any tier, no injection)

**Requirements:**
1. No grid injection at any time
2. Battery power ≤ contracted demand (net of other loads)
3. CRE/CNE notification within 90 business days (medium/high tension)
4. Technical documentation (spec sheet, single‑line diagram, statement of no injection)

**Verdict:** Yes, no permit required — notification is administrative, not an approval gate. See [[sae-cc]].

> **Citation:** A/113/2024, Ch. IV. *(Authority note: A/113/2024 is a CRE DACG; whether it migrates to CNE under the 2025 Ley is an open question — the SAE figure itself is now in LSE art. 3‑L.)*

### PV + BESS combined (< 0.7 MW, medición neta + SAE‑CC)

**Requirements:** all of the above. BESS and PV are treated independently under their respective frameworks.

**Verdict:** Yes — the most common commercial configuration. See [[pv-bess-combined]].

### Autoconsumo permisionado (≥ 0.7 MW)

**Requirements:**
1. **CNE generation permit** — simplified (0.7–20 MW interconnected) or ordinary (>20 MW / aislado)
2. CENACE interconnection studies (scoped to point of interconnection in the simplified track)
3. Contrato de Interconexión; for intermittent PV, **SAE or contracted CFE backup** (mandatory)
4. Surplus sold only to CFE; annual Registro de Autoconsumo (1T); min‑use ≥ 50%/30% over 12 mo

**Verdict:** Conditionally yes — requires the CNE permit process. Timeline ~6–12 mo (simplified) / 12–24 mo (ordinary). Best for sites that need generation **above the 0.7 MW exempt line**. See [[autoconsumo]].

> **Citation:** LSE arts. 30–34; DACG 12‑XII‑2025 (Num. 2.2/2.3); Acuerdo 06‑VIII‑2025.

---

## Financial comparison: medición neta vs. autoconsumo permisionado

### Energy savings

| Metric | Medición neta (< 0.7 MW) | Autoconsumo (≥ 0.7 MW) |
|---|---|---|
| Energy offset mechanism | Period netting + credit carryover | Direct self‑consumption; MEM settlement of Faltantes/Excedentes |
| Value of solar kWh | Retail rate (credits applied) or PML (expired) | Retail rate avoided on self‑consumed kWh; excedentes at PML (to CFE only) |
| Surplus settlement | PML at 12‑month expiry | Sold to CFE at Mercado de Energía de Corto Plazo (or renounced) |

### Demand savings

| Metric | Medición neta | Autoconsumo (interconectado) |
|---|---|---|
| What goes into the umbral | CFE net kWh (after solar netting) | Site demand net of self‑generation (CFE‑only netting under LIE was the old rule; not re‑confirmed under 2025 Ley) |
| BESS interaction | BESS + PV interact as in [[pv-bess-combined]] | Storage is **mandatory** for intermittent PV (Num. 4.5) and also shaves demand |

**For large generators (≥ 0.7 MW):** self‑supply still drives demand down by lowering the CFE‑drawn peak; the open question is whether the 2025 regime preserves the old autoabastecimiento CFE‑only demand‑netting formula for GDMTH billing. Flagged on [[autoconsumo]] and [[demanda-facturable]].

### Which scheme wins?

| Site profile | Recommendation |
|---|---|
| < 0.7 MW PV, goal = reduce energy bill | **Medición neta** — no permit, fast, effective |
| < 0.7 MW PV + BESS, goal = reduce demand | **Medición neta + SAE‑CC** — combined addresses both components |
| Need generation **≥ 0.7 MW** | **Autoconsumo permit** (simplified if ≤ 20 MW); plan for SAE backup + CFE‑only excedentes |
| Consistently over‑generates surplus | Size PV to consumption (avoid PML expiry), or accept CFE‑only sale under autoconsumo |
| Large industrial wanting max self‑supply | Autoconsumo ≥ 0.7 MW; demand reduction on CFE‑drawn quantities can be large — but permit + obligations apply |

---

## Summary answer table

| Use case | Possible? | Scheme | Governing rule | Conditions |
|---|---|---|---|---|
| 250 kW solar + net metering | ✓ Yes | Medición neta | RES/142/2017; Art. 30 LSE | Contrato de Interconexión + Contraprestación |
| 200 kWh battery (no injection) | ✓ Yes | SAE‑CC | A/113/2024 | Notify within 90 business days |
| 250 kW solar + 200 kWh battery | ✓ Yes | Medición neta + SAE‑CC | Both above | Both contracts; umbral interaction applies |
| 750 kW solar | Conditional | **Autoconsumo (simplified)** | Num. 2.2 DACG + Acuerdo 06‑VIII‑2025 | CNE permit; SAE backup; excedentes to CFE only |
| 5 MW solar | Conditional | Autoconsumo (simplified, ≤ 20 MW) | Num. 2.2 DACG | CNE permit; CENACE studies; Registro 1T |
| Sell surplus to a third party | ✗ No | N/A | Art. 32‑II LSE | Excedentes only to CFE |
| Battery injects to grid at night | ✗ No | N/A | A/113/2024 | SAE‑CC prohibits injection |

---

## Related pages

- [[medicion-neta]] — net metering rules in full (< 0.7 MW)
- [[autoconsumo]] — the ≥ 0.7 MW figure: tiers, obligations, roadmap
- [[generador-exento]] — legal status for the exempt tier
- [[pv-savings-model]] / [[bess-savings-model]] / [[pv-bess-combined]] — the savings mechanics
- [[cne]] — the permitting authority for ≥ 0.7 MW
- [[2026-06-09-autoconsumo-cne-2025]] — the primary regulatory package
