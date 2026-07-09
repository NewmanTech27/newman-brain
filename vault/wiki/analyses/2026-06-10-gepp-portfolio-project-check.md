---
title: "GEPP portfolio project check — Ixtlahuacán, Acapulco, Cancún, Proplasa"
type: analysis
tags: [gepp, project-check, autoabasto, ppa, abasto-aislado, pv, fp-correction]
created: 2026-06-10
updated: 2026-06-10
sources: [2026-06-10-perfil-consumo-gepp-2025-26]
cliente: gepp
status: vigente
---

# GEPP portfolio project check — Ixtlahuacán, Acapulco, Cancún, Proplasa

**Question:** [[gepp]]'s brief (RESUMEN_ sheet of [[2026-06-10-perfil-consumo-gepp-2025-26]]): (1) Ixtlahuacán and Proplasa — can they **combine their legacy autoabasto contracts with on-site PV**? (2) Acapulco and Cancún — is a **PPA or "abasto aislado"** viable?

**Fact tiers used here:** all consumption/$ figures are **client-Excel data** (not CFE-bill-validated — the engine has not run; no bills in `raw/bills/`). Regulatory logic is **source-confirmed** via the cited wiki pages. Sizing/savings statements are **qualitative assumptions** pending bills + interval data.

---

## Portfolio snapshot (2025, client data)

| Site | División | kW contratada | kWh 2025 | Recibo 2025 | FP | Cargo FP 2025 (sin IVA) |
|---|---|---|---|---|---|---|
| Ixtlahuacán | Jalisco | 5,000 | 22.17 GWh | $60.95M | 93.6–95.7% | ~$55k (sporadic) |
| Acapulco | Centro Sur | 2,271 | 8.91 GWh | $32.89M | **85–86%** | **$1,716,053** |
| Cancún | Peninsular | 1,500 | 4.75 GWh | $18.55M | **~89%** | **$597,756** |
| Proplasa (PR1+PR2+TAP) | Valle de México Norte | 11,039 | 92.0 GWh | $229.5M | 97–99.5% | bonificación (credit) |
| **Whole portfolio** | — | — | **411.7 GWh** | **$1,205.3M** | ~96% | $4.83M |

---

## 1. Ixtlahuacán — autoabasto (Tala) + on-site PV

**Tariff:** GDMTH-equivalent, Jalisco (SIN schedule, [[horarios-y-divisiones]]); rates routed through [[tala-energy]]'s porteo at CFE-equivalent prices **minus 10% descuento** on energía.

**Current structure:** Tala (bagasse cogen) covers ~100% of consumption **Dec–May (zafra)** and ~0% **Jun–Nov** — 49.5% annual. The CFE-only half of the year is the expensive half.

**Verdict: feasible, and PV is well-matched — with one regulatory question to close.**

- **Regulatory tier** ([[generador-exento]], [[autoconsumo]]): PV **< 0.7 MW** = permit-free, [[medicion-neta]]. PV ≥ 0.7 MW = autoconsumo **simplified CNE permit** (0.7–20 MW interconnected), excedentes CFE-only, and **mandatory SAE storage or CFE backup** because PV is intermittent — a built-in BESS-attach driver.
- **The open question (flagged, do not assert):** whether a load center already under a **legacy autoabasto porteo contract** can simultaneously hold a medición neta interconnection contract on the same meter. Physically PV reduces offtake before the meter either way; contractually this is unconfirmed → added to [[overview]] open gaps. The autoabasto contract's **take-or-pay / committed-volume terms** (unknown) determine whether PV cannibalizes contracted Tala volumes at a penalty.
- **Economics shape:** PV displaces kWh at full CFE energy rates Jun–Nov and at ~90% of CFE rates (Tala's discounted price) Dec–May — a mild seasonal haircut, not a blocker. Per the SIN invariant, **PV ⊥ punta**: capacidad/distribución stay untouched; punta is 9.7% of kWh.
- **Anomaly worth auditing:** Dem. Máx. spiked to 5,872 kW (Abr-25) / 7,310 kW (May-25), **above the 5,000 kW contratada** — verify on real bills; potential billing/contract exposure.

## 2. Acapulco — PPA or abasto aislado

**Tariff:** GDMTH Centro Sur; flat ~1.5–1.8 MW demand profile; punta 9.8% of kWh.

**Verdict: "abasto aislado" is the wrong tool; the right sequence is FP correction now → on-site PV (exento or Grupo de Autoconsumo PPA) → BESS evaluated on bills.**

- **FP first ($1.72M/yr sin IVA, source-confirmed from the workbook):** FP is 85–86% **every month** — chronic, like the Tototlán case ([[2026-06-09-456220800389-yearly-savings]]). A capacitor bank / VAr correction is the highest-ROI action on this site, paybacks of months, orthogonal to everything else.
- **Abasto aislado** ([[autoconsumo]] — aislado vs interconectado): going aislado means leaving the SEN — **ordinary CNE permit (~12–24 mo) at any size ≥ 0.7 MW**, no Faltantes from the grid, so a flat 24/7 industrial load would need firm on-site generation (thermal/cogen + storage), not PV alone. For a 1.7 MW bottling plant this is a major infrastructure project, not a procurement tweak. Not recommended as the framing.
- **On-site PPA (viable):** the [[autoconsumo]] figure explicitly supports third-party structures — EPC / PPA / arrendamiento, with GEPP as Usuaria in a **Grupo de Autoconsumo** under the developer's permit (≥ 0.7 MW), or a simple <0.7 MW [[generador-exento]] system. **Off-site PPA** (suministro calificado / MEM under the 2025 LSE) has **no wiki page — unresearched, flagged as a gap**, not asserted.
- **BESS:** punta share ~10% and flat demand suggest capacidad is punta-coincident → BESS shave plausible, but sizing needs bills + interval data ([[bess-savings-model]]).

## 3. Cancún — PPA or abasto aislado

Same verdict as Acapulco, scaled down (4.75 GWh, $18.55M, 1,500 kW):

- **FP correction: $0.60M/yr** sin IVA, chronic ~89% — do it now.
- Abasto aislado: same objections, smaller load makes it even less proportionate.
- On-site PV: Peninsular división — we already model this división from [[2026-06-08-cfe-bills-780881200029-fy25-26]] (Grupo Posadas Cancún); rates here: int $2.08/punta $2.32/kWh — **the most attractive energy rates in the portfolio for PV displacement**. <0.7 MW exento is proportionate to this site (~35–40% of a ~4.7 GWh load, subject to roof area).
- BESS: punta share 10.9%, highest in the group — candidate, pending bills.

## 4. Proplasa — autoabasto (ENEL) + on-site PV

**Structure:** one predio, three GDMTH meters (PR1 2,600 / PR2 5,625 / TAP 2,814 kW), Valle de México Norte. 92 GWh/yr — GEPP's largest site. [[enel-mexico]] supplied 69.6% in 2025 at $1.78–1.92/kWh (≈ intermedia level).

**Verdict: same coexistence question as Ixtlahuacán; the 2026 ENEL collapse makes this urgent; multi-meter structure is a sizing lever to clarify.**

- **Urgency (source-confirmed):** ENEL's share collapsed from ~55% (Ene–Feb 2026) to **~16% (Mar–Abr 2026)** — every lost ENEL kWh is replaced at full CFE rates (PR1's recibo +55% Feb→Mar). **Ask GEPP why** — if the contract is underdelivering structurally, on-site generation is replacing $2.1+/kWh CFE energy, not $1.8 ENEL energy, which materially improves PV economics.
- **Regulatory tier:** the site could host PV far above 0.7 MW (92 GWh load). Above the line: autoconsumo simplified permit + **mandatory SAE/backup** ([[autoconsumo]]). Below it: whether the 0.7 MW exempt ceiling applies **per meter/RPU or per centro de carga** when three meters share one predio is **unconfirmed** — do not assume 3 × 0.7 MW; flagged as part of the open gap.
- **FP:** healthy (97–99.5, earning bonificaciones) — no FP play here.
- Same unknown: ENEL contract committed volumes/take-or-pay to 2032.

---

## Cross-portfolio actions (priority order)

1. **FP correction at Acapulco + Cancún — ~$2.3M/yr sin IVA combined** (≈$2.7M c/IVA), capacitor-bank capex, payback in months. No regulatory dependencies. *(source-confirmed from workbook FP charges)*
2. **Get 12 months of CFE bills (PDF or CFDI XML) for the 6 flagged meters** → `raw/bills/<RPU>/` → run the engine (Workflow 4) for peso-exact baselines and PV/BESS scenarios. The Excel cannot feed the engine and its own `VR` verification sheet is broken (`#REF!`).
3. **Obtain the Tala and ENEL contracts** (committed %, take-or-pay, porteo costs, exit/modification clauses, vencimiento 2032 detail) — they gate the "combine with PV" question commercially.
4. **Close the regulatory gap:** legacy autoabasto porteo + medición neta coexistence on one meter; per-meter vs per-load-center reading of the 0.7 MW line. Needs a primary source (DACG/RLSE read or CFE/CNE consultation).
5. **Site data:** roof/ground areas, transformer capacities (80% hosting rule, [[interconexion-cre]]), 15-min interval data for BESS sizing.
6. **Audit Ixtlahuacán's Abr/May-25 demand spikes** (above contratada) and Proplasa's ENEL collapse.

## Quantified prefeasibility (added 2026-06-10, scripted from the Excel — engine NOT run)

**Method:** deterministic script over the workbook's 2025 monthly blocks; umbral/demand-basis math per [[demanda-facturable]] (FC 0.57); PV valued at the plant's intermedia rate from the workbook's own `Tarifas` sheet (2026 rates on 2025 volumes — stated mismatch), yields from [[solar-yield-lookup]] by municipio; engine financial defaults (EPC 0.75 USD/Wp, FX 17.55, availability 0.75). **Prefeasibility grade, not bankable** — intra-day shape assumed, no bill validation.

### What each site spends (2025, MXN, recibos incl. autoabasto energy + IVA)

| Site | kWh | Recibo | $/kWh ef. | kWh charges | kW charges (cap+dist) | kW share of subtotal |
|---|---|---|---|---|---|---|
| Ixtlahuacán | 22.17 GWh | $60.95M | 2.75 | $37.4M | $17.7M | 34% |
| Acapulco | 8.91 GWh | $32.89M | **3.69** | $14.3M | $12.2M | **43%** |
| Cancún | 4.75 GWh | $18.55M | **3.90** | $9.5M | $5.9M | 37% |
| Proplasa PR1 | 16.29 GWh | $37.33M | 2.29 | $26.8M | $5.5M | 17% |
| Proplasa PR2 | 45.72 GWh | $118.48M | 2.59 | $76.5M | $26.0M | 25% |
| Proplasa TAP | 30.03 GWh | $73.69M | 2.45 | $49.8M | $13.9M | 22% |

Acapulco and Cancún are the **most expensive electricity in the portfolio** — low load factor (~50–56%), heavy demand charges (Acapulco's distribución rate $221/kW is 2.6× Cancún's), plus the chronic FP cargo. Proplasa is cheapest thanks to ENEL energy at ~$1.8–1.9/kWh.

### Lever sizing (gross / net-of-availability where applicable)

1. **FP correction** *(source-confirmed, workbook charges)*: Acapulco $1,716,053 + Cancún $597,756 = **$2.31M/yr sin IVA ($2.68M c/IVA)**. Capacitor-bank capex, months payback.
2. **PV 700 kWp per meter** *(scripted estimate)*: CAPEX ≈ $9.21M MXN/site.
   | Site | Yield (kWh/kWp) | Gen | % of load | Gross $/yr | Net @0.75 | Payback (gross) |
   |---|---|---|---|---|---|---|
   | Ixtlahuacán* | 1,783 | 1.25 GWh | 5.6% | $2.09M | $1.57M | 4.4y |
   | Acapulco | 1,869 | 1.31 GWh | 14.7% | $2.23M | $1.67M | 4.1y |
   | Cancún | 1,500 | 1.05 GWh | 22.1% | $2.18M | $1.64M | 4.2y |
   | Proplasa (each ×3)** | 1,660 | 1.16 GWh | 2.5–7.1% | $2.11M | $1.59M | 4.4y |

   \* Zafra months valued at 0.9× (displacing discounted Tala kWh). \*\* Cuautitlán yield assumed for Valle de México Norte — confirm CP. All six meters together: **~$12.9M/yr gross, ~$55M CAPEX, ~4.3y simple payback** — before the coexistence gap is resolved for IXT/Proplasa.
3. **BESS punta shave** *(bound, not a sizing)*: marginal capacidad value **$4,400–4,800/kW-yr** of punta-coincident shave. Umbral binding dilutes it: **Cancún binds 9/12 months** (basis already capped below measured punta demand → weak BESS site), Acapulco 2/12, Ixtlahuacán 3/12, **Proplasa 0/12** (full value; e.g. 500 kW shave at PR2 ≈ $2.4M/yr gross — needs interval data + engine before quoting). SIN energy arbitrage was net-negative in the [[2026-06-09-456220800389-yearly-savings|Tototlán]] engine run — do not count it here.

### Order-of-magnitude answer to "what could it do"

FP ($2.3M) + 6×700 kWp PV (~$12.9M gross) ≈ **$15.2M/yr gross (~$11.9M net of availability) against $341.9M of flagged-site spend (~4.4%)**, on ~$56M CAPEX — before any BESS, before scaling Proplasa's PV above 0.7 MW per meter (the big prize if the regulatory reading allows it: 92 GWh site, 0-of-12 umbral binding, ENEL supply collapsing).

## Best-case scenario (added 2026-06-10, client directive: permits assumed granted)

**Directives from GEPP/user:** autoconsumo permits are no obstacle; assume **zero contraprestación** for excedentes under autoconsumo (CFE pays nothing for exports); size BESS where it earns; full economics. Consequence of zero contraprestación: **PV is capped at instantaneous self-consumption** — sized so peak AC output stays under the site's average demand (flat 24/7 industrial loads). Cancún stays **< 0.7 MW on [[medicion-neta]]** (smaller load; netting beats no-contraprestación autoconsumo there).

**Method:** same Excel-derived bases as §Quantified prefeasibility; BESS = 20% punta shave, 2h, monthly umbral-capped per [[demanda-facturable]], SIN arbitrage penalty −$835/kWh-yr **calibrated to the Tototlán engine run** ([[2026-06-09-456220800389-yearly-savings]]); BESS cost $11,412/kWh from the same run; economics through the **engine's `finance.py`** (WACC 12%, CFE esc. 6%, availability 0.75, degradation 0.5%/1.25%, 20y). Engine-grade financial model on Excel-grade inputs — prefeasibility, not bankable.

| Site | PV kWp | Gen (% load) | BESS kW/kWh | CAPEX $M | Year-1 net $M | TIR net | Payback | NPV@12% $M |
|---|---|---|---|---|---|---|---|---|
| Ixtlahuacán | 2,530 | 4.51 GWh (20%) | 850/1,700 | 52.7 | 8.54 | 20.4% | 5.5y | 37.6 |
| Acapulco | 1,020 | 1.91 GWh (21%) | 320/640 | 21.0 | 5.55 | **31.7%** | 3.5y | 38.8 |
| Cancún | 700 | 1.05 GWh (22%) | — (umbral binds) | 9.5 | 2.88 | **35.8%** | 3.1y | 21.6 |
| Proplasa PR1 | 1,860 | 3.09 GWh (19%) | 360/720 | 32.7 | 6.43 | 24.3% | 4.6y | 35.5 |
| Proplasa PR2 | 5,220 | 8.67 GWh (19%) | 1,220/2,440 | 96.6 | 18.43 | 23.6% | 4.7y | 98.6 |
| Proplasa TAP | 3,430 | 5.69 GWh (19%) | 790/1,580 | 63.2 | 12.09 | 23.7% | 4.7y | 64.8 |
| **Portfolio** | **14,760** | **24.9 GWh** | **3,540 kW / 7,080 kWh** | **275.6** | **53.92** | **24.2%** | **4.6y** | **296.8** |

Year-0 savings bases: PV $44.74M + BESS $9.87M + FP $2.31M = **$56.93M/yr gross** (≈16.6% of the four sites' $341.9M spend). Gross view: TIR 25.2%, payback 4.4y, NPV $323.0M. FP correction included at Acapulco/Cancún ($250k capex each).

**Reading:** Acapulco and Cancún are the best risk-adjusted projects (FP cargo + highest effective rates). Proplasa is the volume play — $30.9M/yr year-1 net across three meters, and the **2026 ENEL collapse means PV displaces full CFE rates there, not $1.8 ENEL energy** (upside vs this model, which valued at CFE intermedia anyway). Ixtlahuacán is structurally diluted by the Tala discount (zafra kWh valued at 0.9×) and 3/12 umbral-bound months.

**Assumptions that move these numbers:**
- PV valued at intermedia rate (slight overstatement vs weekend/base-hour displacement); avg-demand sizing assumes 24/7 operation incl. weekends — **weekend shutdowns would force smaller PV or create $0-value exports**; needs interval data.
- Zero contraprestación is the floor — any excedente compensation is upside.
- Areas required @0.17 kWp/m²: IXT 14.9k m², ACA 6.0k, CAN 4.1k, **Proplasa 61.8k m² combined** — Proplasa almost certainly needs ground-mount/carport or a size cut to actual roof; unverified.
- Ixtlahuacán assumes PV can freely displace Tala volumes (take-or-pay unknown) and porteo/medición-neta coexistence resolved.
- Arbitrage/BESS-cost calibration is Jalisco-derived, applied portfolio-wide.

## Monthly reconstruction (added 2026-06-11, script preserved)

The best-case computation was rebuilt at **monthly resolution** in `tools/gepp_monthly_savings.py` (the 2026-06-10 scripts were not kept; this one is). Same method — PV at intermedia rate with the municipio's **monthly** irradiation shape from the solar index, BESS umbral-capped per month, FP printed charges — and it **validates against the filed annuals: PV +0.1%, BESS +0.1%, FP +0.2% (peso-exact on FP: ACA $1,716,053 / CAN $597,756), umbral-binding counts reproduce exactly (IXT 3/12 = Abr/May/Dic, ACA 2/12 = Sep/Oct, CAN 9/12, Proplasa 0/12)**. Monthly tables are filed in [[2026-06-11-gepp-recomendacion-sistemas-por-sitio]].

New findings from the monthly split:
- **IXT's 3 umbral-bound months are exactly its anomalous-demand months** (Abr 5,896 / May 7,008 / Dic 5,731 kW — all above the 5,000 kW contratada). If the spikes are a correctable operational fault, the BESS gains those months too — strengthens the audit request.
- **The ENEL withdrawal at Proplasa was staged per meter:** PR2 collapsed first (~90% Ene–May 2025 → ~16% from Sep 2025, ~15% in 2026); PR1 and TAP held ~90–100% until Feb 2026, then collapsed in Mar 2026 (PR1 28%→25%, TAP 15%→13%). By Abr 2026 the whole predio buys ~85% at full CFE rates. Per-meter 2025 ENEL shares (workbook-block residuals): PR1 ~87%, PR2 ~48%, TAP ~79% — weighted ~65%, vs the 69.6% from the ENEL PROPL sheet (different accounting basis, consistent order).

## Sources consulted
- [[2026-06-10-perfil-consumo-gepp-2025-26]] (all figures)
- [[autoconsumo]], [[generador-exento]], [[generacion-distribuida]], [[medicion-neta]], [[scheme-comparison]] (regulatory tiers)
- [[pv-savings-model]], [[bess-savings-model]], [[demanda-facturable]], [[horarios-y-divisiones]] (bill behavior)
- [[2026-06-09-456220800389-yearly-savings]] (FP-correction precedent), [[2026-06-08-cfe-bills-780881200029-fy25-26]] (Peninsular división precedent)

## Confidence
**Medium.** Consumption and FP-charge figures are client-Excel-sourced (consistent and internally plausible, but not validated against CFE bills — the engine has not run). Regulatory tiers are source-confirmed against the 2025 DACG/LSE pages. The two load-bearing unknowns — autoabasto/medición-neta coexistence and the per-meter 0.7 MW reading — are flagged, not resolved. No savings numbers are quoted beyond the FP charges printed in the workbook.
