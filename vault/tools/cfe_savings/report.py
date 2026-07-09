"""Render the copy-pastable headline table + scenario/financial summary."""
from __future__ import annotations

_MES = {1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"}


def _mes(r):
    return f"{_MES[r['month']]} {str(r['year'])[2:]}"


def headline_table(combined: dict, net: bool = False) -> str:
    """Excel RESUMEN MENSUAL-style table for the combined scenario.
    Columns: Mes | kWh Consumo | Generación kWh | kWh BESS desc |
             Bill ANTES $ | Bill DESPUÉS $ | Ahorro $ | Ahorro %"""
    desp = "bill_despues_net" if net else "bill_despues_gross"
    tot_key = "ahorro_total_net" if net else "ahorro_total_gross"
    rows = combined["months"]
    t = combined["total"]
    h = ["Mes", "kWh Consumo", "Generación kWh", "kWh BESS desc",
         "Bill ANTES $", "Bill DESPUÉS $", "Ahorro $", "Ahorro %"]
    out = ["\t".join(h)]
    for r in rows:
        ahorro = r[tot_key]
        pct = ahorro / r["bill_antes"] if r["bill_antes"] else 0
        out.append("\t".join([
            _mes(r),
            f"{r['kwh_consumo']:,.0f}",
            f"{r['pv_gen_kwh']:,.0f}",
            f"{r['bess_disch_kwh']:,.0f}",
            f"{r['bill_antes']:,.0f}",
            f"{r[desp]:,.0f}",
            f"{ahorro:,.0f}",
            f"{pct*100:.1f}%",
        ]))
    pct_t = t["ahorro_pct_net"] if net else t["ahorro_pct_gross"]
    out.append("\t".join([
        "TOTAL",
        f"{t['kwh_consumo']:,.0f}",
        f"{t['pv_gen_kwh']:,.0f}",
        f"{t['bess_disch_kwh']:,.0f}",
        f"{t['bill_antes']:,.0f}",
        f"{t['bill_despues_net'] if net else t['bill_despues_gross']:,.0f}",
        f"{t[tot_key]:,.0f}",
        f"{pct_t*100:.1f}%",
    ]))
    return "\n".join(out)


def scenarios_summary(res: dict) -> str:
    out = ["Escenario\tAhorro $ (gross)\tAhorro %\tAhorro $ (net avail)\tAhorro % (net)"]
    label = {"pv": "PV solo", "bess": "BESS solo", "combined": "PV + BESS"}
    for scen in ("pv", "bess", "combined"):
        t = res[scen]["total"]
        out.append("\t".join([label[scen],
                              f"{t['ahorro_total_gross']:,.0f}",
                              f"{t['ahorro_pct_gross']*100:.1f}%",
                              f"{t['ahorro_total_net']:,.0f}",
                              f"{t['ahorro_pct_net']*100:.1f}%"]))
    return "\n".join(out)


def financial_summary(proj: dict, saas: dict | None = None) -> str:
    def m(x):
        return f"${x:,.0f}" if x is not None else "n/a"

    def p(x):
        return f"{x*100:.1f}%" if x is not None else "n/a"

    lines = [
        "FINANCIAL (project / unlevered)",
        f"  CAPEX                 {m(proj['capex'])}",
        f"  Ahorro Año-1 (gross)  {m(proj['year1_gross'])}",
        f"  Ahorro Año-1 (net)    {m(proj['year1_net'])}",
        f"  VPN @ WACC (net)      {m(proj['npv_net'])}",
        f"  TIR (net)             {p(proj['irr_net'])}",
        f"  Payback (net)         {proj['payback_net']:.1f} años" if proj['payback_net'] else "  Payback (net)         n/a",
    ]
    if proj.get("fp_base"):
        lines.insert(4, f"  └─ incl. corrección FP {m(proj['year1_fp'])}/año (penalty eliminado)")
    if saas:
        lines += [
            f"SaaS / financier view (share {saas['saas_share']*100:.0f}% of net savings)",
            f"  VPN @ WACC            {m(saas['npv'])}",
            f"  TIR                   {p(saas['irr'])}",
            f"  Payback               {saas['payback']:.1f} años" if saas['payback'] else "  Payback               n/a",
        ]
    return "\n".join(lines)
