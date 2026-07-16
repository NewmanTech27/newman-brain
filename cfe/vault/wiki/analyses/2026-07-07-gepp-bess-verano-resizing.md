---
title: "GEPP — Redimensionado BESS a punta de verano (2h): actual vs verano-2h vs eficiente-12%"
type: analysis
tags: [gepp, bess, sizing, capacidad, tir, proplasa]
created: 2026-07-07
updated: 2026-07-07
sources: []
cliente: gepp
status: vigente
---

# GEPP — Redimensionado BESS a punta de verano (2h)

**Question:** El usuario pidió modelar el BESS de los libros rev2 (4 Sitios + Proplasa 3 sitios) dimensionado a la punta de VERANO (2h de demanda punta promedio) en vez de —según su premisa— las 4h de invierno, comparar ambos escenarios (TIR inversionista, ahorro cliente, salud del sistema) y corregir los libros si tenían errores.

## Answer

### La premisa se invierte (tier b, motor)
El BESS rev2 ya es **0.5C / 2 horas en los 4 sitios** (P = E/2 exacto). En Ixtlahuacán y Proplasa el tamaño actual ≈ la regla verano-2h pedida (7,400 vs 6,900 kWh; 23,574 vs 22,900). Los sobrados reales son **Acapulco (−27%)** y **Cancún (−24%)**. En invierno la energía se reparte en rasurado plano 4h (reducción = E_útil/4); en verano cubre la punta 2h casi completa (reducción = min(D, E_útil/2)) — cada kWh vale el doble por hora de bloque en verano, por eso el kWh marginal "de invierno" es el que muere financieramente.

### Escenarios (portafolio 4 sitios, BESS @50/50, 15a, merma 2m, esc 5%)
| Escenario | E (kWh) | CAPEX | Bruto a1 | TIR inv por sitio | VAN inv @12% | Cliente a1 | VAN cliente 20a |
|---|---|---|---|---|---|---|---|
| A actual | 36,232 | $178.0M | $56.5M | 7.2–12.6% | **−$3.0M** | $28.2M | $301.1M |
| B verano-2h | 33,700 | $165.6M | $54.1M | 10.7–12.7% | **+$3.9M** | $27.1M | $288.8M |
| C eficiente-12% | 27,400 | $134.6M | $45.6M | 11.2–13.3% | +$9.8M | $22.8M | $243.4M |

- **B (recomendado):** Ixt 3,450 kW/6,900 kWh · ACA 1,200/2,400 · CAN 750/1,500 · PRO 11,450/22,900 (P1 2,020/4,040 · P2 5,670/11,340 · Tapa 3,760/7,520). El cliente cede ~4% del beneficio BESS ($1.16M/año); el inversionista pasa a VAN positivo. TIR: ACA 7.2→10.7, CAN 9.3→12.4, Ixt 11.4→11.9, PRO 12.6→12.7.
- **C (frontera, no recomendado):** máximo tamaño con kWh marginal ≥12%; sacrifica $45M de VAN cliente por ~$6M de VAN inversionista. En **Acapulco ningún tamaño alcanza 12% a 50/50** (tope ~11.2%) — ahí la palanca es el split (~63/37 p/ TIR 16% aun en B), no el tamaño.
- **Salud:** ambos sanos (LFP 0.5C, ≤1 ciclo eq./día, DoD 96%); B cicla ~8% más (~255–265 ciclos/año), dentro de warranty 6,000–8,000.
- A nivel PROYECTO (bruto total vs CAPEX) el kWh marginal del tamaño A aún rinde ~18% — el tamaño grande crea valor sistémico; es el split 50/50 el que lo hace VAN-negativo para el financiador. Alternativa a recortar: renegociar split y conservar A.

### Errores encontrados y corregidos en los libros existentes (in place)
1. **Escalación CFE 6% stale** en los libros Proplasa (3-sitios + 3 individuales), contra la doctrina 5% (2026-07-02) y contra su libro hermano 4-Sitios: TIR BESS reportada 13.49% → real 12.59%. Corregido Supuestos!B9.
2. **"Participación req. p/ TIR 16%" (C53) stale** en los 7 sheets (calculadas en la era 6%; en los libros Preforma incluso copiadas del agregado). Recalculadas @5% con los flujos exactos del libro (mi réplica reproduce IRR(N94:N114) a 0.000pp): Ixt 60.9%, ACA 73.7%, CAN 66.9%, PRO 57.7% (tamaño A).
3. **Preforma 1: ahorro de capacidad físicamente imposible** — la reducción implícita del motor prorrateado (1,956 kW) excede la Dem. máx. punta impresa (1,654 kW). Aplicado cap Q ≤ tarifa_cap × D_punta: −$0.62M/año, TIR 12.6→10.8%. **Inconsistencia de datos de origen**: los kWh punta del Perfil implican carga media en punta > demanda máxima reportada (mayo P1: 2,035 kW medios vs 1,654 máx — imposible). El agregado Proplasa es consistente; el split por medidor no. **Pedir recibos CFE por medidor.** El arbitraje usa esos mismos kWh punta — si están inflados, el arbitraje de P1 también lo está (no corregible sin recibos).

### Entregables
- `GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev3 - BESS verano 2h.xlsx` — tamaños B; **columna Q ahora fórmula viva trazable** `tarifa_cap × MIN(D_punta, E_útil/horas_bloque(fila 22), P)` (verificada ±0.07% vs motor al tamaño de diseño; exacta a cualquier tamaño); carga del despacho `=−E_útil/RTE/n` (antes constante); D28/D29=C28/C29.
- `GEPP - Propuesta Proplasa (3 sitios) (2026-07) rev3 - BESS verano 2h.xlsx` — pro-rata del agregado; Q conserva escalado lineal anclado al motor (conservador) + cap físico P1.
- `GEPP - Comparativo BESS actual vs verano-2h (2026-07).xlsx` — autónomo, flujos 0–20 con fórmulas vivas (IRR/NPV recalculan al editar E/palancas), hojas Supuestos/Flujos/Comparativo/Cobertura/Decisión. Verificado 12/12 vs modelo (COM recalc).
- Verificación global: R72 y TIR de cada sitio rev3 = modelo Python a 0.000%, cero celdas de error.
- Libros individuales Preforma: corregidos B9/C53/cap, pero conservan la ilustración de despacho voraz pre-rev2 — regenerarlos si se van a enviar.

## Sources consulted
- [[demanda-facturable]], [[bess-savings-model]], [[horarios-y-divisiones]] (bloques punta 2h verano / 4h invierno)
- [[2026-07-07-gepp-2026-terms-repricing]] (términos 2026, BESS 0.5C/2h), [[2026-07-02-gepp-max-savings-web]] (sweep 2h óptimo)
- Libros rev2 (motor horario embebido, columnas Q/L) — extracción openpyxl + réplica paramétrica verificada al peso

## Confidence
High en la comparación de escenarios (réplica del motor verificada a 0.000% en R72/TIR contra los libros; fórmula Q reconstruida ±0.07%). Medium en niveles absolutos de Proplasa por medidor (inconsistencia kWh-punta vs D-punta de origen — pendiente recibos CFE). Los brutos año-1 son motor (tier b); tarifas y consumos son recibos/Perfil (tier a); merma, degradación y escalaciones son supuestos (tier c).
