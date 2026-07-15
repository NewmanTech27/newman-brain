// DOM-stub runtime test for the GEPP v9 (Carga Solar + Autoconsumo Max) deck script.
// Every renderer x every site x THREE options x both seasons + portfolio + supmas,
// greps captured HTML for NaN/undefined leaks, asserts MODEL == gepp_data_nr_deck.json,
// and spot-checks Op3 coverage vs gepp_data_nr.json (the NR source of truth).
const fs = require('fs');
const src = fs.readFileSync('nr_script.js', 'utf8');
const JSON_DATA = JSON.parse(fs.readFileSync('gepp_data_nr_deck.json', 'utf8'));
const NR_SRC = JSON.parse(fs.readFileSync('gepp_data_nr.json', 'utf8'));  // reference for gate 4
const PEAK_SRC = JSON.parse(fs.readFileSync('peak_analysis.json', 'utf8')); // reference for gate 5 (¿Por qué este tamaño?)

const captured = {};
function mkEl(id) {
  const el = {
    _id: id, _inner: '', _text: '', style: {}, dataset: {}, hidden: false,
    classList: { toggle(){}, add(){}, remove(){}, contains(){ return false; } },
    addEventListener(){}, querySelectorAll(){ return []; }, querySelector(){ return null; },
    closest(){ return null; }, appendChild(){}, setAttribute(){}, getAttribute(){ return null; },
    get offsetWidth(){ return 800; }, get offsetHeight(){ return 60; },
  };
  Object.defineProperty(el, 'innerHTML', { get(){ return el._inner; },
    set(v){ el._inner = v; captured[id] = (captured[id] || '') + '\n' + v; } });
  Object.defineProperty(el, 'textContent', { get(){ return el._text; },
    set(v){ el._text = v; captured[id] = (captured[id] || '') + '\n' + v; } });
  return el;
}
const els = {};
const document = {
  getElementById(id){ if (!els[id]) els[id] = mkEl(id); return els[id]; },
  addEventListener(){}, querySelectorAll(){ return []; }, querySelector(){ return null; },
};
const sandbox = { document, window: { addEventListener(){} }, innerWidth: 1400, innerHeight: 900,
  addEventListener(){}, Intl, console, matchMedia: () => ({ matches: false, addEventListener(){} }) };

const fn = new Function('document','window','innerWidth','innerHeight','addEventListener','matchMedia', src +
  '\n;return {OPNAME, MAIN, META, S, RERENDER, renderStatics, renderConsumo, renderSol, renderVeinte,' +
  ' renderCobertura, renderSupMas, renderPeak, buildPeakCards, R4: MODEL.resumen4, RP: MODEL.resumenP, MODEL,' +
  ' renderDesp: (typeof renderDesp!=="undefined"?renderDesp:null),' +
  ' setOP: (v)=>{OP=v;}, setSeason: (s)=>{ if (typeof despSeason!=="undefined") despSeason=s; } };');

let api;
try { api = fn(document, sandbox.window, sandbox.innerWidth, sandbox.innerHeight, sandbox.addEventListener, sandbox.matchMedia); }
catch (e) { console.error('RUNTIME FAIL on load:', e.message); console.error(e.stack.split('\n').slice(0,6).join('\n')); process.exit(1); }

if (api.OPNAME.length !== 3) { console.error('OPNAME length != 3:', api.OPNAME); process.exit(1); }
console.log('OPNAME:', api.OPNAME.join(' | '));

const sites = ['ixt','aca','can','pro','pr1','pr2','tap'];
const veinteKeys = [...sites, 'all'];
let runs = 0;
for (const op of [0,1,2]) {
  api.setOP(op);
  try { api.renderStatics(); runs++; } catch(e){ console.error(`FAIL statics op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
  try { api.renderCobertura(); runs++; } catch(e){ console.error(`FAIL cobertura op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
  try { api.buildPeakCards(); runs++; } catch(e){ console.error(`FAIL peakcards op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
  for (const k of sites) {
    for (const [name, f] of [['consumo', api.renderConsumo], ['sol', api.renderSol], ['supmas', api.renderSupMas], ['peak', api.renderPeak]]) {
      try { f(k); runs++; } catch(e){ console.error(`FAIL ${name} ${k} op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
    }
    if (api.renderDesp) for (const season of ['inv','ver']) {
      api.setSeason(season);
      try { api.renderDesp(k); runs++; } catch(e){ console.error(`FAIL desp ${k} op${op} ${season}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
    }
  }
  for (const k of veinteKeys) {
    try { api.renderVeinte(k); runs++; } catch(e){ console.error(`FAIL veinte ${k} op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
  }
}
console.log('renderer runs OK:', runs);

// ---- ASSERT: MODEL savings numbers == gepp_data_nr_deck.json exactly (incl Op3 rows) ----
let mismatch = 0;
function cmpRows(modelRes, jsonRes, tag){
  const jr = jsonRes.rows;
  modelRes.rows.forEach((r,i)=>{
    const j = jr[i];
    for(const key of ['kwp','gen','neto','bruto','ppa','ppakwh','tirpv','tirbess']){
      const a=r[key], b=j[key];
      if(a==null&&b==null) continue;
      if(typeof a==='number' && typeof b==='number'){ if(Math.abs(a-b)>1e-6){ mismatch++; console.error(`  ${tag} row${i} ${key}: MODEL ${a} != JSON ${b}`);} }
      else if(a!==b){ mismatch++; console.error(`  ${tag} row${i} ${key}: MODEL ${a} != JSON ${b}`);}
    }
  });
}
cmpRows(api.R4, JSON_DATA.resumen4, 'resumen4');
cmpRows(api.RP, JSON_DATA.resumenP, 'resumenP');
const nOp3 = api.R4.rows.filter(r=>r.op&&r.op.startsWith('Op3')).length + api.RP.rows.filter(r=>r.op&&r.op.startsWith('Op3')).length;
console.log(mismatch? `MODEL/JSON MISMATCH: ${mismatch}` : `MODEL == gepp_data_nr_deck.json (savings exact); Op3 rows present: ${nOp3}`);

// ---- GATE 4: Op3 coverage in deck runtime vs gepp_data_nr.json (±0.1pp) ----
const NR = api.MODEL.nr;
let covFail = 0;
['ixt','aca','can','pro','pr1','pr2','tap'].forEach(k=>{
  const cov = NR.sites[k].gen_kwh_nr / NR.sites[k].consumo_kwh * 100;      // recomputed in-deck
  const ref = NR_SRC.sites[k].cobertura_pct_nr;
  const d = Math.abs(cov - ref); const ok = d <= 0.1; if(!ok) covFail++;
  console.log(`  Op3 cobertura ${k} = ${cov.toFixed(2)}%  (nr.json ${ref}%, Δ${d.toFixed(3)}pp) ${ok?'OK':'FAIL'}`);
});
{ const cov = NR.portfolio.gen_nr_kwh / NR.portfolio.consumo_kwh * 100;
  const ref = NR_SRC.portfolio.cobertura_pct_nr; const d = Math.abs(cov-ref); const ok=d<=0.1; if(!ok)covFail++;
  console.log(`  Op3 cobertura portafolio = ${cov.toFixed(2)}%  (nr.json ${ref}%, Δ${d.toFixed(3)}pp) ${ok?'OK':'FAIL'}`); }
// Op1 coverage regression (unchanged deck convention)
const S = api.S, R4 = api.R4;
const CONS = {ixt:22171919, aca:8906204, can:4752232, pro: S.pr1.ctotal_tot + S.pr2.ctotal_tot + S.tap.ctotal_tot};
const totCons = CONS.ixt + CONS.aca + CONS.can + CONS.pro;
const km = {"Ixtlahuacán":"ixt","Acapulco":"aca","Cancún":"can","Proplasa":"pro"};
const REF = { ixt:41.6, aca:36.7, can:40.1, pro:6.9, portfolio:16.3 };
R4.rows.filter(r=>r.op && r.op.startsWith('Op1') && km[r.site]).forEach(r=>{
  const k=km[r.site]; const cov=r.gen/CONS[k]*100; const d=Math.abs(cov-REF[k]); const ok=d<=0.1; if(!ok)covFail++;
  console.log(`  Op1 cobertura ${k} = ${cov.toFixed(2)}%  (ref ${REF[k]}%, Δ${d.toFixed(3)}pp) ${ok?'OK':'FAIL'}`);
});
console.log(covFail ? `COVERAGE ASSERT FAIL: ${covFail}` : 'COVERAGE ASSERT OK (Op3 within 0.1pp of gepp_data_nr; Op1 no regression)');

// ---- GATE 5: MODEL.peak numbers == peak_analysis.json exactly ("¿Por qué este tamaño?") ----
const PKm = api.MODEL.peak;
let pkFail = 0;
function pkEq(a, b, tag){ if(Math.abs(a-b) > 1e-6){ pkFail++; console.error(`  PEAK ${tag}: MODEL ${a} != peak_analysis ${b}`); } }
['ixt','aca','can','pro'].forEach(k=>{
  const m = PKm.sites[k], j = PEAK_SRC.sites[k];
  pkEq(m.kwp_nr, j.kwp_nr, `${k}.kwp_nr`);
  pkEq(m.sat_opt, j.saturacion_bess_pct_at_opt, `${k}.sat_opt`);
  pkEq(m.verdict.delta_van, j.bess_verdict.delta_van, `${k}.delta_van`);
  pkEq(m.verdict.bono, j.bess_verdict.bono_solar_charge, `${k}.bono`);
  pkEq(m.umbral.delta, j.umbral.delta_book_minus_true, `${k}.umbral_delta`);
  pkEq(m.peak_ah, Math.max(...j.curve.map(c=>c.ahorro_cliente_anio1)), `${k}.peak_ah`);
  pkEq(m.curve.length, j.curve.length, `${k}.curve_len`);
});
pkEq(PKm.portfolio.delta_van, PEAK_SRC.portfolio.bess_verdict.delta_van, 'portfolio.delta_van');
pkEq(PKm.portfolio.con_van, PEAK_SRC.portfolio.bess_verdict.con_bess_van, 'portfolio.con_van');
pkEq(PKm.portfolio.umbral_delta_pct, PEAK_SRC.portfolio.umbral.delta_pct, 'portfolio.umbral_delta_pct');
pkEq(PKm.portfolio.bono_total, ['ixt','aca','can','pro'].reduce((s,k)=>s+PEAK_SRC.sites[k].bess_verdict.bono_solar_charge,0), 'portfolio.bono_total');
console.log(pkFail ? `PEAK ASSERT FAIL: ${pkFail}` : `MODEL.peak == peak_analysis.json (sat/ΔVAN/bono/umbral/curve exact); portfolio ΔVAN +$${(PKm.portfolio.delta_van/1e6).toFixed(1)}M`);

// ---- leak grep ----
let leaks = 0;
for (const [id, html] of Object.entries(captured)) {
  for (const bad of ['NaN', 'undefined', 'null,', '>null<', '$null', 'Infinity']) {
    if (html.includes(bad)) { leaks++; console.error(`LEAK "${bad}" in #${id}:`, html.substr(Math.max(0, html.indexOf(bad)-70), 150).replace(/\n/g,' ')); }
  }
}
console.log(leaks ? `LEAKS: ${leaks}` : 'NO NaN/undefined LEAKS in ' + Object.keys(captured).length + ' captured elements');
process.exit((leaks || covFail || mismatch || pkFail) ? 1 : 0);
