#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_peak_analysis.py — compose deck-ready peak_analysis.json from the four probes."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda f: json.load(open(os.path.join(HERE, f)))
peak, scale, umb, verd = L('probe_peak.json'), L('probe_bess_scale.json'), L('probe_umbral.json'), L('probe_verdict.json')
SITES = ['ixt', 'aca', 'can', 'pro']
NAME = {'ixt': 'Ixtlahuacán', 'aca': 'Acapulco', 'can': 'Cancún', 'pro': 'Proplasa'}

out = {'meta': dict(
    scenario='GEPP Carga Solar rev4 — Autoconsumo Max (NR)', model='Op1 self-basis, BESS fijo, despacho carga-solar',
    generated_by='build_peak_analysis.py', engine='dispatch_cs (motor carga-solar) + calc_core (umbral golden)',
    gate='ahorro año1 NR por sitio reproducido vs NUMBERS_NR a 0.0000% (peso-exacto); portafolio VAN $617,217,004 exacto',
    caveat='Prefactibilidad: datos mensuales GEPP + curva de giro industrial escalada + campana solar sintética; '
           'sin medición 15-min HM. Splits carga-solar/base y pct_ac son de prefactibilidad.'), 'sites': {}}

port = dict(con_a1=0.0, sin_a1=0.0, con_van=0.0, sin_van=0.0, book_dem=0.0, cc_dem=0.0)
for sk in SITES:
    pk = peak['sites'][sk]; cv = pk['curve']; sc = scale['sites'][sk]; vd = verd['sites'][sk]
    # umbral: pro -> per-meter proxy sum; others -> direct
    if sk == 'pro':
        ump = umb['proplasa_per_meter_sum']
        umbral = dict(nota='proxy per-meter (pr1+pr2+tap): pro consolidado no tiene recibos importados',
                      distrib_linear_deck=sum(umb['sites'][k]['nr']['book_distrib_linear'] for k in ['pr1','pr2','tap']),
                      book_capacidad_Q=sum(umb['sites'][k]['nr']['book_Q_capacidad'] for k in ['pr1','pr2','tap']),
                      book_demand_total=ump['book_demand_total_nr'],
                      distrib_true_calc_core=sum(umb['sites'][k]['nr']['cc_dem_pv'] for k in ['pr1','pr2','tap']),
                      capacidad_true_calc_core=ump['dem_bess_nr'],
                      cc_demand_total=ump['calc_demand_total_nr'],
                      delta_book_minus_true=ump['delta'],
                      dem_bess_rev4=ump['dem_bess_rev4'], dem_bess_nr=ump['dem_bess_nr'],
                      dem_bess_collapse=ump['dem_bess_collapse'])
    else:
        u = umb['sites'][sk]
        umbral = dict(distrib_linear_deck=u['nr']['book_distrib_linear'],
                      book_capacidad_Q=u['nr']['book_Q_capacidad'],
                      book_demand_total=u['nr']['book_demand_total'],
                      distrib_true_calc_core=u['nr']['cc_dem_pv'],
                      capacidad_true_calc_core=u['nr']['cc_dem_bess'],
                      cc_demand_total=u['nr']['cc_demand_total'],
                      delta_book_minus_true=u['delta_demand_nr'],
                      delta_pct=u['delta_demand_nr_pct'],
                      dem_bess_rev4=u['dem_bess_rev4'], dem_bess_nr=u['dem_bess_nr'],
                      dem_bess_collapse=u['dem_bess_collapse_rev4_to_nr'])
    curve = []
    for r in cv:
        row = dict(kwp=r['kwp'], ahorro_cliente_anio1=r['ahorro_cliente_anio1'],
                   sat_bess_pct=r['sat_bess_pct'])
        if 'marg' in r:
            m = r['marg']
            row['marginal'] = dict(dGen_kwh=m['dGen_kwh'], a_self=m['a_self_frac'],
                                   b_solar_charge=m['b_solarchg_frac'], c_remanente=m['c_remanente_frac'],
                                   d_ahorro_por_kwp=m['d_ahorro_per_kwp'])
        curve.append(row)
    # what binds
    at_cap = sk == 'pro'
    binder = ('truncamiento regulatorio 20 MW (curva aún subiendo, +$514/kWp marginal)' if at_cap else
              'pico económico interior: valor marginal del PV colapsa (remanente@$0 crece, cubetas self+carga-solar saturan) mientras el CAPEX acarreado a TIR-14 sube k')
    out['sites'][sk] = dict(
        name=NAME[sk], kwp_nr=pk['kwp_nr'], kwp_rev4=pk['kwp_rev4'],
        peak_type=('regulatorio' if at_cap else 'economico_interior'), binder=binder,
        ceiling=dict(daytime_load_kwh=pk['ceiling']['daytime_load_kwh'],
                     punta_N_kwh=pk['ceiling']['punta_N_kwh'],
                     punta_N_max_kwh=pk['ceiling']['punta_N_max_kwh'],
                     addressable_total_kwh=pk['ceiling']['addressable_total_kwh']),
        saturacion_at_opt=pk['saturacion_at_opt'],
        saturacion_bess_pct_at_opt=pk['saturacion_at_opt']['sat_bess_pct'],
        curve=curve,
        bess_scale=dict(N_binding_months=sc['N_binding_months'],
                        capacidad_Q_saturada=True,
                        scale_rows=sc['scale_rows'],
                        veredicto='mas BESS NO sube el optimo kWp (Δ≤+50) y destruye valor cliente '
                                  '(ahorro cae; negativo a 3x). Q capacidad ya saturada; N gana poco vs CAPEX.'),
        umbral=umbral,
        bess_verdict=dict(con_bess_ahorro=vd['con_bess_ahorro_a1'], sin_bess_ahorro=vd['sin_bess_ahorro_a1'],
                          con_bess_van=vd['con_bess_van'], sin_bess_van=vd['sin_bess_van'],
                          delta_van=vd['delta_van_con_minus_sin'], bono_solar_charge=vd['bono_solar_charge'],
                          k_con=vd['k_con'], k_pv=vd['k_pv'],
                          veredicto=vd['veredicto_van']))
    port['con_a1'] += vd['con_bess_ahorro_a1']; port['sin_a1'] += vd['sin_bess_ahorro_a1']
    port['con_van'] += vd['con_bess_van']; port['sin_van'] += vd['sin_bess_van']
    port['book_dem'] += umbral['book_demand_total']; port['cc_dem'] += umbral['cc_demand_total']

out['portfolio'] = dict(
    convencion='4-row (ixt+aca+can+pro)',
    bess_verdict=dict(con_bess_ahorro_a1=round(port['con_a1']), sin_bess_ahorro_a1=round(port['sin_a1']),
                      con_bess_van=round(port['con_van']), sin_bess_van=round(port['sin_van']),
                      delta_van=round(port['con_van'] - port['sin_van']),
                      veredicto=('CON BESS' if port['con_van'] >= port['sin_van'] else 'SIN BESS')),
    umbral=dict(book_demand_total_nr=round(port['book_dem']), cc_demand_total_nr=round(port['cc_dem']),
                delta_book_minus_true=round(port['book_dem'] - port['cc_dem']),
                delta_pct=round((port['book_dem'] / port['cc_dem'] - 1) * 100, 1)),
    nota_verdict='Bajo contabilidad carga-solar CON BESS gana en VAN y ahorro año1 en los 4 sitios — '
                 'REVIERTE la sonda previa grid-charge (no-BESS ganaba VAN en 3/6).')
json.dump(out, open(os.path.join(HERE, 'peak_analysis.json'), 'w'), ensure_ascii=False, indent=1)
print('wrote peak_analysis.json  (%d KB)' % (os.path.getsize(os.path.join(HERE, 'peak_analysis.json')) // 1024))
print('portfolio verdict:', out['portfolio']['bess_verdict']['veredicto'],
      '| con VAN %.0f sin VAN %.0f' % (port['con_van'], port['sin_van']))
print('portfolio umbral book %.0f vs calc %.0f (%.1f%%)' % (port['book_dem'], port['cc_dem'],
      (port['book_dem']/port['cc_dem']-1)*100))
