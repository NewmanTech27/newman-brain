# -*- coding: utf-8 -*-
"""GEPP portfolio — per-site max-savings PV+BESS configuration + deal economics.

Executes the 2026-06-19 log pendings on the 2025 full-year imported dataset:
  1. PV sizing sweep (optimize_sizing, area per gepp_constrained.json → exento DC cap 839.41)
  2. BESS duration sweep 0–5 h at punta-peak power (full-year data → seasonally honest optimum)
  3. FP lever (ACA/CAN) reported as separate additive line with capacitor CAPEX (doctrine)
  4. Deal economics via ppa_pricer: solve PPA $/kWh (comisión BESS 50%) at financier IRR
     18% and 14%; client viability gate; if PPA solves to 0, solve comisión floor instead.

Municipio→estado map fixes the flat-1740 yield caveat (inputs.json lacks CP/estado).
Emits entregables/reportes/gepp_max_savings_data.json for the HTML report builder.
Engine untouched — golden 18/18 verified before this run.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.stdout.reconfigure(encoding="utf-8")

import calc_core
import optimize_sizing
import ppa_pricer
import solar_lookup
from cfe_savings import extract, sizing
from cfe_savings.defaults import punta_hours

SITES = {
    "gepp-cancun":        dict(estado="Quintana Roo",  fp=True,  capacitor=500_000),
    "gepp-acapulco":      dict(estado="Guerrero",      fp=True,  capacitor=1_000_000),
    "gepp-ixtlahuacan":   dict(estado="Jalisco",       fp=False, capacitor=0),
    "gepp-proplasa-pr1":  dict(estado="Estado de México", fp=False, capacitor=0),
    "gepp-proplasa-pr2":  dict(estado="Estado de México", fp=False, capacitor=0),
    "gepp-proplasa-tap":  dict(estado="Estado de México", fp=False, capacitor=0),
}
AREA_M2 = 4938.0          # gepp_constrained.json — proxy area ⇒ PV cap = exento DC ceiling
HOURS_GRID = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
# Deal doctrine: with BESS the dominant lever, solving the PPA at a fixed 50% comisión
# pushes the PPA above the client's CFE blend (unsellable). We fix the PPA at a rate
# below the intermedio energy rate in every division (client wins on every PV kWh) and
# solve the BESS comisión for the target financier IRR instead.
PPA_FIXED_RATE = 1.80     # $/kWh, 15 y, esc 5% — vs intermedio ~$1.82–2.08


def run_site(slug: str, cfg: dict) -> dict:
    folder = ROOT / "imported" / slug
    bills = extract.extract_folder(str(folder))[-12:]
    inp_file = json.loads((folder / "inputs.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))

    y = solar_lookup.municipio_yield(inp_file.get("municipio", ""), cfg["estado"])
    if y:
        ym, ysrc = y["monthly"], f"{y['match']} ({y['anual']:,.0f} kWh/kWp/año)"
    else:
        ym, ysrc = {m: 145.0 for m in range(1, 13)}, "default plano 1,740 — revisar"

    base = dict(giro=inp_file.get("giro", "Industrial 24/7"),
                division=inp_file.get("division", "SIN"),
                yield_monthly=ym,
                demanda_contratada=inp_file.get("demanda_contratada"),
                fp_correction=cfg["fp"])

    # ---- 1. PV sweep (regime-aware; area proxy caps at the exento DC ceiling) ----
    sweep = optimize_sizing.propose(bills, base, area_m2=AREA_M2)
    rec = sweep["recomendado"]
    kwp = rec["kwp"]

    # ---- 2. BESS duration sweep at punta-peak power, chosen PV fixed ----
    be = sizing.propose_bess(bills, base["division"], None)
    pk = float(be["proposed_power_kw"])
    bess_curve = []
    for h in HOURS_GRID:
        inp = dict(base, kwp=kwp, bess_kw=(pk if h > 0 else 0.0), bess_kwh=pk * h)
        r = calc_core.compute(inp, bills)
        f = r["finance"]["Hibrido"]
        bess_curve.append(dict(h=h, bess_kw=(pk if h > 0 else 0.0), bess_kwh=round(pk * h),
                               npv=f["vpn_proyecto"], tir=f["tir_proyecto"],
                               ahorro=r["annual"]["hibrido"], capex=f["capex"],
                               arb=r["annual"]["arb"], dem_bess=r["annual"]["dem_bess_h"]))
    best = max(bess_curve, key=lambda p: p["npv"])

    # ---- 3. Final configuration ----
    final_inputs = dict(base, kwp=kwp, bess_kw=best["bess_kw"], bess_kwh=best["bess_kwh"])
    res = calc_core.compute(final_inputs, bills)
    ann, fin = res["annual"], res["finance"]

    # ---- 4. Deal economics: PPA fixed sellable, solve BESS comisión per target IRR ----
    deals = {}
    for tgt in (0.18, 0.14):
        d = ppa_pricer.price(final_inputs, bills, target_irr=tgt, solve="comision",
                             ppa=PPA_FIXED_RATE, sensitivity=False)
        mode = "comision"
        if not d.get("feasible"):
            # PV-heavy site (small BESS): comisión can't carry the financier — solve the
            # PPA instead at comisión 50%. Sellable when PV also cuts demand via umbral,
            # so the fair optic is the full blend rate, not the intermedio energy rate.
            d = ppa_pricer.price(final_inputs, bills, target_irr=tgt, solve="ppa",
                                 comision=0.5, sensitivity=False)
            mode = "ppa"
        deals[f"{tgt:.0%}"] = dict(mode=mode, **{k: v for k, v in d.items()
                                                 if k not in ("regimen", "annual", "flows")})

    # ---- 5. Escenario cobertura total del consumo (autoconsumo) ----
    # PV dimensionado a generar el 100% del consumo anual (kwp_100 del sweep),
    # mismo BESS óptimo (pico de punta × 2h). Cruza 0.7 MW AC → autoconsumo
    # (permiso CNE; >20 MW → ordinario). Excedentes valuados a texc (default $0,
    # conservador). Sirve para mostrarle al cliente cómo se ve "atender todo".
    kwp_full = sweep["kwp_100"]
    full_inputs = dict(base, kwp=kwp_full, bess_kw=best["bess_kw"],
                       bess_kwh=best["bess_kwh"])
    rfull = calc_core.compute(full_inputs, bills)
    fa = rfull["annual"]
    kwh_tot = sum(r["kwh_total"] for r in rfull["monthly"])
    full = dict(
        kwp=kwp_full, bess_kw=best["bess_kw"], bess_kwh=best["bess_kwh"],
        h=best["h"], regimen=rfull["regimen"]["regimen"],
        autoconsumo=rfull["regimen"]["autoconsumo"],
        alerts=rfull["regimen"]["alerts"],
        capex=rfull["finance"]["Hibrido"]["capex"],
        vpn=rfull["finance"]["Hibrido"]["vpn_proyecto"],
        annual=dict(antes=fa["antes"], hibrido=fa["hibrido"],
                    pct=fa["hibrido"] / fa["antes"] if fa["antes"] else 0,
                    gen=fa["gen"], exced=fa["exced"], kwh=kwh_tot,
                    ah_pv=fa["ah_pv"], dem_pv=fa["dem_pv"],
                    dem_bess=fa["dem_bess_h"], arb=fa["arb"],
                    fp_lever=fa["fp_lever"], pct_ac=fa["pct_ac_avg"]),
    )

    fp_cargo = ann["fp_cargo"]
    monthly = [dict(m=r["month"], antes=r["antes"], hibrido=r["hibrido"],
                    despues=r["despues_hib"], gen=r["gen"], gen_aprov=r["gen_aprov"],
                    desc=r["desc"], arb=r["arb"], dem_bess=r["dem_bess_h"],
                    ah_pv=r["ah_pv"], dem_pv=r["dem_pv"], kwh=r["kwh_total"],
                    kwh_punta=r["kwh_punta"], fp=r["fp_cargo"]) for r in res["monthly"]]

    ph_max = max(punta_hours(base["division"], b["month"]) for b in bills)
    return dict(
        slug=slug, nombre=inp_file.get("nombre", slug), rpu=inp_file.get("rpu"),
        municipio=inp_file.get("municipio"), estado=cfg["estado"],
        demanda_contratada=inp_file.get("demanda_contratada"),
        yield_source=ysrc, yield_annual=sum(ym.values()),
        meta_note=meta.get("note"), meta_worst_diff=meta.get("worst_diff_vs_client"),
        n_meses=ann["meses"], anualizado=ann["anualizado"],
        pv=dict(kwp=kwp, regimen=rec["regimen"], curva=sweep["curva"],
                kwp_100=sweep["kwp_100"], exento=sweep["exento"],
                autoconsumo=sweep["autoconsumo"]),
        bess=dict(kw=best["bess_kw"], kwh=best["bess_kwh"], h=best["h"],
                  h_usable=round(best["h"] * 0.9408, 2), punta_peak_kw=pk,
                  ph_max=ph_max, curve=bess_curve),
        fp=dict(activo=cfg["fp"], cargo_anual=fp_cargo, capacitor=cfg["capacitor"],
                payback_meses=(cfg["capacitor"] / fp_cargo * 12 if cfg["fp"] and fp_cargo else None)),
        annual=dict(antes=ann["antes"], hibrido=ann["hibrido"],
                    pct=ann["hibrido"] / ann["antes"] if ann["antes"] else 0,
                    pv_only=ann["pv_only"], bess_only=ann["bess_only"],
                    ah_pv=ann["ah_pv"], dem_pv=ann["dem_pv"],
                    dem_bess=ann["dem_bess_h"], arb=ann["arb"],
                    gen=ann["gen"], exced=ann["exced"], fp_lever=ann["fp_lever"],
                    neto_disp=ann["neto_disp"]),
        finance={k: dict(capex=v["capex"], tir=v["tir_proyecto"], vpn=v["vpn_proyecto"],
                         payback=v["payback_proyecto"]) for k, v in fin.items()},
        deals=deals, alerts=res["regimen"]["alerts"], regimen=res["regimen"]["regimen"],
        monthly=monthly, full=full,
    )


def main():
    out = dict(sites={}, portfolio={})
    for slug, cfg in SITES.items():
        print(f"→ {slug} ...", flush=True)
        out["sites"][slug] = run_site(slug, cfg)
        s = out["sites"][slug]
        d18 = s["deals"]["18%"]
        print(f"   PV {s['pv']['kwp']:,.0f} kWp + BESS {s['bess']['kw']:,.0f} kW / "
              f"{s['bess']['kwh']:,.0f} kWh ({s['bess']['h']}h) · ahorro ${s['annual']['hibrido']:,.0f} "
              f"({s['annual']['pct']:.0%}) · NPV ${s['finance']['Hibrido']['vpn']:,.0f} · "
              + (f"deal18[{d18['mode']}]: PPA ${d18['ppa_rate']:.2f} + com {d18['comision']:.0%}"
                 if d18.get("feasible") else "deal18 NO alcanzable"))
    agg = {}
    for k in ("antes", "hibrido", "gen", "fp_lever"):
        agg[k] = sum(s["annual"][k] for s in out["sites"].values())
    agg["capex"] = sum(s["finance"]["Hibrido"]["capex"] for s in out["sites"].values())
    agg["vpn"] = sum(s["finance"]["Hibrido"]["vpn"] for s in out["sites"].values())
    agg["kwp"] = sum(s["pv"]["kwp"] for s in out["sites"].values())
    agg["bess_kw"] = sum(s["bess"]["kw"] for s in out["sites"].values())
    agg["bess_kwh"] = sum(s["bess"]["kwh"] for s in out["sites"].values())
    agg["capacitores"] = sum(s["fp"]["capacitor"] for s in out["sites"].values())
    agg["cliente_a1_18"] = sum((s["deals"]["18%"].get("cliente") or {}).get("beneficio_anio1") or 0
                               for s in out["sites"].values())
    agg["vpn_fin_18"] = sum(s["deals"]["18%"].get("vpn_financiador") or 0
                            for s in out["sites"].values())
    out["portfolio"] = agg
    dst = ROOT / "entregables" / "reportes" / "gepp_max_savings_data.json"
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nPortafolio: antes ${agg['antes']:,.0f} · ahorro ${agg['hibrido']:,.0f} "
          f"({agg['hibrido']/agg['antes']:.0%}) + FP ${agg['fp_lever']:,.0f} · "
          f"CAPEX ${agg['capex']:,.0f} · NPV ${agg['vpn']:,.0f}\n→ {dst}")


if __name__ == "__main__":
    main()
