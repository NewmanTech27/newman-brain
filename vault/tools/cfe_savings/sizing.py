"""Auto-propose PV and BESS sizing from the bills + site constraints.
The analyst presents these to the user for confirmation/override before the run.
"""
from __future__ import annotations
from statistics import mean

from .defaults import DG_CEILING_KW, punta_hours


def propose_pv_kwp(bills: list[dict], area_m2: float | None, packing: float,
                   pct_load: float | None = None, allow_autoconsumo: bool = True) -> dict:
    """Prefeasibility PV cap. NOTE: the 0.7 MW DG ceiling is a REGULATORY STEP, not a
    sizing cap — by default it is reported but NOT binding (`allow_autoconsumo=True`),
    so callers don't silently truncate at 699 kW. For the savings-maximizing size use
    `optimize_sizing.propose` (sweeps client NPV; CLAUDE.md 2026-06-19). Set
    `allow_autoconsumo=False` only when the project must stay generador-exento."""
    caps = {}
    if not allow_autoconsumo:
        caps["dg_ceiling_kw"] = DG_CEILING_KW
    if area_m2:
        caps["area_kwp"] = area_m2 * packing
    if pct_load:
        annual_kwh = sum(b["kwh_total"] for b in bills)
        # rough: kWp to supply pct_load of annual energy at ~1800 kWh/kWp/yr
        caps["pct_load_kwp"] = (annual_kwh * pct_load) / 1800.0
    if not caps:  # nothing binds → report the DG line as a reference, unbinding
        caps["dg_ceiling_kw"] = DG_CEILING_KW
    proposed = min(caps.values())
    return {"proposed_kwp": round(proposed, 1), "caps": caps,
            "binding": min(caps, key=caps.get),
            "note": "0.7 MW is regulatory, not a cap — use optimize_sizing for max-NPV size"}


def propose_bess(bills: list[dict], division: str, autonomy_hours: float | None) -> dict:
    """Size to shave the average punta peak across the binding (longest) window."""
    avg_punta_peak = mean(b["kw_punta"] for b in bills)
    max_punta_hours = max(punta_hours(division, b["month"]) for b in bills) or 2
    hours = autonomy_hours or max_punta_hours
    power_kw = round(avg_punta_peak, 0)
    energy_kwh = round(avg_punta_peak * hours, 0)
    return {"proposed_power_kw": power_kw, "proposed_nominal_kwh": energy_kwh,
            "basis": f"avg punta peak {avg_punta_peak:.0f} kW x {hours:.0f} h "
                     f"({'autonomy override' if autonomy_hours else 'longest punta window'})",
            "note": "Energy-limited shave = nominal*DoD*sqrt(RTE)/punta_hours; "
                    "longer punta windows (winter) reduce achievable shave."}
