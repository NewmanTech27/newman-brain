# -*- coding: utf-8 -*-
"""Proposal factory — bills folder in, Spanish client proposal out.

Automates the proven loop of wiki/analyses/2026-06-09-456220800389-propuesta:
  raw/bills/<RPU>/ -> validate footing -> calc_core scenarios -> (optional) PPA
  pricing at a target financier IRR -> "entregables/propuestas/Propuesta - <RPU>.md".

Doctrine honored:
  - A bill that doesn't foot (>0.5%) STOPS the run (--force to override, flagged in doc).
  - FP correction reported as a SEPARATE additive line, never blended into PV/BESS.
  - Headline = gross; net-of-availability shown alongside.
  - Fact tiers stated: recibo = primary source / ahorros = engine / yield+curva = assumption.

Usage:
  python tools/make_proposal.py raw/bills/456220800389 --giro "Industrial 24/7" \
      --kwp 700 --bess-kwh 1700 --bess-kw 850 --fp --target-irr 0.18
  (sizing flags optional — defaults to the engine's proposed sizing)

The .md is Obsidian/vault-native; ask Claude for a .docx/.pptx export when needed.
"""
from __future__ import annotations
import argparse, sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from cfe_savings import extract, sizing
import calc_core, ppa_pricer, solar_lookup

MES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
mxn = lambda x: f"${x:,.0f}"
SEV = {"error": "⛔", "warn": "⚠", "opp": "💡", "info": "ℹ"}


def build(bills_dir: str, giro="Otro", kwp=None, bess_kwh=None, bess_kw=None,
          fp=False, target_irr=None, escenario="Hibrido", cliente="",
          force=False) -> tuple[str, str, dict]:
    bills = extract.extract_folder(bills_dir)
    if not bills:
        sys.exit(f"No se encontraron recibos en {bills_dir}")
    bills = bills[-12:]
    vals = [calc_core.validate_bill(b) for b in bills]
    bad = [b["file"] if "file" in b else f"{b['year']}-{b['month']:02d}"
           for b, v in zip(bills, vals) if not v["ok"]]
    if bad and not force:
        sys.exit(f"DETENIDO: {len(bad)} recibos no cuadran (>0.5%): {bad} — "
                 f"posible error CFE o de parseo; usar --force solo si está explicado")

    import optimize_sizing
    rpu = next((b.get("servicio") for b in bills if b.get("servicio")), Path(bills_dir).name)
    cp = next((b.get("cp") for b in bills if b.get("cp")), None)
    yld = solar_lookup.cp_to_yield(cp) if cp else None
    division = (yld or {}).get("division", "SIN")
    ym, _ = optimize_sizing.resolve_yield({"yield_monthly": (yld or {}).get("monthly")}, bills)
    dcon = max((b.get("demanda_contratada") or 0 for b in bills), default=0)
    # max-NPV sweep decides PV+BESS unless explicitly given (NO 0.7 MW auto-cap)
    if kwp is None:
        opt = optimize_sizing.propose(bills, dict(giro=giro, division=division,
              yield_monthly=ym, demanda_contratada=dcon or None))["recomendado"]
        kwp, bkwh_d, bkw_d = opt["kwp"], float(opt["bess_kwh"]), float(opt["bess_kw"])
    else:
        bep = sizing.propose_bess(bills, division, autonomy_hours=None)
        bkwh_d, bkw_d = float(bep["proposed_nominal_kwh"]), float(bep["proposed_power_kw"])
    inputs = dict(
        cliente=cliente, rpu=rpu, giro=giro, division=division,
        municipio=(f"{yld['municipio']}, {yld['estado']}" if yld else ""),
        kwp=kwp,
        bess_kwh=bess_kwh if bess_kwh is not None else bkwh_d,
        bess_kw=bess_kw if bess_kw is not None else bkw_d,
        yield_monthly=ym,
        demanda_contratada=dcon,
        fp_correction=fp, escenario=escenario,
    )
    res = calc_core.compute(inputs, bills)
    ppa = (ppa_pricer.price(inputs, bills, target_irr=target_irr, solve="ppa",
                            escenario=escenario, sensitivity=False)
           if target_irr else None)
    md = _render(res, ppa, bills_dir, bad)
    return rpu, md, res


def _render(res: dict, ppa: dict | None, bills_dir: str, bad: list) -> str:
    p, a, reg = res["inputs"], res["annual"], res["regimen"]
    esc = p.get("escenario", "Hibrido")
    fin = res["finance"][esc]
    rows = res["monthly"]
    kwh_tot = sum(r["kwh_total"] for r in rows)
    fp_on = p["fp_correction"] and a["fp_cargo"] > 0
    today = date.today().isoformat()

    sav = {"Hibrido": "hibrido", "PV": "pv_only", "BESS": "bess_only"}[esc]
    tot_sav = a[sav] + (a["fp_cargo"] if fp_on else 0.0)

    L = []
    L.append(f"""---
title: "Propuesta — RPU {p['rpu']}"
type: analysis
tags: [propuesta, cliente, {esc.lower()}]
created: {today}
updated: {today}
sources: []
---

# Propuesta de Solución Energética

**Cliente / Servicio:** {p['cliente'] or 'RPU ' + p['rpu']} — {p['municipio'] or 's/municipio'}
**Tarifa:** GDMTH · división {p['division']}
**Periodo analizado:** {len(rows)} meses ({MES[rows[0]['month']]} {rows[0]['year']} – {MES[rows[-1]['month']]} {rows[-1]['year']}), recibos reales
**Documento:** preliminar · cifras sin IVA · MXN · generado por el motor determinístico CFE Brain

---

## 1. Situación actual

| Concepto | Valor anual |
|---|---|
| Consumo de energía | {kwh_tot:,.0f} kWh |
| Demanda contratada | {p['demanda_contratada']:,.0f} kW |
| **Gasto CFE (sin IVA)** | **{mxn(a['antes'])}** |""")
    if a["fp_cargo"] > 0:
        L.append(f"| Cargo por bajo factor de potencia | {mxn(a['fp_cargo'])} |")
    L.append("\n" + ("Los recibos se validaron internamente y cuadran al centavo: "
                     "**no hay errores de facturación de CFE**."
                     if not bad else
                     f"⚠ **{len(bad)} recibos NO cuadran** contra su propio total "
                     f"(posible error de CFE): {bad}. Cifras bajo reserva."))

    sistema = []
    if p["kwp"] > 0:
        sistema.append(f"Solar **{p['kwp']:,.0f} kWp**")
    if p["bess_kwh"] > 0:
        sistema.append(f"BESS **{p['bess_kwh']:,.0f} kWh / {p['bess_kw']:,.0f} kW**")
    if fp_on:
        sistema.append("**Corrección de Factor de Potencia**")
    L.append(f"""
---

## 2. Sistema recomendado

> {' + '.join(sistema)}

- **Régimen regulatorio:** {reg['regimen']}""")
    if p["kwp"] > 0:
        nota = ("al tope del esquema de Generación Distribuida (< 0.7 MW): conserva medición neta sin permiso"
                if p["kwp"] < 700 else
                f"≥ 0.7 MW → figura de autoconsumo (permiso CNE); se acredita ~{a['pct_ac_avg']:.0%} de la generación (autoconsumo instantáneo)")
        L.append(f"- **Solar {p['kwp']:,.0f} kWp** — {nota}. Generación estimada {a['gen']:,.0f} kWh/año.")
    if p["bess_kwh"] > 0:
        L.append(f"- **BESS {p['bess_kwh']:,.0f} kWh** — recorta el pico de demanda en punta (SAE-CC, sin inyección a red) + arbitraje punta→base en días hábiles.")
    if fp_on:
        L.append(f"- **Corrección de FP** — elimina el cargo recurrente de {mxn(a['fp_cargo'])}/año (banco de capacitores o el inversor del BESS).")

    L.append(f"""
---

## 3. Ahorro proyectado (Año 1, escenario {esc})

| Mes | kWh Consumo | Bill ANTES $ | Bill DESPUÉS $ | Ahorro $ | Ahorro % |
|---|---|---|---|---|---|""")
    for r in rows:
        s = r[{"Hibrido": "hibrido", "PV": "pv_only", "BESS": "bess_only"}[esc]]
        s += r["fp_cargo"] if fp_on else 0.0
        L.append(f"| {MES[r['month']]} {r['year'] % 100} | {r['kwh_total']:,.0f} | "
                 f"{r['antes']:,.0f} | {r['antes'] - s:,.0f} | {s:,.0f} | "
                 f"{s / r['antes']:.1%} |")
    L.append(f"| **TOTAL** | **{kwh_tot:,.0f}** | **{a['antes']:,.0f}** | "
             f"**{a['antes'] - tot_sav:,.0f}** | **{tot_sav:,.0f}** | "
             f"**{tot_sav / a['antes']:.1%}** |")

    L.append(f"""
**Ahorro anual estimado: {mxn(tot_sav)} ({tot_sav / a['antes']:.1%}).**

Aporte por palanca (año 0, bruto):

| Palanca | Ahorro anual |
|---|---|""")
    if p["kwp"] > 0:
        L.append(f"| Solar ({p['kwp']:,.0f} kWp) | {mxn(a['ah_pv'] + a['dem_pv'])} |")
    if p["bess_kwh"] > 0:
        L.append(f"| BESS (demanda + arbitraje) | {mxn(a['dem_bess_h'] + a['arb'])} |")
    claw = a[sav] - (a['ah_pv'] + a['dem_pv'] if p['kwp'] > 0 else 0) - \
           (a['dem_bess_h'] + a['arb'] if p['bess_kwh'] > 0 and esc == 'Hibrido' else 0)
    if abs(claw) > 1 and esc == "Hibrido":
        L.append(f"| Ajuste bonificación FP (claw-back) | {mxn(claw)} |")
    if fp_on:
        L.append(f"| Corrección de FP (palanca separada) | {mxn(a['fp_cargo'])} |")
    L.append(f"| **Total** | **{mxn(tot_sav)}** |")

    nd = a["neto_disp"][{"Hibrido": "hibrido", "PV": "pv", "BESS": "bess"}[esc]]
    L.append(f"""
*Neto de disponibilidad ({(p['falla']):.0%} BESS uptime asumido): {mxn(nd + (a['fp_cargo'] if fp_on else 0))}/año.*

---

## 4. Inversión y retorno

| Concepto | Valor |
|---|---|
| CAPEX | {mxn(fin['capex'])} |
| TIR proyecto (unlevered, 20 años) | {fin['tir_proyecto']:.1%} |
| VPN proyecto @ {p['wacc']:.0%} | {mxn(fin['vpn_proyecto'])} |
| Payback simple | {fin['payback_proyecto']} años |

*La TIR del proyecto responde "¿vale la pena construirlo?". El retorno del financiador depende de los términos del contrato (abajo).*""")

    if ppa and ppa.get("feasible"):
        c = ppa["cliente"]
        L.append(f"""
---

## 5. Opción PPA / ahorro compartido

Estructura: el financiador fondea el CAPEX y cobra una tarifa PPA por kWh solar
generado + {ppa['comision']:.0%} del ahorro BESS; el cliente no invierte.

| Término | Valor |
|---|---|
| Tarifa PPA (TIR financiador objetivo {ppa['target_irr']:.0%}) | **${ppa['ppa_rate']:.2f}/kWh** |
| Plazo / escalación | {ppa['ppa_yrs']} años / {ppa['esc_ppa']:.0%} anual |
| Tarifa CFE blend actual del cliente | ${c['tarifa_cfe_blend']:.2f}/kWh |
| Beneficio cliente año 1 (sin invertir) | {mxn(c['beneficio_anio1'])} ({c['pct_ahorro_retenido_a1']:.0%} del ahorro bruto) |
| Beneficio cliente acumulado ({p['horizon']} años) | {mxn(c['beneficio_total'])} |""")
        if c["anios_negativos"]:
            L.append(f"\n⚠ **Años con beneficio negativo para el cliente: {c['anios_negativos']}** — re-estructurar antes de ofrecer.")

    if reg["alerts"]:
        L.append("\n---\n\n## Avisos y supuestos clave\n")
        for sev, msg in reg["alerts"]:
            L.append(f"- {SEV.get(sev, '·')} {msg}")

    L.append(f"""
---

## Niveles de hecho

- **Recibos CFE** = fuente primaria (validados contra su propio total impreso).
- **Ahorros y finanzas** = derivados del motor determinístico (golden-validado).
- **Rendimiento solar municipal, curva intradía y % autoconsumo** = supuestos de
  prefactibilidad — datos medidos (Helioscope / 15-min) los harían bancables.

*Generado {today} desde `{bills_dir}` · motor CFE Brain*""")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Genera 'Propuesta - <RPU>.md' desde una carpeta de recibos")
    ap.add_argument("bills_dir")
    ap.add_argument("--cliente", default="")
    ap.add_argument("--giro", default="Otro")
    ap.add_argument("--kwp", type=float, default=None)
    ap.add_argument("--bess-kwh", type=float, default=None)
    ap.add_argument("--bess-kw", type=float, default=None)
    ap.add_argument("--escenario", choices=["PV", "BESS", "Hibrido"], default="Hibrido")
    ap.add_argument("--fp", action="store_true", help="incluir corrección FP como palanca")
    ap.add_argument("--target-irr", type=float, default=None, help="si se da, agrega sección PPA")
    ap.add_argument("--out", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    rpu, md, res = build(a.bills_dir, giro=a.giro, kwp=a.kwp, bess_kwh=a.bess_kwh,
                         bess_kw=a.bess_kw, fp=a.fp, target_irr=a.target_irr,
                         escenario=a.escenario, cliente=a.cliente, force=a.force)
    out = Path(a.out) if a.out else ROOT / "entregables" / "propuestas" / f"Propuesta - {rpu}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    an = res["annual"]
    print(f"OK -> {out}")
    print(f"   Ahorro bruto año-0 ({a.escenario}): ${an[{'Hibrido':'hibrido','PV':'pv_only','BESS':'bess_only'}[a.escenario]]:,.0f}"
          + (f" + FP ${an['fp_cargo']:,.0f}" if a.fp and an['fp_cargo'] > 0 else ""))


if __name__ == "__main__":
    main()
