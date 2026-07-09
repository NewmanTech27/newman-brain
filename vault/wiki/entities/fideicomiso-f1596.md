---
title: "Fideicomiso F1596 — Hotel Fiesta Inn Loft Ciudad del Carmen"
type: entity
tags: [cliente, hotel, campeche, gdmth, sin, ciudad-del-carmen]
created: 2026-06-07
updated: 2026-06-07
sources: [2026-06-07-cfe-bill-795150706028-mar26]
---

# Fideicomiso F1596 — Hotel Fiesta Inn Loft Ciudad del Carmen

**Type:** organization (trust / commercial hotel operator)

Hotel property operated under Fideicomiso F1596, identified in CFE records as "Hotel Fiesta Inn Loft." Located in Ciudad del Carmen, Campeche — a coastal city on the Gulf of Mexico, primarily an oil-industry hub (Pemex operations). The property is a Fiesta Inn brand hotel (Grupo Posadas chain).

---

## Key attributes

| Attribute | Value |
|---|---|
| RFC | FFX121005C6A |
| Razón social | FIDEICOMISO F/1596 |
| Address | AV 10 DE JULIO 2, COL. PUNTILLA F |
| CP | 24139 |
| City | Ciudad del Carmen, Campeche |
| CFE No. de Servicio | 795150706028 |
| CFE Cuenta | 82DW05A016960140 |
| CFE Tariff | GDMTH |
| División | SIN |
| Carga conectada | 180 kW |
| Demanda contratada | 180 kW |
| Medidor | CKV430 (multiplicador 80) |

---

## Solar resource

- **CP → Municipality:** 24139 → Carmen, Campeche
- **Annual yield:** 1,702.5 kWh/kWp
- **Source:** [[solar-yield-lookup]]

---

## Consumption profile

Historical demand and energy from the March 2026 bill:

| Season | Typical demand | Typical kWh/month | Notes |
|---|---|---|---|
| Summer 2025 (May–Sep) | 80–106 kW | 38,000–53,000 | Normal hotel operation |
| Post-Oct 2025 | 12–23 kW | 6,000–9,000 | Collapsed — cause unknown |

> The collapse in Oct 2025 is significant. Any PV/BESS sizing should clarify whether the site has returned to normal operation or is permanently reduced.

---

## Relevance to this wiki

Sample GDMTH commercial client used to validate the CP → solar yield lookup workflow and to extract actual March 2026 GDMTH SIN division rates. Illustrates the SIN punta timing problem for PV (punta = 20:00–22:00, after sunset).

---

## What sources say

- [[2026-06-07-cfe-bill-795150706028-mar26]]: March 2026 bill. Demand 12 kW, total 7,162 kWh, bill $23,298. Provides actual SIN GDMTH rates for March 2026.
