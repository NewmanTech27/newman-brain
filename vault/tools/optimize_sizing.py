# -*- coding: utf-8 -*-
"""Regime-aware PV+BESS sizing — maximize CLIENT NPV, do NOT auto-cap at 0.7 MW.

Doctrine (CLAUDE.md 2026-06-19 · [[feedback-pv-sizing-maximize-savings]]):
  The 0.7 MW line is a regulatory STEP, not a sizing cap. The binding economic
  ceiling is solar-coincident self-consumption: calc_core values self-consumed PV
  (aprov = min(gen, monthly intermedio kWh)) at the intermedio rate and everything
  beyond at the excedente rate `texc` (≈0). So client NPV rises with kWp while the
  array stays self-consumed, peaks at the self-consumption ceiling, then declines as
  capex grows against ~zero-value excess. We sweep and pick the peak.

Objective = max client NPV = `vpn_proyecto` of the Hibrido scenario (client-as-owner:
NPV of gross savings − O&M, less CAPEX, discounted at WACC). Maximizing the project
NPV maximizes the pie the client keeps (under a PPA the deal then splits it).

We co-optimize BESS (a few sizes off the punta-peak proposal) jointly with PV, and we
report the global optimum PLUS the best exempt (≤839.41 kWp DC = 0.7 MW AC) and autoconsumo
points, so the regulatory-step tradeoff is explicit rather than assumed.

Known model limit (surface it): calc_core charges the BESS from grid-base, not from PV
surplus, so the "store midday excess → discharge into punta" coupling that would let a
larger PV pay off via storage is NOT credited here. PV optimizes on intermedio
self-consumption, BESS on punta demand/arbitraje (additive in SIN). Crossing 0.7 MW also
triggers autoconsumo overhead (CNE permit, annual registro, min-use, mandatory backup)
not priced in the NPV — flagged, and `--autoconsumo-overhead` lets you charge it.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.stdout.reconfigure(encoding="utf-8")
import calc_core
from cfe_savings import extract, sizing
import solar_lookup

# Generador-exento boundary. The 0.7 MW LSE line is on the AC side (inverter /
# interconnection capacity). PV is DC-oversized ~20% (DC/AC ratio), so the DC module
# capacity that still clears 0.7 MW AC is higher. With 0.715 kWp Tongwei/Trina modules,
# the max exento project = 1,174 módulos × 0.715 = 839.41 kWp DC (= 0.7 MW AC × 1.199).
# `kwp` in the engine is DC, so the regime boundary compared against it is the DC ceiling.
AC_EXENTO_KW = 700.0          # regulatory line — AC / interconnection capacity
DC_AC_RATIO = 1.19916         # ~20% DC oversizing (839.41 / 700)
DG_CEILING = round(AC_EXENTO_KW * DC_AC_RATIO, 2)  # 839.41 kWp DC — exento ceiling


def resolve_yield(inp: dict, bills: list[dict]) -> tuple[dict, str]:
    """Monthly kWh/kWp from any inputs schema. Order:
    flat `yield_monthly` > nested `system.pv_monthly_kwh`/`pv_kwp` (cfe_savings schema) >
    bill CP > municipio > flat default (flagged 'revisar')."""
    if inp.get("yield_monthly"):
        return {int(k): float(v) for k, v in inp["yield_monthly"].items()}, "inputs.json"
    sysd = inp.get("system") or {}
    pm, pk = sysd.get("pv_monthly_kwh"), sysd.get("pv_kwp")
    if pm and pk:
        return ({int(k): float(v) / float(pk) for k, v in pm.items()},
                "inputs.json system.pv_monthly_kwh")
    cp = next((b.get("cp") for b in bills if b.get("cp")), None)
    if cp:
        y = solar_lookup.cp_to_yield(cp)
        if y:
            return y["monthly"], f"CP {cp} -> {y['match']}"
    muni = (inp.get("municipio") or "").split(",")
    if len(muni) == 2:
        y = solar_lookup.municipio_yield(muni[0].strip(), muni[1].strip())
        if y:
            return y["monthly"], y["match"]
    return {m: 145.0 for m in range(1, 13)}, "default plano (1,740 kWh/kWp) — revisar"


def sweep(bills: list[dict], base_inputs: dict, area_m2: float | None = None,
          packing: float = 0.17, n_pv: int = 22, bess_factors=(0.0, 0.5, 1.0, 1.5),
          autoconsumo_overhead: float = 0.0, autoconsumo_delay_years: float = 1.0,
          backup_min_factor: float = 1.0) -> dict:
    """Return {optimo, exento, autoconsumo, curva, kwp_100, max_kwp}.
    Each point: dict(kwp, bess_kw, bess_kwh, npv, tir, ahorro, capex, regimen).

    Autoconsumo (≥0.7 MW) is handicapped on two real fronts (assumptions, tunable):
      - **BESS is mandatory** (intermittent autoconsumo requires SAE/backup, Núm. 4.5 DACG):
        candidates ≥0.7 MW must carry at least `backup_min_factor`× the punta BESS — its CAPEX
        is therefore always in the NPV (no BESS-free autoconsumo).
      - **Permit lag**: CNE permit + interconnection push first savings out ~`autoconsumo_delay_years`
        years, so the savings stream is discounted by (1+WACC)^delay while CAPEX stays at t0."""
    p0 = calc_core.merge_inputs(base_inputs)
    wacc = p0["wacc"]
    ym = p0["yield_monthly"]
    annual_yield = sum(ym.values()) if ym else 1750.0
    n = max(1, len(bills))
    annual_kwh = sum(b.get("kwh_total") or (b["kwh_base"] + b["kwh_inter"] + b["kwh_punta"])
                     for b in bills) * (12.0 / n)
    kwp_100 = annual_kwh / annual_yield if annual_yield else 0.0   # 100% annual-offset size

    # PV grid: spread up to 1.3× the 100%-offset size (NPV peaks well below this),
    # capped by usable area; always sample the exento DC ceiling regime step.
    ceiling = kwp_100 * 1.3 if kwp_100 else 2000.0
    if area_m2:
        ceiling = min(ceiling, area_m2 * packing)
    pts = {round(ceiling * i / n_pv, 1) for i in range(1, n_pv + 1)}
    if ceiling > DG_CEILING:          # always sample the 839.41 kWp DC exento step
        pts |= {DG_CEILING, DG_CEILING + 0.59}   # 839.41 (exento) / 840.0 (autoconsumo)
    grid = sorted(k for k in pts if 0 < k <= ceiling + 1)

    be = sizing.propose_bess(bills, base_inputs.get("division", "SIN"), None)
    bkw0, bkwh0 = float(be["proposed_power_kw"]), float(be["proposed_nominal_kwh"])

    curva = []
    for kwp in grid:
        is_auto = kwp > DG_CEILING   # 839.41 kWp DC (=0.7 MW AC) itself is still exento
        # autoconsumo: BESS is MANDATORY → drop BESS-free / sub-backup options
        factors = [f for f in bess_factors if f >= backup_min_factor] if is_auto else bess_factors
        if not factors:
            factors = [backup_min_factor]
        best = None
        for bf in factors:
            inp = dict(base_inputs, kwp=kwp, bess_kw=bkw0 * bf, bess_kwh=bkwh0 * bf)
            res = calc_core.compute(inp, bills)
            fin = res["finance"]["Hibrido"]
            npv = fin["vpn_proyecto"]
            if is_auto:
                # permit lag: defer the savings stream, keep CAPEX at t0
                savings_pv = npv + fin["capex"]
                npv = -fin["capex"] + savings_pv / (1 + wacc) ** autoconsumo_delay_years
                npv -= autoconsumo_overhead
            pt = dict(kwp=kwp, bess_kw=round(bkw0 * bf), bess_kwh=round(bkwh0 * bf),
                      npv=npv, tir=fin["tir_proyecto"], ahorro=res["annual"]["hibrido"],
                      capex=fin["capex"], pct_ac=res["annual"]["pct_ac_avg"],
                      exced=res["annual"]["exced"],
                      regimen="exento" if not is_auto else "autoconsumo")
            if best is None or pt["npv"] > best["npv"]:
                best = pt
        curva.append(best)

    pick = lambda pts: max(pts, key=lambda r: r["npv"]) if pts else None
    return dict(
        optimo=pick(curva),
        exento=pick([p for p in curva if p["kwp"] <= DG_CEILING]),
        autoconsumo=pick([p for p in curva if p["kwp"] > DG_CEILING]),
        curva=curva, kwp_100=kwp_100, max_kwp=ceiling, annual_kwh=annual_kwh)


def propose(bills: list[dict], base_inputs: dict, area_m2: float | None = None,
            autoconsumo_overhead: float = 0.0, autoconsumo_delay_years: float = 1.0) -> dict:
    """Default sizing for callers: the global client-NPV optimum, with the regime
    decision made explicit. Returns the optimum point + the exento/autoconsumo split.
    Autoconsumo carries a mandatory BESS and a permit-lag savings delay (see `sweep`)."""
    r = sweep(bills, base_inputs, area_m2=area_m2, autoconsumo_overhead=autoconsumo_overhead,
              autoconsumo_delay_years=autoconsumo_delay_years)
    opt = r["optimo"]
    # If the optimum sits in autoconsumo but barely beats the best exento point, prefer
    # exento (the NPV doesn't fully price the autoconsumo overhead). 2% guard band.
    ex, au = r["exento"], r["autoconsumo"]
    if opt and opt["regimen"] == "autoconsumo" and ex and au:
        if au["npv"] <= ex["npv"] * 1.02:
            opt = ex
    r["recomendado"] = opt
    return r


def main():
    ap = argparse.ArgumentParser(description="Maximize-NPV PV+BESS sizing sweep (no 0.7 MW auto-cap)")
    ap.add_argument("bills_dir")
    ap.add_argument("--giro", default="Otro")
    ap.add_argument("--division", default=None)
    ap.add_argument("--area", type=float, default=None, help="usable roof/ground m²")
    ap.add_argument("--autoconsumo-overhead", type=float, default=0.0,
                    help="extra NPV haircut for autoconsumo permit/admin ($)")
    ap.add_argument("--autoconsumo-delay", type=float, default=1.0,
                    help="years of permit lag before autoconsumo savings start (default 1)")
    a = ap.parse_args()

    import json
    bills = extract.extract_folder(a.bills_dir)
    if not bills:
        sys.exit(f"No bills in {a.bills_dir}")
    bills = [b for b in bills if calc_core.validate_bill(b)["ok"]][-12:]
    ijson = Path(a.bills_dir) / "inputs.json"
    inp = json.loads(ijson.read_text(encoding="utf-8")) if ijson.exists() else {}
    ym, ysrc = resolve_yield(inp, bills)
    base = dict(giro=a.giro, division=a.division or inp.get("division", "SIN"),
                yield_monthly=ym,
                demanda_contratada=max((b.get("demanda_contratada") or 0 for b in bills), default=0))
    print(f"Rendimiento solar: {ysrc} (~{sum(ym.values()):,.0f} kWh/kWp/año)")

    r = propose(bills, base, area_m2=a.area, autoconsumo_overhead=a.autoconsumo_overhead,
                autoconsumo_delay_years=a.autoconsumo_delay)
    print(f"\n=== Sizing por máximo NPV cliente — {a.bills_dir} ===")
    print(f"Consumo anual ~{r['annual_kwh']:,.0f} kWh · tamaño 100% offset ~{r['kwp_100']:,.0f} kWp "
          f"· techo barrido {r['max_kwp']:,.0f} kWp")
    print(f"\n{'kWp':>7} {'BESS kW':>8} {'NPV cliente':>15} {'TIR':>7} {'Ahorro/año':>13} "
          f"{'%AC':>5} {'Excedente kWh':>13}  Régimen")
    for p in r["curva"]:
        tir = f"{p['tir']:.1%}" if p["tir"] is not None else "n/a"
        mark = "  <<<" if p is r["recomendado"] else ""
        print(f"{p['kwp']:>7,.0f} {p['bess_kw']:>8,.0f} {p['npv']:>15,.0f} {tir:>7} "
              f"{p['ahorro']:>13,.0f} {p['pct_ac']:>5.0%} {p['exced']:>13,.0f}  {p['regimen']}{mark}")
    rec, ex, au = r["recomendado"], r["exento"], r["autoconsumo"]
    rtir = f"{rec['tir']:.1%}" if rec["tir"] is not None else "n/a"
    print(f"\nRECOMENDADO: PV {rec['kwp']:,.0f} kWp + BESS {rec['bess_kw']:,.0f} kW "
          f"({rec['regimen']}) — NPV ${rec['npv']:,.0f}, TIR {rtir}")
    if ex and au:
        delta = au["npv"] - ex["npv"]
        print(f"Decisión de régimen: mejor EXENTO PV {ex['kwp']:,.0f} kWp (NPV ${ex['npv']:,.0f}) "
              f"vs mejor AUTOCONSUMO PV {au['kwp']:,.0f} kWp (NPV ${au['npv']:,.0f}) "
              f"→ cruzar 0.7 MW {'SÍ' if delta > 0 else 'NO'} aporta ${delta:,.0f} de NPV. "
              f"Autoconsumo ya incluye: BESS obligatorio (respaldo de intermitencia) + "
              f"retraso de {a.autoconsumo_delay:.0f} año(s) por permiso CNE (ahorro descontado).")
    print("Nota modelo: calc_core carga el BESS de red-base (no del excedente PV), así que el "
          "acople 'guardar excedente solar → punta' no está acreditado; PV se optimiza por "
          "autoconsumo intermedio, BESS por punta. 15-min interval data lo haría bancable.")


if __name__ == "__main__":
    main()
