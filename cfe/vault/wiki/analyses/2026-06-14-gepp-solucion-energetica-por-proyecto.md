---
title: "GEPP — Solución energética por proyecto: PV/BESS/FP, esquema regulatorio y comparativo Compra vs PPA (motor + 20 años)"
type: analysis
tags: [gepp, pv, bess, fp-correction, ppa, autoconsumo, generacion-distribuida, abasto-aislado, gdmth, motor, 20-anios]
created: 2026-06-14
updated: 2026-06-14
sources: [2026-06-10-perfil-consumo-gepp-2025-26]
cliente: gepp
status: vigente
---

# GEPP — Solución energética por proyecto (motor determinista + comparativo comercial + 20 años)

**Pregunta:** Para cada proyecto del Excel GEPP 2025-26 (Ixtlahuacán, Acapulco, Cancún y Proplasa/PR1-PR2-TAP), ¿cuál es la mejor solución técnica y financiera bajo la ley energética mexicana (generación distribuida vs autoconsumo vs PPA vs abasto aislado) que **maximice el ahorro al cliente**, con simulación trazable, ambas estructuras comerciales (GEPP compra vs PPA/ahorro compartido) y proyección a 20 años?

> **Grado:** prefactibilidad. Ahorros y finanzas **derivados del motor** (`calc_core` sobre los volúmenes del Excel valuados a **tarifa CFE vigente 2026**); mecánica tarifaria/regulatoria **confirmada por fuente primaria**; costos de equipo, escalaciones y términos PPA son **supuestos**. No validado contra recibos CFE ni datos 15-min.

---

## Respuesta — qué pide GEPP y qué se recomienda

GEPP planteó cuatro problemáticas distintas (hoja `RESUMEN_` del workbook); la solución óptima cambia por sitio:

| Sitio | GEPP pide | Solución recomendada | Régimen LSE | Ahorro bruto/año | Compra: TIR / payback | PPA: benef. GEPP/año |
|---|---|---|---|---|---|---|
| **Ixtlahuacán** | combinar autoabasto Tala + solar | PV 2,530 kWp + BESS 850 kW/1,700 kWh | Autoconsumo CNE | $11.5M | 30% / 4 a | $3.6M |
| **Acapulco** | PPA o abasto aislado | FP + PV 1,020 kWp + BESS 320 kW/640 kWh | Autoconsumo CNE | $6.4M | 42% / 3 a | $3.1M |
| **Cancún** | PPA o abasto aislado | FP + PV 699 kWp (sin BESS) | **Generador exento <0.7 MW** | $3.7M | 44% / 3 a | $2.0M |
| **Proplasa** (PR1+PR2+TAP) | combinar autoabasto ENEL + solar | PV 10.5 MWp + BESS 2.37 MW/4.74 MWh | Autoconsumo CNE | $41.3M | ~28% / 5 a | $8.6M |
| **PORTAFOLIO** | — | 16.0 MWp PV + 3.54 MW BESS + FP | mixto | **$62.8M** (~20% del costo) | **TIR proyecto 28–44%** | **$17.1M** |

> **TODAS LAS CIFRAS PRE-IVA** (fila Subtotal del recibo; el IVA es acreditable para GEPP). Gasto total pre-IVA $294.6M ($341.9M con IVA = Total Recibo del workbook).

- **Gasto eléctrico total (2025, pre-IVA):** **$294.6M/año** ($175M→$151M CFE + $166M→$146M Tala/ENEL, pre-IVA; con IVA = $341.9M, que **coincide al dólar con el Total Recibo del Excel de GEPP**). Generación solar propuesta: **24.9 GWh/año**. Ahorro bruto $62.8M = **21.3% del gasto total pre-IVA**.
- **Ahorro bruto $62.8M/año** (régimen actual con Tala/ENEL) = PV $48.5M + BESS $13.3M + FP $2.3M; sube a **$63.2M** desde 2032 cuando expira Tala (el PV de Ixtlahuacán pasa a valor CFE pleno).
- **Compra (CAPEX $229.6M):** GEPP conserva **$57.3M/año** neto de O&M (año 1), beneficio acumulado 20 años ~**$1,969M**. **Comprar maximiza el ahorro** (la directiva del cliente).
- **PPA / ahorro compartido (cero inversión):** GEPP conserva **$17.1M/año** con TIR financiador 18%; **$25.5M/año** si se negocia el financiador a 14%.

## Refinamientos (2026-06-14b)
1. **Excel 100% trazable por fórmulas:** cada palanca (PV energía, PV demanda vía umbral, BESS demanda, arbitraje, FP, claw) se computa con fórmulas vivas desde las ENTRADAS (azul) en cada hoja de sitio; el total reconcilia con el motor a ≤0.01% (no son valores pegados). 2,888 fórmulas, 0 errores; las TIR de compra se derivan con `=IRR()` en hoja y coinciden con el motor.
2. **Tala/ENEL y 2032 con COSTOS REALES del workbook (corrección 2026-06-14c):** el workbook trae el costo peso por fuente en bloques por medidor (Total Planta = CFE + ENEL/Tala, verificado: PR2 $36.49M CFE + $4.67M ENEL = $41.16M). **Estructura real 2025 (PRE-IVA): $151M a CFE + $146M a Tala/ENEL = $294.6M** (con IVA $341.9M). Precios reales pre-IVA: ENEL ~$1.78-1.92/kWh, Tala $2.44, vs CFE $2.46-3.37. **El descuento del autoabasto es ~25-35% por kWh (ENEL), NO el 10% que supuse antes** — pero buena parte de esa brecha es que CFE reparte la demanda sobre menos kWh; al volver todo a CFE la demanda se re-amortiza, así que el **sobrecosto REAL a tarifa CFE plena (2032) = $19.8M/año pre-IVA** (= costo full-CFE $311M − costo actual $295M), no la resta ingenua de ~$70M. **ENEL ya colapsó en 2026** (Proplasa ~74%→15-25%) → el ahorro full-CFE ya es inmediato. El solar desplaza CFE (fuente cara) primero, así que el ahorro no depende del autoabasto restante; excepción zafra IXT 0.90× hasta 2032 (escalón año 7). Pendiente: take-or-pay de Tala/ENEL. **Único supuesto restante: la re-amortización de demanda a CFE pleno (la calcula el motor); los precios Tala/ENEL son dato del workbook.**

**Abasto aislado (preguntado en ACA/CAN): NO recomendado** — para carga industrial 24/7 exige respaldo firme (BESS sobredimensionado + gensets de gas), eleva el CAPEX 3–5× y sacrifica la red como respaldo, por un ahorro marginal. El PV+BESS conectado a red captura casi todo el ahorro a una fracción del costo.

---

## Cómo se obtuvieron los números (cadena determinista)

1. **`tools/import_perfil_xlsx.build_bill`** reconstruye el recibo-motor por mes desde el bloque **"Total Planta"** (carga física total = lo que el PV/BESS desplaza), valuado a **tarifa CFE vigente** (promedio de los meses 2026 publicados en la hoja `Tarifas`; los meses futuros venían en blanco — corregido en el driver).
2. **Dos bases:** **2025** (12 meses, estacionalidad completa) como línea base y **2026 Ene-Abr** (anualizado) como *run-rate* post-colapso ENEL/Tala. Reconcilian: el costo full-CFE 2025 ≈ 2026-anualizado por medidor (misma carga física, misma tarifa) → consistencia confirmada.
3. **`calc_core.compute`** da PV-only / BESS / Híbrido + finanzas (TIR proyecto y TIR financiador). **`ppa_pricer.solve_ppa_rate`** resuelve la tarifa PPA para TIR financiador 18% (y 14%); **`deal_flows`** da los flujos cliente/financiador a 20 años.
4. **Entregables trazables:** el Excel reproduce la generación (`=kWp×rend`), el recibo mensual (Antes/Después/%) y el flujo a 20 años con `=IRR()/=NPV()` en hoja — la TIR de compra de los flujos visibles **coincide con el motor** (Δ ≤ 0.6 pp).

### Diferencia vs el reporte previo ([[2026-06-11-gepp-recomendacion-sistemas-por-sitio]])
El ahorro bruto sube de **$56.9M (modelo simplificado)** a **$63.2M (motor)**. La diferencia es la **reducción de demanda vía umbral** que el PV produce cuando el piso de demanda facturable es el que cobra — el motor la captura (componente `dem_pv`), el modelo simplificado previo solo contaba energía. El motor es la autoridad ([[demanda-facturable]], [[pv-savings-model]]). El gasto CFE base ($341.9M) es idéntico en ambos.

### Hallazgo 2026 (Proplasa)
El **retiro de ENEL ya ocurrió**: PR2 colapsó ~sep 2025, PR1/TAP en mar 2026; a abril 2026 el predio compra ~85% a CFE plena. El ahorro full-CFE de Proplasa es **inmediato**, no a futuro — refuerza el caso solar.

---

## Por sitio (resumen)

- **Ixtlahuacán (Tala):** el PV va detrás del medidor y reduce el consumo neto antes del reparto Tala/CFE; en zafra desplaza energía descontada (0.9×), fuera de zafra CFE plena. No compite con Tala (estacional), lo complementa. Pendiente: cláusulas del contrato (take-or-pay) y auditar picos de demanda 2025 >5,000 kW contratados. ([[generador-exento]]→ aquí >0.7 MW = [[autoconsumo]]).
- **Acapulco (100% CFE):** FP es la palanca #1 (multa $1.7M/año, FP ~85%, payback meses). PV+BESS encima. PPA viable a $1.68/kWh.
- **Cancún (100% CFE):** electricidad más cara (Peninsular); **PV <0.7 MW = exento** (sin permiso, [[medicion-neta]] acredita excedentes) → la vía más rápida; **sin BESS** (umbral satura 9/12 meses, [[bess-savings-model]]). Mejor ROI (TIR 44%).
- **Proplasa (ENEL):** mayor consumidor; 3 medidores independientes; PV 10.5 MWp + BESS 2.37 MW. Mayor ahorro absoluto ($41.3M/año). Pendiente: contrato ENEL y espacio (~62,000 m²).

## Comparativo comercial (doctrina)
- **Comprar** maximiza el ahorro de GEPP y la TIR de proyecto (28–44%) supera el costo de capital → recomendado para un offtaker con capital como GEPP.
- **PPA/ahorro compartido** = cero inversión/riesgo; el financiador es dueño y cobra tarifa PPA (sobre generación PV) + comisión (sobre ahorro BESS) para su TIR objetivo. La TIR financiador es **negociable**: 18%→14% sube el beneficio de GEPP de $17.3M a $25.9M/año.
- FP siempre se trata como palanca GEPP (capex trivial, payback meses), separada de PV/BESS.

---

## Entregables
- `entregables/calculadoras/GEPP - Solucion Energetica por Proyecto.xlsx` — libro maestro: Resumen Ejecutivo, Supuestos, 6 hojas por medidor (memoria de cálculo trazable + resumen mensual + 20 años con IRR/NPV en hoja), Comparativo Comercial, Proyección 20 años (1,520 fórmulas, 0 errores).
- `entregables/propuestas/GEPP - Propuesta Solucion Energetica (4 sitios).docx` (+ `.pdf`) — propuesta es-MX para dirección: resumen ejecutivo, Q&A de dirección, propuesta por sitio, comparativo comercial, veredicto abasto aislado, 20 años, riesgos y próximos pasos.
- `entregables/calculadoras/gepp_solution_data.json` — salida del motor (respaldo de cifras).

## Próximos pasos
1. **Corrección FP en Acapulco y Cancún ya** (no depende de nada; payback meses).
2. **12 recibos CFE + datos 15-min por medidor** → validación peso-exacta y BESS bancable.
3. **Contratos Tala y ENEL**: generación en sitio permitida, take-or-pay, salida (ambos vencen 2032).
4. Áreas reales de techo/terreno y capacidad de transformadores.
5. Decidir compra vs PPA; si PPA, negociar TIR del financiador.

## Sources consultadas
- [[2026-06-10-perfil-consumo-gepp-2025-26]] — el Excel base (datos)
- [[2026-06-10-gepp-portfolio-project-check]] · [[2026-06-11-gepp-recomendacion-sistemas-por-sitio]] — análisis previos (este los extiende con motor + estructuras comerciales + 20 años)
- [[pv-savings-model]] · [[bess-savings-model]] · [[pv-bess-combined]] · [[demanda-facturable]] · [[medicion-neta]] · [[horarios-y-divisiones]] — mecánica de palancas
- [[autoconsumo]] · [[generador-exento]] · [[generacion-distribuida]] · [[scheme-comparison]] · [[cne]] — marco regulatorio LSE/CNE 2025
- Motor: `tools/cfe_savings` (golden 18/18 vigente), `tools/calc_core.py`, `tools/ppa_pricer.py`, `tools/import_perfil_xlsx.py`

## Confidence
**Media (prefactibilidad).** Niveles de certeza: gasto CFE base ($341.9M) y volúmenes = **dato del cliente** (extracción validada al dólar). Multas FP (ACA/CAN) **impresas en el Excel** (dato duro). Ahorros PV/BESS y finanzas = **derivados del motor** (golden 18/18; Excel reconcilia a motor Δ≤0.6pp). Mecánica regulatoria = **fuente primaria**. Supuestos: EPC/FX/escalaciones/disponibilidad/PPA/cero-contraprestación. Incógnitas abiertas: contratos Tala/ENEL, datos 15-min, recibos CFE, espacio Proplasa, picos de demanda Ixtlahuacán.
