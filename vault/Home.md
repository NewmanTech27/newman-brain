---
cssclasses: [cfe-dashboard]
updated: 2026-06-12
---

> [!tip]+ ⚡ CFE Brain — Segundo Cerebro
> **Wiki LLM + motor determinístico de ahorros PV/BESS bajo regulación CFE.**
> Los números salen del motor (golden-validado al centavo); la lógica sale del wiki (fuentes primarias curadas). Nunca de memoria.

> [!grid]
> > [!info] 🧭 [[OS - Centro de Mando|Centro de Mando]]
> > Reglas no negociables, mapa completo de capacidades y límites honestos.
>
> > [!info] 🗂️ [[index|Índice maestro]]
> > Catálogo de las ~85 páginas del wiki, organizado por tema.
>
> > [!info] 🧠 [[overview|Tesis]]
> > El panorama regulatorio completo y los **huecos abiertos**.
>
> > [!info] 📜 [[log|Bitácora]]
> > Registro cronológico append-only (lo más nuevo, al final).

## 📊 Últimos análisis

![[analyses.base#Recientes]]

→ Tabla completa: [[analyses.base|todos los análisis]] · plantilla: [[_TEMPLATE-yearly-savings]]

## 📚 Fuentes recientes

![[sources.base#Recientes]]

→ Biblioteca completa: [[sources.base]]

## 🏢 Clientes y servicios activos

![[entities.base#Clientes]]

| RPU | Sitio | Recibos | Formato |
|---|---|---|---|
| 456220800389 | Planta industrial, Tototlán, Jalisco | 12 meses | CFDI XML |
| 780881200029 | [[grupo-posadas\|Grupo Posadas]] — resort, Zona Hotelera Cancún | 12 meses | PDF |

## 🔧 Catálogo de equipos

![[equipment.base#Catálogo]]

## ⚠️ Pendientes y vigencia

> [!warning] Antes de confiar en un número
> - **Huecos abiertos:** [[overview]] §Open gaps — leerlos antes de declarar algo "confirmado".
> - **[[rate-inputs]] caduca mensualmente** — revisa su `updated:` contra el mes que necesitas.
> - Análisis con estado `superado` en la tabla de arriba ya fueron corregidos por una versión posterior — usa la vigente.

## 🗣️ Cómo pedir cosas

| Necesito… | Digo… |
|---|---|
| Análisis de ahorro anual | recibos a `raw/bills/<RPU>/` + *"analiza ahorros"* |
| Propuesta cliente lista para enviar | *"genera la propuesta para <RPU>"* |
| Cotizar el PPA del deal | *"cotiza el PPA de <RPU> a TIR X%"* |
| Veredicto de viabilidad | describir el proyecto + *"project check"* |
| Auditar números de terceros | *"audita este modelo"* + archivo |
| Ingerir una fuente | archivo a `raw/` + *"ingest <archivo>"* |
| Pregunta regulatoria / técnica | la pregunta, sin más |
| Salud del sistema | *"lint"* — o el atajo `/lint` |
| Portafolio completo (todos los RPU) | doble clic a `CFE Brain OS.bat` → *Portafolio* |
| Reporte ejecutivo para dirección | *"genera el reporte ejecutivo"* → `entregables/reportes/` |
| Pregunta rápida desde el navegador | pestaña **Chat** de la webapp (`/chat`) — cita el wiki, no modifica nada |

> [!tip] 🖥️ Interfaz visual
> Doble clic a **`CFE Brain OS.bat`** (raíz) → dashboard + portafolio + cotizador + **chat** en el navegador, 100% local.
> Todo lo que el sistema produce para humanos cae en **`entregables/`** (propuestas · calculadoras · reportes).

> [!example] Atajos de Claude Code
> `/daily` brief de sesión · `/capture` nota rápida a `raw/notes/` · `/lint` health check · `/refresh-dashboard` audita este tablero
