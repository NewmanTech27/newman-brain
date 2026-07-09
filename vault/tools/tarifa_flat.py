# -*- coding: utf-8 -*-
"""Flat-tariff savings model — GDMTO and PDBT (prefeasibility grade).

Opens the small-commercial long tail below the 100 kW GDMTH gate:
  GDMTO : media tensión < 100 kW, flat energy rate, demand charges with the
          umbral cap at FC = 0.55 (wiki gdmto / demanda-facturable).
  PDBT  : baja tensión ≤ 25 kW, single integrated $/kWh (wiki pdbt) — energy only.

Honest scope (stated in every output):
  - extract.py does NOT parse GDMTO/PDBT bills yet — rows are MANUAL entry
    (or CSV paste in the webapp). When the first real GDMTO bill lands in
    raw/bills/, build the parser and validate against it.
  - GDMTO has no punta windows -> no BESS arbitrage. BESS demand shave requires
    an explicit, user-supplied `bess_shave_kw` (interval data makes it credible);
    without it BESS savings are 0 by design, never guessed.
  - Same regulatory caps as calc_core: <700 kWp medición neta (PV credited up to
    the month's kWh), >=700 kWp autoconsumo (pct_autoconsumo only) — though a
    GDMTO/PDBT site that big is itself a red flag (wrong tariff).

Bill row keys (MXN sin IVA, kWh, kW):
  GDMTO: year, month, days, kwh, kw_max, energia, distribucion, capacidad,
         suministro [, fp_cargo, total]
  PDBT : year, month, days, kwh, energia, suministro [, total]

Finance reuses calc_core._finance (same doctrine, same defaults).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc_core

FC_GDMTO = 0.55  # A/158/2024 via wiki gdmto


def validate_flat(b: dict, tarifa: str) -> dict:
    keys = (("energia", "distribucion", "capacidad", "suministro", "fp_cargo")
            if tarifa == "GDMTO" else ("energia", "suministro"))
    mem = sum(b.get(k) or 0.0 for k in keys)
    calc = mem * 1.16
    rec = b.get("total")
    diff = (calc / rec - 1) if rec else None
    return dict(mem=mem, calc_total=calc, recibo=rec, diff=diff,
                ok=(diff is None or abs(diff) < 0.005))  # no total -> can't check


def compute_flat(inputs: dict, bills: list[dict], tarifa: str = "GDMTO") -> dict:
    p = calc_core.merge_inputs(inputs)
    p["fc"] = FC_GDMTO
    autoc = p["kwp"] >= 700.0
    shave = float(inputs.get("bess_shave_kw") or 0.0)
    rows, val_rows = [], []
    for b in bills:
        y, m = int(b["year"]), int(b["month"])
        v = validate_flat(b, tarifa)
        val_rows.append(dict(year=y, month=m, **v))
        days = b.get("days") or 30
        kwh = float(b["kwh"] or 0.0)
        rate_e = (b.get("energia") or 0.0) / kwh if kwh else 0.0
        gen = p["kwp"] * p["yield_monthly"].get(m, 0.0)
        pct_m = 1.0 if not autoc else p["pct_autoconsumo"]
        usable = gen * pct_m
        aprov = min(usable, kwh)
        exced = gen - aprov
        ah_pv_e = aprov * rate_e + exced * p["texc"]
        dem_pv = dem_bess = 0.0
        if tarifa == "GDMTO":
            kw_max = float(b.get("kw_max") or 0.0)
            umbral = kwh / (days * 24 * FC_GDMTO) if days else 0.0
            basis = min(kw_max, umbral) if kw_max else umbral
            r_dem = (((b.get("distribucion") or 0.0) + (b.get("capacidad") or 0.0))
                     / basis if basis else 0.0)
            umb_post = (kwh - aprov) / (days * 24 * FC_GDMTO) if days else 0.0
            basis_pv = min(kw_max, umb_post) if kw_max else umb_post
            dem_pv = (basis - basis_pv) * r_dem
            if shave > 0 and kw_max:
                basis_b = min(max(kw_max - shave, 0.0), umb_post)
                dem_bess = (basis_pv - basis_b) * r_dem
        antes = v["mem"]
        pv_only = ah_pv_e + dem_pv
        hib = pv_only + dem_bess
        rows.append(dict(year=y, month=m, days=days, kwh_total=kwh,
                         kwh_punta=0.0, gen=gen, gen_aprov=aprov, exced=exced,
                         desc=0.0, ah_pv=ah_pv_e, dem_pv=dem_pv,
                         dem_bess_h=dem_bess, arb=0.0,
                         pv_only=pv_only, bess_only=dem_bess, hibrido=hib,
                         pct_ac=pct_m, antes=antes, despues_hib=antes - hib,
                         pct_hib=hib / antes if antes else 0.0,
                         fp_cargo=b.get("fp_cargo") or 0.0))
    T = lambda k: sum(r[k] for r in rows)
    annual = dict(antes=T("antes"), gen=T("gen"), exced=T("exced"),
                  pv_only=T("pv_only"), bess_only=T("bess_only"),
                  hibrido=T("hibrido"), ah_pv=T("ah_pv"), dem_pv=T("dem_pv"),
                  dem_bess_h=T("dem_bess_h"), arb=0.0, fp_cargo=T("fp_cargo"))
    annual["fp_lever"] = annual["fp_cargo"] if p["fp_correction"] else 0.0
    annual["pct_ac_avg"] = (sum(r["pct_ac"] * r["gen"] for r in rows) / annual["gen"]
                            if annual["gen"] else 1.0)
    bess_part = annual["dem_bess_h"]
    annual["neto_disp"] = dict(
        pv=annual["pv_only"],
        bess=annual["bess_only"] * p["falla"],
        hibrido=annual["hibrido"] - bess_part * (1 - p["falla"]),
    )
    alerts = _alerts(p, bills, annual, tarifa, shave)
    fin = {e: calc_core._finance(p, annual, e) for e in ("PV", "BESS", "Hibrido")}
    return dict(inputs=p, tarifa=tarifa, monthly=rows, validacion=val_rows,
                annual=annual, regimen=alerts, finance=fin)


def _alerts(p, bills, annual, tarifa, shave):
    autoc = p["kwp"] >= 700.0
    reg = ("GENERADOR EXENTO — Medición Neta (sin permiso)" if not autoc
           else "AUTOCONSUMO — permiso CNE (revisar: ¿un sitio ≥0.7 MW en tarifa "
                f"{tarifa}? probablemente la tarifa está mal)")
    alerts = [("info", f"Modelo {tarifa} = prefactibilidad: filas de recibo manuales "
                       "(sin parser aún) y sin ventanas horarias")]
    if tarifa == "GDMTO":
        kwmax = max((float(b.get("kw_max") or 0) for b in bills), default=0)
        if kwmax >= 90:
            alerts.append(("warn", f"Demanda máx {kwmax:.0f} kW — cerca del gate de "
                                   "100 kW: a la 3ª medición ≥100 kW migra a GDMTH "
                                   "(re-evaluar ahí: punta/BESS cambian el caso)"))
        if shave > 0:
            alerts.append(("warn", f"BESS shave {shave:.0f} kW = SUPUESTO del usuario "
                                   "(GDMTO no tiene punta); requiere datos de "
                                   "intervalo para ser creíble"))
        else:
            if p["bess_kwh"] > 0:
                alerts.append(("warn", "BESS sin `bess_shave_kw` explícito -> ahorro "
                                       "BESS = $0 por diseño (sin arbitraje en tarifa "
                                       "plana, sin shave adivinado)"))
    else:
        kwhm = max((float(b.get("kwh") or 0) for b in bills), default=0)
        if kwhm > 25 * 24 * 30 * 0.5:
            alerts.append(("warn", "Consumo alto para PDBT (≤25 kW) — verificar si "
                                   "aplica reclasificación a GDBT"))
        if p["bess_kwh"] > 0:
            alerts.append(("warn", "PDBT no tiene cargos de demanda ni horarios — "
                                   "un BESS no ahorra nada aquí"))
    if annual["exced"] > 1.0:
        alerts.append(("warn", f"{annual['exced']:,.0f} kWh/año de excedentes a "
                               f"${p['texc']:.2f} — ajustar kWp al consumo"))
    if annual["fp_cargo"] > 0:
        alerts.append(("opp", f"Cargos FP ${annual['fp_cargo']:,.0f}/año — corrección "
                              "FP suele ser el ROI más alto"))
    if any(not validate_flat(b, tarifa)["ok"] for b in bills):
        alerts.append(("error", "Hay filas que no cuadran contra su total (>0.5%)"))
    if len(bills) < 12:
        alerts.append(("warn", f"Solo {len(bills)} meses — riesgo de estacionalidad"))
    return dict(autoconsumo=autoc, regimen=reg, alerts=alerts)


if __name__ == "__main__":
    # smoke test with synthetic GDMTO rows (flat shapes, plausible rates)
    bills = [dict(year=2026, month=m, days=30, kwh=30000, kw_max=80,
                  energia=30000 * 2.1, distribucion=80 * 95.0, capacidad=80 * 320.0,
                  suministro=550.0, total=None) for m in range(1, 13)]
    inputs = dict(giro="Comercial/Retail", kwp=150, bess_kwh=0, bess_kw=0,
                  yield_monthly={m: 150 for m in range(1, 13)})
    r = compute_flat(inputs, bills, "GDMTO")
    a = r["annual"]
    print(f"GDMTO smoke: antes ${a['antes']:,.0f} · PV-only ${a['pv_only']:,.0f} "
          f"({a['pv_only']/a['antes']:.1%}) · TIR {r['finance']['PV']['tir_proyecto']:.1%}")
    for sev, msg in r["regimen"]["alerts"]:
        print(f"  [{sev}] {msg}")
