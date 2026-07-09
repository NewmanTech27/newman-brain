# -*- coding: utf-8 -*-
"""Verify make_project_book.py: the live formulas recalc and reconcile to the engine.

Evaluates the generated workbook with the pure-Python `formulas` engine, then checks:
  - site CAPEX TOTAL (B22)           == calc_core finance Hibrido capex
  - site Resumen TOTAL ahorro (J38)  == engine annual hibrido (+FP)
  - projection Flujo Compra IRR      ~= engine tir_proyecto (Hibrido)
  - a bumped PPA $/kWh moves the financier IRR (liveness)
Run after any change to the builder.
"""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import make_project_book as B
import numpy_financial as nf
import formulas

BILLS = str(TOOLS.parent / "raw" / "bills" / "780881200029")


def _evaluate(path):
    xl = formulas.ExcelModel().loads(str(path)).finish()
    return xl, xl.calculate()


def _cell(sol, book, sheet, ref):
    key = f"'[{book}]{sheet.upper()}'!{ref}"
    v = sol[key].value
    try:
        return float(v[0, 0])
    except Exception:
        return float(v)


def main():
    print("Construyendo libro de prueba (780881200029, sizing auto)...")
    cli = dict(cliente=None, kwp=None, bess_kwh=None, bess_kw=None, fp=False,
               target_irr=0.18, force=False)
    proj = B.load_project(BILLS, {}, cli)
    proj["sheet"] = proj["name"]
    res = proj["res"]
    eng_capex = res["finance"]["Hibrido"]["capex"]
    eng_hib = res["annual"]["hibrido"]
    eng_tir = res["finance"]["Hibrido"]["tir_proyecto"]

    import openpyxl
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    _, rowmap = B.build_supuestos(wb, [proj])
    B.build_site_sheet(wb, proj, rowmap[proj["folder"]])
    B.build_resumen(wb, [proj])
    tmp = Path(tempfile.gettempdir()) / "test_book.xlsx"
    wb.save(tmp)
    book = tmp.name
    sheet = proj["sheet"]

    print("Evaluando fórmulas con `formulas`...")
    xl, sol = _evaluate(tmp)

    capex = _cell(sol, book, sheet, f"B{B.CAP_TOTAL}")
    ahorro = _cell(sol, book, sheet, f"J{B.RES_TOTAL}")
    # projection Flujo Compra (col G) years 0..20
    flow = [_cell(sol, book, sheet, f"G{B.PRJ_Y0 + i}") for i in range(21)]
    tir = nf.irr(flow)
    # financier flows (col K) for liveness check
    finflow = [_cell(sol, book, sheet, f"K{B.PRJ_Y0 + i}") for i in range(21)]
    tir_fin = nf.irr(finflow)

    checks = []
    checks.append(("CAPEX TOTAL == engine", abs(capex - eng_capex) < 1.0, f"{capex:,.0f} vs {eng_capex:,.0f}"))
    checks.append(("Ahorro TOTAL == engine hibrido", abs(ahorro - eng_hib) < 1.0, f"{ahorro:,.0f} vs {eng_hib:,.0f}"))
    checks.append(("TIR compra ~= engine (<=0.6pp)", abs((tir or 0) - (eng_tir or 0)) < 0.006,
                   f"{(tir or 0):.4f} vs {(eng_tir or 0):.4f}"))
    checks.append(("TIR financiador computable", tir_fin is not None, f"{(tir_fin or 0):.4f}"))

    # liveness: bump PPA $/kWh in Supuestos and confirm financier IRR rises
    ppa_cell = f"I{B.MROW0}"  # project's PPA $/kWh in the Supuestos matrix
    base_ppa = _cell(sol, book, "Supuestos", ppa_cell)
    sol2 = xl.calculate(inputs={f"'[{book}]SUPUESTOS'!{ppa_cell}": base_ppa * 1.5})
    finflow2 = [_cell(sol2, book, sheet, f"K{B.PRJ_Y0 + i}") for i in range(21)]
    tir_fin2 = nf.irr(finflow2)
    checks.append(("↑PPA ⇒ ↑TIR financiador (live)", (tir_fin2 or 0) > (tir_fin or 0),
                   f"{(tir_fin or 0):.4f} -> {(tir_fin2 or 0):.4f}"))

    print()
    ok = True
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name:<36} {detail}")
        ok = ok and passed
    print(f"\n{sum(c[1] for c in checks)}/{len(checks)} checks passed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
