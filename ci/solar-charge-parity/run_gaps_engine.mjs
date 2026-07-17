// solar-charge gaps 2/4/5 — JS side (issue #2). Sibling of run_engine.mjs.
// Drives supabase/functions/cfe-ppa-bess/engine.js on the fixture built by
// run_gaps.py and emits everything the Python side diffs:
//   period_unit  pv_period_split() on the EXACT args dispatch_cs.sim_month
//                uses — gap 5 unit parity (B1)
//   pcp_on       compute(pv_credit_periods:true) — per-period credit end to
//                end (B2); pcp_off = compute(pv_credit_periods:false) minus
//                the inputs echo (golden compare vs baseline_off.json)
//   both_on      compute(solar_charge:true, pv_credit_periods:true) — the
//                three-bucket no-double-count identity under both flags (B5)
//   scaled_unit  solar_charge_split() at BESS scales x{1,1.5,2,3} on book
//                dias_punta args — gap 2 unit parity across the size axis (B3a)
//   sizing       optimize_sizing() sweeps (free + exced-reject variants) —
//                gap 2 grid/ranking integrity + gap 4 superficie output (B3b/B4)
//
// Usage: node run_gaps_engine.mjs <fixture.json> <out.json>
import { readFileSync, writeFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const enginePath = process.env.ENGINE_JS ||
  resolve(HERE, "../../supabase/functions/cfe-ppa-bess/engine.js");
const [fixturePath, outPath] = process.argv.slice(2);

const eng = await import(new URL(`file://${resolve(enginePath)}`));
const fx = JSON.parse(readFileSync(fixturePath, "utf8"));

const stripInputs = (res) => { const { inputs, ...rest } = res; return rest; };

const out = { engine: enginePath, sites: {} };
for (const [k, f] of Object.entries(fx.sites)) {
  const site = {};

  // B1 — gap 5 unit parity args (identical to sim_month's frame)
  site.period_unit = f.sim_args.map((a) => eng.pv_period_split(
    f.inputs.giro, f.inputs.division, a.year, a.month, a.kwh_total, a.gen));

  // B2 — per-period credit end to end + flag-off inertness
  const on = eng.compute({ ...f.inputs, pv_credit_periods: true }, f.bills);
  site.pcp_on = {
    monthly: on.monthly.map((r) => ({
      month: r.month, gen: r.gen, gen_aprov: r.gen_aprov, exced: r.exced,
      ah_pv: r.ah_pv, pct_ac: r.pct_ac,
      aprov_base: r.aprov_base, aprov_inter: r.aprov_inter, aprov_punta: r.aprov_punta,
    })),
    annual: on.annual,
  };
  site.pcp_off = stripInputs(eng.compute({ ...f.inputs, pv_credit_periods: false }, f.bills));

  // B5 — both flags: three-bucket partition of gen must be exact
  const both = eng.compute({ ...f.inputs, solar_charge: true, pv_credit_periods: true }, f.bills);
  site.both_on = {
    monthly: both.monthly.map((r) => ({
      month: r.month, gen: r.gen, gen_aprov: r.gen_aprov,
      carga_solar: r.carga_solar, exced_export: r.exced_export,
    })),
    annual: both.annual,
  };

  // B3a — gap 2 unit parity across BESS scales (book dias_punta basis args)
  site.scaled_unit = f.scaled_args.map((a) => eng.solar_charge_split(
    f.inputs.giro, a.year, a.month, a.kwh_total, a.gen,
    a.bess_kw, a.charge_energy, a.dias_punta_book, Infinity));

  // B3b/B4 — sizing sweeps: free = legacy pricing (flags off), reject = the
  // rev4 stack (solar-charge dispatch + per-period credit + excess reject on
  // the exced_export basis)
  site.sizing_free = eng.optimize_sizing(f.inputs, f.bills, f.sizing_free_opts);
  site.sizing_reject = eng.optimize_sizing(
    { ...f.inputs, solar_charge: true, pv_credit_periods: true },
    f.bills, f.sizing_reject_opts);

  out.sites[k] = site;
}
writeFileSync(outPath, JSON.stringify(out));
