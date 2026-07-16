---
title: "Automatización de la calculadora — auto-fill desde recibos CFE + webapp local"
type: analysis
tags: [automatizacion, calculadora, webapp, extraccion, pdf, cfdi-xml, solar-yield, build]
created: 2026-06-11
updated: 2026-06-11
sources: [2026-06-08-cfe-bills-780881200029-fy25-26, 2026-06-09-cfe-bills-456220800389-fy25-26]
status: vigente
---

# Automatización de la calculadora — auto-fill desde recibos CFE + webapp local

**Question:** ¿Cómo automatizar el llenado de variables de la calculadora desde recibos CFE (PDF o CFDI XML) e info del cliente — que el sistema detecte y llene solo? ¿Script, HTML, o backend?

## Answer

La extracción ya existía (`cfe_savings/extract.py` saca RPU, demanda contratada, CP, división, kWh/kW por periodo, importes MEM, FP y bonificación/cargo de ambos formatos). Lo que faltaba era el **cableado**. Se construyeron dos rutas que comparten un solo cerebro:

**Núcleo compartido — `tools/calc_core.py`.** El modelo mensual de la calculadora genérica ([[2026-06-11-calculadora-generica-pv-bess]]) como módulo python: 3 escenarios (PV/BESS/Híbrido), caps regulatorios (<0.7 MW [[medicion-neta]] / ≥0.7 MW [[autoconsumo]] con % autoconsumo por giro y excedentes a $0), claw-back de bonificación, alertas REGIMEN y finanzas etiquetadas (TIR proyecto vs financiador). Reusa `cfe_savings.defaults` (horas punta, días hábiles, festivos) y `cfe_savings.sizing` (propuestas PV/BESS) **read-only** — `engine.py` intocado, golden intacto. Validado: desde los PDFs crudos reproduce el golden **al centavo** (híbrido $7,083,252.48).

**Ruta A — `tools/fill_calculadora.py` (CLI).** `python tools/fill_calculadora.py raw/bills/<RPU>/ [--giro ... --kwp ...]` → valida el footing de cada recibo (`(MEM+FP)×1.16` vs impreso; **detiene** si >0.5%, doctrina), llena una copia `Calculadora - <RPU>.xlsx` con BILLS + RPU + demanda contratada + división + rendimiento solar municipal, e imprime los resultados esperados. El Excel sigue siendo la calculadora; el script solo teclea por ti.

**Ruta B — `tools/webapp/` (webapp local).** `python tools/webapp/server.py` → http://127.0.0.1:8765. Server stdlib-only (sin dependencias nuevas); arrastras PDFs/XMLs al navegador → chips de validación por recibo → inputs auto-detectados y editables (con botón de sizing propuesto) → alertas de régimen → tarjetas de los 3 escenarios + corrección FP separada → tabla titular mensual + finanzas. **Los recibos nunca salen de la máquina** y los bytes crudos nunca tocan contexto LLM.

**Cadena de auto-detección:** RPU y demanda contratada del recibo; CP (campo nativo en XML, regex en PDF) → `tools/solar_lookup.py` → municipio/estado (`codigo_postal.csv`) → rendimiento **mensual** kWh/kWp (`Solar_index_geografico.csv`, fallback promedio estatal) → división (BC/BCS por estado, resto SIN). Lo que nunca se adivina: giro, área de techo, deal terms.

**Por qué no la opción C (HTML puro sin backend):** exigiría re-portar extractor y motor a JavaScript — dos codebases que el golden test no puede guardar a la vez. La webapp local mantiene un solo origen de la verdad en python; cuando se hostee, el mismo `calc_core` se expone tras un API real.

## Validación (engine-derived)

| Check | Resultado |
|---|---|
| calc_core vs golden (PDFs crudos 780881200029) | híbrido $7,083,252.48; arb $790,048.75; TIR 34.87%/14.97% — al centavo |
| fill 780881200029 (PDF) | 12/12 recibos cuadran ±0.000%; CP 77500 → Benito Juárez, QRoo, 1,500 kWh/kWp |
| fill 456220800389 (CFDI XML) | CP 47730 → Tototlán 1,831 kWh/kWp; Excel recalc 0 errores; Excel = core al centavo en los 3 escenarios (HIB $4,491,708.94); cargo FP $874,974 detectado; régimen autoconsumo dispara a 700 kWp |
| webapp endpoints | /api/parse + /api/run reproducen los mismos números; propuesta sizing 699 kWp / 849 kW / 3,397 kWh (pico punta × ventana) |

## Contradictions / tensions
- `cfe_savings/defaults.py` da punta BC en **abr–oct**; [[horarios-y-divisiones]] dice verano BC = **may 1–oct**. Divergencia menor (solo abril BC), sin sitio BC activo. Reconciliar antes del primer cliente BC.

## Sources consulted
- [[2026-06-11-calculadora-generica-pv-bess]] — el modelo que este build automatiza
- [[solar-yield-lookup]], [[2026-06-07-codigo-postal]], [[2026-06-07-solar-index-geografico]] — la cadena geográfica
- [[medicion-neta]], [[autoconsumo]], [[scheme-comparison]] — caps; [[demanda-facturable]], [[bess-savings-model]] — motor

## Confidence
**High** en extracción y motor (golden al centavo, dos clientes reales, dos formatos). **Medium** en CP-sniff de PDFs (regex best-effort — el XML lo trae nativo) y en el rendimiento municipal (prefactibilidad; Helioscope lo sobreescribe). Supuestos siguen siendo supuestos: giro→% autoconsumo, curva intradía.
