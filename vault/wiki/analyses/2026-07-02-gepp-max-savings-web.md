---
title: "GEPP — configuración max-ahorro por sitio + economía del deal (web report)"
type: analysis
tags: [gepp, pv, bess, sizing, ppa, deal, reporte]
created: 2026-07-02
updated: 2026-07-02
sources: [2026-06-10-perfil-consumo-gepp-2025-26]
cliente: gepp
status: vigente
---

# GEPP — configuración max-ahorro por sitio + economía del deal (web report)

**Question:** ¿Qué configuración PV+BESS maximiza el ahorro de GEPP manteniendo buena nuestra rentabilidad (financiador), y cómo se presenta por sitio y en conjunto? Ejecuta los tres pendientes del log 2026-06-19: horas BESS año-completo, economía de ahorro compartido, y entregable navegable.

## Answer

Sobre los 12 meses reales de 2025 (`imported/gepp-*`), yields por municipio (fix del default plano 1,740), PV topado al exento 839.41 kWp DC = 0.7 MW AC, barrido BESS 0–5 h a potencia de pico de punta, FP en ACA/CAN, deal vía `ppa_pricer`:

| Sitio | Sistema | Ahorro año 1 (bruto) | CAPEX | NPV / TIR compra | Deal @18% fin. | Cliente año 1 @18% |
|---|---|---|---|---|---|---|
| Cancún | 839 kWp + 1,002 kW/2,004 kWh + FP | $6.24M (41.9%) + FP $0.60M | $20.9M | $35.4M / 30.1% | PPA $2.82 + com 50% | $1.39M |
| Acapulco | 839 kWp + 1,609 kW/3,218 kWh + FP | $8.43M (32.0%) + FP $1.72M | $26.9M | $43.6M / 29.6% | PPA $1.80 + com 70.4% | $1.93M |
| Ixtlahuacán | 839 kWp + 4,233 kW/8,466 kWh | $16.93M (31.7%) | $52.7M | $75.3M / 27.8% | PPA $1.80 + com 73.5% | $3.41M |
| Proplasa PR1 | 839 kWp + 1,795 kW/3,590 kWh | $9.54M (26.1%) | $28.7M | $47.1M / 29.9% | PPA $1.80 + com 62.0% | $2.26M |
| Proplasa PR2 | 839 kWp + 6,104 kW/12,208 kWh | $26.55M (24.4%) | $71.0M | $125.1M / 31.2% | PPA $1.80 + com 62.5% | $7.17M |
| Proplasa TAP | 839 kWp + 3,936 kW/7,872 kWh | $18.19M (25.5%) | $49.7M | $87.5M / 31.2% | PPA $1.80 + com 61.7% | $4.86M |
| **Portafolio** | **5.04 MWp + 18.68 MW / 37.36 MWh (2h) + FP** | **$85.9M (27.6%) + FP $2.31M** | **$249.9M + $1.5M cap.** | **$413.9M / 27.8–31.2%** | — | **$21.0M (+FP = $23.3M)** |

**Hallazgos clave (engine-derived):**
1. **Horas BESS resueltas: 2 h en LOS SEIS sitios** (pendiente "¿2.5–3h?" del 19-jun). Con año completo, la ventana de verano (2h, may–oct) domina; el óptimo 4h previo era sesgo de invierno. BESS total 37.4 MWh vs 72 MWh del run de 4h — mitad de CAPEX de batería con NPV superior ($414M vs $343M del run anterior).
2. **Deal re-estructurado por doctrina de vendibilidad:** resolver el PPA con comisión fija 50% daba PPA > blend CFE en sitios BESS-dominantes (IXT $3.82 vs blend $2.41 — invendible). Estructura correcta: **PPA fijo $1.80/kWh** (bajo el intermedio en todas las divisiones, 15a esc 5%) y **resolver la comisión BESS** → 62–73% @18%. Cancún es la excepción (palanca PV-dominante vía umbral): comisión no alcanza y se resuelve el PPA → $2.82 (bajo su blend $3.13).
3. **Ahorro compartido:** GEPP año 1 = $23.3M (incl. 100% FP) @ financiador 18%; $31.1M @ 14%; años 16–20 (post transferencia PV) 100% GEPP. VPN financiador @18% $96.4M.
4. **Cruzar 0.7 MW sigue sin pagar** en ningún sitio (BESS obligatorio + retraso permiso CNE ~1 año): el punto 840 kWp cae $6–25M de NPV vs 839.41 en todas las curvas.
5. **Yields corregidos por municipio:** CAN 1,500 · ACA 1,869 · IXT 1,783 · Cuautitlán Izcalli 1,660 kWh/kWp (antes: plano 1,740 los seis).
6. **Mismatch de etiquetas motor↔regla exento:** `calc_core` marca ≥700 kWp DC como autoconsumo (alertas CNE/respaldo); la regla vigente es 0.7 MW AC = 839.41 kWp DC. Sin efecto numérico (100% acreditado, excedentes ≈ 0); las alertas se sustituyen en el reporte. Pendiente: propagar la regla AC↔DC a `calc_core._regimen`.

**Entregables:** `entregables/reportes/GEPP - Solucion Energetica Web.html` (webpage autocontenida: overview + tab por sitio, curvas de dimensionado, deal, alertas, caveats; también publicada como Artifact) · `entregables/reportes/gepp_max_savings_data.json` · `tools/gepp_max_savings_sweep.py` (regenera datos) · `tools/make_gepp_web_report.py` + `tools/gepp_web_report_body.html` (regeneran la página).

**Relación con v3:** [[2026-06-15-gepp-v3-audit-rebuild]] sigue vigente como caso curado con PV grande (16 MWp cruzando 0.7 MW, techo real Proplasa) y ancla "Tarifa Actual" del workbook. Este análisis es la línea max-NPV/exento del sweep sobre 2025 año-completo; la reconciliación v3↔sweep (áreas de techo reales + tratamiento autoabasto) sigue abierta.

## Sources consulted
- [[2026-06-10-perfil-consumo-gepp-2025-26]] — dataset base (workbook 2025)
- [[2026-06-15-gepp-v3-audit-rebuild]] — doctrina del deal (PPA 15a + transferencia, capacitores al financiador, decomposición Tala/ENEL)
- [[pv-bess-combined]], [[bess-savings-model]], [[demanda-facturable]], [[medicion-neta]], [[generador-exento]], [[sae-cc]] — mecánica
- [[solar-yield-lookup]] — yields por municipio

## Confidence
Medium — motor determinista (golden 18/18) sobre reconstrucción validada del workbook (engine-derived), pero: forma de carga modelada (no 15-min) → el recorte de punta del BESS (≈2/3 del valor) es prefactibilidad; áreas de techo sin confirmar (proxy 4,938 m²); IXT medido vs CFE pleno (beneficio neto ~$2.7M/año menor mientras viva Tala, hasta 2032); tarifas 2025 constantes hacia adelante (assumption).
