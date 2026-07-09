# -*- coding: utf-8 -*-
"""PPA pricer — solve the PPA $/kWh (or the BESS savings-share) that hits a target
financier IRR, on top of the deterministic calc_core scenario.

Doctrine (CLAUDE.md financial reporting):
  - Unlevered project IRR answers "is it worth building" — calc_core already gives it.
  - Financier IRR depends on deal terms — THIS module makes those terms explicit and
    solves them, instead of treating the PPA rate as a frozen input.
  - The financier cashflow here reproduces calc_core._finance's `fl_new` EXACTLY
    (validated: defaults on the 780881200029 demo give the same TIR to 1e-9).
    calc_core/engine are never modified — golden test untouched.

Deal structure modeled (the SaaS/PPA hybrid used by the business):
  financier funds CAPEX; receives PPA $/kWh on PV generation (term/escalation) +
  `comision` x BESS savings (term bess_yrs); pays O&M + fianza. Client keeps
  bruto - ppa_pay - comision (their bill savings minus what they pay the financier).

Usage:
  python tools/ppa_pricer.py raw/bills/<RPU> --target-irr 0.18
  python tools/ppa_pricer.py raw/bills/<RPU> --target-irr 0.18 --solve comision --ppa 1.2
  python tools/ppa_pricer.py raw/bills/<RPU> --target-irr 0.18 --kwp 700 --bess-kwh 1700 --bess-kw 850 --giro "Industrial 24/7"

Library use (webapp / proposal factory):
  price(inputs, bills, target_irr=0.18, solve="ppa", ...) -> dict
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import calc_core


# ---------------------------------------------------------------- cashflows

def _bases(p: dict, annual: dict, esc: str) -> dict:
    """Mirror of calc_core._finance's per-scenario savings bases."""
    has_pv = esc in ("PV", "Hibrido") and p["kwp"] > 0
    has_bess = esc in ("BESS", "Hibrido") and p["bess_kwh"] > 0
    base_pv = (annual["ah_pv"] + annual["dem_pv"]) if has_pv else 0.0
    if esc == "Hibrido":
        base_bess = annual["dem_bess_h"] + annual["arb"]
        bruto0 = annual["hibrido"]
    elif esc == "BESS":
        base_bess = annual["bess_only"]
        bruto0 = annual["bess_only"]
    else:
        base_bess, bruto0 = 0.0, annual["pv_only"]
    base_claw = bruto0 - base_pv - base_bess if esc != "BESS" else 0.0
    capex = (p["capex_pv"] if has_pv else 0.0) + (p["capex_bess"] if has_bess else 0.0)
    return dict(has_pv=has_pv, has_bess=has_bess, base_pv=base_pv,
                base_bess=base_bess, base_claw=base_claw, capex=capex,
                gen=annual["gen"] if has_pv else 0.0)


def deal_flows(p: dict, annual: dict, esc: str, ppa: float, ppa_yrs: int,
               esc_ppa: float, comision: float) -> dict:
    """Financier + client yearly cashflows under explicit deal terms.
    Identical math to calc_core._finance fl_new, with deal terms as arguments."""
    b = _bases(p, annual, esc)
    fl_fin, fl_cli, rows = [-b["capex"]], [0.0], []
    for yy in range(1, p["horizon"] + 1):
        e = (1 + p["esc_cfe"]) ** yy
        dpv = (1 - p["pv_degr"]) ** yy
        dbe = (1 - p["bess_degr"]) ** yy
        sav_pv = b["base_pv"] * e * dpv
        sav_bess = b["base_bess"] * e * dbe * p["falla"]
        clw = b["base_claw"] * e * (dpv + dbe) / 2
        bruto = sav_pv + sav_bess + clw
        ppa_pay = (b["gen"] * dpv * ppa * (1 + esc_ppa) ** (yy - 1)
                   if (b["has_pv"] and yy <= ppa_yrs) else 0.0)
        com = sav_bess * comision if (b["has_bess"] and yy <= p["bess_yrs"]) else 0.0
        ompv = p["om_pv"] * (1 + p["esc_cfe"]) ** (yy - 1) if (b["has_pv"] and yy <= ppa_yrs) else 0.0
        ombe = p["om_bess"] * (1 + p["esc_cfe"]) ** (yy - 1) if (b["has_bess"] and yy <= p["bess_yrs"]) else 0.0
        fz = ppa_pay * p["fianza"]
        fl_fin.append(ppa_pay + com - ompv - ombe - fz)
        fl_cli.append(bruto - ppa_pay - com)
        rows.append(dict(year=yy, bruto=bruto, ppa_pay=ppa_pay, comision=com,
                         om=ompv + ombe, fianza=fz,
                         financier=fl_fin[-1], cliente=fl_cli[-1]))
    return dict(capex=b["capex"], fl_fin=fl_fin, fl_cli=fl_cli, rows=rows)


def _irr(flows, lo=-0.95, hi=4.0):
    f = lambda r: sum(x / (1 + r) ** i for i, x in enumerate(flows))
    if not flows or f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _npv(flows, rate):
    return sum(x / (1 + rate) ** i for i, x in enumerate(flows))


# ---------------------------------------------------------------- solvers

def financier_irr(p, annual, esc, ppa, ppa_yrs, esc_ppa, comision):
    return _irr(deal_flows(p, annual, esc, ppa, ppa_yrs, esc_ppa, comision)["fl_fin"])


def solve_ppa_rate(p, annual, esc, target_irr, ppa_yrs, esc_ppa, comision,
                   lo=0.0, hi=12.0) -> float | None:
    """Bisection on the PPA rate (financier IRR is monotonic in it)."""
    f = lambda r: (financier_irr(p, annual, esc, r, ppa_yrs, esc_ppa, comision)
                   or -1.0) - target_irr
    if f(hi) < 0:
        return None  # even an absurd rate can't reach the target
    if f(lo) > 0:
        return 0.0   # target met with no PPA at all (comision alone carries it)
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def solve_comision(p, annual, esc, target_irr, ppa, ppa_yrs, esc_ppa,
                   lo=0.0, hi=1.0) -> float | None:
    """Bisection on the BESS savings-share."""
    f = lambda c: (financier_irr(p, annual, esc, ppa, ppa_yrs, esc_ppa, c)
                   or -1.0) - target_irr
    if f(hi) < 0:
        return None
    if f(lo) > 0:
        return 0.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- main API

def price(inputs: dict, bills: list[dict], target_irr: float = 0.18,
          solve: str = "ppa", escenario: str | None = None,
          ppa_yrs: int | None = None, esc_ppa: float | None = None,
          ppa: float | None = None, comision: float | None = None,
          sensitivity: bool = True) -> dict:
    """Run calc_core, then solve the deal term for the target financier IRR.

    solve = "ppa"      -> find PPA $/kWh holding comision fixed
    solve = "comision" -> find BESS savings-share holding PPA rate fixed
    """
    res = calc_core.compute(inputs, bills)
    p, annual = res["inputs"], res["annual"]
    esc = escenario or p.get("escenario", "Hibrido")
    ppa_yrs = int(ppa_yrs if ppa_yrs is not None else p["ppa_yrs"])
    esc_ppa = float(esc_ppa if esc_ppa is not None else p["esc_ppa"])
    ppa0 = float(ppa if ppa is not None else p["ppa"])
    com0 = float(comision if comision is not None else p["comision"])

    out = dict(escenario=esc, target_irr=target_irr, solve=solve,
               ppa_yrs=ppa_yrs, esc_ppa=esc_ppa,
               tir_proyecto=res["finance"][esc]["tir_proyecto"],
               capex=res["finance"][esc]["capex"],
               bruto_anio0=res["finance"][esc]["bruto_anio0"],
               regimen=res["regimen"], annual=annual)

    if solve == "comision":
        sol = solve_comision(p, annual, esc, target_irr, ppa0, ppa_yrs, esc_ppa)
        out["ppa_rate"] = ppa0
        out["comision"] = sol
        solved_ppa, solved_com = ppa0, sol
    else:
        sol = solve_ppa_rate(p, annual, esc, target_irr, ppa_yrs, esc_ppa, com0)
        out["ppa_rate"] = sol
        out["comision"] = com0
        solved_ppa, solved_com = sol, com0
    out["feasible"] = sol is not None

    if sol is not None:
        d = deal_flows(p, annual, esc, solved_ppa, ppa_yrs, esc_ppa, solved_com)
        out["tir_financiador"] = _irr(d["fl_fin"])
        out["vpn_financiador"] = _npv(d["fl_fin"], p["wacc"])
        out["flows"] = d["rows"]
        cli = d["fl_cli"][1:]
        out["cliente"] = dict(
            beneficio_anio1=cli[0],
            beneficio_total=sum(cli),
            anios_negativos=[i + 1 for i, x in enumerate(cli) if x < -1e-6],
            pct_ahorro_retenido_a1=(cli[0] / d["rows"][0]["bruto"]
                                    if d["rows"][0]["bruto"] else None),
        )
        # sanity reference: client's blended CFE rate vs the PPA rate
        kwh_tot = sum(r["kwh_total"] for r in res["monthly"])
        out["cliente"]["tarifa_cfe_blend"] = (annual["antes"] / kwh_tot) if kwh_tot else None

    if sensitivity and solve == "ppa":
        grid = {}
        for t in (10, 15, 20):
            for ev in (0.0, 0.03, 0.05):
                r = solve_ppa_rate(p, annual, esc, target_irr, t, ev, com0)
                grid[f"{t}y/{ev:.0%}"] = r
        out["sensibilidad"] = grid
    return out


# ---------------------------------------------------------------- CLI

def main():
    from cfe_savings import extract, sizing
    import solar_lookup

    ap = argparse.ArgumentParser(description="Solve PPA rate / savings-share for a target financier IRR")
    ap.add_argument("bills_dir")
    ap.add_argument("--target-irr", type=float, default=0.18)
    ap.add_argument("--solve", choices=["ppa", "comision"], default="ppa")
    ap.add_argument("--escenario", choices=["PV", "BESS", "Hibrido"], default="Hibrido")
    ap.add_argument("--kwp", type=float, default=None)
    ap.add_argument("--bess-kwh", type=float, default=None)
    ap.add_argument("--bess-kw", type=float, default=None)
    ap.add_argument("--giro", default="Otro")
    ap.add_argument("--term", type=int, default=None, help="PPA term years")
    ap.add_argument("--esc-ppa", type=float, default=None)
    ap.add_argument("--ppa", type=float, default=None, help="fixed PPA rate when solving comision")
    ap.add_argument("--comision", type=float, default=None, help="fixed share when solving ppa")
    a = ap.parse_args()

    bills = extract.extract_folder(a.bills_dir)
    if not bills:
        sys.exit(f"No bills in {a.bills_dir}")
    bills = bills[-12:]
    bad = [b for b in bills if not calc_core.validate_bill(b)["ok"]]
    if bad:
        sys.exit(f"{len(bad)} recibos no cuadran (>0.5%) — corregir antes de cotizar")

    import optimize_sizing, json
    cp = next((b.get("cp") for b in bills if b.get("cp")), None)
    yld = solar_lookup.cp_to_yield(cp) if cp else None
    ijson = Path(a.bills_dir) / "inputs.json"
    inp_file = json.loads(ijson.read_text(encoding="utf-8")) if ijson.exists() else {}
    division = (yld or {}).get("division") or inp_file.get("division", "SIN")
    ym, _ = optimize_sizing.resolve_yield({**inp_file, "yield_monthly": (yld or {}).get("monthly")}, bills)
    dcon = max((b.get("demanda_contratada") or 0 for b in bills), default=0)
    # max-NPV sweep decides PV+BESS unless overridden (NO 0.7 MW auto-cap)
    if a.kwp is None:
        opt = optimize_sizing.propose(bills, dict(giro=a.giro, division=division,
              yield_monthly=ym, demanda_contratada=dcon or None))["recomendado"]
        kwp, bkwh_d, bkw_d = opt["kwp"], float(opt["bess_kwh"]), float(opt["bess_kw"])
    else:
        be = sizing.propose_bess(bills, division, autonomy_hours=None)
        kwp, bkwh_d, bkw_d = a.kwp, float(be["proposed_nominal_kwh"]), float(be["proposed_power_kw"])
    inputs = dict(
        giro=a.giro,
        kwp=kwp,
        bess_kwh=a.bess_kwh if a.bess_kwh is not None else bkwh_d,
        bess_kw=a.bess_kw if a.bess_kw is not None else bkw_d,
        division=division,
        yield_monthly=ym,
        demanda_contratada=dcon,
        escenario=a.escenario,
    )

    r = price(inputs, bills, target_irr=a.target_irr, solve=a.solve,
              escenario=a.escenario, ppa_yrs=a.term, esc_ppa=a.esc_ppa,
              ppa=a.ppa, comision=a.comision)

    fmt = lambda x: "n/a" if x is None else f"{x:,.4f}"
    print(f"\n=== PPA Pricer — {a.bills_dir} · escenario {r['escenario']} ===")
    print(f"CAPEX ${r['capex']:,.0f} · ahorro bruto año-0 ${r['bruto_anio0']:,.0f} · "
          f"TIR proyecto {r['tir_proyecto']:.1%}")
    if not r["feasible"]:
        print(f"NO ALCANZABLE: ni el término extremo llega a TIR {a.target_irr:.0%} — "
              f"revisar CAPEX/sizing o bajar el target")
        return
    print(f"Target TIR financiador {r['target_irr']:.1%} -> "
          f"{'PPA $' + fmt(r['ppa_rate']) + '/kWh' if a.solve == 'ppa' else 'comisión ' + f'{r:.1%}'.format(r=r['comision'])}"
          f"  (término {r['ppa_yrs']} años, esc. PPA {r['esc_ppa']:.0%}, "
          f"comisión BESS {r['comision']:.0%})")
    print(f"Verificación: TIR financiador resuelta {r['tir_financiador']:.4%} · "
          f"VPN financiador ${r['vpn_financiador']:,.0f}")
    c = r["cliente"]
    print(f"Cliente: beneficio año 1 ${c['beneficio_anio1']:,.0f} "
          f"({c['pct_ahorro_retenido_a1']:.0%} del ahorro bruto) · "
          f"tarifa CFE blend ${c['tarifa_cfe_blend']:.2f}/kWh vs PPA ${r['ppa_rate']:.2f}/kWh")
    if c["anios_negativos"]:
        print(f"⚠ Años con beneficio NEGATIVO para el cliente: {c['anios_negativos']} — deal no vendible así")
    if "sensibilidad" in r:
        print("Sensibilidad (término/escalación -> PPA $/kWh):")
        for k, v in r["sensibilidad"].items():
            print(f"  {k:>8}: {fmt(v)}")


if __name__ == "__main__":
    main()
