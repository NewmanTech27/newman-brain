#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_umbral.py — Q3: umbral-energético audit of the NR deck's demand-side savings.

The NR deck (dispatch_cs L158-159) scales the distribución line LINEARLY with kWp
(distrib = sumL * kwp / M_div) and holds the capacidad line Q FIXED (Q = Qcoef *
min(1,C30/Qdiv), already =1).  Neither captures the TRUE umbral mechanics: as PV grows,
kWh_red falls -> umbral collapses -> facturable demand basis drops -> the BESS's room to
further cut demand (capacidad) SHRINKS (cannibalization).

We recompute the demand side under the GOLDEN calc_core umbral logic on imported/gepp-*
bills at rev4 kWp and at NR kWp (book BESS: bess_kw=C28, bess_kwh=C29).  calc_core's
  dem_pv      = (f_pre - f_prebess)*r_cap   (PV demand reduction via umbral collapse)
  dem_bess_h  = (f_prebess - f_post_h)*r_cap (BESS incremental demand cut, POST-PV umbral)
are the true distribución+capacidad demand savings.  We compare their sum to the book's
(distrib_linear + Q_annual) at NR kWp, per site, and show dem_bess_h rev4->NR (collapse).

calc_core BESS charge mode is grid-base (not solar-charge) — irrelevant here: the DEMAND
side (dem_pv, dem_bess_h) does not depend on charge source.  READ-ONLY (golden untouched).
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/tools')
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import calc_core
from cfe_savings import extract
import dispatch_cs as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/home/mario/CFE Brain'
sw_ext = json.load(open(os.path.join(HERE, 'sweep_cs_ext.json')))

# site-key -> imported slug (pro consolidated has no imported bills -> per-meter proxy)
SLUG = {'ixt': 'gepp-ixtlahuacan', 'aca': 'gepp-acapulco', 'can': 'gepp-cancun',
        'pr1': 'gepp-proplasa-pr1', 'pr2': 'gepp-proplasa-pr2', 'tap': 'gepp-proplasa-tap'}
KWP_NR = {sk: float(sw_ext['sites'][sk]['standalone']['kwp_opt']) for sk in SLUG}
KWP_REV4 = {sk: D.NEW_KWP_OP1.get(sk, D.books()[sk]['op1']['26']) for sk in SLUG}


def book_demand(sk, kwp):
    """Book/deck demand-side total at kwp: linear distribución + fixed capacidad Q."""
    c = D.books()[sk]['op1']
    distrib = sum(c['L']) * kwp / c['M_div']
    Qann = sum(q * min(1.0, c['30'] / c['Q_div']) for q in c['Q_coefs'])
    return distrib, Qann


def calc_core_demand(sk, kwp):
    """Golden umbral demand side at kwp with book BESS (C28 kW, C29 kWh)."""
    slug = SLUG[sk]
    c = D.books()[sk]['op1']; s = D.books()[sk]
    bills = extract.extract_folder(os.path.join(ROOT, 'imported', slug))[-12:]
    inp_file = json.load(open(os.path.join(ROOT, 'imported', slug, 'inputs.json')))
    ym = {int(s['months'][i]): float(s['yield'][i]) for i in range(12)}  # book yield (match dispatch)
    base = dict(giro=inp_file.get('giro', 'Industrial 24/7'),
                division=inp_file.get('division', 'SIN'), yield_monthly=ym,
                kwp=kwp, bess_kw=c['28'], bess_kwh=c['29'])
    res = calc_core.compute(base, bills)
    a = res['annual']
    return dict(dem_pv=a['dem_pv'], dem_bess_h=a['dem_bess_h'], arb=a['arb'],
                ah_pv=a['ah_pv'], exced=a['exced'], gen=a['gen'],
                pct_ac=a['pct_ac_avg'], antes=a['antes'])


def run(sk):
    r4, nr = KWP_REV4[sk], KWP_NR[sk]
    d4, q4 = book_demand(sk, r4);  cc4 = calc_core_demand(sk, r4)
    dN, qN = book_demand(sk, nr);  ccN = calc_core_demand(sk, nr)
    return dict(site=sk, slug=SLUG[sk], kwp_rev4=r4, kwp_nr=nr,
        rev4=dict(book_distrib_linear=round(d4), book_Q_capacidad=round(q4),
                  book_demand_total=round(d4 + q4),
                  cc_dem_pv=round(cc4['dem_pv']), cc_dem_bess=round(cc4['dem_bess_h']),
                  cc_demand_total=round(cc4['dem_pv'] + cc4['dem_bess_h']),
                  cc_pct_ac=round(cc4['pct_ac'], 3)),
        nr=dict(book_distrib_linear=round(dN), book_Q_capacidad=round(qN),
                book_demand_total=round(dN + qN),
                cc_dem_pv=round(ccN['dem_pv']), cc_dem_bess=round(ccN['dem_bess_h']),
                cc_demand_total=round(ccN['dem_pv'] + ccN['dem_bess_h']),
                cc_pct_ac=round(ccN['pct_ac'], 3), cc_exced=round(ccN['exced'])),
        delta_demand_nr=round((dN + qN) - (ccN['dem_pv'] + ccN['dem_bess_h'])),
        delta_demand_nr_pct=round(((dN + qN) / (ccN['dem_pv'] + ccN['dem_bess_h']) - 1) * 100, 1)
            if (ccN['dem_pv'] + ccN['dem_bess_h']) else None,
        dem_bess_collapse_rev4_to_nr=round(ccN['dem_bess_h'] - cc4['dem_bess_h']),
        dem_bess_rev4=round(cc4['dem_bess_h']), dem_bess_nr=round(ccN['dem_bess_h']))


if __name__ == '__main__':
    out = {'sites': {}, 'meta': dict(
        note='Q3 umbral audit. Book demand = linear distribución (sumL*kwp/M_div) + fixed '
             'capacidad Q (min(1,C30/Qdiv)=1). calc_core demand = dem_pv+dem_bess_h (golden '
             'umbral). pro = per-meter proxy (pr1+pr2+tap): consolidated pro has no imported bills.',
        kwp_nr=KWP_NR, kwp_rev4=KWP_REV4)}
    for sk in ['ixt', 'aca', 'can', 'pr1', 'pr2', 'tap']:
        r = run(sk)
        out['sites'][sk] = r
        print(f"\n=== {sk}  kWp {r['kwp_rev4']:.0f}->{r['kwp_nr']:.0f} ===")
        print(f"  BOOK  @NR: distrib_lin={r['nr']['book_distrib_linear']:>12,.0f}  Q_cap={r['nr']['book_Q_capacidad']:>12,.0f}  total={r['nr']['book_demand_total']:>12,.0f}")
        print(f"  CALC  @NR: dem_pv={r['nr']['cc_dem_pv']:>12,.0f}  dem_bess={r['nr']['cc_dem_bess']:>12,.0f}  total={r['nr']['cc_demand_total']:>12,.0f}  (pct_ac {r['nr']['cc_pct_ac']:.0%})")
        print(f"  DELTA book-vs-calc @NR: {r['delta_demand_nr']:>+13,.0f}  ({r['delta_demand_nr_pct']}%)")
        print(f"  dem_bess collapse rev4->NR: {r['dem_bess_rev4']:>12,.0f} -> {r['dem_bess_nr']:>12,.0f}  (Δ{r['dem_bess_collapse_rev4_to_nr']:+,.0f})")
    # Proplasa per-meter roll-up
    pr = ['pr1', 'pr2', 'tap']
    agg = dict(book=sum(out['sites'][k]['nr']['book_demand_total'] for k in pr),
               calc=sum(out['sites'][k]['nr']['cc_demand_total'] for k in pr),
               dem_bess_rev4=sum(out['sites'][k]['dem_bess_rev4'] for k in pr),
               dem_bess_nr=sum(out['sites'][k]['dem_bess_nr'] for k in pr))
    out['proplasa_per_meter_sum'] = dict(
        book_demand_total_nr=round(agg['book']), calc_demand_total_nr=round(agg['calc']),
        delta=round(agg['book'] - agg['calc']),
        dem_bess_rev4=round(agg['dem_bess_rev4']), dem_bess_nr=round(agg['dem_bess_nr']),
        dem_bess_collapse=round(agg['dem_bess_nr'] - agg['dem_bess_rev4']))
    print(f"\n=== Proplasa (pr1+pr2+tap) @NR: book={agg['book']:,.0f}  calc={agg['calc']:,.0f}  "
          f"delta={agg['book']-agg['calc']:+,.0f}  dem_bess {agg['dem_bess_rev4']:,.0f}->{agg['dem_bess_nr']:,.0f}")
    json.dump(out, open(os.path.join(HERE, 'probe_umbral.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nwrote probe_umbral.json')
