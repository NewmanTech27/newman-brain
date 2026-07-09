---
title: "PDBT — Pequeña Demanda en Baja Tensión"
type: concept
tags: [cfe, tarifa, pdbt, baja-tension, demanda]
created: 2026-06-08
updated: 2026-06-08
sources: [2026-06-08-pdbt]
---

# PDBT — Pequeña Demanda en Baja Tensión

The CFE tariff for **low-voltage** business services with contracted demand **up to 25 kW**.
It is the entry rung of the commercial tariff ladder, below the medium-voltage tariffs
[[gdmto]] and [[gdmth]]. Applies to any use in baja tensión up to 25 kW, except services
with a specifically fixed tariff.

## The CFE commercial tariff ladder

| Tariff | Voltage | Demand | Pricing |
|---|---|---|---|
| **PDBT** | Baja tensión | **≤ 25 kW** | integrated final rate, no TOU |
| GDBT | Baja tensión | > 25 kW | (gran demanda, BT) |
| [[gdmto]] | Media tensión | < 100 kW | flat (no TOU) |
| [[gdmth]] | Media tensión | ≥ 100 kW | time-of-use (punta/intermedio/base) |

Each boundary is a two-way migration gate: cross it for 3 consecutive measurements and CFE
reclassifies you.

## Billing structure
- **Integrated final rate** by región tarifaria — the published cargo bundles Transmisión, Distribución, Operación del CENACE, Operación del Suministrador Básico, Servicios Conexos no-MEM, Energía y Capacidad into the rate (unlike GDMTH, which itemizes these). Rates set in the CRE *Acuerdos que autorizan o modifican tarifas*.
- **Mínimo mensual**: the amount resulting from the Suministrador de Servicios Básicos operation charge.
- **Demanda por contratar**: set by the user per their power needs; any fraction of a kW counts as a full kW.
- **Depósito de garantía** (by hilos de corriente): 125 kWh (1 hilo) / 350 kWh (2 hilos) / 400 kWh (3 hilos); doubled for bimonthly billing.

## 25 kW migration trigger
> If the user exceeds **25 kW**, they must request migration to **GDBT**. After the **third
> consecutive** measurement above 25 kW, CFE reclassifies them automatically and notifies
> the user.

PV/BESS relevance: a small business near the 25 kW line can use load management / storage to
stay on PDBT, or accept GDBT. PDBT has **no demand charge structure like the umbral** — it is
the simplest commercial tariff.

## Related concepts
- [[gdmto]] — the MT <100 kW sister tariff (next rungs up via GDBT)
- [[gdmth]] — the MT TOU tariff at the top of the ladder
- [[demanda-facturable]] — umbral logic (applies to GDMT*, not PDBT)
- [[medicion-neta]] — net metering still available to small BT generadores exentos

## How sources treat this
- [[2026-06-08-pdbt]]: official CFE PDBT tariff page (web clip). Defines application, mínimo mensual, contracted demand, security deposit. **Missing: actual numeric rate values** (the rate table is a per-month/region lookup not in the clip).

## Open questions
- Current PDBT $/kWh by región tarifaria?
- Is the boundary above PDBT always GDBT, and where does the small-business DAC/▒ residential boundary sit relative to it?
