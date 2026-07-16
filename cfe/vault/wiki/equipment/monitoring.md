---
title: "Monitoring & Comms"
type: concept
tags: [equipment, monitoring]
created: 2026-06-08
updated: 2026-06-08
sources: []
---

# Monitoring & Comms

Dataloggers / gateways that collect inverter data and push it to each vendor's cloud.
The right one is dictated by the inverter brand: Huawei → SmartLogger, Hoymiles → DTU,
APsystems → ECU. These also matter for **savings verification** — the 15-min telemetry
they log is exactly the metered load-shape data the [[2026-06-08-780881200029-yearly-savings]]
analysis flagged as needed to make a case bankable (vs. a modeled curve).

## Comparison

| Spec | Huawei SmartLogger3000A | Hoymiles DTU-Lite-S | APsystems ECU-R |
|---|---|---|---|
| Pairs with | [[string-inverters]] (SUN2000) | [[microinverters]] HMS/HMT | [[microinverters]] YC/DS |
| Devices managed | up to 80 | up to 99 panels | 30 rec / 100 max |
| Link to inverter | RS485 ×3, MBUS | Sub-1G (≤400 m) | Zigbee 2.4 GHz |
| Uplink | WAN/LAN GbE, 4G, RS485 | Wi-Fi / 4G | Wi-Fi, Ethernet |
| Sampling | real-time | every 15 min | real-time |
| Protocols | Modbus-TCP/RTU, IEC 60870-5-104/103, DL/T645 | S-Miles Cloud | EMA cloud |
| Zero-export | **yes** (smart export control) | — | — |
| Power / consumption | 100–240 V AC, ~8 W | 5 V adapter, ~1 W | 120–240 V, 1.7 W |
| Mounting / IP | DIN/wall, IP20 | plug-in | indoor IP20 (NEMA1) |
| Temp range | −40…+60 °C | −20…+55 °C | −20…+65 °C |

Raw: `raw/pdfs/2025-06-30 - HUAWEI SmartLogger3000A (1).pdf`,
`...portal de acceso HMS DTU-Lite-S_Global.pdf`,
`...Sistema comunicacion APS ECU-R.pdf`.

## Selection notes
- **SmartLogger3000A** is the only one here with **zero-export control** and industrial protocols (IEC 60870 / Modbus) — needed when CFE/interconnection requires export limiting or SCADA integration on a [[string-inverters|SUN2000]] plant. This is the datalogger for Posadas-scale jobs.
- **DTU-Lite-S** logs at 15-min cadence (matches CFE billing intervals) but is residential-scale (99 panels, Wi-Fi) — fine for small Hoymiles micro arrays.
- **ECU-R** is the APsystems gateway; Zigbee to YC600/DS3D micros.

## Related
- [[string-inverters]] / [[microinverters]] — what each gateway talks to
- [[2026-06-08-780881200029-yearly-savings]] — needs metered 15-min data; these loggers provide it
- [[medicion-neta]] — export measurement context
