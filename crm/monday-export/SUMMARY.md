# monday.com Archive — Business Summary

Export date: 2026-07-15. monday.com (newman-re.monday.com) is decommissioned; newman-brain is now the CRM source of truth. 70 boards / 3,138 items archived under `boards/`. This file summarizes what actually matters.

## The pipeline — Deals board 9913323254 (169 deals)

Groups: Top Deals 17 · Active Deals 85 · Stand by 54 · Closed 9 · Lost 4.
Stages: Lead 76, Earlies 29, Stand by 18, Forwards 7, Docs 6, In signing 4, Closed 9, Perdido 2 (Top Deals group unstaged).

**Top Deals (strategic/large accounts):** GEEP (Pepsi), Casa Ley, LaComer, Calimax, Pueblo Bonito, Fibrahotel, Costco, CarOne, Frisa, Grupo Presidente, Soriana, OCESA, Grupo Imagen, Universidad Anáhuac, Tiendas 3B, La Costeña del Valle, Yazaki.

**Closest to won — In signing:** OVQ Qto, El Camarón Dorado, Hilaturas Castilla. **Docs:** El Cerrito. **Forwards:** Calimax, Pueblo Bonito, Car One, Ifood, Armas Mendoza.

**Earlies (~20):** Grupo Aceites del Mayo, OCESA, Aguas de Saltillo, GICSA 2.0, Tecnovidrios, Grupo Imagen, Bemis Packaging, PTAR-CEA Querétaro, Centro Int. de Congresos Yucatán, Casino Solaz Chihuahua, Hospital ABC, Universidad Iberoamericana, Plaza Lilas, and more.

**Lead (~55):** long tail of hotels, universities, industrials, retail — includes Industrial Tototlán (RPU 456220800389, GDMTH) and Grupo Posadas Cancún Hotel (RPU 780881200029).

**Closed/won (9):** GICSA, Calimax 1ra Etapa, Grupo Amkie, Mercury Aircraft, DAISA, Infinity Mérida, Eugenio Sue, Casa Santiago Fernández, Alfa Montes.

**Stand by (54, notable):** Grupo Acerero, Sello Rojo Planta, Casa Ley, Aeropuertos y Auxiliares (ASA), Cryopharma, Estadio Rayados de Monterrey, Traxion, Wolstrat (was In signing). **Lost (4):** Expo Guadalajara, Residencial Lomas, Cabo Dolphins, Terminal Granos Tultepec.

**Key numbers (from the 683-row Subitems of Deals board — kWp / MXN-per-kWh / annual MXN):** Sello Rojo Planta 4,888 kWp @ 1.85 (~8.6M/yr PPA) · Aceites Mayo 4,836 kWp @ 1.82 (~9.3M/yr) · Centro Banamex 3,960 kWp @ 2.24 (~6.9M/yr) · Pueblo Bonito global 3,932 kWp @ 3.27 · "828" 3,002 kWp (~5.45M/yr) · GORM Ampliación 3,001 kWp (~4.96M/yr) · Zaratini 2,681 kWp (~4.9M/yr) · Sunset Quivira 2,630 kWp (~5.1M/yr). Largest BESS: Proplasa PR2 11,340 kWh / 5,670 kW, "031 BESS" 10,000 kWh, Proplasa TAP 7,520 kWh, Ixtlahuacán 6,900 kWh, Posadas Cancún 2,940 kWh / 1,503 kW, Tototlán 1,700 kWh / 850 kW.

Note: on the parent Deals board the kWp / VPN contrato / EPC columns are mirror/formula types and the API returns null — the real numbers live in the subitems export (numeric kWp, MXN kWh, kWh annum, Tipo = PPA/BESS/EPC).

## Deals NPA 18402262283 (6) + subitems (62)

Kuehne & Nagel (Lead), Fibra Shop – La Puerta Victoria (Lead), Hotel Royal Pedregal (Stand by), and **Yazaki México — Portafolio Solar + BESS** (Lead): full preliminary analysis embedded — 55 of 77 sites viable, 48.0 MWp solar + 32.7 MWh BESS, capex ~$1,069M MXN, year-1 savings $214M MXN, 5.0-yr payback, NPV +$121M @12%/10yr; savings mix 57% energy / 38% demand / 4% peak arbitrage; top sites YCC P1 MFG (2.4-yr payback, 43% IRR), Tuxtla DC. The 62 subitems are the Yazaki site list (YCC P1–P3 Chihuahua, Juárez 1–5, Saltillo, Durango, Tuxtla/Tapachula, Obregón, Monterrey, SLP…). Pendientes: exact coordinates, real capex, missing bills, qualified-supply contracts, discount rate.

## CRM Redesign — Migration board 18421500142 (33 items, phases P0–P5, none started)

All statuses unset; Priority column drives it. P0 Audit & Freeze (5: snapshot/backup all boards, resolve canonical Deals board, inventory automations, full GraphQL export — this archive fulfills that item — freeze legacy schema). P1 Canonical Model (7: ER model, Owner/Salesman columns, standardized Stage, de-dupe solar columns, fix Contacts Type, Quotes schema, SSOT naming). P2 Migration & Dedupe (9). P3 Replica Workspace & Access (5, mostly Critical: client-safe mirror boards without internal economics, salesman row-level permissions, per-client guest access). P4 Automations & Sync (4: one-way master→replica sync). P5 Cutover & Governance (3: cutover + archive legacy, governance doc, 30-day review).

## Contacts 9913323235 (15)

Internal Newman roster, not clients: Jonathan Zuniga (Partner, jonathan@newman.re), Carlos Ballman (Partner, c@newman.re), Chandel Chan (Partner), Juan Godinez (Partner), Natan Herrera / Fauro / Santiago (Vendedores), Arturo Perez (Gerente Regional), Adrian Miranda, plus placeholders and untyped Luis Zuñiga, José Luis, Jesús López, Angie.

## Accounts (archived, 9913323267, 52)

Company registry companion to the pipeline: OVQ, Uyeda, Blindajes Epel, Sello Rojo, Casa Ley, DAISA, GICSA, Car One, Cryopharma, Bemis… with board relations to contacts/deals, Region dropdowns, mirrored "Valor Cuenta". Board 18402261990 (archived Deals, 124) is the pre-migration snapshot of the same pipeline (Active 62 / Stand by 49 / Closed 9 / Lost 4).

## Operations & finance boards

- **Gastos de proyectos (69: 44 Pagado / 25 pending):** solar EPC cash ledger. DAISA (inverters $15,700 USD pending, rails, installs, freight), Averanda 739 (largest pending: $4,768,352.76 MXN install 2/2; $53,654 USD panels), Infiniti Mérida (~$234K MXN anticipos paid + $180,923.50 finiquito pending), Mercury Aircraft ($71,195 USD panels pending), El Camarón Dorado / Hilaturas Castilla / Lindavista / Luna Parc / Comercial PET (10% TW panel anticipos paid Nov-2025, 90% balances due 2026-03-18), TAMEX credit 4×$112,262.52 MXN (1 paid). Many payments via "Klar".
- **Reporte Ops (26):** 24-step solar construction checklist for the Hilaturas project (design → izaje/montaje → DC/AC → commissioning → interconexión → UVIE/UIIE); statuses not yet set.
- **NBM (20):** side-venture incubation — Ariia (bank-ready financial analysis), Atlas Motor (yonke/parts marketplace, inventory API En Proceso), The Pizza Society (10 startup tasks).
- **GASTOS JONATHAN_AHM (archived, 1,241):** 2020–2021 credit-card expense ledger splitting charges between "Jonathan" (~878) and "AHM" (~346) — meals, gas, retail, hotels around Culiacán/Guadalajara/Mazatlán.

## Historical archives (pre-Newman era)

- **Proyectos Chedraui (120):** full portfolio of Chedraui store solar sites in 3 "Bloques" — each row a store with POTENCIA (39–482 kW), state, and CFE RPU. High-value dataset.
- **Duplicate of MIRAKL (44 + 23 subitems):** residential & commercial solar install tracker (client, city, CFE tariff GDMTH/DAC/PDBT/1E, kW, install status, interconnection date); includes Chedraui 300–400 kW stores.
- **Duplicate of SALES FORCE (13):** 2023 customer-support ticket queue (warranty claims, early terminations).
- **Mind Map (43 + 131 subitems):** director's strategic brain dump — ~60 VIP contacts (bankers, magistrado, Huawei rep), business ideas (Fibra E, casa de bolsa, JV "N Solar", JV Enermex, fideicomisos, Panamá Pacífico).
- **Subelementos de Minutas Reuniones (28):** 2021 meeting action items for solar installs.
- Remaining archived boards (marketing templates, RSVP, training, stock CRM demo sets in workspaces "other" / "Not workspace") are monday template/demo data, exported faithfully for completeness.
