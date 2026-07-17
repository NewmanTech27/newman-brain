// solar-charge parity — JS side (issue #5).
// Drives supabase/functions/cfe-ppa-bess/engine.js on the GEPP fixture built by
// run_parity.py and emits everything the Python side diffs:
//   unit    solar_charge_split() on the EXACT args dispatch_cs.sim_month uses
//           (book dias_punta, book charge energy N/RTE, no exced cap)
//   on      compute(solar_charge:true)  — monthly dispatch + annual bonus + TIR
//   off     compute(solar_charge:false) minus the inputs echo (golden compare)
//   default compute() with no solar_charge key (must equal off)
//   bridge  solar_charge_split() re-run with the engine's OWN calendar wd /
//           desc/rte charge energy / row exced — must equal compute()'s
//           carga_solar exactly, proving the prototype↔engine gap is ONLY the
//           punta-day basis (calendar punta_weekdays vs book billing-period
//           dias_punta), with zero unexplained residual.
//
// Usage: node run_engine.mjs <fixture.json> <out.json>
// Env:   ENGINE_JS — override engine path (used to point at the pre-flag
//        b53ad23 engine when regenerating baseline_off.json; that engine has
//        no solar_charge_split export, so unit/on/bridge are skipped).
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

  const off = eng.compute({ ...f.inputs, solar_charge: false }, f.bills);
  const inDef = { ...f.inputs }; delete inDef.solar_charge;
  const def = eng.compute(inDef, f.bills);
  site.off = stripInputs(off);
  site.default = stripInputs(def);

  if (typeof eng.solar_charge_split === "function") {
    site.unit = f.sim_args.map((a) => eng.solar_charge_split(
      f.inputs.giro, a.year, a.month, a.kwh_total, a.gen,
      f.inputs.bess_kw, a.charge_energy, a.dias_punta_book, Infinity));

    const on = eng.compute({ ...f.inputs, solar_charge: true }, f.bills);
    site.on = {
      monthly: on.monthly.map((r) => ({
        month: r.month, carga_solar: r.carga_solar, carga_base: r.carga_base,
        exced_export: r.exced_export, arb: r.arb, arb_grid: r.arb_grid,
      })),
      annual: on.annual,
      tir_financiador: on.finance.Hibrido.tir_financiador,
      tir_proyecto: on.finance.Hibrido.tir_proyecto,
    };

    const deliv = f.inputs.bess_kwh * f.inputs.dod * Math.sqrt(f.inputs.rte);
    site.bridge = on.monthly.map((r, i) => {
      const b = f.bills[i];
      const wd = eng.punta_weekdays(b.year, b.month);
      const desc = Math.min(deliv * wd, b.kwh_punta);
      const { carga_solar } = eng.solar_charge_split(
        f.inputs.giro, b.year, b.month,
        b.kwh_base + b.kwh_inter + b.kwh_punta, r.gen,
        f.inputs.bess_kw, desc / f.inputs.rte, wd, r.exced);
      return { month: r.month, wd_calendar: wd, carga_solar };
    });
  }
  out.sites[k] = site;
}
writeFileSync(outPath, JSON.stringify(out));
