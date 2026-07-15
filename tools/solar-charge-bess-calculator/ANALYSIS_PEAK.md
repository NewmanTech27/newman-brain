# ANALYSIS_PEAK — ¿Por qué el "Autoconsumo Max" (NR) hace pico?

**Fecha:** 2026-07-15 · **Modelo:** GEPP BESS Carga Solar rev4 · **Opción:** 1 (Autoconsumo) · **Estado:** análisis derivado, prefactibilidad.
**Motor:** `dispatch_cs.py` (despacho carga-solar, self-basis, BESS fijo) para energía y economía del deal; `tools/calc_core.py` (lógica umbral golden, RPU `780881200029` intacto) para la auditoría de demanda. Cifras **[motor]** = engine-derived; **[sup]** = supuesto/convención.

**Sondas nuevas (re-ejecutables, no tocan la maquinaria entregada):** `probe_peak.py` → `probe_peak.json` (Q1) · `probe_bess_scale.py` → `probe_bess_scale.json` (Q2) · `probe_umbral.py` → `probe_umbral.json` (Q3) · `probe_verdict.py` → `probe_verdict.json` (Q4) · `build_peak_analysis.py` → `peak_analysis.json` (deck-ready). Correr con `BOOKS_DATA=$PWD/books_data.json`.

---

## Gate de sanidad (obligatorio) — **PASS**

Reproducción del **ahorro cliente año 1 NR por sitio** con la metodología EXACTA del deck NR (k conjunto `k_NR=0.949527` sobre SITES4=[ixt,aca,can,pro] a TIR inversionista combinada 14.000%):

| Sitio | Motor (esta corrida) | NUMBERS_NR.md | Desv. |
|---|---|---|---|
| Ixtlahuacán | $10,796,202 | $10,796,202 | 0.0000% |
| Acapulco | $5,061,321 | $5,061,321 | 0.0000% |
| Cancún | $2,861,105 | $2,861,105 | 0.0000% |
| Proplasa | $38,462,663 | $38,462,663 | 0.0000% |

Portafolio VAN 20a NR = **$617,217,004** (exacto vs NUMBERS_NR). `dispatch_cs.py` gate 1 (réplica modo-viejo) worst 0.008% < 0.1%. **Todo por debajo de 0.1% → números nuevos confiables.**

---

## Q1 — ¿Por qué el óptimo NR hace pico aunque el excedente pueda cargar el BESS?

**Metodología (4 líneas).** Barrido fino de kWp alrededor del óptimo standalone (k re-resuelto por punto a TIR 14%). En cada paso descompongo el **kWh marginal de generación** en tres cubetas excluyentes: **(a)** autoconsumo directo `d(self)=d Σmin(carga,pv)`, **(b)** carga solar absorbida por el BESS `d(carga_solar)` (acotada por la energía de carga FIJA `N/RTE`), **(c)** excedente remanente `d(remanente)` a `texc≈$0`. Identidad exacta: `dGen = d(self)+d(carga_solar)+d(remanente)`. Techo direccionable = carga diurna coincidente (asintótica) + `N` (desplazamiento de punta).

**Respuesta en una frase:** el excedente solar **sí** carga el BESS, pero el requerimiento de carga es **FIJO** (`N/RTE`, lo fija el lado de descarga = desplazamiento de punta), así que la cubeta (b) **satura rápido**; saturadas (a) autoconsumo diurno y (b) carga-solar, cada kWp extra cae en (c) remanente a **$0**, mientras su CAPEX acarreado a TIR-14 **sube k** (el PPA sube en TODOS los kWh autoconsumidos). El valor marginal cliente cruza a negativo → pico.

**Techo direccionable y saturación en el óptimo [motor]:**

| Sitio | kWp_NR | Carga diurna (techo self) | N (punta) | Direccionable total | self @opt (% techo) | carga-solar @opt | **Sat. BESS @opt** | remanente @opt |
|---|---|---|---|---|---|---|---|---|
| Ixtlahuacán | 5,430 | 11,544,261 | 1,829,374 | 13,373,635 | 8,501,741 (74%) | 803,335 | **42.2%** | 379,220 |
| Acapulco | 2,270 | 4,354,310 | 759,294 | 5,113,604 | 3,379,797 (78%) | 603,263 | **76.3%** | 260,588 |
| Cancún | 1,410 | 2,343,634 | 452,699 | 2,796,333 | 1,777,476 (76%) | 219,930 | **46.6%** | 117,300 |
| Proplasa | 20,000 | 46,362,533 | 6,173,297 | 52,535,830 | 31,485,777 (68%) | 1,048,313 | **16.3%** | 669,270 |

*(kWh/año, [motor])*

**Traza marginal cerca del pico [motor]** (fracción a/b/c del kWh incremental, y $ marginal por kWp):

- **Ixtlahuacán** (pico ≈5,430): a 5,450→5,600 el marginal $/kWp voltea **+23 → −55**; el split pasa de a0.35/b0.48/c0.17 a a0.34/b0.44/**c0.22** (remanente creciendo). Sat. BESS 42%→49%.
- **Acapulco** (pico 2,270): pasado el óptimo el remanente domina (**c≈0.79→0.87**), la carga-solar **satura al 100%** (~2,850 kWp), $/kWp ≈ **−900 a −1,090**.
- **Cancún** (pico 1,410): idéntico — carga-solar satura ~2,000 kWp, remanente **c≈0.79→0.90**, $/kWp ≈ **−1,130 a −1,420**.
- **Proplasa** (20,000): la curva **AÚN SUBE** en el cap (marginal **+$514/kWp**, split a0.59/b0.30/c0.11) — no es pico interior.

**Qué liga exactamente en cada sitio:**

- **Ixtlahuacán — pico económico interior.** BESS solo 42% saturado (holgura de carga-solar), pero el valor marginal combinado (autoconsumo diurno declinante ~t_int + bono carga-solar ~t_base) ya no cubre el CAPEX acarreado. Por eso ixt se estira más allá del rev4 (5,170→5,430) antes de topar.
- **Acapulco / Cancún — pico por saturación de ambas cubetas de valor.** La carga-solar del BESS satura (76%/47% en el óptimo, 100% justo después) y el autoconsumo diurno se aplana (~77-78% del techo, fracción marginal ya baja); el kWh siguiente es remanente@$0.
- **Proplasa — truncamiento regulatorio.** El consumo es tan grande que 20 MW apenas cubre el 68% del techo diurno y satura el BESS al 16%; el óptimo económico está **por encima** del cap de 20 MW → el pico es el **techo regulatorio**, no economía.

**Por qué el usuario esperaba más PV (y por qué no):** la intuición "el excedente carga el BESS → cabe más PV" falla porque el BESS solo absorbe `N/RTE` al año (fijado por lo que descarga en punta, no por el sol disponible). Absorbida esa energía, el sol extra no tiene comprador (texc≈$0). La coincidencia solar-mediodía del autoconsumo + la energía de carga fija del BESS son el techo real — no la superficie.

---

## Q2 — ¿El pico es un ARTEFACTO del BESS fijo? ¿Más BESS destraba más PV?

**Metodología (3 líneas).** Chequeo barato: ¿qué liga `N` mes a mes? ¿está saturada la capacidad `Q`? Luego co-optimización: escalo potencia+energía del BESS **×1.5/×2/×3** (C28, C29, C30 y CAPEX BESS lineales; base CAPEX = `C29·B7(0.28)·1000·FX(17.55)` = **$4,914/kWh**, idéntica al libro), re-resuelvo k standalone por kWp **incluyendo CAPEX+O&M BESS incremental**, y veo si el óptimo cliente sube.

**Chequeo barato [motor]:** la **capacidad `Q` ya está saturada** en los 4 sitios: `min(1, C30/Qdiv) = 1.0000` → **más energía de BESS agrega CERO ahorro de capacidad**. El binding de `N` es mixto (energía `C30·días` liga en varios meses; potencia `C28` nunca liga):

| Sitio | N liga por punta(kWh) | N liga por energía(C30·d) | N actual → N máx (energía libre) |
|---|---|---|---|
| Ixtlahuacán | 6 meses | 6 meses | 1,829,374 → 2,150,783 (+18%) |
| Acapulco | 7 | 5 | 759,294 → 857,678 (+13%) |
| Cancún | 7 | 5 | 452,699 → 494,180 (+9%) |
| Proplasa | 2 | 10 | 6,173,297 → 7,891,185 (+28%) |

Hay holgura de descarga en los meses "energía", pero pequeña frente al CAPEX que la crea.

**Co-optimización [motor]** — óptimo cliente (kWp / ahorro año1) al escalar BESS:

| Escala BESS | Ixt | Aca | Can | Pro |
|---|---|---|---|---|
| ×1.0 | 5,450 / **$10.62M** | 2,250 / **$4.21M** | 1,400 / **$2.58M** | 20,000 / **$39.76M** |
| ×1.5 | 5,450 / $7.74M | 2,300 / $2.89M | 1,400 / $1.78M | 20,000 / $30.81M |
| ×2.0 | 5,450 / $4.56M | 2,300 / $1.48M | 1,400 / $0.93M | 20,000 / $20.89M |
| ×3.0 | 5,450 / **−$1.80M** | 2,300 / **−$1.36M** | 1,400 / **−$0.75M** | 20,000 / $0.62M |

**Respuesta: NO.** Más BESS **no mueve el óptimo kWp** (Δ ≤ +50 kWp) y **destruye valor cliente** (ahorro cae monótonamente; a ×3 el deal se vuelve negativo). Razón: `Q` ya está tope, y el `N` incremental (arbitraje ≈ (t_punta−t_base)/kWh) es chico frente al CAPEX+O&M acarreado a TIR-14 (que el cliente paga vía B17=0.5 y vía k más alto). El pico del PV **no** es artefacto del BESS fijo; el BESS entregado ya es, si acaso, ligeramente generoso. **Más BESS no destraba más PV.**

---

## Q3 — Auditoría del UMBRAL ENERGÉTICO (escalado lineal del deck vs mecánica calc_core)

**Metodología (4 líneas).** El deck (`dispatch_cs` L158-159) escala distribución **lineal** con kWp (`distrib = ΣL·kwp/M_div`) y mantiene `Q` **fija**. La mecánica verdadera (calc_core / demanda-facturable): más PV → baja `kWh_red` → **colapsa el umbral** `= kWh_red/(d·0.57·24)` → baja la base de demanda facturable → **canibaliza** el ahorro de demanda del BESS. Recalculo con calc_core (umbral golden) sobre `imported/gepp-*` a kWp_NR con el BESS del libro (C28, C29): `dem_pv` (reducción PV vía umbral) + `dem_bess_h` (recorte incremental del BESS, base umbral POST-PV). El modo grid-base de calc_core es irrelevante: el lado de demanda no depende de la fuente de carga.

**Resultado [motor]** — demanda total (distrib+capacidad) a kWp_NR, libro vs calc_core golden:

| Sitio | Libro distrib lineal | Libro Q capacidad | **Libro total** | calc dem_pv | calc dem_bess | **calc total** | Δ (libro−verdad) |
|---|---|---|---|---|---|---|---|
| Ixtlahuacán | 0 | 11,749,925 | 11,749,925 | 5,405,109 | 6,591,516 | 11,996,625 | **−$246,700 (−2.1%)** |
| Acapulco | 884,838 | 4,276,904 | 5,161,742 | 2,204,200 | 3,029,242 | 5,233,442 | **−$71,699 (−1.4%)** |
| Cancún | 228,807 | 2,799,362 | 3,028,169 | 1,657,914 | 1,471,027 | 3,128,942 | **−$100,773 (−3.2%)** |
| Proplasa* | 0 | 39,451,578 | 39,451,578 | 3,884,953 | 36,964,355 | 40,849,309 | **−$1,397,731 (−3.4%)** |
| **Portafolio** | | | **59,391,414** | | | **61,208,318** | **−$1,816,904 (−3.0%)** |

*Proplasa = proxy per-meter (pr1+pr2+tap): `pro` consolidado no tiene recibos importados. Preforma-1 es la excepción: el libro **sobreestima** +5.6% (+$370k); el resto subestima.

**Dirección y magnitud del error del deck:** el escalado lineal + Q fija **subestima levemente** la demanda verdadera (−1.4% a −3.4% por sitio, **−3.0% portafolio ≈ −$1.8M/año**), salvo pr1 (+5.6%). Es **conservador**. El acierto viene de una compensación: al subir la penetración PV, `dem_pv` **sube** mientras `dem_bess` **baja**, y el (distrib lineal + Q fija) captura la suma reasignada dentro de ±3%.

**¿El colapso del umbral a NR reduce materialmente el ahorro de demanda del BESS?** Sí, **modestamente** [motor] — `dem_bess` rev4→NR: Ixt −$126k (−1.9%), **Aca −$338k (−10%)**, Can −$73k (−4.7%), Proplasa −$3.88M (−9.5%). Acapulco es el peor caso relativo (−10%); el resto −2 a −5%. Es real (no-aditividad pv-bess-combined), pero no cambia el orden de magnitud y el deck ya lo absorbe dentro de su margen conservador del 3%.

---

## Q4 — VEREDICTO: ¿la carga solar hace al BESS irrelevante o MÁS relevante?

**Metodología (3 líneas).** A kWp_NR por sitio comparo **CON BESS** (config NR, despacho carga-solar) vs **SIN BESS** (mismo kWp, solo PV), con **k re-resuelto standalone por config** (ambos a TIR inversionista 14%). CON BESS: cliente = `(M72+ahorro_bess) − K72·precio − ahorro_bess·B17`. SIN BESS: cliente = `M72 − K72·precio_pv`, inversionista = solo PPA PV. Combino (i) el bono de arbitraje casi-gratis, (ii) el colapso de umbral de Q3, (iii) la sonda previa grid-charge (no-BESS ganaba VAN en 3/6).

**Resultado [motor]** — VAN 20a cliente CON vs SIN BESS a kWp_NR:

| Sitio | Bono carga-solar $/año | CON BESS VAN | SIN BESS VAN | Δ VAN (con−sin) | **Veredicto** |
|---|---|---|---|---|---|
| Ixtlahuacán | 893,114 | $115,053,920 | $59,691,309 | **+$55,362,611** | **CON BESS** |
| Acapulco | 605,097 | $46,301,055 | $27,893,583 | **+$18,407,472** | **CON BESS** |
| Cancún | 283,437 | $28,328,224 | $15,671,537 | **+$12,656,686** | **CON BESS** |
| Proplasa | 1,184,247 | $427,533,805 | $245,736,829 | **+$181,796,976** | **CON BESS** |
| **Portafolio (4-row)** | 2,965,895 | **$617,217,004** | **$348,993,258** | **+$268,223,746** | **CON BESS** |

**Veredicto: la carga solar hace al BESS MÁS relevante, no irrelevante — en los 4 sitios.** **REVIERTE** la conclusión de la sonda grid-charge previa (2026-07-15-gepp-autoconsumo-max-bess-y-techo-solar), donde no-BESS ganaba el VAN cliente en Cancún, Acapulco e Ixtlahuacán. El mecanismo del vuelco: (i) bajo carga-solar el ciclo del BESS es casi gratis (bono = `carga_solar·t_base`, $283k–$1.18M/año por sitio), así que el arbitraje ya no compite contra un costo de carga en base; (ii) la capacidad `Q` sigue viva y **saturada** (el colapso de umbral solo la recorta 2-10%, Q3); (iii) el shave de punta del BESS es la única palanca que toca la punta (bess-savings-model) — el PV en SIN no la toca (pv-savings-model). A kWp_NR el híbrido domina claramente al PV-solo.

**Caveat regulatorio (fuente-confirmada):** el caso SIN BESS a ≥0.7 MW intermitente **exige SAE o respaldo CFE contratado** (DACG 4.5, autoconsumo); ese costo **no está modelado**. Aun ignorándolo (favoreciendo a SIN BESS), CON BESS gana — con el costo de respaldo, gana por más.

---

## Caveats (prefactibilidad)

- **Prefactibilidad, no bancable.** Datos GEPP mensuales (B/I/P de `imported/gepp-*`) + curva de giro industrial 24/7 escalada + campana solar sintética (`PV_BELL`); **sin medición horaria HM 15-min**. El reparto carga-solar/base, `pct_ac` y el techo diurno son cifras de prefactibilidad.
- **Umbral con calc_core:** usa los recibos importados (lógica umbral golden, RPU 780881200029 intacto). Su modo de carga BESS es grid-base — irrelevante para el lado de demanda auditado. `pro` consolidado no tiene recibos → proxy per-meter (pr1+pr2+tap) para Q3/pro.
- **k y subsidio cruzado:** Q1/Q2/Q4 usan **k standalone por sitio** (cota defensible, sin subsidio cruzado). El gate y el deck NR usan **k conjunto** (SITES4). Ambos son engine-derived; los rótulos lo indican. La suma de VAN cliente sobre SITES4 es invariante al reparto de k (verificado: standalone y conjunto dan $617,217,004).
- **Superficie / interconexión sin visita técnica.** kWp_NR de aca (faltan 2,061 m²) y pro (topa 20 MW regulatorio; predio insuficiente) son cotas teóricas.
- `tools/cfe_savings/` y `calc_core.py` **no se tocaron**; ninguna maquinaria entregada (`dispatch_cs`/`sweep_cs*`/`solve_k_cs`/`build_nr`, xlsx/html/motor_*.json) se modificó — las sondas son scripts nuevos.

## Salidas

- `ANALYSIS_PEAK.md` (este documento).
- `peak_analysis.json` — deck-ready: por sitio {curve con split marginal a/b/c, saturacion_bess_pct_at_opt, ceiling, umbral {distrib_linear_deck, distrib_true_calc_core, capacidad_true, delta}, bess_scale, bess_verdict {con/sin ahorro+VAN, veredicto}} + totales portafolio.
- Sondas fuente: `probe_peak.json`, `probe_bess_scale.json`, `probe_umbral.json`, `probe_verdict.json`.
