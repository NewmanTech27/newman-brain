# GEPP — Fact Pack para "Preguntas que GEPP podría hacernos sobre el modelo"

**Fecha de compilación:** 2026-07-15 · **Propósito:** insumo para un documento de Q&A anticipada, disparado por la pregunta del usuario: *"en Ixtlahuacán solo tomamos valores CFE como referencia de ahorro — ¿esto se ve impactado cuando TALA se va?"*

**Convención de etiquetado (obligatoria por fact-tier, CLAUDE.md):**
- **[source-confirmed]** — dato duro citado de un workbook del cliente, contrato, o página wiki con fuente primaria.
- **[engine-derived]** — salida de `calc_core.py` / `dispatch_cs.py` / los libros rev3/rev4/NR (golden-anclado, verificado).
- **[assumption]** — supuesto/convención editable de Newman (financiero, de sizing, o de forma de carga) — no dato del cliente ni salida cruda del motor.

---

## 0 · Respuesta directa a la pregunta disparadora

**"En Ixtlahuacán solo tomamos CFE como referencia — ¿esto cambia cuando TALA se va?"**

**No — y es por diseño, no por descuido.** [source-confirmed + engine-derived]

- La línea base de ahorro ("Tarifa Actual" / "CFE bruto") en **todos** los libros GEPP (v3 en adelante) es **la carga total del sitio valuada a tarifas CFE GDMTH plenas, sin ningún descuento de autoabasto** — es decir, exactamente el escenario "TALA ya no está". Ver [[2026-06-15-gepp-v3-audit-rebuild]], `imported/gepp-ixtlahuacan/meta.json` (nota: *"la reconstrucción = carga TOTAL valuada a tarifas CFE GDMTH, la base correcta para dimensionar PV/BESS"*).
- El beneficio actual de Tala (**10% de descuento sobre importe de energía, ≈ $2.68M/año en Ixtlahuacán 2025**, fuente workbook `TALA`/`Perfil de Consumo`) se muestra como una **línea separada y editable** ("Beneficio autoabasto"), restada del CFE bruto para llegar al "costo actual hoy" — **nunca mezclada dentro del ahorro PV+BESS del proyecto**. Ver `GEPP - Solución Curada y Estructura Comercial.md` §3, y la columna naranja "Beneficio autoab. (→2032)" en `GEPP - Propuesta PV+BESS 4 Sitios (2026-07) — Resumen.md`.
- Motivo explícito documentado (doble): (1) **motivo técnico** — 0/12 meses de la reconstrucción cuadran contra el recibo impreso de Ixtlahuacán (diverge exactamente por el descuento Tala), así que el CFE pleno es la única base *comparable* y defendible para dimensionar PV/BESS sin contaminar el motor con el descuento de un tercero; (2) **motivo de negocio** — ambos contratos de autoabasto (Tala e ENEL) **vencen en 2032**; los libros v3+ modelan explícitamente un **"cliff" en 2032** donde el gasto real de GEPP salta de "costo actual con autoabasto" a "CFE pleno" — el proyecto solar ya está dimensionado y valuado contra ese escenario post-2032, así que la salida de Tala (antes o en 2032) **no requiere re-trabajar el ahorro reportado del proyecto**; sólo hace desaparecer la línea "Beneficio autoabasto" que ya se mostraba aparte.
- **Consecuencia práctica para la conversación con GEPP:** el ahorro PV+BESS de Ixtlahuacán (**$11.3M/año neto Op1** en el libro rev2/v2, recalibrado en rev3/rev4 a $9.9M→$10.8M según escenario — ver §3) **es el mismo con o sin Tala**, porque nunca asumió a Tala en el baseline. Lo único que cambia con la salida de Tala es que GEPP deja de disfrutar el ~$2.68M/año de descuento — un efecto **anterior y externo** al proyecto solar, no una consecuencia del modelo.
- Esta misma convención (CFE pleno como baseline, autoabasto como línea aparte) se aplicó también a **Proplasa/ENEL** — la respuesta es simétrica: si ENEL se va del todo (ya colapsó de ~90% a ~16% en 2026), el ahorro PV+BESS reportado de Proplasa tampoco cambia.

---

## 1 · Situación de suministro por sitio

| Sitio | Suministrador actual | % del consumo 2025 | Tarifa/división | Baseline $/kWh usado en el modelo de ahorro | Origen del número |
|---|---|---|---|---|---|
| **Ixtlahuacán** | [[tala-energy]] (cogen bagazo, zafra) + CFE | ~49.5% Tala (100% Dic–May, ~0% Jun–Nov) / balance CFE | DIST Jalisco (SIN; **no es GDMTH** — sin cargo distribución explícito) [source-confirmed, MC-GEPP-4SITIOS] | **CFE GDMTH/DIST pleno** (sin descontar el 10% Tala) | [source-confirmed] hoja `Tarifas` del workbook `Perfil de Consumo GEPP 2025-26`; validado por `tools/import_perfil_xlsx.py` (`imported/gepp-ixtlahuacan/`) |
| **Acapulco** | 100% CFE | 100% | GDMTH Centro Sur | CFE GDMTH pleno (recibo real) | [source-confirmed] recibo/workbook — sitio sin autoabasto, no hay ambigüedad de baseline |
| **Cancún** | 100% CFE | 100% | GDMTH Peninsular | CFE GDMTH pleno (recibo real) | [source-confirmed] recibo/workbook |
| **Proplasa (PR1/PR2/TAP)** | [[enel-mexico]] (autoabasto) + CFE | 69.6% ENEL en 2025 (colapsó a ~16% Mar–Abr 2026) | GDMTH Valle de México Norte | **CFE GDMTH pleno** (sin descontar el precio ENEL $1.78–1.92/kWh) | [source-confirmed] hoja `ENEL PROPL`; nota de reconstrucción en `imported/gepp-proplasa-pr1/meta.json` idéntica en lógica a Ixtlahuacán |

**Por qué CFE pleno en TODOS los sitios con autoabasto, no solo Ixtlahuacán:** es la misma convención aplicada uniformemente — no es un tratamiento especial de Ixtlahuacán. La nota estándar en cada `meta.json` de sitio con autoabasto dice literalmente: *"Diverge del total impreso por el cliente — típicamente sitio con autoabasto (descuento Tala/ENEL). La reconstrucción = carga TOTAL valuada a tarifas CFE GDMTH, la base correcta para dimensionar PV/BESS. Delta ≈ descuento autoabasto."* [source-confirmed, `imported/gepp-ixtlahuacan/meta.json`, `imported/gepp-proplasa-pr1/meta.json`]

**Régimen regulatorio elegido por sitio (Op1 Autoconsumo vs Op2 GD Medición Neta), última versión rev4/NR:**

| Sitio | Op1 Autoconsumo (kWp, rev4→NR) | Op2 GD Medición Neta (kWp, fijo) | Nota |
|---|---|---|---|
| Ixtlahuacán | 4,550 → 5,170 → 5,430 | 839.45 (<0.7 MW AC) | Recomendado: Op1 |
| Acapulco | 1,618 → 1,748 → 2,270 | 839.45 | Recomendado: Op2 (o Op1 si consigue ~3,000 m² extra) |
| Cancún | 1,100 → 1,270 → 1,410 | 839.45 | Recomendado: Op2 (mejor ROI del portafolio) |
| Proplasa (3 medidores) | 3,849 → sin cambio (techo 100% usado) → 20,000 (tope regulatorio, teórico) | 2,518 (= 3× 839.45, sin permiso) | Recomendado: Op2 (3 puntos de interconexión = 3 plantas GD) |

[engine-derived] — cifras de `NUMBERS_NR.md`, `REPORT.md` y `MC-GEPP-4SITIOS-2026-07.md`.

---

## 2 · ENEL / TALA — qué se sabe y qué NO se sabe

### Lo confirmado [source-confirmed, todo del workbook `Perfil de Consumo GEPP 2025-26`]
- Ambos contratos son **legacy autoabasto** (LIE/LSP-era), porteo a través de la red CFE, y **vencen en 2032**.
- **Tala** (Ixtlahuacán): cogenerador de bagazo de caña (ingenio Tala, Jalisco). Factura a **tarifa CFE-equivalente menos 10% de descuento** sobre importe de energía. Generación **estacional por zafra**: ~100% Dic–May, ~0% Jun–Nov (49.5% anual). Descuento 2025 = **$2.68M**.
- **ENEL** (Proplasa): generador (Enel Green Power/Generación México). Precio **$1.78–1.92/kWh** (≈ nivel intermedia GDMTH). Cobertura 2025 = 69.6% del predio (PR1 87%, PR2 57%, TAP 79%).
- **Anomalía 2026 de ENEL:** su participación **colapsó de ~55% (Ene–Feb) a ~16% (Mar–Abr 2026)** — colapso escalonado por medidor (PR2 primero, PR1/TAP después). La causa es **desconocida**.

### Lo NO confirmado — huecos abiertos [flagged, no asumido]
1. **Volúmenes comprometidos / take-or-pay** de ambos contratos — no se tienen los contratos Tala/ENEL, solo el resultado facturado en el workbook del cliente.
2. **Costo de porteo** y estructura tarifaria fina de cada contrato.
3. **Cláusulas de salida/modificación** rumbo al vencimiento 2032 (¿hay opción de salida anticipada, penalización, o es automático al 2032?).
4. **Causa del retiro de ENEL en 2026** — ¿incumplimiento estructural del suministrador o decisión estratégica de GEPP? Determina si el PV en Proplasa desplaza energía cara (CFE, ya ocurriendo) o barata (ENEL, escenario pasado). *(Pregunta explícita ya formulada a GEPP en `GEPP - Preguntas para el cliente.md` §1.2.)*
5. **Coexistencia legal** — ¿puede un centro de carga bajo porteo de autoabasto legado sostener simultáneamente una interconexión de medición neta / autoconsumo en el mismo medidro? **Sin precedente confirmado**; abierto en `wiki/overview.md` y repetido en cada análisis GEPP desde 2026-06-10.
6. **Lectura del techo 0.7 MW en Proplasa** — ¿por medidor/RPU o por centro de carga (un predio, 3 medidores)? El modelo asume "3× exento" (por medidor) pero **no está confirmado** con CNE/CFE.
7. Si Tala o ENEL terminan **antes** de 2032 (ej. el colapso de ENEL en 2026 podría ser el inicio de una salida temprana) — el modelo no tiene un mecanismo de "salida anticipada", solo el cliff programado a 2032; ver §0 arriba por qué esto no afecta el ahorro reportado del proyecto (sí afecta cuándo desaparece el "Beneficio autoabasto").

---

## 3 · Metodología del baseline de ahorro ("¿cómo se calcula el ahorro?")

**Estructura de cascada (todas las versiones desde v3, [engine-derived]):**

```
CFE BRUTO (Tarifa Actual: toda la carga a CFE pleno, sin autoabasto)      $316.2M portafolio (2025, v3)
(−) Ahorro autoabasto Tala + ENEL (línea SEPARADA, desaparece en 2032)     $21.6M
(=) Costo actual que paga GEPP hoy                                        $294.6M
(−) Ahorro del proyecto (PV + BESS + FP)                                  $62.8M (curada v3) / $39.1M (rev4 Op1, 4 sitios ppal.) / $57.2M (NR, sin restricción de superficie)
(=) Costo neto con proyecto
```

- El **ahorro PV** se calcula por sitio/mes: `aprov = min(generación × pct_ac, kWh_intermedio del mes)` — el PV solo desplaza energía del **periodo intermedio** (PV ⊥ punta, invariante del dominio); el excedente que no se autoconsume se valora a `texc ≈ $0` en Autoconsumo (venta a CFE a nivel mayorista) o a la tarifa del periodo bajo medición neta. [engine-derived, `tools/calc_core.py`]
- El **ahorro BESS** viene de arbitraje: `arb = descarga × tarifa_punta − carga × tarifa_base`, con `carga = descarga / RTE`. **El motor carga la batería de RED en horario base — NO de excedente solar** (hallazgo crítico documentado en [[2026-07-14-gepp-pv-upsize-solar-charged-bess]]); el modelo "BESS Carga Solar" (rev4) es una variante posterior que sí simula carga solar-primero (ver §4).
- El **ahorro FP** es la corrección de la multa por factor de potencia (capacitores), tratado siempre como **palanca separada**, nunca mezclado con PV/BESS.
- **PPA self-basis:** el PPA se factura sobre los kWh efectivamente autoconsumidos (Op1) o generados (Op2) — no sobre toda la generación bruta. El multiplicador de precio `k` **se resuelve por bisección**, no se asume, para alcanzar una TIR inversionista objetivo (históricamente 18% estándar → 14% concesión GEPP → 14.000% exacto en rev3/rev4/NR, verificado). [engine-derived]
- **Escaladores:** evolucionaron durante el proyecto — versión inicial (Checkpoint C, jul-07) usó **CFE 6% / PPA 5%**; corregido a **CFE 5%** (hallazgo de "escalación stale" en libros Proplasa); la versión **vigente (rev3/rev4/NR, "Esc 4pct TIR 14")** usa **4% flat para CFE y PPA por igual**. [assumption, editable en Supuestos — **verificar cuál escalador es el que GEPP vio en la última reunión**, porque hubo tres valores distintos en el histórico del proyecto].
- **Doble línea base + cliff 2032:** la proyección a 20 años en los libros rev2+ modela explícitamente el salto de gasto cuando Tala/ENEL vencen en 2032 — el "hedge" narrativo es que el PPA fijo del proyecto solar amortigua ese salto justo cuando ocurre. [engine-derived + assumption de escenario]

---

## 4 · Supuestos clave del modelo (valor, procedencia, tier)

| Supuesto | Valor | Tier | Fuente |
|---|---|---|---|
| Fuente de yield solar | Índice geográfico por municipio (municipio→CP→kWh/kWp) — Ixt 1,783 · Aca 1,869 · Can 1,500 · Pro/Cuautitlán 1,660 kWh/kWp·año | [assumption — prefactibilidad] | `tools/solar-yield-lookup`; validado vs Global Solar Atlas (Cancún ~5–10% conservador). **No es HelioScope** — sería el upgrade a bancable. |
| Forma de carga intradía | Curva de giro **"Industrial 24/7"** (pesos 1.30 día / 1.15 tarde / ×0.85 domingo), normalizada para reproducir exactamente los kWh mensuales B/I/P facturados | [assumption] | `tools/load_curves.py`; aplica a los 7 sitios GEPP (`imported/*/inputs.json` → `"giro": "Industrial 24/7"`) |
| Curva solar intradía | Campana sintética `PV_BELL` 6:30–19:00, normalizada al yield mensual | [assumption] | `tools/load_curves.py` |
| Resolución de datos | **Solo mensual (kWh Base/Intermedio/Punta), NO 15-min HM** | [source-confirmed — límite del dato entregado por GEPP] | `Perfil de Consumo GEPP 2025-26.xlsx` — es el techo de bancabilidad citado en cada análisis GEPP |
| RTE (round-trip efficiency BESS) | 0.96 | [assumption — default de casa] | `calc_core.py` default; `dispatch_cs.py: RTE = 0.96` |
| DoD (profundidad de descarga usable) | 0.96 | [assumption — default de casa] | `calc_core.py` default `dod=0.96`; `E_útil = kWh × DoD × √RTE` |
| Merma BESS (downtime) | **2 meses/año sin ahorro** → factor 10/12 (0.833) | [assumption] | `dispatch_cs.py: MERMA = 2`; MC-GEPP-4SITIOS §4 |
| Degradación PV | **0.5%/año** | [assumption — default `calc_core.py`, `pv_degr=0.005`] | MC-GEPP-4SITIOS §5: "Degr. PV 0.5%/año" — **nota:** el estándar de casa Newman evolucionó después (jul-12, cliente AFC/KFC) a un split **1.0% año 1 + 0.4% años 2+**; los libros GEPP vigentes (rev3/rev4/NR) **siguen en el default antiguo 0.5% plano**, no en el split nuevo — punto a homologar o a explicar si GEPP compara con otra propuesta Newman más reciente. |
| Degradación BESS | 1.25%/año | [assumption — default `calc_core.py`, `bess_degr=0.0125`] | MC-GEPP-4SITIOS §5 |
| Densidad de instalación | **4.0 m²/kWp** (m²/kWp de Supuestos, estándar de casa Newman, confirmado por el usuario) | [assumption] | MC-GEPP-4SITIOS §3: alternativa conservadora sería 6.2 m²/kWp; módulo de referencia Tongwei TWMNF-66HD715, 715 Wp |
| texc (valor del excedente en Autoconsumo) | ≈ $0 (venta a CFE a nivel mayorista/PML) | [source-confirmed — regla regulatoria, directiva del cliente "cero contraprestación"] | [[autoconsumo]]; confirmado como directiva explícita de GEPP en `2026-06-10-gepp-portfolio-project-check.md` §Best-case |
| Tope GD sin permiso (Op2) | **< 0.7 MW AC ≈ 839.45 kWp DC** (ratio DC/AC ≈1.20) | [source-confirmed — LSE 2025, DOF 18-mar-2025] | [[generador-exento]], MC-GEPP-4SITIOS §1 |
| Tope autoconsumo permiso simplificado | 0.7–20 MW | [source-confirmed — DACG CNE, DOF 12-dic-2025] | [[autoconsumo]] |
| Tope regulatorio duro (escenario NR) | **20,000 kWp** por sitio (más allá, permiso ordinario) | [source-confirmed] | `NUMBERS_NR.md` — Proplasa NR trunca exactamente aquí (cota teórica, no óptimo interior) |
| EPC PV (precio de venta al cliente) | **0.65 USD/Wp** (costo duro 0.50 USD/Wp = spread Newman) | [assumption — término comercial 2026, confirmado por usuario] | MC-GEPP-4SITIOS §5 |
| CAPEX BESS | **0.28 USD/Wh instalado** (0.18 FOB) | [assumption] | MC-GEPP-4SITIOS §5 |
| FX | 17.55 MXN/USD | [assumption — confirmado por usuario 2026-07-08, verificado ≈17.55] | MC-GEPP-4SITIOS §5 |
| Escalación CFE / PPA | **4% / 4%** (vigente, rev3/rev4/NR) — histórico: 6%/5% inicial, luego 5%/? | [assumption — editable en Supuestos] | ver §3 arriba; `solve_tir14.py` docstring |
| Plazo PPA | 15 años (independiente del plazo BESS, ambos editables en Supuestos B18/B19) | [assumption] | `Resumen.md` rev v2 |
| Horizonte de proyección | 20 años (GEPP conserva 100% del ahorro PV años 16–20 tras transferencia del activo) | [assumption — término comercial] | `Solución Curada...` §4 |
| Participación BESS (split ahorro) | **50/50** (inversionista/cliente) | [assumption — decisión de usuario] | MC-GEPP-4SITIOS §5: a 50/50 la TIR BESS queda 8.1–13.5%, no 16% — reportado como hallazgo, no resuelto automáticamente |
| Fianza (PPA bond cost) | 13.9% (default `calc_core.py`) | [assumption] | usado en el análisis de upsize 2026-07-14 |
| WACC de referencia | 12% | [assumption — default `calc_core.py`; no es el mecanismo primario de precio — el PPA se resuelve por TIR objetivo, no por WACC] | `calc_core.py` default |
| Tope GD Op2 en el escenario NR | Sin cambio — 0.7 MW liga antes que el techo físico, así que Op2 nunca cambia entre rev4 y NR | [engine-derived] | `NUMBERS_NR.md` |
| TIR inversionista objetivo (combinada, portafolio) | **14.000%** exacto, resuelto por bisección del multiplicador PPA `k`, ambas opciones (Op1/Op2), verificado en rev3/rev4/NR | [engine-derived] | `solve_tir14.py`, `solve_k_cs.py`, gates de `verify_nr.py` |
| Carga del BESS: fuente | **Rev3 y anteriores: 100% red, horario base (0–5h)**. **Rev4/NR: PRIMERO excedente solar de mediodía (limitado por potencia del inversor C28 y por el excedente real del día), el faltante de red en horario base** | [engine-derived, rev4 en adelante] | `DESIGN.md` §2, `dispatch_cs.py` |
| % de la carga BESS que sale de excedente solar (rev4) | Ixt 30.5% · Aca 18.3% · Can 27.7% · Proplasa 0% (sin headroom de techo) | [engine-derived] | `REPORT.md` §3 |

---

## 5 · Debilidades / huecos abiertos que un cliente informado podría señalar

*(Solo temas de sustancia del modelo — se excluyen incidentes internos de construcción como el error de caché rev3 o el crash de LibreOffice, ya corregidos y documentados internamente.)*

1. **Prefactibilidad, no bancable — falta validación con recibos CFE reales.** El baseline GEPP viene del workbook `Perfil de Consumo` (dato preparado por el propio cliente), no de recibos CFE validados. 0/12 meses de la reconstrucción cuadran al 0.5% contra el total impreso en los sitios con autoabasto (por diseño, ver §0/§1) — pero tampoco se han validado los sitios 100%-CFE (Acapulco/Cancún) contra recibo real; la auditoría de jul-07 encontró que el motor reproduce $311.4M vs $316.2M/$341.9M de versiones anteriores — **todas grado prefactibilidad**.
2. **Sin datos de intervalo 15-minutos (HM).** Toda la forma intradía (pct_ac, split carga-solar/carga-base, dimensionamiento de BESS) es una curva de giro genérica ("Industrial 24/7") escalada a los kWh mensuales facturados — no la curva real del sitio. Esto es la brecha de bancabilidad más citada en el vault para GEPP.
3. **Sin visita técnica / sin datos de techo-terreno reales para todo el rango de kWp propuesto.** Las áreas usadas (m²/kWp = 4.0) son un estándar de casa, no un levantamiento; el escenario "sin restricción de superficie" (NR) es explícitamente teórico en Proplasa (requeriría 64,604 m² adicionales, topa el límite regulatorio de 20 MW antes de encontrar el óptimo real).
4. **Capacidad de transformador / regla de hosting 80%** no verificada — cualquier kWp adicional (ej. el upsize de +0.92 MW o el escenario NR) puede requerir revisión de punto de interconexión.
5. **Coexistencia legal porteo-autoabasto + medición neta/autoconsumo — sin resolver.** Ver §2.5; es el hueco regulatorio más repetido en todo el proyecto GEPP y afecta Ixtlahuacán Y Proplasa por igual.
6. **Lectura del techo 0.7 MW en Proplasa (por medidor vs por predio)** — el modelo asume "3× exento por medidor", sin confirmación de CNE/CFE.
7. **Anomalía de demanda en Ixtlahuacán** — picos de 5,872–7,310 kW en Abr/May/Dic-2025, por encima de los 5,000 kW contratados. No verificado contra recibo real; podría ser evento operativo, error de medición, o exposición de penalización — pendiente de aclarar con el cliente.
8. **Inconsistencia de origen en Preforma 1 (Proplasa)** — los kWh de punta del `Perfil` implican una carga media mayor que la demanda máxima reportada; el ahorro de capacidad se acotó al máximo físico. Se pidió el recibo CFE del medidor para resolverlo.
9. **Bono "carga solar del BESS" es modesto frente al techo analítico inicial** — el primer análisis (2026-07-14) estimó hasta +$3.08M/año de bono si el BESS cargara 100% de excedente solar; el motor de despacho real (rev4) entrega solo **+$954,437/año** (18–31% de la carga del BESS es solar, no el 100% asumido) — importante para no sobre-prometer si GEPP vio la cifra preliminar en alguna conversación.
10. **Split de participación BESS 50/50 no alcanza la TIR estándar de 16% del financiador** (queda en 8.1–13.5% según sitio) — es un hallazgo abierto, no resuelto; requeriría negociar el split (57–72% a favor del inversionista) o repreciar. Si GEPP pregunta "¿por qué la batería rinde menos que el estándar de ustedes?", esta es la respuesta honesta.
11. **Degradación PV inconsistente con el estándar de casa más reciente** — ver tabla §4 (0.5% plano en GEPP vs 1.0%/0.4% split ya usado en propuestas posteriores a otros clientes). No es un error, pero si GEPP compara notas con otro cliente Newman podría notar la diferencia.
12. **Sin costo de respaldo obligatorio CFE modelado** (alternativa a BESS para cumplir el requisito DACG Núm. 4.5 de respaldo para intermitentes ≥0.7 MW) — el análisis del 2026-07-15 encontró que en 3 de 6 sitios (Cancún, Acapulco, Ixtlahuacán) el **mejor NPV es SIN BESS**, contratando respaldo con CFE en su lugar — pero el costo de ese contrato de respaldo no está modelado; sigue siendo un hueco.
13. **Autoabasto Tala/ENEL no modela una salida anticipada** — el modelo asume vencimiento en 2032 tal cual contratado; si Tala o ENEL salen antes (posible dado el colapso de ENEL en 2026), el "Beneficio autoabasto" línea desaparecería antes de lo modelado — pero, como se explica en §0, esto **no** afecta el ahorro del proyecto solar reportado, solo el momento en que el "Beneficio autoabasto" (línea aparte) deja de aplicar.
14. **Múltiples cifras de ahorro histórico para el mismo portafolio a lo largo del proyecto** ($56.9M → $62.8M → $39.1M rev4 4-sitios → $57.2M NR) reflejan cambios de alcance/metodología documentados (áreas reales 2026, BESS 2h vs 4h, TIR 14% vs 18%, restricción de superficie sí/no) — **no son inconsistencias**, pero si GEPP vio una cifra anterior en una llamada, hay que aclarar cuál versión y por qué cambió (ver `2026-07-07-gepp-2026-terms-repricing.md` para la reconciliación completa).

---

## Fuentes consultadas (todas en `/home/mario/CFE Brain`)

- `wiki/entities/gepp.md`, `wiki/entities/enel-mexico.md`, `wiki/entities/tala-energy.md`
- `wiki/sources/2026-06-10-perfil-consumo-gepp-2025-26.md`
- `wiki/analyses/2026-06-10-gepp-portfolio-project-check.md`, `2026-06-15-gepp-v3-audit-rebuild.md`, `2026-07-07-gepp-2026-terms-repricing.md`, `2026-07-14-gepp-pv-upsize-solar-charged-bess.md`, `2026-07-15-gepp-autoconsumo-max-sin-restriccion-superficie.md`, `2026-07-15-gepp-autoconsumo-max-bess-y-techo-solar.md`, `MC-GEPP-4SITIOS-2026-07.md`
- `entregables/propuestas/GEPP - Solución Curada y Estructura Comercial.md`, `GEPP - Preguntas para el cliente.md`, `GEPP - Propuesta PV+BESS 4 Sitios (2026-07) — Resumen.md`
- `imported/gepp-ixtlahuacan/{meta.json,inputs.json}`, `imported/gepp-proplasa-pr1/{meta.json,inputs.json}`
- `work/gepp-carga-solar/DESIGN.md`, `NUMBERS_NR.md`, `REPORT.md`, `dispatch_cs.py`, `build_nr.py`, `solve_k_cs.py`
- `work/gepp-deck/solve_tir14.py`, `gepp_data_tir14.json`
- `tools/calc_core.py` (defaults de motor)
- `wiki/log.md` (entradas 2026-07-13 a 2026-07-15)
