---
title: "Calculadora genérica PV/BESS/Híbrido — rebuild cliente-agnóstico de la calculadora v1"
type: analysis
tags: [calculadora, excel, pv, bess, hibrido, gdmth, autoconsumo, medicion-neta, webapp, build]
created: 2026-06-11
updated: 2026-06-11
sources: [2026-06-08-calculadora-bess-pv-excel, 2026-06-08-cfe-bills-780881200029-fy25-26]
status: vigente
---

# Calculadora genérica PV/BESS/Híbrido — rebuild cliente-agnóstico

**Question:** "Redo this excel calculator" (raw/data/780881200029.xlsx) — pero genérica: cualquier cliente, 12 meses de recibos, escenarios PV / BESS / Híbrido, supuestos auto-propuestos por perfil, **caps regulatorios** al cruzar de medición neta (DG) a autoconsumo, y arquitectura lista para ser la base de una webapp.

## Answer

**Entregable:** `Calculadora Ahorros PV-BESS (generica).xlsx` (en `entregables/calculadoras/`; originalmente raíz, movida 2026-06-12), generada por `tools/build_calculadora_generica.py` (espejo python de cada fórmula). Demo precargado: 780881200029.

**Qué es:** la generalización de `780881200029 - Calculadora v2.xlsx` (el rebuild corregido del audit [[2026-06-11-780881200029-calculadora-audit]]). Hereda todo el set de fórmulas corregido (sin E1–E5) y agrega lo que la v2 no tenía:

1. **Cliente-agnóstica** — INPUTS con perfil (giro, división, demanda contratada), BILLS con captura de 12 recibos y validación `(MEM + bonif FP) × 1.16` vs recibo por mes (REVISAR si >0.5%), RATES deriva tarifas implícitas del propio recibo (0-safe para meses sin punta/base).
2. **Tres escenarios side-by-side** en CALC: PV-only / BESS-only / Híbrido, con la interacción de umbral correcta ([[pv-bess-combined]]: híbrido ≥ suma cuando el umbral no amarra).
3. **Caps regulatorios automáticos** (hoja REGIMEN, dispara en `kWp ≥ 700`):
   - **< 0.7 MW** — [[generador-exento]] / [[medicion-neta]]: 100% del PV acreditable con tope al consumo del mes; excedente estructural alertado (créditos expiran a PML en 12 meses) y valuado a tarifa excedentes editable (default $0, piso conservador).
   - **≥ 0.7 MW** — [[autoconsumo]]: solo el **% de autoconsumo instantáneo** se acredita (default por giro: Hotel 80%, Industrial 24/7 90%, 1 turno 65%, Retail 75%, Oficinas 60% — **supuestos**, override-ables), excedentes solo a CFE (default $0), y checklist de obligaciones: permiso CNE simplificado/ordinario, registro anual 1T, uso mínimo 30%, **respaldo SAE obligatorio** (marcado como cubierto si el proyecto trae BESS).
   - **BESS / [[sae-cc]]**: sin permiso, inyección prohibida, alerta si potencia BESS > demanda contratada; descarga limitada a días hábiles punta (NETWORKDAYS + festivos) y al kWh punta del recibo ([[bess-savings-model]]).
   - Alertas adicionales: gate 100 kW GDMTO/GDMTH, cargo FP detectado (palanca de corrección FP separada, opt-in, nunca mezclada), división no-SIN (precaución: tarifas no-SIN = gap abierto).
4. **División configurable** (SIN/BC/BCS) — matriz de horas punta por mes; BC/BCS invierno sin punta manejado (shave y arbitraje = 0).
5. **FINANCE doctrina completa** — proyección 20 años del escenario elegido; TIR proyecto (unlevered) vs TIR financiador **etiquetadas y separadas**; bruto titular + neto de disponibilidad al lado.
6. **Arquitectura webapp** — una hoja = un módulo: INPUTS→formulario, BILLS→grid validado, RATES+CALC→motor, REGIMEN→motor de reglas, RESULTADOS→dashboard, FINANCE→financiero. Sin macros, sin solver, sin hojas muertas (la v1 tenía 40+ hojas, 756 filas de leasing inactivo y un literal congelado).

## Validación (engine-derived)

| Check | Resultado |
|---|---|
| Recalc LibreOffice | 1,209 fórmulas, **0 errores** |
| Híbrido demo vs golden | **$7,083,252.47** — exacto al centavo (PV $787,522.28, dem $5,590,209.47, arb $790,048.75, claw −$84,528.03) |
| TIR proyecto / financiador | 34.87% / 14.97% — igual al engine v2 |
| 12 recibos demo | Check "OK" los 12 (±<0.5%) |
| PV-only / BESS-only | $778,203 / $6,305,050 (espejo python idéntico) |
| Test régimen kWp=1000 | caps activos (80% acreditable, 360,053 kWh excedentes a $0), híbrido $9,506,213.43 = espejo exacto |
| Test división BC | horas punta correctas (may–oct 4h, invierno 0), 0 errores |

## Sources consulted
- [[2026-06-11-780881200029-calculadora-audit]] — set de fórmulas corregido (base del motor)
- [[demanda-facturable]], [[gdmth-bill-structure]], [[horarios-y-divisiones]] — mecánica de cobro
- [[pv-savings-model]], [[bess-savings-model]], [[pv-bess-combined]] — palancas
- [[medicion-neta]], [[autoconsumo]], [[scheme-comparison]], [[generador-exento]], [[sae-cc]] — caps y obligaciones

## Confidence
**High** para el motor GDMTH SIN (golden-validado al centavo). **Medium** para los caps de autoconsumo: el % de autoconsumo instantáneo es **supuesto** (sin datos 15-min) y la mecánica de créditos <0.7 MW bajo LSE 2025 sigue sin re-confirmar ([[overview]] gaps). **Low** para divisiones no-SIN (tarifas no-SIN = gap abierto; PV-en-punta de BC/BCS no acreditado = conservador). Niveles: recibos = fuente primaria; ahorros = derivados; % autoconsumo, rendimiento municipal y curva intradía = supuestos.
