# -*- coding: utf-8 -*-
"""Industry load-curve library + CFE horario overlay + fit vs bill kWh splits.

Purpose (wiki: [[perfiles-de-carga]]):
  1. Model a 7-day hourly consumption curve per industry (lun-vie / sabado / domingo+festivo).
  2. Overlay the CFE period windows ([[horarios-y-divisiones]]: division x temporada x dia)
     to get the MODELED energy split %B/%I/%P for any month.
  3. Compare modeled split vs the ACTUAL kWh B/I/P printed on each bill -> fit score,
     so the curve is chosen with evidence (fixes audit error I8: wrong profile class).
  4. Curve x solar bell overlap -> derived % autoconsumo instantaneo per month
     (replaces the flat per-giro default when PV >= 0.7 MW).

The curves are ASSUMPTIONS (documented shapes, not measured); 15-min interval data
supersedes them. Festivos count as domingo (CFE treats holidays as Sunday schedule).
"""
from __future__ import annotations
import calendar, math, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cfe_savings.defaults import festivos

# ---------------- 24h shapes per day type (relative load, peak ~1.0) ----------------
def _blk(*segs):
    """segs: (start, end, value) half-open hour ranges -> 24-vector."""
    v = [0.0] * 24
    for a, b, x in segs:
        for h in range(a, b):
            v[h] = x
    return v

CURVES = {
    "Hotel/Turismo": {   # evening peak (occupancy+HVAC), high night base; 7-day operation
        "MF": _blk((0, 6, .55), (6, 7, .60), (7, 11, .75), (11, 17, .80), (17, 18, .90), (18, 23, 1.0), (23, 24, .70)),
        "SA": _blk((0, 6, .58), (6, 7, .62), (7, 11, .78), (11, 17, .82), (17, 18, .92), (18, 23, 1.0), (23, 24, .72)),
        "DO": _blk((0, 6, .58), (6, 7, .62), (7, 11, .78), (11, 17, .80), (17, 18, .90), (18, 23, 1.0), (23, 24, .70)),
    },
    "Industrial 24/7": {  # 3 turnos: near-flat, mild day bump, lighter weekends
        "MF": _blk((0, 7, .90), (7, 19, 1.0), (19, 24, .95)),
        "SA": _blk((0, 7, .85), (7, 19, .95), (19, 24, .90)),
        "DO": _blk((0, 24, .85)),
    },
    "Industrial 1 turno": {  # 7:00-17:00 production; Saturday half day
        "MF": _blk((0, 6, .20), (6, 7, .60), (7, 17, 1.0), (17, 18, .50), (18, 24, .25)),
        "SA": _blk((0, 7, .20), (7, 14, .70), (14, 24, .20)),
        "DO": _blk((0, 24, .20)),
    },
    "Comercial/Retail": {  # 9:00-21:00 open, broad midday-evening peak, weekends strong
        "MF": _blk((0, 8, .30), (8, 9, .60), (9, 12, .85), (12, 19, 1.0), (19, 21, .90), (21, 23, .50), (23, 24, .30)),
        "SA": _blk((0, 8, .30), (8, 9, .65), (9, 12, .90), (12, 19, 1.0), (19, 21, .95), (21, 23, .50), (23, 24, .30)),
        "DO": _blk((0, 8, .30), (8, 9, .60), (9, 12, .85), (12, 19, .95), (19, 21, .85), (21, 23, .45), (23, 24, .30)),
    },
    "Oficinas": {  # 8:00-18:00, HVAC midday, weekends near-empty
        "MF": _blk((0, 7, .20), (7, 8, .50), (8, 10, .90), (10, 16, 1.0), (16, 18, .85), (18, 20, .40), (20, 24, .20)),
        "SA": _blk((0, 8, .20), (8, 14, .35), (14, 24, .20)),
        "DO": _blk((0, 24, .20)),
    },
    "Otro": {  # neutral flat
        "MF": _blk((0, 24, 1.0)), "SA": _blk((0, 24, 1.0)), "DO": _blk((0, 24, 1.0)),
    },
}

# ---------------- CFE period windows: division x temporada x day type ----------------
# Per [[horarios-y-divisiones]] (CFE tariff page as billing reference; 22:00-24:00 = I).
# Labels per hour: "B" base, "I" intermedio, "P" punta.
def _lab(base=(), inter=(), punta=()):
    v = ["I"] * 24
    for a, b in base:
        for h in range(a, b): v[h] = "B"
    for a, b in inter:
        for h in range(a, b): v[h] = "I"
    for a, b in punta:
        for h in range(a, b): v[h] = "P"
    return v

WINDOWS = {
    ("SIN", "verano"): {
        "MF": _lab(base=[(0, 6)], punta=[(20, 22)]),
        "SA": _lab(base=[(0, 7)]),
        "DO": _lab(base=[(0, 19)]),
    },
    ("SIN", "invierno"): {
        "MF": _lab(base=[(0, 6)], punta=[(18, 22)]),
        "SA": _lab(base=[(0, 8)], punta=[(19, 21)]),
        "DO": _lab(base=[(0, 18)]),
    },
    ("BC", "verano"): {   # no Base in BC summer
        "MF": _lab(punta=[(14, 18)]),
        "SA": _lab(),
        "DO": _lab(),
    },
    ("BC", "invierno"): {  # no punta in BC winter
        "MF": _lab(base=[(0, 17), (22, 24)]),
        "SA": _lab(base=[(0, 18), (21, 24)]),
        "DO": _lab(base=[(0, 24)]),
    },
    ("BCS", "verano"): {  # no Base in BCS summer
        "MF": _lab(punta=[(12, 22)]),
        "SA": _lab(punta=[(19, 22)]),
        "DO": _lab(),
    },
    ("BCS", "invierno"): {  # no punta in BCS winter
        "MF": _lab(base=[(0, 18), (22, 24)]),
        "SA": _lab(base=[(0, 18), (21, 24)]),
        "DO": _lab(base=[(0, 19), (21, 24)]),
    },
}


def season(division: str, month: int) -> str:
    """Whole-month approximation. SIN/BCS: verano abr-oct. BC: verano may-oct (wiki;
    nota: cfe_savings/defaults.py usa abr-oct para BC — divergencia flaggeada)."""
    d = (division or "SIN").upper()
    if d == "BC":
        return "verano" if 5 <= month <= 10 else "invierno"
    return "verano" if 4 <= month <= 10 else "invierno"


def day_counts(year: int, month: int) -> dict:
    """{'MF': n, 'SA': n, 'DO': n} — festivos cuentan como DO (horario domingo)."""
    f = festivos(year)
    out = {"MF": 0, "SA": 0, "DO": 0}
    for d in range(1, calendar.monthrange(year, month)[1] + 1):
        dt = date(year, month, d)
        if dt in f:
            out["DO"] += 1
        elif dt.weekday() < 5:
            out["MF"] += 1
        elif dt.weekday() == 5:
            out["SA"] += 1
        else:
            out["DO"] += 1
    return out


def model_split(giro: str, division: str, year: int, month: int) -> dict:
    """Modeled energy fractions {'B','I','P'} for the month."""
    curve = CURVES[giro]
    win = WINDOWS[((division or "SIN").upper() if (division or "SIN").upper() in ("BC", "BCS") else "SIN",
                   season(division, month))]
    cnt = day_counts(year, month)
    tot = {"B": 0.0, "I": 0.0, "P": 0.0}
    for dt in ("MF", "SA", "DO"):
        for h in range(24):
            tot[win[dt][h]] += curve[dt][h] * cnt[dt]
    s = sum(tot.values())
    return {k: v / s for k, v in tot.items()} if s else tot


def fit_bills(bills: list[dict], division: str) -> dict:
    """Rank giros by mean absolute error between modeled and actual period shares.
    Returns {'ranking':[{giro, mae, by_month:[...]}...], 'best': giro}."""
    out = []
    for giro in CURVES:
        errs, rows = [], []
        for b in bills:
            kb, ki, kp = b.get("kwh_base") or 0, b.get("kwh_inter") or 0, b.get("kwh_punta") or 0
            tot = kb + ki + kp
            if not tot:
                continue
            act = {"B": kb / tot, "I": ki / tot, "P": kp / tot}
            mod = model_split(giro, division, b["year"], b["month"])
            e = sum(abs(mod[k] - act[k]) for k in "BIP") / 3
            errs.append(e)
            rows.append(dict(year=b["year"], month=b["month"],
                             actual=act, modeled=mod, mae=e))
        out.append(dict(giro=giro, mae=(sum(errs) / len(errs)) if errs else None, by_month=rows))
    out.sort(key=lambda r: (r["mae"] is None, r["mae"]))
    return dict(ranking=out, best=out[0]["giro"] if out and out[0]["mae"] is not None else None)


# ---------------- solar overlap -> % autoconsumo instantaneo ----------------
PV_BELL = [max(0.0, math.sin(math.pi * (h - 7) / 12)) for h in range(24)]  # 7:00-19:00
_PV_SUM = sum(PV_BELL)


def autoconsumo_pct(giro: str, year: int, month: int,
                    kwh_month: float, gen_month: float) -> float:
    """Fraction of the month's PV generation consumed instantaneously, from the
    hourly overlap of the scaled load curve vs the scaled solar bell (same bell
    all 7 days). Size-dependent: more PV -> lower %. Returns 1.0 if gen=0."""
    if gen_month <= 0 or kwh_month <= 0:
        return 1.0
    curve = CURVES[giro]
    cnt = day_counts(year, month)
    days = sum(cnt.values())
    load_units = sum(curve[dt][h] * cnt[dt] for dt in cnt for h in range(24))
    ls = kwh_month / load_units          # kWh per curve-unit-hour
    gs = gen_month / (days * _PV_SUM)    # kWh per bell-unit-hour
    selfc = sum(min(curve[dt][h] * ls, PV_BELL[h] * gs) * cnt[dt]
                for dt in cnt for h in range(24))
    return min(1.0, selfc / gen_month)


def curve_payload(division: str) -> dict:
    """Chart data for the webapp: curves + period labels per day type, both seasons."""
    key = (division or "SIN").upper()
    key = key if key in ("BC", "BCS") else "SIN"
    return dict(curves=CURVES,
                windows={s: WINDOWS[(key, s)] for s in ("verano", "invierno")},
                pv_bell=PV_BELL)


def punta_days(division, year, month):
    """Days in the month whose day-type actually carries a punta hour for this
    division+season (SIN winter Saturdays 19-21, BCS/BC summer Saturdays) — not
    just Mon-Fri. Reads the same WINDOWS (A/158/2024) the engine is calibrated
    on; cross-checked vs cfe.tarifa_horario. Replaces the legacy weekday-only
    count, which understated punta days where weekend punta applies."""
    dkey = (division or "SIN").upper()
    dkey = dkey if dkey in ("BC", "BCS") else "SIN"
    win = WINDOWS[(dkey, season(division, month))]
    cnt = day_counts(year, month)
    return sum(cnt[td] for td in ("MF", "SA", "DO") if "P" in win[td])
