# -*- coding: utf-8 -*-
"""Analyze a client intake folder -> structured profile.json + outbound_draft.md.

Given intake/<slug>/ containing:
  messages/   inbound message bodies (.txt, one per email/whatsapp message)
  attachments/  whatever the client sent (CFE bill PDFs, CFDI XMLs, perfil .xlsx, ...)

this script:
  1. summarizes the attachments via cfe_savings.extract (RPU, tariff, months, FP)
     -- raw bytes never enter LLM context; only the compact summary is kept;
  2. fills the profile against intake_schema (derivable fields from bills, the rest
     marked missing or defaulted);
  3. writes profile.json (the handoff artifact) and outbound_draft.md (the simple
     client questions, in Spanish, for the user to approve before sending).

It computes; it does not decide tone. The `client-intake` subagent reads profile.json
and may rewrite outbound_draft.md in warmer/clearer language before approval.

Usage:
  python tools/intake/profile_builder.py <slug>            # intake/<slug>/
  python tools/intake/profile_builder.py --root intake <slug>
"""
from __future__ import annotations
import argparse, json, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from intake_schema import (FIELDS, FIELDS_BY_KEY, CLIENT_FIELDS, empty_profile,
                           coverage_flag)

MONTHS_ES = ["", "ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]


def _summarize_bills(attach_dir: Path) -> dict:
    """Call the existing extractor on the attachments folder. Returns a compact
    summary, never the raw bill text. Tolerant: a parse failure is reported, not
    fatal (the analyst can still look)."""
    out = {"present": False, "count": 0, "months": [], "rpu": None, "tarifa": None,
           "fp_min": None, "fp_penalty_seen": False, "parse_errors": [], "kwh_year": None}
    if not attach_dir.exists():
        return out
    bill_files = [p for p in attach_dir.iterdir()
                  if p.suffix.lower() in (".pdf", ".xml")]
    if not bill_files:
        return out
    try:
        from cfe_savings.extract import extract_folder
        bills = extract_folder(str(attach_dir))
    except Exception as e:                       # noqa: BLE001
        out["parse_errors"].append(f"{type(e).__name__}: {e}")
        out["present"] = bool(bill_files)
        out["count"] = len(bill_files)
        return out
    out["present"] = True
    out["count"] = len(bills)
    out["months"] = [f"{MONTHS_ES[b['month']]}{str(b['year'])[2:]}"
                     for b in bills if b.get("month")]
    fps = [b.get("fp") for b in bills if b.get("fp") is not None]
    if fps:
        out["fp_min"] = min(fps)
        out["fp_penalty_seen"] = out["fp_min"] < 90
    pens = [b.get("cargo_fp_penalty") or 0 for b in bills]
    if any(p > 0 for p in pens):
        out["fp_penalty_seen"] = True
    rpus = {b.get("servicio") for b in bills if b.get("servicio")}
    if len(rpus) == 1:
        out["rpu"] = rpus.pop()
    kwh = [b.get("kwh_total") or 0 for b in bills]
    if kwh and len(bills) >= 1:
        out["kwh_year"] = round(sum(kwh) / max(1, len(bills)) * 12)
    return out


def _client_answers(client_dir: Path) -> dict:
    """Optional answers.json the user fills as the client replies:
       {"roof_area_m2": 4000, "transformer_kva": 1000, "interval_15min": true, ...}"""
    f = client_dir / "answers.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8-sig"))   # tolerate BOM
        except Exception:                        # noqa: BLE001
            return {}
    return {}


def build(slug: str, root: Path) -> dict:
    client_dir = root / slug
    client_dir.mkdir(parents=True, exist_ok=True)
    (client_dir / "messages").mkdir(exist_ok=True)
    (client_dir / "attachments").mkdir(exist_ok=True)

    # preserve known meta if a profile already exists
    pf_path = client_dir / "profile.json"
    if pf_path.exists():
        profile = json.loads(pf_path.read_text(encoding="utf-8"))
    else:
        profile = empty_profile(slug)

    bills = _summarize_bills(client_dir / "attachments")
    answers = _client_answers(client_dir)

    # --- bills block ---
    nmonths = len(bills["months"])
    profile["bills"] = {"present": bills["present"], "count": bills["count"],
                        "months": bills["months"], "coverage_flag": coverage_flag(nmonths),
                        "kwh_year_est": bills.get("kwh_year"),
                        "parse_errors": bills["parse_errors"]}
    if bills["rpu"]:
        profile["tariff"]["rpu"] = bills["rpu"]

    # --- fill every field ---
    fields = profile.get("fields", {})

    def set_field(key, value, status, source):
        fields[key] = {"value": value, "status": status, "source": source}

    for f in FIELDS:
        # 1) explicit client answer wins
        if f.key in answers and answers[f.key] not in (None, ""):
            set_field(f.key, answers[f.key], "known", "client"); continue
        # 2) derivable from bills
        if f.key == "rpu" and bills["rpu"]:
            set_field(f.key, bills["rpu"], "known", "bill"); continue
        if f.key == "fp_penalty":
            set_field(f.key, bills["fp_penalty_seen"],
                      "known" if bills["present"] else "missing", "bill"); continue
        if f.key == "bills_12m":
            ok = nmonths >= 12
            set_field(f.key, f"{nmonths} meses" if bills["present"] else None,
                      "known" if ok else ("partial" if bills["present"] else "missing"),
                      "bill"); continue
        # 3) internal default
        if f.audience == "internal" and f.default is not None:
            set_field(f.key, f.default, "assumed", "default"); continue
        # 4) otherwise missing (client question pending)
        if f.key not in fields or fields[f.key].get("status") not in ("known",):
            set_field(f.key, None, "missing", None)

    profile["fields"] = fields

    # --- completeness + next questions ---
    open_client = [f for f in CLIENT_FIELDS
                   if fields.get(f.key, {}).get("status") in ("missing", "partial", None)]
    blocking = [f.key for f in FIELDS if f.blocking
                and fields.get(f.key, {}).get("status") not in ("known",)]
    answered_client = len(CLIENT_FIELDS) - len(open_client)
    profile["completeness"] = {
        "client_questions_open": [f.key for f in open_client],
        "blocking_missing": blocking,
        "pct_client": round(100.0 * answered_client / max(1, len(CLIENT_FIELDS)), 1),
    }
    profile["next_questions"] = [{"key": f.key, "es": f.es_question} for f in open_client]
    profile["ready_for"] = (["cfe-savings-analyst"] if not blocking and bills["present"]
                            else [])
    profile["updated"] = datetime.date.today().isoformat()

    pf_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_draft(client_dir, profile, bills)
    return profile


def _write_draft(client_dir: Path, profile: dict, bills: dict) -> None:
    """Plain-Spanish question draft for the user to approve before sending. The
    subagent may rewrite this; this is the deterministic floor."""
    name = profile["client"].get("name", profile["client"]["slug"])
    qs = profile["next_questions"]
    lines = [f"# Borrador de correo — {name}", "",
             "_Revíselo y edítelo antes de enviar. El sistema NO envía nada sin su aprobación._", ""]
    if bills["present"]:
        lines.append(f"**Recibimos:** {bills['count']} recibo(s) "
                     f"({', '.join(bills['months']) or 's/f'}); "
                     f"cobertura {profile['bills']['coverage_flag']}.")
        if bills.get("fp_penalty_seen"):
            lines.append("**Detectado:** penalización por bajo factor de potencia "
                         "(FP<90%) — palanca de ahorro de alto retorno.")
        lines.append("")
    if not qs:
        lines.append("**Perfil completo.** No hay preguntas pendientes para el cliente. "
                     "Listo para el `cfe-savings-analyst`.")
    else:
        lines += ["Estimado(a) cliente:", "",
                  "Gracias por la información. Para entregarle un análisis de ahorro "
                  "preciso (no estimado), nos faltarían un par de datos sencillos:", ""]
        for i, q in enumerate(qs, 1):
            lines.append(f"{i}. {q['es']}")
        lines += ["", "Con eso modelamos su caso a la medida. Quedamos atentos.", ""]
    (client_dir / "outbound_draft.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--root", default=str(ROOT / "intake"))
    a = ap.parse_args()
    p = build(a.slug, Path(a.root))
    print(json.dumps({"slug": a.slug,
                      "pct_client": p["completeness"]["pct_client"],
                      "blocking_missing": p["completeness"]["blocking_missing"],
                      "client_questions_open": p["completeness"]["client_questions_open"],
                      "ready_for": p["ready_for"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
