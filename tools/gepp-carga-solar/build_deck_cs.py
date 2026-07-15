#!/usr/bin/env python3
"""Build the GEPP "Carga Solar" (v8) deck from the delivered gepp_v7.html.
Rerunnable. Copies v7 (never modifies it) and applies:
  1. <title> -> v8 Carga Solar
  2. MODEL splice with gepp_data_cs.json (new kWp/PPA/savings/TIR/NPV + typical_day dispatch)
  3. renderDesp targeted edits: solar-charge capsules + bands + Op2 base redistribution + copy
  4. #cobertura rewrite: solar-charge is now the ENGINE (bono/site), new coverage %s
  5. NEW section "¿Y con más superficie?" (standalone-basis per-site optimum)
  6. footer/vigencia/PROB capacity + despacho intro copy
"""
import re, json

SRC = '/home/mario/CFE Brain/work/gepp-deck/gepp_v7.html'
OUT = '/home/mario/CFE Brain/work/gepp-carga-solar/GEPP - Solucion Energetica Solar-Charge BESS.html'
DATA = '/home/mario/CFE Brain/work/gepp-carga-solar/gepp_data_cs.json'

html = open(SRC, encoding='utf-8').read()
model = open(DATA, encoding='utf-8').read()

def rep(old, new, n=1):
    global html
    c = html.count(old)
    assert c == n, f'expected {n}, found {c}: {old[:80]!r}'
    html = html.replace(old, new)

# ---- 1. MODEL splice ----
html2 = re.sub(r'const MODEL = \{.*?\};\n', 'const MODEL = ' + model + ';\n', html, count=1, flags=re.S)
assert html2 != html and 'const MODEL = ' + model[:40] in html2, 'MODEL splice failed'
html = html2

# ---- 2. title ----
rep('<title>Solución Energética v7 — GEPP · Solar + Almacenamiento · Newman Power Alliance</title>',
    '<title>GEPP — Solución Energética v8 · Carga Solar</title>')

# ---- 3. PROB capacities (design kWp) ----
rep('4.55 MWp + BESS', '5.17 MWp + BESS')
rep('1.62 MWp + BESS', '1.75 MWp + BESS')
rep('1.10 MWp + BESS', '1.27 MWp + BESS')

# ---- 4. despacho intro copy ----
rep('<p>El BESS se carga en horario base (energía barata) y se descarga de forma pareja durante el horario punta: recorta la demanda facturable y desplaza los kWh más caros del recibo.</p>',
    '<p>Primero el BESS se carga con el <strong>excedente solar</strong> del mediodía; solo el faltante se toma de la red en horario base. Luego se descarga de forma pareja durante la punta: recorta la demanda facturable y desplaza los kWh más caros del recibo.</p>')

# ---- 5. vigencia ----
rep('<li>Vigencia de la propuesta: 30 días a partir de su emisión (13 de julio de 2026).</li>',
    '<li>Vigencia de la propuesta: 30 días a partir del 14 de julio de 2026.</li>')

# ================= 6. renderDesp targeted edits =================
# 6a. Op2 base redistribution (insert after prof map)
rep('''  const prof = d.prof.map(p=>{
    const pv=p.pv*ratio;
    return {...p, pv, neta: p.carga - pv - p.chg - p.dis};
  });''',
'''  const prof = d.prof.map(p=>{
    const pv=p.pv*ratio;
    return {...p, pv, neta: p.carga - pv - p.chg - p.dis};
  });
  // Opción 2 (GD): tope 0.7 MW, sin excedente solar — la carga solar se reasigna a horario base
  if(OP){
    let solarE=0;
    prof.forEach(p=>{ if(p.chg<0 && p.pv>0){ solarE+=-p.chg; p.chg=0; } });
    const bh=prof.filter(p=>p.chg<0 && p.pv<=0);
    if(bh.length){ const per=solarE/bh.length; bh.forEach(p=>{ p.chg-=per; }); }
    prof.forEach(p=>{ p.neta=p.carga-p.pv-p.chg-p.dis; });
  }''')

# 6b. capsule labels: solar vs base
rep('''    const tag=r.t==="c"?"carga":"descarga";
    const tcol=r.t==="c"?"rgba(67,86,165,.85)":"rgba(98,21,88,.85)";''',
'''    const isSolar=r.t==="c"&&prof[r.s].pv>0;
    const tag=r.t==="c"?(isSolar?"carga solar":"carga base"):"descarga";
    const tcol=r.t==="c"?"rgba(67,86,165,.85)":"rgba(98,21,88,.85)";''')

# 6c. explanatory bands: solar (pv↔carga) + base (neta↔carga, only if faltante)
rep('''  // relleno explicativo: banda navy tenue entre carga del sitio y carga neta durante la carga nocturna
  let chgfill="",chglabel="";
  const crun=runs.filter(r=>r.t==="c").sort((a,b)=>(b.e-b.s)-(a.e-a.s))[0];
  if(crun){
    let up="",down="";
    for(let i=crun.s;i<=crun.e;i++)up+=`${i===crun.s?"M":"L"}${x(i).toFixed(1)},${y(prof[i].neta).toFixed(1)}`;
    for(let i=crun.e;i>=crun.s;i--)down+=`L${x(i).toFixed(1)},${y(prof[i].carga).toFixed(1)}`;
    chgfill=`<path class="fadein" d="${up}${down}Z" fill="rgba(67,86,165,.1)" stroke="none"/>`;
    const mi=Math.round((crun.s+crun.e)/2);
    const gy=(y(prof[mi].neta)+y(prof[mi].carga))/2;
    const gap=Math.abs(y(prof[mi].carga)-y(prof[mi].neta));
    const ly=gap>=15?gy+2.5:y(prof[mi].neta)-6;
    chglabel=`<text class="fadein" x="${x(mi).toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="7.5" letter-spacing=".5" fill="rgba(67,86,165,.9)" stroke="#F6F4F9" stroke-width="3" paint-order="stroke" stroke-linejoin="round">BESS cargando · horario base</text>`;
  }''',
'''  // relleno explicativo: banda por tipo de carga del BESS
  let chgfill="",chglabel="";
  const crunS=runs.filter(r=>r.t==="c"&&prof[r.s].pv>0).sort((a,b)=>(b.e-b.s)-(a.e-a.s))[0];
  const crunB=runs.filter(r=>r.t==="c"&&prof[r.s].pv<=0).sort((a,b)=>(b.e-b.s)-(a.e-a.s))[0];
  const band=(run,hi,lo,fill)=>{
    let up="",down="";
    for(let i=run.s;i<=run.e;i++)up+=`${i===run.s?"M":"L"}${x(i).toFixed(1)},${y(prof[i][hi]).toFixed(1)}`;
    for(let i=run.e;i>=run.s;i--)down+=`L${x(i).toFixed(1)},${y(prof[i][lo]).toFixed(1)}`;
    return `<path class="fadein" d="${up}${down}Z" fill="${fill}" stroke="none"/>`;
  };
  const bandLabel=(run,hi,lo,txt)=>{
    const mi=Math.round((run.s+run.e)/2);
    const gap=Math.abs(y(prof[mi][lo])-y(prof[mi][hi]));
    const gy=(y(prof[mi][hi])+y(prof[mi][lo]))/2;
    const ly=gap>=15?gy+2.5:y(prof[mi][hi])-6;
    return `<text class="fadein" x="${x(mi).toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="7.5" letter-spacing=".5" fill="rgba(67,86,165,.9)" stroke="#F6F4F9" stroke-width="3" paint-order="stroke" stroke-linejoin="round">${txt}</text>`;
  };
  if(crunS){ chgfill+=band(crunS,"pv","carga","rgba(67,86,165,.13)"); chglabel+=bandLabel(crunS,"pv","carga","BESS cargando · excedente solar"); }
  if(crunB){ chgfill+=band(crunB,"neta","carga","rgba(67,86,165,.1)"); if(!crunS) chglabel+=bandLabel(crunB,"neta","carga","BESS cargando · carga base"); }''')

# 6d. foot-desp copy
rep('''  document.getElementById("foot-desp").textContent =
   `${META[k].full}. Perfil sintético calibrado al recibo; recorte plano del BESS. `+
   (OP?`Curva solar escalada al tamaño GD (${fmtN.format(sysv(k,"Potencia PV (kWp DC)",1))} kWp); el BESS y su recorte de diseño son idénticos en ambas opciones. `:"")+''',
'''  document.getElementById("foot-desp").textContent =
   `${META[k].full}. Despacho modelado a partir de la curva de giro industrial escalada al recibo mensual (prefactibilidad, sin medición 15-minutal); recorte plano del BESS. `+
   (OP?`En Opción 2 (GD) el PV se dimensiona al tope de 0.7 MW: sin excedente, el BESS se carga íntegramente en horario base. `
      :`En Opción 1 el BESS se carga primero con el excedente solar del mediodía y solo el faltante en horario base. `)+''')

# ================= 7. cobertura section (HTML + JS) =================
COB_START = '<!-- 6b · COBERTURA Y RUTA DE CRECIMIENTO -->'
COB_END = '<!-- 7 · CONSUMO HOY -->'
i0 = html.index(COB_START); i1 = html.index(COB_END)
assert i0 < i1

NEW_COB_HTML = '''<!-- 6b · COBERTURA Y MOTOR DE CARGA SOLAR -->
<style>
#cobertura .eyebrow{margin-bottom:.5rem}
#cobertura h2{font-size:clamp(1.5rem,2.7vw,2rem);margin-bottom:.1rem;line-height:1.1}
#cobertura .grid2{margin-top:.5rem;gap:2.4rem}
#cobertura h3.cob-h{font-size:.76rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-60);margin-bottom:.3rem}
#cobertura table{font-size:.77rem}
#cobertura th{padding:.34rem .5rem}
#cobertura td{padding:.28rem .5rem}
#cobertura .cob-note{font-size:.78rem;color:var(--ink-60);line-height:1.35}
#cobertura .cob-note b{color:var(--ink)}
#cobertura .kpi-rail{grid-template-columns:1fr 1fr;gap:1rem 1.4rem;padding:.4rem 0;margin:.4rem 0}
#cobertura .kpi .v{font-size:clamp(1.3rem,2.2vw,1.7rem)}
#cobertura .footnote{margin-top:.4rem;font-size:.68rem}
@media print{#cobertura{padding-top:1.2vh;padding-bottom:1vh}}
</style>
<section class="page" id="cobertura">
  <div class="pagenum">Cobertura y carga solar</div>
  <div class="eyebrow">Cobertura solar y motor de carga solar · <span class="opname"></span></div>
  <h2 id="cob-headline"></h2>
  <div class="grid2" style="align-items:start">
    <div>
      <h3 class="cob-h">Cobertura solar · generación vs consumo · año 1</h3>
      <div id="cob-tabla"></div>
      <p class="cob-note" style="margin-top:.6rem"><b>Por qué este tamaño.</b> Cada kWh solar coincidente con el consumo diurno desplaza energía a tarifa plena de CFE; el diseño se amplió justo hasta donde el excedente de mediodía alimenta al BESS. Con 90–97 % de autoconsumo efectivo (autoconsumo directo + carga del BESS), el sistema está en su punto de máximo aprovechamiento por peso invertido.</p>
      <div id="cob-mas" style="margin-top:.6rem"></div>
    </div>
    <div>
      <h3 class="cob-h">El motor de carga solar</h3>
      <div id="cob-motor"></div>
    </div>
  </div>
  <p class="footnote" id="cob-foot">Perfil de consumo modelado a partir de datos mensuales (curva de giro industrial), sin medición 15-minutal; la capacidad de transformador e interconexión se confirma en visita técnica. El esquema de autoconsumo se mantiene &lt;20 MW (permiso CNE simplificado). Cifras del motor de despacho carga-solar (prefactibilidad).</p>
</section>

'''

NEW_COB_JS = r'''
// ---------- COBERTURA SOLAR Y MOTOR DE CARGA SOLAR (v8) ----------
function renderCobertura(){
  const CONS = {ixt:22171919, aca:8906204, can:4752232,
                pro: S.pr1.ctotal_tot + S.pr2.ctotal_tot + S.tap.ctotal_tot};
  const totCons = CONS.ixt + CONS.aca + CONS.can + CONS.pro;
  const SC = MODEL.solarcharge;
  const autoEff = k => { const s=SC[k]; const rem=Math.max(0,(s.exceso_kwh||0)-(s.carga_solar_kwh||0)); return (s.gen_kwh-rem)/s.gen_kwh; };
  const km = {"Ixtlahuacán":"ixt","Acapulco":"aca","Cancún":"can","Proplasa":"pro"};
  const pref = OP? "Op2":"Op1";
  const rows = R4.rows.filter(r=>r.op && r.op.startsWith(pref) && km[r.site]);
  const portP = OP? R4.portfolio["Suma Opción 2"] : R4.portfolio["Suma Opción 1"];
  const covP = portP.gen/totCons;

  document.getElementById("cob-headline").innerHTML = OP
    ? `En Opción 2, el portafolio cubre <b>${pct(covP)}</b> de su consumo con generación solar propia.`
    : `El sistema cubre <b>${pct(covP)}</b> del consumo y aprovecha casi todo lo que genera.`;

  let body="";
  rows.forEach(r=>{
    const k=km[r.site], cons=CONS[k], cov=r.gen/cons;
    const auto = OP? "—" : pct(autoEff(k));
    body += `<tr><td>${META[k].name}</td><td>${fmtN.format(r.gen)} kWh</td><td>${fmtN.format(cons)} kWh</td><td><b>${pct(cov)}</b></td><td>${auto}</td></tr>`;
  });
  const autoP = OP? "—" : pct((SC.ixt.gen_kwh*autoEff("ixt")+SC.aca.gen_kwh*autoEff("aca")+SC.can.gen_kwh*autoEff("can")+SC.pro.gen_kwh)/(SC.ixt.gen_kwh+SC.aca.gen_kwh+SC.can.gen_kwh+SC.pro.gen_kwh));
  body += `<tr class="total"><td>Portafolio</td><td>${fmtN.format(portP.gen)} kWh</td><td>${fmtN.format(totCons)} kWh</td><td><b>${pct(covP)}</b></td><td>${autoP}</td></tr>`;
  document.getElementById("cob-tabla").innerHTML =
    `<div class="tablewrap"><table><thead><tr><th>Sitio · ${OPNAME[OP].split(" — ")[0]}</th><th>Generación solar año 1</th><th>Consumo año 1</th><th>Cobertura</th><th>Autoconsumo efect.</th></tr></thead><tbody>${body}</tbody></table></div>`
    + (OP? `<p class="footnote" style="margin-top:.5rem">El autoconsumo efectivo y el motor de carga solar corresponden al esquema de Autoconsumo (Opción 1).</p>` : "");

  const motor = document.getElementById("cob-motor");
  const mas = document.getElementById("cob-mas");
  if(!OP){
    const B = k => SC[k].solar_charge_bonus_mxn;
    const bonoP = B("ixt")+B("aca")+B("can");
    const solarE = SC.ixt.carga_solar_kwh+SC.aca.carga_solar_kwh+SC.can.carga_solar_kwh;
    const mrows = [["ixt",B("ixt"),SC.ixt.pct_carga_solar],["aca",B("aca"),SC.aca.pct_carga_solar],["can",B("can"),SC.can.pct_carga_solar]]
      .map(([k,b,p])=>`<tr><td>${META[k].name}</td><td>${fmtN.format(SC[k].carga_solar_kwh)} kWh</td><td>${pct(p)}</td><td><b>+${fmt$.format(b)}</b></td></tr>`).join("");
    motor.innerHTML = `
      <span class="chip ok">Rung 2 · carga solar del BESS · motor</span>
      <p class="cob-note" style="margin:.4rem 0 .5rem">El BESS ya no se carga de la red en horario base: primero absorbe el <b>excedente solar del mediodía</b>. Ese kWh solar, que si no se vendería a CFE a valor mayorista, sustituye compra de red y libera el costo de carga base. Es salida del motor, no un supuesto.</p>
      <div class="tablewrap"><table>
        <thead><tr><th>Sitio</th><th>Carga solar / año</th><th>% de la carga</th><th>Bono carga solar</th></tr></thead>
        <tbody>${mrows}
          <tr class="total"><td>Portafolio</td><td>${fmtN.format(solarE)} kWh</td><td>—</td><td><b>+${fmt$.format(bonoP)}</b></td></tr>
        </tbody></table></div>
      <div class="kpi-rail">
        <div class="kpi"><span class="v">+${M$(bonoP)}</span><span class="l">Bono carga solar · portafolio · año 1</span></div>
        <div class="kpi"><span class="v">${fmtN.format(Math.round(solarE/1000))} MWh</span><span class="l">Excedente solar al BESS · año</span></div>
      </div>`;
    mas.innerHTML = `<p class="cob-note" style="margin:.2rem 0 0"><b>¿Y con más superficie?</b> Donde el techo lo permite, ampliar el PV por encima del diseño rinde ahorro adicional. Se detalla por sitio en la sección siguiente.</p>`;
  } else {
    motor.innerHTML = `<p class="cob-note">El <b>motor de carga solar</b> corresponde al esquema de <b>Autoconsumo (Opción 1)</b>: allí el BESS se carga con el excedente solar de mediodía (bono de carga solar por sitio). En Opción 2 (GD Medición Neta) el PV se mantiene bajo el tope de 0.7 MW y prácticamente no hay excedente. Las cifras de cobertura de arriba corresponden a la Opción 2.</p>`;
    mas.innerHTML = "";
  }
}
RERENDER.push(renderCobertura);
'''

# splice cobertura HTML (replace old cobertura block, keep the CONSUMO anchor)
html = html[:i0] + NEW_COB_HTML + html[i1:]
# replace old renderCobertura JS block
html = re.sub(r'\n// ----------[^\n]*COBERTURA[^\n]*\nfunction renderCobertura\(\)\{.*?RERENDER\.push\(renderCobertura\);\n',
              NEW_COB_JS, html, count=1, flags=re.S)
assert 'cob-motor' in html and html.count('function renderCobertura') == 1, 'cobertura JS splice failed'

# ================= 8. NEW section "¿Y con más superficie?" =================
SUP_HTML = '''<!-- 6c · ¿Y CON MÁS SUPERFICIE? -->
<style>
#supmas h2{font-size:clamp(1.5rem,2.7vw,2rem);margin-bottom:.1rem;line-height:1.1}
#supmas .layout-sb{margin-top:.8rem}
#supmas .terms{gap:.7rem}
#supmas .terms .v{font-size:clamp(1.15rem,2vw,1.5rem)}
#supmas .foot-note{margin-top:.5rem;font-size:.68rem;color:var(--ink-60)}
#supmas .mas-note{font-size:.8rem;color:var(--ink-60);line-height:1.4;margin-top:.5rem}
#supmas .mas-note b{color:var(--ink)}
</style>
<section class="page" id="supmas">
  <div class="pagenum">Potencial con más superficie</div>
  <div class="eyebrow">Potencial adicional con más superficie · Autoconsumo (Op1)</div>
  <h2>¿Y con más superficie?</h2>
  <p>El diseño rev4 se topa a la superficie disponible de cada sitio. Con techo adicional, el PV puede crecer hasta su óptimo de máximo ahorro (con el BESS fijo y el mismo despacho carga-solar). Aquí el potencial por sitio.</p>
  <div class="tabs" id="tabs-supmas" role="tablist"></div>
  <div class="subtabs" id="sub-supmas" hidden></div>
  <div class="layout-sb">
    <aside class="terms" id="terms-supmas"></aside>
    <div>
      <div class="chart" id="chart-supmas"></div>
      <div class="legend">
        <span><i style="background:#8F3A81"></i>Ahorro cliente año 1 vs superficie</span>
        <span><i class="sq" style="background:#621558"></i>Diseño rev4</span>
        <span><i class="sq" style="background:#B8741A"></i>Óptimo (sitio solo)</span>
      </div>
      <div class="mas-note" id="note-supmas"></div>
    </div>
  </div>
  <p class="foot-note" id="foot-supmas"></p>
</section>

'''

SUP_JS = r'''
// ---------- ¿Y CON MÁS SUPERFICIE? (v8) ----------
function renderSupMas(k){
  const sw=MODEL.sweep.sites[k], st=sw.standalone, m2k=MODEL.meta_cs.m2_per_kwp;
  const desK=sw.kwp_design, desM2=desK*m2k;
  const disp=(sw.m2_disponibles!=null)?sw.m2_disponibles:desM2;
  const optK=st.kwp_opt, optM2=(st.m2_opt!=null)?st.m2_opt:optK*m2k;
  const falt=(st.m2_faltantes!=null)?st.m2_faltantes:Math.max(0,optM2-disp);
  const dAh=st.delta_ahorro||0;
  const factor=sw.union_design.van_20a_mxn/sw.union_design.ahorro_cliente_anio1_mxn; // 20-yr multiple (prefactibilidad)
  const vanAdd=dAh*factor;
  const atCap=!!st.opt_at_cap;
  const usoPct=Math.min(1,desM2/disp);

  document.getElementById("terms-supmas").innerHTML=[
    [fmtN.format(desK)+" kWp","Diseño rev4 · "+fmtN.format(desM2)+" m² ("+pct(usoPct)+" del techo)"],
    [(atCap?"≥ "+fmtN.format(optK):fmtN.format(optK))+" kWp",atCap?"Óptimo: sigue creciendo hasta 20 MW":"kWp óptimo (sitio solo)"],
    [fmtN.format(optM2)+" m²","Superficie para el óptimo"+(falt>0?" · faltan "+fmtN.format(falt)+" m²":" · disponible alcanza")],
    ["+"+fmt$.format(dAh),"Ahorro adicional cliente · año 1"],
    ["+"+M$(vanAdd),"VAN adicional aprox. · 20 años"]
  ].map(([v,l])=>`<div><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");

  // mini-curve: ahorro cliente año1 vs m² (curva base portafolio, ilustrativa)
  const cv=sw.curve;
  const W=560,H=280,mL=64,mR=14,mT=22,mB=40;
  const xs=cv.map(c=>c.m2), ys=cv.map(c=>c.ahorro);
  const x0=Math.min(...xs), x1=Math.max(desM2,optM2,Math.max(...xs));
  const xmin=Math.min(x0,desM2), xmax=x1*1.02;
  const ymax=Math.max(...ys)*1.06, ymin=0;
  const X=v=>mL+(W-mL-mR)*(v-xmin)/(xmax-xmin);
  const Y=v=>mT+(H-mT-mB)*(1-(v-ymin)/(ymax-ymin));
  let axis="";
  const ystep=[500000,1000000,2000000,5000000,10000000,20000000].find(s=>ymax/s<=4.4)||20000000;
  for(let v=0;v<=ymax;v+=ystep){axis+=`<line x1="${mL}" y1="${Y(v).toFixed(1)}" x2="${W-mR}" y2="${Y(v).toFixed(1)}" stroke="rgba(34,26,51,.07)"/><text x="${mL-8}" y="${(Y(v)+4).toFixed(1)}" text-anchor="end" font-size="10" fill="rgba(34,26,51,.5)">${fMM(v)}</text>`;}
  // x ticks (m²)
  let xt="";[[xmin,"start"],[(xmin+xmax)/2,"middle"],[xmax,"end"]].forEach(([v,an])=>{xt+=`<text x="${X(v).toFixed(1)}" y="${H-8}" text-anchor="${an}" font-size="9" fill="rgba(34,26,51,.5)">${fmtN.format(Math.round(v))} m²</text>`;});
  const pts=cv.map(c=>[X(c.m2),Y(c.ahorro)]);
  let line=`M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for(let i=1;i<pts.length;i++)line+=`L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
  const area=line+`L${X(cv[cv.length-1].m2).toFixed(1)},${Y(0).toFixed(1)}L${X(cv[0].m2).toFixed(1)},${Y(0).toFixed(1)}Z`;
  // interpolate union-curve ahorro at a given m² (for marker y)
  const yat=m2=>{ if(m2<=xs[0])return ys[0]; if(m2>=xs[xs.length-1])return ys[ys.length-1];
    for(let i=0;i<cv.length-1;i++){ if(m2>=xs[i]&&m2<=xs[i+1]){const t=(m2-xs[i])/(xs[i+1]-xs[i]);return ys[i]+t*(ys[i+1]-ys[i]);}} return ys[ys.length-1]; };
  const mkr=(m2,col,txt,ly,an)=>{const px=X(m2),py=Y(yat(m2));
    return `<line x1="${px.toFixed(1)}" y1="${mT}" x2="${px.toFixed(1)}" y2="${(H-mB).toFixed(1)}" stroke="${col}" stroke-width="1" stroke-dasharray="3 3" opacity=".7"/>`
      +`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.5" fill="${col}"/>`
      +`<text x="${px.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="${an||'middle'}" font-size="8.5" font-weight="600" fill="${col}">${txt}</text>`;};
  const optX = atCap? Math.min(optM2,xmax) : optM2;
  const close = Math.abs(X(optX)-X(desM2)) < 46;
  const desMk = mkr(desM2,"#621558","diseño",mT-6,close?"end":"middle");
  const optMk = mkr(optX,"#B8741A",atCap?"óptimo →":"óptimo",close?mT-6:mT-6,close?"start":"middle");
  document.getElementById("chart-supmas").innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Ahorro vs superficie">
    ${axis}${xt}
    <path d="${area}" fill="rgba(143,58,129,.10)" stroke="none"/>
    <path d="${line}" fill="none" stroke="#8F3A81" stroke-width="2"/>
    ${desMk}${optMk}
  </svg>`;

  document.getElementById("note-supmas").innerHTML = atCap
    ? `<b>${META[k].name}.</b> El ahorro sigue creciendo con más superficie sin óptimo interno hasta el límite regulatorio de 20 MW: el potencial está acotado por el techo disponible, no por el modelo. Diseño rev4 hoy a ${pct(usoPct)} del techo.`
    : (falt>0
      ? `<b>${META[k].name}.</b> El óptimo requiere <b>${fmtN.format(optM2)} m²</b> (${fmtN.format(falt)} m² más que el techo disponible): con esa superficie, <b>+${fmt$.format(dAh)}/año</b> de ahorro adicional para el cliente.`
      : `<b>${META[k].name}.</b> La superficie disponible alcanza para el óptimo (${fmtN.format(optM2)} m²): ampliar del diseño al óptimo rinde <b>+${fmt$.format(dAh)}/año</b> adicionales.`);

  document.getElementById("foot-supmas").textContent =
    "Óptimo de máximo ahorro con BESS fijo y despacho carga-solar; base individual por sitio (PPA re-resuelto sobre el sitio solo, TIR inversionista 14 %) — la cota defendible. La curva es ilustrativa (base portafolio). VAN aproximado con el múltiplo 20-años del diseño. Prefactibilidad: superficie, transformador e interconexión se confirman en visita técnica; densidad 4.0 m²/kWp.";
}
makeSiteTabs("tabs-supmas","sub-supmas",renderSupMas);
'''

# insert SUP_HTML right before the CONSUMO anchor
rep(COB_END, SUP_HTML + COB_END)
# insert SUP_JS before setOp(0)
rep('\nsetOp(0);', '\n' + SUP_JS + '\nsetOp(0);')

open(OUT, 'w', encoding='utf-8').write(html)
print('wrote', OUT, len(html)//1024, 'KB')
