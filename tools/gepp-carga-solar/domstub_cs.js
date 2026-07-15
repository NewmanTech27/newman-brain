// DOM-stub runtime test for the GEPP v8 (Carga Solar) deck script.
// Every renderer x every site x both options x both seasons + portfolio + the new
// renderSupMas, then greps captured HTML for NaN/undefined leaks, asserts MODEL
// savings numbers match gepp_data_cs.json exactly, and coverage = gen/consumo.
const fs = require('fs');
const src = fs.readFileSync('cs_script.js', 'utf8');
const JSON_DATA = JSON.parse(fs.readFileSync('gepp_data_cs.json', 'utf8'));

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
  ' renderCobertura, renderSupMas, R4: MODEL.resumen4, RP: MODEL.resumenP, MODEL,' +
  ' renderDesp: (typeof renderDesp!=="undefined"?renderDesp:null),' +
  ' setOP: (v)=>{OP=v;}, setSeason: (s)=>{ if (typeof despSeason!=="undefined") despSeason=s; } };');

let api;
try { api = fn(document, sandbox.window, sandbox.innerWidth, sandbox.innerHeight, sandbox.addEventListener, sandbox.matchMedia); }
catch (e) { console.error('RUNTIME FAIL on load:', e.message); console.error(e.stack.split('\n').slice(0,5).join('\n')); process.exit(1); }

const sites = ['ixt','aca','can','pro','pr1','pr2','tap'];
const veinteKeys = [...sites, 'all'];
let runs = 0;
for (const op of [0,1]) {
  api.setOP(op);
  try { api.renderStatics(); runs++; } catch(e){ console.error(`FAIL statics op${op}:`, e.message); process.exit(1); }
  try { api.renderCobertura(); runs++; } catch(e){ console.error(`FAIL cobertura op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
  for (const k of sites) {
    for (const [name, f] of [['consumo', api.renderConsumo], ['sol', api.renderSol], ['supmas', api.renderSupMas]]) {
      try { f(k); runs++; } catch(e){ console.error(`FAIL ${name} ${k} op${op}:`, e.message); console.error(e.stack.split('\n').slice(0,4).join('\n')); process.exit(1); }
    }
    if (api.renderDesp) for (const season of ['inv','ver']) {
      api.setSeason(season);
      try { api.renderDesp(k); runs++; } catch(e){ console.error(`FAIL desp ${k} op${op} ${season}:`, e.message); process.exit(1); }
    }
  }
  for (const k of veinteKeys) {
    try { api.renderVeinte(k); runs++; } catch(e){ console.error(`FAIL veinte ${k} op${op}:`, e.message); process.exit(1); }
  }
}
console.log('renderer runs OK:', runs);

// ---- ASSERT: MODEL savings numbers == gepp_data_cs.json exactly ----
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
console.log(mismatch? `MODEL/JSON MISMATCH: ${mismatch}` : 'MODEL == gepp_data_cs.json (savings numbers exact)');

// ---- ASSERT: coverage = gen/consumo within 0.1pp of reference ----
const S = api.S, R4 = api.R4;
const CONS = {ixt:22171919, aca:8906204, can:4752232, pro: S.pr1.ctotal_tot + S.pr2.ctotal_tot + S.tap.ctotal_tot};
const totCons = CONS.ixt + CONS.aca + CONS.can + CONS.pro;
const km = {"Ixtlahuacán":"ixt","Acapulco":"aca","Cancún":"can","Proplasa":"pro"};
const REF = { ixt:41.6, aca:36.7, can:40.1, pro:6.9, portfolio:16.3 };  // new design (Op1)
const rows1 = R4.rows.filter(r=>r.op && r.op.startsWith('Op1') && km[r.site]);
let covFail = 0;
rows1.forEach(r=>{
  const k = km[r.site];
  const cov = r.gen/CONS[k]*100;
  const d = Math.abs(cov - REF[k]);
  const ok = d <= 0.1; if(!ok) covFail++;
  console.log(`  cobertura ${k} Op1 = ${cov.toFixed(2)}%  (ref ${REF[k]}%, Δ${d.toFixed(3)}pp) ${ok?'OK':'FAIL'}`);
});
const covP = R4.portfolio["Suma Opción 1"].gen/totCons*100;
{ const d=Math.abs(covP-REF.portfolio); const ok=d<=0.1; if(!ok)covFail++;
  console.log(`  cobertura portafolio Op1 = ${covP.toFixed(2)}%  (ref ${REF.portfolio}%, Δ${d.toFixed(3)}pp) ${ok?'OK':'FAIL'}`); }
const rows2 = R4.rows.filter(r=>r.op && r.op.startsWith('Op2') && km[r.site]);
rows2.forEach(r=>{ const c=r.gen/CONS[km[r.site]]*100; if(!isFinite(c)){ console.error('Op2 coverage NaN',r.site); covFail++; } });
console.log(covFail ? `COVERAGE ASSERT FAIL: ${covFail}` : 'COVERAGE ASSERT OK (Op1 within 0.1pp; Op2 finite)');

// ---- leak grep ----
let leaks = 0;
for (const [id, html] of Object.entries(captured)) {
  for (const bad of ['NaN', 'undefined', 'null,', '>null<', '$null', 'Infinity']) {
    if (html.includes(bad)) { leaks++; console.error(`LEAK "${bad}" in #${id}:`, html.substr(Math.max(0, html.indexOf(bad)-70), 150).replace(/\n/g,' ')); }
  }
}
console.log(leaks ? `LEAKS: ${leaks}` : 'NO NaN/undefined LEAKS in ' + Object.keys(captured).length + ' captured elements');
process.exit((leaks || covFail || mismatch) ? 1 : 0);
