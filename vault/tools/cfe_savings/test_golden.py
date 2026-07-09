"""Golden regression test: the engine must reproduce the CORRECTED reference
(780881200029 - Calculadora v2.xlsx / the 2026-06-11 calculadora audit) for
RPU 780881200029, peso-exact.

Re-baselined 2026-06-11: arbitrage limited to punta weekdays + capped at the
bill's punta kWh (was 365 cycles/yr uncapped, inherited from the client Excel);
FP bonificacion claw-back added. Old golden: Ahorro $7,593,969 / 25.2%.
See wiki/analyses/2026-06-11-780881200029-calculadora-audit.md.

Run: "$PY" tools/cfe_savings/test_golden.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cfe_savings import extract_folder, run_scenarios, baseline_month, derive_rates  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOLDER = os.path.join(ROOT, "raw", "bills", "780881200029")


def approx(a, b, tol):
    return abs(a - b) <= tol


def main():
    inp = json.load(open(os.path.join(FOLDER, "inputs.json"), encoding="utf-8"))
    bills = extract_folder(FOLDER)
    sysc = dict(inp["system"]); sysc["division"] = inp["division"]
    pv = {int(k): v for k, v in sysc["pv_monthly_kwh"].items()}
    res = run_scenarios(bills, sysc, pv)
    t = res["combined"]["total"]

    checks = []
    checks.append(("bills count", len(bills) == 12, len(bills)))
    checks.append(("baseline", approx(sum(baseline_month(b) for b in bills), 30157371, 50), None))
    checks.append(("kWh consumo", approx(t["kwh_consumo"], 10414208, 1), t["kwh_consumo"]))
    checks.append(("PV gen", approx(t["pv_gen_kwh"], 350116, 1), t["pv_gen_kwh"]))
    checks.append(("BESS desc", approx(t["bess_disch_kwh"], 670200, 2), t["bess_disch_kwh"]))
    checks.append(("Bill ANTES", approx(t["bill_antes"], 30157371, 50), t["bill_antes"]))
    checks.append(("Bill DESPUES", approx(t["bill_despues_gross"], 23074119, 50), t["bill_despues_gross"]))
    checks.append(("Ahorro $", approx(t["ahorro_total_gross"], 7083252, 50), t["ahorro_total_gross"]))
    checks.append(("Ahorro %", approx(t["ahorro_pct_gross"], 0.2349, 0.001), t["ahorro_pct_gross"]))
    cap = sum(r["ahorro_capacidad"] for r in res["combined"]["months"])
    arb = sum(r["ahorro_arbitraje"] for r in res["combined"]["months"])
    checks.append(("cap savings", approx(cap, 5590209, 200), cap))
    checks.append(("arb savings (weekday+punta-capped)", approx(arb, 790049, 5), arb))
    claw = sum(r["ahorro_bonif_clawback"] for r in res["combined"]["months"])
    checks.append(("bonif claw-back", approx(claw, -84528, 5), claw))
    # physics guard: no month may discharge more punta kWh than the bill holds
    viol = [b["month"] for b, r in zip(bills, res["combined"]["months"])
            if r["bess_disch_kwh"] > b["kwh_punta"] + 0.01]
    checks.append(("disch <= punta kWh (all months)", not viol, viol))
    # FP correction is opt-in and these PDFs have FP>=90% (no penalty) -> must be 0,
    # so the headline is unaffected by the FP feature.
    fp_penalty = sum(b.get("cargo_fp_penalty", 0.0) for b in bills)
    checks.append(("FP penalty == 0 (no FP feature impact)", approx(fp_penalty, 0.0, 1), fp_penalty))
    fp_corr = sum(r["ahorro_fp_correction"] for r in res["combined"]["months"])
    checks.append(("FP correction off by default", approx(fp_corr, 0.0, 1), fp_corr))

    # distribución rule: billed on max(B,I,P), not KWMax, on ABR/OCT/DIC
    for b in bills:
        if b["month"] in (4, 10, 12):
            r = derive_rates(b)
            mx = max(b["kw_base"], b["kw_inter"], b["kw_punta"])
            billed = b["distribucion"] / r["r_dist"]
            ok = approx(billed, min(mx, r["umbral"]), 1) and b["kw_max"] > mx + 1
            checks.append((f"distrib basis m{b['month']} (max={mx:.0f} vs KWMax={b['kw_max']:.0f})", ok, billed))

    passed = sum(1 for _, ok, _ in checks if ok)
    for name, ok, val in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {val}" if (not ok and val is not None) else ""))
    print(f"\n{passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
