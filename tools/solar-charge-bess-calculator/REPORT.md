# REPORT — GEPP rev4 "BESS Carga Solar" (números clave y deltas vs rev3)

**Fecha:** 2026-07-14 · **Estado:** entregado, pendiente aprobación del usuario sobre el producto final (ver `DESIGN.md`).
**Propósito de este documento:** DESIGN.md §6 — números clave y deltas vs rev3 para el paquete de aprobación.

---

## 1. Qué cambió (modelo)

El BESS ahora se carga **primero con excedente solar de mediodía**; sólo el faltante se carga de red en horario base (0-5h). La descarga no cambia (rasurado plano en punta). Contabilidad **self-basis** (PPA facturado sobre kWh autoconsumido — continuidad con rev3); el beneficio de la carga solar vive únicamente en la columna nueva `O_new = carga_base·t_base + carga_solar·c_oport` (`c_oport = 0` en Op1 / `t_int` en Op2). Simulador: `dispatch_cs.py` → `motor_cs.json`. El multiplicador PPA `k` se re-resuelve por opción (`solve_k_cs.py`) para mantener TIR inversionista combinada (agregado PV+BESS, portafolio 4-Sitios) = **14.000%** en ambas opciones. Sweep extendido de superficie (`sweep_cs_ext.py` → `sweep_cs_ext.json`): `k` re-resuelto en cada punto del barrido; el óptimo standalone por sitio (unión de los 7 sitios a su diseño rev4, sólo el sitio evaluado variando) es la cota defensible reportada en el deck.

Esto **reemplaza** el "Rung 2" que en la consulta previa (`wiki/analyses/2026-07-14-gepp-pv-upsize-solar-charged-bess.md`) era un supuesto a mano acotado por `carga·t_base` (tope teórico $3.08M/año). Ahora es una cifra derivada del motor de despacho horario, con throughput real de carga solar limitado por coincidencia sol-mediodía / excedente.

## 2. Solve de k y PPA (nivel opción/portafolio)

| Opción | k rev4 | TIR inversionista combinada (k viejo) | TIR con k re-resuelto |
|---|---|---|---|
| Op1 (Autoconsumo) | 1.009527 | 13.894% | **14.000%** |
| Op2 (GD Medición Neta) | 1.000029 | 13.9998% | **14.000%** |

Basis alternativa retenida para formalización post-aprobación del engine (Option B, PPA sobre generación total): Op1 k=0.960258 (TIR 14.463%→14.000%), Op2 k=1.000030. No usada en los libros entregados (self-basis es la primaria, por continuidad con rev3).

## 3. Resultados por sitio — Opción 1 (Autoconsumo), rev3 → rev4

| Sitio | kWp | PPA $/kWh | Carga solar kWh/año | % de la carga BESS | Bono solar-charge $/año | TIR BESS | NPV cliente 20a |
|---|---|---|---|---|---|---|---|
| Ixtlahuacán | 4,550 → **5,170** | 1.2848 → **1.2971** | 581,755 | 30.5% | **$644,140** | 10.46% → **11.51%** | $103.5M → **$108.9M** |
| Acapulco | 1,618 → **1,748** (tope superficie) | 1.2258 → **1.2375** | 145,024 | 18.3% | **$143,202** | 6.32% → **6.92%** | — |
| Cancún | 1,100 → **1,270** | 1.5278 → **1.5423** | 130,445 | 27.7% | **$167,095** | 8.41% → **9.50%** | — |
| Proplasa / Preformas / Tapa | sin cambio (superficie 100% usada) | 1.3527 → 1.3656* | 0 | 0% | $0 | sin cambio | sin cambio |

*El PPA de Proplasa/Preformas/Tapa sube ligeramente sólo por el `k` re-resuelto a nivel portafolio (mismo kWp, mismo despacho — sin carga solar propia).

**Portafolio (4 Sitios + Proplasa):** bono solar-charge total **+$954,437/año** (644,140 + 143,202 + 167,095); **857 MWh/año** de excedente solar cargado al BESS (581,755 + 145,024 + 130,445 kWh).

Cobertura generación/consumo Op1: Ixtlahuacán 36.6% → **41.6%**, Acapulco 34.0% → **36.7%**, Cancún 34.7% → **40.1%**, Proplasa 6.9% (sin cambio). Portafolio: **15.0% → 16.25%**.

**Cliente neto año 1 (libro 4-Sitios):** Op1 **$39.13M** · Op2 **$31.09M**.

## 4. Sección "¿Y con más superficie?" (deck) — resumen

Barrido standalone por sitio (k re-resuelto por punto, cota defensible: cada sitio evaluado solo, con el resto de sitios fijo al diseño rev4):

| Sitio | kWp óptimo standalone | m² requeridos | m² disponibles hoy | Δ ahorro cliente año 1 vs diseño rev4 |
|---|---|---|---|---|
| Ixtlahuacán | 5,430 kWp | 21,720 m² | 25,308 m² (techo alcanza) | **+$20,617/año** |
| Acapulco | 2,270 kWp | 9,080 m² | 7,019 m² (**faltan 2,061 m²**) | **+$185,795/año** |
| Cancún | 1,410 kWp | 5,640 m² | 6,828 m² (techo alcanza) | **+$8,986/año** |
| Proplasa (3 sitios) | tope regulatorio 20 MW por sitio | 80,000 m² c/u | 100% del predio ya usado | **+$17.8M/año** (si existiera superficie; teórico) |

Nota: el óptimo **conjunto** (unión de los 7 sitios recalculando `k` sobre el portafolio completo) da cifras algo distintas por el acoplamiento del PPA vía `k` — se usa el standalone porque es la cota defensible por sitio sin comprometer al resto del portafolio a un `k` distinto.

## 5. Gates de verificación (todos PASS)

1. **Réplica modo-viejo:** motor con kWp_old y carga solar deshabilitada reproduce R72/C52 de rev3-live <0.1% — 28 checks, 7 hojas × 2 opciones.
2. **Identidades de energía:** V+W=N/RTE, V≤U, N≡motor — 1,176 checks, todo OK.
3. **Recalculo LibreOffice (UNO, `recalc.sh`/`recalc_uno.py`) vs réplica Python:** <0.5% — 112 checks.
4. **Viabilidad cliente:** positivo año 1, todos los sitios y opciones.
5. **Deck:** sintaxis node OK · `domstub_cs.js` 90 renders, 0 fugas (NaN/undefined) · `MODEL` del deck idéntico byte a byte al JSON fuente (`gepp_data_cs.json`) · cobertura recalculada en runtime ±0.046pp vs motor · 9 capturas Playwright inspeccionadas (`shots/`: despacho invierno/verano Ixt+Can, cobertura Op1/Op2, "más superficie" Ixt/Can/Pro).

## 6. Hallazgo — cachés de rev3 desactualizadas (⚠️ importante)

Los libros rev3 entregados ("... rev3 - Esc 4pct TIR 14.xlsx", 4-Sitios y Proplasa) tienen las celdas de proyección (**C52** TIR BESS, **C55** NPV cliente) con **caché desactualizada** en las 7 hojas de sitio — precede un cambio tardío en Supuestos. Al recalcular en vivo (LibreOffice UNO, verificado independientemente con la librería `formulas` de Python — ambas coinciden), los valores reales difieren sensiblemente de la caché:

| Sitio (ej.) | C52 TIR BESS caché | C52 TIR BESS live | C55 NPV cliente caché | C55 NPV cliente live |
|---|---|---|---|---|
| Ixtlahuacán | 11.363% | **10.462%** | $128.6M | **$103.5M** |

R72 (total anual) y C44 (año 1 con merma) **sí son consistentes** — no están afectados. Cualquier extracción que lea la caché de rev3 (p.ej. `extract_tir14.py` o una apertura `data_only=True` de openpyxl) muestra los números viejos/incorrectos. **Los archivos rev3 NO se tocaron.** Todas las comparaciones rev4-vs-rev3 de este reporte se rebasaron contra rev3-**recalculado en vivo** (copias en `_rev3_recalc/rev3_4S_recalc.xlsx` y `rev3_PP_recalc.xlsx`), no contra la caché.

## 7. Caveats (prefactibilidad)

- **Prefactibilidad, no bancable.** Los datos de GEPP son mensuales (B/I/P de `imported/gepp-*/bills.json`); la forma intradía usada por el simulador de despacho es una **curva de giro industrial 24/7 escalada** (`tools/load_curves.py`) + una campana solar sintética (`PV_BELL`) — no hay datos de medición horaria (15-min HM) de ningún sitio. El `pct_ac` (autoconsumo) y el reparto carga-solar/carga-base son, por tanto, cifras de prefactibilidad.
- **Superficie y punto de interconexión** en la sección "¿Y con más superficie?" usan la tabla SITIOS de Supuestos (m²/kWp = 4.0) — **no** hay visita técnica que confirme estructura de techo, sombreado real, o capacidad del transformador/punto de interconexión para el kWp ampliado. Cualquier kWp por encima del diseño rev4 requiere validación en sitio antes de comprometerse.
- El modelo de despacho asume un día "típico" por mes/estación (invierno/verano) sin variabilidad día a día de irradiancia ni de la curva de carga real.
- `tools/cfe_savings/` (motor engine, golden test) **no se tocó** — la formalización de este modo de despacho en el engine es una fase posterior a la aprobación del usuario.

## 8. Entregables y ubicaciones Drive

| Archivo | Drive file id |
|---|---|
| `GEPP - Solucion Energetica Solar-Charge BESS - 4 Sitios.xlsx` | `1bebuh6a7CFnagLOLVcjc1BfDszMZozEg` |
| `GEPP - Solucion Energetica Solar-Charge BESS - Proplasa.xlsx` | `1ycaxDxssLudSnPG2oHUAhcpUrdSZpGEO` |
| `GEPP - Solucion Energetica Solar-Charge BESS.html` ("Solución Energética v8 · Carga Solar") | `1wk66oHR16t5Rv9meylWBzbX5VTGQb4aQ` |
| Carpeta Drive (ambos libros) | `1INDng8_TDPSgC0m69PnjkDHZ5f3BzCOQ` |

Working files locales en `work/gepp-carga-solar/`: `dispatch_cs.py` (simulador) · `solve_k_cs.py`/`solve_k_cs.json` (solve de k) · `sweep_cs_ext.py`/`sweep_cs_ext.json` (barrido superficie) · `build_books_cs.py` / `build_deck_cs.py` (constructores) · `extract_cs.py` → `gepp_data_cs.json` (fuente del deck) · `recalc.sh`/`recalc_uno.py` (recalculo LibreOffice UNO) · `verify_cs.py` (gates) · `shots_cs.py` + `shots/` (capturas) · `motor_cs.json` (salida cruda del simulador) · `_rev3_recalc/` (copias rev3 recalculadas en vivo, para comparación — no son entregables).

## 9. Incidente (breve, ver también log)

La primera corrida de LibreOffice usó una URL `-env:UserInstallation` con espacio sin codificar ("CFE Brain") → `soffice` crasheó y su maquinaria de modo seguro reubicó contenido del home a `~/SafeMode`; restaurado completamente en la misma sesión. Lección: siempre URL-encodear rutas de `UserInstallation`; `soffice --convert-to` **no** recalcula de forma confiable — se requiere UNO + `calculateAll()` (ver `recalc.sh`).
