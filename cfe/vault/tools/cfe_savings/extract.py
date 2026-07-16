"""Parse CFE GDMTH bills into structured monthly data.

Two formats supported:
  - PDF (pdfplumber): CFE prints the MEM cost table (left) and the payment
    desglose (right) on the same text line, so MEM importes are read as the 4th
    number on each concept line (cols: $ | $/kW | $/kWh | Importe).
  - CFDI XML (CFE / iTComplements complemento): the bill data lives in a flat
    `clsRegArchFact` block inside the SAT CFDI Addenda. MEM importes are read by
    concept code (ES1/ED1/ETB/ECB/EGB/EGI/EGP/EID/EMB), kWh by period from
    CONSUMO1F/2F/3F, demands from DEMANDA1P/2P/3P. Added 2026-06-09 for RPU
    456220800389 (Jalisco/SIN, tarifa HM=GDMTH) — see analysis page.

Output: list of per-month dicts, sorted by billing date. Raw bytes never leave
this module — callers receive only parsed numbers (token-efficient).
"""
from __future__ import annotations
import re
import glob
import os
from datetime import date
import xml.etree.ElementTree as ET

from .defaults import MONTH_TOKENS

_NUM = re.compile(r"-?\d[\d,]*\.\d\d|-?\d[\d,]*")


def _nums(s: str):
    return [float(x.replace(",", "")) for x in _NUM.findall(s)]


def _first_line(lines, prefix):
    for ln in lines:
        if ln.strip().startswith(prefix):
            return ln
    return None


def _consumo(lines, label):
    ln = _first_line(lines, label)
    return _nums(ln)[-1] if ln else None


def _mem(lines, label):
    """MEM importe = 4th number on the concept line (left table)."""
    ln = _first_line(lines, label)
    if not ln:
        return None
    n = _nums(ln)
    return n[3] if len(n) > 3 else (n[-1] if n else None)


def _desglose(lines, *substrings):
    for ln in lines:
        if any(s in ln for s in substrings):
            n = _nums(ln)
            if n:
                return n[-1]
    return None


def _parse_period(text):
    """'PERIODO FACTURADO:31 MAR 25-30 ABR 25' -> (start, end, days, month, year)."""
    m = re.search(r"PERIODO FACTURADO:\s*(\d{1,2})\s+([A-Z]{3})\s+(\d{2})\s*-\s*(\d{1,2})\s+([A-Z]{3})\s+(\d{2})", text)
    if not m:
        return None
    d1, mo1, y1, d2, mo2, y2 = m.groups()
    start = date(2000 + int(y1), MONTH_TOKENS[mo1], int(d1))
    end = date(2000 + int(y2), MONTH_TOKENS[mo2], int(d2))
    days = (end - start).days
    return start, end, days, end.month, end.year


def parse_bill(path: str) -> dict:
    import pdfplumber  # lazy: only the PDF path needs it; XML path is stdlib-only
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text()
    lines = text.split("\n")
    per = _parse_period(text)
    if not per:
        raise ValueError(f"Could not parse PERIODO FACTURADO in {path}")
    start, end, days, month, year = per

    bonif = _desglose(lines, "Bonificacion Factor de Potencia", "Bonificación Factor")
    # bonificacion is a credit (negative) when FP>=90%; sign comes from the '-' in text
    bonif_line = next((ln for ln in lines if "onificacion Factor" in ln or "onificación Factor" in ln), "")
    if bonif is not None and "-" in bonif_line.split("Factor")[-1]:
        bonif = -abs(bonif)

    d = {
        "file": os.path.basename(path),
        "start": start.isoformat(), "end": end.isoformat(),
        "days": days, "month": month, "year": year,
        "servicio": (re.search(r"NO\. DE SERVICIO:\s*(\d+)", text) or [None, None])[1]
            if re.search(r"NO\. DE SERVICIO:\s*(\d+)", text) else None,
        "multiplicador": (lambda m: float(m.group(1).replace(",", "")) if m else None)(
            re.search(r"MULTIPLICADOR:\s*([\d,]+)", text)),
        "demanda_contratada": (lambda m: float(m.group(1).replace(",", "")) if m else None)(
            re.search(r"DEMANDA CONTRATADA kW:\s*([\d,]+)", text)),
        # consumo block
        "kwh_base": _consumo(lines, "kWh base"),
        "kwh_inter": _consumo(lines, "kWh intermedia"),
        "kwh_punta": _consumo(lines, "kWh punta"),
        "kw_base": _consumo(lines, "kW base"),
        "kw_inter": _consumo(lines, "kW intermedia"),
        "kw_punta": _consumo(lines, "kW punta"),
        "kw_max": _consumo(lines, "KWMax"),
        "kvarh": _consumo(lines, "kVArh"),
        "fp": _consumo(lines, "Factor de potencia"),
        # MEM importes (left table, 4th number)
        "suministro": _mem(lines, "Suministro"),
        "distribucion": _mem(lines, "Distribución"),
        "transmision": _mem(lines, "Transmisión"),
        "cenace": _mem(lines, "CENACE"),
        "gen_base": _mem(lines, "Generación B"),
        "gen_inter": _mem(lines, "Generación I"),
        "gen_punta": _mem(lines, "Generación P"),
        "capacidad": _mem(lines, "Capacidad"),
        "scnmem": _mem(lines, "SCnMEM"),
        # desglose (right column)
        "bonif_fp": bonif or 0.0,
        # FP penalty (cargo por bajo factor de potencia, FP<90%) as a positive amount.
        # PDFs here (780881200029) all have FP>=90% -> credit -> penalty 0. A penalty
        # prints on its own desglose line; capture it best-effort, else 0.
        "cargo_fp_penalty": max(0.0, _desglose(lines, "Cargo Factor de Potencia",
                                               "Cargo por bajo Factor", "Cargo por Factor de Potencia") or 0.0),
        "energia_desglose": _desglose(lines, "Energia "),
        "subtotal_recibo": _desglose(lines, "Subtotal"),
        "facturacion_recibo": _desglose(lines, "Facturacion del Periodo", "Fac. del Periodo"),
    }
    d["kwh_total"] = sum(x for x in (d["kwh_base"], d["kwh_inter"], d["kwh_punta"]) if x)
    return d


# --- CFDI XML loader (CFE / iTComplements complemento) ---

def _xml_text_map(path: str) -> dict:
    """Flatten every element under the CFDI tree to {localname: text}.
    The CFE complemento (clsRegArchFact) has unique leaf names, so a flat map is
    sufficient. Raw bytes stay inside this function."""
    root = ET.parse(path).getroot()
    out = {}
    for e in root.iter():
        local = e.tag.split("}")[-1]
        txt = (e.text or "").strip()
        if txt and local not in out:  # first non-empty wins (avoids dup leaf names)
            out[local] = txt
    return out


def _f(v):
    """Parse a possibly-zero-padded numeric string -> float (None if blank/NaN)."""
    if v is None:
        return None
    v = v.replace(",", "").strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _parse_period_xml(desde: str, hasta: str):
    """'30 ABR 25' / '31 MAY 25' -> (start, end, days, month, year)."""
    def one(s):
        m = re.match(r"\s*(\d{1,2})\s+([A-Z]{3})\s+(\d{2})", (s or "").upper())
        if not m:
            return None
        d, mo, y = m.groups()
        return date(2000 + int(y), MONTH_TOKENS[mo], int(d))
    start, end = one(desde), one(hasta)
    if not start or not end:
        return None
    return start, end, (end - start).days, end.month, end.year


# CFDI CONSUMO<n>F -> billing period, keyed by CFE DIVISION code.
#
# The CFE horaria addenda numbers the three registers 1F/2F/3F. The mapping to
# base/intermedia/punta is a per-division-code fact, NOT the fixed 1F=base order
# the pre-2026-07 code assumed ("verified by EG* importes" — a method proven
# WRONG for DW, and never independently confirmed for any other division).
#
# Byte-verified CFE convention (harvest PR #17, cfe-collector enrich.py): the
# addenda orders the registers **1F=Punta, 2F=Intermedia, 3F=Base**, confirmed
# by two independent reconciliations to CONSUMO_R (the total):
#   - BG-000027808909.xml: 1F=6132(punta) + 2F=64288(inter) + 3F=26894(base)
#                          = 97314 = CONSUMO_R  (punta smallest = fewest peak hrs)
#   - RPU 780881200029 / DW (SIN Peninsular), NOV25, WH-000552276133.xml:
#                          1F=104467(punta) 2F=440446(inter) 3F=268822(base),
#                          PDF-validated peso-exact (4/4 canonical XMLs). #18.
#
# So the register order is a fixed CFE convention, and the OLD extract.py order
# was inverted for base<->punta on every division. The table below is keyed by
# division so a genuine per-division exception (if CFE ever ships one) is a
# one-line addition, not a silent re-inversion. Order = (1F, 2F, 3F) fields.
_STD_CONSUMO_ORDER = ("kwh_punta", "kwh_inter", "kwh_base")  # CFE addenda default

# Divisions whose (1F,2F,3F)->period order is BYTE-VERIFIED against ground truth.
# Everything not listed here falls back to _STD_CONSUMO_ORDER (the CFE convention
# above) and is flagged unverified via _consumo_order_verified().
_CONSUMO_ORDER_BY_DIVISION = {
    "DW": _STD_CONSUMO_ORDER,  # SIN Peninsular — #18, PDF + byte verified (4/4)
    "DB": _STD_CONSUMO_ORDER,  # BG-000027808909.xml reconciles to CONSUMO_R (PR #17)
}
# NOTE: DX (Jalisco, RPU 456220800389) is NOT listed — the only prior "check" used
# the discredited EG*-importe method. It falls back to the CFE-standard order,
# which is the safest default, but is flagged as unverified until a PDF-validated
# split confirms it. See #18.


def _consumo_order(division: str | None) -> tuple[str, str, str]:
    d = (division or "").strip().upper()
    return _CONSUMO_ORDER_BY_DIVISION.get(d, _STD_CONSUMO_ORDER)


def consumo_order_verified(division: str | None) -> bool:
    """True iff the CONSUMO->period order for this division is byte-verified
    against PDF/CONSUMO_R ground truth (not merely the CFE-convention default)."""
    return (division or "").strip().upper() in _CONSUMO_ORDER_BY_DIVISION


# CFE MEM concept codes (IMPTE_TOT_REG_n / MOTIVO_REG_n) -> engine field.
# Verified against bill arithmetic for RPU 456220800389 (tarifa HM/GDMTH).
_MEM_CODE_MAP = {
    "ES1": "suministro",     # Operación Suministrador Básico (cargo fijo)
    "ED1": "distribucion",   # Cargo por Distribución ($/kW)
    "ETB": "transmision",    # Transmisión (flat $/kWh)
    "ECB": "cenace",         # Operación CENACE (flat $/kWh)
    "EGB": "gen_base",       # Generación base
    "EGI": "gen_inter",      # Generación intermedia
    "EGP": "gen_punta",      # Generación punta
    "EID": "capacidad",      # Cargo por Capacidad ($/kW)
    "EMB": "scnmem",         # SCnMEM (flat $/kWh)
}


def parse_bill_xml(path: str) -> dict:
    v = _xml_text_map(path)
    per = _parse_period_xml(v.get("FECDESDE"), v.get("FECHASTA"))
    if not per:
        raise ValueError(f"Could not parse FECDESDE/FECHASTA in {path}")
    start, end, days, month, year = per

    # MEM importes by concept code
    mem = {field: 0.0 for field in _MEM_CODE_MAP.values()}
    for i in range(1, 11):
        code = (v.get(f"MOTIVO_REG_{i}") or "").strip()
        field = _MEM_CODE_MAP.get(code)
        if field:
            mem[field] = _f(v.get(f"IMPTE_TOT_REG_{i}")) or 0.0

    # kWh by period: the CONSUMO1F/2F/3F -> base/inter/punta order is a per-
    # division CFE-addenda fact, mapped via _consumo_order (see #18). The old
    # fixed 1F=base order was inverted (base<->punta) for DW and unverified
    # elsewhere. Default is the byte-verified CFE convention 1F=punta/2F=inter/3F=base.
    division = v.get("DIVISION")
    f1 = _f(v.get("CONSUMO1F")) or 0.0
    f2 = _f(v.get("CONSUMO2F")) or 0.0
    f3 = _f(v.get("CONSUMO3F")) or 0.0
    by_field = dict(zip(_consumo_order(division), (f1, f2, f3)))
    kwh_base = by_field["kwh_base"]
    kwh_inter = by_field["kwh_inter"]
    kwh_punta = by_field["kwh_punta"]
    # Self-validating guard (mirrors harvest PR #17): the three registers must
    # reconcile to CONSUMO_R (the total). A mismatch means an unknown addenda
    # layout for this division — surface it rather than emit a garbage split.
    consumo_r = _f(v.get("CONSUMO_R"))
    if consumo_r and abs((f1 + f2 + f3) - consumo_r) > max(1.0, 0.001 * consumo_r):
        raise ValueError(
            f"CONSUMO1F+2F+3F ({f1 + f2 + f3:.0f}) != CONSUMO_R ({consumo_r:.0f}) "
            f"for division {division!r} in {os.path.basename(path)} — "
            f"unknown addenda layout; add it to _CONSUMO_ORDER_BY_DIVISION (#18)")
    # demands by period: DEMANDA1P/2P/3P; DEMANDA = max register
    kw_base = _f(v.get("DEMANDA1P")) or 0.0
    kw_inter = _f(v.get("DEMANDA2P")) or 0.0
    kw_punta = _f(v.get("DEMANDA3P")) or 0.0

    # baseline (sum MEM importes) and FP charge/credit derived from SubTotal so the
    # receipt check reproduces 'Facturacion del Periodo' = (SubTotal)*1.16 exactly.
    mem_sum = sum(mem.values())
    subtotal = _f(v.get("SubTotal"))
    bonif_fp = (subtotal - mem_sum) if subtotal is not None else 0.0
    # bonif_fp is the NET FP effect (subtotal - MEM): positive = cargo por bajo factor
    # de potencia (FP<90%), negative = bonificación (FP>=90%). The penalty is the
    # positive part — additive savings if corrected. Kept separate so baseline_month
    # and receipt_check (which use the net bonif_fp) stay unchanged.
    cargo_fp_penalty = max(0.0, bonif_fp)
    # 'Facturacion del Periodo' = SubTotal * 1.16 (IVA). IMPTOTAL is in centavos.
    facturacion = round(subtotal * 1.16, 2) if subtotal is not None else None

    d = {
        "file": os.path.basename(path),
        "start": start.isoformat(), "end": end.isoformat(),
        "days": days, "month": month, "year": year,
        "servicio": v.get("RPU"),
        "multiplicador": None,
        "demanda_contratada": _f(v.get("CARGA_CONTRATADA")),
        "tarifa": v.get("TARIFA"),
        "division_code": v.get("DIVISION"),
        "cp": v.get("CODIGO_POSTAL"),
        "kwh_base": kwh_base, "kwh_inter": kwh_inter, "kwh_punta": kwh_punta,
        "kw_base": kw_base, "kw_inter": kw_inter, "kw_punta": kw_punta,
        "kw_max": _f(v.get("DEMANDA")),
        "kvarh": _f(v.get("KVARH")),
        "fp": _f(v.get("FacPot")),
        **mem,
        "bonif_fp": bonif_fp,
        "cargo_fp_penalty": cargo_fp_penalty,
        "energia_desglose": None,
        "subtotal_recibo": subtotal,
        "facturacion_recibo": facturacion,
    }
    d["kwh_total"] = kwh_base + kwh_inter + kwh_punta
    return d


def load_bills_json(path: str) -> list[dict]:
    """Pre-extracted bill records (same schema as parse_bill), e.g. produced by
    tools/import_perfil_xlsx.py from a client 'Perfil de Consumo' workbook."""
    import json
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def extract_folder(folder: str) -> list[dict]:
    # A folder of imported records (no raw recibos) carries bills.json directly.
    bj = os.path.join(folder, "bills.json")
    if os.path.exists(bj):
        bills = load_bills_json(bj)
    else:
        pdfs = sorted(glob.glob(os.path.join(folder, "*.pdf")))
        xmls = sorted(glob.glob(os.path.join(folder, "*.xml")))
        bills = [parse_bill(p) for p in pdfs] + [parse_bill_xml(p) for p in xmls]
    bills.sort(key=lambda b: (b["year"], b["month"]))
    return bills
