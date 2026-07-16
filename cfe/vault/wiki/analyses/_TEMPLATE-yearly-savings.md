---
title: "Yearly PV+BESS Savings — Service <RPU> (<Site>)"
type: analysis
tags: [analisis, savings, bess, solar, gdmth, <division>, <client>]
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
sources: [<bills-source-slug>]
cliente: <client-slug>
rpu: "<RPU>"
status: vigente
---

# Yearly PV+BESS Savings — Service <RPU> (<Site>)

**Question:** From <N> months of GDMTH bills, what is the annual PV+BESS savings,
which configuration wins, and what is the financial case?

> Produced by the `cfe_savings` engine (`tools/cfe_savings`). Logic per CFE Brain;
> numbers deterministic. System: PV <kWp> kWp · BESS <kWh>/<kW> · availability <f>.

## 1. Baseline — validation
- Annual baseline (sin IVA): **$<baseline>**.
- Bill arithmetic check: <✓ all foot within 0.5% | ⚠ list any failing months — likely CFE errors>.
- Demand basis confirmed: capacidad on kW punta, distribución on max(B,I,P), umbral cap (FC=0.57). See [[demanda-facturable]].

## 2. Headline — combined PV+BESS (gross)

| Mes | kWh Consumo | Generación kWh | kWh BESS desc | Bill ANTES $ | Bill DESPUÉS $ | Ahorro $ | Ahorro % |
|---|---|---|---|---|---|---|---|
| ... paste engine headline_table ... |
| **TOTAL** | | | | | | | |

Net-of-availability total: **$<net> (<pct>%)**.

## 3. Scenarios — which wins

| Escenario | Ahorro $ (gross) | % | Ahorro $ (net) | % |
|---|---|---|---|---|
| PV solo | | | | |
| BESS solo | | | | |
| PV + BESS | | | | |

**Recommendation:** <which config, why; note umbral binding / PV-vs-punta interaction>.

## 4. Financial case

| Metric | Project (unlevered) | SaaS / financier (share <x>%) |
|---|---|---|
| CAPEX | $<capex> | — |
| Ahorro Año-1 (net) | $ | |
| VPN @ WACC | $ | $ |
| TIR | % | % |
| Payback | yr | yr |

## 5. Findings & risks
- <key finding 1>
- <key finding 2 — e.g. PV sizing headroom vs <0.7 MW ceiling, load-shape caveat>

## Sources consulted
- [[<bills-source-slug>]] · [[gdmth-bill-structure]] · [[demanda-facturable]] · [[bess-savings-model]] · [[pv-bess-combined]]

## Confidence
**Baseline: High** (deterministic vs real bills). **Savings: <H/M>** — <note any modeled-not-metered inputs, e.g. PV monthly shape>.
