"""Tariff + PV/BESS savings math. Deterministic; mirrors the CFE Brain wiki.

Reproduces the CORRECTED reference (Calculadora v2 / the 2026-06-11 audit,
wiki/analyses/2026-06-11-780881200029-calculadora-audit.md):
  baseline (sin IVA, no FP bonus) = sum of MEM importes        (gdmth-bill-structure)
  capacidad on kW_punta, distribucion on max(B,I,P), umbral cap (demanda-facturable)
  BESS shave = nominal*DoD*sqrt(RTE) / punta_hours(season)     (bess-savings-model)
  arbitrage = disch*bundled_punta - charge*bundled_base, with disch limited to
    punta weekdays (Mon-Fri minus festivos) and capped at the bill's punta kWh —
    a load-center BESS cannot displace punta energy that doesn't exist (sae-cc)
  FP bonificacion claw-back: the FP>=90% credit (~% of the bill) shrinks in
    proportion as savings shrink the bill
  PV savings = gen * bundled_inter (SIN: all PV lands in inter)(pv-savings-model)

History: v1 of this engine reproduced the client's reference Excel to the peso,
including its arbitrage flaw (365 cycles/yr, uncapped). Corrected + golden
re-baselined 2026-06-11.
"""
from __future__ import annotations
import math

from .defaults import FC_GDMTH, punta_hours, punta_weekdays


def _safe_div(a, b):
    return a / b if b else 0.0


def derive_rates(bill: dict) -> dict:
    """Per-bill unit rates derived from importes (region-agnostic)."""
    kwh_t = bill["kwh_total"]
    flat = (_safe_div(bill["transmision"], kwh_t)
            + _safe_div(bill["cenace"], kwh_t)
            + _safe_div(bill["scnmem"], kwh_t))
    gen_b = _safe_div(bill["gen_base"], bill["kwh_base"])
    gen_i = _safe_div(bill["gen_inter"], bill["kwh_inter"])
    gen_p = _safe_div(bill["gen_punta"], bill["kwh_punta"])
    umbral = _safe_div(kwh_t, bill["days"] * FC_GDMTH * 24)
    cap_billed = min(bill["kw_punta"], umbral)
    dist_billed = min(max(bill["kw_base"], bill["kw_inter"], bill["kw_punta"]), umbral)
    return {
        "flat": flat,
        "bundled_base": gen_b + flat,
        "bundled_inter": gen_i + flat,
        "bundled_punta": gen_p + flat,
        "r_cap": _safe_div(bill["capacidad"], cap_billed),
        "r_dist": _safe_div(bill["distribucion"], dist_billed),
        "umbral": umbral,
        "cap_billed": cap_billed,
        "dist_billed": dist_billed,
    }


def baseline_month(bill: dict) -> float:
    """Bill ANTES (sin IVA, no FP bonus) = sum of MEM importes — matches Excel."""
    return sum(bill[k] for k in
               ("suministro", "distribucion", "transmision", "cenace",
                "gen_base", "gen_inter", "gen_punta", "capacidad", "scnmem"))


def receipt_check(bill: dict):
    """Internal arithmetic check that catches CFE errors.
    (sum MEM importes + bonif_fp) * 1.16  ?=  facturacion_recibo."""
    calc = (baseline_month(bill) + bill.get("bonif_fp", 0.0)) * 1.16
    rec = bill.get("facturacion_recibo")
    if not rec:
        return None
    return {"calc_con_iva": calc, "facturacion_recibo": rec,
            "delta": calc - rec, "delta_pct": _safe_div(calc - rec, rec)}


def savings_month(bill: dict, sys: dict, pv_gen_kwh: float,
                  scenario: str = "combined") -> dict:
    """Monthly savings for one scenario: 'pv', 'bess', or 'combined'."""
    r = derive_rates(bill)
    days, month = bill["days"], bill["month"]
    div = sys.get("division", "SIN")

    use_pv = scenario in ("pv", "combined")
    use_bess = scenario in ("bess", "combined")
    pv = pv_gen_kwh if use_pv else 0.0

    # BESS daily dischargeable energy and seasonal power shave
    dischargeable_day = (sys["bess_nominal_kwh"] * sys["dod"] * math.sqrt(sys["rte"])) if use_bess else 0.0
    ph = punta_hours(div, month)
    shave = _safe_div(dischargeable_day, ph) if (use_bess and ph) else 0.0
    shave = min(shave, sys.get("bess_power_kw", shave))  # power limit
    # Discharge only on days with a punta window, capped at the bill's punta kWh:
    # the battery cannot displace punta energy that doesn't exist (no injection,
    # sae-cc). Corrected 2026-06-11 (audit); was dischargeable_day * calendar days.
    wd = punta_weekdays(bill["year"], month) if use_bess else 0
    disch_month = min(dischargeable_day * wd, bill["kwh_punta"]) if use_bess else 0.0
    charge_month = _safe_div(disch_month, sys["rte"])

    kw_punta = bill["kw_punta"]
    residual_punta = max(0.0, kw_punta - shave)

    umbral_pre = r["umbral"]
    cap_pre = min(kw_punta, umbral_pre)
    kwh_red_post = bill["kwh_total"] - pv - disch_month + charge_month
    umbral_post = _safe_div(kwh_red_post, days * FC_GDMTH * 24)
    cap_post = min(residual_punta, umbral_post)

    ahorro_capacidad = (cap_pre - cap_post) * r["r_cap"]
    ahorro_arbitraje = (disch_month * r["bundled_punta"] - charge_month * r["bundled_base"]) if use_bess else 0.0
    ahorro_pv = pv * r["bundled_inter"]

    # FP correction (opt-in): eliminating the cargo por bajo factor de potencia by
    # raising FP to >=90% (BESS/hybrid inverter reactive support or a capacitor bank).
    # Orthogonal to PV/BESS sizing — present in every scenario when enabled. It is a
    # hardware certainty, so no availability haircut. fp_correction_factor (default 1.0)
    # = fraction of the measured penalty eliminated. See factor-de-potencia logic.
    fp_on = sys.get("fp_correction_enabled", False)
    fp_factor = sys.get("fp_correction_factor", 1.0)
    ahorro_fp_correction = bill.get("cargo_fp_penalty", 0.0) * fp_factor if fp_on else 0.0

    # availability haircut applies to BESS value (gross headline keeps it = 1.0)
    avail = sys.get("availability_factor", 1.0)
    bess_value = (ahorro_capacidad + ahorro_arbitraje)

    baseline = baseline_month(bill)
    # FP bonificacion claw-back (added 2026-06-11, audit): when the site earns the
    # FP>=90% bonificacion (bonif_fp < 0, ~1-2.5% of the bill), the credit shrinks
    # in proportion as savings shrink the bill — part of every savings peso is
    # clawed back. Penalty sites (bonif_fp > 0) are handled by --fp-correction.
    bonif = bill.get("bonif_fp", 0.0)
    bonif_share = _safe_div(-bonif, baseline) if bonif < 0 else 0.0
    claw_gross = -(bess_value + ahorro_pv) * bonif_share
    claw_net = -(bess_value * avail + ahorro_pv) * bonif_share
    total_gross = bess_value + ahorro_pv + claw_gross + ahorro_fp_correction
    total_net = bess_value * avail + ahorro_pv + claw_net + ahorro_fp_correction

    return {
        "month": month, "year": bill["year"], "days": days,
        "kwh_consumo": bill["kwh_total"],
        "pv_gen_kwh": pv,
        "bess_disch_kwh": disch_month if use_bess else 0.0,
        "bess_charge_kwh": charge_month if use_bess else 0.0,
        "pico_punta_pre": kw_punta,
        "pico_punta_post": residual_punta if use_bess else kw_punta,
        "ahorro_capacidad": ahorro_capacidad,
        "ahorro_arbitraje": ahorro_arbitraje,
        "ahorro_pv": ahorro_pv,
        "ahorro_bonif_clawback": claw_gross,
        "ahorro_fp_correction": ahorro_fp_correction,
        "bill_antes": baseline,
        "ahorro_total_gross": total_gross,
        "ahorro_total_net": total_net,
        "bill_despues_gross": baseline - total_gross,
        "bill_despues_net": baseline - total_net,
    }


def run_scenarios(bills: list[dict], sys: dict, pv_monthly: dict) -> dict:
    """Compute pv-only, bess-only, combined for the full year.
    pv_monthly: {month:int -> kwh} (PV generation per calendar month)."""
    out = {}
    for scen in ("pv", "bess", "combined"):
        rows = [savings_month(b, sys, pv_monthly.get(b["month"], 0.0), scen) for b in bills]
        tot = _aggregate(rows)
        out[scen] = {"months": rows, "total": tot}
    return out


def _aggregate(rows: list[dict]) -> dict:
    keys = ["kwh_consumo", "pv_gen_kwh", "bess_disch_kwh",
            "ahorro_capacidad", "ahorro_arbitraje", "ahorro_pv",
            "ahorro_bonif_clawback", "ahorro_fp_correction",
            "bill_antes", "ahorro_total_gross", "ahorro_total_net",
            "bill_despues_gross", "bill_despues_net"]
    t = {k: sum(r[k] for r in rows) for k in keys}
    t["ahorro_pct_gross"] = _safe_div(t["ahorro_total_gross"], t["bill_antes"])
    t["ahorro_pct_net"] = _safe_div(t["ahorro_total_net"], t["bill_antes"])
    return t
