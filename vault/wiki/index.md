# Wiki Index

*Master catalog of all pages. Updated after every ingest. Read this first when answering queries.*

---

## Billing — How CFE Charges GDMTH and GDMTO

- [[gdmth-bill-structure]] — complete bill anatomy: every component, formula, and bill reconstruction walkthrough
- [[demanda-facturable]] — the umbral cap logic for capacidad and distribución demand charges (FC=0.57)
- [[horarios-y-divisiones]] — authoritative period schedule (punta/intermedio/base) by division and season; includes the 22:00-24:00 flag
- [[rate-inputs]] — time-varying $/kWh and $/kW-mes values; update monthly from CFE

## Tariff Profiles
- [[gdmto]] — GDMTO tariff: media tensión <100 kW, flat rate, same umbral formula as GDMTH (FC=0.55)
- [[pdbt]] — PDBT tariff: baja tensión ≤25 kW, integrated flat rate; bottom rung of the commercial ladder (PDBT→GDBT→GDMTO→GDMTH)

## Geographic Data — Address to Solar Yield

- [[solar-yield-lookup]] — workflow: CP from CFE bill → municipality → kWh/kWp yield (the geographic layer for PV sizing)

## Optimization — PV, BESS, and Compensation Schemes

- [[pv-savings-model]] — how solar reduces energy charges and the umbral effect on demand
- [[bess-savings-model]] — how a battery reduces Dmax_punta; when BESS saves and when it doesn't
- [[pv-bess-combined]] — the umbral interaction: why combined savings ≠ PV savings + BESS savings
- [[medicion-neta]] — net metering rules, period credit priority matrix, 12-month expiry rule
- [[autoconsumo]] — the formal 2025 Autoconsumo figure (≥0.7 MW): three permit tiers, CFE-only excedentes, mandatory storage backup, obligations & roadmap

## Eligibility — Can We Do X?

- [[scheme-comparison]] — decision tree: medición neta vs. autoconsumo; eligibility conditions table

## Equipment Catalog — BOM Component Library

- [[equipment/index|Equipment Catalog]] — landing page; how sizing maps to hardware classes
- [[pv-modules]] — PV panels: Trina 710/720, Seraphim HJT 720, Tongwei 720 (210mm bifacial, ~720 Wp)
- [[string-inverters]] — Huawei SUN2000 family, 20–150 kW grid-tie
- [[microinverters]] — APsystems YC600/DS3D, Hoymiles HMS-2000 (module-level)
- [[hybrid-inverters]] — Sigen Hybrid 50–125 kW (PV + battery DC-coupled)
- [[bess]] — BYD MC Cube-T, Huawei LUNA2000-215, SigenStack (LFP storage)
- [[monitoring]] — SmartLogger3000A, DTU-Lite-S, ECU-R (dataloggers/gateways)
- [[protection-bos]] — ABB T5N/XT3N breakers, Suntree SL7 DC breaker, Kibor FV cable

## Technical Standards — Installation Requirements

- [[instalacion-pv-interconectada]] — NOM-001-SEDE-2012 Art. 690 + 705: PV installation and grid-tie rules; 120% bus rule, anti-islanding, conductor sizing
- [[instalacion-bess]] — NOM-001-SEDE-2012 Art. 480 + 690-H: stationary battery installation; ventilation, disconnect, conduit, Li-ion/lead-acid requirements
- [[interconexion-cre]] — administrative interconnection procedure for DG <0.5 MW (solicitud→estudio→contrato→inspección→sync); BT/MT1/MT2 classes, 80% hosting rule
- [[pv-degradation]] — gradual PLR + failure modes (TOPCon/HJT); the derate behind 20-yr generation
- [[solar-resource-data]] — irradiance data quality/uncertainty; prefeasibility lookup vs bankable measured data

## Regulatory Background — Entities and Source Documents

### Sources
- [[2026-06-04-gdmth]] — official CFE GDMTH tariff page (web clip)
- [[2026-06-04-acuerdo-a158-2024]] — Acuerdo A/158/2024: CRE's authoritative tariff methodology for 2025; FC=0.57, period schedules, demand formulas
- [[2026-06-04-dacg-sae-a113-2024]] — CRE regulation A/113/2024 for SAE energy storage; SAE-CC rules
- [[2026-06-04-res142-2017-gen-dist]] — CRE resolution RES/142/2017 for distributed generation ≤0.5 MW; net metering rules
- [[2026-06-04-ley-sector-electrico-2025]] — landmark March 2025 decree; new legal ceiling over all prior regulations
- [[2026-06-09-autoconsumo-cne-2025]] — the 2025 Autoconsumo regulatory package: CNE DACG (12-XII-2025) + RLSE/requisitos/formato; the ≥0.7 MW figure, CFE-only excedentes, mandatory storage backup
- [[2026-06-09-dacg-nota-juridico-comercial]] — user's jurídico-comercial synthesis of the autoconsumo regime; three tiers, obligations, project roadmap (the ingest anchor)
- [[2026-06-05-nom-001-sede-2012]] — NOM-001-SEDE-2012: Mexico's national electrical installations code (Art. 690, 480, 705 relevant to PV/BESS)
- [[2026-06-05-nom-001-semarnat-2021]] — NOM-001-SEMARNAT-2021: SEMARNAT environmental standard; image-based PDF, content pending
- [[2026-06-07-gdmto]] — official CFE GDMTO tariff page (web clip); media tensión <100 kW, flat rate
- [[2026-06-07-codigo-postal]] — SEPOMEX national CP catalog (157k rows); maps CP → municipio + estado
- [[2026-06-07-solar-index-geografico]] — PV yield by municipality (2,369 rows); 1,355–1,912 kWh/kWp annual range
- [[2026-06-08-pdse-2025-2039]] — SENER Plan de Desarrollo 2025-2039; DG ceiling now < 0.7 MW (art. 25 Ley); 2024 GD = 4,449.79 MW
- [[2026-06-08-manual-interconexion-500kw]] — SENER Manual de Interconexión <0.5 MW (DOF 2016); the DG connection procedure, classes & hosting limits
- [[2026-06-08-cfe-transformer-norms]] — CFE K0000-07 (pad-mount 300/500 kVA) + NMX-J-351-3-ANCE-2016 (dry-type short-circuit); the MV transformer layer
- [[2026-06-08-nom-009-stps-2011]] — STPS work-at-height safety (>1.80 m); rooftop PV install labor requirements
- [[2026-06-08-pdbt]] — official CFE PDBT tariff page (web clip); baja tensión ≤25 kW
- [[2026-06-08-ci-pv-install-best-practices]] — NREL C&I PV install best-practices (2015); bankability/quality protocol
- [[2026-06-08-solar-resource-data-handbook]] — IEA-PVPS T16-6:2024 solar resource data handbook (516 pp); irradiance/yield/uncertainty
- [[2026-06-08-iea-pvps-t13-degradation]] — IEA-PVPS T13-30:2025 PV failure fact sheets + new-tech (TOPCon/HJT) degradation
- [[2026-06-08-iea-pvps-t13-32-climate]] — IEA-PVPS T13-32:2025 climate optimisation; hot-humid (Cancún) module selection & PLR
- [[2026-06-08-iea-pvps-t17-pv-ev-charging]] — IEA-PVPS T17-04:2025 PV-powered EV charging stations (adjacent opportunity)

### CFE Bill Sources
- [[2026-06-07-cfe-bill-795150706028-mar26]] — Hotel Fiesta Inn Loft, Ciudad del Carmen, March 2026; GDMTH SIN; provides real rate data
- [[2026-06-08-cfe-bills-780881200029-fy25-26]] — Grupo Posadas Cancún, 12 months Abr25–Mar26; GDMTH SIN; ~10.4 GWh/yr; clean savings dataset
- [[2026-06-09-cfe-bills-456220800389-fy25-26]] — Industrial Tototlán Jalisco, 12 months May25–Abr26; GDMTH SIN; CFDI XML format; ~5.58 GWh/yr; chronic FP penalty
- [[2026-06-08-calculadora-bess-pv-excel]] — client's manual PV+BESS Excel model for 780881200029 (comparison target)
- [[2026-06-10-perfil-consumo-gepp-2025-26]] — GEPP portfolio workbook: 2025 + Ene–Abr 2026 monthly profiles for ~30 services (411.7 GWh, $1,205M); the four-site problemática (Ixtlahuacán, Acapulco, Cancún, Proplasa)

### Entities
- [[grupo-posadas]] — hotel operator; CFE client behind services 780881200029 (Cancún) and 795150706028 (Cd. del Carmen)
- [[fideicomiso-f1596]] — Hotel Fiesta Inn Loft, Ciudad del Carmen, Campeche; GDMTH client; 180 kW contracted
- [[cfe]] — Comisión Federal de Electricidad; national utility
- [[cfe-ssb]] — CFE Suministrador de Servicios Básicos; the entity that bills GDMTH users
- [[cenace]] — grid operator; its operation cost is a billing component
- [[cne]] — 2025 energy regulator (órgano desconcentrado of SENER); grants generation/storage permits + issues the autoconsumo DACGs
- [[cre]] — LIE-2014-era regulator; issued A/158/2024 + legacy DACGs; permit authority superseded by CNE in 2025
- [[sener]] — Secretaría de Energía; issues NOM-001-SEDE, the interconnection manual, the PDSE; CNE is sectorized under it
- [[gepp]] — PepsiCo bottler México; multi-service GDMTH portfolio client (411.7 GWh/yr); four-site 2026 brief
- [[tala-energy]] — bagasse cogenerator (Tala, Jalisco); legacy autoabasto supplier to GEPP Ixtlahuacán (zafra-seasonal, vence 2032)
- [[enel-mexico]] — legacy autoabasto supplier to GEPP Proplasa (~70% of 92 GWh in 2025; share collapsed 2026)

### Supporting Concepts
- [[gdmth]] — tariff overview and application criteria
- [[sae-cc]] — SAE-CC regulatory treatment under A/113/2024
- [[sae-modalidades]] — all 4 SAE modalities
- [[generacion-distribuida]] — DG < 0.7 MW framework overview (ceiling raised from 0.5 MW in 2025)
- [[generador-exento]] — permit-free legal status for DG <0.7 MW; the tier below the autoconsumo permit line
- [[perfiles-de-carga]] — industry 7-day load-curve library + horario overlay: modeled %B/%I/%P vs bill splits (fit/MAE), curve x solar overlap -> derived % autoconsumo; assumptions, superseded by 15-min data
- [[interconexion-cre]] — DG interconnection procedure (also listed under Standards)
- [[pv-degradation]] — degradation/failure modes; derate factor for savings model
- [[solar-resource-data]] — solar resource data quality; yield bankability

## Analyses
- [[reset-vs-merge-hazard]] — **finding (2026-07-10 drain):** GATE 0 reconciliation must be a preserve-both MERGE, never a reset; fork dev +102 / main +55 over `d28ae6b`; a reset orphans an entire product (CRM or collector + `docs/cfe-collection.md`); executor = `supabase-devops` with Supabase write tools + skip-permissions; precondition for safety
- [[design-engine-live-or-orphan]] — **finding (2026-07-10 drain):** `design-engine/sizing.py` is live-capable but dormant behind 3 gates (worker off, allowlist empty, 0 live data); prod `/opt` still runs the OLD divergent file; **latent DEL-5 P0** — one re-arm from pricing deals on 3 invariant violations
- [[the-58-designs]] — **finding (2026-07-10 drain):** 58 rows in prod `client.design` = stored PV/BESS sizings from the divergent engine; flawed (overstate) AND unreproducible (`invoice`/`bulk_bill` = 0); latent landmine on allowlist entry; quarantine recommended, not executed (prod write = Jesus)
- [[tonight-sizing-fix]] — **decision (2026-07-10 drain):** sizing.py rewired to delegate to the golden engine, divergent physics removed, on `spec/cfe-ppa-bess @ 4a2f319` (local-only); golden 18/18 + sizing 3/3 + integ 14/14 re-run; NOT 95 (gap = step 3, upstream-blocked); changed no prod
- [[single-disk-risks]] — **finding (2026-07-10 drain):** inventory of what exists only on this box — `/home/mario` ~155MB PDFs+entregables (incl. the golden fixture), unversioned `~/newman-sso` 92K / `~/excalidraw-auth` 36K, local-only branches (`spec/cfe-ppa-bess@4a2f319`, `spec/tuesday-inputs@5f6f804`, `integration/gate0@38ebff0` +57), 84MB transcripts
- [[2026-07-10-extraction-golden-proof-scope]] — golden test PASSED (18/18, exit 0) on RPU 780881200029: exact scope of what the proof covers (vault `cfe_savings` extract→arithmetic, 1 RPU/GDMTH/SIN) vs what it does NOT (other formats, failure paths, the whole live production pipeline, the divergent `design-engine`, dashboard/deploy)
- [[2026-07-09-sizing-py-golden-ingest-materiality]] — clean-room `sizing.py` can't reproduce golden RPU 780881200029: fixture unreachable from vault + structurally lossy (capacidad/distribución, seasonal shave, weekday arbitrage); net direction = **overstate/oversell**
- [[2026-07-09-cfe-ppa-bess-cleanroom-divergences]] — clean-room `design-engine/sizing.py` dropped the umbral + inverted the PV→BESS coupling + isn't golden-tested (P0); deal-offer floor decided IRR-only (engine has no DSCR). Feeds `docs/specs/cfe-ppa-bess.md`
- [[2026-07-10-engine-wrap-decision]] — **decision (newman-rebuild, lead-engine):** vendor `newman-brain`'s `engine.js` pinned to a commit SHA + CI-checksummed, not a live cross-project call to the old prod edge function — kills drift by making any edit/re-pin a loud CI failure instead of a silent copy; reconcile the FIXED golden system (194.48 kWp/2940 kWh), never the NPV sweep; names the dependency chain (#9 golden-CI, recibo horaria-split upstream of #5, P1 schema) that gates any merge
- [[2026-06-08-780881200029-yearly-savings]] — Grupo Posadas Cancún PV+BESS yearly savings; baseline validated peso-exact; combined $7.59M/yr gross (25.2%), BESS = dominant lever
- [[2026-06-09-456220800389-yearly-savings]] — Industrial Tototlán Jalisco PV+BESS; CFDI XML bills; combined $4.31M/yr gross (27.6%), TIR 22.5% / payback 5.0y; with FP correction $5.18M/yr (33.2%), TIR 27.8% / payback 4.0y; PV = dominant lever
- [[2026-06-09-456220800389-propuesta]] — client-facing Spanish proposal for 456220800389: PV 700 kWp + BESS 1,700 kWh/850 kW + FP correction; $5.18M/yr (33.2%), TIR 27.8%, payback 4.0y
- [[2026-06-09-456220800389-autoconsumo]] — would autoconsumo/autoabastecimiento or PV >0.7 MW beat medición neta for 456220800389? Scheme switch neutral; demand-netting floored; scaling PV adds energy-only savings capped by self-consumption
- [[2026-06-10-second-brain-use-cases]] — strategy brainstorm: 20 use cases across deal lifecycle (proposal factory, bill audits, FP product, M&V, benchmarks) + build priorities (15-min HM data first)
- [[2026-06-10-gepp-portfolio-project-check]] — GEPP four-site project check + quantified prefeasibility + best-case scenario (permits assumed, zero contraprestación): 14.8 MWp PV + 3.5 MW BESS + FP, $275.6M CAPEX, $53.9M/yr year-1 net, TIR 24.2%, payback 4.6y, NPV $297M
- [[2026-06-11-gepp-recomendacion-sistemas-por-sitio]] — *(superado por [[2026-06-14-gepp-solucion-energetica-por-proyecto]])* client-facing report: recommended system per GEPP site (simplified model, gross $56.9M)
- [[2026-06-14-gepp-solucion-energetica-por-proyecto]] — **vigente** GEPP solución por proyecto con MOTOR (no simplificado): ahorro bruto $63.2M/año (engine capta reducción demanda vía umbral), gasto CFE $341.9M (=Excel cliente), 2025+2026 run-rate (colapso ENEL confirmado), ambas estructuras (Compra TIR 28-44% $57.5M/año vs PPA $17.3M@18%/$25.9M@14%), 20 años, abasto-aislado descartado, Cancún exento <0.7MW; entregables Excel trazable (1,520 fórmulas, 0 err) + propuesta es-MX docx/pdf
- [[2026-06-15-gepp-v3-audit-rebuild]] — **vigente** auditoría del Excel v2 (bug del split CFE/Tala de Ixtlahuacán: $25.7M→$28.4M correcto; $55.2M = Tarifa Actual full-CFE nativa del workbook) + reconstrucción v3: Supuestos en vivo por proyecto (PPA $/kWh, plazo, costo PV/BESS, comisión → propagan a todo), PPA 15a + transferencia PV al cliente, capacitores al financiador, columna Tarifa Actual con escalón 2032, decomposición ENEL/Tala, Comparativo+Proyección conectados; 3,882 fórmulas, 0 err, motor replicado al peso
- [[2026-06-11-780881200029-calculadora-audit]] — formula-level audit of the client Excel: +1.2% gap = untranscribed FP bonificación (peso-exact); arbitrage overstated 35% (365-day cycling, no punta-energy cap); O&M escalation bug; corrected gross $7.08M (23.5%) vs $7.59M claimed; **engine shares the arbitrage flaw — fix pending** ([[overview]] gap 7); modular rebuild `780881200029 - Calculadora v2.xlsx`
- [[2026-06-11-calculadora-generica-pv-bess]] — generic client-agnostic PV/BESS/Híbrido calculator (`entregables/calculadoras/Calculadora Ahorros PV-BESS (generica).xlsx`): 3 scenarios, profile-driven assumptions, automatic regulatory caps at the 0.7 MW line (medición neta → autoconsumo), REGIMEN rules/alerts sheet, full finance doctrine; golden-validated to the centavo; webapp-ready module architecture
- [[2026-06-11-automatizacion-calculadora]] — automation layer: shared `calc_core.py` (golden to the centavo from raw PDFs), `fill_calculadora.py` CLI (bills folder → filled per-client Excel), local webapp (`tools/webapp/`, drag-and-drop PDFs/XMLs → scenarios live), CP→municipio→monthly-yield chain; flags BC punta-month divergence engine vs wiki (resolved 2026-06-11: engine fixed to may–oct)
- [[2026-07-07-gepp-bess-verano-resizing]] — **vigente** BESS rev2 ya es 0.5C/2h (la premisa “dimensionado a invierno 4h” se invierte): sobrados reales ACA −27% / CAN −24%; escenarios A/B/C → recomendado B verano-2h (33.7 MWh; VAN inversionista −$3.0M→+$3.9M; cliente cede ~4%); correcciones in-place: esc CFE 6%→5% stale en los 4 libros Proplasa, C53 (particip. req. 16%) recalculadas en 7 sheets, cap físico Q≤t_cap×D en Preforma 1 (−$0.62M/año; kWh-punta vs D-punta inconsistentes → pedir recibos por medidor); libros rev3 con columna Q fórmula viva trazable + Comparativo autónomo de flujos vivos
- [[2026-07-07-gepp-2026-terms-repricing]] — **vigente** auditoría de lo curado (bruto $62.8M correcto/+3%, base corregida $341.9M→$311.4M) + re-precio a términos 2026: áreas reales (Proplasa 15,396 m² sólo aloja 2,617 kWp → PV grande sólo con terreno), EPC 0.65, BESS 0.5C/2h+haircut 2m, mezcla por-sitio; value-stack neto techo-PV+FP $33.4M → +BESS $50.5M → +PV terreno $59.5M = $143.5M; deal PPA @14% $1.13–1.40 + comisión BESS 50/50 (TIR fin 10–14%); libros verificados + parche additivo make_project_book
- [[2026-07-02-gepp-max-savings-web]] — **vigente** GEPP config max-ahorro por sitio sobre 2025 año-completo: PV 5.04 MWp (839.41 exento ×6) + BESS 18.7 MW/37.4 MWh (**2h óptimo los seis sitios** — resuelve el pendiente de horas), $85.9M/año (27.6%) + FP $2.31M, CAPEX $250M, NPV $414M; deal PPA $1.80 fijo + comisión BESS resuelta (62–73% @18% fin.; Cancún PPA-solve $2.82), cliente $23.3M→$31.1M/año @18→14%; entregable webpage por-sitio (`GEPP - Solucion Energetica Web.html`)
- [[2026-06-11-ai-operating-system]] — the OS build: PPA pricer (solve $/kWh for target financier IRR; Tototlán 18% → $2.29/kWh), proposal factory (bills → `Propuesta - <RPU>.md`), GDMTO/PDBT flat-tariff model, webapp v2 (deal solver + proposal download + flat tab), 4 new subagents, `OS - Centro de Mando.md` front door, BC punta fix; all golden-validated al centavo

## Tools
- `tools/cfe_savings/` — deterministic GDMTH PV+BESS savings engine (PDF **and CFDI-XML** bills → headline table + financials). **v2 (2026-06-11):** arbitrage limited to punta weekdays + capped at the bill's punta kWh, FP-bonificación claw-back — reproduces the corrected reference (`780881200029 - Calculadora v2.xlsx`) to the centavo; golden re-baselined (Ahorro $7,083,252 / 23.5%, 18 checks). Optional opt-in `--fp-correction` (factor-de-potencia penalty). Run via the `cfe-savings-analyst` subagent.
- `tools/import_perfil_xlsx.py` — **workbook importer (2026-06-14):** reinterpreta un Excel "Perfil de Consumo" tipo GEPP al esquema de recibo del OS (`cfe_savings.extract`). Reconstruye los componentes MEM desagregados (Generación B/I/P, Capacidad, Distribución, Suministro) como `cantidad × tarifa` desde la hoja `Tarifas`, aplicando la lógica de demanda del wiki (umbral FC=0.57, [[demanda-facturable]]); valida cada mes contra el total impreso del cliente (Cancún +0.12% = recibo CFE fiel; sitios con autoabasto divergen = descuento Tala/ENEL, reconstrucción = carga total a tarifas CFE). Escribe `imported/<slug>/{bills.json,inputs.json,meta.json}`. `extract_folder` lee `bills.json` si existe → calc_core/portfolio/webapp modelan sin cambios. Dataset GEPP: 6 servicios (CAN, ACA, IXT, PR1, PR2, TAP).
- `imported/` — **registros de recibo derivados (2026-06-14):** reconstrucciones machine-readable desde workbooks de cliente (no es `raw/`, regenerable); un folder por servicio con `bills.json` (esquema extract) + `inputs.json` (scaffold) + `meta.json` (QA vs total impreso). Ver `imported/README.md`. Cobertura GEPP: 2026 Ene–Abr (4 meses → flag de estacionalidad).
- `tools/portfolio.py` — **portfolio batch runner (2026-06-12):** todo `raw/bills/*` en una pasada (validación footing por recibo, 3 escenarios calc_core, agregado + ranking de palancas); RPUs que no cuadran quedan excluidos y marcados. CLI + `GET /api/portfolio` + vista `/portafolio` de la webapp. Config por RPU en `tools/portfolio_overrides.json` (raw/ es inmutable).
- `tools/make_executive_report.py` — reporte ejecutivo standalone (`entregables/reportes/Reporte Ejecutivo - CFE Brain OS.html`): cartera en vivo del motor + caso GEPP archivado + doctrina; autocontenido, regenerable con un comando.
- `tools/ppa_pricer.py` — PPA deal pricer: bisects the PPA $/kWh (or BESS savings-share) to a target financier IRR over calc_core's exact financier cashflow (validated 1e-9); term/escalation sensitivity + client-viability gate. Subagent: `ppa-deal-pricer` (Workflow 7).
- `tools/make_proposal.py` — proposal factory: `raw/bills/<RPU>/` → validated Spanish client proposal `entregables/propuestas/Propuesta - <RPU>.md` (FP as separate lever, fact tiers, optional PPA section). Subagent: `proposal-writer`.
- `tools/optimize_sizing.py` — **PV+BESS sizing por máximo NPV cliente (2026-06-19):** barre kWp×BESS por `calc_core`, escoge el óptimo de NPV del cliente (`vpn_proyecto`), **NO topa a 0.7 MW** (el techo real es el autoconsumo solar, no el % de offset). Reporta óptimo + mejor-exento (≤699) vs mejor-autoconsumo (≥700) + curva tamaño-vs-NPV, haciendo explícita la decisión de régimen. `resolve_yield` lee esquema flat/nested/CP/municipio. Sizing por defecto de make_project_book/ppa_pricer/make_proposal (reemplaza el viejo cap `min(...,699)`). Límite del modelo: el motor carga el BESS de red-base, no del excedente PV.
- `tools/make_project_book.py` — **DEFAULT calculadora (2026-06-18):** GEPP-style **"Solución Energética"** Excel book for any project (recibo folder / CFDI XML / imported workbook). 1 proyecto → `<RPU> - Solucion Energetica.xlsx`; varios servicios de un cliente → libro de grupo (hojas por proyecto + Comparativo Comercial + Proyección 20 años). **Híbrido:** motor mensual = valores del engine (golden, reconcilia al peso); Supuestos/CAPEX/proyección/IRR/NPV/roll-ups = fórmulas vivas. Reemplaza a `fill_calculadora.py` por defecto. Skill `/project-book`; verificador `tools/test_project_book.py` (lib `formulas`).
- `tools/gepp_bess_scenarios.py` — **modelo paramétrico de dimensionado BESS (2026-07-07):** réplica exacta del motor mensual de los libros GEPP (verificada 0.000% en R72/TIR), forma cerrada del rasurado plano Q = t_cap×MIN(D_punta, E_útil/horas_bloque, P); escenarios actual / verano-2h / eficiente-WACC con TIR/VAN inversionista y cliente; corre directo contra el libro 4-Sitios rev2. Ver [[bess-savings-model]] §Step 6 y [[2026-07-07-gepp-bess-verano-resizing]]
- `tools/gepp_max_savings_sweep.py` — **GEPP sweep integral (2026-07-02):** los 6 `imported/gepp-*` → yields por municipio+estado, PV sweep (exento 839.41), barrido BESS 0–5h a pico de punta, FP ACA/CAN, deal `ppa_pricer` (PPA fijo $1.80 → comisión resuelta @18%/14%, fallback PPA-solve en sitios PV-dominantes) → `entregables/reportes/gepp_max_savings_data.json`.
- `tools/make_gepp_web_report.py` + `tools/gepp_web_report_body.html` — **webpage GEPP (2026-07-02):** JSON del sweep → `entregables/reportes/GEPP - Solucion Energetica Web.html` (autocontenida, estilo casa dark+esmeralda, overview + tab por sitio, curvas de dimensionado interactivas, deal, alertas del motor con corrección de etiqueta exento AC↔DC, caveats).
- `tools/tarifa_flat.py` — GDMTO (FC=0.55 umbral) / PDBT (energy-only) flat-tariff model; manual bill rows until a real bill enables a parser; BESS shave only if explicitly supplied. Prefeasibility grade.
- `tools/webapp/` — **v3 (2026-06-12):** the OS interface: `/` = visual command center (live vault stats, capability map, activity feed, ahorro-identificado stat, one-click golden test) · `/portafolio` = vista portafolio (agregado multi-RPU, palancas, gráfica mensual, alertas por servicio) · `/cotizador` = GDMTH drag-and-drop + GDMTO/PDBT manual tab + live PPA solver + proposal download · `/chat` = webchat sobre el vault (`claude -p` con cwd=vault, herramientas read-only + Bash(python); cita [[páginas]], no modifica archivos); same calc_core as Excel/CLI. Launcher 1-click: `CFE Brain OS.bat` (raíz).
- `OS - Centro de Mando.md` (vault root) — the front door: capability map (need → command → output), non-negotiable rules, honest limits.
- `Home.md` (vault root) — Spanish **visual dashboard**: live Bases embeds (análisis, fuentes, clientes, equipos), quick nav, workflow cheat-sheet.
- `wiki/*.base` — Bases views feeding Home: `analyses.base` / `sources.base` / `entities.base` (vista Clientes) / `equipment.base`.
- `.claude/commands/` — slash commands: `/daily` (brief de sesión), `/capture` (nota rápida → `raw/notes/`), `/lint`, `/refresh-dashboard`.
- `entregables/` — **todas las salidas para humanos** (2026-06-12): `propuestas/` (Propuesta - <RPU>.md), `calculadoras/` (Calculadora - <RPU>.xlsx + plantilla genérica + v2 Posadas), `reportes/` (reporte ejecutivo + reportes GEPP). La raíz del vault queda limpia; ver `entregables/README.md`.
- `tools/intake/` — **client-intake layer (2026-06-16):** front of the funnel. `email_connector.py` (on-demand IMAP fetch of client mail+attachments → `intake/<slug>/`; approval-gated SMTP `send --confirm` — nothing leaves without sign-off), `profile_builder.py` (summarizes attachments via `cfe_savings.extract` — raw bytes never in context — fills the profile, computes completeness, writes `profile.json` + `outbound_draft.md`), `intake_schema.py` (machine-readable mirror of CLAUDE.md's Intake question bank; `audience=client` simple Spanish Qs vs `internal` defaults). Driven by the `client-intake` subagent; hands `profile.json` to `cfe-savings-analyst`. Email transport chosen first; WhatsApp slots behind the same adapter. See `tools/intake/README.md`.
- `intake/` — **client profiling workspace (2026-06-16):** one folder per client (`messages/`, `attachments/`, `thread.json`, `answers.json`, `profile.json`, `outbound_draft.md`); regenerable, not `raw/`. `profile.json.ready_for == ["cfe-savings-analyst"]` = enough to run the engine.
- `.claude/agents/` — six executors: `cfe-savings-analyst` (W4), `project-checker` (W5), `financial-auditor` (W6), `ppa-deal-pricer` (W7), `proposal-writer`, `client-intake` (front-of-funnel profiling).

## Pipeline Engineering — Findings (cfe-bill-parser)

*Engineering knowledge-graph findings on the WhatsApp→CFE bill-intake pipeline. See [[edge-function-maximalist]] for the governing decision.*

- [[needs-name-has-no-outbound-prompt-consumer]] — WhatsApp intake acks "te confirmaremos los RPUs" and stores `confirm_phone`, but the `needs_name`/`needs_ocr` bulk_pdf states have no consumer that prompts the sender — a silent dead-end (watchdog only logs at ~2h). The "wired-consumer" gap of [[edge-function-maximalist]].
- [[pdf-intake-titular-extraction-fails-real-bill]] — on a real CFE bulk PDF the RPU parses but the titular does not (observed 3×), so nameless bills can't reach CFE Consulta. The per-function-test / RPU+titular-only-purpose gap of [[edge-function-maximalist]].

## Supabase-DevOps — Reconciliation & Drift

*Git↔prod reconciliation and the GATE-0 fork. See [[canonicity-prod-is-truth]] for the governing decision.*

- [[2026-07-09-gate0-reconciliation-report]] — GATE-0 report for Jesus's canonicity ruling: dev vs main uniqueness, live-vs-dead code, stranded files, the 119-migration prod ledger (DEL-4), recommended direction, and preserve-both merge mechanics (no reset, nothing orphaned). Authorizes no execution.
- [[prod-only-drift-register]] — prod-only changes owed to the canonical branch: the 3 freeze REVOKEs, 016 claim_media (`20260709124613`), 017 bulk_pdf (`20260709132040`).
- [[2026-07-10-multirepo-branch-audit]] — READ-ONLY post-fetch audit across all repos/worktrees: per-repo divergence, stranded files, live-surface→branch map (main is live for nothing on its own), 3 unversioned deploy/auth dirs, 4 unpushed local branches. Confirms the newman-architecture fork still current (dev +102 / main +55).
- [[canonicity-prod-is-truth]] — decision: prod DB is source of truth; reconcile git to it, unify the fork.
- [[main-dev-fork]] — finding: main (cfe-collector) vs dev (CRM) is a two-way fork off frozen staging.
- [[migration-git-prod-drift]] — finding: git migrations do not reproduce the prod schema.
- [[graph-filing-two-roots-failure]] — finding: two wiki roots caused the phantom-page false alarm; single-root enforced.
