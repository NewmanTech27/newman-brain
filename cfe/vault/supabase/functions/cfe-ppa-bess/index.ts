// CFE Brain — PPA+BESS solution engine as a Supabase Edge Function.
//
// Ports the deterministic logic behind the GEPP projects (calc_core.py / load_curves.py /
// cfe_savings) — the same engine that produced "GEPP - Propuesta PV+BESS 4 Sitios rev3 -
// BESS verano 2h". Verified bit-for-bit against the Python reference (4,536 fields, 0 diff).
//
// POST JSON { mode, ... }:
//   mode "compute"    { inputs, bills }          -> monthly + annual + regimen + finance (PV/BESS/Hibrido)
//   mode "size-bess"  { bills, hours?, dod?, rte? } -> verano-2h BESS size (kW, kWh)
//   mode "gepp"       { pv_kwp?: {slug:kWp}, fp_correction?: {slug:bool} }
//                        -> runs the seeded GEPP 4-sitios rev3 (verano-2h BESS) design,
//                           per-service + Proplasa rollup + portfolio totals
//   GET / -> this usage help
//
// Numbers-only, deterministic; no external calls, no secrets.

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { compute, size_bess_verano } from "./engine.js";
import { GEPP } from "./gepp_data.js";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });

const USAGE = {
  service: "cfe-ppa-bess",
  description: "Deterministic CFE GDMTH PV+BESS savings & PPA engine (calc_core port). Verified vs the Python golden engine.",
  modes: {
    compute: {
      body: { mode: "compute", inputs: "calc_core inputs (division, giro, kwp, yield_monthly, bess_kw, bess_kwh, ppa, comision, ...)", bills: "array of monthly bills (cfe_savings.extract schema)" },
      returns: "{ inputs, monthly[], validacion[], annual, regimen, finance:{PV,BESS,Hibrido} }",
    },
    "size-bess": {
      body: { mode: "size-bess", bills: "array", hours: "block hours (default 2 = verano)", dod: "default 0.96", rte: "default 0.96" },
      returns: "{ bess_kw, bess_kwh, avg_summer_punta_kw, basis }",
    },
    gepp: {
      body: { mode: "gepp", pv_kwp: "optional {slug:kWp} to layer PV", fp_correction: "optional {slug:bool}" },
      note: "Seeded with GEPP 4-sitios rev3 (BESS verano 2h). Default is BESS-only (PV off) unless pv_kwp given.",
      services: Object.keys(GEPP),
    },
  },
};

function money(res: any) {
  const a = res.annual;
  return {
    bill_antes_anual: a.antes,
    ahorro_pv_only: a.pv_only,
    ahorro_bess_only: a.bess_only,
    ahorro_hibrido: a.hibrido,
    ahorro_hibrido_pct: a.antes ? a.hibrido / a.antes : 0,
    neto_disponibilidad: a.neto_disp,
    desglose: { ah_pv: a.ah_pv, dem_pv: a.dem_pv, dem_bess: a.dem_bess_h, arbitraje: a.arb, fp_cargo: a.fp_cargo },
    meses: a.meses, anualizado: a.anualizado,
  };
}

function runGepp(body: any) {
  const pv_kwp = body.pv_kwp || {};
  const fp = body.fp_correction || {};
  const services: Record<string, any> = {};
  const proplasa_slugs: string[] = [];
  let port = { antes: 0, hibrido: 0, capex: 0, gen: 0 };

  for (const [slug, d] of Object.entries(GEPP) as [string, any][]) {
    const m = d.meta;
    const kwp = Number(pv_kwp[slug] ?? 0);
    const ym: Record<number, number> = {};
    for (let mo = 1; mo <= 12; mo++) ym[mo] = m.yield_kwh_kwp_yr / 12.0;
    const inputs = {
      cliente: "gepp", rpu: d.inputs.rpu, municipio: d.inputs.municipio,
      division: d.inputs.division || "SIN", giro: d.inputs.giro || "Industrial 24/7",
      demanda_contratada: d.inputs.demanda_contratada || 0,
      kwp, yield_monthly: ym, epc_usd_wp: 0.65, ppa: 1.2, ppa_yrs: 15,
      bess_kw: m.bess_kw, bess_kwh: m.bess_kwh, epc_bess: 280.0, comision: 0.5,
      fx: 17.55, esc_cfe: 0.05, esc_ppa: 0.05, falla_meses: 2,
      bess_yrs: 15, pv_degr: 0.005, bess_degr: 0.0125, dod: 0.96, rte: 0.96,
      wacc: 0.12, horizon: 20, fp_correction: !!fp[slug],
    };
    const res = compute(inputs, d.bills);
    const scen = kwp > 0 ? "Hibrido" : "BESS";
    const finance = res.finance[scen];
    services[slug] = {
      nombre: m.nombre, site: m.site,
      diseno: { pv_kwp: kwp, bess_kw: m.bess_kw, bess_kwh: m.bess_kwh, regimen: res.regimen.regimen },
      resumen: money(res),
      finance: { escenario: scen, ...finance },
      alerts: res.regimen.alerts,
    };
    if (m.proplasa) proplasa_slugs.push(slug);
    port.antes += res.annual.antes;
    port.hibrido += res.annual.hibrido;
    port.capex += finance.capex;
    port.gen += res.annual.gen;
  }

  const rollup = (slugs: string[]) => slugs.reduce((acc, s) => {
    const r = services[s].resumen; const f = services[s].finance;
    acc.antes += r.bill_antes_anual; acc.ahorro += r.ahorro_hibrido; acc.capex += f.capex;
    acc.bess_kw += services[s].diseno.bess_kw; acc.bess_kwh += services[s].diseno.bess_kwh;
    return acc;
  }, { antes: 0, ahorro: 0, capex: 0, bess_kw: 0, bess_kwh: 0 });

  return {
    proposal: "GEPP - Propuesta PV+BESS 4 Sitios (2026-07) rev3 - BESS verano 2h",
    doctrine: "BESS 0.5C / 2h (energía = 2h × demanda punta verano); dispatch punta weekdays; medición neta <0.7 MWp / autoconsumo ≥0.7 MWp.",
    services,
    proplasa_rollup: proplasa_slugs.length ? rollup(proplasa_slugs) : null,
    portfolio: {
      sitios: 4, servicios: Object.keys(GEPP).length,
      bill_antes_anual: port.antes,
      ahorro_anual: port.hibrido,
      ahorro_pct: port.antes ? port.hibrido / port.antes : 0,
      capex_total_mxn: port.capex,
      pv_gen_anual_kwh: port.gen,
    },
  };
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method === "GET") return json(USAGE);
  if (req.method !== "POST") return json({ error: "Use POST with {mode,...} or GET for usage." }, 405);

  let body: any;
  try { body = await req.json(); } catch { return json({ error: "Invalid JSON body" }, 400); }
  const mode = body?.mode;

  try {
    if (mode === "compute") {
      if (!body.inputs || !Array.isArray(body.bills)) return json({ error: "compute requires {inputs, bills[]}" }, 400);
      return json(compute(body.inputs, body.bills));
    }
    if (mode === "size-bess") {
      if (!Array.isArray(body.bills)) return json({ error: "size-bess requires {bills[]}" }, 400);
      return json(size_bess_verano(body.bills, { hours: body.hours, dod: body.dod, rte: body.rte }));
    }
    if (mode === "gepp") return json(runGepp(body));
    return json({ error: `Unknown mode '${mode}'. See GET / for usage.`, usage: USAGE }, 400);
  } catch (e) {
    return json({ error: String(e?.message || e) }, 500);
  }
});
