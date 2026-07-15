# NUMBERS_NR — Escenario "Sin Restricción de Superficie" (NR)

**Fecha:** 2026-07-14 · **Modelo:** GEPP BESS Carga Solar rev4 · **Opción:** 1 (Autoconsumo) · **Estado:** escenario derivado, prefactibilidad.
**Convención de portafolio (corregida):** 4-row — `pro` (3,848.9 kWp rev4) ES la consolidación de pr1+pr2+tap (681.2+1,912+1,255.7 = 3,848.9): el mismo complejo físico Proplasa modelado de dos formas (predio consolidado vs per-meter). Las sumas de portafolio usan **ixt+aca+can+pro solamente**; pr1/pr2/tap se reportan como pestañas per-meter, excluidas de la suma (sin doble conteo).

## Metodología (3-4 frases)

Variante de la Op1 (Autoconsumo) donde la superficie de techo NO es restricción: cada sitio se dimensiona a su **óptimo standalone** — el `k` PPA resuelto sobre el sitio SOLO a TIR inversionista 14% (self-basis, BESS fijo, despacho carga-solar, tope regulatorio duro 20,000 kWp), la cota defensible por sitio (bloque `standalone` de `sweep_cs_ext.json`). Con los sitios a kWp_NR se **re-resuelve un único `k` sobre SITES4 = [ixt, aca, can, pro]** — la metodología EXACTA del rev4 entregado (`solve_k_cs.py`) — para TIR inversionista combinada = **14.000%**; los 7 sitios se cotizan a ese `k` y la IRR combinada de SITESP=[pr1,pr2,tap] a ese `k` se reporta (no se resuelve). El despacho es el motor carga-solar (`dispatch_cs.py`): el BESS se carga primero con excedente solar de mediodía (cap C28), el faltante de red en horas base 0-5; descarga = rasurado plano en punta, sin cambio; contabilidad self-basis, `O_new = carga_base·t_base + carga_solar·c_oport` con `c_oport=0` en Op1 y `carga_solar + carga_base = N/RTE` exacto. **Op2 (GD Medición Neta) NO cambia** — el tope regulatorio GD de 0.7 MW liga, no el techo; los bloques Op2 se copian verbatim de rev4.

## k y precio (portafolio SITES4)

| | k | TIR inversionista combinada (SITES4) |
|---|---|---|
| rev4 entregado (Op1) | 1.009527 | 14.000% |
| **NR (Op1)** | **0.949527** | **14.000%** (verificado 14.00000%) |

IRR combinada **SITESP** (pr1+pr2+tap per-meter) al k_NR: **13.81%** (reportada, no resuelta — misma convención que `solve_k_cs.json`).

El `k` **baja** (0.9495 < 1.0095): la base PV mucho mayor reparte el retorno del inversionista sobre más generación, así que el multiplicador PPA cae y el precio $/kWh baja en todos los sitios — el cliente gana por doble vía (más kWh propios + PPA más barato).

## Resultados por sitio — Op1, rev4 → NR

### Sitios del portafolio (suma 4-row)

| Sitio | kWp rev4 | kWp NR | m² req. | m² faltantes | PPA rev4 | PPA NR | Ahorro año1 rev4 | Ahorro año1 NR | Δ ahorro año1 | Cob. rev4 | Cob. NR | Tope reg. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ixtlahuacán | 5,170 | 5,430 | 21,720 | 0 | 1.2971 | 1.2200 | $9,935,583 | $10,796,202 | **+$860,619** | 41.2% | 43.3% | no |
| Acapulco | 1,748 | 2,270 | 9,080 | 2,061 | 1.2375 | 1.1639 | $4,243,625 | $5,061,321 | **+$817,696** | 38.7% | 50.3% | no |
| Cancún | 1,270 | 1,410 | 5,640 | 0 | 1.5423 | 1.4507 | $2,581,137 | $2,861,105 | **+$279,968** | 41.9% | 46.5% | no |
| Proplasa | 3,849 | 20,000 | 80,000 | 64,604 | 1.3656 | 1.2844 | $22,367,603 | $38,462,663 | **+$16,095,059** | 7.1% | 36.9% | **sí** |

### Pestañas per-meter Proplasa (modelado alternativo del MISMO complejo que `pro` — excluidas de la suma)

| Pestaña | kWp rev4 | kWp NR | m² req. | PPA rev4 | PPA NR | Ahorro año1 rev4 | Ahorro año1 NR | Δ ahorro año1 | Cob. NR |
|---|---|---|---|---|---|---|---|---|---|
| Preforma 1 | 681 | 4,210 | 16,840 | 1.3656 | 1.2844 | $3,867,982 | $6,891,812 | +$3,023,830 | 42.9% |
| Preforma 2 | 1,912 | 11,950 | 47,800 | 1.3656 | 1.2844 | $10,856,621 | $19,449,181 | +$8,592,560 | 43.4% |
| Tapa | 1,256 | 7,700 | 30,800 | 1.3656 | 1.2844 | $7,186,888 | $12,712,346 | +$5,525,458 | 42.6% |

*m² disponibles (tabla SITIOS): ixt 25,308 · aca 7,019 · can 6,828 · pro 15,396 · pr1/pr2/tap sin fila (n/d). m²/kWp = 4.0. Todos los precios NR usan el `k` de SITES4 — ningún sitio requirió el fallback standalone (todos viables al k conjunto).*

## Portafolio (convención 4-row: ixt+aca+can+pro)

| Métrica | rev4 | NR | Δ |
|---|---|---|---|
| kWp Op1 total | 12,037 | **29,110** | +17,073 |
| Cobertura generación/consumo | 16.6% | **39.3%** | +22.7 pp |
| Ahorro cliente año 1 | $39,127,948 | **$57,181,291** | **+$18,053,342/año** |
| VAN cliente 20a | $411,671,139 | **$617,217,004** | **+$205,545,865** |
| Carga solar al BESS | — | 2,674,841 kWh/año | — |
| Excedente remanente (a texc≈0) | — | 1,426,378 kWh/año | — |
| Inversión estimada Newman (CAPEX NR) | — | **$510,116,373** | — |

**Ahorro adicional total si la superficie existiera: +$18.05M/año (+$205.5M VAN 20a).** El baseline rev4 4-row ($39.13M) reconcilia exacto con la suma de netos del deck (9.94+4.24+2.58+22.37M).

## Gates de verificación (todos PASS — ver `verify_nr.py`)

| Gate | Resultado | Detalle |
|---|---|---|
| A · Identidad energía `carga_solar+carga_base=N/RTE` (84 meses) | PASS | dev rel máx 1.7e-16 (precisión completa) |
| A · `carga_solar ≤ exceso disponible` | PASS | overshoot 0 kWh |
| B · Continuidad motor@rev4 ≡ `motor_cs.json` | PASS | dev máx 0.0003% (<0.1%) |
| C · TIR inversionista combinada @ k_NR en SITES4 = 14.000% | PASS | 14.00000% (k_NR=0.949527) |
| C2 · IRR combinada SITESP @ k_NR reportada | PASS | 13.8138% |
| C3 · Baseline rev4 4-row = $39.13M (suma del deck) | PASS | $39,127,948, dev 0.0000% |
| C4 · Suma portafolio = SITES4 solamente (sin doble conteo) | PASS | exacto |
| D · Ahorro cliente NR ≥ rev4 por sitio | PASS | sin excepciones (7/7) |
| E · Beneficio neto cliente año 1 > 0 todos los sitios @ k_NR | PASS | sin negativos (minJ 20a > 0 en los 7) |
| F · kWp NR ≥ diseño rev4 por sitio | PASS | ninguno se encoge |
| G · Op2 sin cambio vs `motor_cs.json` | PASS | copiado verbatim |
| H · Carga total día típico = C30/RTE | PASS | dev rel máx 1.0e-5 |

## Caveats

- **Prefactibilidad, no bancable.** Datos GEPP mensuales (B/I/P) + curva de giro industrial 24/7 escalada + campana solar sintética; sin medición horaria HM 15-min. El reparto carga-solar/carga-base y el `pct_ac` son cifras de prefactibilidad.
- **Doble modelado Proplasa.** `pro` y pr1/pr2/tap son el mismo complejo físico: `pro` consolidado (predio), pr1/pr2/tap per-meter (por medidor/RPU). El portafolio suma SOLO la vista consolidada; las pestañas per-meter son ilustrativas de la repartición por medidor y usan el mismo `k`.
- **Superficie / interconexión sin visita técnica.** Todo kWp por encima del diseño rev4 supone techo/estructura/punto de interconexión disponibles. Los m² requeridos NR exceden lo disponible en aca (faltan 2,061 m²) y masivamente en pro (faltan 64,604 m²).
- **Proplasa NR es cota teórica.** El consumo del complejo es muy grande frente a su predio; el óptimo standalone lleva a 20,000 kWp — **topa el techo regulatorio de 20 MW** (la curva aún subía; es truncamiento, no óptimo interior). Demuestra el *potencial* si la superficie existiera; no ejecutable sin predio adicional. Framing correcto: "potencial adicional con más superficie".
- **Artefacto de subsidio cruzado:** bajo un `k` conjunto un sitio sobredimensionado se apoya en el PPA del resto. Por eso el dimensionado usa el **óptimo standalone** (cada sitio resuelto solo) como cota defensible; el `k` de precio sí es conjunto (SITES4, metodología rev4).
- Op2 (GD Medición Neta) sin cambio: el tope 0.7 MW liga antes que el techo.

## Salidas

- `motor_nr.json` — salida cruda del simulador NR (Op1 a kWp_NR + Op2 verbatim rev4 + día típico), forma de `motor_cs.json`.
- `gepp_data_nr.json` — datos deck-ready por sitio (con marca `en_suma_portafolio`) + totales 4-row + `k` + curvas día típico (invierno/verano) + cobertura.
- `build_nr.py` (constructor) · `verify_nr.py` (gates).
