---
title: "Horarios y Divisiones — Periodos GDMTH por División y Temporada"
type: concept
tags: [cfe, gdmth, periodos-horarios, divisiones, temporadas, punta, intermedio, base]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024]
---

# Horarios y Divisiones — Periodos GDMTH por División y Temporada

> **Purpose:** Authoritative reference for which hours are punta, intermedio, and base — for every tariff division, every season, every day type. Required by the billing calculator to assign kWh consumption and identify Dmax_punta windows.

> **Primary citation:** CFE GDMTH tariff page §5 and §6 (user-facing published schedule). Acuerdo A/158/2024 Annexo Único Table 5 (regulatory source). Where the two conflict, the CFE tariff page is used as the user-billing reference and the conflict is flagged.

---

## Division lookup — which system applies to you?

Every GDMTH user is in exactly one of 17 tariff divisions. All 17 fall into three interconnected systems:

| System | Divisions | Period schedule |
|---|---|---|
| **BC** | Baja California | [[#baja-california]] |
| **BCS** | Baja California Sur | [[#baja-california-sur]] |
| **SIN** | All other 15 divisions | [[#sin-all-other-divisions]] |

**The 15 SIN divisions:** Bajío, Centro Occidente, Centro Oriente, Centro Sur, Golfo Centro, Golfo Norte, Jalisco, Noroeste, Norte, Oriente, Peninsular, Sureste, Valle de México Centro, Valle de México Norte, Valle de México Sur.

Division is determined by municipality. Full municipal mapping in Acuerdo A/158/2024, Annexo Tables 25–42.

---

## Season calendar

| System | Temporada de Verano | Temporada de Invierno |
|---|---|---|
| BC | May 1 → Saturday before last Sunday of October | Last Sunday of October → April 30 |
| BCS | First Sunday of April → Saturday before last Sunday of October | Last Sunday of October → Saturday before first Sunday of April |
| SIN | First Sunday of April → Saturday before last Sunday of October | Last Sunday of October → Saturday before first Sunday of April |

**Key difference:** BC summer starts ~1 month later than BCS/SIN (May 1 vs. first Sunday of April).

> **Citation:** A/158/2024 Annexo Table 4.

---

## Baja California {#baja-california}

> **Citation:** CFE GDMTH tariff page §6, "Región Baja California." A/158/2024 Table 5, Sistema BC.

### Verano: May 1 → Saturday before last Sunday of October

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | — | 0:00–14:00, 18:00–24:00 | **14:00–18:00** (4h) |
| Saturday | — | 0:00–24:00 | — |
| Sunday & holiday | — | 0:00–24:00 | — |

**⚠ Note: BC summer has NO Base period.** All non-punta hours are billed at the intermedio rate.

### Invierno: Last Sunday of October → April 30

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | 0:00–17:00, 22:00–24:00 | 17:00–22:00 | — |
| Saturday | 0:00–18:00, 21:00–24:00 | 18:00–21:00 | — |
| Sunday & holiday | 0:00–24:00 | — | — |

**BC winter has no punta period.** Cargo por Capacidad = umbral only (no Dmax_punta measurement applies).

**BC peak characteristics:** Afternoon peak (14:00–18:00) unlike the evening peak of SIN. Punta only in summer. Solar PV generates partially during the punta window (noon–14:00 is still intermedio in BC summer).

---

## Baja California Sur {#baja-california-sur}

> **Citation:** CFE GDMTH tariff page §6, "Región Baja California Sur." A/158/2024 Table 5, Sistema BCS.

### Verano: First Sunday of April → Saturday before last Sunday of October

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | — | 0:00–12:00, 22:00–24:00 | **12:00–22:00** (10h) |
| **Saturday** | — | 0:00–19:00, 22:00–24:00 | **19:00–22:00** (3h) |
| Sunday & holiday | — | 0:00–24:00 | — |

**⚠ Note: BCS summer has NO Base period.** All non-punta hours are billed at intermedio rate.  
**BCS summer is the most expensive to operate in** — 10 hours/day of punta on weekdays.

### Invierno: Last Sunday of October → Saturday before first Sunday of April

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | 0:00–18:00, 22:00–24:00 | 18:00–22:00 | — |
| Saturday | 0:00–18:00, 21:00–24:00 | 18:00–21:00 | — |
| Sunday & holiday | 0:00–19:00, 21:00–24:00 | 19:00–21:00 | — |

**BCS winter has no punta period.**

---

## SIN — All other 15 divisions {#sin-all-other-divisions}

> **Citation:** CFE GDMTH tariff page §6, "Regiones Central, Noreste, Noroeste, Norte, Peninsular y Sur" (pre-2025 naming; same schedule applies to all 15 SIN GDMTH divisions). A/158/2024 Table 5, Sistema SIN.

### Verano: First Sunday of April → Saturday before last Sunday of October

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | 0:00–6:00 | 6:00–20:00, **22:00–24:00** | **20:00–22:00** (2h) |
| Saturday | 0:00–7:00 | 7:00–24:00 | — |
| Sunday & holiday | 0:00–19:00 | 19:00–24:00 | — |

**⚠ Flag:** The post-punta window 22:00–24:00 is classified as **Intermedio** per the CFE tariff page (base column = 0:00–6:00 only). The A/158/2024 PDF extraction is ambiguous on this point. CFE tariff page used as billing reference.

### Invierno: Last Sunday of October → Saturday before first Sunday of April

| Day type | Base | Intermedio | Punta |
|---|---|---|---|
| **Mon–Fri** | 0:00–6:00 | 6:00–18:00, **22:00–24:00** | **18:00–22:00** (4h) |
| **Saturday** | 0:00–8:00 | 8:00–19:00, **21:00–24:00** | **19:00–21:00** (2h) |
| Sunday & holiday | 0:00–18:00 | 18:00–24:00 | — |

**⚠ Same flag:** 22:00–24:00 (weekdays) and 21:00–24:00 (Saturday) are Intermedio, not Base, per CFE tariff page.

**SIN punta summary:** 2h/day (summer weekdays), 4h/day (winter weekdays), 2h (winter Saturdays only), none on Sundays and holidays.

---

## Summary: weekday punta hours by system and season

| System | Verano (weekday) | Invierno (weekday) |
|---|---|---|
| BC | 14:00–18:00 **(4h)** | None |
| BCS | 12:00–22:00 **(10h)** | None |
| SIN | 20:00–22:00 **(2h)** | 18:00–22:00 **(4h)** |

---

## What counts as a "festivo" (holiday)?

> **Citation:** GDMTH tariff page §5

Official holidays = mandatory rest days per Art. 74 of the Ley Federal del Trabajo (except fraction IX), plus any holidays established by Presidential agreement. These days are treated as "domingo y festivo" for period assignment purposes.

---

## Implications for Dmax_punta measurement

- **Dmax_punta** is measured only during punta hours. A 500 kW demand spike at 3:00 AM (base/intermedio) does NOT affect the capacity charge.
- **Days with no punta** (BC winter, BCS winter, any Sunday/holiday in any system): no contribution to Dmax_punta for those days.
- **BCS summer** has punta on Saturdays (19:00–22:00) — unlike BC and SIN where Saturdays are always punta-free in summer.

---

## Implications for PV generation period classification

Solar PV generates during daylight hours, roughly 7:00–19:00 (seasonal variation). Period classification of solar generation:

| System | Summer solar peak (10:00–16:00) | Notes |
|---|---|---|
| BC | Intermedio (until 14:00), then Punta (14:00–18:00) | PV captures some punta hours |
| BCS | Punta 12:00–22:00 | Nearly all midday solar is punta generation |
| SIN | Intermedio (punta not until 20:00) | Very little solar captures punta hours |

This directly affects [[pv-savings-model]] — punta energy credits are worth more than intermedio credits.

---

## Related pages

- [[gdmth-bill-structure]] — uses these period definitions to allocate kWh by period
- [[demanda-facturable]] — requires knowing when punta hours are to compute Dmax_punta
- [[pv-savings-model]] — which period solar generation falls in determines credit value
