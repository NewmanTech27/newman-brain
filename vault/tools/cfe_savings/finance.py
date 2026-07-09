"""Financial model: project economics + optional savings-as-a-service split.

Scope boundary (deliberate): this computes a transparent, reusable financial view
(CAPEX, escalated/degraded net savings, O&M -> NPV/IRR/payback). The reference
Excel's "Flujo Newman" IRR (~19%) embeds a bespoke debt + PPA + savings-share
structure (ActiveLeasing tabs); that is parameterized here via `saas_share`, not
hardcoded. Supply real financing terms per deal to reproduce a specific financier
return.
"""
from __future__ import annotations


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def irr(cashflows: list[float], lo=-0.9, hi=2.0, tol=1e-7) -> float | None:
    """IRR via bisection. Returns None if no sign change in [lo, hi]."""
    f_lo, f_hi = npv(lo, cashflows), npv(hi, cashflows)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid, cashflows)
        if abs(f_mid) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def simple_payback(cashflows: list[float]) -> float | None:
    cum = 0.0
    for t, cf in enumerate(cashflows):
        prev = cum
        cum += cf
        if prev < 0 <= cum and t > 0:
            return t - 1 + (-prev) / cf  # fractional year
    return None


def project_financials(pv_base: float, bess_base: float, capex: float, fin: dict,
                       fp_base: float = 0.0) -> dict:
    """Unlevered project view.
    pv_base  = annual PV savings (gross, year 0 basis)
    bess_base= annual BESS savings (cap+arb, gross, before availability)
    fp_base  = annual FP-correction savings (year 0 basis); escalates with CFE, no
               device degradation; applied to both gross and net (hardware certainty).
    """
    H = int(fin.get("horizon_years", 20))
    cfe = fin.get("cfe_escalation", 0.05)
    pv_degr = fin.get("pv_degradation", 0.005)
    bess_degr = fin.get("bess_degradation", 0.0125)
    avail = fin.get("availability_factor", 0.75)
    om_pv = fin.get("om_pv_mxn_yr", 0.0)
    om_bess = fin.get("om_bess_mxn_yr", 0.0)
    om_term = int(fin.get("ppa_term_years", H))

    cf_gross = [-capex]
    cf_net = [-capex]
    rows = []
    for t in range(1, H + 1):
        pv_t = pv_base * (1 + cfe) ** t * (1 - pv_degr) ** t
        bess_gross_t = bess_base * (1 + cfe) ** t * (1 - bess_degr) ** t
        bess_net_t = bess_gross_t * avail
        fp_t = fp_base * (1 + cfe) ** t  # no degradation on FP correction
        om_t = (om_pv + om_bess) * (1 + cfe) ** (t - 1) if t <= om_term else 0.0
        gross = pv_t + bess_gross_t + fp_t - om_t
        net = pv_t + bess_net_t + fp_t - om_t
        cf_gross.append(gross)
        cf_net.append(net)
        rows.append({"year": t, "pv": pv_t, "bess_gross": bess_gross_t,
                     "bess_net": bess_net_t, "fp": fp_t, "om": om_t, "cf_net": net})

    wacc = fin.get("wacc", 0.12)
    return {
        "capex": capex,
        "fp_base": fp_base, "year1_fp": fp_base * (1 + cfe) if fp_base else 0.0,
        "year1_gross": cf_gross[1], "year1_net": cf_net[1],
        "npv_net": npv(wacc, cf_net),
        "irr_net": irr(cf_net),
        "payback_net": simple_payback(cf_net),
        "npv_gross": npv(wacc, cf_gross),
        "irr_gross": irr(cf_gross),
        "payback_gross": simple_payback(cf_gross),
        "rows": rows,
        "params": {"wacc": wacc, "cfe_esc": cfe, "availability": avail,
                   "horizon": H, "om_term": om_term},
    }


def saas_split(project: dict, saas_share: float, capex: float, fin: dict) -> dict:
    """Optional financier view: financier funds CAPEX, receives `saas_share` of
    net savings. IRR/NPV on the financier cashflow. Deal-specific — supply share."""
    wacc = fin.get("wacc", 0.12)
    cf = [-capex] + [r["cf_net"] * saas_share for r in project["rows"]]
    return {"saas_share": saas_share, "npv": npv(wacc, cf),
            "irr": irr(cf), "payback": simple_payback(cf)}
