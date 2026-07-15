# GEPP — Preguntas Anticipadas

**Documento interno de preparación · Newman · 2026-07-15**
Insumo para la reunión con el equipo de energía de GEPP. Reúne las preguntas que un cliente industrial sofisticado con equipo técnico propio podría hacernos sobre los modelos PV+BESS, cada una con la respuesta más fuerte y honesta que podemos dar. Uso interno — franco sobre supuestos y huecos.

**Convención de etiquetas (fact-tier):**
- **[motor]** — cifra derivada del motor (`dispatch_cs.py` / `calc_core.py` / libros rev4/NR), golden-anclada y verificada.
- **[fuente]** — dato duro del workbook del cliente, contrato, o regla regulatoria con fuente primaria.
- **[supuesto]** — convención editable de Newman (financiera, de sizing o de forma de carga). No es dato del cliente ni salida cruda del motor.

**Números de referencia (config vigente):** el diseño **entregado** es **rev4 "BESS Carga Solar"** (Op1 Autoconsumo, portafolio 4 sitios: ahorro cliente año 1 **$39.13M**, VAN 20a **$411.7M**). El escenario **"Autoconsumo Max" (NR, sin restricción de superficie)** es la cota superior teórica (ahorro año 1 **$57.18M**, VAN 20a **$617.2M**, CAPEX Newman **$510.1M**). Cuando una cifra tiene historia, se usa la vigente y se dice a qué revisión pertenece.

---

## Índice

**Las 5 preguntas clave**
1. ¿Por qué esta configuración es la más eficiente?
2. ¿Por qué esta configuración y no otra?
3. ¿Cómo tomaron los valores de ENEL y TALA?
4. En Ixtlahuacán sólo tomaron CFE como referencia — ¿se afecta cuando TALA salga?
5. ¿Cómo justifican que sus supuestos son correctos?

**A · Metodología y motor** — A1–A9
**B · Umbral energético y demanda** — B1–B3
**C · BESS** — C1–C7
**D · Regulatorio** — D1–D6
**E · Comercial y contractual** — E1–E8
**F · Datos y validación** — F1–F4
**G · Proplasa específico** — G1–G3
**H · Escenario Autoconsumo Max (NR)** — H1–H3

---

## Las 5 preguntas clave

### 1 · ¿Por qué esta configuración es la más eficiente?

**Porque el óptimo es un punto interior demostrado por barrido, no una elección de catálogo.** Cada kWh adicional de generación cae en tres cubetas excluyentes: **(a)** autoconsumo directo (desplaza energía intermedia CFE ≈ tarifa intermedia), **(b)** carga solar del BESS (desplaza carga de red que luego se descarga en punta), y **(c)** excedente remanente que se vende a CFE a nivel mayorista ≈ **$0** [fuente, directiva "cero contraprestación" GEPP]. El techo direccionable es la suma de la carga diurna coincidente con el sol (asintótica) más la energía de carga del BESS `N/RTE` — **no la superficie** [motor]. La clave física: **el requerimiento de carga del BESS es FIJO** (lo fija el lado de descarga en punta, no el sol disponible), así que la cubeta (b) satura rápido; saturadas (a) autoconsumo diurno y (b) carga-solar, cada kWp extra cae en (c) a $0, mientras su CAPEX acarreado a TIR-14% **sube el multiplicador `k`** del PPA (que se paga sobre TODOS los kWh autoconsumidos). El valor marginal para el cliente cruza a negativo → ahí está el pico [motor].

**Evidencia del barrido (Ixtlahuacán, [motor]):** en el óptimo (~5,430 kWp) el BESS está sólo 42% saturado y el autoconsumo diurno cubre 74% de su techo; el $/kWp marginal voltea de **+$67 a −$55** entre 5,450 y 5,600 kWp, cuando la fracción de remanente@$0 sube de 0.17 a 0.22. Acapulco y Cancún hacen pico por saturación de ambas cubetas de valor (la carga-solar del BESS llega al 100%); pasado el óptimo el $/kWp marginal es de **−$900 a −$1,420** [motor]. En los tres sitios el óptimo es interior, verificable, y no depende de una restricción externa.

### 2 · ¿Por qué esta configuración y no otra?

Cada alternativa se probó explícitamente y pierde valor [motor]:

- **Más PV:** más allá del óptimo el kWh cae en remanente@$0 mientras sube el `k`; el ahorro cliente baja (ver P1). El pico es interior en Ixt/Aca/Can.
- **Menos PV:** deja autoconsumo diurno sobre la mesa — el $/kWp marginal antes del óptimo sigue siendo **+$1,000 a +$1,600** [motor], valor que se perdería.
- **Más BESS:** escalando la batería ×1.5/×2/×3 el óptimo kWp **no se mueve** (Δ ≤ +50 kWp) y el ahorro cliente **cae monótonamente**; a ×3 el negocio se vuelve **negativo** en los tres sitios chicos (Ixt −$1.80M, Aca −$1.36M, Can −$0.75M) [motor]. La capacidad `Q` ya está saturada al 100%: más energía de BESS agrega **cero** ahorro de capacidad.
- **Sin BESS (PV-only):** bajo la contabilidad carga-solar el híbrido gana en VAN en **los 4 sitios**; sin BESS se pierden **−$268.2M de VAN de portafolio** (VAN sin-BESS $349.0M vs con-BESS $617.2M en el escenario NR) [motor]. El BESS es la única palanca que toca la punta; el PV no la toca (PV ⊥ punta, invariante del dominio).
- **BESS-only:** no aprovecha el techo de autoconsumo diurno, la mayor fuente de valor; sólo tendría sentido si no hubiera carga diurna coincidente, que no es el caso.
- **GD Medición Neta (Op2) vs Autoconsumo (Op1) por sitio:** Op2 está **topada regulatoriamente a 0.7 MW AC (≈839 kWp DC)** por punto de interconexión, así que en sitios de consumo grande (Ixtlahuacán, Proplasa) Op1 captura mucho más ahorro; en sitios chicos con buena economía de crédito neto (Cancún, Acapulco) Op2 puede dar mejor ROI. Por eso la recomendación es **por sitio**, no uniforme: Op1 en Ixtlahuacán, Op2 en Cancún/Acapulco, Op2 en Proplasa (3 puntos = 3 plantas GD) [motor].

### 3 · ¿Cómo tomaron los valores de ENEL y TALA?

**No los metimos dentro del ahorro del proyecto — los tratamos como una línea aparte y editable.** La línea base de ahorro ("Tarifa Actual") en todos los libros GEPP es **la carga total del sitio valuada a tarifas CFE GDMTH plenas, sin ningún descuento de autoabasto** [fuente, `meta.json` de cada sitio importado]. El beneficio actual de Tala (**10% de descuento ≈ $2.68M/año en Ixtlahuacán 2025**) y de ENEL (precio **$1.78–1.92/kWh**, 69.6% del predio Proplasa en 2025) se muestra en una columna separada — "Beneficio autoabasto (→2032)" — que se resta del CFE bruto para llegar al costo que GEPP paga hoy, pero **nunca se mezcla con el ahorro PV+BESS** [fuente]. Motivo doble: (1) **técnico** — 0/12 meses de la reconstrucción cuadran contra el recibo impreso en los sitios con autoabasto (divergen exactamente por el descuento), así que el CFE pleno es la única base comparable y defendible para dimensionar; (2) **de negocio** — ambos contratos vencen en 2032, y los libros modelan un "cliff" donde el gasto de GEPP salta a CFE pleno; el proyecto ya está dimensionado y valuado contra ese escenario. Los valores de Tala/ENEL provienen del workbook `Perfil de Consumo GEPP 2025-26` del propio cliente [fuente]; no tenemos los contratos, así que volúmenes take-or-pay y cláusulas de salida quedan como preguntas abiertas hacia GEPP.

### 4 · En Ixtlahuacán sólo tomaron CFE como referencia — ¿se afecta el ahorro cuando TALA salga?

**No, y es por diseño, no por descuido.** El ahorro PV+BESS de Ixtlahuacán (**$10.80M/año año 1 en NR; $9.94M en rev4**) [motor] es **el mismo con o sin Tala**, porque el baseline nunca asumió a Tala: ya está construido sobre CFE pleno, que es exactamente el escenario "Tala ya no está". Lo único que cambia cuando Tala se retira es que GEPP deja de disfrutar el descuento de **~$2.68M/año** — un efecto **externo y anterior** al proyecto solar, que en el libro vive en la línea separada "Beneficio autoabasto" y simplemente desaparece a su vencimiento (2032, o antes si Tala sale temprano). El ahorro reportado del proyecto **no se re-trabaja**. La misma lógica aplica simétricamente a Proplasa/ENEL. Narrativa de venta: el PPA fijo del proyecto solar **amortigua** el salto de gasto de 2032 justo cuando ocurre — es un hedge contra la salida del autoabasto, no una víctima de ella.

### 5 · ¿Cómo justifican que sus supuestos son correctos?

Con honestidad sobre el grado: **esto es prefactibilidad, no un modelo bancable — y lo decimos de frente.** Cada supuesto tiene fuente, sensibilidad conocida, y una ruta de validación que lo cierra:

| Supuesto | Valor | Cómo se sostiene / qué lo cerraría |
|---|---|---|
| Yield solar | Índice geográfico municipal (Ixt 1,783 · Aca 1,869 · Can 1,500 · Pro 1,660 kWh/kWp·año) | Validado vs Global Solar Atlas (Cancún ~5–10% conservador). Upgrade a bancable = **HelioScope** por sitio. |
| Forma de carga intradía | Curva de giro "Industrial 24/7" escalada a los kWh B/I/P facturados | Reproduce exacto el mensual; lo que falta es la forma real → **datos 15-min HM** de un día típico verano/invierno por medidor. |
| Yield/PPA/economía | k resuelto por bisección a TIR 14% | Verificado peso-exacto vs `NUMBERS_NR.md` (desviación 0.0000%). |
| Escaladores CFE/PPA | 4% / 4% flat (vigente) | Editable en Supuestos; sensibilidad directa en la proyección 20a. |
| Degradación PV | 0.5%/año | Default de motor; sensibilidad baja en VAN. |
| RTE / DoD / merma BESS | 0.96 / 0.96 / 2 meses/año | Defaults de casa; se ajustan con la ficha técnica del BESS elegido. |
| Superficie (4.0 m²/kWp) | Estándar de casa | Se cierra con **visita técnica** (techo, estructura, sombreado, punto de interconexión). |

**Lo que honestamente aún NO tenemos:** recibos CFE validados peso-exacto en los sitios 100%-CFE, medición 15-min, visita técnica, y confirmación regulatoria de la coexistencia porteo-autoabasto + autoconsumo. Ninguno **invalida** las cifras — las mueven dentro de un rango de prefactibilidad — y la ruta para cerrar cada uno está identificada. Es la conversación honesta que preferimos tener antes de la ingeniería de detalle.

---

## A · Metodología y motor

### A1 · ¿Cómo calculan el ahorro exactamente?

Por sitio y por mes, con un motor determinista [motor]. El **ahorro PV** es `aprov = min(generación × pct_ac, kWh_intermedio del mes)`: el PV sólo desplaza energía del **periodo intermedio** (PV ⊥ punta, invariante del dominio CFE-SIN); el excedente no autoconsumido se valora a `texc ≈ $0` en Autoconsumo o a la tarifa del periodo en Medición Neta. El **ahorro BESS** es arbitraje de demanda y energía: descarga en punta valuada a tarifa punta, menos el costo de recargar. El **ahorro por factor de potencia** (capacitores) es una palanca **separada**, nunca mezclada. Todo se ancla peso-exacto: la corrida reproduce el ahorro NR por sitio con desviación **0.0000%** vs `NUMBERS_NR.md` [motor].

### A2 · ¿Qué es "self-basis" y por qué el PPA se factura sobre el autoconsumo y no sobre toda la generación?

El PPA se cobra únicamente sobre los kWh **efectivamente autoconsumidos** (Op1) o generados-acreditados (Op2), no sobre la generación bruta [motor, convención self-basis, continuidad desde rev3]. Esto protege a GEPP: no paga por electrones que se van a la red a $0. Existe una base alternativa (PPA sobre generación total) reservada para formalización post-aprobación, pero **los libros entregados usan self-basis** por ser la más favorable y transparente para el cliente.

### A3 · ¿Por qué TIR inversionista 14% y no otra?

Es una **concesión deliberada a GEPP**: el estándar de casa Newman es 18%; para este portafolio se bajó a **14.000%** exacto [supuesto comercial + motor]. Bajar la TIR objetivo baja el precio del PPA, así que es directamente ahorro trasladado a GEPP. El 14% se logra resolviendo el multiplicador `k` del PPA por bisección hasta alcanzar esa TIR combinada de portafolio, verificada a 14.00000% en ambas opciones [motor].

### A4 · El precio del PPA ($/kWh), ¿lo asumieron o lo calcularon?

**Se calcula, no se asume.** El multiplicador `k` se resuelve por bisección sobre el flujo de caja exacto del inversionista para alcanzar la TIR objetivo de 14% [motor]. En el diseño rev4 los PPA resultantes son: Ixt **$1.2971**, Aca $1.2375, Can $1.5423, Proplasa $1.3656 /kWh; en el escenario NR (más base PV) **bajan** a Ixt $1.2200, Aca $1.1639, Can $1.4507, Pro $1.2844 — porque una base de generación mayor reparte el retorno del inversionista sobre más kWh (`k` cae de 1.0095 a 0.9495) [motor]. GEPP gana por doble vía: más kWh propios y PPA más barato.

### A5 · ¿Por qué escalación 4% CFE y 4% PPA?

Es un supuesto editable en Supuestos; la versión **vigente (rev3/rev4/NR) usa 4% flat parejo para CFE y PPA** [supuesto]. **Nota interna importante:** hubo tres valores en la historia del proyecto (inicial 6% CFE / 5% PPA → corregido 5% CFE → vigente 4%/4%). Antes de la reunión conviene confirmar **cuál escalador vio GEPP en la última interacción**, para no defender un número que ya cambió. El 4% parejo es conservador vs la inflación tarifaria histórica de CFE y neutro entre las partes (mismo escalador ambos lados).

### A6 · ¿Por qué degradación PV de 0.5%/año?

Es el default del motor [supuesto]. **Nota interna:** el estándar de casa Newman evolucionó después (jul-2026, cliente AFC) a un split **1.0% año 1 + 0.4% años siguientes**; los libros GEPP vigentes **siguen en 0.5% plano**. No es un error — el 0.5% plano es defendible y en 20 años da un resultado similar — pero si GEPP compara notas con otra propuesta Newman más reciente podría notar la diferencia; hay que estar listos para homologar o explicar.

### A7 · ¿Cómo modelan disponibilidad / paros del BESS?

Con una **merma de 2 meses/año sin ahorro de arbitraje** → factor 10/12 (0.833) sobre el ahorro BESS [supuesto]. Es un supuesto conservador de disponibilidad (mantenimiento, indisponibilidad), no física; se afina con la garantía de disponibilidad del proveedor del BESS.

### A8 · ¿Qué RTE y DoD usan?

RTE (eficiencia de ida y vuelta) **0.96** y DoD (profundidad de descarga usable) **0.96**, con `E_útil = kWh × DoD × √RTE` [supuesto, defaults de casa]. Son valores de LFP moderno; se reemplazan por la ficha técnica del equipo específico en ingeniería de detalle. La carga se dimensiona como `carga = descarga / RTE`.

### A9 · Horizonte de 20 años — ¿qué pasa con el ahorro después del PPA?

El PPA corre **15 años** (editable, independiente del plazo BESS); la proyección es a **20 años**. Tras la transferencia del activo, **GEPP conserva el 100% del ahorro PV en los años 16–20** [supuesto comercial]. Ese cambio de estructura es parte del VAN 20a reportado ($411.7M rev4 / $617.2M NR).

---

## B · Umbral energético y demanda

### B1 · Si meto más PV, ¿no colapsa el umbral y mata el ahorro de demanda del BESS?

Es la pregunta correcta y la auditamos [motor]. Sí existe el efecto: más PV baja `kWh_red`, colapsa el umbral `= kWh_red/(d·0.57·24)`, baja la base de demanda facturable y **canibaliza** parte del ahorro de demanda del BESS. La magnitud rev4→NR es **modesta**: `dem_bess` cae Ixt −1.9%, **Aca −10%** (peor caso), Can −4.7%, Proplasa −9.5% [motor]. Es real (no-aditividad PV-BESS), pero **no cambia el orden de magnitud** ni el veredicto CON BESS.

### B2 · Entonces, ¿el libro sobrestima o subestima la demanda?

**Subestima levemente — el libro es conservador.** El escalado lineal + `Q` fija del deck da una demanda total **−3.0% por debajo** de la mecánica verdadera de `calc_core` con umbral golden (**−$1.8M/año de portafolio**), por sitio de −1.4% a −3.4% [motor]. La única excepción es Preforma 1 (Proplasa), donde el libro sobreestima +5.6%. El acierto viene de una compensación: al subir la penetración PV, la componente de distribución sube mientras la de capacidad baja, y el método captura la suma dentro de ±3%. En resumen: si el número tuviera un sesgo, es **a favor de GEPP** (subestima el ahorro de demanda).

### B3 · ¿Y los picos de demanda anómalos de Ixtlahuacán?

Ixtlahuacán mostró picos de **5,872–7,310 kW en Abr/May/Dic-2025**, por encima de los 5,000 kW contratados [fuente, workbook]. No lo hemos verificado contra recibo CFE real; puede ser evento operativo (arranques simultáneos), artefacto de medición, o exposición a penalización por demanda. Es una pregunta abierta hacia GEPP: si es corregible o es penalización real, el BESS gana meses adicionales de valor. No lo dimos por sentado en el modelo.

---

## C · BESS

### C1 · ¿Por qué ese tamaño de BESS y no más grande?

Porque su capacidad `Q` ya está **saturada al 100%** en los 4 sitios: más energía de BESS agrega **cero** ahorro de capacidad [motor]. Escalando ×1.5/×2/×3 el óptimo kWp no se mueve y el ahorro cliente cae monótonamente hasta volverse negativo a ×3. El BESS está dimensionado para **rasurar la punta** (el `N` anual que descarga), y ese `N` está limitado por la energía de punta a desplazar, no por cuánta batería se instale. El BESS entregado es, si acaso, ligeramente generoso — no corto.

### C2 · ¿Por qué cargan el BESS con solar y no de la red?

Es el cambio central de rev4 [motor]. El BESS se carga **primero con excedente solar de mediodía** (limitado por la potencia del inversor y por el excedente real del día), y sólo el faltante se toma de la red en horario base (0–5h). Beneficio: bajo carga solar el ciclo del BESS es **casi gratis** (el excedente valía $0), así que el arbitraje punta-base ya no compite contra un costo de carga. Ese bono es lo que **revierte** el veredicto anterior (donde sin-BESS ganaba en 3 sitios) a **CON BESS en los 4**.

### C3 · ¿Qué porcentaje de la carga del BESS es realmente solar?

Honestamente, **una fracción, no el 100%**: Ixt 30.5%, Aca 18.3%, Can 27.7%, Proplasa 0% (sin headroom de techo) [motor]. El bono de carga solar entregado (rev4) es **+$954,437/año de portafolio** — importante: un análisis preliminar (14-jul) estimó hasta **+$3.08M/año** asumiendo carga solar del 100%; **ese techo no es real**, el motor de despacho entrega la cifra menor. Si GEPP escuchó la cifra preliminar en alguna llamada, hay que corregir a $954k. En el escenario NR (más PV) el bono sube a ~$2.97M/año [motor].

### C4 · Ciclos, degradación y garantía del BESS

Degradación modelada **1.25%/año** [supuesto, default]; el BESS hace un ciclo diario de rasurado de punta. La garantía específica (ciclos, retención de capacidad, disponibilidad) se ata a la ficha técnica del equipo elegido en ingeniería de detalle — el modelo usa defaults conservadores que se reemplazan por los términos reales del proveedor. La merma de 2 meses/año (P-A7) ya castiga la disponibilidad.

### C5 · ¿Qué pasa en invierno, cuando hay menos sol?

El motor modela **día típico de invierno y de verano por separado** [motor], así que la estacionalidad ya está en las cifras. En invierno el excedente solar disponible para cargar el BESS baja (por eso la carga-solar es una fracción, no el 100%), y el faltante se cubre de red en horario base — el BESS sigue rasurando punta. El horario de punta en invierno (18:00–22:00 SIN) también cambia vs verano (20:00–22:00), y el motor lo respeta. La estacionalidad de Tala (zafra Dic–May) es de suministro, no afecta el despacho del proyecto solar.

### C6 · Para más de 0.7 MW intermitente, la regulación exige respaldo. ¿El BESS cumple?

El BESS es precisamente la respuesta a ese mandato [fuente, DACG autoconsumo Núm. 4.5]: un generador intermitente ≥0.7 MW bajo autoconsumo debe contratar **SAE (almacenamiento) o respaldo CFE**. El BESS del proyecto sirve como ese almacenamiento **y** genera arbitraje. **Caveat honesto:** no hemos modelado el costo de la alternativa (respaldo CFE contratado); un análisis del 15-jul encontró que si sólo se contara arbitraje puro con carga de red, en 3 de 6 sitios el mejor VAN sería sin BESS — pero bajo carga solar (rev4), CON BESS gana en los 4, y ese costo de respaldo evitado lo refuerza aún más.

### C7 · ¿Por qué la batería rinde menos que su TIR estándar?

Respuesta honesta: con el **split de participación BESS 50/50** (inversionista/cliente) que estamos usando, la TIR del BESS aislado queda en **8.1%–13.5% según sitio**, por debajo del estándar de 16% del financiador [motor/supuesto]. Es un hallazgo abierto, no resuelto automáticamente: para llevar el BESS a su TIR estándar habría que renegociar el split (57–72% a favor del inversionista) o repreciar. Lo mencionamos porque un CFO agudo lo va a ver; la respuesta correcta es que el BESS se justifica por su contribución al **VAN combinado del portafolio** (+$268M vs sin BESS), no como activo aislado.

---

## D · Regulatorio

### D1 · 0.7 MW GD exento vs autoconsumo — ¿cuál aplica a cada sitio?

Debajo de **0.7 MW AC (≈839 kWp DC)** por punto de interconexión, el sitio es **generador exento** en medición neta, sin permiso (Op2) [fuente, LSE 2025, DOF 18-mar-2025]. Arriba de 0.7 MW entra la figura de **autoconsumo**: permiso simplificado CNE (0.7–20 MW), excedentes vendidos sólo a CFE, y respaldo/almacenamiento obligatorio si es intermitente (Op1) [fuente, DACG CNE, DOF 12-dic-2025]. Por eso Op2 está capada a 839 kWp y Op1 puede crecer hasta la economía o el techo de 20 MW.

### D2 · ¿Y el tope de 20 MW?

Es el **techo regulatorio duro** por sitio: más allá de 20 MW se requiere permiso ordinario [fuente]. Sólo liga en el escenario NR de Proplasa, donde el óptimo económico estaría **por encima** de 20 MW — ahí el "pico" es el tope regulatorio, no economía (la curva de ahorro aún subía) [motor]. En los demás sitios liga antes la economía o la superficie.

### D3 · ¿Un porteo de autoabasto legado puede coexistir con autoconsumo/medición neta en el mismo medidor?

**Honestamente, sin precedente confirmado.** Es el hueco regulatorio más repetido del proyecto GEPP y afecta por igual a Ixtlahuacán (Tala) y Proplasa (ENEL) [flagged, no asumido]. Ya está formulada como pregunta explícita hacia GEPP: si su área legal/regulatoria tiene postura o precedente dentro del grupo. No lo dimos por resuelto en el modelo; es un tema a cerrar antes de comprometerse.

### D4 · Permisos e interconexión — ¿tiempos?

El proceso <0.7 MW es solicitud → estudio → contrato → inspección → sincronización, con clases BT/MT1/MT2 y la **regla de hosting del 80% del transformador** [fuente]. Los tiempos dependen de CFE/CNE por sitio y no los hemos comprometido; para autoconsumo (>0.7 MW) se suma el permiso CNE simplificado. La **capacidad de transformador** por servicio no está verificada — cualquier kWp adicional puede requerir revisión del punto de interconexión. Es parte del alcance de la visita técnica.

### D5 · En Proplasa, ¿el techo de 0.7 MW se lee por medidor o por predio?

**No confirmado — lo tenemos flagged.** El modelo asume "3× exento" (0.7 MW por cada uno de los 3 medidores, tratados como 3 plantas GD) [supuesto], lo que sostiene la recomendación Op2 en Proplasa. Pero si CNE/CFE lo leen **por centro de carga** (un predio = un tope de 0.7 MW), la estrategia cambia. Es una pregunta explícita hacia el área regulatoria de GEPP; no está resuelta.

### D6 · La directiva de "cero contraprestación" por excedentes, ¿es real o conservadora?

La tratamos como restricción real por directiva de GEPP: el excedente en Autoconsumo se valora a **≈$0** (venta a CFE a nivel mayorista/PML) [fuente, directiva del cliente]. **Pero es una palanca:** si GEPP aceptara el mecanismo de excedentes con CFE, se podría crecer el PV por encima del autoconsumo instantáneo y mejorar la economía. Está formulado como pregunta hacia ellos — si "cero contraprestación" es política firme o supuesto conservador de planeación.

---

## E · Comercial y contractual

### E1 · ¿Cuál es el plazo del contrato?

PPA de **15 años** (editable en Supuestos), con proyección y beneficio a **20 años** [supuesto comercial]. El plazo del BESS es independiente y también editable. Tras el PPA, GEPP conserva el 100% del ahorro PV (años 16–20).

### E2 · ¿Quién es dueño del activo?

Depende de la estructura que GEPP prefiera — es una pregunta abierta hacia ellos: **ser dueño** (CAPEX propio, mejor TIR, activo en balance) o **ahorro-como-servicio / PPA** (fuera de balance, Newman/inversionista es dueño y transfiere el activo al final). El modelo vigente asume la estructura PPA con transferencia. La "Inversión estimada Newman" (CAPEX) es **$510.1M** en el escenario NR [motor].

### E3 · ¿Qué pasa en el año 21?

El activo ya fue transferido a GEPP (en el modelo PPA) y sigue generando; GEPP conserva el 100% del ahorro. La vida útil del PV excede 20 años (con degradación 0.5%/año, retiene >90% de capacidad), así que hay cola de valor post-modelo que no se cuenta en el VAN reportado — es upside conservador.

### E4 · ¿Hay opción de compra anticipada (buyout)?

Es un término a estructurar con GEPP, no fijado en el modelo actual. En una estructura PPA típica se ofrece un calendario de buyout; no está cuantificado en los libros entregados. Punto a definir en la mesa comercial.

### E5 · O&M y garantías, ¿quién los cubre?

En la estructura PPA, el inversionista/Newman cubre O&M durante el plazo (está en el flujo del inversionista que fija el PPA). Las garantías de equipo (PV, inversores, BESS) son las del fabricante y se atan en ingeniería de detalle. El costo de fianza del PPA (13.9%) está en el modelo [supuesto].

### E6 · ¿Qué pasa si mi consumo cambia — crece o baja?

Es una sensibilidad clave y honesta. El dimensionamiento está atado al **autoconsumo diurno coincidente**: si el consumo diurno **crece**, sube el techo de autoconsumo y el proyecto puede crecer (más valor); si **baja**, más generación cae en excedente@$0 y el ahorro por kWh baja. Bajo self-basis GEPP no paga PPA sobre kWh que no autoconsume, así que está parcialmente protegido a la baja. Con datos 15-min reales y el perfil de crecimiento de GEPP se afina el sizing para que sea robusto a su plan de negocio. Es exactamente por qué pedimos su perfil de operación.

### E7 · ¿Qué pasa si CFE cambia las tarifas?

El baseline y el ahorro se recalculan con las tarifas vigentes; el modelo usa escalación CFE de 4%/año [supuesto], conservadora vs la inflación tarifaria histórica. Un alza de CFE **aumenta** el valor del proyecto (más ahorro desplazado); una baja lo reduce. El PPA fijo con escalador propio (4%) da a GEPP visibilidad y cobertura contra la volatilidad tarifaria de CFE — es parte del valor del hedge, especialmente frente al cliff de autoabasto 2032.

### E8 · ¿Quién asume el riesgo de curtailment o falla del sistema?

En la estructura PPA (self-basis), GEPP paga sobre kWh **efectivamente autoconsumidos**: si el sistema no genera (falla, curtailment), no hay kWh que cobrar, así que el riesgo de generación recae en el inversionista/Newman, no en GEPP. La disponibilidad del BESS ya está castigada (merma 2 meses/año). Las garantías de disponibilidad y penalizaciones específicas se fijan en el contrato.

---

## F · Datos y validación

### F1 · ¿Por qué 12 meses de recibos es suficiente?

12 meses capturan el ciclo estacional completo (zafra de Tala, temporada de bebida, verano/invierno tarifario) [fuente]. Es suficiente para **dimensionar a grado prefactibilidad** con confianza en los kWh mensuales B/I/P. Lo que **no** capturan es la forma intradía (para eso hacen falta datos 15-min) ni la validación peso-exacta contra recibo CFE impreso en los sitios 100%-CFE. Por eso el entregable es explícitamente prefactibilidad, no bancable.

### F2 · ¿Qué cambiaría con datos de intervalo de 15 minutos (HM)?

Volvería el dimensionamiento **bancable**. Hoy la forma intradía (el `pct_ac` de autoconsumo, el reparto carga-solar/carga-base del BESS, el techo diurno) es una curva de giro genérica "Industrial 24/7" escalada a los kWh facturados, no la curva real del sitio [supuesto]. Con 15-min HM — aunque sea un día típico de verano y uno de invierno por medidor — se reemplaza el supuesto por dato real y se afina el tamaño de PV y BESS. Es la brecha de bancabilidad más citada en todos los análisis GEPP.

### F3 · ¿Qué incluye la visita técnica?

Confirmar los supuestos de sitio que hoy son estándar de casa: área de techo/terreno disponible y su capacidad estructural (hoy 4.0 m²/kWp), sombreado real, capacidad del transformador y del punto de interconexión (regla de hosting 80%), y si los inmuebles son propios o arrendados (plazo de arrendamiento vs vida de activo 20a). Cierra los huecos de superficie e interconexión — críticos en Acapulco y Proplasa (ver H2).

### F4 · ¿Por qué llaman a esto "prefactibilidad" y no un modelo final?

Por disciplina y honestidad. Prefactibilidad = datos mensuales del cliente + curvas sintéticas + supuestos de casa, sin medición horaria ni visita técnica. Es suficiente para decidir **si vale la pena** y para dimensionar de forma defendible, pero antes de comprometer ingeniería y capital se cierran las tres brechas (15-min, visita, coexistencia regulatoria). Preferimos nombrarlo así que sobre-vender un número como bancable cuando no lo es.

---

## G · Proplasa específico

### G1 · Los 20 MW de Proplasa en el escenario Max — ¿es real?

**No, es explícitamente una cota teórica y así hay que presentarlo.** El consumo del complejo Proplasa es tan grande que su óptimo económico standalone quedaría por encima de 20 MW; el modelo **trunca en el tope regulatorio de 20 MW**, y aun ahí la curva de ahorro seguía subiendo [motor]. Requeriría **64,604 m² adicionales** de superficie que el predio no tiene. El framing correcto: "**potencial adicional si existiera la superficie**", no un diseño ejecutable. El diseño ejecutable rev4 de Proplasa es 3,849 kWp (100% del techo disponible usado).

### G2 · ENEL colapsó de ~90% a ~16% en 2026 — ¿qué implica para el modelo?

El colapso de cobertura ENEL (de ~55% Ene–Feb a ~16% Mar–Abr 2026, escalonado por medidor) es real pero de **causa desconocida** [fuente, flagged]. Es una pregunta explícita hacia GEPP: ¿incumplimiento estructural del suministrador o decisión estratégica de GEPP? Determina si el PV en Proplasa desplaza energía cara (CFE, ya ocurriendo) o barata (ENEL, escenario pasado). El ahorro reportado del proyecto **no depende** de la respuesta, porque el baseline es CFE pleno (ver P3/P4), pero la respuesta afina la narrativa comercial.

### G3 · ¿Por qué modelan Proplasa de dos formas (per-medidor y consolidado)?

Porque es un predio con **3 medidores/RPU** (Preforma 1, Preforma 2, Tapa), y el régimen regulatorio depende de si el techo de 0.7 MW se lee por medidor o por predio (ver D5). El portafolio suma **sólo la vista consolidada** (`pro`) para no doble-contar; las pestañas per-medidor son ilustrativas de cómo se reparte por punto de interconexión y usan el mismo `k` de precio. Los 3 puntos de interconexión son lo que permite, bajo la lectura per-medidor, desplegar 3 plantas GD Op2.

---

## H · Escenario Autoconsumo Max (NR)

### H1 · ¿Qué es el escenario "sin restricción de superficie"?

Es la variante de Op1 donde la superficie de techo **no es la restricción**: cada sitio se dimensiona a su óptimo económico standalone (o al tope regulatorio de 20 MW) [motor]. Muestra el **potencial** del portafolio si hubiera techo/terreno: ahorro cliente año 1 **$57.18M** (vs $39.13M rev4), VAN 20a **$617.2M** (vs $411.7M), cobertura 39.3% del consumo (vs 16.6%), CAPEX Newman **$510.1M**. Es cota superior, no propuesta ejecutable — sirve para enmarcar cuánto valor deja sobre la mesa la falta de superficie.

### H2 · ¿Dónde falta superficie y cuánta?

Sólo dos sitios topan superficie en el escenario Max [motor]: **Acapulco** necesita **2,061 m² adicionales** (óptimo 2,270 kWp vs 7,019 m² disponibles) y **Proplasa** necesita **64,604 m²** adicionales (masivamente inviable en el predio). Ixtlahuacán (25,308 m² disponibles) y Cancún (6,828 m²) **sí alcanzan** su óptimo con el techo actual. Por eso el diseño ejecutable (rev4) capa Acapulco y Proplasa a su superficie real, y el escenario Max sólo ilustra el upside.

### H3 · ¿Cómo se validaría el escenario Max?

Con la **visita técnica** (F3): confirmar techo/terreno realmente disponible, estructura, y punto de interconexión para el kWp ampliado, más la revisión de capacidad de transformador. Para Acapulco, ver si hay ~2,061 m² adicionales (piso, carport, terreno anexo); para Proplasa, el escenario 20 MW simplemente no cabe en el predio y no debe presentarse como ejecutable. Cualquier kWp por encima del diseño rev4 requiere esa validación antes de comprometerse.

---

*Documento interno de preparación — Newman · 2026-07-15. Cifras vigentes: diseño entregado rev4 "BESS Carga Solar" y escenario Autoconsumo Max (NR). Grado prefactibilidad. No distribuir al cliente.*
