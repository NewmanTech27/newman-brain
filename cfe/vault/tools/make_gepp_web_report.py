# -*- coding: utf-8 -*-
"""GEPP web report builder — entregables/reportes/gepp_max_savings_data.json →
self-contained HTML webpage (portfolio overview + per-site drill-down tabs).

House style: dark navy + emerald (make_executive_report.py conventions), Spanish,
no external assets. Chart mark palette validated (dataviz six checks, dark surface
#0b1120): PV #d97706 · BESS #3b82f6 · FP #ec4899 · después/total #059669.

Outputs:
  entregables/reportes/GEPP - Solucion Energetica Web.html   (full document)
  --artifact-body <path>: same content without the <!doctype>/<html> wrapper
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")

SHORT = {"gepp-cancun": "Cancún", "gepp-acapulco": "Acapulco",
         "gepp-ixtlahuacan": "Ixtlahuacán", "gepp-proplasa-pr1": "Proplasa PR1",
         "gepp-proplasa-pr2": "Proplasa PR2", "gepp-proplasa-tap": "Proplasa TAP"}
ORDER = ["gepp-cancun", "gepp-acapulco", "gepp-ixtlahuacan",
         "gepp-proplasa-pr1", "gepp-proplasa-pr2", "gepp-proplasa-tap"]

CAVEATS = {
    "gepp-cancun": [
        "El umbral de demanda satura 9/12 meses: el PV captura el ahorro de demanda vía umbral y el BESS óptimo queda chico (2h).",
        "La reconstrucción diverge del total impreso del cliente −2% a −9% (la hoja CAN trae bloques TALA/PTAR además de CFE); la base usada = carga total a tarifa CFE plena.",
        "FP crónico ~89%: multa ≈ $0.60M/año. Capacitor $0.5M — payback en meses; palanca separada de PV/BESS.",
    ],
    "gepp-acapulco": [
        "FP crónico 85–86% todos los meses: multa $1.72M/año — la palanca #1 del sitio, payback del capacitor ($1.0M) en meses.",
        "Cargo de demanda = 43% del subtotal (el más pesado del portafolio) — por eso el BESS 2h rinde tanto aquí.",
        "100% CFE (sin autoabasto): la base de ahorro es directa.",
    ],
    "gepp-ixtlahuacan": [
        "Autoabasto Tala (bagazo, zafra dic–may) con ~10% de descuento sobre energía hasta 2032: el ahorro aquí está medido contra CFE pleno; el beneficio neto vs lo que paga HOY es ~$2.7M/año menor mientras viva el contrato Tala.",
        "Picos de demanda por ENCIMA de la contratada (5,000 kW) en abr/may/dic 2025 (hasta 7,310 kW) — auditar exposición y falla operativa.",
        "El BESS de 4.2 MW es el segundo mayor del portafolio; su valor descansa en el recorte de punta modelado — confirmar con data 15-min.",
    ],
    "gepp-proplasa-pr1": [
        "Colapso ENEL confirmado (PR1 cayó a ~25–28% en mar–abr 2026): la base a CFE pleno ya es la realidad vigente, no un supuesto.",
        "El umbral NO satura ningún mes: cada kW recortado por el BESS vale 1:1 — el mejor tipo de sitio para batería.",
        "Área de techo compartida del predio Proplasa sin confirmar (proxy 4,938 m²/servicio).",
    ],
    "gepp-proplasa-pr2": [
        "Colapso ENEL: PR2 fue el primero (~16% desde sep-2025) — lleva más de un año pagando CFE pleno en ~85% de su carga.",
        "El sitio más grande del portafolio (45.7 GWh): BESS 6.1 MW / 12.2 MWh es el activo individual mayor del deal — su tamaño depende del load-shape modelado; data 15-min lo haría bancable.",
        "El umbral NO satura ningún mes: valor 1:1 del recorte de punta.",
    ],
    "gepp-proplasa-tap": [
        "Colapso ENEL (TAP a ~13–15% en mar–abr 2026): base CFE plena vigente.",
        "El umbral NO satura ningún mes: valor 1:1 del recorte de punta.",
        "Área de techo compartida del predio Proplasa sin confirmar (proxy 4,938 m²/servicio).",
    ],
}

GLOBAL_CAVEATS = [
    ("motor", "Números del MOTOR determinista CFE Brain (calibrado al peso contra recibos reales) sobre los 12 meses reales de 2025 importados del workbook del cliente — no de recibos CFE originales. Reconstrucción validada mes a mes contra el total impreso."),
    ("carga", "Forma de carga intra-día MODELADA (curva industrial 24/7 escalada al pico), no medida: el recorte de punta del BESS es prefactibilidad. Data 15-min del medidor lo vuelve bancable y es el siguiente paso #1."),
    ("pv", "PV topado al máximo generador exento: 839.41 kWp DC = 0.7 MW AC (DC/AC 1.199). El barrido confirma que cruzar a autoconsumo (permiso CNE + BESS obligatorio + ~1 año de retraso) NO agrega NPV en ningún sitio."),
    ("bess", "BESS operando como SAE-CC (sin permiso, sin inyección a red, behind-the-meter). Duración óptima = 2h a potencia de pico de punta en LOS SEIS sitios — la ventana de punta de verano (2h, may–oct) domina el año completo."),
    ("area", "Área de techo real por sitio SIN confirmar (proxy 4,938 m² por servicio). 839 kWp requieren ~4,940 m² — confirmar techo/estacionamiento antes de ingeniería."),
    ("rates", "Tarifas 2025 del workbook (≈$1.82/kWh intermedio); escalación CFE 5%/año, WACC 12%, FX 17.55, EPC 0.75 USD/Wp, BESS 280 USD/kWh."),
]


# Engine defaults (calc_core.DEFAULT_INPUTS) — the sweep ran with these untouched.
# The projection below replicates calc_core._finance / ppa_pricer.deal_flows exactly;
# the compra flows are reconciled at build time against the engine numbers stored in
# the sweep JSON (see _projection) — any drift vs calc_core fails the build.
ESC_CFE, WACC = 0.05, 0.12
PV_DEGR, BESS_DEGR = 0.005, 0.0125
FALLA = (12 - 3) / 12
FIANZA = 0.139
OM_PV_KWP, OM_BESS_KWH = 310.0, 180.0
BESS_YRS, HORIZON = 15, 20

# ---- Esquema presentado al CLIENTE (2026-07-02): PPA solar + BESS 50/50 ----
# El cliente pidió PPA + almacenamiento compartido 50/50. El documento NO muestra
# TIR/VPN del financiador (economía interna) — el builder la imprime en consola
# al regenerar para revisión nuestra. Ajustar la tarifa PPA aquí si el comité
# mueve el precio; todo lo demás se recalcula.
PPA_CLIENT, COM_CLIENT = 1.80, 0.50
PPA_YRS_CLIENT, ESC_PPA_CLIENT = 15, 0.05


def _irr(flows, lo=-0.95, hi=4.0):
    f = lambda r: sum(x / (1 + r) ** i for i, x in enumerate(flows))
    if not flows or f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _npv(flows, rate=WACC):
    return sum(x / (1 + rate) ** i for i, x in enumerate(flows))


def _close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _projection(s: dict) -> tuple[dict, dict]:
    """Per-site 20-year projection rows (Hibrido) — same idea as the calculadora's
    '6. PROYECCIÓN 20 AÑOS' section, same math as calc_core._finance and
    ppa_pricer.deal_flows, computed from the sweep JSON's annual bases, at the
    CLIENT deal terms (PPA_CLIENT + COM_CLIENT 50/50). FP stays OUT of the flows
    (separate additive lever, 100% client) — shown as its own informational column.

    Returns (client_embed, internal): client_embed goes into the HTML DATA and
    carries NO financier economics and NO IRR; internal (financier TIR/VPN at
    these terms) is printed to console for our review only. The compra flows are
    reconciled against the engine numbers stored in the sweep JSON — any
    parameter drift vs calc_core fails the build."""
    ann, fin = s["annual"], s["finance"]["Hibrido"]
    base_pv = ann["ah_pv"] + ann["dem_pv"]
    base_bess = ann["dem_bess"] + ann["arb"]
    base_claw = ann["hibrido"] - base_pv - base_bess
    gen, antes, fp0 = ann["gen"], ann["antes"], ann["fp_lever"]
    has_pv, has_bess = s["pv"]["kwp"] > 0, s["bess"]["kwh"] > 0
    om_pv = s["pv"]["kwp"] * OM_PV_KWP if has_pv else 0.0
    om_bess = s["bess"]["kwh"] * OM_BESS_KWH if has_bess else 0.0
    ppa, com_sh = PPA_CLIENT, COM_CLIENT
    ppa_yrs, esc_ppa = PPA_YRS_CLIENT, ESC_PPA_CLIENT
    capex = fin["capex"]
    R = lambda x: round(x)
    rows = []
    fl_proj, fl_fin, fl_cli = [-capex], [-capex], [0.0]
    for yy in range(1, HORIZON + 1):
        e = (1 + ESC_CFE) ** yy
        dpv = (1 - PV_DEGR) ** yy
        dbe = (1 - BESS_DEGR) ** yy
        sav_pv = base_pv * e * dpv if has_pv else 0.0
        sav_bess = base_bess * e * dbe * FALLA if has_bess else 0.0
        clw = base_claw * e * (dpv + dbe) / 2
        bruto = sav_pv + sav_bess + clw
        ppa_pay = gen * dpv * ppa * (1 + esc_ppa) ** (yy - 1) if (has_pv and yy <= ppa_yrs) else 0.0
        com = sav_bess * com_sh if (has_bess and yy <= BESS_YRS) else 0.0
        ompv = om_pv * (1 + ESC_CFE) ** (yy - 1) if (has_pv and yy <= ppa_yrs) else 0.0
        ombe = om_bess * (1 + ESC_CFE) ** (yy - 1) if (has_bess and yy <= BESS_YRS) else 0.0
        fz = ppa_pay * FIANZA
        fl_proj.append(bruto - ompv - ombe)
        fl_fin.append(ppa_pay + com - ompv - ombe - fz)
        fl_cli.append(bruto - ppa_pay - com)
        tarifa = antes * e
        fp_y = fp0 * e
        rows.append(dict(y=yy, tarifa=R(tarifa), pv=R(sav_pv), bess=R(sav_bess),
                         fp=R(fp_y), costo=R(tarifa - bruto - fp_y),
                         compra=R(fl_proj[-1]), ppa=R(ppa_pay), com=R(com),
                         cli=R(fl_cli[-1])))
    # ---- reconcile the compra flows against the engine (sweep JSON) ----
    checks = [
        ("vpn_proyecto", _npv(fl_proj), fin["vpn"]),
        ("tir_proyecto", _irr(fl_proj), fin["tir"]),
    ]
    for name, got, want in checks:
        if not _close(got, want, 1e-5):
            raise SystemExit(f"proyección {s['slug']}: {name} recalculado {got!r} "
                             f"≠ motor {want!r} — parámetros desalineados con calc_core")
    neg = [i + 1 for i, x in enumerate(fl_cli[1:]) if x < -1e-6]
    client = dict(ppa=round(ppa, 3), com=round(com_sh, 3),
                  ppa_yrs=ppa_yrs, esc_ppa=esc_ppa, capex=R(capex),
                  vpn_compra=R(fin["vpn"]), payback=fin["payback"],
                  cli_a1=R(fl_cli[1]), cum_compra=R(sum(fl_proj[1:])),
                  cum_cli=R(sum(fl_cli[1:])), rows=rows)
    internal = dict(tir_fin=_irr(fl_fin), vpn_fin=_npv(fl_fin),
                    tir_compra=fin["tir"], anios_negativos=neg)
    return client, internal


def _fix_alerts(s: dict) -> list:
    """The engine's internal exento line is 700 kWp DC; the vault rule (2026-06-19,
    feedback-exento-dc-cap) puts it at 0.7 MW AC = 839.41 kWp DC. At 839.41 the
    engine's autoconsumo alerts (CNE permit / mandatory backup) are therefore wrong
    labels — the savings numbers are unaffected (100% credited, excedentes ≈ 0).
    Replace them with one truthful note instead of silently dropping them."""
    if s["pv"]["kwp"] > 839.41:
        return s["alerts"]
    out = [a for a in s["alerts"]
           if not (a[1].startswith("Autoconsumo activo")
                   or a[1].startswith("Respaldo de intermitencia"))]
    out.append(["info", "839.41 kWp DC = 0.7 MW AC → GENERADOR EXENTO (regla AC↔DC del "
                "19-jun). El motor marca internamente ≥700 kWp DC como autoconsumo; sin "
                "efecto en los números (100% del PV acreditado, excedentes ≈ 0)."])
    return out


def build_data() -> dict:
    raw = json.loads((ROOT / "entregables" / "reportes" / "gepp_max_savings_data.json")
                     .read_text(encoding="utf-8"))
    R = lambda x: round(x) if isinstance(x, float) else x
    sites, internal = {}, {}
    for slug in ORDER:
        s = raw["sites"][slug]
        pv_lever = R(s["annual"]["ah_pv"] + s["annual"]["dem_pv"])
        bess_lever = R(s["annual"]["dem_bess"] + s["annual"]["arb"])
        proj, internal[slug] = _projection(s)
        kwh_tot = sum(r["kwh"] for r in s["monthly"])
        f, fa = s["full"], s["full"]["annual"]
        sites[slug] = dict(
            corto=SHORT[slug], nombre=s["nombre"], rpu=s["rpu"], municipio=s["municipio"],
            estado=s["estado"], dem=s["demanda_contratada"], yield_src=s["yield_source"],
            regimen=s["regimen"], kwp=s["pv"]["kwp"],
            bess=dict(kw=s["bess"]["kw"], kwh=s["bess"]["kwh"], h=s["bess"]["h"],
                      pico=s["bess"]["punta_peak_kw"]),
            fp=dict(activo=s["fp"]["activo"], cargo=R(s["fp"]["cargo_anual"]),
                    capacitor=s["fp"]["capacitor"],
                    payback_m=round(s["fp"]["payback_meses"], 1) if s["fp"]["payback_meses"] else None),
            annual=dict(antes=R(s["annual"]["antes"]), hib=R(s["annual"]["hibrido"]),
                        pct=s["annual"]["pct"], pv=pv_lever, bess=bess_lever,
                        fp=R(s["annual"]["fp_lever"]), gen=R(s["annual"]["gen"]),
                        neto=R(s["annual"]["neto_disp"]["hibrido"])),
            fin=dict(capex=R(s["finance"]["Hibrido"]["capex"]),
                     vpn=R(s["finance"]["Hibrido"]["vpn"]),
                     payback=s["finance"]["Hibrido"]["payback"]),
            deal=dict(ppa=proj["ppa"], com=proj["com"], ppa_yrs=proj["ppa_yrs"],
                      esc_ppa=proj["esc_ppa"], cli_a1=proj["cli_a1"],
                      cum_cli=proj["cum_cli"],
                      blend=round(s["annual"]["antes"] / kwh_tot, 4) if kwh_tot else None),
            monthly=[dict(m=r["m"], antes=R(r["antes"]), hib=R(r["hibrido"]),
                          desp=R(r["despues"]), gen=R(r["gen"]), pv=R(r["ah_pv"] + r["dem_pv"]),
                          bess=R(r["dem_bess"] + r["arb"]), fp=R(r["fp"]),
                          kwh=R(r["kwh"]), desc=R(r["desc"]))
                     for r in s["monthly"]],
            proj=proj,
            full=dict(kwp=round(f["kwp"], 1), bess_kw=f["bess_kw"], bess_kwh=f["bess_kwh"],
                      h=f["h"], regimen=f["regimen"], capex=R(f["capex"]), vpn=R(f["vpn"]),
                      antes=R(fa["antes"]), hib=R(fa["hibrido"]), pct=fa["pct"],
                      gen=R(fa["gen"]), exced=R(fa["exced"]), kwh=R(fa["kwh"]),
                      pct_ac=fa["pct_ac"],
                      ordinario=f["kwp"] > 20000),
            bessCurve=[dict(h=p["h"], npv=R(p["npv"]), ahorro=R(p["ahorro"]),
                            kwh=p["bess_kwh"]) for p in s["bess"]["curve"]],
            pvCurve=[dict(kwp=p["kwp"], npv=R(p["npv"]), regimen=p["regimen"])
                     for p in s["pv"]["curva"]],
            alerts=_fix_alerts(s), caveats=CAVEATS[slug],
        )
    # portfolio aggregates
    P = raw["portfolio"]
    mon = []
    for i in range(12):
        mon.append(dict(m=i + 1,
                        antes=sum(sites[s]["monthly"][i]["antes"] for s in ORDER),
                        hib=sum(sites[s]["monthly"][i]["hib"] for s in ORDER),
                        desp=sum(sites[s]["monthly"][i]["desp"] for s in ORDER)))
    deal_sum = dict(ppa=PPA_CLIENT, com=COM_CLIENT, ppa_yrs=PPA_YRS_CLIENT,
                    esc_ppa=ESC_PPA_CLIENT,
                    cli_a1=sum(sites[s]["deal"]["cli_a1"] for s in ORDER),
                    cum_cli=sum(sites[s]["deal"]["cum_cli"] for s in ORDER))
    # portfolio 20-yr projection = sum of the 6 per-site projections (all at the
    # client deal terms), cumulative columns included — mirrors the calculadora's
    # 'Proyección 20 años' roll-up sheet
    pproj, cum_c, cum_p = [], 0.0, 0.0
    for i in range(20):
        row = {k: sum(sites[s]["proj"]["rows"][i][k] for s in ORDER)
               for k in ("tarifa", "pv", "bess", "fp", "costo", "compra", "cli")}
        row["y"] = i + 1
        cum_c += row["compra"]; cum_p += row["cli"]
        row["cum_compra"], row["cum_cli"] = round(cum_c), round(cum_p)
        pproj.append(row)
    proj_port = dict(capex=sum(sites[s]["proj"]["capex"] for s in ORDER),
                     cum_compra=sum(sites[s]["proj"]["cum_compra"] for s in ORDER),
                     cum_cli=sum(sites[s]["proj"]["cum_cli"] for s in ORDER),
                     rows=pproj)
    full_port = dict(
        kwp=round(sum(sites[s]["full"]["kwp"] for s in ORDER), 1),
        capex=sum(sites[s]["full"]["capex"] for s in ORDER),
        gen=sum(sites[s]["full"]["gen"] for s in ORDER),
        exced=sum(sites[s]["full"]["exced"] for s in ORDER),
        kwh=sum(sites[s]["full"]["kwh"] for s in ORDER),
        hib=sum(sites[s]["full"]["hib"] for s in ORDER),
        antes=sum(sites[s]["full"]["antes"] for s in ORDER),
    )
    portfolio = dict(
        antes=R(P["antes"]), hib=R(P["hibrido"]), pct=P["hibrido"] / P["antes"],
        fp=R(P["fp_lever"]), capex=R(P["capex"]), vpn=R(P["vpn"]),
        kwp=round(P["kwp"], 1), bess_kw=P["bess_kw"], bess_kwh=P["bess_kwh"],
        capacitores=P["capacitores"], gen=R(P["gen"]), monthly=mon, deal=deal_sum,
        proj=proj_port, full=full_port,
        pv_lever=sum(sites[s]["annual"]["pv"] for s in ORDER),
        bess_lever=sum(sites[s]["annual"]["bess"] for s in ORDER),
        payback_min=min(sites[s]["fin"]["payback"] for s in ORDER),
        payback_max=max(sites[s]["fin"]["payback"] for s in ORDER),
    )
    return dict(order=ORDER, sites=sites, portfolio=portfolio,
                global_caveats=GLOBAL_CAVEATS), internal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-body", default=None)
    a = ap.parse_args()
    data, internal = build_data()
    # Economía interna del esquema cliente (PPA + 50/50) — SOLO consola, nunca al HTML
    print(f"— Economía interna @ PPA ${PPA_CLIENT:.2f} + comisión {COM_CLIENT:.0%} "
          f"(no incluida en el documento):")
    for slug, i in internal.items():
        neg = f" · años cliente NEGATIVOS: {i['anios_negativos']}" if i["anios_negativos"] else ""
        print(f"   {slug}: TIR financiador {i['tir_fin']:.1%} · VPN financiador "
              f"${i['vpn_fin']/1e6:,.1f}M · TIR compra cliente {i['tir_compra']:.1%}{neg}")
    tpl = (ROOT / "tools" / "gepp_web_report_body.html").read_text(encoding="utf-8")
    fonts = (ROOT / "tools" / "newman_fonts_inline.css").read_text(encoding="utf-8")
    body = (tpl.replace("__FONTS__", fonts)
               .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"))))
    full = ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            "<title>GEPP — Solución Energética · CFE Brain OS</title>\n</head>\n<body>\n"
            + body + "\n</body>\n</html>\n")
    dst = ROOT / "entregables" / "reportes" / "GEPP - Solucion Energetica Web.html"
    dst.write_text(full, encoding="utf-8")
    print(f"→ {dst} ({len(full)/1024:.0f} KB)")
    if a.artifact_body:
        Path(a.artifact_body).write_text(body, encoding="utf-8")
        print(f"→ {a.artifact_body}")


if __name__ == "__main__":
    main()
