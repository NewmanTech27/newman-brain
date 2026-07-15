# DESIGN — Modelo "BESS Carga Solar" (GEPP rev4)

**Fecha:** 2026-07-14 · **Estado:** spec aprobada internamente, pendiente aprobación del usuario sobre el producto final.
**Objetivo:** nueva variante del modelo GEPP donde el BESS se carga PRIMERO con excedente solar y sólo el faltante se carga de red en horario base; descarga idéntica (rasurado plano en punta). Entregables: 2 libros nuevos (rev4) + 1 deck HTML nuevo con el "Despacho de un día típico" rediseñado. Nada de lo entregado se sobrescribe.

---

## 1. Hechos de referencia (verificados por scouting 2026-07-14)

- **Libros de referencia** (NO tocar): `work/gepp-deck/GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev3 - Esc 4pct TIR 14.xlsx` y `...Proplasa (3 sitios)...rev3...xlsx`. 7 hojas de sitio estructuralmente idénticas.
- **Deck de referencia** (NO tocar): `work/gepp-deck/gepp_v7.html` (vivo). Pipeline: xlsx →(`extract_tir14.py`)→ `gepp_data_tir14.json` →(regex splice `const MODEL = {...};`)→ html. Gate mecánico: `domstub_v7.js`. Screenshots: patrón `shots_v7.py` (Playwright chrome-headless-shell, ya instalado).
- **Motor mensual del libro** (por hoja de sitio, Op1 filas 59-72, Op2 filas 76-89, cols B..T):
  - N (`=MIN($C$30*B$11, $C$28*B$12*B$11, B$7)`) = kWh desplazados a punta — VIVA, no cambia.
  - **O (`=N/Supuestos!$B$14*B$14`) = costo de carga en base — ESTA es la celda que el nuevo modelo reemplaza** (O60:O71, O77:O88).
  - P `=N*t_punta−O`, R `=P+Q`, R72/R89 total anual, C44 `=R72*(12-merma)/12`, C52 `=IRR(N94:N114)`, C55 ArrayFormula NPV — todas VIVAS, recalculan solas.
  - Q (capacidad) = coeficiente horneado × `MIN(1,$C$30/E_diseño)` — NO cambia (la descarga es idéntica).
  - D/E/F (%Base/%Int/%Punta de la generación) = VALORES inyectados; C col `=$C$26*B$21` (kWp×yield) VIVA; K `=G+H+I` alimenta el pago PPA.
  - Despacho día típico DENTRO del xlsx: filas 150-184 (invierno) y 186-219 (verano). Col C carga y col D pv = estáticas; col F carga BESS = constante `−(C29·DoD/√RTE)/6` en horas 0-5; col G descarga = rasurado plano vivo (`E180`/`E216`); col E `=C−D`, col H `=E−F−G` vivas.
- **Hallazgo clave:** con los kWp actuales, `pv` NUNCA excede `carga` en ninguna hora de ningún sitio (autoconsumo 95-99.9%). **El excedente solar sólo existe si se amplía el PV** — exactamente el "Rung 1" ya validado por el motor en `wiki/analyses/2026-07-14-gepp-pv-upsize-solar-charged-bess.md`:
  - Ixtlahuacán 4,550 → **5,170 kWp** · Acapulco 1,618 → **1,748 kWp** (tope superficie) · Cancún 1,100 → **1,270 kWp** · Proplasa/Preformas/Tapa **sin cambio** (superficie 100% usada).
- **Ventanas SIN** (`wiki/billing/horarios-y-divisiones.md`): verano L-V punta 20-22; invierno L-V punta 18-22 y sábado 19-21; 22-24 = Intermedio; domingo/festivo sin punta. Sólo hay ciclo BESS en días con punta.
- **Valor del excedente PV:** Op1 autoconsumo → `texc ≈ $0` (venta a CFE a mayorista). Op2 medición neta → crédito ≈ tarifa del periodo (t_int de día; el excedente dominical cae en base). El costo de oportunidad de cargar el BESS con excedente depende del esquema.
- **Convención de energía del libro:** `E_útil = C29·DoD·√RTE` (C30); energía de carga = `N/RTE`. Mantenerla exactamente.
- **Datos GEPP:** sólo mensuales B/I/P (imported/gepp-*/bills.json). Forma intradía = curva de giro (`tools/load_curves.py` CURVES/WINDOWS/day_counts) + campana solar `PV_BELL`. Escalado mensual→horario: receta de `autoconsumo_pct` (load_curves.py:186-192). Prefactibilidad, no bancable — decirlo en el pie.

## 2. Regla de despacho (la lógica nueva)

Por sitio, por mes `m`, por tipo de día (sólo días CON punta ciclan):

1. Curvas horarias: `load[h]` = curva de giro escalada al kWh del mes; `pvS[h]` = campana solar escalada a `gen_m = kWp_new × yield_m`, distribuida uniforme entre los días del mes.
2. `exceso[h] = max(0, pvS[h] − load[h])` (sólo existe con el PV ampliado).
3. Energía a cargar del día: `C_day = N_day / RTE`, con `N_day = N_m / días_punta_m` (N del libro, fórmula intacta).
4. **Prioridad de carga:** primero excedente solar de las horas de sol (limitado por potencia `C28` por hora y por `Σ exceso` del día); el faltante `C_day − carga_solar_day` se carga de red en horas base 0-5 (plano, como hoy).
5. Descarga: idéntica al libro (rasurado plano en punta, fórmulas G intactas).
6. Agregación mensual: `carga_solar_m`, `carga_base_m` (con `carga_solar_m + carga_base_m = N_m/RTE`), `exceso_m`, `exceso_remanente_m = exceso_m − carga_solar_m`.

**Economía (columna O nueva y ajuste de J):**
- `O_new = carga_base_m·t_base_m + carga_solar_m·c_oport` donde `c_oport = texc ≈ 0` (Op1) / `≈ t_int` (Op2; en la práctica Op2 casi no tiene excedente por el tope 0.7 MW — el modelo lo resuelve solo).
- El PV ampliado genera más kWh: los consumidos en sitio se valoran a tarifa de periodo (como hoy vía D/E/F·J); el **excedente remanente** se valora a `texc`. J debe descontar el excedente para no sobrevalorar: mantener D+E+F = 1 (K/pago PPA paga sobre TODA la generación) y restar en J el ajuste `Σ_periodo exc_per·(t_per − texc)` con el excedente ya usado para carga excluido (ese se paga en O). **Sin doble conteo**: cada kWh de excedente está en exactamente una de tres cubetas: cargado al BESS (costo en O), remanente a texc (ajuste en J), o no existe.
- Identidad de verificación anual por sitio: `Δbeneficio vs rev3 ≈ (ahorro por carga solar evitando base) + (beneficio PV incremental del upsize) − (excedente remanente valorado a diferencia de tarifas)`.

**Implementación en el libro:** insertar las cantidades nuevas como columnas VALOR adicionales a la derecha del bloque (U: Exceso solar kWh, V: Carga solar BESS kWh, W: Carga base kWh, X: Ajuste excedente $ — o el layout mínimo equivalente que el implementador juzgue más limpio), y reescribir O y J como fórmulas VIVAS que las referencien (p.ej. `O60 = W60*B$14 + V60*<c_oport>` y `J60 = G60*B$14+H60*B$15+I60*B$16 − X60`). Actualizar la nota de la fila 73 describiendo el despacho carga-solar. Todo lo demás (P,R,S,T, totales, C44-C55, proyección 94-139, Resumen, Supuestos) queda vivo e intacto. Preservar la ArrayFormula de C55/D55.

## 3. Cambios de dimensionado y precio

- `C26` (kWp Op1): ixt 5170 · aca 1748 · can 1270 · Proplasa book sin cambio. `D26` (Op2) SIN cambio (tope GD 0.7 MW).
- CAPEX PV, superficie, generación: recalculan vivos desde C26.
- **PPA:** re-resolver el multiplicador k (metodología idéntica a `solve_tir14.py`) para TIR inversionista combinada = 14.0% por opción, ahora sobre el motor nuevo. Reportar k_old vs k_new y el precio PPA resultante por sitio. (Doctrina: los términos del deal se RESUELVEN, no se asumen.)
- Participación BESS se mantiene 0.5; reportar el TIR BESS resultante (subirá — la carga solar abarata el ciclo). NO retunear sin aprobación.
- L (ahorro distrib/umbral): escala vivo con el ratio de kWp en la fórmula M existente — aceptable a este nivel; documentar.

## 4. Despacho día típico (xlsx filas 150-219 y chart del deck)

- Col D (pv): escalar la curva estática por `kWp_new/kWp_old` (misma técnica que usa `renderDesp` para Op2).
- Col F (carga BESS): nueva colocación — en horas con `exceso>0` cargar `min(exceso[h], C28, faltante)` (VALORES o fórmula, a juicio del implementador manteniendo consistencia), y el faltante repartido plano en horas 0-5 como hoy. Etiquetas del chart: "CARGA SOLAR" (mediodía) y "CARGA BASE" (madrugada, sólo si hay faltante).
- Cols E, G, H: fórmulas vivas intactas (recalculan).
- Deck `renderDesp`: el carril BESS ya es genérico para cualquier bloque contiguo; actualizar el relleno explicativo y el copy que hoy dice "BESS cargando · horario base" → versión solar ("BESS cargando · excedente solar" con la banda entre pv y carga durante la carga solar; banda base sólo si existe faltante). Actualizar los pies de sección y la página Cobertura (el "Rung 2" deja de ser supuesto: ahora es motor). Framing positivo (sin "problemática/merma" en copy visible; mostrar "Inversión estimada Newman").

## 4b. Sección nueva del deck: "¿Y con más superficie?" (selector por sitio)

Requerimiento del usuario (2026-07-14): el deck debe incluir un **selector por sitio** que muestre (a) cuántos m² se necesitan para el PV de **máximo ahorro posible** (óptimo SIN tope de superficie, con el BESS fijo y el despacho carga-solar), y (b) **cuánto dinero adicional** ahorrarían si esos m² estuvieran disponibles (vs el diseño rev4 topado por superficie).

- Motor: barrido de kWp por sitio (Op1, BESS fijo, despacho carga-solar, paso ≤50 kWp, hasta bien pasado el óptimo) → curva kWp → {ahorro cliente año1, VAN 20a, exceso remanente}. Óptimo = máximo ahorro neto cliente año1 (reportar también el máx-VAN si difiere). m² = kWp × Supuestos!B24 (4.0 m²/kWp). Emitir en `motor_cs.json` como `sweep_superficie` por sitio: la curva + óptimo + delta vs diseño rev4 + m² disponibles hoy (tabla SITIOS de Supuestos) + m² faltantes.
- Deck: sección nueva con tabs por sitio (patrón `makeSiteTabs`) mostrando: m² requeridos vs disponibles, kWp óptimo vs diseño, ahorro adicional $/año (y VAN) si la superficie existiera, y una mini-curva ahorro-vs-m² con el punto de diseño y el óptimo marcados. Framing positivo ("potencial adicional con más superficie"), pie con la caveat de prefactibilidad.

## 5. Verificación (gates obligatorios)

1. **Réplica modo-viejo:** con kWp_old y carga solar deshabilitada, el motor nuevo reproduce R72 y C52 de los rev3 a <0.1% en las 7 hojas.
2. **Identidades de energía:** por mes: `V+W = N/RTE`; `V ≤ U`; `N ≤ min(E_útil·días, P·hrs·días, kWh_punta)`; ciclos ≤ ~1/día.
3. **Sanidad libro:** abrir con openpyxl, recalcular con LibreOffice headless (`soffice --convert-to xlsx --calc`) o `formulas` lib y verificar C44/C52/C55 contra el cálculo Python a <0.5%.
4. **Domstub gate** del deck nuevo (sin NaN/undefined, todas las combinaciones sitio×OP×temporada).
5. **Screenshots** del despacho (invierno+verano, 2-3 sitios) y de Resumen/Cobertura para el paquete de aprobación.
6. **NO tocar:** `tools/cfe_savings/` (golden intacto — la formalización al engine es fase post-aprobación), archivos rev3/v7 entregados, `raw/`, wiki (hasta aprobación).

## 6. Nombres de salida (en `work/gepp-carga-solar/`)

- `GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev4 - Carga Solar TIR 14.xlsx`
- `GEPP - Propuesta Proplasa (3 sitios) (2026-07) rev4 - Carga Solar TIR 14.xlsx`
- `gepp_data_cs.json` · `gepp_cs_v1.html` (título "Solución Energética v8 — GEPP · Carga Solar") · `shots/` · `dispatch_cs.py` (el simulador) · `build_books_cs.py` · `build_deck_cs.py` · `REPORT.md` (números clave y deltas vs rev3)
