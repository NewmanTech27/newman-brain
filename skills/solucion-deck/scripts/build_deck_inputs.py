#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_deck_inputs.py — offer JSON -> deck MODEL fragment (issue #3).

No hand-edited MODEL JSON: everything the v5 template needs beyond the raw
bills/offer is generated here — régimen dual-run (Op1/Op2 or single-option
fallback), pricer-sourced PPA terms, 20-yr projection, synthetic despacho
24 h footnoted "ilustrativo", and the 12-mo baseline.

Both OPEN decisions are required CLI flags (no default winner):
  --target-irr   0.14 | 0.19 | ...   (TIR inversionista objetivo)
  --punta-basis  billing | calendar  (base de días punta)

Modes:
  offer JSON (any RPU):   build_deck_inputs.py OFFER.json --target-irr X --punta-basis B
  GEPP book fixture:      build_deck_inputs.py --gepp-book --target-irr X --punta-basis B

OFFER.json = { "inputs": {calc_core inputs incl. kwp/bess_kw/bess_kwh/
               yield_monthly/giro/division}, "bills": [12 cfe_savings bills],
               "site": {"superficie_m2": .., "autoab_mxn": ..} (optional) }
Engine path is calendar-only on punta days (calc_core hardcodes
punta_weekdays); --punta-basis billing there requires dias_punta on each bill
(perfil/book sourced) and only affects the despacho cap — flagged in meta.
"""
import argparse
import json
import sys

import deck_model as M


def build_from_offer(offer, target_irr, punta_basis, op2_kwp=None):
    inputs, bills = offer['inputs'], offer['bills']
    site = offer.get('site') or {}
    sup = M.supuestos()
    runs = M.dual_run(inputs, bills, op2_kwp=op2_kwp)
    options = {}
    for opk, res in (('op1', runs['op1']), ('op2', runs['op2'])):
        if res is None:
            continue
        p = res['inputs']
        # price on the RAW option inputs — re-feeding merged inputs would flip
        # pct_mode curva->manual inside calc_core.merge_inputs
        raw = inputs if opk == 'op1' else dict(inputs, kwp=p['kwp'])
        terms = M.ppa_terms(raw, bills, target_irr)
        proj = M.proj_from_deal(res, terms['precio_ppa'], terms['participacion'])
        options[opk] = dict(
            kwp=p['kwp'], bess_kw=p['bess_kw'], bess_kwh=p['bess_kwh'],
            bess_util_kwh=p['deliv'],
            superficie_req_m2=p['kwp'] * sup['m2_per_kwp'],
            regimen=res['regimen']['regimen'],
            autoconsumo=res['regimen']['autoconsumo'],
            capex_pv_mxn=p['capex_pv'], capex_bess_mxn=p['capex_bess'],
            ahorro_anio1=res['annual']['hibrido'],
            ahorro_pct=res['annual']['hibrido'] / res['annual']['antes']
            if res['annual']['antes'] else 0.0,
            ppa=terms, proj=proj,
            finance=res['finance']['Hibrido'])
    p1 = runs['op1']['inputs']
    despacho = M.synthetic_profiles(
        inputs, bills, p1['kwp'], p1['bess_kw'], p1['bess_kwh'],
        punta_basis=punta_basis, dod=p1['dod'], rte=p1['rte'],
        yield_monthly=p1['yield_monthly'])
    model = dict(
        meta=dict(target_irr=target_irr, punta_basis=punta_basis,
                  engine_punta_basis='calendar (calc_core punta_weekdays; '
                                     'billing solo afecta el despacho)',
                  single=runs['single'], nota=runs['nota'],
                  generated_by='skills/solucion-deck/scripts/build_deck_inputs.py'),
        baseline=M.baseline_12mo(bills),
        options=options,
        proj1=options['op1']['proj'],
        proj2=options['op2']['proj'] if 'op2' in options else None,
        inv=despacho['inv'], ver=despacho['ver'],
        despacho_footnote=despacho['footnote'],
        superficie_disponible_m2=site.get('superficie_m2'))
    return model


def build_gepp_book(target_irr, punta_basis):
    """GEPP fixture: book-anchored k-solve + projections for all 7 sites."""
    sup = M.supuestos()
    out = dict(meta=dict(target_irr=target_irr, punta_basis=punta_basis,
                         basis='self (PPA sobre K72 autoconsumido, rev3)',
                         portfolio='4-Sitios combinado (ixt,aca,can,pro)'))
    for op in ('op1', 'op2'):
        sol = M.solve_k_book(op, target_irr, punta_basis)
        out[op] = dict(k=sol['k'], irr=sol['irr'], sites={})
        for sk in M.SITES4 + M.SITESP:
            a = M.book_anchors(sk, op, sol['k'], punta_basis)
            r = M.proj_rows(a, sup)
            out[op]['sites'][sk] = dict(
                kwp=a['kwp'], precio_ppa=a['price'],
                participacion=a['participacion'],
                pago_anio1=r['rows'][1]['ppa'],
                participacion_anio1=r['rows'][1]['part'],
                neto_anio1=r['rows'][1]['neto'],
                tir_pv=r['tir_pv'], tir_bess=r['tir_bess'],
                van_cliente=r['van_cliente'], proj=r['rows'])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('offer', nargs='?', help='offer JSON (inputs+bills[+site])')
    ap.add_argument('--gepp-book', action='store_true',
                    help='GEPP book fixture mode (books_data.json anchors)')
    ap.add_argument('--target-irr', type=float, required=True,
                    help='TIR inversionista objetivo (decisión abierta: 0.14 vs 0.19)')
    ap.add_argument('--punta-basis', choices=M.PUNTA_BASES, required=True,
                    help='base días punta (decisión abierta: billing vs calendar)')
    ap.add_argument('--op2-kwp', type=float, default=None,
                    help='kWp del run Op2 exento (default %.1f)' % M.EXENTO_KWP)
    ap.add_argument('--out', help='write JSON here (default stdout)')
    args = ap.parse_args()

    if args.gepp_book:
        model = build_gepp_book(args.target_irr, args.punta_basis)
    else:
        if not args.offer:
            ap.error('offer JSON requerido (o --gepp-book)')
        offer = json.load(open(args.offer))
        model = build_from_offer(offer, args.target_irr, args.punta_basis,
                                 op2_kwp=args.op2_kwp)
    js = json.dumps(model, indent=1, ensure_ascii=False)
    if args.out:
        with open(args.out, 'w') as f:
            f.write(js)
        print('wrote %s' % args.out, file=sys.stderr)
    else:
        print(js)


if __name__ == '__main__':
    main()
