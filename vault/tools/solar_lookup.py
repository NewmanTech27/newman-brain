# -*- coding: utf-8 -*-
"""CP -> municipio/estado -> monthly solar yield (kWh/kWp).
Chain per [[solar-yield-lookup]]: codigo_postal.csv + Solar_index_geografico.csv.
Prefeasibility grade — Helioscope monthlies override this when available.
"""
from __future__ import annotations
import csv, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CP_CSV = ROOT / "raw" / "assets" / "codigo_postal.csv"
SOLAR_CSV = ROOT / "raw" / "assets" / "Solar_index_geografico.csv"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def cp_to_municipio(cp: str) -> tuple[str, str] | None:
    cp = str(cp or "").strip().lstrip("0")
    if not cp:
        return None
    with open(CP_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["d_codigo"].lstrip("0") == cp:
                return row["D_mnpio"], row["d_estado"]
    return None


def municipio_yield(municipio: str, estado: str) -> dict | None:
    """-> {'anual': float, 'monthly': {1..12: kWh/kWp}, 'match': str} or None."""
    mn, es = _norm(municipio), _norm(estado)
    best, state_rows = None, []
    with open(SOLAR_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if _norm(row["estado"]) != es:
                continue
            state_rows.append(row)
            if _norm(row["ciudad"]) == mn:
                best = (row, f"{row['ciudad']}, {row['estado']}")
                break
    if best is None and state_rows:  # fallback: state average
        import statistics
        cols = [f"kWh/kWp_{m}" for m in ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                          "Jul", "Ago", "Sep", "Oct", "Nov", "Dec")]
        avg = {c: statistics.mean(float(r[c]) for r in state_rows) for c in cols}
        avg["kWh/kWp_anual"] = statistics.mean(float(r["kWh/kWp_anual"]) for r in state_rows)
        best = (avg, f"promedio estatal {estado} ({len(state_rows)} municipios)")
    if best is None:
        return None
    row, match = best
    keys = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dec"]
    monthly = {i + 1: float(row[f"kWh/kWp_{k}"]) for i, k in enumerate(keys)}
    return dict(anual=float(row["kWh/kWp_anual"]), monthly=monthly, match=match)


def cp_to_yield(cp: str) -> dict | None:
    loc = cp_to_municipio(cp)
    if not loc:
        return None
    y = municipio_yield(*loc)
    if y:
        y["municipio"], y["estado"] = loc
        y["division"] = ("BCS" if _norm(loc[1]) == "baja california sur"
                         else "BC" if _norm(loc[1]) == "baja california" else "SIN")
    return y
