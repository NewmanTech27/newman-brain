#!/usr/bin/env python3
"""Build the GEPP "Carga Solar + Autoconsumo Max" (v9) deck.

Starts from the DELIVERED v8 deck (GEPP - Solucion Energetica Solar-Charge BESS.html,
never modified) and adds a THIRD option OP=2 "Opción 3 — Autoconsumo Max" (the NR
"Sin Restricción de Superficie" scenario from gepp_data_nr.json / motor_nr.json):

  1. Augment the MODEL: append a 3rd element to every sys label, add Op3 rows to
     resumen4/resumenP + "Suma Opción 3" portfolio, add proj3 (scaled) per site,
     MODEL.op3_td (NR typical-day dispatch curves), MODEL.nr (coverage/m2 block).
     The augmented data is written to gepp_data_nr_deck.json and spliced BYTE-IDENTICAL.
  2. Generalize the OP-aware JS from 2 -> 3 options and add Op3 branches
     (renderCum 3 series, renderDesp NR curves, renderCobertura NR coverage,
      renderSupMas m² required-vs-available flip, renderSup Op3 copy).
  3. Add the 3rd opswitch button, bump the <title> to v9, add Op3 footnotes/caveats.

Rerunnable. Writes:
  GEPP - Solucion Energetica Solar-Charge BESS + Autoconsumo Max.html
  gepp_data_nr_deck.json  (augmented MODEL source, byte-identical to the splice)
  nr_script.js            (the new deck's main <script>, for domstub_nr.js)
"""
import re, json, copy

SP  = '/home/mario/CFE Brain/work/gepp-carga-solar'
SRC = f'{SP}/GEPP - Solucion Energetica Solar-Charge BESS.html'          # delivered v8 (read-only)
OUT = f'{SP}/GEPP - Solucion Energetica Solar-Charge BESS + Autoconsumo Max.html'
DECKJSON = f'{SP}/gepp_data_nr_deck.json'
NRSCRIPT = f'{SP}/nr_script.js'

SITES  = ['ixt','aca','can','pro','pr1','pr2','tap']
MAIN   = ['ixt','aca','can','pro']
SUBS   = ['pr1','pr2','tap']
KMNAME = {'ixt':'Ixtlahuacán','aca':'Acapulco','can':'Cancún','pro':'Proplasa',
          'pr1':'Proplasa · Preforma 1','pr2':'Proplasa · Preforma 2','tap':'Proplasa · Tapa'}

# ============================================================ 1. AUGMENT MODEL
cs = json.load(open(f'{SP}/gepp_data_cs.json', encoding='utf-8'))
nr = json.load(open(f'{SP}/gepp_data_nr.json', encoding='utf-8'))
mo = json.load(open(f'{SP}/motor_nr.json',     encoding='utf-8'))

k_nr, k_rev4 = nr['k']['k_nr'], nr['k']['k_rev4_delivered']
data = copy.deepcopy(cs)

# ---- per-site Op3 derived cascade (anchors neto to gepp_data_nr; apv is the balancing term) ----
op3 = {}
for k in SITES:
    ann = mo['sites'][k]['op1']['annual']
    snr = nr['sites'][k]
    sys = cs['sites'][k]['sys']
    price = round(ann['price_ppa_rev4'] * (k_nr / k_rev4), 6)
    ab   = ann['ahorro_bess_bruto_mxn']            # BESS bruto (solar-charge dispatch)
    ppa  = ann['K72_new_kwh'] * price              # PPA payment yr1
    part = 0.5 * ab
    neto = snr['ahorro_cliente_anio1_nr']          # authoritative
    apv  = neto + ppa + part - ab                  # balancing term -> cascade foots exactly
    gasto = sys['Gasto real hoy (con autoabasto) ($/año)'][0]
    op3[k] = dict(price=price, ab=ab, ppa=ppa, part=part, neto=neto, apv=apv,
                  bruto=apv + ab, gen=snr['gen_kwh_nr'], gasto=gasto,
                  kwp=snr['kwp_nr'], m2req=snr['m2_requeridos'],
                  ppakwh=price, tirbess=sys['TIR inversionista BESS'][0])

# ---- 1a. append 3rd element to every sys label (all 7 sites) ----
STR3 = {'Concepto': 'OPCIÓN 3 — Autoconsumo Max',
        'Esquema legal': 'Autoconsumo interconectado — potencial máximo (permiso CNE simplificado, <20 MW)'}
def op3_sys_value(k, label, op1val):
    o = op3[k]
    m = {
        'Potencia PV (kWp DC)': o['kwp'],
        'Superficie requerida (m²)': o['m2req'],
        'Precio PPA (MXN/kWh, año 1)': o['price'],
        'Ahorro bruto PV año 1 ($)': o['apv'],
        'Ahorro bruto BESS año 1 c/merma ($)': o['ab'],
        'Ahorro bruto total ($)': o['bruto'],
        'Pago PPA año 1 ($)': o['ppa'],
        'Pago participación BESS ($)': o['part'],
        'AHORRO NETO GEPP año 1 ($)': o['neto'],
        '% ahorro bruto (vs gasto real hoy)': o['bruto'] / o['gasto'],
        '% ahorro neto (vs gasto real hoy)': o['neto'] / o['gasto'],
        'Generación PV año 1 (kWh)': o['gen'],
        'Energía facturada al PPA (kWh)': mo['sites'][k]['op1']['annual']['K72_new_kwh'],
        'TIR inversionista PV': 0.14,
        'CAPEX PV (MXN)': nr['sites'][k]['capex_pv_nr_mxn'],
        'CAPEX PV (USD)': round(nr['sites'][k]['capex_pv_nr_mxn'] / 17.55, 2),
    }
    if label in STR3: return STR3[label]
    if label in m:    return m[label]
    return op1val                                   # unchanged labels reuse Op1 value

for k in SITES:
    sys = data['sites'][k]['sys']
    for label, arr in sys.items():
        arr.append(op3_sys_value(k, label, arr[0]))

# ---- 1b. Op3 resumen rows + "Suma Opción 3" portfolio ----
def op3_row(k, r1, opstr):
    o = op3[k]
    return {'site': KMNAME[k], 'op': opstr,
            'kwp': o['kwp'], 'bkw': r1['bkw'], 'bkwh': r1['bkwh'], 'gen': o['gen'],
            'gasto': o['gasto'], 'autoab': r1.get('autoab'), 'bruto': o['bruto'],
            'ppa': o['ppa'], 'part': o['part'], 'neto': o['neto'],
            'pctb': o['bruto'] / o['gasto'], 'pctn': o['neto'] / o['gasto'],
            'ppakwh': o['ppakwh'], 'tirpv': 0.14, 'tirbess': o['tirbess']}

def op1_row_of(res, k):
    for r in res['rows']:
        if r['site'] == KMNAME[k] and isinstance(r['op'], str) and r['op'].startswith('Op1'):
            return r
    return None

for k in MAIN:
    r1 = op1_row_of(cs['resumen4'], k)
    opstr = 'Op3: Autoconsumo Max' + (' (predio + medidores)' if k == 'pro' else '')
    data['resumen4']['rows'].append(op3_row(k, r1, opstr))
for k in SUBS:
    r1 = op1_row_of(cs['resumenP'], k)
    data['resumenP']['rows'].append(op3_row(k, r1, 'Op3: Autoconsumo Max'))

# 7-row portfolio "potencial máximo" (faithful to gepp_data_nr)
gasto7 = sum(cs['sites'][k]['sys']['Gasto real hoy (con autoabasto) ($/año)'][0] for k in SITES)
bkw7   = sum(cs['sites'][k]['sys']['BESS potencia (kW)'][0]   for k in SITES)
bkwh7  = sum(cs['sites'][k]['sys']['BESS capacidad (kWh)'][0] for k in SITES)
P3 = {'kwp': nr['portfolio']['kwp_nr'], 'bkw': bkw7, 'bkwh': bkwh7,
      'gen': nr['portfolio']['gen_nr_kwh'], 'gasto': gasto7,
      'autoab': sum(op3[k]['neto'] for k in SITES) * 0,  # placeholder, not displayed
      'bruto': sum(op3[k]['bruto'] for k in SITES),
      'ppa': sum(op3[k]['ppa'] for k in SITES),
      'part': sum(op3[k]['part'] for k in SITES),
      'neto': nr['portfolio']['ahorro_cliente_anio1_nr_mxn'],
      'capex': nr['portfolio']['inversion_estimada_newman_nr_mxn']}
data['resumen4']['portfolio']['Suma Opción 3'] = P3
data['resumenP']['portfolio']['Suma Opción 3'] = P3

# ---- 1c. proj3 per site (scale Op1 trajectory by year-1 neto ratio r_k; prefeasibility) ----
for k in SITES:
    p1 = cs['sites'][k]['proj1']
    neto1 = cs['sites'][k]['sys']['AHORRO NETO GEPP año 1 ($)'][0]
    rk = op3[k]['neto'] / neto1
    p3 = []
    for r in p1:
        real = r['real']
        neto = r['neto'] * rk
        p3.append({'yr': r['yr'], 'pleno': r['pleno'], 'autoab': r['autoab'], 'real': real,
                   'apv': r['apv'] * rk, 'abess': r['abess'] * rk,
                   'ppa': r['ppa'] * rk, 'part': r['part'] * rk,
                   'neto': neto, 'acum': r['acum'] * rk,
                   'pct': (neto / real) if real else 0})
    data['sites'][k]['proj3'] = p3

# ---- 1d. op3 typical-day dispatch (NR curves, all 7 sites) ----
data['op3_td'] = {}
for k in SITES:
    td = nr['sites'][k]['typical_day']
    def clean(rows):
        return [{'h': p['h'], 'per': p['per'], 'carga': p['carga'], 'pv': p['pv'],
                 'chg': p['chg'], 'dis': p['dis'], 'neta': p['neta']} for p in rows]
    data['op3_td'][k] = {'invierno': clean(td['invierno']), 'verano': clean(td['verano'])}

# ---- 1e. MODEL.nr : coverage + m² block for renderCobertura / renderSupMas ----
nr_sites = {}
for k in SITES:
    s = nr['sites'][k]
    gen = s['gen_kwh_nr']; cob = s['cobertura_pct_nr']
    consumo = gen / (cob / 100.0)
    autoeff = (gen - s['exceso_remanente_kwh']) / gen
    nr_sites[k] = {
        'name': KMNAME[k], 'kwp_nr': s['kwp_nr'], 'kwp_rev4': s['kwp_rev4'],
        'gen_kwh_nr': gen, 'consumo_kwh': consumo, 'cobertura_pct_nr': cob,
        'autoconsumo_efectivo': autoeff, 'carga_solar_kwh': s['carga_solar_kwh'],
        'pct_carga_solar_del_bess': s['pct_carga_solar_del_bess'],
        'solar_charge_bonus_mxn': s['solar_charge_bonus_mxn'],
        'm2_requeridos': s['m2_requeridos'], 'm2_disponibles': s.get('m2_disponibles'),
        'm2_faltantes': s['m2_faltantes'], 'nr_at_regulatory_cap': s['nr_at_regulatory_cap'],
        'delta_ahorro_anio1': s['delta_ahorro_anio1'],
    }
nr_port = {
    'cobertura_pct_nr': nr['portfolio']['cobertura_pct_nr'],
    'gen_nr_kwh': nr['portfolio']['gen_nr_kwh'], 'consumo_kwh': nr['portfolio']['consumo_kwh'],
    'carga_solar_kwh': sum(nr['sites'][k]['carga_solar_kwh'] for k in MAIN),
    'solar_charge_bonus_mxn': sum(nr['sites'][k]['solar_charge_bonus_mxn'] for k in MAIN),
    'inversion_estimada_newman_nr_mxn': nr['portfolio']['inversion_estimada_newman_nr_mxn'],
}
data['nr'] = {'sites': nr_sites, 'portfolio': nr_port,
              'meta': {'k_nr': k_nr, 'tir_sites4': nr['k']['tir_nr_sites4'],
                       'sitesp_combined_irr': nr['k']['sitesp_combined_irr_at_knr'],
                       'scenario': nr['meta']['scenario']}}

# ---- 1f. MODEL.peak : "¿Por qué este tamaño?" técnico-económico (peak_analysis.json) ----
pk = json.load(open(f'{SP}/peak_analysis.json', encoding='utf-8'))
def _near_opt_split(site):
    withm = [c for c in site['curve'] if 'marginal' in c]
    n = min(withm, key=lambda c: abs(c['kwp'] - site['kwp_nr']))
    return n['marginal']
peak_sites = {}
for k in MAIN:
    s   = pk['sites'][k]
    cur = s['curve']
    pkpt   = max(cur, key=lambda c: c['ahorro_cliente_anio1'])
    rising = (s['peak_type'] == 'regulatorio')      # pro: curva aún sube en el tope 20 MW
    so     = _near_opt_split(s)
    last   = cur[-1]; lm = last.get('marginal')
    sat    = s['saturacion_at_opt']; ceil = s['ceiling']; bv = s['bess_verdict']; um = s['umbral']
    peak_sites[k] = {
        'name': s['name'], 'kwp_nr': s['kwp_nr'], 'kwp_rev4': s['kwp_rev4'],
        'peak_type': s['peak_type'], 'rising': rising,
        'sat_opt': s['saturacion_bess_pct_at_opt'],
        'ceiling': {'daytime': ceil['daytime_load_kwh'], 'punta_N': ceil['punta_N_kwh'],
                    'addressable': ceil['addressable_total_kwh']},
        'sat': {'self_kwh': sat['self_kwh'], 'self_pct': sat['self_vs_daytime_ceiling_pct'],
                'carga_solar': sat['carga_solar_kwh'], 'charge_energy': sat['charge_energy_kwh'],
                'remanente': sat['remanente_kwh'], 'gen_kwh': sat['gen_kwh']},
        'curve': [{'kwp': c['kwp'], 'ah': c['ahorro_cliente_anio1'], 'sat': c['sat_bess_pct']} for c in cur],
        'peak_kwp': pkpt['kwp'], 'peak_ah': pkpt['ahorro_cliente_anio1'],
        'split_opt': {'a': so['a_self'], 'b': so['b_solar_charge'], 'c': so['c_remanente'], 'd': so['d_ahorro_por_kwp']},
        'split_sat': (None if rising else {'a': lm['a_self'], 'b': lm['b_solar_charge'],
                                           'c': lm['c_remanente'], 'd': lm['d_ahorro_por_kwp'], 'kwp': last['kwp']}),
        'bess_scale': [{'scale': r['scale'], 'kwp_opt': r['kwp_opt'], 'ahorro_opt': r['ahorro_opt'],
                        'capex_bess': r['capex_bess']} for r in s['bess_scale']['scale_rows']],
        'umbral': {'book': um['book_demand_total'], 'cc': um['cc_demand_total'],
                   'delta': um['delta_book_minus_true'], 'delta_pct': um.get('delta_pct')},
        'verdict': {'con_van': bv['con_bess_van'], 'sin_van': bv['sin_bess_van'], 'delta_van': bv['delta_van'],
                    'bono': bv['bono_solar_charge'], 'con_a1': bv['con_bess_ahorro'], 'sin_a1': bv['sin_bess_ahorro']},
    }
pbv = pk['portfolio']['bess_verdict']; pum = pk['portfolio']['umbral']
peak_port = {
    'con_van': pbv['con_bess_van'], 'sin_van': pbv['sin_bess_van'], 'delta_van': pbv['delta_van'],
    'con_a1': pbv['con_bess_ahorro_a1'], 'sin_a1': pbv['sin_bess_ahorro_a1'],
    'umbral_delta': pum['delta_book_minus_true'], 'umbral_delta_pct': pum['delta_pct'],
    'bono_total': sum(pk['sites'][k]['bess_verdict']['bono_solar_charge'] for k in MAIN),
    'capex_bess_per_kwh': 4914,
}
data['peak'] = {'sites': peak_sites, 'portfolio': peak_port,
                'meta': {'gate': pk['meta']['gate'], 'caveat': pk['meta']['caveat']}}

# ---- write the augmented MODEL source (compact, same serialization as extract_cs) ----
model_str = json.dumps(data, ensure_ascii=False)
open(DECKJSON, 'w', encoding='utf-8').write(model_str)

# ============================================================ 2. HTML / JS EDITS
html = open(SRC, encoding='utf-8').read()

def rep(old, new, n=1):
    global html
    c = html.count(old)
    assert c == n, f'rep expected {n}, found {c}: {old[:70]!r}'
    html = html.replace(old, new, n)

def splice(start, end, new, keep_end):
    """Replace html[i(start)..j(end)] with new. If keep_end, j is the START of `end`
    (end preserved); else end is consumed (j = end of `end`)."""
    global html
    i = html.index(start)
    j = html.index(end, i)
    if not keep_end:
        j += len(end)
    html = html[:i] + new + html[j:]

# ---- 2.0 MODEL splice (byte-identical) ----
new_model = 'const MODEL = ' + model_str + ';\n'
html2 = re.sub(r'const MODEL = \{.*?\};\n', lambda m: new_model, html, count=1, flags=re.S)
assert html2 != html, 'MODEL splice failed'
html = html2

# ---- 2.1 title (v9) ----
rep('<title>GEPP — Solución Energética v8 · Carga Solar</title>',
    '<title>GEPP — Solución Energética v9 · Carga Solar + Autoconsumo Max</title>')

# ---- 2.2 opswitch: 3rd button ----
rep('  <button data-op="1">Opción 2 · GD Medición Neta</button>',
    '  <button data-op="1">Opción 2 · GD Medición Neta</button>\n  <button data-op="2">Opción 3 · Autoconsumo Max</button>')

# ---- 2.3 supmas legend + eyebrow + intro: give ids so they can flip per option ----
rep('<div class="chart" id="chart-supmas"></div>\n      <div class="legend">',
    '<div class="chart" id="chart-supmas"></div>\n      <div class="legend" id="leg-supmas">')
rep('<div class="eyebrow">Potencial adicional con más superficie · Autoconsumo (Op1)</div>',
    '<div class="eyebrow" id="eyebrow-supmas">Potencial adicional con más superficie · Autoconsumo (Op1)</div>')
rep('<p>El diseño rev4 se topa a la superficie disponible de cada sitio. Con techo adicional, el PV puede crecer hasta su óptimo de máximo ahorro (con el BESS fijo y el mismo despacho carga-solar). Aquí el potencial por sitio.</p>',
    '<p id="intro-supmas">El diseño rev4 se topa a la superficie disponible de cada sitio. Con techo adicional, el PV puede crecer hasta su óptimo de máximo ahorro (con el BESS fijo y el mismo despacho carga-solar). Aquí el potencial por sitio.</p>')

# ---- 2.4 OPNAME ----
i = html.index('const OPNAME = ['); j = html.index('];', i)
old = html[i:j+2]
rep(old, old[:-2] + ',"Opción 3 — Autoconsumo Max"];')

# ---- 2.5 P() ----
rep('const P = ()=> OP? R4.portfolio["Suma Opción 2"] : R4.portfolio["Suma Opción 1"];',
    'const P = ()=> R4.portfolio[["Suma Opción 1","Suma Opción 2","Suma Opción 3"][OP]];')

# ---- 2.6 projOf ----
rep('const projOf = k => OP? S[k].proj2 : S[k].proj1;',
    'const projOf = k => [S[k].proj1,S[k].proj2,S[k].proj3][OP];')

# ---- 2.7 aggProj (key + site set) + PROJ_ALL ----
rep('  const key = op? "proj2":"proj1";',
    '  const key = ["proj1","proj2","proj3"][op];\n  const asites = op===2? ["ixt","aca","can","pro","pr1","pr2","tap"] : MAIN;')
rep('    MAIN.forEach(k=>{const p=S[k][key][i];r.pleno+=p.pleno;r.real+=p.real;r.neto+=p.neto;r.acum+=p.acum;r.autoab+=p.autoab;});',
    '    asites.forEach(k=>{const p=S[k][key][i];r.pleno+=p.pleno;r.real+=p.real;r.neto+=p.neto;r.acum+=p.acum;r.autoab+=p.autoab;});')
rep('const PROJ_ALL = [aggProj(0), aggProj(1)];',
    'const PROJ_ALL = [aggProj(0), aggProj(1), aggProj(2)];')

# ---- 2.8 CAPEXof (Op3 uses NR CAPEX directly) ----
rep('const CAPEXof = p => p.kwp*1000*0.65*17.55 + p.bkwh*1000*0.28*17.55;   // precios Supuestos: 0.65 USD/Wp · 0.28 USD/Wh · TC 17.55',
    'const CAPEXof = p => (p.capex!=null? p.capex : p.kwp*1000*0.65*17.55 + p.bkwh*1000*0.28*17.55);   // precios Supuestos: 0.65 USD/Wp · 0.28 USD/Wh · TC 17.55 (Op3: CAPEX NR directo)')

# ---- 2.9 renderResumenTable pref ----
rep('  const pref = OP? "Op2":"Op1";', '  const pref = ["Op1","Op2","Op3"][OP];', n=2)

# ---- 2.10 renderCum : 3 series ----
NEW_CUM = r'''// ---------- CHART: portfolio cumulative op1/op2/op3 (selected emphasized) ----------
function renderCum(){
  const series=[PROJ_ALL[0].slice(1).map(p=>p.acum),PROJ_ALL[1].slice(1).map(p=>p.acum),PROJ_ALL[2].slice(1).map(p=>p.acum)];
  const cols=["#621558","#8F3A81","#B8741A"];
  const names=["Opción 1 · Autoconsumo","Opción 2 · GD Medición Neta","Opción 3 · Autoconsumo Max"];
  const n=series[0].length;
  const W=560,H=300,mL=64,mR=16,mT=16,mB=30;
  const max=Math.max(...series[0],...series[1],...series[2])*1.04, min=0;
  const x=i=>mL+(W-mL-mR)*i/(n-1), y=v=>mT+(H-mT-mB)*(1-(v-min)/(max-min));
  const bw=(W-mL-mR)/(n-1);
  let hover="";
  for(let i=0;i<n;i++){
    hover+=`<rect x="${(x(i)-bw/2).toFixed(1)}" y="${mT}" width="${bw.toFixed(1)}" height="${H-mT-mB}" fill="transparent" data-tip="<b>${2026+i}</b><br>Opción 1: ${fmt$.format(series[0][i])}<br>Opción 2: ${fmt$.format(series[1][i])}<br>Opción 3: ${fmt$.format(series[2][i])}"/>`;
  }
  const path=a=>a.map((v,i)=>`${i?"L":"M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  let labels="";[2026,2031,2036,2041,2045].forEach(yr=>{labels+=`<text x="${x(yr-2026).toFixed(1)}" y="${H-8}" text-anchor="middle" font-size="10" fill="rgba(34,26,51,.5)">${yr}</text>`;});
  let paths="";
  for(let s=0;s<3;s++){ if(s===OP) continue;
    paths+=`<path d="${path(series[s])}" fill="none" stroke="${cols[s]}" stroke-width="2" opacity=".3"/>`;
  }
  const sel=series[OP];
  paths+=`<path d="${path(sel)}" fill="none" stroke="${cols[OP]}" stroke-width="2.6"/>`
    +`<circle cx="${x(n-1).toFixed(1)}" cy="${y(sel[n-1]).toFixed(1)}" r="4" fill="${cols[OP]}"/>`
    +`<text x="${(x(n-1)-12).toFixed(1)}" y="${(y(sel[n-1])-10).toFixed(1)}" text-anchor="end" font-size="11" font-weight="600" fill="#221A33">${fmt$.format(sel[n-1])}</text>`;
  const el=document.getElementById("chart-cum");
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Ahorro neto acumulado 20 años, Opción 1 / 2 / 3">
   ${axisY(min,max,W,H,mL,mR,mT,mB,fMM)}${paths}${labels}${hover}</svg>`;
  document.getElementById("leg-cum").innerHTML = names.map((nm,s)=>
    `<span><i style="background:${cols[s]}${s===OP?"":";opacity:.3"}"></i>${nm}${s===OP?" — seleccionada":""}</span>`).join("");
  bindTips(el);
}
'''
splice('// ---------- CHART: portfolio cumulative op1 vs op2 (selected emphasized) ----------',
       '// ---------- SUPERFICIE ----------', NEW_CUM + '\n', keep_end=True)

# ---- 2.11 renderSup: compute sub fits (honest for Op3), Op3 headline + foot ----
rep('        rows.push({k:sk,label:META[sk].name,req:sysv(sk,"Superficie requerida (m²)"),av,kwp:sysv(sk,"Potencia PV (kWp DC)"),fits:true,sub:true});',
    '        rows.push({k:sk,label:META[sk].name,req:sysv(sk,"Superficie requerida (m²)"),av,kwp:sysv(sk,"Potencia PV (kWp DC)"),fits:sysv(sk,"Superficie requerida (m²)")<=av,sub:true});')

splice('document.getElementById("sup-headline").innerHTML =', ';',
       '''document.getElementById("sup-headline").innerHTML = OP===2
    ? "Potencial máximo de autoconsumo:<br>qué techo habilita cada sitio."
    : (allFit
      ? "Sí: los 4 sitios caben<br>en la superficie disponible."
      : "Tres verdades por sitio:<br>qué cabe, cuánto y qué falta.");''', keep_end=False)

splice('document.getElementById("foot-sup").textContent =', ';',
       '''document.getElementById("foot-sup").textContent =
   (OP===2
    ? "Opción 3 — Autoconsumo Max: cada sitio se dimensiona a su potencial máximo de autoconsumo (PV ampliado, con el BESS fijo y el mismo despacho carga-solar). Varios sitios requieren superficie adicional a la disponible hoy: los m² faltantes son la condición que habilita el potencial. Proplasa se muestra a su tope regulatorio de 20 MW (autoconsumo, permiso CNE simplificado). Cifras de prefactibilidad; techo, estructura e interconexión se validan en visita técnica."
    : OP===0
    ? "Opción 1: Proplasa se diseñó exactamente al límite de su predio (15,396 m²) — la visita técnica valida los elementos de azotea (equipos, andadores, sombras) para el ajuste fino. Cancún e Ixtlahuacán quedan limitados por carga, no por techo: hay superficie de sobra para crecer."
    : "Opción 2: el tope legal de 839.45 kWp por medidor requiere solo 3,357.8 m² por servicio — cabe con holgura en los 4 sitios (Proplasa: 3 medidores × 3,357.8 m² = 10,073 m² de 15,396 m² disponibles).")+
   " Densidad 4.0 m²/kWp del módulo Tongwei 715 Wp.";''', keep_end=False)

# ---- 2.12 renderSol foot (Op3 note) ----
splice('  document.getElementById("foot-sol").textContent =', '`;',
       '''  document.getElementById("foot-sol").textContent =
   `Cascada del año 1, ${OPNAME[OP]}. El “gasto final con Newman” incluye la factura CFE remanente más los pagos a Newman; la diferencia contra el gasto actual es el ahorro neto de GEPP. Montos MXN sin IVA.`
   + (OP===2? " Opción 3 amplía el PV de la Opción 1 a su potencial máximo de autoconsumo; requiere superficie adicional a la disponible hoy (prefactibilidad)." : "");''', keep_end=False)

# ---- 2.13 renderDesp: use NR typical-day curves for Op3 ----
splice('  const s=S[k], d=s[despSeason];', '  // demanda punta',
       '''  const s=S[k];
  let prof;
  if(OP===2){
    const td=MODEL.op3_td[k][despSeason==="inv"?"invierno":"verano"];
    prof=td.map(p=>({...p, neta:p.carga-p.pv-p.chg-p.dis}));
  } else {
    const d=s[despSeason];
    const ratio = OP? sysv(k,"Potencia PV (kWp DC)",1)/sysv(k,"Potencia PV (kWp DC)",0) : 1;
    prof = d.prof.map(p=>{ const pv=p.pv*ratio; return {...p, pv, neta: p.carga - pv - p.chg - p.dis}; });
    if(OP===1){
      let solarE=0;
      prof.forEach(p=>{ if(p.chg<0 && p.pv>0){ solarE+=-p.chg; p.chg=0; } });
      const bh=prof.filter(p=>p.chg<0 && p.pv<=0);
      if(bh.length){ const per=solarE/bh.length; bh.forEach(p=>{ p.chg-=per; }); }
      prof.forEach(p=>{ p.neta=p.carga-p.pv-p.chg-p.dis; });
    }
  }
''', keep_end=True)

# ---- 2.14 renderDesp foot (Op3 copy) ----
splice('  document.getElementById("foot-desp").textContent =', '\ndrawSeason();',
       '''  document.getElementById("foot-desp").textContent =
   `${META[k].full}. Despacho modelado a partir de la curva de giro industrial escalada al recibo mensual (prefactibilidad, sin medición 15-minutal); recorte plano del BESS. `+
   (OP===2
      ?`En Opción 3 (Autoconsumo Max) el PV crece a su potencial máximo: la campana solar de mediodía es mayor, más excedente carga el BESS y solo el faltante restante se toma en horario base. `
      :OP
      ?`En Opción 2 (GD) el PV se dimensiona al tope de 0.7 MW: sin excedente, el BESS se carga íntegramente en horario base. `
      :`En Opción 1 el BESS se carga primero con el excedente solar del mediodía y solo el faltante en horario base. `)+
   (despSeason==="inv"
    ? "En invierno la punta dura 4 horas (18–22 h): el BESS la recorta parcialmente hasta el nivel plano de diseño."
    : "En verano la punta dura 2 horas (20–22 h): el BESS la cubre casi por completo — la demanda facturable en punta se aproxima a cero.");
}''', keep_end=True)

# ---- 2.15 renderVeinte foot (Op3 caveat) ----
splice('  document.getElementById("foot-veinte").textContent =', '\nmakeSiteTabs("tabs-veinte"',
       '''  document.getElementById("foot-veinte").textContent =
   (isAll?`Portafolio: suma de los ${OP===2?"siete medidores (potencial máximo; incluye el predio Proplasa consolidado y sus tres medidores)":"cuatro sitios (Proplasa consolidado)"}, ${OPNAME[OP]}. `:`${OPNAME[OP]}. `)+
   "El “gasto sin sistema” salta en 2033 al vencer el autoabasto (la brecha contra la línea punteada de gasto CFE pleno se cierra). El ahorro Newman —a precio PPA fijo pactado— no depende de ese contrato: es la cobertura que amortigua el salto. A partir del año 16, sin pagos de PPA ni participación, el ahorro completo queda en GEPP."
   + (OP===2? " Opción 3: trayectoria escalada ilustrativa del potencial máximo (prefactibilidad)." : "");
}''', keep_end=True)

# ---- 2.16 renderCobertura: Op3 branch (NR coverage + motor) ----
COB3 = '''  const SC = MODEL.solarcharge;
  const NR = MODEL.nr;
  if(OP===2){
    const covP = NR.portfolio.cobertura_pct_nr/100;
    document.getElementById("cob-headline").innerHTML =
      `Al potencial máximo de autoconsumo, el portafolio cubre <b>${pct(covP)}</b> de su consumo con generación solar propia.`;
    let body="";
    ["ixt","aca","can","pro"].forEach(k=>{ const s=NR.sites[k];
      body += `<tr><td>${META[k].name}</td><td>${fmtN.format(Math.round(s.gen_kwh_nr))} kWh</td><td>${fmtN.format(Math.round(s.consumo_kwh))} kWh</td><td><b>${pct(s.cobertura_pct_nr/100)}</b></td><td>${pct(s.autoconsumo_efectivo)}</td></tr>`;
    });
    body += `<tr class="total"><td>Portafolio</td><td>${fmtN.format(Math.round(NR.portfolio.gen_nr_kwh))} kWh</td><td>${fmtN.format(Math.round(NR.portfolio.consumo_kwh))} kWh</td><td><b>${pct(covP)}</b></td><td>—</td></tr>`;
    document.getElementById("cob-tabla").innerHTML =
      `<div class="tablewrap"><table><thead><tr><th>Sitio · Opción 3</th><th>Generación solar año 1</th><th>Consumo año 1</th><th>Cobertura</th><th>Autoconsumo efect.</th></tr></thead><tbody>${body}</tbody></table></div>`
      + `<p class="footnote" style="margin-top:.5rem">Escenario “Sin restricción de superficie”: cada sitio a su potencial máximo de autoconsumo. El portafolio incluye el predio Proplasa consolidado (topado a 20 MW) y sus tres medidores como potencial.</p>`;
    const bonoP = NR.portfolio.solar_charge_bonus_mxn, solarE = NR.portfolio.carga_solar_kwh;
    const mrows = ["ixt","aca","can","pro"].map(k=>{ const s=NR.sites[k];
      return `<tr><td>${META[k].name}</td><td>${fmtN.format(Math.round(s.carga_solar_kwh))} kWh</td><td>${pct(s.pct_carga_solar_del_bess)}</td><td><b>+${fmt$.format(s.solar_charge_bonus_mxn)}</b></td></tr>`; }).join("");
    document.getElementById("cob-motor").innerHTML = `
      <span class="chip ok">Potencial máximo · carga solar del BESS</span>
      <p class="cob-note" style="margin:.4rem 0 .5rem">Con más superficie, la campana solar de mediodía crece y alimenta más al <b>BESS</b>: ese excedente —que si no se vendería a CFE a valor mayorista— sustituye compra de red. Salida del motor de despacho carga-solar (prefactibilidad).</p>
      <div class="tablewrap"><table>
        <thead><tr><th>Sitio</th><th>Carga solar / año</th><th>% de la carga</th><th>Bono carga solar</th></tr></thead>
        <tbody>${mrows}
          <tr class="total"><td>Sitios principales</td><td>${fmtN.format(Math.round(solarE))} kWh</td><td>—</td><td><b>+${fmt$.format(bonoP)}</b></td></tr>
        </tbody></table></div>
      <div class="kpi-rail">
        <div class="kpi"><span class="v">${M$(NR.portfolio.inversion_estimada_newman_nr_mxn)}</span><span class="l">Inversión estimada Newman · potencial máximo</span></div>
        <div class="kpi"><span class="v">${fmtN.format(Math.round(solarE/1000))} MWh</span><span class="l">Excedente solar al BESS · sitios ppales · año</span></div>
      </div>`;
    document.getElementById("cob-mas").innerHTML = `<p class="cob-note" style="margin:.2rem 0 0"><b>¿Qué habilita este potencial?</b> Superficie adicional a la disponible hoy en varios sitios. Los m² requeridos vs disponibles se detallan por sitio en la sección siguiente.</p>`;
    return;
  }
'''
rep('  const SC = MODEL.solarcharge;\n', COB3)

# ---- 2.17 renderSupMas: legend flip + Op3 (required vs available m²) ----
SUP3 = '''function renderSupMas(k){
  const legEl=document.getElementById("leg-supmas");
  if(legEl) legEl.innerHTML = OP===2
    ? `<span><i class="sq" style="background:#4F8A6B"></i>Superficie disponible hoy</span><span><i class="sq" style="background:#B8741A"></i>Superficie requerida (Op3)</span><span><i class="sq" style="background:rgba(184,116,26,.45)"></i>m² faltantes</span>`
    : `<span><i style="background:#8F3A81"></i>Ahorro cliente año 1 vs superficie</span><span><i class="sq" style="background:#621558"></i>Diseño rev4</span><span><i class="sq" style="background:#B8741A"></i>Óptimo (sitio solo)</span>`;
  const ebEl=document.getElementById("eyebrow-supmas"), inEl=document.getElementById("intro-supmas");
  if(ebEl) ebEl.textContent = OP===2 ? "Superficie que habilita el potencial máximo · Autoconsumo Max (Op3)" : "Potencial adicional con más superficie · Autoconsumo (Op1)";
  if(inEl) inEl.textContent = OP===2 ? "En la Opción 3, cada sitio se dimensiona a su potencial máximo de autoconsumo. Aquí, por sitio, la superficie requerida frente a la disponible hoy: los m² faltantes son la condición que habilita el ahorro adicional." : "El diseño rev4 se topa a la superficie disponible de cada sitio. Con techo adicional, el PV puede crecer hasta su óptimo de máximo ahorro (con el BESS fijo y el mismo despacho carga-solar). Aquí el potencial por sitio.";
  if(OP===2){
    const s=MODEL.nr.sites[k];
    const req=s.m2_requeridos, disp=(s.m2_disponibles!=null)?s.m2_disponibles:null, falt=s.m2_faltantes||0, cap=s.nr_at_regulatory_cap;
    document.getElementById("terms-supmas").innerHTML=[
      [fmtN.format(s.kwp_nr)+" kWp",(cap?"Tope regulatorio 20 MW · ":"")+"Potencial máximo de autoconsumo"],
      [fmtN.format(req)+" m²","Superficie requerida (4.0 m²/kWp)"],
      [disp!=null?fmtN.format(disp)+" m²":"n/d","Superficie disponible hoy"],
      [falt>0?fmtN.format(falt)+" m²":"0 m²",falt>0?"m² faltantes · condición habilitante":"El techo disponible alcanza"],
      ["+"+fmt$.format(s.delta_ahorro_anio1),"Ahorro adicional cliente · año 1 vs diseño actual"]
    ].map(([v,l])=>`<div><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");
    const W=560,H=210,mL=96,mR=96,mT=28,mB=26;
    const xmax=Math.max(req,disp!=null?disp:0)*1.14||1;
    const X=v=>mL+(W-mL-mR)*v/xmax;
    const bar=(y,v,col,lab)=>`<rect x="${mL}" y="${y}" width="${Math.max(1,X(v)-mL).toFixed(1)}" height="26" rx="3" fill="${col}"/><text x="${(X(v)+6).toFixed(1)}" y="${y+18}" font-size="11" font-weight="600" fill="#221A33">${fmtN.format(Math.round(v))} m²</text><text x="${mL-8}" y="${y+18}" text-anchor="end" font-size="10" fill="rgba(34,26,51,.6)">${lab}</text>`;
    let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Superficie requerida vs disponible"><defs><pattern id="faltp" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse"><rect width="4" height="8" fill="rgba(184,116,26,.45)"/></pattern></defs>`;
    if(disp!=null) svg+=bar(mT,disp,"#4F8A6B","Disponible hoy");
    svg+=bar(mT+64,req,"#B8741A","Requerida (Op3)");
    if(falt>0 && disp!=null){ const x0=X(disp),x1=X(req);
      svg+=`<rect x="${x0.toFixed(1)}" y="${mT+64}" width="${(x1-x0).toFixed(1)}" height="26" fill="url(#faltp)"/>`
        +`<text x="${((x0+x1)/2).toFixed(1)}" y="${(mT+120).toFixed(1)}" text-anchor="middle" font-size="10" font-weight="600" fill="#B8741A">faltan ${fmtN.format(Math.round(falt))} m²</text>`;
    }
    svg+=`</svg>`;
    document.getElementById("chart-supmas").innerHTML=svg;
    const nm=META[k].name;
    document.getElementById("note-supmas").innerHTML = cap
      ? `<b>${nm}.</b> A su potencial de autoconsumo, ${nm} alcanzaría el tope regulatorio de <b>20 MW</b> (permiso CNE simplificado). Requiere <b>${fmtN.format(req)} m²</b>${disp!=null?` de ${fmtN.format(disp)} disponibles — ${fmtN.format(falt)} m² adicionales habilitan <b>+${fmt$.format(s.delta_ahorro_anio1)}/año</b>`:""}. Cota teórica del potencial máximo.`
      : (falt>0
        ? `<b>${nm}.</b> El potencial máximo requiere <b>${fmtN.format(req)} m²</b> (${fmtN.format(falt)} m² más que el techo disponible hoy): esa superficie habilita <b>+${fmt$.format(s.delta_ahorro_anio1)}/año</b> de ahorro adicional para el cliente.`
        : `<b>${nm}.</b> El techo disponible (${disp!=null?fmtN.format(disp)+" m²":"n/d"}) alcanza para el potencial máximo: <b>+${fmt$.format(s.delta_ahorro_anio1)}/año</b> de ahorro adicional para el cliente.`);
    document.getElementById("foot-supmas").textContent =
      "Opción 3 — Autoconsumo Max: cada sitio a su óptimo de autoconsumo (BESS fijo, despacho carga-solar; precios PPA re-resueltos para TIR inversionista combinada 14.0 %). Los m² requeridos y todo kWp por encima del diseño actual suponen techo, estructura e interconexión disponibles (sin visita técnica). Proplasa se trunca en el tope regulatorio de 20 MW por sitio. Prefactibilidad; densidad 4.0 m²/kWp.";
    return;
  }
'''
rep('function renderSupMas(k){\n', SUP3)

# ---- 2.18 NEW SECTION "¿Por qué este tamaño?" (after #supmas, before #consumo) ----
SEC_OPTIMO = '''<section class="page" id="optimo">
  <style>
    #optimo .pkbanner{display:flex;gap:.7rem;align-items:baseline;flex-wrap:wrap;margin:.2rem 0 1rem;
      font-size:.8rem;color:var(--ink-60);border-left:2px solid var(--s-amber);padding-left:.9rem}
    #optimo .pk-split{margin:.2rem 0 .1rem}
    #optimo .pk-split svg{width:100%;max-width:420px;height:auto}
    #optimo .pk-splitleg{display:flex;gap:1.1rem;flex-wrap:wrap;font-size:.68rem;color:var(--ink-60);margin:.1rem 0 .3rem}
    #optimo .pk-splitleg i.sq{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:middle;margin-right:.35rem}
    #optimo .pk-h3{font-size:1.02rem;font-weight:600;letter-spacing:-.01em;margin:.7rem 0 .4rem;color:var(--ink)}
    #optimo .pk-p{font-size:.82rem;color:var(--ink-60);line-height:1.5;margin:0 0 .8rem}
    #optimo .pk-mini{display:flex;gap:1.6rem;flex-wrap:wrap;margin:.2rem 0 .5rem}
    #optimo .pk-mini .v{font-weight:300;color:var(--ink);letter-spacing:-.01em}
    #optimo .pk-mini .l{font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-60)}
    #optimo .pk-note{font-size:.68rem;color:var(--ink-30);line-height:1.45;margin:.3rem 0 0}
    #optimo #cards-optimo table{width:100%;border-collapse:collapse;font-size:.8rem}
    #optimo #cards-optimo td{padding:.28rem 0;border-bottom:1px solid var(--line)}
    #optimo #cards-optimo tr.total td{border-bottom:none;padding-top:.5rem;color:var(--accent)}
  </style>
  <div class="pagenum">El óptimo técnico-económico</div>
  <div class="eyebrow" id="eyebrow-optimo">El óptimo técnico-económico · Autoconsumo Max (Op3)</div>
  <h2>¿Por qué este tamaño?</h2>
  <p id="intro-optimo"></p>
  <div id="banner-optimo"></div>
  <div class="tabs" id="tabs-optimo" role="tablist"></div>
  <div class="subtabs" id="sub-optimo" hidden></div>
  <div class="layout-sb">
    <aside class="terms" id="terms-optimo"></aside>
    <div>
      <div class="chart" id="chart-optimo"></div>
      <div class="legend" id="leg-optimo">
        <span><i style="background:#8F3A81"></i>Ahorro cliente año 1 vs potencia PV</span>
        <span><i class="sq" style="background:#B8741A"></i>Pico (óptimo interior)</span>
        <span><i class="sq" style="background:#621558"></i>Punto de diseño (Op3)</span>
      </div>
      <div class="mas-note" id="note-optimo"></div>
    </div>
  </div>
  <div class="cardgrid" id="cards-optimo"></div>
  <p class="foot-note" id="foot-optimo"></p>
</section>

'''
rep('</section>\n\n<!-- 7 · CONSUMO HOY -->',
    '</section>\n\n' + SEC_OPTIMO + '<!-- 7 · CONSUMO HOY -->')

# ---- 2.19 renderPeak JS + tabs + cards (registered for OP re-render) ----
PEAK_JS = r'''
// ---------- ¿POR QUÉ ESTE TAMAÑO? — óptimo técnico-económico (peak_analysis) ----------
const PK = MODEL.peak;
const _sm = v => (v<0?"−":"")+"$"+fmt1.format(Math.abs(v)/1e6)+" M";
function pkSplitBar(sp,x0,y,w,h){
  const cols={a:"#621558",b:"#4356A5",c:"#B8741A"};
  let x=x0,out="";
  [["a",sp.a],["b",sp.b],["c",sp.c]].forEach(([key,f])=>{ const ww=w*f;
    out+=`<rect x="${x.toFixed(1)}" y="${y}" width="${Math.max(0,ww).toFixed(1)}" height="${h}" rx="1.5" fill="${cols[key]}"/>`;
    if(f>=0.09) out+=`<text x="${(x+ww/2).toFixed(1)}" y="${(y+h/2+3.4).toFixed(1)}" text-anchor="middle" font-size="9" font-weight="600" fill="#fff">${Math.round(f*100)}%</text>`;
    x+=ww; });
  return out;
}
function renderPeak(k){
  const kk = PK.sites[k] ? k : "pro";
  const s  = PK.sites[kk];
  const eb=document.getElementById("eyebrow-optimo"), intro=document.getElementById("intro-optimo"), ban=document.getElementById("banner-optimo");
  if(eb) eb.textContent = "El óptimo técnico-económico · Autoconsumo Max (Op3)";
  if(intro) intro.textContent = "Cada kWp adicional se reparte en tres cubetas: (a) autoconsumo directo —limitado por la carga diurna—, (b) carga solar del BESS —acotada por la energía que el BESS descarga en punta (N/RTE), no por el sol— y (c) excedente vendido a CFE a valor mayorista (≈ $0 en autoconsumo). Cuando (a) y (b) se saturan, el kWh siguiente cae en (c) a $0 mientras la inversión marginal encarece el PPA de todos los kWh: por eso el ahorro del cliente hace pico. Aquí, por sitio.";
  if(ban) ban.innerHTML = OP===2 ? "" :
    `<div class="pkbanner"><span class="chip">Dimensionamiento · Opción 3</span><span>El punto de diseño marcado corresponde a la Opción 3 — Autoconsumo Max (superficie sin restricción). Selecciónela en el conmutador superior para ver el escenario completo; la física del óptimo es la misma en todo tamaño.</span></div>`;

  const rising=s.rising, optC=s.split_opt.c, satC=s.split_sat?s.split_sat.c:null;
  document.getElementById("terms-optimo").innerHTML=[
    [fmtN.format(s.kwp_nr)+" kWp",(rising?"Tope regulatorio 20 MW · ":"")+"Punto de diseño · máximo ahorro cliente"],
    [Math.round(s.sat_opt)+" %","Saturación del BESS con sol · carga solar ÷ energía de carga fija"],
    [fmtN.format(Math.round(s.ceiling.addressable/1000))+" MWh","Techo direccionable · autoconsumo diurno + N de punta"],
    [(s.split_opt.d>=0?"+":"−")+"$"+fmtN.format(Math.abs(Math.round(s.split_opt.d)))+"/kWp","Valor del kWp marginal en el óptimo"],
    [rising ? "sube · +$"+fmtN.format(Math.round(s.split_opt.d))+"/kWp"
            : Math.round(optC*100)+" % → "+Math.round(satC*100)+" %",
     rising ? "En el tope la curva aún crece · cota regulatoria" : "Excedente a $0 del kWp marginal · óptimo → saturación"]
  ].map(([v,l])=>`<div><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");

  // savings-vs-kWp curve
  const cv=s.curve, W=560,H=280,mL=64,mR=16,mT=22,mB=40;
  const xs=cv.map(c=>c.kwp), ys=cv.map(c=>c.ah);
  const xmin=Math.min(...xs), xmax=Math.max(...xs)*1.012;
  const ymax=Math.max(...ys)*1.08, ymin=0;
  const X=v=>mL+(W-mL-mR)*(v-xmin)/(xmax-xmin);
  const Y=v=>mT+(H-mT-mB)*(1-(v-ymin)/(ymax-ymin));
  let axis="";
  const ystep=[1e6,2e6,5e6,1e7,2e7].find(st=>ymax/st<=4.4)||2e7;
  for(let v=0;v<=ymax;v+=ystep){axis+=`<line x1="${mL}" y1="${Y(v).toFixed(1)}" x2="${W-mR}" y2="${Y(v).toFixed(1)}" stroke="rgba(34,26,51,.07)"/><text x="${mL-8}" y="${(Y(v)+4).toFixed(1)}" text-anchor="end" font-size="10" fill="rgba(34,26,51,.5)">${fMM(v)}</text>`;}
  let xt="";[[xmin,"start"],[(xmin+xmax)/2,"middle"],[xmax,"end"]].forEach(([v,an])=>{xt+=`<text x="${X(v).toFixed(1)}" y="${H-8}" text-anchor="${an}" font-size="9" fill="rgba(34,26,51,.5)">${fmtN.format(Math.round(v))} kWp</text>`;});
  const pts=cv.map(c=>[X(c.kwp),Y(c.ah)]);
  let line=`M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  for(let i=1;i<pts.length;i++)line+=`L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
  const area=line+`L${X(cv[cv.length-1].kwp).toFixed(1)},${Y(0).toFixed(1)}L${X(cv[0].kwp).toFixed(1)},${Y(0).toFixed(1)}Z`;
  const yat=xv=>{ if(xv<=xs[0])return ys[0]; if(xv>=xs[xs.length-1])return ys[ys.length-1];
    for(let i=0;i<cv.length-1;i++){ if(xv>=xs[i]&&xv<=xs[i+1]){const t=(xv-xs[i])/(xs[i+1]-xs[i]);return ys[i]+t*(ys[i+1]-ys[i]);}} return ys[ys.length-1]; };
  const mkr=(xv,col,txt,ly,an)=>{const px=X(xv),py=Y(yat(xv));
    return `<line x1="${px.toFixed(1)}" y1="${mT}" x2="${px.toFixed(1)}" y2="${(H-mB).toFixed(1)}" stroke="${col}" stroke-width="1" stroke-dasharray="3 3" opacity=".75"/><circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="4" fill="${col}"/><text x="${px.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="${an||'middle'}" font-size="8.5" font-weight="600" fill="${col}">${txt}</text>`;};
  let mk;
  if(rising){ mk=mkr(s.kwp_nr,"#621558","diseño = tope 20 MW",mT-6,"end"); }
  else{ const close=Math.abs(X(s.peak_kwp)-X(s.kwp_nr))<58;
    mk = mkr(s.peak_kwp,"#B8741A","pico",mT-6,close?"start":"middle")
       + mkr(s.kwp_nr,"#621558","diseño",close?mT+9:mT-6,close?"end":"middle"); }
  document.getElementById("chart-optimo").innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Ahorro cliente año 1 vs potencia PV, ${s.name}">
    ${axis}${xt}<path d="${area}" fill="rgba(143,58,129,.10)"/><path d="${line}" fill="none" stroke="#8F3A81" stroke-width="2.2"/>${mk}</svg>`;

  // marginal-split mini-viz (a/b/c at optimum vs past optimum)
  const sw=400,sh=(rising?46:82),bx=6,bw=sw-12-96;
  let ssvg=`<svg viewBox="0 0 ${sw} ${sh}" role="img" aria-label="Reparto del kWp marginal, ${s.name}">`;
  ssvg+=`<text x="${bx}" y="12" font-size="9" font-weight="600" fill="rgba(34,26,51,.62)">EN EL ÓPTIMO</text>`
      + pkSplitBar(s.split_opt,bx,17,bw,16)
      + `<text x="${bx+bw+6}" y="29" font-size="8.5" fill="rgba(34,26,51,.62)">${Math.round(optC*100)}% a CFE (≈$0)</text>`;
  if(!rising){
    ssvg+=`<text x="${bx}" y="54" font-size="9" font-weight="600" fill="rgba(34,26,51,.62)">PASADO EL ÓPTIMO</text>`
        + pkSplitBar(s.split_sat,bx,59,bw,16)
        + `<text x="${bx+bw+6}" y="71" font-size="8.5" fill="rgba(34,26,51,.62)">${Math.round(satC*100)}% a CFE (≈$0)</text>`;
  }
  ssvg+=`</svg>`;
  document.getElementById("note-optimo").innerHTML =
    `<div class="pk-split">${ssvg}</div>`
    + `<div class="pk-splitleg"><span><i class="sq" style="background:#621558"></i>autoconsumo directo (a)</span><span><i class="sq" style="background:#4356A5"></i>carga solar del BESS (b)</span><span><i class="sq" style="background:#B8741A"></i>excedente a CFE ≈ $0 (c)</span></div>`
    + `<p style="margin:.5rem 0 0;font-size:.82rem;color:var(--ink-60);line-height:1.5">`
    + (rising
        ? `<b>${s.name} — cota regulatoria.</b> El consumo es tan grande que 20 MW apenas cubre el <b>${Math.round(s.sat.self_pct)}%</b> del techo diurno y satura el BESS al <b>${Math.round(s.sat_opt)}%</b>: la curva aún sube (marginal <b>+$${fmtN.format(Math.round(s.split_opt.d))}/kWp</b>). El tamaño lo limita la regulación y la superficie, no la economía — hay potencial adicional si el predio existiera.`
        : `<b>${s.name}.</b> En el óptimo el excedente a $0 es apenas el <b>${Math.round(optC*100)}%</b> del kWp marginal; pasado el óptimo salta a <b>${Math.round(satC*100)}%</b> mientras el precio PPA de <i>todos</i> los kWh sube (TIR inversionista 14%). Ese cruce — no la superficie — fija el tamaño de máximo ahorro.`)
    + `</p>`;

  document.getElementById("foot-optimo").textContent =
    "Prefactibilidad · escenario Autoconsumo Max (Op3): motor de despacho carga-solar + mecánica de umbral golden (RPU 780881200029 intacto). Ahorro año 1 por sitio reproducido peso-exacto vs el modelo del deck; VAN portafolio $617.2 M. Datos GEPP mensuales + curva de giro industrial escalada + campana solar sintética, sin medición 15-minutal. Óptimo por sitio a base individual (PPA re-resuelto a TIR inversionista 14 %). Densidad 4.0 m²/kWp.";
}
function buildPeakCards(){
  const P=PK.portfolio, ix=PK.sites.ixt;
  const scaleRow = ix.bess_scale.filter(r=>r.scale===1||r.scale===2||r.scale===3).map(r=>
    `<div><div class="v" style="font-size:1.05rem">${_sm(r.ahorro_opt)}</div><div class="l">BESS ×${r.scale}</div></div>`).join("");
  const bonos=["ixt","aca","can","pro"].map(k=>PK.sites[k].verdict.bono);
  const bmin=Math.min(...bonos), bmax=Math.max(...bonos);
  const dvRows=["ixt","aca","can","pro"].map(k=>{const s=PK.sites[k];
    return `<tr><td>${s.name}</td><td style="text-align:right"><b>+${_sm(s.verdict.delta_van)}</b></td></tr>`;}).join("");
  document.getElementById("cards-optimo").innerHTML = `
   <div class="card">
     <span class="chip">Palanca BESS · saturada</span>
     <h3 class="pk-h3">¿Más batería desbloquearía más solar?</h3>
     <p class="pk-p">No. La capacidad del BESS ya aporta el <b>100 %</b> de su recorte en punta; escalar el BESS ×1.5 / ×2 / ×3 mueve el óptimo <b>≤ +50 kWp</b> mientras el ahorro del cliente cae — el costo de batería (${fmtN.format(P.capex_bess_per_kwh)} $/kWh) no se recupera con los ciclos adicionales. El dimensionamiento PV + BESS actual es el óptimo conjunto.</p>
     <div class="pk-mini">${scaleRow}</div>
     <p class="pk-note">Ahorro cliente año 1 en el óptimo (Ixtlahuacán) al escalar el BESS · a ×3 el ciclo extra ya no se paga.</p>
   </div>
   <div class="card">
     <span class="chip ok">Piso conservador</span>
     <h3 class="pk-h3">Umbral energético: los números son un piso</h3>
     <p class="pk-p">El modelo de demanda del libro se auditó contra la mecánica fina de umbral — demanda facturable = mín(máx kW medido, kWh de red ÷ (días · 0.57 · 24)). El libro <b>subestima</b> el ahorro de demanda ≈ <b>${Math.abs(P.umbral_delta_pct).toFixed(1)} %</b> del portafolio: lo publicado es un piso.</p>
     <div class="pk-mini">
       <div><div class="v" style="font-size:1.05rem">+${_sm(Math.abs(P.umbral_delta))}</div><div class="l">Ahorro/año no reclamado</div></div>
       <div><div class="v" style="font-size:1.05rem">−${Math.abs(P.umbral_delta_pct).toFixed(1)} %</div><div class="l">Libro vs mecánica fina</div></div>
     </div>
     <p class="pk-note">Auditado con la lógica de umbral golden (RPU 780881200029 intacto).</p>
   </div>
   <div class="card">
     <span class="chip ok">CON BESS &gt; SIN BESS · 4 / 4 sitios</span>
     <h3 class="pk-h3">Con carga solar, el BESS gana relevancia</h3>
     <p class="pk-p">Lejos de volverse irrelevante: con carga solar el ciclo del BESS es casi gratis (bono ${_sm(bmin)}–${_sm(bmax)}/año por sitio) y <b>CON BESS supera a SIN BESS</b> en VAN a 20 años en los 4 sitios — además del respaldo que la regulación exige a generación intermitente ≥ 0.7 MW.</p>
     <div class="tablewrap"><table><tbody>${dvRows}<tr class="total"><td>Portafolio · ΔVAN 20 a</td><td style="text-align:right"><b>+${_sm(P.delta_van)}</b></td></tr></tbody></table></div>
     <p class="pk-note">VAN 20 años CON vs SIN BESS a kWp óptimo por sitio (prefactibilidad).</p>
   </div>`;
}
makeSiteTabs("tabs-optimo","sub-optimo",renderPeak);
buildPeakCards();
'''
rep('makeSiteTabs("tabs-supmas","sub-supmas",renderSupMas);\n\nsetOp(0);',
    'makeSiteTabs("tabs-supmas","sub-supmas",renderSupMas);\n' + PEAK_JS + '\nsetOp(0);')

# ============================================================ 3. GATES + WRITE
# Gate: MODEL splice byte-identical to gepp_data_nr_deck.json
assert new_model[:-1] in html, 'MODEL not present verbatim'
disk = open(DECKJSON, encoding='utf-8').read()
assert ('const MODEL = ' + disk + ';') in html, 'MODEL splice NOT byte-identical to gepp_data_nr_deck.json'

open(OUT, 'w', encoding='utf-8').write(html)

# extract the new main <script> (minus leading newline) -> nr_script.js (for domstub)
o = html.rfind('<script>', 0, html.find('const MODEL'))
inner = html[o+len('<script>'):html.index('</script>', o)]
open(NRSCRIPT, 'w', encoding='utf-8').write(inner.lstrip('\n'))

print('wrote', OUT.split("/")[-1], len(html)//1024, 'KB')
print('wrote gepp_data_nr_deck.json', len(disk)//1024, 'KB ; nr_script.js', len(inner)//1024, 'KB')
print('GATE MODEL byte-identical: PASS')
print('Op3 portfolio: kWp', P3['kwp'], 'neto', round(P3['neto']), 'capex', round(P3['capex']),
      'cobertura', nr['portfolio']['cobertura_pct_nr'], '%')
