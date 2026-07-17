# -*- coding: utf-8 -*-
"""Deterministic core of the generic PV/BESS/Hibrido calculator.

Single source of truth shared by:
  - tools/fill_calculadora.py   (auto-fill of the Excel calculator)
  - tools/webapp/server.py      (local webapp backend)

Formula set = the corrected v2 model (wiki/analyses/2026-06-11-780881200029-calculadora-audit)
generalized with the regulatory caps of the generic calculator
(wiki/analyses/2026-06-11-calculadora-generica-pv-bess):
  < 700 kWp : generador exento / medicion neta — PV credited up to monthly kWh intermedio
  >= 700 kWp: autoconsumo — only pct_autoconsumo credited; excedentes at texc (default $0)
  BESS      : SAE-CC — discharge only punta weekdays, capped at the bill's punta kWh
Golden anchor: demo 780881200029 hibrido = $7,083,252.47 (arb $790,048.75, claw -$84,528.03).

Bills use the cfe_savings.extract key names. Numbers out only — no raw bytes.
"""
from __future__ import annotations
import math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cfe_savings.defaults import punta_hours, punta_weekdays
import load_curves

GIRO_PCT_AC = {"Hotel/Turismo": 0.80, "Industrial 24/7": 0.90, "Industrial 1 turno": 0.65,
               "Comercial/Retail": 0.75, "Oficinas": 0.60, "Otro": 0.75}

DEFAULT_INPUTS = dict(
    cliente="", rpu="", municipio="", division="SIN", giro="Otro",
    demanda_contratada=0.0, fp_correction=False, fc=0.57,
    kwp=0.0, yield_monthly={}, pv_degr=0.005, epc_usd_wp=0.75, fx=17.55,
    om_pv=None, ppa=1.5, ppa_yrs=15, esc_ppa=0.05,
    bess_kwh=0.0, bess_kw=0.0, dod=0.96, rte=0.96, bess_degr=0.0125,
    epc_bess=280.0, om_bess=None, comision=0.5, falla_meses=3, bess_yrs=15,
    pct_autoconsumo=None, curva=None, texc=0.0,
    wacc=0.12, esc_cfe=0.05, fianza=0.139, horizon=20, escenario="Hibrido",
)


def merge_inputs(over: dict) -> dict:
    p = dict(DEFAULT_INPUTS)
    p.update({k: v for k, v in (over or {}).items() if v is not None})
    # % autoconsumo: manual override > derived from load curve > flat giro default
    p["pct_mode"] = "manual" if (over or {}).get("pct_autoconsumo") is not None else "curva"
    if p["curva"] not in load_curves.CURVES:
        p["curva"] = p["giro"] if p["giro"] in load_curves.CURVES else "Otro"
    if p["pct_autoconsumo"] is None:
        p["pct_autoconsumo"] = GIRO_PCT_AC.get(p["giro"], 0.75)
    ym = {int(k): float(v) for k, v in (p["yield_monthly"] or {}).items()}
    p["yield_monthly"] = ym
    if p["om_pv"] is None:
        p["om_pv"] = p["kwp"] * 310.0          # ~v2 ratio MXN/kWp-yr
    if p["om_bess"] is None:
        p["om_bess"] = p["bess_kwh"] * 180.0   # ~v2 ratio MXN/kWh-yr
    p["capex_pv"] = p["kwp"] * 1000 * p["epc_usd_wp"] * p["fx"]
    p["capex_bess"] = p["bess_kwh"] * p["epc_bess"] * p["fx"]
    p["deliv"] = p["bess_kwh"] * p["dod"] * math.sqrt(p["rte"])
    p["falla"] = (12 - p["falla_meses"]) / 12
    return p


def validate_bill(b: dict) -> dict:
    mem = sum(b.get(k) or 0.0 for k in ("suministro", "distribucion", "transmision",
              "cenace", "gen_base", "gen_inter", "gen_punta", "capacidad", "scnmem"))
    bonif = b.get("bonif_fp") or 0.0
    calc = (mem + bonif) * 1.16
    rec = b.get("facturacion_recibo")
    diff = (calc / rec - 1) if rec else None
    return dict(mem=mem, bonif=bonif, calc_total=calc, recibo=rec, diff=diff,
                ok=(diff is not None and abs(diff) < 0.005))


def compute(inputs: dict, bills: list[dict]) -> dict:
    p = merge_inputs(inputs)
    autoc = p["kwp"] >= 700.0
    rows, val_rows = [], []
    for b in bills:
        y, m = b["year"], b["month"]
        v = validate_bill(b)
        val_rows.append(dict(year=y, month=m, **v))
        days = b["days"] or 30
        kb, ki, kp = b["kwh_base"] or 0.0, b["kwh_inter"] or 0.0, b["kwh_punta"] or 0.0
        kwh_tot = kb + ki + kp
        kwb, kwi, kwp_ = b["kw_base"] or 0.0, b["kw_inter"] or 0.0, b["kw_punta"] or 0.0
        mem, bonif = v["mem"], v["bonif"]
        umbral = kwh_tot / (days * 24 * p["fc"]) if days else 0.0
        basis_cap = umbral if kwp_ == 0 else min(kwp_, umbral)
        r_cap = (b["capacidad"] or 0.0) / basis_cap if basis_cap else 0.0
        flat = sum((b[k] or 0.0) for k in ("transmision", "cenace", "scnmem")) / kwh_tot if kwh_tot else 0.0
        bnd_i = ((b["gen_inter"] or 0.0) / ki + flat) if ki else 0.0
        bnd_b = ((b["gen_base"] or 0.0) / kb + flat) if kb else bnd_i
        bnd_p = ((b["gen_punta"] or 0.0) / kp + flat) if kp else 0.0
        ph = punta_hours(p["division"], m)
        from load_curves import punta_days as _pd
        wd = _pd(p["division"], y, m)
        gen = p["kwp"] * p["yield_monthly"].get(m, 0.0)
        if not autoc:
            pct_m = 1.0
        elif p["pct_mode"] == "manual":
            pct_m = p["pct_autoconsumo"]
        else:  # derived: hourly overlap of the industry curve vs the solar bell
            pct_m = load_curves.autoconsumo_pct(p["curva"], y, m, kwh_tot, gen)
        usable = gen * pct_m
        aprov = min(usable, ki)
        exced = gen - aprov
        ah_pv = aprov * bnd_i + exced * p["texc"]
        umb_post = (kwh_tot - aprov) / (days * 24 * p["fc"]) if days else 0.0
        f_pre = basis_cap
        f_prebess = umb_post if kwp_ == 0 else min(kwp_, umb_post)
        dem_pv = (f_pre - f_prebess) * r_cap
        share = -bonif / mem if mem else 0.0
        claw = lambda s: -s * share if bonif < 0 else 0.0
        pv_only = ah_pv + dem_pv + claw(ah_pv + dem_pv)
        shave = min(p["bess_kw"], p["deliv"] / ph) if ph else 0.0
        resid = max(0.0, kwp_ - shave)
        f_post_h = min(resid, umb_post)
        dem_bess_h = (f_prebess - f_post_h) * r_cap
        desc = min(p["deliv"] * wd, kp) if ph else 0.0
        carga = desc / p["rte"] if p["rte"] else 0.0
        arb = desc * bnd_p - carga * bnd_b
        hib = (s := ah_pv + dem_pv + dem_bess_h + arb) + claw(s)
        f_post_b = min(resid, umbral)
        dem_bess_o = (f_pre - f_post_b) * r_cap
        bess_only = (sb := dem_bess_o + arb) + claw(sb)
        antes = mem + bonif
        rows.append(dict(
            year=y, month=m, days=days, kwh_total=kwh_tot, kwh_punta=kp,
            gen=gen, gen_aprov=aprov, exced=exced, desc=desc,
            ah_pv=ah_pv, dem_pv=dem_pv, dem_bess_h=dem_bess_h, arb=arb,
            pv_only=pv_only, bess_only=bess_only, hibrido=hib, pct_ac=pct_m,
            antes=antes, despues_hib=antes - hib,
            pct_hib=hib / antes if antes else 0.0,
            fp_cargo=b.get("cargo_fp_penalty") or 0.0,
        ))
    # Annualization guard: bills sum over the months PROVIDED. When fewer than 12
    # are supplied, the $/kWh aggregates are a partial-year figure; the finance and
    # 20-yr projection charge a FULL annual CAPEX against them, so they must be
    # scaled to a 12-month basis (×12/n). 12-month inputs → factor 1 (golden intact).
    # Ratios (pct_ac_avg) and per-month `rows` are NOT scaled. Seasonality caveat:
    # the months present are assumed representative; flagged in _regimen below.
    n_meses = len(rows)
    ann = (12.0 / n_meses) if 0 < n_meses < 12 else 1.0
    T = lambda k: sum(r[k] for r in rows) * ann
    annual = dict(antes=T("antes"), gen=T("gen"), exced=T("exced"),
                  pv_only=T("pv_only"), bess_only=T("bess_only"), hibrido=T("hibrido"),
                  ah_pv=T("ah_pv"), dem_pv=T("dem_pv"), dem_bess_h=T("dem_bess_h"),
                  arb=T("arb"), fp_cargo=T("fp_cargo"))
    annual["meses"] = n_meses
    annual["factor_anual"] = ann
    annual["anualizado"] = ann != 1.0
    annual["fp_lever"] = annual["fp_cargo"] if p["fp_correction"] else 0.0
    annual["pct_ac_avg"] = (sum(r["pct_ac"] * r["gen"] for r in rows) / sum(r["gen"] for r in rows)
                            if sum(r["gen"] for r in rows) else 1.0)
    # neto de disponibilidad: falla aplica solo al ahorro atribuible al BESS
    bess_part_h = annual["dem_bess_h"] + annual["arb"]
    annual["neto_disp"] = dict(
        pv=annual["pv_only"],
        bess=annual["bess_only"] - (annual["bess_only"]) * (1 - p["falla"]),
        hibrido=annual["hibrido"] - (bess_part_h) * (1 - p["falla"]),
    )
    regimen = _regimen(p, bills, rows, annual)
    fin = {esc: _finance(p, annual, esc) for esc in ("PV", "BESS", "Hibrido")}
    return dict(inputs=p, monthly=rows, validacion=val_rows, annual=annual,
                regimen=regimen, finance=fin)


def _regimen(p, bills, rows, annual):
    autoc = p["kwp"] >= 700.0
    if not autoc:
        reg = "GENERADOR EXENTO — Medición Neta (sin permiso; Art. 30 LSE; RES/142/2017)"
    elif p["kwp"] <= 20000:
        reg = "AUTOCONSUMO interconectado 0.7–20 MW — permiso SIMPLIFICADO CNE (Núm. 2.2 DACG)"
    else:
        reg = "AUTOCONSUMO >20 MW — permiso ORDINARIO CNE (Núm. 2.3 DACG)"
    alerts = []
    if any(not v["ok"] for v in (validate_bill(b) for b in bills)):
        alerts.append(("error", "Hay recibos que no cuadran (>0.5%) — corregir transcripción/parseo antes de usar resultados"))
    kwmax = max((max(b.get("kw_base") or 0, b.get("kw_inter") or 0, b.get("kw_punta") or 0) for b in bills), default=0)
    if kwmax < 110:
        alerts.append(("warn", f"Demanda máx {kwmax:.0f} kW — cerca del gate de 100 kW; revisar si la tarifa correcta es GDMTO"))
    if p["bess_kw"] > (p["demanda_contratada"] or float("inf")):
        alerts.append(("error", f"BESS {p['bess_kw']:.0f} kW > demanda contratada {p['demanda_contratada']:.0f} kW — viola condición SAE-CC"))
    if annual["exced"] > 1.0:  # >1 kWh: ignora polvo de punto flotante
        alerts.append(("warn", f"{annual['exced']:,.0f} kWh/año de excedentes valuados a ${p['texc']:.2f} — bajo medición neta los créditos expiran a PML en 12 meses; ajustar kWp al consumo"))
    if annual["fp_cargo"] > 0:
        alerts.append(("opp", f"Cargos FP por ${annual['fp_cargo']:,.0f}/año — la corrección FP suele ser el ROI más alto y es ortogonal a PV/BESS"))
    if p["division"] != "SIN":
        alerts.append(("warn", f"División {p['division']}: modelo calibrado SIN; PV genera parcialmente en punta (no acreditado = conservador); tarifas no-SIN = gap abierto del wiki"))
    if autoc:
        src = ("manual" if p["pct_mode"] == "manual"
               else f"derivado de curva '{p['curva']}' × campana solar")
        alerts.append(("info", f"Autoconsumo activo: {annual['pct_ac_avg']:.0%} del PV acreditado ({src}); excedentes solo a CFE a ${p['texc']:.2f}/kWh; permiso CNE + registro anual 1T + uso mínimo 30%"))
        if p["pct_mode"] == "curva":
            fit = load_curves.fit_bills(bills, p["division"])
            row = next((r for r in fit["ranking"] if r["giro"] == p["curva"]), None)
            if row and row["mae"] is not None and row["mae"] > 0.08:
                alerts.append(("warn", f"La curva '{p['curva']}' NO ajusta bien a los recibos (MAE {row['mae']:.1%}) — el % autoconsumo derivado es poco confiable; mejor ajuste: '{fit['best']}'. Considerar override manual o datos 15-min"))
        if p["bess_kwh"] > 0:
            alerts.append(("info", "Respaldo de intermitencia OBLIGATORIO — cubierto por el BESS del proyecto (Núm. 4.5 DACG)"))
        else:
            alerts.append(("error", "PV ≥0.7 MW intermitente REQUIERE SAE o respaldo CFE contratado — el proyecto no trae BESS"))
    if len(bills) < 12:
        alerts.append(("warn", f"Solo {len(bills)} meses de recibos — riesgo de estacionalidad; ideal 12"))
    return dict(autoconsumo=autoc, regimen=reg, alerts=alerts)


def _finance(p, annual, esc):
    has_pv = esc in ("PV", "Hibrido") and p["kwp"] > 0
    has_bess = esc in ("BESS", "Hibrido") and p["bess_kwh"] > 0
    base_pv = (annual["ah_pv"] + annual["dem_pv"]) if has_pv else 0.0
    if esc == "Hibrido":
        base_bess = annual["dem_bess_h"] + annual["arb"]
        bruto0 = annual["hibrido"]
    elif esc == "BESS":
        base_bess = annual["bess_only"]  # incl claw (small)
        bruto0 = annual["bess_only"]
    else:
        base_bess, bruto0 = 0.0, annual["pv_only"]
    base_claw = bruto0 - base_pv - base_bess if esc != "BESS" else 0.0
    capex = (p["capex_pv"] if has_pv else 0.0) + (p["capex_bess"] if has_bess else 0.0)
    gen = annual["gen"] if has_pv else 0.0
    fl_new, fl_proj = [-capex], [-capex]
    for yy in range(1, p["horizon"] + 1):
        e = (1 + p["esc_cfe"]) ** yy
        dpv = (1 - p["pv_degr"]) ** yy
        dbe = (1 - p["bess_degr"]) ** yy
        sav_pv = base_pv * e * dpv
        sav_bess = base_bess * e * dbe * p["falla"]
        clw = base_claw * e * (dpv + dbe) / 2
        bruto = sav_pv + sav_bess + clw
        ppa_pay = gen * dpv * p["ppa"] * (1 + p["esc_ppa"]) ** (yy - 1) if (has_pv and yy <= p["ppa_yrs"]) else 0.0
        com = sav_bess * p["comision"] if (has_bess and yy <= p["bess_yrs"]) else 0.0
        ompv = p["om_pv"] * (1 + p["esc_cfe"]) ** (yy - 1) if (has_pv and yy <= p["ppa_yrs"]) else 0.0
        ombe = p["om_bess"] * (1 + p["esc_cfe"]) ** (yy - 1) if (has_bess and yy <= p["bess_yrs"]) else 0.0
        fz = ppa_pay * p["fianza"]
        fl_new.append(ppa_pay + com - ompv - ombe - fz)
        fl_proj.append(bruto - ompv - ombe)
    def irr(flows, lo=-0.95, hi=4.0):
        f = lambda r: sum(x / (1 + r) ** i for i, x in enumerate(flows))
        if not flows or f(lo) * f(hi) > 0: return None
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(lo) * f(mid) <= 0: hi = mid
            else: lo = mid
        return (lo + hi) / 2
    npv = lambda fl: sum(x / (1 + p["wacc"]) ** i for i, x in enumerate(fl))
    def pay(fl):
        c = 0.0
        for i, x in enumerate(fl):
            c += x
            if c >= 0: return i
        return None
    return dict(capex=capex, bruto_anio0=bruto0,
                tir_proyecto=irr(fl_proj), tir_financiador=irr(fl_new),
                vpn_proyecto=npv(fl_proj), vpn_financiador=npv(fl_new),
                payback_proyecto=pay(fl_proj), payback_financiador=pay(fl_new))
