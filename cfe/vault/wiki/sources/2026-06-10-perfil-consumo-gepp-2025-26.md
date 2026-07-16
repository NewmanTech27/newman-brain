---
title: "Perfil de Consumo Eléctrico GEPP 2025-26 (client workbook)"
type: source
tags: [gepp, portfolio, gdmth, autoabasto, consumption-profile]
created: 2026-06-10
updated: 2026-06-10
sources: []
---

# Perfil de Consumo Eléctrico GEPP 2025-26

**Type:** data
**Date:** 2026 (full-year 2025 actuals + Ene–Abr 2026 YTD)
**Author:** GEPP (client-prepared workbook)
**Raw file:** `raw/Perfil de Consumo Eléctrico GEPP 2025-26 (1).xlsx`

> **Machine-readable since 2026-06-14.** `tools/import_perfil_xlsx.py` reinterprets this workbook into the OS bill schema (`cfe_savings.extract`): it reconstructs the disaggregated MEM components from each plant sheet's per-period quantities × the `Tarifas` rates and validates against the printed totals. Six services land in `imported/<slug>/` (CAN, ACA, IXT, PR1, PR2, TAP), engine-readable via `extract_folder`. Cancún foots to +0.12% (faithful CFE recibo); autoabasto sites diverge by the Tala/ENEL discount (IXT +22%, PR1 +45%, TAP +33% — the reconstruction values the full load at CFE GDMTH rates, the correct PV/BESS-sizing basis). Coverage = 2026 Ene–Abr only (4 months → seasonality flag). See `imported/README.md`.

## Summary

Client-prepared Excel with monthly GDMTH consumption/billing profiles for [[gepp]]'s plant portfolio (~30+ services nationwide), plus a `RESUMEN_` sheet stating the **actual project brief** for four sites: Ixtlahuacán, Acapulco, Cancún, and Proplasa (PR1/PR2/TAP, one predio, three meters). Each plant sheet carries, per month: kWh by period (base/intermedia/punta), Dem. Máx. per period, kWMax año móvil, kVArh, FP, and the full charge stack (importe de energía, cargo fijo, bonificación/cargo FP, porteo, subtotal, total recibo). A `Tarifas` sheet holds per-plant monthly CFE rates by división; `ENEL PROPL` and `TALA` sheets split kWh between CFE and the legacy autoabasto suppliers; `VR` is GEPP's own bill-verification sheet (largely broken `#REF!` links to external workbooks).

Portfolio 2025 totals (per the `GEPP` sheet): **411.7 GWh, $1,205.3M MXN total recibos**, portfolio FP cargo $4.83M, punta share ~9.5%. Coverage: 2025 complete, 2026 Ene–Abr.

The stated problemática (`RESUMEN_`, verbatim intent):
- **Ixtlahuacán** — autoabasto with "Tala Energy" (bagasse cogen) to 2032, ~50% of consumption but only half the year (zafra); wants to **combine autoabasto with on-site PV**.
- **Acapulco** and **Cancún** — 100% CFE; want to **explore a PPA or Abasto Aislado**.
- **Proplasa** — autoabasto with ENEL to 2032, ~60% of consumption; largest consumer in GEPP; wants to **combine autoabasto with on-site PV**.

## Key claims (all client-Excel data, not CFE-bill-validated)

- Ixtlahuacán (Jalisco, 5,000 kW, medidor 455GR3): 2025 = 22.17 GWh, $60.95M; % cogeneración 100% Ene–May + Dic, ~0% Jun–Nov (annual 49.5%) — matches the zafra-seasonality claim. Tala bills at CFE-equivalent rates **minus a 10% descuento** on importe de energía ($2.68M discount in 2025). 2026 Ene–Abr ran 100% Tala.
- Acapulco (Centro Sur, 2,271 kW): 2025 = 8.91 GWh, $32.89M; **FP 85–86% every month → cargo FP $1.72M/yr sin IVA** (~6.1% of subtotal).
- Cancún (Peninsular, 1,500 kW): 2025 = 4.75 GWh, $18.55M; **FP ~89% → cargo FP $0.60M/yr sin IVA**.
- Proplasa (Valle de México Norte; PR1 2,600 + PR2 5,625 + TAP 2,814 kW): 2025 combined = 92.0 GWh, $229.5M; ENEL supplied 64.0 GWh (69.6%) at $1.78–1.92/kWh (≈ CFE intermedia level). **2026 anomaly: ENEL share collapsed from ~55% (Ene–Feb) to ~16% (Mar–Abr)**, pushing CFE bills up sharply (e.g. PR1 recibo $2.34M Feb → $3.63M Mar). FP healthy (97–99.5).
- Ixtlahuacán demand anomaly: Dem. Máx. spikes to 5,872 kW (Abr-25) and 7,310 kW (May-25) vs ~3,500 kW typical — **above the 5,000 kW contratada**; worth verifying against actual bills.
- `Comentarios` sheet (GEPP's own to-do): "Validar FP Total, Mérida, Edosa y cogeneración".

## Entities mentioned
- [[gepp]] — portfolio owner; the client
- [[tala-energy]] — bagasse cogenerator; legacy autoabasto supplier to Ixtlahuacán
- [[enel-mexico]] — legacy autoabasto supplier to Proplasa
- [[cfe]] / [[cfe-ssb]] — supplier of the balance

## Concepts mentioned
- [[autoconsumo]] — the 2025 figure the "combine autoabasto + on-site PV" and "abasto aislado" asks map onto
- [[medicion-neta]] / [[generador-exento]] — the <0.7 MW on-site PV route
- [[gdmth]] — all flagged services are GDMTH
- [[demanda-facturable]], [[horarios-y-divisiones]] — divisions: Jalisco, Centro Sur, Peninsular, Valle de México Norte

## Contradictions / tensions
- None against the Domain invariants. Note the workbook tracks `kWMax Año Móvil` as a distinct row from per-period Dem. Máx. — consistent with [[demanda-facturable]] (printed KWMax ≠ demand basis).
- Many sheets (`VR`, `TALA`, `FP`) are full of `#REF!` errors — the workbook references external files we don't have; only the four flagged plants' data is intact.

## Questions raised
- Can a load center under a **legacy autoabasto porteo contract** simultaneously hold a [[medicion-neta]] interconnection for on-site DG <0.7 MW? (→ added to [[overview]] open gaps)
- What are the Tala/ENEL contract terms — committed %, take-or-pay minimums, porteo cost structure, early-exit clauses (both vence 2032)?
- Why did Proplasa's ENEL share collapse in Mar–Abr 2026?
- Off-site PPA route (suministro calificado / MEM) under the 2025 LSE — no wiki page yet; unresearched.
