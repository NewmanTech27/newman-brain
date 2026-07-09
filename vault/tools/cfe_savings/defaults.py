"""Default assumptions and regulatory constants for the CFE PV+BESS savings engine.

All tariff/billing logic mirrors the CFE Brain wiki (the single source of truth):
  - FC=0.57 umbral, capacidad on kW_punta, distribucion on max(B,I,P)  -> demanda-facturable
  - GDMTH bill structure                                               -> gdmth-bill-structure
  - SIN/BC/BCS period schedules                                        -> horarios-y-divisiones
  - BESS seasonal shave (usable/punta_hours)                           -> bess-savings-model
  - DG ceiling < 0.7 MW (art.25 Ley del Sector Electrico 2025)         -> generacion-distribuida

Financial defaults are seeded from the reference Excel (raw/data/780881200029.xlsx).
Override any of them per-RPU via inputs.json.
"""

# --- Regulatory constants ---
FC_GDMTH = 0.57          # factor de carga, GDMTH (A/158/2024)
IVA = 0.16
DG_CEILING_KW = 700.0    # Generacion Distribuida ceiling, art.25 Ley 2025 (< 0.7 MW)

# Spanish 3-letter month tokens on CFE bills -> month number
MONTH_TOKENS = {
    "ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12,
}

# --- Period schedules (hour -> period) by division and season ---
# Confirmed for SIN from horarios-y-divisiones + the reference Excel SIN matrix.
# BC/BCS encoded from overview.md and flagged for validation when a real BC/BCS
# bill is ingested.
#
# punta_hours_by_division[division](month) -> number of punta hours/day
def _sin_punta_hours(month: int) -> int:
    # Summer Apr-Oct: punta 20:00-22:00 (2h). Winter Nov-Mar: punta 18:00-22:00 (4h).
    return 2 if 4 <= month <= 10 else 4


def _bcs_punta_hours(month: int) -> int:
    # BCS summer (Apr-Oct): punta 12:00-22:00 (10h); winter: no punta (treat as 0 -> umbral only)
    return 10 if 4 <= month <= 10 else 0


def _bc_punta_hours(month: int) -> int:
    # BC summer starts May 1 (NOT first Sunday of April like SIN/BCS):
    # May-Oct punta 14:00-18:00 (4h); winter: no punta.
    # Reconciled 2026-06-11 vs wiki horarios-y-divisiones (A/158/2024 Table 4).
    return 4 if 5 <= month <= 10 else 0


PUNTA_HOURS = {
    "SIN": _sin_punta_hours,
    "BCS": _bcs_punta_hours,
    "BC": _bc_punta_hours,
}


def punta_hours(division: str, month: int) -> int:
    fn = PUNTA_HOURS.get((division or "SIN").upper(), _sin_punta_hours)
    return fn(month)


# --- Punta-day calendar (added 2026-06-11, calculadora audit) ---
# Punta windows exist Mon-Fri only; sabado/domingo/festivos run the domingo
# schedule (horarios-y-divisiones). Festivos = the statutory list.
import calendar as _calendar
from datetime import date as _date


def _nth_monday(year: int, month: int, n: int) -> "_date":
    d = _date(year, month, 1)
    off = (7 - d.weekday()) % 7
    return _date(year, month, 1 + off + 7 * (n - 1))


def festivos(year: int) -> set:
    """Statutory holidays treated as domingo by the tariff schedule."""
    return {_date(year, 1, 1), _nth_monday(year, 2, 1), _nth_monday(year, 3, 3),
            _date(year, 5, 1), _date(year, 9, 16), _nth_monday(year, 11, 3),
            _date(year, 12, 25)}


def punta_weekdays(year: int, month: int) -> int:
    """Days of the calendar month that have a punta window (Mon-Fri minus festivos)."""
    f = festivos(year)
    return sum(1 for d in range(1, _calendar.monthrange(year, month)[1] + 1)
               if _date(year, month, d).weekday() < 5 and _date(year, month, d) not in f)


# --- System / dispatch defaults (Excel-seeded) ---
SYSTEM_DEFAULTS = {
    "division": "SIN",
    "dod": 0.96,            # depth of discharge
    "rte": 0.96,            # round-trip efficiency
    "pv_degradation": 0.005,    # %/yr
    "bess_degradation": 0.0125, # %/yr
    "availability_factor": 0.75,  # "Factor BESS falla" — ~3 months/yr downtime (SaaS)
    "compensation": "medicion_neta",
    "pv_packing_kwp_per_m2": 0.17,  # usable kWp per m2 of roof/ground (C&I fixed-tilt)
    "bess_autonomy_hours": None,    # if set, size BESS energy = peak_shave_target * hours
}

# --- Financial defaults (Excel-seeded) ---
FINANCE_DEFAULTS = {
    "epc_pv_usd_per_wp": 0.75,
    "fx_mxn_per_usd": 17.55,
    "bess_cost_mxn_per_kwh": None,  # if None, derive BoP from CAPEX override
    "wacc": 0.12,
    "horizon_years": 20,
    "cfe_escalation": 0.05,
    "ppa_escalation": 0.05,
    "ppa_rate_mxn_per_kwh": 1.50,
    "ppa_term_years": 15,
    "om_pv_mxn_yr": 60288.8,
    "om_bess_mxn_yr": 529200.0,
    "capex_total_mxn": None,  # if provided, used directly (overrides component build-up)
}
