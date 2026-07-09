---
title: "CFE Brain OS — consolidación + capa de deals (PPA pricer, proposal factory, GDMTO/PDBT, webapp v2)"
type: analysis
tags: [meta, build, ppa, tools]
created: 2026-06-11
updated: 2026-06-11
sources: []
status: vigente
---

# CFE Brain OS — el sistema operativo de la empresa

**Question:** "Create my whole, complete AI operating system for my company — PPAs,
PV and BESS: models, simulations, savings, financial runs, technical/legal viability
under Mexican rules." Decisiones del usuario: fase consolidación→extensión; PPA
pricing model completo; prioridades = proposal factory, GDMTO/PDBT, interfaz; ambas
interfaces (Claude + webapp) con paridad.

## Answer

El sistema ya existía en un ~70% (motor v2 golden-tested, calculadora genérica,
auto-fill, webapp, curvas). Esta build agregó la capa que faltaba — **deals y
operación** — y consolidó todo bajo un front door.

### Construido (todo validado)

1. **PPA pricer** (`tools/ppa_pricer.py`, subagente `ppa-deal-pricer`, Workflow 7
   en CLAUDE.md): dado un TIR financiador objetivo, **resuelve** la tarifa PPA
   $/kWh (o la comisión BESS) por bisección sobre el flujo financiador exacto de
   `calc_core._finance` (reproducción validada a 1e-9). Incluye sensibilidad
   plazo×escalación y vista cliente (beneficio año 1, % retenido, años negativos
   = deal no vendible). Demo Tototlán: TIR 18% → **$2.2942/kWh** (15a/5%);
   cliente retiene 14% del ahorro sin invertir.
2. **Proposal factory** (`tools/make_proposal.py`, subagente `proposal-writer`):
   `raw/bills/<RPU>/` → `Propuesta - <RPU>.md` (es-MX) en un comando — situación
   actual validada, sistema, tabla mensual, palancas (FP separada), inversión,
   opción PPA. Automatiza el loop probado de [[2026-06-09-456220800389-propuesta]].
3. **GDMTO/PDBT** (`tools/tarifa_flat.py`): modelo de tarifa plana con umbral
   FC=0.55 ([[gdmto]]) y PDBT energía-only ([[pdbt]]). Prefactibilidad: filas
   manuales (sin parser hasta tener recibo real), BESS shave solo explícito
   (sin punta no hay arbitraje), mismos caps regulatorios del core.
4. **Webapp v2** (`tools/webapp/`): rediseño completo (dark glass, KPI cards,
   gráfica de barras mensual) + pestaña GDMTO/PDBT + panel "Estructurar deal"
   (solver PPA en vivo) + botón de descarga de propuesta. Endpoints nuevos:
   `/api/ppa`, `/api/proposal`, `/api/run_flat`.
5. **Subagentes** (`.claude/agents/`): `proposal-writer`, `ppa-deal-pricer`,
   `project-checker` (Workflow 5), `financial-auditor` (Workflow 6) — junto al
   existente `cfe-savings-analyst`, cada workflow tiene ejecutor dedicado.
6. **Front door**: `OS - Centro de Mando.md` (raíz) — mapa capacidad→comando→
   producto, reglas no negociables, límites honestos, anatomía.
7. **Corrección de invariante**: `defaults.py` BC punta abr–oct → **may–oct**
   (BC verano inicia 1-mayo; [[horarios-y-divisiones]], A/158/2024 Tabla 4).
   El wiki tenía razón; el engine estaba mal. Golden intacto (SIN no usa BC).

### Validación

- Golden test **18/18** antes y después de cada cambio (pycache limpio).
- `calc_core` desde PDFs crudos con el config demo = **$7,083,252.48 al centavo**;
  webapp `/api/run` = idéntico al core.
- `ppa_pricer` reproduce el TIR financiador de calc_core a 1e-9; solver verifica
  18.0000% en la tarifa resuelta.
- 5 endpoints curl-tested verdes; JS `node --check` OK; AST de todos los .py OK.
- Incidente repetido de sync del mount (server.py, index.html, defaults.py
  truncados del lado Linux) — reparado vía bash con verificación, sin pérdida.

### Límites honestos / siguiente

- GDMTO/PDBT sin parser de recibos (esperar el primer recibo real).
- Pricer PPA modela la estructura financiador-fondea-CAPEX; otras estructuras
  (leasing, deuda) = extensión.
- Pendientes del backlog del usuario: **datos 15-min** (la mejora #1 para
  bancabilidad), M&V post-venta, DOF watcher, benchmarks.

## Sources consulted
- [[2026-06-10-second-brain-use-cases]] (el backlog), [[2026-06-11-calculadora-generica-pv-bess]],
  [[2026-06-11-automatizacion-calculadora]], [[2026-06-11-780881200029-calculadora-audit]],
  [[horarios-y-divisiones]], [[gdmto]], [[pdbt]], CLAUDE.md.

## Confidence
High — todos los números citados son engine-derived y verificados en esta sesión;
las mecánicas GDMTO/PDBT son source-confirmed en wiki pero sin recibo real validado
(estado declarado en el propio módulo).
