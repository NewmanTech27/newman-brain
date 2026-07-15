# FibraHotel (Grupo Posadas / F1596) — 5-Hotel PPA Proposals

**Summary**: Parsed 12 real GDMTH bills per RPU for 5 Grupo Posadas hotels, built per-site editable live-motor books plus a consolidated portfolio workbook, fixed a BCS DIV/0 bug, and later fixed the delivered HTML decks' broken mobile rendering.
**Tags**: #newman #fibrahotel #posadas #cfe-brain #bess #proposal #bcs #excel
**Created**: 2026-07-12
**Source**: newman-vps sessions f16242e1, 55270344, beb0ac94, a316b0cf, user mario

---

## Content
- Client: **FibraHotel / FIDEICOMISO F/1596** (Grupo Posadas), Drive folder `1km8W9V-64woB89QiomZPGaSvM3JZ-eFd`. 12 bills per RPU. Workflow = the AFC/GEPP process (asked how to name/invoke it — it's the `/solucion-deck` + book pipeline).
- **5 hotels** (12 GDMTH months each, footed to the peso; roof + location built in):
  | Hotel (RPU) | City/div | PV | BESS | Ahorro híbrido |
  |---|---|---|---|---|
  | Médano `008111000167` | Cabo/BCS | 291 kWp | — | (see fix below) |
  | Fairfield Vallejo `573170411137` | CDMX/SIN | 97 kWp | 186 kW | $1.33M/yr (40.4%) |
  | FA Condesa Cancún `780881200029` | Cancún/SIN | 194 kWp | 1,503 kW | $6.95M/yr (23.3%) |
  | Fiesta Inn Periférico Sur `968221200700` | CDMX/SIN | 349 kWp | 207 kW | $2.24M/yr (63.8%) |
  | FA Viaducto Aeropuerto `986190901451` | CDMX/SIN | 234 kWp | 254 kW | $2.11M/yr (48.4%) |
- Location → division (BCS vs SIN → correct punta schedule + yield by CP); Google Solar-API roof area → hard cap on PV NPV sweep. Engine golden 18/18, book reconciliation 5/5.
- **Notable**: Médano `008111000167` is Baja-Tensión-metered (hidden "2% Baja Tensión" line, now footed); BCS 10-hour punta window makes BESS uneconomic there.
- **BCS DIV/0 bug fixed** (55270344): only Médano's book had errors — 249 broken cells. Root cause: monthly punta capacity charge `= Capacidad$ / MIN(kW_punta, kW_umbral)`; BCS GDMTH has no punta demand Oct–Mar → kW_punta=0 → `#DIV/0!` cascading to `#VALUE!` on IRR. Fix: `IFERROR(…,0)` on all 5 books' month rows. **Fixing it changed Médano's real numbers: ahorro now $1.08M/yr (40.6%), not the inflated $1.29M/48.5%.**
- Consolidated workbook `FibraHotel - Portafolio (Resumen + 5 sitios).xlsx` (Resumen row per hotel + portfolio total + KPI band + 5 per-project sheets). Later remade AFC-V2-style (live formulas, separate tariff/BESS/PV breakdown) and merged to `NewmanTech27/newman-brain` master (`53be543`), uploaded to mario@newman.re Drive `01_recibos`.
- **Mobile-render fix** (a316b0cf): decks showed blank on phones because all numbers/charts/photos are injected by JS at load — raw HTML has only headings; phone viewers (Files, WhatsApp, Gmail, Drive preview) don't run scripts. Fix = `work/prerender.py`, loads each deck in headless Chrome, lets scripts run, saves fully-rendered page back to disk (baked SVG charts, tables, base64 photos). Verified with JS off. This root cause affects **every deck the skill produces**.

## Related Notes
- [[2026-07-12-afc-kfc-pizzahut-proposal]]
- [[2026-07-09-bess-portfolio-master-document]]
- [[fibrahotel-analysis-project]]
- [[2026-07-13-pueblo-bonito-desaladora]]
