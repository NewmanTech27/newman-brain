---
title: "GEPP — Auditoría + re-precio a términos 2026 (áreas reales, EPC 0.65, BESS 0.5C/2h)"
type: analysis
tags: [gepp, audit, repricing, ppa, autoconsumo, bess, area-constraint]
created: 2026-07-07
updated: 2026-07-07
cliente: gepp
rpu: "073EEK, MX096Y, 455GR3, 806DYN, 805DYN, 807DYN"
status: vigente
sources: [2026-06-10-perfil-consumo-gepp-2025-26, 2026-06-15-gepp-v3-audit-rebuild, 2026-07-02-gepp-max-savings-web]
---

# GEPP — Auditoría de la solución curada + re-precio a mis términos 2026

**Pregunta:** ¿Es correcta y valiosa la solución GEPP existente (curada $62.8M, JSON, calculadoras v3/v5), y cómo cambia al aplicar mis áreas de techo reales 2026 y mis términos financieros (EPC PV 0.65, IRR financiador 14% PV / 16% BESS, BESS 0.5C/2h, haircut 2 meses)?

## Answer

### Checkpoint A — Auditoría (verificar y valorar lo existente)
- **Golden 18/18** (motor intacto). Re-corrida independiente del config curado reproduce el bruto **$62.8M → $64.7M (+3%)** con el motor actual: el bruto curado es **CORRECTO** y ligeramente conservador. *(engine-derived)*
- **Línea base corregida:** el motor reproduce **$311.4M** (carga total @ tarifas CFE GDMTH 2025), no los **$341.9M** del reporte "Recomendación por Sitio" (SUPERADO) ni los $316.2M de la curada. **Todas las bases GEPP son grado prefactibilidad** — 0/12 meses cuadran al 0.5% vs recibo impreso (CAN/ACA reconstruyen 6-9% *bajo* impreso; Proplasa/IXT demanda a carga plena, no la parcial que hoy pagan con Tala/ENEL). Válida como base *forward* (post-2032), no como recibo actual.
- **Invariante 0.7 MW confirmado** (< 0.7 MW AC = **839.41 kWp DC**). Sin contaminación de "0.5 MW" en los entregables GEPP (los `<0.5 MW` del vault son el Manual de Interconexión real + texto histórico RES/142/2017). Bug latente: `calc_core._regimen` y `make_project_book` etiquetan exento/autoconsumo a **700 kWp DC**, no 839.41 — cosmético, sin efecto numérico en configs 699 o ≥1,020; importa sólo en la banda 700-839.
- **Reconciliación de las tres cifras de ahorro:** $56.9M (Recomendación, reconstrucción simplificada, SUPERADO) < $62.8M (curada = motor, capta reducción de demanda vía umbral, VIGENTE) < $85.9M (web max-ahorro, config 839×6 + BESS 2h, más agresivo).
- **Veredicto:** motor + estructura comercial (PPA Camino B + share BESS + transferencia PV año 15) + palanca FP + lógica cualitativa por sitio = **SÓLIDO, KEEP**. Dos correcciones: base → $311.4M; **Proplasa físicamente inviable en techo** (ver crux).

### Crux — Áreas reales 2026 colapsan Proplasa
Áreas autoritativas (0.17 kWp/m²): Ixtlahuacán 25,308 m²→4,302 kWp · Acapulco 7,019→1,193 · Cancún 6,828→1,161 · **Proplasa 15,396 m² (3 servicios) → 2,617 kWp para los tres**. La curada puso **10,510 kWp en Proplasa** (necesita ~61,824 m², 4×). PR2 solo (5,220 kWp) necesita ~30,700 m². **~$25M/año del bruto curado (PV Proplasa) sólo es alcanzable adquiriendo terreno.** BESS (huella mínima) sobrevive.

### Checkpoint B — Dos opciones por sitio (EPC 0.65, sizing max-NPV)
| Sitio | Opt1 max (terreno) | Opt2 techo | Régimen (cruzar 0.7MW paga) |
|---|---|---|---|
| Ixtlahuacán | 5,142 kWp autoconsumo | 4,302 kWp (techo casi óptimo) | +$51M → autoconsumo |
| Acapulco | 1,971 autoconsumo | 839 exento | +$8M (marginal) |
| Cancún | 839 exento | 839 exento | −$1M → **exento** |
| Proplasa PR1/PR2/TAP | 4,058 / 11,391 / 7,481 autoconsumo | 464 / 839 / 839 | +$27/+$101/+$61M → autoconsumo |

BESS del sweep = pico de punta (18.7 MW total), idéntico al trabajo 2025 full-year; **sobredimensionado** (energía a 4h) → se fija a la regla del usuario **0.5C/2h**.

### Checkpoint C — Precio (mezcla por-sitio, decisión del usuario)
Config final: **mezcla por-sitio** (techo en CAN/ACA/IXT, **terreno en Proplasa**), BESS 2h, haircut 2 meses (0.833), EPC 0.65, **FX 17.52** (verificado 2026-07-08 ≈ 17.55), IRR nominal MXN.

**Value-stack (neto $/año):**
- Techo PV + FP = **$33.4M** (medición neta, sin terreno ni permiso — entregable ya).
- + BESS 2h = **+$50.5M** (requiere data 15-min; bancabilidad de potencia).
- + PV terreno Proplasa = **+$59.5M** (requiere ~12 ha + permiso CNE autoconsumo + 1 año de retraso).
- = **$143.5M neto máximo** (bruto $153.6M). PV $90.6M · BESS neto $50.5M · FP $2.3M.

**Deal (streams separados):** PV PPA resuelto @14% = **$1.13–1.40/kWh** (blend ~$1.25 vs CFE $2.5–3.9). **BESS comisión fija 50/50** (decisión usuario) → **TIR financiador 10–14%** (bajo el target 16%; alcanzar 16% pediría comisión 54-64%). FP palanca separada 100% cliente.

### Entregables
- `entregables/calculadoras/GEPP - Solucion Energetica (2026 per-site-mix).xlsx` — libro grupo (Resumen + Supuestos vivo + 6 sitios + Comparativo + Proyección 20a), términos 2026, verificado por la maquinaria (test_project_book 5/5, reconcilia al peso).
- `entregables/calculadoras/GEPP - Proplasa Roof-Fallback (2026).xlsx` — variante Proplasa sólo-techo (sin terreno): hibrido $54.6M vs $109M terreno.
- Configs: `gepp_book_config_2026.json` / `_roof.json`.
- Parche additivo `make_project_book.py`: config ahora acepta `epc_usd_wp/fx/falla_meses/esc_ppa` (defaults intactos; golden 18/18, verifier 5/5).

## Pendientes / hallazgos de tooling
1. `optimize_sizing.resolve_yield` + `make_project_book` caen al **plano 1,740** cuando `inputs.json` no trae estado → sesga yields. Workaround: inyecté `yield_monthly` en el config. **Fix permanente ofrecido:** mapa municipio→estado (como `gepp_max_savings_sweep.py`) o CP en inputs.json.
2. Etiqueta exento/autoconsumo a 700 kWp DC (debe ser 839.41). Ya en pendientes del vault.
3. Simulador/DISPATCH + cascada (waterfall) + gráficas + dos-opciones lado-a-lado (estilo Fibrahotel) = capa de legibilidad pendiente de construir sobre el core verificado.

## Confidence
Media-alta. Motor golden-anclado y reconciliado; áreas y términos 2026 son dato duro del usuario. Bases = prefactibilidad hasta 12 recibos CFE. BESS a 2h aún se apoya en load-shape modelado (no 15-min) — bancable con data de intervalo. El máximo $143.5M depende de terreno Proplasa + permisos.
