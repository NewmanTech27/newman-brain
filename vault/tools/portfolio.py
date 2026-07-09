# -*- coding: utf-8 -*-
"""Portfolio batch runner — todo raw/bills/* en una pasada determinística.

Recorre cada carpeta raw/bills/<RPU>/, parsea los recibos (PDF/CFDI XML),
valida el footing de cada uno, corre los 3 escenarios de calc_core y agrega
los totales del portafolio. Un RPU con recibos que no cuadran (>0.5%) se
reporta como INVÁLIDO y se excluye del agregado — la doctrina no construye
encima de un recibo que no cuadra.

Config por servicio (en orden de precedencia):
  1. tools/portfolio_overrides.json  — {"<RPU>": {"giro": ..., "cliente": ...}}
     (vive FUERA de raw/ porque raw/ es inmutable)
  2. raw/bills/<RPU>/inputs.json     — sizing/finanzas del análisis archivado
  3. derivación automática            — CP→municipio→yield, sizing propuesto

Niveles de hecho: recibos = fuente primaria · ahorros = derivados del motor
(calc_core v2, golden-validado) · yield/curva = supuesto (prefactibilidad).

CLI:
  python tools/portfolio.py            # tabla es-MX en consola
  python tools/portfolio.py --json     # payload completo (el de /api/portfolio)
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from cfe_savings import extract, sizing  # noqa: E402
import calc_core                          # noqa: E402
import solar_lookup                       # noqa: E402

BILLS_ROOT = ROOT / "raw" / "bills"
OVERRIDES = TOOLS / "portfolio_overrides.json"
MES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
       "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ---------------------------------------------------------------- inputs.json
def _inputs_from_json(d: dict) -> dict:
    """Mapea el inputs.json archivado (esquema del analista) a calc_core."""
    s, f = d.get("system", {}), d.get("finance", {})
    out = dict(rpu=d.get("rpu", ""), division=d.get("division", "SIN"))
    kwp = s.get("pv_kwp")
    if kwp:
        out["kwp"] = float(kwp)
        pm = s.get("pv_monthly_kwh") or {}
        if pm:  # inputs.json guarda kWh absolutos; calc_core espera kWh/kWp
            out["yield_monthly"] = {int(k): float(v) / float(kwp) for k, v in pm.items()}
    for src, dst in (("bess_nominal_kwh", "bess_kwh"), ("bess_power_kw", "bess_kw"),
                     ("dod", "dod"), ("rte", "rte")):
        if s.get(src) is not None:
            out[dst] = float(s[src])
    if s.get("availability_factor") is not None:
        out["falla_meses"] = round(12 * (1 - float(s["availability_factor"])))
    if s.get("fp_correction_enabled"):
        out["fp_correction"] = True
    for src, dst in (("wacc", "wacc"), ("cfe_escalation", "esc_cfe"),
                     ("ppa_escalation", "esc_ppa"), ("ppa_rate_mxn_per_kwh", "ppa"),
                     ("ppa_term_years", "ppa_yrs"), ("horizon_years", "horizon"),
                     ("om_pv_mxn_yr", "om_pv"), ("om_bess_mxn_yr", "om_bess"),
                     ("fx_mxn_per_usd", "fx"), ("epc_pv_usd_per_wp", "epc_usd_wp")):
        if f.get(src) is not None:
            out[dst] = (int(f[src]) if dst in ("ppa_yrs", "horizon") else float(f[src]))
    if f.get("bess_cost_mxn_per_kwh") and out.get("fx", 17.55):
        out["epc_bess"] = float(f["bess_cost_mxn_per_kwh"]) / float(f.get("fx_mxn_per_usd", 17.55))
    return out


def _derive_inputs(bills: list[dict]) -> dict:
    """Sin inputs.json: deriva lo que los recibos dan (mismo camino que el cotizador)."""
    cp = next((b.get("cp") for b in bills if b.get("cp")), None)
    yld = solar_lookup.cp_to_yield(cp) if cp else None
    division = (yld or {}).get("division", "SIN")
    pv = sizing.propose_pv_kwp(bills, area_m2=None, packing=0.17)
    be = sizing.propose_bess(bills, division, autonomy_hours=None)
    return dict(
        rpu=next((b.get("servicio") for b in bills if b.get("servicio")), ""),
        division=division,
        municipio=(f"{yld['municipio']}, {yld['estado']}" if yld else ""),
        yield_monthly=(yld or {}).get("monthly", {}),
        kwp=min(pv["proposed_kwp"], 699.0),
        bess_kwh=be["proposed_nominal_kwh"], bess_kw=be["proposed_power_kw"],
        demanda_contratada=max((b.get("demanda_contratada") or 0 for b in bills), default=0),
    )


# ---------------------------------------------------------------- per service
def load_service(d: Path, overrides: dict) -> dict:
    bills = extract.extract_folder(str(d))
    if not bills:
        return dict(rpu=d.name, status="vacio", site="", months=0)
    bills = bills[-12:]
    meta_path = d / "inputs.json"
    site = ""
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        site = meta.get("site", "")
        inputs = _inputs_from_json(meta)
        if not inputs.get("demanda_contratada"):
            inputs["demanda_contratada"] = max(
                (b.get("demanda_contratada") or 0 for b in bills), default=0)
    else:
        inputs = _derive_inputs(bills)
    inputs.update(overrides.get(d.name, {}))
    inputs.setdefault("rpu", d.name)

    vals = [dict(year=b["year"], month=b["month"], **calc_core.validate_bill(b))
            for b in bills]
    bad = [f"{v['year']}-{v['month']:02d}" for v in vals if not v["ok"]]
    svc = dict(
        rpu=inputs["rpu"], site=site, cliente=inputs.get("cliente", ""),
        division=inputs.get("division", "SIN"),
        municipio=inputs.get("municipio", ""),
        months=len(bills), bad_bills=bad,
        kwp=inputs.get("kwp", 0.0), bess_kwh=inputs.get("bess_kwh", 0.0),
        bess_kw=inputs.get("bess_kw", 0.0),
        fp_correction=bool(inputs.get("fp_correction")),
        config_source=("inputs.json" if meta_path.exists() else "derivado"),
    )
    if bad:
        svc.update(status="invalido", validacion=vals)
        return svc

    res = calc_core.compute(inputs, bills)
    a, fin = res["annual"], res["finance"]
    esc_fin = fin.get("Hibrido") or {}
    fp = a["fp_lever"]
    levers = dict(pv=a["ah_pv"] + a["dem_pv"], bess=a["dem_bess_h"] + a["arb"], fp=fp)
    svc.update(
        status="ok",
        antes=a["antes"], kwh_total=sum(r["kwh_total"] for r in res["monthly"]),
        gen=a["gen"],
        pv_only=a["pv_only"], bess_only=a["bess_only"], hibrido=a["hibrido"],
        fp_cargo=a["fp_cargo"], fp_lever=fp,
        total=a["hibrido"] + fp,
        pct=(a["hibrido"] + fp) / a["antes"] if a["antes"] else 0.0,
        neto_disp=a["neto_disp"]["hibrido"] + fp,
        levers=levers,
        best_lever=max(levers, key=lambda k: levers[k]),
        capex=esc_fin.get("capex"),
        tir_proyecto=esc_fin.get("tir_proyecto"),
        payback=esc_fin.get("payback_proyecto"),
        regimen=res["regimen"]["regimen"],
        alerts=res["regimen"]["alerts"],
        monthly=[dict(year=r["year"], month=r["month"], mes=MES[r["month"]],
                      antes=r["antes"], hibrido=r["hibrido"],
                      fp=r["fp_cargo"] if svc["fp_correction"] else 0.0,
                      kwh=r["kwh_total"]) for r in res["monthly"]],
        validacion=vals,
    )
    return svc


# ----------------------------------------------------------------- aggregate
def run(bills_root: Path | str = BILLS_ROOT) -> dict:
    bills_root = Path(bills_root)
    overrides = (json.loads(OVERRIDES.read_text(encoding="utf-8"))
                 if OVERRIDES.exists() else {})
    services = []
    if bills_root.exists():
        for d in sorted(bills_root.iterdir()):
            if d.is_dir() and (list(d.glob("*.pdf")) + list(d.glob("*.xml"))
                               or (d / "bills.json").exists()):
                services.append(load_service(d, overrides))
    ok = [s for s in services if s.get("status") == "ok"]
    S = lambda k: sum(s[k] for s in ok)
    agg = dict(
        servicios=len(services), ok=len(ok),
        invalidos=sum(1 for s in services if s.get("status") == "invalido"),
        antes=S("antes"), kwh_total=S("kwh_total"), gen=S("gen"),
        pv_only=S("pv_only"), bess_only=S("bess_only"), hibrido=S("hibrido"),
        fp_lever=S("fp_lever"), total=S("total"), neto_disp=S("neto_disp"),
        pct=(S("total") / S("antes")) if ok and S("antes") else 0.0,
        capex=sum(s["capex"] or 0 for s in ok),
        levers=dict(pv=sum(s["levers"]["pv"] for s in ok),
                    bess=sum(s["levers"]["bess"] for s in ok),
                    fp=sum(s["levers"]["fp"] for s in ok)),
        kwp=S("kwp"), bess_kwh=S("bess_kwh"),
    )
    return dict(generated=datetime.now().isoformat(timespec="seconds"),
                services=services, aggregate=agg,
                doctrina="recibos=fuente primaria · ahorros=motor v2 golden-validado · yield/curva=supuesto")


# ----------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description="Portafolio: todos los RPU de raw/bills/")
    ap.add_argument("--json", action="store_true", help="payload completo JSON")
    ap.add_argument("--bills-root", default=str(BILLS_ROOT))
    a = ap.parse_args()
    res = run(a.bills_root)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return
    mxn = lambda x: f"${x:,.0f}"
    print(f"\nPORTAFOLIO — {res['aggregate']['servicios']} servicios "
          f"({res['aggregate']['ok']} ok, {res['aggregate']['invalidos']} inválidos)\n")
    hdr = f"{'RPU':<14}{'Sitio':<38}{'Meses':>6}{'Bill ANTES':>15}{'Híbrido':>13}{'FP':>11}{'Total':>13}{'%':>7}  Palanca"
    print(hdr); print("-" * len(hdr))
    for s in res["services"]:
        if s.get("status") != "ok":
            print(f"{s['rpu']:<14}{(s.get('site') or '')[:36]:<38}{s.get('months', 0):>6}"
                  f"{'— ' + s.get('status', '?').upper():>15}")
            continue
        print(f"{s['rpu']:<14}{(s['site'] or s['municipio'])[:36]:<38}{s['months']:>6}"
              f"{mxn(s['antes']):>15}{mxn(s['hibrido']):>13}{mxn(s['fp_lever']):>11}"
              f"{mxn(s['total']):>13}{s['pct']:>6.1%}  {s['best_lever'].upper()}")
    ag = res["aggregate"]
    print("-" * len(hdr))
    print(f"{'TOTAL':<58}{mxn(ag['antes']):>15}{mxn(ag['hibrido']):>13}"
          f"{mxn(ag['fp_lever']):>11}{mxn(ag['total']):>13}{ag['pct']:>6.1%}")
    print(f"\nPalancas agregadas: PV {mxn(ag['levers']['pv'])} · "
          f"BESS {mxn(ag['levers']['bess'])} · FP {mxn(ag['levers']['fp'])}")
    print(f"Sistemas: {ag['kwp']:,.0f} kWp PV · {ag['bess_kwh']:,.0f} kWh BESS · "
          f"CAPEX {mxn(ag['capex'])}")
    print(f"\n[{res['doctrina']}]")


if __name__ == "__main__":
    main()
