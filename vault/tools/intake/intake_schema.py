# -*- coding: utf-8 -*-
"""Client-intake profile schema + profiling question bank.

This is the canonical, machine-readable mirror of the "Intake question bank" in
CLAUDE.md. The profiling layer (transport connector + profile_builder + the
`client-intake` subagent) reads it to decide what a client profile already knows,
what is still missing, and which SIMPLE questions to put to the client.

Design rules baked in here:
  - Auto-derive everything the bills/wiki can answer; ask the client ONLY what they
    can't (CLAUDE.md). So fields carry `derivable_from_bill` and `audience`.
  - `audience="client"` -> a plain-Spanish question a non-engineer can answer.
    `audience="internal"` -> our assumption/default; NEVER sent to the client, just
    handed to the analyst (cfe-savings-analyst / project-checker) as a default.
  - `blocking=True` -> the downstream engine can't run a meaningful case without it.

The profile this produces is a handoff artifact, not a result. Numbers/savings come
later from the engine. Raw bill bytes never enter LLM context: attachments are
summarized by cfe_savings.extract, and only the summary lands in the profile.
"""
from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Optional, Any
import re, unicodedata


def slugify(text: str) -> str:
    """email/display-name -> stable folder slug."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "cliente"


@dataclass
class Field:
    key: str
    audience: str            # "client" | "internal"
    blocking: bool
    derivable_from_bill: bool
    default: Any
    es_question: Optional[str]   # client-facing, simple Spanish (None for internal)
    note: str = ""


# Order matters: bills first (unlock the derivable fields), then the few simple
# physical questions, then internal defaults.
FIELDS: list[Field] = [
    # --- identity / derivable from the recibo itself ---
    Field("rpu", "internal", True, True, None, None,
          "No. de servicio / RPU; parsed from the bill."),
    Field("tarifa", "internal", False, True, "GDMTH", None,
          "GDMTH / GDMTO / PDBT; defaults GDMTH (the engine's regime), analyst confirms."),
    Field("fp_penalty", "internal", False, True, None, None,
          "Factor-de-potencia penalty (FP<90%) detected on the bills -> a high-ROI lever."),

    # --- the one thing we always need from the client ---
    Field("bills_12m", "client", False, True, None,
          "Para darle números reales y no estimados, ¿nos comparte sus últimos 12 "
          "recibos CFE en PDF (o la factura CFDI en XML)? Con 12 meses captamos la "
          "estacionalidad; con menos, le avisamos del margen de error."),

    # --- simple physical questions only the client can answer ---
    Field("roof_area_m2", "client", False, False, None,
          "¿Cuánta área disponible tienen para paneles? Un estimado en m² de techo o "
          "terreno está bien (con eso calculamos cuánto solar cabe)."),
    Field("transformer_kva", "client", False, False, None,
          "¿De qué capacidad es su transformador o subestación, en kVA? Viene en la "
          "placa del equipo o en su contrato de CFE."),
    Field("interval_15min", "client", False, False, None,
          "¿Pueden conseguir su medición a intervalos de 15 minutos? Su medidor CFE "
          "horario normalmente la exporta; con ese dato el análisis pasa de estimado "
          "a nivel banco. Si no, no hay problema, lo modelamos."),
    Field("growth_plans", "client", False, False, None,
          "¿Tienen planes de aumentar su consumo o agregar carga importante (nueva "
          "línea, ampliación, cargadores de auto) en los próximos 2-3 años?"),

    # --- internal defaults: handed to the analyst, NEVER asked to the client ---
    Field("scheme", "internal", False, False, "medicion_neta", None,
          "Default medición neta (<0.7 MW exento); revisit if generation crosses 0.7 MW."),
    Field("pv_sizing", "internal", False, False, "auto", None,
          "Default min(area-cap, 700 kW) to stay permit-exempt."),
    Field("bess_sizing", "internal", False, False, "auto", None,
          "Default: cover the punta peak."),
    Field("yield_source", "internal", False, False, "lookup", None,
          "Prefeasibility municipio lookup unless a Helioscope/PVsyst file is provided."),
    Field("availability", "internal", False, False, 0.75, None,
          "Savings-as-a-service downtime assumption, not physics."),
    Field("financials", "internal", False, False, "defaults", None,
          "EPC USD/Wp, FX, BESS $/kWh, O&M, PPA rate/term, WACC, escalation, CAPEX, "
          "SaaS share, FP-correction on/off -> defaults; ask only overrides, and only "
          "to the user/financier, never to the client."),
]

FIELDS_BY_KEY = {f.key: f for f in FIELDS}
CLIENT_FIELDS = [f for f in FIELDS if f.audience == "client"]


def coverage_flag(months: int) -> str:
    if months >= 12:
        return "ok(>=12)"
    if months >= 1:
        return f"partial({months}<12) -> flag seasonality risk"
    return "none -> baseline cannot be validated"


def empty_profile(slug: str, name: str = "", email: str = "") -> dict:
    return {
        "client": {"slug": slug, "name": name or slug,
                   "contact": {"email": email or None, "whatsapp": None}},
        "channel": None,
        "tariff": {"rpu": None, "tarifa": None, "division": None, "tension": None},
        "bills": {"present": False, "count": 0, "months": [], "coverage_flag": coverage_flag(0)},
        "fields": {},          # key -> {value, status, source}
        "completeness": {"client_questions_open": [k.key for k in CLIENT_FIELDS],
                         "blocking_missing": [], "pct_client": 0.0},
        "ready_for": [],       # ["cfe-savings-analyst"] when the blocking set is satisfied
        "next_questions": [],  # [{key, es}]
        "messages_seen": [],
        "updated": None,
    }
