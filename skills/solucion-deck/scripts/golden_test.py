#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""golden_test.py — gates for the deck-input scripts (issue #3).

Pinned references (delivered GEPP artifacts, in-repo):
  * books_data.json caches R72/K72/M72       — rev3 book cells (motor replica)
  * gepp_data_nr_deck.json proj1/proj2       — delivered rev4 deck v9 projection
  * gepp_data_nr_deck.json sys PPA prices    — delivered deck PPA año-1 prices
  * solve_k_cs.json                          — delivered rev4 book k (TIR 14, billing)
  * motor_cs.json typical_day                — delivered rev4 book despacho columns
Where the books contain no reference (TIR 19, calendar punta basis, engine-path
dual-run/PPA/despacho) the current output is pinned in baselines.json so future
drift turns red. `--pin` regenerates baselines.json (review the diff!).

Run:  python3 golden_test.py [--pin]
"""
import argparse
import json
import os
import sys

import deck_model as M

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINES = os.path.join(HERE, 'baselines.json')
CALC = M.CALC
DECK = json.load(open(os.path.join(CALC, 'gepp_data_nr_deck.json')))
KSOLVE = json.load(open(os.path.join(CALC, 'solve_k_cs.json')))
MOTOR = json.load(open(os.path.join(CALC, 'motor_cs.json')))
IMPORTED = os.path.join(M.REPO, 'cfe', 'vault', 'imported')

FAILS = []


def check(name, ok, detail=''):
    print('  [%s] %s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        FAILS.append(name)


def close(a, b, rel=1e-6, abs_=1e-6):
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if a is None or b is None:
        return a is b
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def deep_close(a, b, path=''):
    """Recursive numeric compare; returns list of mismatch paths."""
    bad = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                bad.append('%s.%s (missing)' % (path, k))
            else:
                bad += deep_close(a[k], b[k], '%s.%s' % (path, k))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            bad.append('%s (len %d vs %d)' % (path, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                bad += deep_close(x, y, '%s[%d]' % (path, i))
    elif not close(a, b):
        bad.append('%s (%r vs %r)' % (path, a, b))
    return bad


# ---------------------------------------------------------------- fixture
def ixt_offer():
    """GEPP Ixtlahuacán engine-path fixture: vault bills + rev4 Op1 design
    (kwp 5170, BESS rev3 verano-2h 3700/7400), monthly yields from the book,
    dias_punta attached from the book perfil (billing punta basis)."""
    base = os.path.join(IMPORTED, 'gepp-ixtlahuacan')
    bills = json.load(open(os.path.join(base, 'bills.json')))
    inputs = json.load(open(os.path.join(base, 'inputs.json')))
    s = M.D.books()['ixt']
    ym = {int(s['months'][i]): s['yield'][i] for i in range(12)}
    dias = {int(s['months'][i]): s['dias_punta'][i] for i in range(12)}
    for b in bills:
        b['dias_punta'] = dias[b['month']]
    c = M.D.books()['ixt']['op1']
    inputs = dict(inputs, kwp=5170.0, yield_monthly=ym,
                  bess_kw=c['28'], bess_kwh=c['29'])
    return inputs, bills


# ---------------------------------------------------------------- gates
def g1_motor_replica():
    print('G1 — motor replica (old kWp, solar OFF) vs rev3 book R72/K72/M72:')
    B = M.D.books()
    worst = 0.0
    for sk in M.SITES4 + M.SITESP:
        for op in ('op1', 'op2'):
            r = M.D.motor_site(sk, op, B[sk][op]['26'], solar_charge=False)['annual']
            ca = B[sk][op]['cache']
            worst = max(worst,
                        abs(r['R_new'] / ca['R72'] - 1),
                        abs(r['K72_self'] / ca['K72'] - 1),
                        abs(r['M72_new'] / ca['M72'] - 1))
    check('rev3 replica worst dev', worst < 1e-3, '%.5f%%' % (worst * 100))


def g2_projection_vs_deck():
    print('G2 — 20-yr projection vs delivered rev4 deck proj1/proj2 (7 sites × 2 ops):')
    sup = M.supuestos()
    worst, worst_at = 0.0, ''
    for sk in M.SITES4 + M.SITESP:
        for op, pk in (('op1', 'proj1'), ('op2', 'proj2')):
            k = KSOLVE[op]['k_selfbasis']
            r = M.proj_rows(M.book_anchors(sk, op, k, 'billing'), sup)
            ref = DECK['sites'][sk][pk]
            for mine, theirs in zip(r['rows'][1:], ref[1:]):
                for f in ('pleno', 'autoab', 'real', 'apv', 'abess',
                          'ppa', 'part', 'neto', 'acum'):
                    d = abs(mine[f] - theirs[f]) / max(1.0, abs(theirs[f]))
                    if d > worst:
                        worst, worst_at = d, '%s %s yr%s %s' % (sk, op, mine['yr'], f)
    check('proj vs deck worst rel dev', worst < 2e-4,
          '%.2e (@ %s)' % (worst, worst_at))
    k1 = KSOLVE['op1']['k_selfbasis']
    r = M.proj_rows(M.book_anchors('ixt', 'op1', k1, 'billing'), sup)
    ref = DECK['sites']['ixt']['proj1']
    print('    ixt op1 año1: neto %.2f (deck %.2f), año20 acum %.0f (deck %.0f)'
          % (r['rows'][1]['neto'], ref[1]['neto'],
             r['rows'][20]['acum'], ref[20]['acum']))


def g3_ppa_book(baseline, pin):
    print('G3 — PPA pricing (book k-solve), matrix target TIR × punta basis:')
    out = {}
    for basis in M.PUNTA_BASES:
        for tgt in (0.14, 0.19):
            key = '%s_tir%02d' % (basis, round(tgt * 100))
            rec = {}
            for op in ('op1', 'op2'):
                sol = M.solve_k_book(op, tgt, basis)
                price_ixt = M.D.books()['ixt'][op]['31'] * sol['k']
                a = M.book_anchors('ixt', op, sol['k'], basis)
                r = M.proj_rows(a, M.supuestos())
                rec[op] = dict(k=sol['k'], irr=sol['irr'],
                               price_ixt=price_ixt,
                               ixt_neto_anio1=r['rows'][1]['neto'],
                               ixt_van_cliente=r['van_cliente'])
                print('    {:<8s} TIR {:.0f}% {}: k={:.8f}  ixt precio ${:.6f}'
                      '  neto a1 ${:,.0f}'.format(basis, tgt * 100, op,
                                                  sol['k'], price_ixt,
                                                  r['rows'][1]['neto']))
            out[key] = rec
    # delivered references: rev4 book/deck = billing basis @ TIR 14
    b14 = out['billing_tir14']
    check('k op1 @14/billing vs solve_k_cs.json',
          close(b14['op1']['k'], KSOLVE['op1']['k_selfbasis'], rel=1e-6))
    check('k op2 @14/billing vs solve_k_cs.json',
          close(b14['op2']['k'], KSOLVE['op2']['k_selfbasis'], rel=1e-6))
    sysrow = DECK['sites']['ixt']['sys']['Precio PPA (MXN/kWh, año 1)']
    check('precio ixt op1 vs deck sys', close(b14['op1']['price_ixt'], sysrow[0], abs_=1e-5))
    check('precio ixt op2 vs deck sys', close(b14['op2']['price_ixt'], sysrow[1], abs_=1e-5))
    _pin_or_compare('ppa_book_matrix', out, baseline, pin,
                    skip=('billing_tir14',))  # billing@14 already book-pinned
    return out


def g4_dual_run(baseline, pin):
    print('G4 — régimen dual-run (calc_core, GEPP ixt fixture):')
    inputs, bills = ixt_offer()
    runs = M.dual_run(inputs, bills)
    r1, r2 = runs['op1'], runs['op2']
    check('op1 régimen = autoconsumo simplificado',
          r1['regimen']['regimen'].startswith('AUTOCONSUMO interconectado'))
    check('op2 régimen = generador exento',
          r2['regimen']['regimen'].startswith('GENERADOR EXENTO'))
    check('dual-run no single', not runs['single'])
    single = M.dual_run(dict(inputs, kwp=500.0), bills)
    check('kwp<700 -> single-option fallback',
          single['single'] and single['op2'] is None)
    rec = dict(
        op1=dict(regimen=r1['regimen']['regimen'],
                 antes=r1['annual']['antes'], hibrido=r1['annual']['hibrido'],
                 pct=r1['annual']['hibrido'] / r1['annual']['antes']),
        op2=dict(regimen=r2['regimen']['regimen'], kwp=r2['inputs']['kwp'],
                 hibrido=r2['annual']['hibrido']))
    print('    op1 ahorro ${:,.0f} ({:.1f}% de ${:,.0f}) | op2 ({:.1f} kWp) '
          '${:,.0f}'.format(rec['op1']['hibrido'], rec['op1']['pct'] * 100,
                            rec['op1']['antes'], rec['op2']['kwp'],
                            rec['op2']['hibrido']))
    _pin_or_compare('dual_run_ixt', rec, baseline, pin)
    return inputs, bills, runs


def g5_ppa_engine(inputs, bills, baseline, pin):
    print('G5 — PPA terms (engine path, ppa_pricer) @ TIR 14 vs 19:')
    rec = {}
    for tgt in (0.14, 0.19):
        t = M.ppa_terms(inputs, bills, tgt)
        rec['tir%02d' % round(tgt * 100)] = dict(
            precio_ppa=t['precio_ppa'], participacion=t['participacion'],
            pago_anio1=t['pago_anio1'], cliente_anio1=t['cliente_anio1'],
            tir_financiador=t['tir_financiador'])
        check('tir_financiador==target @%.2f' % tgt,
              close(t['tir_financiador'], tgt, abs_=1e-6))
        print('    TIR {:.0f}%: precio ${:.6f}/kWh, pago a1 ${:,.0f}, '
              'cliente a1 ${:,.0f}'.format(tgt * 100, t['precio_ppa'],
                                           t['pago_anio1'], t['cliente_anio1']))
    _pin_or_compare('ppa_engine_ixt', rec, baseline, pin)


def g6_despacho(inputs, bills, baseline, pin):
    print('G6 — despacho 24 h:')
    # (a) replay: dispatcher on the delivered carga/pv reproduces the rev4
    #     book typical-day columns (motor_cs.json == book rows 152-211)
    worst = 0.0
    B = M.D.books()
    for sk in M.SITES4:
        c = B[sk]['op1']
        for seas in ('invierno', 'verano'):
            ref = MOTOR['sites'][sk]['typical_day'][seas]
            prof = M.dispatch_day([r['carga'] for r in ref],
                                  [r['pv'] for r in ref],
                                  [r['per'] for r in ref],
                                  c['28'], c['30'])
            for mine, theirs in zip(prof, ref):
                for f in ('chg', 'dis', 'neta'):
                    worst = max(worst, abs(mine[f] - theirs[f]))
    check('replay vs motor_cs typical_day (4 sitios × 2 temporadas)',
          worst < 0.02, 'worst %.4f kW' % worst)
    # (b) synthetic fallback: energy identities + both punta bases pinned
    rec = {}
    for basis in M.PUNTA_BASES:
        d = M.synthetic_profiles(inputs, bills, inputs['kwp'], inputs['bess_kw'],
                                 inputs['bess_kwh'], punta_basis=basis,
                                 yield_monthly=inputs['yield_monthly'])
        util = inputs['bess_kwh'] * 0.96 * (0.96 ** 0.5)
        for dkey in ('inv', 'ver'):
            prof = d[dkey]['prof']
            chg = -sum(r['chg'] for r in prof)
            dis = sum(r['dis'] for r in prof)
            off = [r for r in prof if r['dis'] > 0 and r['per'] != 'Punta']
            check('%s/%s carga=util/RTE' % (basis, dkey),
                  close(chg, util / M.RTE, rel=1e-3), '%.1f kWh' % chg)
            check('%s/%s descarga<=util, solo punta' % (basis, dkey),
                  dis <= util + 0.01 and not off, 'dis %.1f kWh' % dis)
        check('%s footnote ilustrativo' % basis, 'ilustrativo' in d['footnote'])
        rec[basis] = dict(inv=d['inv'], ver=d['ver'])
        print('    %s: inv dis %.1f kWh (mes %s) | ver dis %.1f kWh (mes %s)'
              % (basis, sum(r['dis'] for r in d['inv']['prof']),
                 d['inv']['design_month'],
                 sum(r['dis'] for r in d['ver']['prof']),
                 d['ver']['design_month']))
    _pin_or_compare('despacho_synthetic_ixt', rec, baseline, pin)


# ---------------------------------------------------------------- baselines
_PINNED = {}


def _pin_or_compare(key, value, baseline, pin, skip=()):
    value = json.loads(json.dumps(value))  # normalize tuples/floats
    for s in skip:
        value.pop(s, None) if isinstance(value, dict) and s in value else None
    _PINNED[key] = value
    if pin:
        print('    [PIN ] %s' % key)
        return
    if key not in baseline:
        check('baseline %s exists (run --pin)' % key, False)
        return
    bad = deep_close(value, baseline[key], key)
    check('baseline %s' % key, not bad,
          '' if not bad else '; '.join(bad[:4]) + (' …' if len(bad) > 4 else ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pin', action='store_true',
                    help='re-write baselines.json from current output')
    args = ap.parse_args()
    baseline = json.load(open(BASELINES)) if os.path.exists(BASELINES) else {}

    g1_motor_replica()
    g2_projection_vs_deck()
    g3_ppa_book(baseline, args.pin)
    inputs, bills, _ = g4_dual_run(baseline, args.pin)
    g5_ppa_engine(inputs, bills, baseline, args.pin)
    g6_despacho(inputs, bills, baseline, args.pin)

    if args.pin:
        with open(BASELINES, 'w') as f:
            json.dump(_PINNED, f, indent=1, ensure_ascii=False)
        print('wrote %s' % BASELINES)
    print()
    if FAILS:
        print('FAIL (%d): %s' % (len(FAILS), ', '.join(FAILS)))
        sys.exit(1)
    print('ALL GATES PASS')


if __name__ == '__main__':
    main()
