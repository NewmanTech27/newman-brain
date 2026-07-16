---
title: "Perfiles de Carga — curvas de consumo por industria, fit vs recibos y traslape solar"
type: concept
tags: [perfiles, curva-de-carga, industrias, horarios, punta, autoconsumo, fit, modelado]
created: 2026-06-11
updated: 2026-06-11
sources: [2026-06-04-gdmth, 2026-06-04-acuerdo-a158-2024]
---

# Perfiles de Carga — curvas de consumo por industria

Libreria de curvas horarias de consumo de 7 dias (lun-vie / sabado / domingo+festivo, 24 valores cada una) por giro industrial, superpuestas a las ventanas horarias de CFE ([[horarios-y-divisiones]]: division x temporada x tipo de dia) para producir el **reparto modelado de energia %B/%I/%P de cualquier mes** — y compararlo contra el reparto real impreso en los recibos. Implementada en `tools/load_curves.py`; consumida por `tools/calc_core.py`, la webapp y `fill_calculadora.py`.

**Las curvas son SUPUESTOS** (formas tipicas documentadas, no mediciones). Datos de intervalo 15-min las reemplazan y hacen el resultado bancable. Festivos se tratan con horario de domingo (los 7 estatutarios del engine).

## How it works

1. **Curvas** — 6 giros: Hotel/Turismo (pico vespertino, base nocturna alta, opera 7 dias), Industrial 24/7 (casi plana, leve joroba diurna), Industrial 1 turno (7-17h, sabado medio dia), Comercial/Retail (9-21h, fuerte en fin de semana), Oficinas (8-18h, fin de semana vacio), Otro (plana neutral).
2. **Ventanas** — codificadas las 6 combinaciones (SIN/BC/BCS x verano/invierno) con los 3 tipos de dia, incluyendo: punta sabatina de invierno SIN (19-21h), BC/BCS invierno sin punta, BC/BCS verano sin base. Temporada aproximada a mes completo (SIN/BCS: abr-oct; BC: may-oct segun wiki — ver tension abajo).
3. **Fit** — para cada giro, MAE promedio entre reparto modelado y real (kWh B/I/P del recibo) sobre los meses disponibles; ranking + mejor ajuste. MAE > 8% = ninguna curva representa al cliente (alerta, no se confia el derivado).
4. **Traslape solar** — % autoconsumo instantaneo derivado: curva escalada al kWh del mes vs campana solar (seno 7-19h) escalada a la generacion del mes; min() horario sobre la semana → fraccion del PV consumida al instante. **Dependiente del tamano**: mas PV → menor %. Alimenta el cap de [[autoconsumo]] (>=0.7 MW) en calc_core; el override manual siempre gana.

## Validacion contra recibos reales

| Cliente | Mejor ajuste | MAE | Leccion |
|---|---|---|---|
| 780881200029 (hotel Cancun) | Industrial 24/7 (0.5%) — Hotel/Turismo 3o (2.5%) | excelente | la carga real es mas plana que la curva estilizada de hotel; el fit elige por evidencia, no por etiqueta (leccion del error I8 del [[2026-06-11-780881200029-calculadora-audit|audit]]) |
| 456220800389 (industrial Tototlan) | ninguno (mejor 12.3%) | pobre | el sitio corre punta-pesado (30% de la energia en ventana punta); la libreria no lo representa → alerta + pedir datos 15-min |

## Related concepts
- [[horarios-y-divisiones]] — la fuente de las ventanas
- [[autoconsumo]] — el % derivado alimenta su cap de acreditacion
- [[pv-savings-model]] / [[bess-savings-model]] — los modelos que consumen el reparto
- [[2026-06-11-calculadora-generica-pv-bess]] / [[2026-06-11-automatizacion-calculadora]] — donde vive

## Open questions
- **Tension BC**: `cfe_savings/defaults.py` usa abr-oct para punta BC; el wiki dice verano BC = may-oct. load_curves sigue al wiki; reconciliar antes del primer cliente BC.
- La campana solar es fija (seno 7-19h); un perfil por latitud/estacion mejoraria el traslape.
- Curvas faltantes deliberadamente (usuario eligio 6): Industrial 2 turnos / vespertino — exactamente el perfil que Tototlan sugiere; agregar cuando haya un segundo sitio punta-pesado.
