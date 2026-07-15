# Clients & Deals

**Summary**: The running roster of Newman client/lead deals distilled from the sessions — who, what tariff, what system, what economics, and where the deliverable lives.
**Tags**: #newman #ppa #clients #deals #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

- **KFC / Pizza Hut** (proven full pipeline): per-site — Plaza Bella (GDMTO, 19,120 kWh/mo, 106.14 kWp, 30 kWh BESS, $134,852 yr1), Boulevard (125.28 kWp, $168,977), Centro (GDMTH, 110.2 kWp + 86.4 kWh, $225,085, 27.9%), Pizza Hut Oriente (63.8 kWp, $103,724). Portfolio: 405.4 kWp + 186.4 kWh BESS, 82.2% coverage, yr1 $617,856 MXN, 20-yr $62.2M, ref investment $437,341 USD. Live: newmantech27.github.io/kfc-report. Leads folder id `1LIbd84tYYo5k0DVei5m9XCJ-WDgnXqA2`.
- **AFCH** (Alimentos y Franquicias de Chiapas, RPU 671071116338, GDMTH, División Sureste, Tuxtla CP 29000): password-gated PPA offer + data room + calculadora consolidated into repo NewmanTech27/afch (propuesta pwd `verde-maya-rio-sierra-35`, flujo pwd `nodo-nucleo-forja-flujo-31`); afch.newman.re via Cloudflare. First live CFE Brain optimize_sizing run (--area 626).
- **COVESTRO** Ecatepec (Valle de México Norte, GDMTH): 570,075 kWh/mo (base 33,286/intermedio 347,276/punta 189,513), 1,138 kW, MXN 1,701,443.51; outlier month 101,636 kWh. Used as the verified test deal across finance-review evals (scored 4–7/10 — DSCR undermodeled).
- **FibraHotel**: 6 Solar+BESS sims audited (arithmetic-clean, not sales-ready, 9 P1s); portfolio $4.56M MXN/yr on $43.2M billing across 6 RPUs (061950755457 = 46.7%; 780881200029 = $2.08M/6.9%). Password-gated report newmantech27.github.io/fibrahotel-report (pwd `bess-gdmth-newman-fibra-7320`). Golden fixture RPU = 780881200029 (Grupo Posadas).
- **Universidad Anáhuac Cancún**: BYD/FinDreams BESS RFQ (1.25 MW / 2.5 MWh, 1 cycle/day, CIF Progreso); the Anáhuac PPA PDF format (35–55% savings band) is the reference template for offers.
- **PepsiCo/GEPP**: two solar+BESS PPA excels + executive proposal site (lopezpalacios.github.io/newman-pepsico).
- **Yazaki/ARNECOM**: 48 MWp portfolio (Monday export), 76-RPU harvest sweep (18s pacing), 39 GDMTH bills validated in the recibo parser; the 168-page bulk PDF seed (69 bills).
- **Chiapas leads**: full-depth MiEspacio harvests of RPUs 679220758161, 671071116338, 671140638635, 744931031693 (under `00_Leads`).
- **AFC (KFC–Pizza Hut Chiapas)** proposal (Jul 12, Mario): 4 sites mixed GDMTO/GDMTH, editable live-motor Excel v2 + Newman HTML deck; **PV-only final** (Tuxtla Centro better without battery — BESS gate fired): $2,355,276 gasto → **$617,636 ahorro/yr (26.22%)**, CAPEX $2,058,727, TIR 32–34%/site. Reference workflow for all later proposals ([[2026-07-12-afc-kfc-pizzahut-proposal]]).
- **GEPP** (4 sites incl. Proplasa 3-in-1): deck iterated v1→v8 with the `/solucion-deck` skill; 4% escalators, combined investor TIR held at 14.0%; +0.92 MW growth path (+$1.69M/yr for ~$10.5M, 14.9% incr. IRR); rev4 solar-charge BESS dispatch adds +$954k/yr portfolio ([[2026-07-13-gepp-solucion-deck]], [[2026-07-14-gepp-solar-charge-bess-dispatch]]).
- **Pueblo Bonito / El Chileno desaladora** (Los Cabos, BCS): ~30 MWh/day, 6-year PPA then cede asset; escenario B tarifa ≈ $2.81/kWh at 18% pre-tax vs CFE blended ≈ $3.07; open decision = EPC price chip (only 0.65 USD/Wp viable at 6 yr). Surfaced the SIN-vs-BCS motor bug ([[2026-07-13-pueblo-bonito-desaladora]]).
- **FibraHotel / Grupo Posadas (F/1596), 5-hotel proposal** (Jul 12, Mario): 12 GDMTH bills each — Médano (Cabo, PV-only, $1.08M/40.6% after the BCS DIV/0 fix), Fairfield Vallejo ($1.33M/40.4%), FA Condesa Cancún 780881200029 ($6.95M/23.3%), Fiesta Inn Periférico Sur ($2.24M/63.8%), FA Viaducto ($2.11M/48.4%); consolidated portfolio workbook merged to newman-brain ([[2026-07-12-fibrahotel-proposals]]).
- **El Camarón Dorado** (shrimp producer, 347 kWp PPA target): financial DD **3.31/5 "requiere mitigantes"** — fortress balance sheet but qualified audits, zero ISR (AGAPES exit pending), MXN 39.4M interest-free related-party loans; covenants recommended ([[2026-07-10-camaron-dorado-financial-dd]]).
- **Yazaki** engine runs (verano-2h BESS): media $6.55M/yr (25.5%), grande $10.87M (28.5%), chico UNRELIABLE (checksum 15.77%); portfolio $17.8M/yr on $64.9M, 27.4% — prefeasibility only (per-period kWh/demand registers NULL in Supabase) ([[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]).
- **BESS portfolio master doc** (Jul 09, Mario): 136 projects, **129.9 MWh / 72.3 MW** consolidated from Drive/Monday/CFE Brain/Gmail; Monday sizes for Inzentrum/Covestro/Molex are proposal-template placeholders, not real ([[2026-07-09-bess-portfolio-master-document]]).
- **Others harvested**: FIDEICOMISO F/1596 (968221200700), HOTELES YORI (527051004386), ETG RESORTS (008970211013, $281,439 adeudo / 8 invoices), Grupo Posadas.

## Related Notes
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-05-afch-ppa-offer-dataroom]]
- [[2026-07-03-review-finance-covestro-deal]]
- [[2026-07-02-agent-org-restructure-fibrahotel]]
- [[2026-06-24-byd-bess-rfq-anahuac]]
- [[2026-06-20-pepsico-ppa-proposal]]
- [[2026-07-04-solar-bess-sizing-agent]]
- [[2026-07-10-chiapas-cfe-invoice-harvest]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-11-invoice-review-ui-and-cosecha]]
- [[2026-07-12-afc-kfc-pizzahut-proposal]]
- [[2026-07-13-gepp-solucion-deck]]
- [[2026-07-14-gepp-solar-charge-bess-dispatch]]
- [[2026-07-13-pueblo-bonito-desaladora]]
- [[2026-07-12-fibrahotel-proposals]]
- [[2026-07-10-camaron-dorado-financial-dd]]
- [[2026-07-09-bess-portfolio-master-document]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
