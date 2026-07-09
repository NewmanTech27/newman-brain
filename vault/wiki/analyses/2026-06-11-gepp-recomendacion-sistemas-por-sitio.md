---
title: "GEPP — Recomendación de sistema por sitio: qué instalar, cuánto ahorra y por qué"
type: analysis
tags: [gepp, reporte-cliente, pv, bess, fp-correction, gdmth, recomendacion]
created: 2026-06-11
updated: 2026-06-11
sources: [2026-06-10-perfil-consumo-gepp-2025-26]
cliente: gepp
status: superado
---

> **Superado (2026-06-14)** por [[2026-06-14-gepp-solucion-energetica-por-proyecto]], que reemplaza el modelo simplificado por el motor determinista (ahorro bruto $63.2M vs $56.9M — el motor capta la reducción de demanda vía umbral), añade el run-rate 2026, ambas estructuras comerciales (Compra vs PPA), proyección a 20 años y los entregables (Excel trazable + propuesta es-MX). Las tablas mensuales de abajo siguen siendo una referencia útil del reparto estacional.

# GEPP — Recomendación de sistema por sitio: qué instalar, cuánto ahorra y por qué

**Pregunta:** Para cada sitio señalado por GEPP (Ixtlahuacán, Acapulco, Cancún y Proplasa), ¿qué sistema de energía conviene — solar (PV), batería (BESS), ambos, o corrección de factor de potencia (FP) — cuánto ahorra, y **por qué** el ahorro es el que es?

> **Grado del análisis:** prefactibilidad. Las cifras provienen del Excel de consumo de GEPP (2025) procesado con el modelo determinista del proyecto ([[2026-06-10-gepp-portfolio-project-check]]); **no están validadas contra recibos CFE**. La validación peso-exacta requiere 12 meses de recibos (PDF/CFDI) por medidor.

---

## Resumen ejecutivo

| Sitio | Sistema recomendado | Ahorro año 1 (neto) | TIR | Payback |
|---|---|---|---|---|
| **Cancún** | Corrección FP + PV 700 kWp (sin batería) | $2.88M | **35.8%** | 3.1 años |
| **Acapulco** | Corrección FP + PV 1,020 kWp + BESS 320 kW/640 kWh | $5.55M | **31.7%** | 3.5 años |
| Proplasa PR1 | PV 1,860 kWp + BESS 360 kW/720 kWh | $6.43M | 24.3% | 4.6 años |
| Proplasa PR2 | PV 5,220 kWp + BESS 1,220 kW/2,440 kWh | $18.43M | 23.6% | 4.7 años |
| Proplasa TAP | PV 3,430 kWp + BESS 790 kW/1,580 kWh | $12.09M | 23.7% | 4.7 años |
| Ixtlahuacán | PV 2,530 kWp + BESS 850 kW/1,700 kWh | $8.54M | 20.4% | 5.5 años |
| **Portafolio** | **14,760 kWp PV + 3,540 kW/7,080 kWh BESS + FP** | **$53.92M/año** | **24.2%** | **4.6 años** |

- CAPEX total: **$275.6M MXN** (~$15.7M USD). VPN @12%: **$296.8M**.
- Ahorro bruto año 0: **$56.93M/año** = PV $44.74M + BESS $9.87M + FP $2.31M — ≈16.6% del gasto eléctrico de los cuatro sitios ($341.9M en 2025).
- El ahorro "neto" descuenta una disponibilidad del 75% (supuesto comercial de tiempo fuera de servicio, no física).

**La lectura en una línea:** los cuatro sitios pagan la electricidad de forma distinta, y por eso el sistema óptimo cambia: donde la energía es cara y hay multa de FP (Acapulco, Cancún) mandan FP+PV; donde el volumen es enorme y los cargos de demanda cobran completo (Proplasa) manda PV grande + batería; donde un cogenerador ya descuenta la energía media parte del año (Ixtlahuacán) el solar sigue ganando, pero menos.

---

## Cómo ahorra cada tecnología en una tarifa GDMTH

Un recibo GDMTH tiene tres bloques que un proyecto puede mover, y **cada tecnología ataca un bloque distinto**:

### 1. Corrección de factor de potencia — elimina una multa

Cuando el factor de potencia de la planta cae **debajo de 90%**, CFE agrega un **cargo FP** (multa) calculado sobre todo el recibo. Un banco de capacitores corrige el FP y la multa **desaparece por completo**. Es el ahorro más simple del portafolio: equipo pasivo, sin permisos, sin interacción con PV o batería, y con retorno en **meses** (capex ≈ $250 mil por sitio contra multas de $0.6–1.7M anuales). Por eso es siempre el primer paso donde existe. *(Las multas de Acapulco y Cancún están impresas en el propio Excel de GEPP — es el dato más duro de este reporte.)*

### 2. Solar (PV) — desplaza energía, no demanda

Cada kWh que generan los paneles es un kWh que la planta **deja de comprar** a CFE (o al suministrador legado). En el sistema interconectado nacional (SIN), el horario punta es **nocturno** (20:00–22:00 verano, 18:00–22:00 invierno), así que el sol genera prácticamente todo en horario **intermedio** ([[horarios-y-divisiones]]): el PV desplaza energía a la tarifa intermedia (~$2.0–2.3/kWh en estos sitios).

Dos consecuencias importantes ([[pv-savings-model]]):
- **El PV no reduce los cargos de demanda (kW)** — la potencia máxima se mide de noche, cuando no hay sol. Por eso el PV solo no basta en sitios donde los kW pesan mucho.
- **Dimensionamos el PV al autoconsumo instantáneo** (≈ la demanda promedio de la planta, cargas planas 24/7): bajo el supuesto del cliente de **cero contraprestación por excedentes**, cada kWh exportado vale $0, así que el sistema se dimensiona para no exportar. Cualquier compensación que sí se obtenga es upside.

### 3. Batería (BESS) — recorta la demanda punta

El **cargo por capacidad** (~25% de un recibo típico) se cobra sobre los kW máximos medidos en horario punta. La batería se descarga exactamente en esas 2–4 horas y **recorta el pico** que ve el medidor: cada kW recortado vale **$4,400–4,800 al año** en estos sitios ([[bess-savings-model]]).

Pero hay un límite estructural: la tarifa tiene un **piso de demanda facturable** (el "umbral", [[demanda-facturable]]). Si el consumo de energía del mes es alto en relación al pico, CFE ya factura ese piso aunque el pico medido baje — y entonces **la batería no ahorra nada ese mes**. Este efecto es decisivo en el portafolio:

| Sitio | Meses (de 12) en que el umbral anula la batería | Veredicto BESS |
|---|---|---|
| Proplasa (3 medidores) | **0** | Mejor sitio para batería — valor completo |
| Acapulco | 2 | Bueno |
| Ixtlahuacán | 3 | Aceptable |
| **Cancún** | **9** | **No instalar batería** |

*(Nota: en el SIN, usar la batería para arbitraje de energía — cargar barato, descargar caro — resultó **negativo** en nuestra corrida validada de Jalisco; el valor de la batería aquí es demanda, no energía.)*

### Por qué PV + BESS suman sin estorbarse

El solar trabaja sobre el bloque de **energía** y la batería sobre el bloque de **demanda** — líneas distintas del recibo. Mientras el umbral no esté saturado, los ahorros son **aditivos** ([[pv-bess-combined]]): instalar ambos rinde la suma de los dos, y por eso la recomendación combinada domina en cinco de los seis medidores.

---

## Por sitio: qué, cuánto y por qué

### Cancún (Peninsular, 1,500 kW) — FP + PV 700 kWp, sin batería

**El proyecto más rentable del portafolio (TIR 35.8%, payback 3.1 años) — y el único sin batería.**

- **Por qué FP:** paga multa de FP **$597,756/año** (FP ~89%, crónico). Se elimina con capacitores.
- **Por qué PV:** es la **electricidad más cara del portafolio** ($3.90/kWh efectivo) y la división Peninsular tiene las tarifas de energía más atractivas para desplazamiento solar (intermedia $2.08, punta $2.32). 700 kWp generan ~1.05 GWh (22% de la carga).
- **Por qué 700 kWp y no más:** debajo de **0.7 MW** el sistema es generación distribuida exenta — **sin permiso**, con [[medicion-neta]] (los excedentes se acreditan en lugar de perderse). Para una carga de 4.75 GWh es además el tamaño proporcionado.
- **Por qué SIN batería:** el umbral satura la demanda facturable **9 de 12 meses** — CFE ya cobra el piso, no el pico medido, así que recortar el pico no cambia el recibo. La batería aquí sería capex sin retorno.

### Acapulco (Centro Sur, 2,271 kW) — FP + PV 1,020 kWp + BESS 320 kW/640 kWh

**El segundo mejor (TIR 31.7%, payback 3.5 años), con los tres palancas activas.**

- **Por qué FP:** la multa más grande del portafolio — **$1,716,053/año** (FP 85–86% **todos los meses**). Es ~6% del recibo, y desaparece con un banco de capacitores. Acción inmediata, sin dependencias.
- **Por qué PV:** segunda electricidad más cara ($3.69/kWh efectivo); 1,020 kWp generan 1.91 GWh (21% de la carga) a tarifa plena CFE.
- **Por qué BESS:** Acapulco es el sitio donde los **cargos de demanda pesan más** — 43% del subtotal del recibo, con la tarifa de distribución más alta del grupo ($221/kW, 2.6× la de Cancún). El umbral casi no estorba (2/12 meses), así que el recorte de pico cobra casi completo.

### Proplasa — PR1, PR2 y TAP (Valle de México Norte, 11,039 kW) — PV 10,510 kWp + BESS 2,370 kW/4,740 kWh

**El juego de volumen: $36.95M/año netos entre los tres medidores (TIR ~24%).**

Proplasa es un solo predio con **tres servicios GDMTH independientes** ante CFE — cada medidor tiene su propia demanda contratada, su propio recibo y su propio piso de demanda facturable, así que el proyecto se dimensiona y evalúa **medidor por medidor**:

| Medidor | Planta | kW contratada | Consumo 2025 | Recibo 2025 | Pico punta (rango) | Piso/umbral (rango) | ENEL 2025* |
|---|---|---|---|---|---|---|---|
| PR1 | Preformas 1 | 2,600 | 16.3 GWh | $37.3M | 1.5–2.3 MW | 2.7–3.7 MW | ~87% |
| PR2 | Preformas 2 (principal) | 5,625 | 45.7 GWh | $118.5M | 4.5–6.7 MW | 7.7–10.6 MW | ~48% |
| TAP | Tapas | 2,814 | 30.0 GWh | $73.7M | 3.1–4.3 MW | 5.2–6.6 MW | ~79% |

\* Participación de ENEL derivada de los bloques del propio Excel (consumo total del medidor menos su bloque CFE).

**Sistema recomendado y resultado por medidor:**

| Medidor | PV kWp | BESS | CAPEX | Ahorro año 1 neto | TIR |
|---|---|---|---|---|---|
| PR1 | 1,860 | 360 kW/720 kWh | $32.7M | $6.43M | 24.3% |
| PR2 | 5,220 | 1,220 kW/2,440 kWh | $96.6M | $18.43M | 23.6% |
| TAP | 3,430 | 790 kW/1,580 kWh | $63.2M | $12.09M | 23.7% |

- **Por qué PV grande:** 92 GWh/año — el mayor consumidor de GEPP. Aunque su $/kWh es el más bajo del grupo (gracias a la energía ENEL a ~$1.8–1.9/kWh), el volumen convierte un ahorro porcentual modesto en el mayor ahorro absoluto del portafolio.
- **El retiro de ENEL fue escalonado — y ya casi terminó** (hallazgo del desglose mensual del Excel): **PR2 colapsó primero** — de ~90% del consumo (ene–may 2025) cayó a ~16% desde sep 2025 y sigue en ~15% en 2026. **PR1 y TAP aguantaron ~90–100% hasta feb 2026 y colapsaron en mar 2026** (PR1 a 28%→25%, TAP a 15%→13% en mar–abr). A abril de 2026 el predio completo ya compra **~85% de su energía a tarifa plena CFE**. Esto refuerza el caso solar: el PV desplaza CFE plena (~$2.1+/kWh), no energía ENEL a ~$1.8 — y el modelo, que valuó a tarifa intermedia CFE, queda del lado correcto. Sigue pendiente preguntar a GEPP la causa del retiro (¿salida estructural rumbo al vencimiento 2032?).
- **Por qué la batería cobra completo aquí (único sitio 0/12):** en los tres medidores el pico de demanda punta queda **muy por debajo** del piso de demanda facturable todos los meses (PR2: picos de 4.5–6.7 MW contra pisos de 7.7–10.6 MW). CFE factura el pico real medido, así que **cada kW que la batería recorta se descuenta 1:1, los 12 meses** — a diferencia de Cancún (9/12 meses anulados) o Ixtlahuacán (3/12).
- **Por qué el PV es ~19% de la carga y no más:** con cero contraprestación por excedentes, el PV se topa al autoconsumo instantáneo de cada medidor — su demanda promedio: PR1 ~1.9 MW, PR2 ~5.2 MW, TAP ~3.4 MW (de ahí los 1,860 / 5,220 / 3,430 kWp). Crecer más allá produciría kWh exportados sin valor bajo el supuesto de cero contraprestación.
- **FP sano** (97–99.5%, recibe bonificaciones): no hay palanca FP en Proplasa.
- **Advertencia de espacio:** los 10,510 kWp requieren ~62,000 m² — casi seguro implica montaje en piso/estacionamientos o recortar el tamaño al techo real disponible.

### Ixtlahuacán (Jalisco, 5,000 kW) — PV 2,530 kWp + BESS 850 kW/1,700 kWh

**Sólido pero estructuralmente el más débil (TIR 20.4%, payback 5.5 años) — por el contrato con Tala.**

- **Por qué PV:** 22.17 GWh/año de carga; 2,530 kWp generan 4.51 GWh (20%).
- **Por qué rinde menos que los demás:** el cogenerador Tala (bagazo) cubre ~100% del consumo **dic–may (zafra)** con un descuento del 10% sobre la energía. En esos meses el solar desplaza energía **ya descontada** (vale 0.9× tarifa CFE); jun–nov desplaza tarifa CFE plena. Además el umbral anula la batería 3 de 12 meses.
- **Por qué BESS de todos modos:** fuera de los meses saturados, el recorte de 850 kW punta cobra a valor casi completo.
- **FP:** sano (93.6–95.7%) — sin palanca FP relevante (~$55k esporádicos).
- **Dos pendientes propios del sitio:** (1) confirmar contractualmente que el PV puede convivir con el porteo de Tala (y si hay mínimos take-or-pay que el solar canibalizaría); (2) auditar los picos de demanda de abr–may 2025 (5,872 y 7,310 kW, **arriba de los 5,000 kW contratados**) — posible exposición de contrato/facturación.

---

## Ahorro mensual por sitio (año 0, bruto)

> **Método:** reconstrucción mensual determinista (`tools/gepp_monthly_savings.py`) con la misma metodología del escenario best-case: la generación solar se reparte con el **perfil mensual real de irradiación** de cada municipio ([[solar-yield-lookup]]), la batería se topa **mes a mes** contra el piso de demanda facturable, y las multas FP son las impresas en el Excel. La suma anual reproduce las cifras ya presentadas con desviación ≤0.2%. Cifras **brutas año 0**; la vista comercial conservadora multiplica PV y BESS por 0.75 de disponibilidad.

**Cómo leer las tablas:**
- **El PV sigue al sol:** marzo–abril son los mejores meses (temporada seca); septiembre es el más bajo (lluvias).
- **La batería es pareja… salvo cuando el umbral satura:** en los meses marcados el piso de demanda facturable absorbe el recorte y la batería no ahorra. (El valor negativo mostrado es el costo modelado de ciclarla de todos modos; en operación real se dejaría en reposo esos meses, ahorro $0.)
- **La multa FP sigue al consumo** del mes — estable todo el año.

### Ixtlahuacán (PV 2,530 kWp + BESS 850 kW)

| Mes | Gen PV MWh | Ahorro PV $ | Ahorro BESS $ | Total $ |
|---|---|---|---|---|
| Ene | 372 | 593,464 | 223,468 | 816,932 |
| Feb | 360 | 574,901 | 223,468 | 798,369 |
| Mar | 457 | 728,570 | 223,468 | 952,037 |
| Abr | 426 | 679,886 | −118,292 ⚠ | 561,595 |
| May | 412 | 656,513 | −118,292 ⚠ | 538,222 |
| Jun | 375 | 663,960 | 223,468 | 887,428 |
| Jul | 351 | 621,597 | 223,468 | 845,065 |
| Ago | 333 | 590,462 | 223,468 | 813,930 |
| Sep | 321 | 568,186 | 223,468 | 791,654 |
| Oct | 371 | 658,292 | 223,468 | 881,760 |
| Nov | 384 | 681,178 | 223,468 | 904,646 |
| Dic | 350 | 558,437 | −118,292 ⚠ | 440,145 |
| **Año** | **4,512** | **$7,575,446** | **$1,656,335** | **$9,231,782** |

⚠ Abr, may y dic son exactamente los meses con **picos de demanda anómalos** (5,896 / 7,008 / 5,731 kW — todos **arriba de los 5,000 kW contratados**): el pico dispara el medidor por encima del piso y el umbral anula a la batería. Si esos picos resultan ser una falla operativa corregible (arranques simultáneos, etc.), la batería ganaría también esos meses — otra razón para auditarlos. El PV de ene–mar y dic vale 0.9× (desplaza energía Tala ya descontada, zafra).

### Acapulco (FP + PV 1,020 kWp + BESS 320 kW)

| Mes     | Gen PV MWh | Ahorro PV $    | Ahorro BESS $ | Ahorro FP $    | Total $        |
| ------- | ---------- | -------------- | ------------- | -------------- | -------------- |
| Ene     | 163        | 278,166        | 72,313        | 137,544        | 488,023        |
| Feb     | 154        | 262,171        | 72,313        | 134,641        | 469,125        |
| Mar     | 188        | 321,360        | 72,313        | 153,664        | 547,337        |
| Abr     | 174        | 297,200        | 72,313        | 148,846        | 518,359        |
| May     | 170        | 289,829        | 72,313        | 143,046        | 505,188        |
| Jun     | 150        | 255,817        | 72,313        | 139,779        | 467,909        |
| Jul     | 160        | 273,415        | 72,313        | 150,699        | 496,427        |
| Ago     | 147        | 250,091        | 72,313        | 147,113        | 469,517        |
| Sep     | 132        | 226,139        | 40,597 ⚠      | 145,342        | 412,079        |
| Oct     | 156        | 266,072        | −14,156 ⚠     | 135,089        | 387,005        |
| Nov     | 157        | 268,775        | 72,313        | 136,386        | 477,475        |
| Dic     | 156        | 266,936        | 72,313        | 143,904        | 483,153        |
| **Año** | **1,907**  | **$3,255,972** | **$749,572**  | **$1,716,053** | **$5,721,596** |

⚠ Sep–oct: el consumo baja y el pico sube, el piso cae por debajo del pico y el recorte de la batería se acredita solo parcialmente (los 2/12 meses saturados del sitio).

### Cancún (FP + PV 700 kWp — sin batería)

| Mes | Gen PV MWh | Ahorro PV $ | Ahorro FP $ | Total $ |
|---|---|---|---|---|
| Ene | 81 | 169,387 | 49,039 | 218,426 |
| Feb | 80 | 165,717 | 45,534 | 211,251 |
| Mar | 98 | 204,781 | 44,272 | 249,053 |
| Abr | 98 | 203,768 | 47,051 | 250,818 |
| May | 98 | 203,337 | 48,308 | 251,645 |
| Jun | 89 | 185,593 | 55,432 | 241,024 |
| Jul | 92 | 191,057 | 55,105 | 246,161 |
| Ago | 86 | 179,500 | 53,077 | 232,576 |
| Sep | 83 | 172,311 | 49,101 | 221,413 |
| Oct | 85 | 177,333 | 53,035 | 230,368 |
| Nov | 81 | 167,418 | 47,771 | 215,189 |
| Dic | 79 | 163,969 | 50,032 | 214,002 |
| **Año** | **1,050** | **$2,184,170** | **$597,756** | **$2,781,926** |

### Proplasa PR1 (PV 1,860 kWp + BESS 360 kW)

| Mes | Gen PV MWh | Ahorro PV $ | Ahorro BESS $ | Total $ |
|---|---|---|---|---|
| Ene | 266 | 483,483 | 94,646 | 578,129 |
| Feb | 259 | 470,811 | 94,646 | 565,457 |
| Mar | 316 | 575,814 | 94,646 | 670,461 |
| Abr | 280 | 510,126 | 94,646 | 604,772 |
| May | 266 | 484,322 | 94,646 | 578,968 |
| Jun | 249 | 453,265 | 94,646 | 547,911 |
| Jul | 251 | 457,462 | 94,646 | 552,108 |
| Ago | 235 | 428,084 | 94,646 | 522,730 |
| Sep | 222 | 404,527 | 94,646 | 499,173 |
| Oct | 245 | 445,711 | 94,646 | 540,357 |
| Nov | 254 | 462,200 | 94,646 | 556,846 |
| Dic | 244 | 443,192 | 94,646 | 537,839 |
| **Año** | **3,088** | **$5,618,997** | **$1,135,753** | **$6,754,750** |

### Proplasa PR2 (PV 5,220 kWp + BESS 1,220 kW)

| Mes | Gen PV MWh | Ahorro PV $ | Ahorro BESS $ | Total $ |
|---|---|---|---|---|
| Ene | 746 | 1,356,871 | 320,745 | 1,677,616 |
| Feb | 726 | 1,321,308 | 320,745 | 1,642,053 |
| Mar | 888 | 1,615,995 | 320,745 | 1,936,741 |
| Abr | 787 | 1,431,645 | 320,745 | 1,752,390 |
| May | 747 | 1,359,226 | 320,745 | 1,679,972 |
| Jun | 699 | 1,272,066 | 320,745 | 1,592,811 |
| Jul | 706 | 1,283,845 | 320,745 | 1,604,590 |
| Ago | 660 | 1,201,396 | 320,745 | 1,522,141 |
| Sep | 624 | 1,135,285 | 320,745 | 1,456,030 |
| Oct | 687 | 1,250,865 | 320,745 | 1,571,610 |
| Nov | 713 | 1,297,143 | 320,745 | 1,617,888 |
| Dic | 684 | 1,243,798 | 320,745 | 1,564,543 |
| **Año** | **8,666** | **$15,769,444** | **$3,848,941** | **$19,618,385** |

### Proplasa TAP (PV 3,430 kWp + BESS 790 kW)

| Mes | Gen PV MWh | Ahorro PV $ | Ahorro BESS $ | Total $ |
|---|---|---|---|---|
| Ene | 490 | 891,584 | 207,696 | 1,099,279 |
| Feb | 477 | 868,216 | 207,696 | 1,075,911 |
| Mar | 584 | 1,061,851 | 207,696 | 1,269,547 |
| Abr | 517 | 940,717 | 207,696 | 1,148,412 |
| May | 491 | 893,132 | 207,696 | 1,100,827 |
| Jun | 459 | 835,860 | 207,696 | 1,043,555 |
| Jul | 464 | 843,599 | 207,696 | 1,051,295 |
| Ago | 434 | 789,423 | 207,696 | 997,119 |
| Sep | 410 | 745,982 | 207,696 | 953,678 |
| Oct | 452 | 821,929 | 207,696 | 1,029,624 |
| Nov | 468 | 852,337 | 207,696 | 1,060,033 |
| Dic | 449 | 817,285 | 207,696 | 1,024,981 |
| **Año** | **5,694** | **$10,361,914** | **$2,492,347** | **$12,854,261** |

### Portafolio — total mensual bruto

| Mes | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic | **Año** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $M | 4.88 | 4.76 | 5.63 | 4.84 | 4.65 | 4.78 | 4.80 | 4.56 | 4.33 | 4.64 | 4.83 | 4.26 | **56.96** |

El mejor mes es **marzo** (pico solar + multas FP altas) y el más bajo **diciembre** (menos sol, PV de Ixtlahuacán a 0.9× por zafra y su batería anulada por el pico anómalo). La banda mensual es estrecha — $4.3–5.6M — porque las cargas son planas y la batería y la multa FP no dependen del clima.

---

## Supuestos que mueven estos números

1. **Datos del Excel del cliente, no de recibos CFE** — consistentes internamente, pero la validación peso-exacta requiere los recibos.
2. **Cero contraprestación por excedentes** (directiva del cliente) — es el piso; cualquier pago por excedentes mejora todos los números. Cancún, en medición neta <0.7 MW, sí acredita excedentes.
3. **Carga plana 24/7 asumida** — si las plantas paran fines de semana, el PV debe achicarse o habrá excedentes sin valor. Los datos de intervalo 15-min lo resuelven.
4. **Permisos de autoconsumo asumidos otorgados** para los sistemas ≥0.7 MW (directiva del cliente); incluyen obligación de respaldo de almacenamiento para PV intermitente — la batería recomendada ayuda a cumplirla.
5. **Convivencia autoabasto legado + generación en sitio** (Ixtlahuacán, Proplasa): físicamente el PV reduce el consumo antes del medidor; la confirmación contractual/regulatoria sigue abierta.
6. Economía a 20 años: WACC 12%, escalación CFE 6%/año, disponibilidad 75%, degradación PV 0.5%/año y BESS 1.25%/año.
7. Las tablas mensuales provienen de la reconstrucción determinista `tools/gepp_monthly_savings.py`; su suma anual ($56.96M bruto) reproduce las bases ya presentadas ($56.93M) con desviación ≤0.2% — la diferencia es el reparto mensual de irradiación, no un cambio de método.

## Siguientes pasos (datos que afinan el proyecto)

1. **12 meses de recibos CFE** (PDF o CFDI XML) de los 6 medidores → validación peso-exacta y corrida del motor de ahorro por sitio.
2. **Datos de medición 15-min** (al menos un día típico de verano e invierno por sitio) → dimensionamiento bancable de batería y verificación del riesgo de fin de semana.
3. **Contratos Tala y ENEL** (volúmenes comprometidos, take-or-pay, costos de porteo, cláusulas de salida; ambos vencen 2032).
4. **Áreas reales de techo/terreno y capacidad de transformadores** por sitio.
5. Arrancar **ya** la corrección FP en Acapulco y Cancún — no depende de nada de lo anterior.

---

## Fuentes consultadas
- [[2026-06-10-gepp-portfolio-project-check]] — análisis cuantitativo completo (prefactibilidad + best case); todas las cifras de este reporte
- [[2026-06-10-perfil-consumo-gepp-2025-26]] — el Excel de GEPP (datos base)
- [[pv-savings-model]] · [[bess-savings-model]] · [[demanda-facturable]] · [[pv-bess-combined]] · [[medicion-neta]] · [[horarios-y-divisiones]] — mecánica de cada palanca
- [[2026-06-09-456220800389-yearly-savings]] — corrida validada del motor (Jalisco) que calibra costo BESS y penalización de arbitraje

## Confidence

**Media.** Niveles de certeza: las **multas FP** ($1.72M + $0.60M) están impresas en el Excel del cliente (dato duro). Los ahorros PV/BESS y la economía son **derivados del modelo** sobre datos del Excel sin validar contra recibos — grado prefactibilidad. La mecánica regulatoria y tarifaria es **confirmada por fuentes primarias** (páginas citadas). Dos incógnitas regulatorias siguen abiertas y están señaladas en el texto (convivencia autoabasto+generación en sitio; lectura por-medidor del límite 0.7 MW).
