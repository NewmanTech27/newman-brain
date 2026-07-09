"""CLI: python -m cfe_savings <rpu_folder> [--inputs inputs.json] [--net] [--json out.json]

Orchestrates extract -> validate -> savings scenarios -> finance -> report.
Raw bill bytes never leave the engine; stdout is the copy-pastable summary.
"""
from __future__ import annotations
import argparse
import json
import os
import sys

from .extract import extract_folder
from .engine import run_scenarios, receipt_check
from .finance import project_financials, saas_split
from .report import headline_table, scenarios_summary, financial_summary
from .defaults import SYSTEM_DEFAULTS, FINANCE_DEFAULTS


def main(argv=None):
    # The summary uses ✓ and accented Spanish; force UTF-8 so the default Windows
    # console (cp1252) doesn't crash on encode.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(prog="cfe_savings")
    ap.add_argument("folder", help="raw/bills/<RPU>/ folder with bill PDFs")
    ap.add_argument("--inputs", default=None, help="inputs.json (default: <folder>/inputs.json)")
    ap.add_argument("--net", action="store_true", help="show net-of-availability savings in headline")
    ap.add_argument("--json", default=None, help="write full result JSON to this path")
    ap.add_argument("--saas-share", type=float, default=None, help="financier share of net savings (0-1)")
    ap.add_argument("--fp-correction", action="store_true",
                    help="count savings from correcting the cargo por bajo factor de potencia (FP under 90%%); opt-in")
    args = ap.parse_args(argv)

    inputs_path = args.inputs or os.path.join(args.folder, "inputs.json")
    inp = json.load(open(inputs_path, encoding="utf-8")) if os.path.exists(inputs_path) else {}

    bills = extract_folder(args.folder)
    if not bills:
        print("No bill PDFs found in", args.folder); return 1

    sys_cfg = dict(SYSTEM_DEFAULTS)
    sys_cfg.update(inp.get("system", {}))
    sys_cfg["division"] = inp.get("division", sys_cfg.get("division", "SIN"))
    # FP correction: opt-in via --fp-correction flag OR inputs.json system block
    if args.fp_correction:
        sys_cfg["fp_correction_enabled"] = True
    fin_cfg = dict(FINANCE_DEFAULTS)
    fin_cfg.update(inp.get("finance", {}))
    # carry degradation/availability into finance from system block
    for k in ("availability_factor", "pv_degradation", "bess_degradation"):
        if k in sys_cfg:
            fin_cfg.setdefault(k, sys_cfg[k])

    pv_monthly = {int(k): v for k, v in sys_cfg.get("pv_monthly_kwh", {}).items()}
    if not pv_monthly and sys_cfg.get("pv_kwp") and sys_cfg.get("pv_yield_kwh_per_kwp"):
        annual = sys_cfg["pv_kwp"] * sys_cfg["pv_yield_kwh_per_kwp"]
        for b in bills:  # flat shape fallback if no monthly profile supplied
            pv_monthly[b["month"]] = annual / 12.0

    res = run_scenarios(bills, sys_cfg, pv_monthly)
    cm = res["combined"]
    pv_base = sum(r["ahorro_pv"] for r in cm["months"])
    bess_base = sum(r["ahorro_capacidad"] + r["ahorro_arbitraje"] for r in cm["months"])
    fp_base = sum(r["ahorro_fp_correction"] for r in cm["months"])
    capex = fin_cfg.get("capex_total_mxn") or 0.0
    proj = project_financials(pv_base, bess_base, capex, fin_cfg, fp_base=fp_base)
    saas = saas_split(proj, args.saas_share, capex, fin_cfg) if args.saas_share else None

    # validation
    checks = [(b["month"], receipt_check(b)) for b in bills]

    print(f"\n=== RPU {inp.get('rpu','?')}  |  {inp.get('site','')}  |  división {sys_cfg['division']} ===")
    print(f"PV {sys_cfg.get('pv_kwp','?')} kWp · BESS {sys_cfg.get('bess_nominal_kwh','?')} kWh / "
          f"{sys_cfg.get('bess_power_kw','?')} kW · availability {sys_cfg.get('availability_factor')}")
    fp_penalty_measured = sum(b.get("cargo_fp_penalty", 0.0) for b in bills)
    if sys_cfg.get("fp_correction_enabled"):
        print(f"FP correction ON · cargo por bajo FP medido en recibos = ${fp_penalty_measured:,.0f}/año")
    elif fp_penalty_measured > 0:
        print(f"(FP correction OFF · recibos traen cargo por bajo FP ${fp_penalty_measured:,.0f}/año — usa --fp-correction)")

    print("\n--- BASELINE VALIDATION (bill internal arithmetic) ---")
    bad = [(m, c) for m, c in checks if c and abs(c["delta_pct"]) > 0.005]
    if bad:
        for m, c in bad:
            print(f"  ⚠ month {m}: calc {c['calc_con_iva']:,.0f} vs receipt {c['facturacion_recibo']:,.0f} "
                  f"({c['delta_pct']*100:+.2f}%)")
    else:
        print("  ✓ all bills foot within 0.5% (no CFE arithmetic errors detected)")

    print("\n--- HEADLINE (combined PV+BESS, " + ("net of availability" if args.net else "gross") + ") ---")
    print(headline_table(cm, net=args.net))
    print("\n--- SCENARIOS ---")
    print(scenarios_summary(res))
    print("\n--- " + financial_summary(proj, saas))

    if args.json:
        json.dump({"rpu": inp.get("rpu"), "scenarios": res, "finance": proj, "saas": saas},
                  open(args.json, "w", encoding="utf-8"), indent=2, default=float)
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
