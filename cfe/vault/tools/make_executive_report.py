# -*- coding: utf-8 -*-
"""Reporte ejecutivo del OS — HTML standalone para presentar a dirección.

Corre el portafolio en vivo (tools/portfolio.py -> calc_core, golden-validado)
y lo combina con el caso GEPP archivado (prefactibilidad best-case,
[[2026-06-10-gepp-portfolio-project-check]]). Cada cifra lleva su nivel de
hecho: recibo (fuente primaria) / motor / prefactibilidad archivada.

Salida: entregables/reportes/Reporte Ejecutivo - CFE Brain OS.html
(autocontenido: sin servidor, sin internet — se abre con doble clic y se
puede enviar por correo).

Uso:  python tools/make_executive_report.py
"""
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import portfolio as pf

OUT = ROOT / "entregables" / "reportes" / "Reporte Ejecutivo - CFE Brain OS.html"
MES = pf.MES

# Caso GEPP — cifras ARCHIVADAS (prefactibilidad best-case, permisos asumidos,
# contraprestacion cero). Fuente: wiki/analyses/2026-06-10-gepp-portfolio-project-check.md
GEPP = dict(
    cliente="GEPP (embotellador PepsiCo México)",
    alcance="4 sitios problemáticos de un portafolio de ~30 servicios · 411.7 GWh/año · $1,205M/año",
    bruto=56_930_000, neto1=53_920_000, capex=275_600_000,
    tir=0.242, payback="4.6 años", npv=296_800_000,
    pv_kwp=14_760, bess_kw=3_540, bess_kwh=7_080,
    sitios=[
        ("Ixtlahuacán", 2530, "850/1,700", 52.7, 8.54, "20.4%", "5.5a"),
        ("Acapulco", 1020, "320/640", 21.0, 5.55, "31.7%", "3.5a"),
        ("Cancún", 700, "— (umbral)", 9.5, 2.88, "35.8%", "3.1a"),
        ("Proplasa PR1", 1860, "360/720", 32.7, 6.43, "24.3%", "4.6a"),
        ("Proplasa PR2", 5220, "1,220/2,440", 96.6, 18.43, "23.6%", "4.7a"),
        ("Proplasa TAP", 3430, "790/1,580", 63.2, 12.09, "23.7%", "4.7a"),
    ],
)

mxn = lambda x: f"${x:,.0f}"
mxnM = lambda x: f"${x/1e6:,.1f} M"
pcts = lambda x: f"{100*x:,.1f}%"
LCOL = {"pv": "#fbbf24", "bess": "#60a5fa", "fp": "#a78bfa"}
LNAME = {"pv": "PV (energía)", "bess": "BESS (demanda + arbitraje)", "fp": "Corrección FP"}

CSS = """
:root{--bg0:#070b14;--bg1:#0b1120;--card:rgba(20,28,46,.78);--line:#1f2b44;--line2:#2c3c5e;
--txt:#e9eef7;--mut:#8b9bb4;--acc:#34d399;--acc2:#10b981;--amber:#fbbf24;--err:#f87171;
--info:#60a5fa;--violet:#a78bfa}
*{box-sizing:border-box;margin:0;padding:0}
body{font:14px/1.6 "Segoe UI",system-ui,sans-serif;color:var(--txt);background:var(--bg0);padding:0 0 60px}
body::before{content:"";position:fixed;inset:0;z-index:-1;background:
radial-gradient(1000px 500px at 20% -10%,rgba(52,211,153,.13),transparent 60%),
radial-gradient(900px 450px at 95% 5%,rgba(96,165,250,.10),transparent 55%),
linear-gradient(180deg,var(--bg0),var(--bg1))}
.wrap{max-width:1080px;margin:auto;padding:0 26px}
.hero{padding:56px 0 18px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.bolt{width:60px;height:60px;border-radius:17px;display:grid;place-items:center;font-size:29px;
background:linear-gradient(135deg,#0e2e22,#123a2b);border:1px solid rgba(52,211,153,.45);
box-shadow:0 0 36px rgba(52,211,153,.3)}
h1{font-size:33px;font-weight:800;letter-spacing:-.03em;
background:linear-gradient(90deg,#e9eef7 20%,#34d399 75%);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--mut);font-size:13.5px;margin-top:5px;max-width:680px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 6px}
.chip{font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:4px 12px;
border-radius:99px;border:1px solid rgba(52,211,153,.45);color:var(--acc)}
.chip.b{border-color:rgba(96,165,250,.45);color:var(--info)}
.chip.a{border-color:rgba(251,191,36,.45);color:var(--amber)}
h2{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--mut);
margin:38px 0 16px;display:flex;align-items:center;gap:12px}
h2::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line2),transparent)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:14px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:linear-gradient(90deg,var(--c,#34d399),transparent)}
.kpi h3{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.09em;font-weight:600}
.kpi .v{font-size:27px;font-weight:800;margin-top:6px;letter-spacing:-.02em;color:var(--c,#34d399)}
.kpi .d{font-size:11.5px;color:var(--mut);margin-top:3px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;margin-bottom:16px}
.panel h3{font-size:16.5px;font-weight:750;letter-spacing:-.01em}
.rpu{font:11.5px ui-monospace,Consolas,monospace;color:#9fd4ff;background:#0a101d;
border:1px solid var(--line);border-radius:8px;padding:3px 10px}
.badge{font-size:9.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:3px 9px;
border-radius:99px;border:1px solid var(--line2);color:var(--mut)}
.badge.ok{color:var(--acc);border-color:rgba(52,211,153,.5)}
.badge.warn{color:var(--amber);border-color:rgba(251,191,36,.5)}
.badge.info{color:var(--info);border-color:rgba(96,165,250,.5)}
.badges{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}
.head{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;flex-wrap:wrap}
.big{text-align:right}.big .v{font-size:24px;font-weight:800;color:var(--acc)}.big .d{font-size:11.5px;color:var(--mut)}
.cells{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:15px}
.cell{background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:12px;padding:10px 13px}
.cell h4{font-size:10px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em;font-weight:600}
.cell .v{font-size:16px;font-weight:750;margin-top:3px}
.cell .v small{font-size:11px;color:var(--mut);font-weight:500}
.cell.hi{border-color:rgba(52,211,153,.45);background:rgba(52,211,153,.05)}.cell.hi .v{color:var(--acc)}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:12px}
th{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.07em;text-align:right;
padding:8px 10px;border-bottom:1px solid var(--line2)}
th:first-child,td:first-child{text-align:left}
td{padding:8px 10px;border-bottom:1px solid rgba(31,43,68,.55);text-align:right}
tr:last-child td{border-bottom:none}
tr.tot td{font-weight:800;color:var(--acc);border-top:1px solid var(--line2)}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px}
.step{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.step .n{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;font-weight:800;font-size:13px;
background:rgba(52,211,153,.12);color:var(--acc);border:1px solid rgba(52,211,153,.4);margin-bottom:9px}
.step b{font-size:13px}.step p{font-size:11.5px;color:var(--mut);margin-top:4px}
ol.rules{margin-left:18px;display:flex;flex-direction:column;gap:8px;font-size:13px}
ol.rules li::marker{color:var(--acc);font-weight:700}
.note{font-size:11.5px;color:var(--mut);margin-top:10px;line-height:1.6}
.foot{color:var(--mut);font-size:11px;margin-top:40px;line-height:1.8;text-align:center}
svg{display:block;width:100%;height:auto}
@media print{body{background:#fff;color:#111}.panel,.kpi,.step{border-color:#ccc;background:#fff}}
"""


def svg_levers(levers: dict, width=640) -> str:
    total = sum(levers.values()) or 1
    x, parts = 0.0, []
    for k in ("pv", "bess", "fp"):
        w = width * levers[k] / total
        if w > 0.5:
            parts.append(f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="14" rx="4" fill="{LCOL[k]}"/>')
        x += w
    leg = " · ".join(f'<tspan fill="{LCOL[k]}">{LNAME[k].split(" (")[0]} {mxn(v)}</tspan>'
                     for k, v in levers.items())
    return (f'<svg viewBox="0 0 {width} 38" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}'
            f'<text x="0" y="32" font-size="11" fill="#8b9bb4" font-family="Segoe UI">{leg}</text></svg>')


def svg_monthly(services: list, width=1020, height=210) -> str:
    agg = {}
    for s in services:
        for r in s["monthly"]:
            k = (r["year"], r["month"])
            a = agg.setdefault(k, dict(antes=0.0, ahorro=0.0, mes=r["mes"]))
            a["antes"] += r["antes"]
            a["ahorro"] += r["hibrido"] + (r.get("fp") or 0.0)
    keys = sorted(agg)
    if not keys:
        return ""
    padl, padb, padt = 52, 24, 8
    mx = max(agg[k]["antes"] for k in keys) or 1
    bw = (width - padl - 10) / len(keys)
    out = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
    for i in range(4):
        v = mx * i / 3
        y = height - padb - (height - padb - padt) * i / 3
        out.append(f'<line x1="{padl}" y1="{y:.1f}" x2="{width-6}" y2="{y:.1f}" stroke="rgba(44,60,94,.5)"/>')
        out.append(f'<text x="{padl-6}" y="{y+3:.1f}" font-size="9.5" fill="#8b9bb4" text-anchor="end" font-family="Segoe UI">{v/1e6:.1f}M</text>')
    for i, k in enumerate(keys):
        a = agg[k]
        x = padl + i * bw
        hA = (height - padb - padt) * a["antes"] / mx
        hD = (height - padb - padt) * (a["antes"] - a["ahorro"]) / mx
        out.append(f'<rect x="{x+bw*.14:.1f}" y="{height-padb-hA:.1f}" width="{bw*.33:.1f}" height="{hA:.1f}" rx="2" fill="#3a4a6b"/>')
        out.append(f'<rect x="{x+bw*.52:.1f}" y="{height-padb-hD:.1f}" width="{bw*.33:.1f}" height="{hD:.1f}" rx="2" fill="#34d399"/>')
        if bw > 24:
            out.append(f'<text x="{x+bw/2:.1f}" y="{height-7}" font-size="9.5" fill="#8b9bb4" text-anchor="middle" font-family="Segoe UI">{a["mes"]}</text>')
    out.append("</svg>")
    return "".join(out)


def build() -> str:
    data = pf.run()
    ag = data["aggregate"]
    ok = [s for s in data["services"] if s.get("status") == "ok"]
    hoy = date.today().isoformat()
    opp_total = ag["total"] + GEPP["bruto"]

    H = []
    H.append(f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Reporte Ejecutivo — CFE Brain OS</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head><body><div class="wrap">
<div class="hero"><div class="bolt">⚡</div><div>
<h1>CFE Brain OS</h1>
<div class="sub">Sistema operativo determinístico para deals de energía — PPA · solar · baterías bajo regulación
mexicana (CFE/LSE/CNE). Los números salen de un motor validado al centavo; la lógica, de un wiki de fuentes
primarias. Nunca de memoria.</div>
<div class="chips"><span class="chip">motor golden-validado · 18/18 checks peso-exactos</span>
<span class="chip b">corre 100% local — los recibos no salen de la máquina</span>
<span class="chip a">reporte generado {hoy}</span></div>
</div></div>""")

    # ---- resumen ejecutivo
    H.append(f"""<h2>Resumen ejecutivo</h2><div class="kpis">
<div class="kpi" style="--c:#34d399"><h3>Oportunidad identificada</h3><div class="v">{mxnM(opp_total)}/año</div>
<div class="d">ahorro anual bruto, cartera + pipeline GEPP</div></div>
<div class="kpi" style="--c:#e9eef7"><h3>Cartera con recibos</h3><div class="v" style="color:var(--txt)">{mxnM(ag["total"])}/año</div>
<div class="d">{ag["ok"]} servicios · {pcts(ag["pct"])} del bill · grado motor</div></div>
<div class="kpi" style="--c:#fbbf24"><h3>Pipeline GEPP</h3><div class="v" style="color:var(--amber)">{mxnM(GEPP["bruto"])}/año</div>
<div class="d">4 sitios · prefactibilidad best-case · TIR {pcts(GEPP["tir"])}</div></div>
<div class="kpi" style="--c:#60a5fa"><h3>Energía analizada</h3><div class="v" style="color:var(--info)">{(ag["kwh_total"]/1e6 + 24.9):,.0f} GWh/año</div>
<div class="d">{ag["kwh_total"]/1e6:,.1f} GWh con recibos + 24.9 GWh GEPP modelado</div></div>
</div>
<p class="note">Niveles de hecho: la cartera con recibos es <b>derivada del motor</b> sobre recibos CFE reales validados
(la aritmética interna de cada recibo cuadra contra el total impreso antes de calcular nada). El caso GEPP es
<b>prefactibilidad archivada</b> — permisos asumidos, sin datos de medidor 15-min. Nada en este reporte viene de memoria de un LLM.</p>""")

    # ---- cartera
    H.append('<h2>Cartera con recibos — números del motor, al centavo</h2>')
    for s in ok:
        fp_badge = '<span class="badge ok">FP activa</span>' if s["fp_correction"] else ""
        H.append(f"""<div class="panel"><div class="head"><div>
<h3>{s["site"] or s["municipio"] or s["rpu"]}</h3>
<div class="badges"><span class="rpu">{s["rpu"]}</span><span class="badge info">{s["division"]}</span>
<span class="badge ok">{s["months"]} meses · recibos cuadran</span>{fp_badge}
<span class="badge">palanca nº1: {s["best_lever"].upper()}</span></div></div>
<div class="big"><div class="v">{mxn(s["total"])}/año</div>
<div class="d">{pcts(s["pct"])} del bill · neto de disponibilidad {mxn(s["neto_disp"])}</div></div></div>
<div style="margin-top:14px">{svg_levers(s["levers"])}</div>
<div class="cells">
<div class="cell"><h4>Bill antes</h4><div class="v">{mxnM(s["antes"])}<small>/año</small></div></div>
<div class="cell"><h4>Solo PV</h4><div class="v">{mxnM(s["pv_only"])}</div></div>
<div class="cell"><h4>Solo BESS</h4><div class="v">{mxnM(s["bess_only"])}</div></div>
<div class="cell hi"><h4>Híbrido{" + FP" if s["fp_correction"] else ""}</h4><div class="v">{mxnM(s["total"])}</div></div>
<div class="cell"><h4>Sistema</h4><div class="v">{s["kwp"]:,.0f} kWp <small>+ {s["bess_kwh"]:,.0f} kWh</small></div></div>
<div class="cell"><h4>CAPEX</h4><div class="v">{mxnM(s["capex"] or 0)}</div></div>
<div class="cell"><h4>TIR proyecto</h4><div class="v">{pcts(s["tir_proyecto"]) if s["tir_proyecto"] is not None else "—"}</div></div>
<div class="cell"><h4>Payback</h4><div class="v">{str(s["payback"]) + " años" if s["payback"] is not None else "—"}</div></div>
</div></div>""")

    H.append(f"""<div class="panel"><h3 style="font-size:14px">Bill mensual agregado — antes <span style="color:#3a4a6b">■</span>
 vs después <span style="color:#34d399">■</span> (híbrido + FP)</h3>{svg_monthly(ok)}</div>""")

    # ---- GEPP
    g = GEPP
    H.append(f"""<h2>Pipeline — caso {g["cliente"]}</h2>
<div class="panel"><div class="head"><div><h3>{g["alcance"]}</h3>
<div class="badges"><span class="badge warn">prefactibilidad best-case · permisos asumidos · contraprestación cero</span>
<span class="badge info">análisis archivado 2026-06-10/11</span></div></div>
<div class="big"><div class="v">{mxnM(g["bruto"])}/año</div>
<div class="d">bruto año-0 · neto año-1 {mxnM(g["neto1"])} · TIR {pcts(g["tir"])} · payback {g["payback"]} · VPN@12% {mxnM(g["npv"])}</div></div></div>
<table><tr><th>Sitio</th><th>PV kWp</th><th>BESS kW/kWh</th><th>CAPEX $M</th><th>Neto año-1 $M</th><th>TIR</th><th>Payback</th></tr>""")
    for row in g["sitios"]:
        H.append(f"<tr><td>{row[0]}</td><td>{row[1]:,}</td><td>{row[2]}</td><td>{row[3]:,.1f}</td>"
                 f"<td>{row[4]:,.2f}</td><td>{row[5]}</td><td>{row[6]}</td></tr>")
    H.append(f"""<tr class="tot"><td>Portafolio</td><td>{g["pv_kwp"]:,}</td><td>{g["bess_kw"]:,} / {g["bess_kwh"]:,}</td>
<td>{g["capex"]/1e6:,.1f}</td><td>{g["neto1"]/1e6:,.2f}</td><td>{pcts(g["tir"])}</td><td>{g["payback"]}</td></tr></table>
<p class="note">Modelo financiero grado-motor sobre insumos grado-Excel: PV valuado a tarifa intermedia, BESS con tope
de umbral mes a mes, penalización de arbitraje calibrada al run de Tototlán. Lo que mueve estos números: datos de
medidor 15-min (paros de fin de semana), superficie real en Proplasa (~62k m²), y la coexistencia regulatoria en
Ixtlahuacán. Detalle completo en el wiki: análisis 2026-06-10 y recomendación por sitio 2026-06-11.</p></div>""")

    # ---- cómo funciona
    H.append("""<h2>Cómo funciona — del recibo al deal</h2><div class="steps">
<div class="step"><div class="n">1</div><b>Recibos CFE</b><p>PDF o CFDI XML — descargados del portal CFE o arrastrados al cotizador. Nunca se modifican.</p></div>
<div class="step"><div class="n">2</div><b>Validación</b><p>La aritmética de cada recibo debe cuadrar contra el total impreso (±0.5%). Si no cuadra, todo se detiene.</p></div>
<div class="step"><div class="n">3</div><b>Motor determinístico</b><p>Tarifa, umbral de demanda, horarios punta, régimen regulatorio (línea 0.7 MW). Mismo número en Excel, CLI y webapp.</p></div>
<div class="step"><div class="n">4</div><b>Escenarios</b><p>PV solo · BESS solo · Híbrido + corrección FP como palanca separada. TIR de proyecto y de financiador, etiquetadas.</p></div>
<div class="step"><div class="n">5</div><b>Deal</b><p>El pricer resuelve la tarifa PPA para la TIR objetivo del financiador — con la viabilidad del cliente como restricción. Propuesta es-MX lista para enviar.</p></div>
</div>""")

    H.append("""<div class="panel" style="margin-top:16px"><h3 style="font-size:14px;margin-bottom:12px">Reglas que no se negocian</h3>
<ol class="rules">
<li><b>Recibo que no cuadra detiene todo</b> — probable error CFE; se reporta, no se construye encima.</li>
<li><b>Golden test sagrado</b> — 18 verificaciones peso-exactas contra un caso real auditado, antes y después de cada cambio al motor.</li>
<li><b>TIR proyecto ≠ TIR financiador</b> — una dice si vale la pena construir; la otra se resuelve con el pricer del PPA.</li>
<li><b>Corrección FP = palanca separada</b> — suele ser el ROI más alto del stack y es ortogonal a PV/BESS.</li>
<li><b>Niveles de hecho en cada cifra</b> — fuente primaria / derivado del motor / supuesto. Sin excepciones.</li>
</ol></div>""")

    # ---- roadmap
    H.append("""<h2>Qué sigue</h2><div class="steps">
<div class="step"><div class="n">→</div><b>Datos 15-min (medidor HM)</b><p>Reemplaza curvas supuestas por carga medida: sizing y shave de punta pasan de prefactibilidad a bancable. La mejora #1.</p></div>
<div class="step"><div class="n">→</div><b>Más servicios al portafolio</b><p>Cada carpeta nueva de recibos en raw/bills/ aparece sola en la vista portafolio — el costo marginal de analizar un servicio más es ~cero.</p></div>
<div class="step"><div class="n">→</div><b>GDMTO/PDBT con parser</b><p>El modelo de tarifa plana existe; falta el primer recibo real de esas tarifas para automatizar la captura.</p></div>
</div>""")

    H.append(f"""<div class="foot">CFE Brain OS · reporte generado {hoy} por <b>tools/make_executive_report.py</b> —
regenerable en cualquier momento con un comando; las cifras de cartera se recalculan del motor en cada corrida.<br>
Bill ANTES = MEM + bonificación FP (sin IVA). Ahorros brutos comparables a Excel; netos de disponibilidad mostrados junto a cada cifra.<br>
Análisis regulatorio, no opinión legal.</div>
</div></body></html>""")
    return "".join(H)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    OUT.write_text(html, encoding="utf-8")
    print(f"OK -> {OUT}  ({len(html):,} chars)")


if __name__ == "__main__":
    main()
