---
title: "MC-GEPP-4SITIOS-2026-07 — Memoria de cálculo y razonamiento, Propuesta PV+BESS GEPP 4 sitios"
type: analysis
tags: [gepp, memoria-de-calculo, pv, bess, autoconsumo, medicion-neta, gdmth, dist, sizing, ppa, 2026]
created: 2026-07-07
updated: 2026-07-07
sources: [2026-06-10-perfil-consumo-gepp-2025-26, 2026-06-09-autoconsumo-cne-2025, 2026-06-04-res142-2017-gen-dist, 2026-06-04-ley-sector-electrico-2025]
---

# MC-GEPP-4SITIOS-2026-07 — Memoria de cálculo

> **ID citable: `MC-GEPP-4SITIOS-2026-07`.** Razonamiento completo detrás de
> `entregables/propuestas/GEPP - Propuesta PV+BESS 4 Sitios (2026-07).xlsx` (que incluye esta memoria
> como hoja homónima). Elaborada 2026-07-07 con sign-off del usuario en 3 checkpoints (A regulatorio,
> B sizing, C financiero — C delegado a recomendaciones del modelo).

## 1. Marco regulatorio verificado (Checkpoint A, aprobado)

- **GD / Generador Exento <0.7 MW** por punto de interconexión, sin permiso (Art. 30 LSE, DOF 18-mar-2025).
  Tope de trabajo acordado: **839.45 kWp DC con <700 kW AC** (DC/AC ≈1.20).
- **Medición neta** vigente vía RES/142/2017 (neteo por periodo, créditos 12 meses con conversión por ratio
  de tarifas, vencidos a PML). **Riesgo**: CNE tiene el marco "en actualización"; borrador previo (CONAMER
  2022, nunca publicado) eliminaba medición neta en MT para contratos nuevos, respetando firmados →
  **urgencia de firmar contratos de contraprestación**.
- **Autoconsumo ≥0.7 MW** (DACG CNE, DOF 12-dic-2025): permiso simplificado 0.7–20 MW (~4–8 meses);
  excedentes **sin contraprestación** (base conservadora del modelo) o venta exclusiva a CFE; los excedentes
  **pueden almacenarse en SAE (Num. 4.4)**; respaldo obligatorio para intermitentes (Num. 4.5) — **el BESS
  cumple ese requisito de paso**. BESS aparte bajo SAE-CC (A/113/2024): sin permiso, aviso 90 días hábiles.
- Decisión aprobada: Proplasa tiene 3 servicios (PR1/PR2/TAP) en un predio → **3 puntos de interconexión =
  3 plantas GD <0.7 MW sin ningún permiso** (plantas eléctricamente separadas detrás de cada medidor).

## 2. Baseline (12 meses reales may-25 → abr-26)

- Fuente: `raw/Perfil de Consumo Eléctrico GEPP 2025-26 (1).xlsx`. Estructura clave: cada hoja de planta
  trae el año 2026 en cols 1–15 y **2025 en cols 18–32**; bloques Total Planta / CFE / TALA-ENEL.
  `Total Recibo = Subtotal × 1.16` (IVA) → **todo el modelo es pre-IVA sobre Subtotal**.
- **Ixtlahuacán es tarifa DIST (Jalisco), no GDMTH** (sin cargo distribución; capacidad ~402–432 MXN/kW).
  Los demás: GDMTH (ACA Centro Sur, CAN Peninsular, PRO Valle de México Norte). Tarifas tomadas de la hoja
  `Tarifas` del propio workbook (validada por el import de junio: Cancún cuadra +0.12% vs recibo real).
- 12m: IXT 22.38 GWh/$52.1M · ACA 8.44/$27.1M · CAN 4.54/$15.2M · PR1 15.74/$31.8M · PR2 45.07/$108.9M ·
  TAP 29.07/$61.6M. Punta = 8.7–10.9% del kWh en todos.
- Anomalías IXT excluidas del sizing BESS: Dem.máx. may-25 7,310 kW y dic-25 5,731 kW (contratada 5,000).
- **Curva horaria sintética** (no hay 15-min): perfil embotelladora 24/7 — pesos 1.30 (7–19h), 1.15 (19–23h),
  ×0.85 domingos — distribuidos dentro de cada periodo tarifario SIN y **normalizados para reproducir
  exactamente los kWh mensuales B/I/P facturados**. PV = campana sinusoidal 6:30–19:00 normalizada al yield
  mensual municipal.

## 3. Sizing (Checkpoint B, aprobado)

- Módulo **Tongwei TWMNF-66HD715**: 715 Wp, 2.384×1.303 m (3.106 m²), η 23.0%, bifacial 80±5%,
  γ −0.28%/°C, degradación garantía ≤1% año 1 / ≤0.4% anual.
- **Densidad 4.0 m²/kWp** (estándar de casa Newman, confirmado por el usuario; el conservador sería
  6.2 m²/kWp = empaque 0.70 sobre 230 Wp/m² de módulo).
- Yields (índice geográfico municipal, validado vs Global Solar Atlas; Cancún ~5-10% conservador):
  IXT 1,783 · ACA 1,869 · CAN 1,500 · PRO 1,660 kWh/kWp·año.
- **Límite "sin exportar"** = kWp donde la exportación anual simulada llega a 2% (relevante en Autoconsumo,
  donde el excedente no se compensa): IXT 4,550 · ACA 1,618 · CAN 1,100 · PRO ~19,000 kWp.
- Aprobado: IXT Op1=4,550 kWp Autoconsumo / Op2=839 GD · ACA Op1=1,618 Auto (requiere ~3,025 m² extra) /
  Op2=839 GD · CAN Op1=1,100 Auto / Op2=839 GD · PRO Op1=3,849 (PR1+TAP GD, PR2 2,170 con permiso) /
  Op2=2,518 (3× GD sin permiso). Los 4 sitios son SIN: punta 20–22h verano / 18–22h invierno → **el PV no
  toca punta; la punta es del BESS**.
- **BESS** (regla confirmada por usuario): energía = potencia punta × **2h**, a 0.5C; potencia = promedio de
  Dem.máx. punta mensual (sin anomalías): IXT 3.7 MW/7.4 MWh · ACA 1.65/3.3 · CAN 0.98/1.96 ·
  PRO 11.8/23.6 (por medidor: PR1 1.96/3.9, PR2 5.97/11.9, TAP 3.86/7.7). En invierno (punta 4h) el BESS de
  2h rasura parcialmente — el modelo lo captura con MIN(E_util, P×h, kWh punta) por día.

## 4. Convenciones de cálculo (replican la casa Newman)

- Demanda facturable: **MIN(Dmáx, umbral)**, umbral = kWh/(24·días·**0.57**) — convención de la calculadora
  GEPP v5 y el simulador Fibrahotel (ingeniería inversa 2026-07-07, ver `scratchpad calculadora_reverse.md`
  de la sesión o la hoja PROJECT_INPUTS/DISPATCH del Fibrahotel6).
- Ahorro **capacidad → flujo BESS**; ahorro **distribución/umbral → flujo PV**. Ambos calibrados con la
  simulación horaria al tamaño de diseño y escalan linealmente con las celdas de entrada en el Excel.
- E_util BESS = kWh × DoD 0.96 × √RTE 0.96. Arbitraje = desplazado×tarifa punta − (desplazado/RTE)×tarifa base.
- Merma BESS: **2 meses/año sin ahorro** → factor 10/12.
- GD medición neta: toda la generación se valúa a tarifa del periodo (neteo). Autoconsumo: solo lo
  autoconsumido (excedente ≤2% no compensado; puede cargarse al BESS).

## 5. Finanzas (Checkpoint C, resuelto con recomendaciones)

- MXN nominal, pre-IVA, sin apalancamiento. **FX 17.55** (confirmado por usuario). Esc. CFE 6% / PPA 5%.
  Degr. PV 0.5%/año, BESS 1.25%/año. O&M 310 MXN/kWp / 180 MXN/kWh (esc. 6%, a cargo del inversionista).
  Plazo contratos 15 años; horizonte 20 (GEPP se queda 100% del ahorro años 16–20). WACC referencia 12%.
- **PV**: CAPEX inversionista = **0.65 USD/Wp** (precio venta; costo duro 0.50 = spread Newman). PPA resuelto
  por bisección para **TIR 14% a 15 años**: IXT 1.0492 · ACA 0.9810 (Op1 1.0010) · CAN 1.2227 (Op1 1.2476) ·
  PRO 1.1046 MXN/kWh. El PPA se factura sobre kWh entregados (autoconsumidos en Autoconsumo; generados en GD).
- **BESS**: CAPEX = **0.28 USD/Wh** instalado (0.18 FOB). **Hallazgo central: con participación 50/50 la TIR
  BESS queda en 8.1% (ACA) – 13.5% (PRO), no 16%.** Para TIR 16% el split requerido es 57% (PRO), 60% (IXT),
  66% (CAN), 72% (ACA) a favor del inversionista. Driver: el BESS 2h solo captura ~half de la ventana punta
  invernal de 4h, y la capacidad instalada (USD/Wh) pesa más que el ahorro anual por kWh en sitios con
  capacidad barata. Recomendación comercial registrada: negociar ~60/40 o repriciar.
- Resultado año 1 (recomendado: IXT Op1, ACA/CAN/PRO Op2): **ahorro neto GEPP ≈ $39.9M MXN/año** (~$84M
  bruto); CAPEX ≈ 5.7M USD PV + 10.1M USD BESS. Netos por sitio: IXT $11.3M (21.7%) · ACA $3.7M (13.5%) ·
  CAN $2.6M (17.1%) · PRO $22.3M (11.0%).

## 6. Validación del entregable

- Workbook generado 100% con openpyxl (gráficas incluidas — **nunca re-guardar con openpyxl: destruye las
  17 gráficas**; ediciones posteriores vía Excel/COM). Test-open + recálculo vía COM: celdas clave cuadran
  con la simulación Python <0.7% (TIR BESS +0.4 pp en Excel por agregación mensual vs diaria — aceptado).
- Pendientes explícitos: recibos reales de IXT may/dic-25; opinión legal autoabasto legacy (Tala −10% zafra,
  ENEL colapsado a ~16% en 2026, ambos vencen 2032) + GD simultáneos en el mismo centro de carga; descuento
  Tala no modelado (conservador en meses CFE).

## 7. Corrección del despacho día-típico (2026-07-07, sign-off PEPSI)

- **Hallazgo:** el despacho día-típico graficado (addendum del 2026-07-07) usaba una descarga BESS **voraz**
  (llena las primeras horas de punta y se vacía). En invierno (punta SIN 4h, 18–22h) dejaba la última hora sin
  rasurar; como CFE factura la **capacidad sobre el intervalo de punta más alto** ([[demanda-facturable]]), la
  ilustración mostraba una reducción de sólo ~222 kW (IXT) mientras la col Q (motor) sostiene ~1,740–1,908 kW.
- **Veredicto:** error de **ilustración**, no de números. Q y L son valores de la simulación horaria (§4) y ya
  asumen rasurado ~óptimo (plano); el motor y las finanzas (TIR/VPN/ahorros) quedan **intactos**.
- **Corrección** (Excel COM, preserva gráficas): despacho invierno → **rasurado plano** (descarga = MIN(P, E−nivel),
  nivel resuelve la energía útil repartida sobre las 4 h) + bloque de reconciliación *pico antes→después*;
  **despacho de VERANO** añadido (punta 2h → cubierta casi entera) con su gráfica; **columnas S–T** en el modelo
  mensual = demanda de punta facturable real mes a mes (Reducción = Q ÷ tarifa capacidad; Después = Dmáx − Reducción);
  headers L/Q → "(motor)" + nota de procedencia. **Ixtlahuacán = DIST** → umbral con **FC 0.74** (celda editable
  `O20`; resto GDMTH 0.57), sin impacto financiero (la Dmáx medida ata; el umbral no alimenta ninguna fórmula).
- **Entregables NUEVOS** (originales sin tocar): `GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev2 - Despacho
  flat-top + DIST.xlsx` y `GEPP - Propuesta Proplasa (3 sitios) (2026-07) rev2 - Despacho flat-top.xlsx`.
