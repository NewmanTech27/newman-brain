# CFE Brain OS — Centro de Mando

*El sistema operativo de la empresa para PPAs, PV y BESS bajo regulación mexicana.
Una página: qué puede hacer el sistema, cómo pedirlo, y qué produce.
Actualizado: 2026-06-12.*

**Principio rector:** los números salen del motor determinístico (golden-validado al
centavo), la lógica sale del wiki (fuentes primarias curadas). Nunca de memoria.

*Vista rápida del sistema (tablero visual con datos en vivo): [[Home]].*

---

## Mapa de capacidades

| Necesito… | Cómo lo pido | Qué corre | Qué produce |
|---|---|---|---|
| **Análisis de ahorro anual** de un servicio (PV/BESS/Híbrido) | Subo recibos a `raw/bills/<RPU>/` y digo *"analiza ahorros"* | subagente `cfe-savings-analyst` → `tools/cfe_savings` | Tabla mensual + 3 escenarios + finanzas; página en `wiki/analyses/` |
| **Propuesta cliente** (es-MX, lista para enviar) | *"genera la propuesta para <RPU>"* | subagente `proposal-writer` → `tools/make_proposal.py` | `entregables/propuestas/Propuesta - <RPU>.md` (docx/pdf a pedido) |
| **Portafolio completo** — todos los servicios de un jalón | doble clic a `CFE Brain OS.bat` → *Portafolio* — o `python tools/portfolio.py` | `tools/portfolio.py` (mismo calc_core) | Ahorro agregado + ranking de palancas por RPU; recibos que no cuadran quedan excluidos y marcados |
| **Reporte ejecutivo** (para dirección) | *"genera el reporte ejecutivo"* — o `python tools/make_executive_report.py` | portafolio en vivo + caso GEPP archivado | `entregables/reportes/Reporte Ejecutivo - CFE Brain OS.html` (standalone, enviable) |
| **Cotizar el PPA** — ¿a qué $/kWh sale el deal? | *"cotiza el PPA de <RPU> a TIR X%"* | subagente `ppa-deal-pricer` → `tools/ppa_pricer.py` | Tarifa PPA (o comisión) resuelta + sensibilidad plazo/escalación + vista cliente |
| **¿Es viable el proyecto?** (técnica + legal) | Describo el proyecto y digo *"project check"* | subagente `project-checker` (Workflow 5: 7 capas) | Veredicto + obligaciones + riesgos; página en `wiki/analyses/` |
| **Auditar números de terceros** (propuesta rival, Excel del cliente) | *"audita este modelo"* + el archivo | subagente `financial-auditor` (Workflow 6) | Tabla claim-vs-engine con cada delta clasificado |
| **Interfaz del OS** (dashboard + portafolio + cotizador + chat) | **doble clic a `CFE Brain OS.bat`** (o `python tools/webapp/server.py`) → http://127.0.0.1:8765 | mismo `calc_core` que todo lo demás | `/` = centro de mando (stats en vivo, ahorro identificado, golden test) · `/portafolio` = todos los RPU · `/cotizador` = drag & drop, escenarios, solver PPA, propuesta · `/chat` = webchat |
| **Preguntar desde el navegador** (normas, proyectos, reglas) | pestaña *Chat* de la webapp (`/chat`) | `claude -p` (Claude Code CLI) con cwd = vault; herramientas Read/Grep/Glob/Bash(python) | Respuesta con citas `[[página]]` y niveles de hecho; puede correr el motor; **no modifica archivos** |
| **Excel calculadora llenada** | *"llena la calculadora de <RPU>"* | `tools/fill_calculadora.py` | `entregables/calculadoras/Calculadora - <RPU>.xlsx` (espejo exacto del motor) |
| **Sitio chico GDMTO / PDBT** | Pestaña *GDMTO/PDBT* del webapp, o *"corre tarifa_flat"* | `tools/tarifa_flat.py` | Ahorro PV + demanda (prefactibilidad; filas manuales) |
| **Bajar recibos del portal CFE** | *"descarga los recibos de <RPU>"* | skill `cfe-bill-downloader` (Chrome) | XML+PDF en `raw/bills/<RPU>/` |
| **Ingerir una fuente** (DACG, datasheet, paper) | Archivo a `raw/` + *"ingest <archivo>"* | Workflow 1 | Página fuente + 5–15 páginas wiki actualizadas |
| **Pregunta regulatoria/técnica** | La pregunta, sin más | Workflow 2 (wiki primero) | Respuesta con niveles de hecho y citas `[[página]]` |
| **Salud del sistema** | *"lint"* o *"health check"* | Workflow 3 | Lista de contradicciones, datos vencidos, huecos |

---

## Las reglas que no se negocian

1. **Recibo que no cuadra (>0.5%) detiene todo** — probable error de CFE; se
   reporta, no se construye encima.
2. **Golden test sagrado** — cualquier cambio al motor corre el test del RPU
   780881200029 antes y después (peso-exacto, 18 checks).
3. **TIR proyecto ≠ TIR financiador** — la primera dice si vale la pena construir;
   la segunda depende del deal (y ahora se *resuelve* con el PPA pricer, no se asume).
4. **Corrección FP = palanca separada** — nunca mezclada en la atribución PV/BESS.
   Suele ser el ROI más alto del stack.
5. **Niveles de hecho en toda respuesta** — fuente-confirmado / derivado-del-motor /
   supuesto.
6. **`raw/` es inmutable** — fuentes originales nunca se tocan.

---

## Límites honestos (hoy)

- **Tarifas no-SIN** (BC/BCS): horarios codificados y reconciliados con el wiki,
  pero sin sitio real validado — primer cliente BC/BCS requiere validación con recibo.
- **GDMTO/PDBT sin parser** — el modelo existe, las filas se capturan a mano hasta
  que caiga el primer recibo real de esas tarifas.
- **Prefactibilidad vs bancable** — rendimiento municipal + curva por giro son
  supuestos; datos 15-min del medidor HM o Helioscope los vuelven bancables
  (la mejora #1 pendiente del sistema).
- **Análisis regulatorio, no opinión legal** — abogado en el loop para trámites.
- **[[rate-inputs]] caduca mensualmente** — los recibos son la verdad de su propio mes.
- Huecos abiertos: ver [[overview]] §Open gaps.

---

## Anatomía (dónde vive cada cosa)

- `CLAUDE.md` — contrato del agente: invariantes de dominio, workflows 1–7, doctrina
- `wiki/` — el conocimiento: billing, optimization, eligibility, equipment, sources, analyses
- `tools/cfe_savings/` — motor GDMTH (PDF/XML → ahorros; golden-tested)
- `tools/calc_core.py` — núcleo compartido (Excel = CLI = webapp = mismo número)
- `tools/ppa_pricer.py` · `tools/make_proposal.py` · `tools/tarifa_flat.py` — deal, propuesta, tarifas planas
- `tools/webapp/` — interfaz del OS: dashboard (`os.html`) + portafolio (`portfolio.html`) + cotizador (`index.html`) + chat (`chat.html`, vía Claude Code CLI); todo local — launcher: `CFE Brain OS.bat`
- `.claude/agents/` — los 5 subagentes especializados
- `raw/` — fuentes inmutables; `raw/bills/<RPU>/` los recibos por servicio
- `entregables/` — **todo lo que sale para humanos**: `propuestas/` · `calculadoras/` · `reportes/` (la raíz queda limpia)
