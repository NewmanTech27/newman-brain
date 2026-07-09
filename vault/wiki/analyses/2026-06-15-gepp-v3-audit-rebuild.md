---
title: "GEPP — Auditoría del Excel v2 y reconstrucción v3: línea base CFE pleno, Tarifa Actual, PPA 15a + transferencia, Supuestos en vivo"
type: analysis
tags: [gepp, audit, pv, bess, fp-correction, ppa, autoconsumo, tarifa-actual, supuestos-vivo, 20-anios, pre-iva]
created: 2026-06-15
updated: 2026-06-15
sources: [2026-06-10-perfil-consumo-gepp-2025-26]
cliente: gepp
rpu: "455GR3, MX096Y, 073EEK, 806DYN, 805DYN, 807DYN"
status: vigente
---

# GEPP — Auditoría v2 + reconstrucción v3 (Excel en vivo)

**Pregunta:** Revisar la lógica de ahorro del Excel `GEPP - Solucion Energetica (v2 pre-IVA)`, explicar de dónde sale el `$25,723,110` de costo CFE para Ixtlahuacán (el usuario veía `$55,226,961`), y reconstruir el modelo: PPA 15 años editable + BESS 20 años, capacitores a cargo del financiador en PPA, columna "Tarifa Actual" con el escalón 2032, decomposición ENEL/Tala, página de Supuestos en vivo por proyecto, y por qué cada dimensionamiento PV/BESS es el óptimo.

> **Grado:** prefactibilidad. Línea base = recibo GEPP (dato del workbook); ahorros = motor determinista (golden 18/18, replicado al peso); finanzas/PPA = supuestos editables.

## Hallazgo 1 — el bug del costo CFE de Ixtlahuacán ($25,723,110)

El v2 imputaba el CFE por resta: `CFE = Total neto − Tala bruto = $52,544,793 − $26,821,683 = $25,723,110`. Eso mezcla bases (resta el bloque Tala **bruto/equiv-CFE** del total **neto** que ya descuenta Tala), subvaluando CFE por exactamente el descuento Tala (`$28,405,279 − $25,723,110 = $2,682,168 = 26,821,683 × 10%`).

**El número correcto de CFE es `$28,405,279`** (bloque CFE real del workbook, `IXT!AF53` — la cifra del usuario). Reconciliación de Ixtlahuacán (pre-IVA, 2025), toda con datos del workbook:

| Concepto | $ | Origen |
|---|---|---|
| **CFE BRUTO = Tarifa Actual** (todo a CFE pleno, sin autoabasto) | **55,226,961** | `Total Planta` gross = `SUM(AF17:AF22)` = la cifra `$55,226,961` del usuario |
| (−) Ahorro autoabasto Tala (Descuento) | 2,682,168 | fila `Descuento` (AF28) |
| (=) Costo actual que paga GEPP hoy | 52,544,793 | `Subtotal` neto (×1.16 = $60.95M) |
| ›CFE (real) | 28,405,279 | bloque CFE (AF53) — **corrige el $25.7M** |
| ›Tala neto | 24,139,514 | bloque Tala − descuento |

El `$55,226,961` del usuario **es correcto**: es la carga completa valuada a CFE pleno (Tala sin su descuento), que es exactamente la **línea base que pidió** ("el costo que tendrían con CFE sin ENEL/TALA ni PV/BESS").

## Hallazgo 2 — la línea base del motor venía 3-7% baja

La reconstrucción del motor subvalúa el recibo impreso (Acapulco/Cancún −7%, Ixtlahuacán −3.3%) por la base de demanda no importada (distribución/umbral). **v3 ancla "Tarifa Actual" al número duro del workbook** (`Total Planta` gross para sitios CFE/Tala; `costo + premium` validado por el colapso ENEL 2026 para Proplasa) con un factor de calibración visible por hoja. Los ahorros PV/BESS/FP siguen siendo del motor (pesos absolutos, válidos).

## Hallazgo 3 — Comparativo y Proyección estaban desconectados (valores pegados). v3 los conecta por fórmula a una página de Supuestos en vivo.

## Marco de línea base (cartera, pre-IVA, año 1)

| | $ |
|---|---|
| **CFE BRUTO (Tarifa Actual, todo CFE sin autoabasto)** | **316,192,996** |
| (−) Ahorro autoabasto Tala+ENEL (vence 2032) | 21,558,823 |
| (=) Costo actual hoy | 294,634,173 |
| (−) Ahorro PV | 48,449,691 |
| (−) Ahorro BESS | 12,036,603 |
| (−) Ahorro FP | 2,313,809 |
| (=) Costo neto con proyecto | 231,834,071 |

Ahorro proyecto PV+BESS+FP = **$62.8M (21.3% del gasto actual)**; gen solar 24.9 GWh. Refinamiento vs v2: el beneficio autoabasto de Ixtlahuacán se ancla al `Descuento` duro del workbook ($2.68M) en vez del premium del motor ($0.9M) → cliff de cartera $21.56M (antes $19.8M).

## El entregable v3 (`entregables/calculadoras/GEPP - Solucion Energetica (v3 pre-IVA).xlsx`)

10 hojas, 3,882 fórmulas, 0 errores. Novedades sobre v2:

1. **Supuestos = página de control en vivo:** globales + tabla **por proyecto** (PV/BESS kWp, costo PV USD/Wp, costo BESS USD/kWh, capacitor $, **PPA $/kWh**, **plazo PPA**, comisión BESS%). Toda celda azul propaga a las 6 hojas de sitio, Comparativo y Proyección. TIR financiador, TIR compra y ahorro/año se calculan en vivo.
2. **PPA 15 años editable + BESS 20 años:** el PV se transfiere a GEPP al término del PPA (año 16-20 el cliente conserva 100% del ahorro PV; `PagoPPA→0`, flujo financiador cae a sólo comisión BESS). TIR financiador resuelta sobre el flujo combinado PV(15)+BESS(20); las tarifas PPA semilla dan 18%.
3. **Capacitores (FP) a cargo del financiador en PPA** → el cliente no desembolsa; conserva 100% del ahorro FP.
4. **Columna "Tarifa Actual" en los 20 años** = lo que pagarían sin proyecto, con autoabasto hasta 2031 y **escalón a CFE pleno en 2032** (visible: año 6→7).
5. **Decomposición ENEL/Tala por sitio:** CFE bruto → Ahorro autoabasto → Ah PV → Ah BESS → Ah FP; en Proplasa se muestra la mezcla CFE%/ENEL% (PR2 43%/57%) y cómo el PV recorta primero la porción CFE.
6. **Comparativo Comercial conectado** (referencias en vivo a cada sitio) y **Proyección 20 años** = suma por fórmula de los 6 medidores.
7. **§8 por sitio: por qué ese dimensionamiento es el óptimo** (maximiza ahorro sin sobredimensionar).

## Por qué cada configuración es la óptima (resumen)

- **Ixtlahuacán** — PV 2,530 kWp al consumo intermedio diurno (autoconsumo, >0.7 MW ⇒ CNE); BESS 850 kW recorta el pico de punta (única palanca de demanda bajo umbral). Complementa a Tala (estacional) y cubre el escalón 2032.
- **Acapulco** — FP primero (multa $1.7M, payback meses); PV 1,020 kWp diurno; BESS chico (320 kW) porque el umbral satura la demanda. TIR compra 42%.
- **Cancún** — PV 699 kWp **deliberadamente <0.7 MW** = generador exento (medición neta, sin permiso), mejor ROI (TIR 44%); sin BESS (umbral satura 9/12 meses). FP corrige multa.
- **Proplasa (PR1/PR2/TAP)** — PV al consumo diurno desplazando energía CFE cara primero; BESS recorta punta; >0.7 MW ⇒ Autoconsumo CNE. ENEL ya colapsó (2026) ⇒ ahorro full-CFE inmediato.

## Veredicto comercial
Comprar maximiza el ahorro (TIR proyecto 28-44%, beneficio $57.2M/año, acum 20a ~$1,965M). PPA/ahorro compartido = cero inversión (financiador funda todo, incl. capacitores), beneficio cliente $20.0M/año @18%; negociable a 14%. Todo recalcula en vivo desde Supuestos.

## Verificación
- Motor replicado al peso en Python y como fórmulas Excel: los 6 sitios coinciden con el motor v2 (PV/BESS/FP) — arbitraje carga en base, descarga en punta; Fac.AA zafra Ene-May+Dic.
- `recalc` LibreOffice: 3,882 fórmulas, **0 errores**.
- Liveness probada: ↑PPA $/kWh ⇒ ↑TIR fin; ↑costo PV ⇒ ↓TIR compra; plazo PPA 15→10 ⇒ TIR fin 18%→14% (propaga a Comparativo).
- Reconciliación: CFE bruto $316.2M, costo hoy $294.6M, ahorro $62.8M, gen 24.9 GWh — cuadran con el motor y el workbook GEPP.

## Sources consultadas
- [[2026-06-10-perfil-consumo-gepp-2025-26]] — workbook base (datos duros)
- [[2026-06-14-gepp-solucion-energetica-por-proyecto]] — análisis previo (este lo audita, corrige el split CFE/Tala y reestructura)
- [[demanda-facturable]] · [[pv-savings-model]] · [[bess-savings-model]] · [[pv-bess-combined]] · [[medicion-neta]] — mecánica de palancas
- [[autoconsumo]] · [[generador-exento]] · [[cne]] — marco LSE/CNE 2025

## Confidence
**Media (prefactibilidad).** Línea base = recibo GEPP (dato duro, validado al dólar); el `$28,405,279` de CFE y el `$55,226,961` de Tarifa Actual son cifras nativas del workbook. Ahorros = motor (golden 18/18, replicado al peso). Supuestos editables: EPC/FX/escalaciones/PPA/comisión/cliff ENEL. Pendiente: contratos Tala/ENEL (take-or-pay), datos 15-min, recibos CFE, áreas reales.
