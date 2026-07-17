#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solar-charge parity harness (issue #5) — dispatch_cs.py vs engine.js.

Runs the GEPP rev4 prototype (tools/solar-charge-bess-calculator/dispatch_cs.py,
the code that produced the delivered $954,437/yr solar-charge bonus) and the
production engine (supabase/functions/cfe-ppa-bess/engine.js) on identical
inputs derived from books_data.json (the committed rev3-book extract behind the
delivered rev3/rev4 GEPP books), and asserts:

  A1 ALGORITHM PARITY (hard): engine.solar_charge_split() == dispatch_cs
     sim_month() carga_solar/exceso on identical args, 7 sites x 12 months,
     tol 1e-6 kWh.  Proves the hourly-dispatch port is exact.
  A2 FLAG-OFF GOLDEN (hard, the #1 gate): compute(solar_charge:false) and
     compute() with no flag at HEAD are bit-for-bit identical (JSON round-trip
     equality, inputs echo excluded) to baseline_off.json, generated from the
     PRE-FLAG engine at commit b53ad23.  Proves the flag is inert when OFF.
  A3 END-TO-END PIN (documented current state): each side reproduces its own
     pinned solar-charge bonus (prototype $954,436.41/yr == the delivered
     $954,437 claim; engine $831,890.72/yr), and the cross-model gap
     (-$122,545.69, -12.84%) is attributed with ZERO residual to the punta-day
     basis: engine uses calendar punta_weekdays(y,m) (19-22 d), prototype uses
     the rev3 book's billing-period dias_punta (22-27 d).  The bridge check
     re-runs solar_charge_split with the engine's own wd/charge-energy/exced
     and must equal compute()'s carga_solar to 1e-6 kWh.  Any OTHER divergence
     introduced later breaks A1/A3 and turns this red.

Usage:
  python3 ci/solar-charge-parity/run_parity.py                  # full parity run
  ENGINE_JS=<pre-flag engine.js> python3 ... --write-baseline   # regen baseline

Stdlib only.  JS side runs under node (same as newman-rebuild ci/golden).
"""
import json, math, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(REPO, 'tools', 'solar-charge-bess-calculator')
BASELINE = os.path.join(HERE, 'baseline_off.json')

TOL_KWH = 1e-6          # A1/A3-bridge: float-exact port, allow accumulation noise
TOL_MXN = 2.0           # A3 pins: whole-peso stability of each side's own number

# A3 pins — current state 2026-07-17 (see README.md for the full delta story).
PIN = {
    'proto':  {'ixt': 644140.06, 'aca': 143201.53, 'can': 167094.82,
               'pro': 0.0, 'pr1': 0.0, 'pr2': 0.0, 'tap': 0.0,
               'portfolio': 954436.41},   # == delivered claim $954,437/yr
    'engine': {'ixt': 559892.02, 'aca': 121613.36, 'can': 150385.35,
               'pro': 0.0, 'pr1': 0.0, 'pr2': 0.0, 'tap': 0.0,
               'portfolio': 831890.72},
}

FAILS = []
def check(ok, msg):
    print(('  [PASS] ' if ok else '  [FAIL] ') + msg)
    if not ok:
        FAILS.append(msg)
    return ok


def load_prototype():
    os.environ['BOOKS_DATA'] = os.path.join(TOOLS, 'books_data.json')
    sys.path.insert(0, TOOLS)
    sys.path.insert(0, os.path.join(REPO, 'cfe', 'vault', 'tools'))  # cfe_savings
    import dispatch_cs
    return dispatch_cs


def build_fixture(D):
    """Engine inputs+bills per site (op1, rev4 kWp) from books_data.json.

    Bills are constructed so the engine's bill-derived energy rates equal the
    book's bundled rates exactly: gen_<per> = t_<per> * kwh_<per>, flat adders
    (transmision/cenace/scnmem) = 0  =>  bnd_b/i/p = t_base/int/punta.
    Demand-side charges (capacidad/distribucion) are zeroed — parity scope is
    the solar-charge energy dispatch, not demand savings.
    bess_kw = C28 (book power cap), bess_kwh chosen so deliv == C30 (book daily
    discharge): bess_kwh = C30 / (dod*sqrt(rte)).
    """
    B = D.books()
    sites = {}
    for k in D.SITE_KEYS:
        s, c = B[k], B[k]['op1']
        kwp = D.NEW_KWP_OP1.get(k, c['26'])
        bills, ym, sim_args = [], {}, []
        for i in range(12):
            m = s['months'][i]
            y = D.month_year(m)[0]
            kb, ki, kp = s['kwh_base'][i], s['kwh_inter'][i], s['kwh_punta'][i]
            tb, ti, tp = s['t_base'][i], s['t_int'][i], s['t_punta'][i]
            ym[str(m)] = s['yield'][i]
            bills.append(dict(
                year=y, month=m, days=s['dias_mes'][i],
                kwh_base=kb, kwh_inter=ki, kwh_punta=kp,
                kw_punta=s['dem_punta'][i],
                gen_base=tb * kb, gen_inter=ti * ki, gen_punta=tp * kp,
                transmision=0.0, cenace=0.0, scnmem=0.0,
                suministro=0.0, distribucion=0.0, capacidad=0.0, bonif_fp=0.0))
            sim_args.append(dict(
                year=y, month=m, kwh_total=kb + ki + kp, gen=kwp * s['yield'][i],
                charge_energy=D.N_month(s, c, i) / D.RTE,
                dias_punta_book=s['dias_punta'][i]))
        sites[k] = dict(
            inputs=dict(kwp=kwp, yield_monthly=ym, giro='Industrial 24/7',
                        division='SIN', bess_kw=c['28'],
                        bess_kwh=c['30'] / (0.96 * math.sqrt(0.96)),
                        dod=0.96, rte=0.96, texc=0.0),
            bills=bills, sim_args=sim_args)
    return sites


def run_prototype(D):
    B = D.books()
    out = {}
    for k in D.SITE_KEYS:
        kwp = D.NEW_KWP_OP1.get(k, B[k]['op1']['26'])
        r = D.motor_site(k, 'op1', kwp, solar_charge=True)
        out[k] = dict(
            bonus=r['annual']['bonus'],
            carga_solar=[m['carga_solar_kwh'] for m in r['months']],
            exceso=[m['exceso_kwh'] for m in r['months']])
    return out


def main():
    write_baseline = '--write-baseline' in sys.argv
    D = load_prototype()
    fixture = dict(sites=build_fixture(D))

    with tempfile.TemporaryDirectory() as td:
        fxp, outp = os.path.join(td, 'fx.json'), os.path.join(td, 'out.json')
        with open(fxp, 'w') as f:
            json.dump(fixture, f)
        subprocess.run(['node', os.path.join(HERE, 'run_engine.mjs'), fxp, outp],
                       check=True)
        with open(outp) as f:
            js = json.load(f)

    if write_baseline:
        base = {k: v['off'] for k, v in js['sites'].items()}
        with open(BASELINE, 'w') as f:
            json.dump(base, f)
        print(f"baseline_off.json written from ENGINE_JS={js['engine']}")
        return 0

    proto = run_prototype(D)

    print('A1 — algorithm parity: solar_charge_split vs sim_month (identical args)')
    worst = 0.0
    for k, p in proto.items():
        for i, u in enumerate(js['sites'][k]['unit']):
            worst = max(worst, abs(u['carga_solar'] - p['carga_solar'][i]),
                        abs(u['exceso'] - p['exceso'][i]))
    check(worst <= TOL_KWH, f'7 sites x 12 months, worst |diff| = {worst:.3e} kWh (tol {TOL_KWH})')

    print('A2 — flag-OFF golden: HEAD compute(off) & compute(default) vs pre-flag b53ad23 baseline')
    with open(BASELINE) as f:
        base = json.load(f)
    for k, site in js['sites'].items():
        check(site['off'] == base[k], f'{k}: solar_charge:false bit-identical to pre-flag baseline')
        check(site['default'] == site['off'], f'{k}: no-flag default == solar_charge:false')

    print('A3 — end-to-end pin: annual.solar_charge_bonus (the $954,437/yr claim)')
    tot_p = tot_e = 0.0
    for k, p in proto.items():
        e = js['sites'][k]['on']['annual']['solar_charge_bonus']
        tot_p += p['bonus']; tot_e += e
        check(abs(p['bonus'] - PIN['proto'][k]) <= TOL_MXN,
              f"{k}: prototype bonus {p['bonus']:,.2f} == pin {PIN['proto'][k]:,.2f}")
        check(abs(e - PIN['engine'][k]) <= TOL_MXN,
              f"{k}: engine   bonus {e:,.2f} == pin {PIN['engine'][k]:,.2f}")
    check(abs(tot_p - PIN['proto']['portfolio']) <= TOL_MXN,
          f'portfolio prototype {tot_p:,.2f} == delivered claim $954,437/yr')
    check(abs(tot_e - PIN['engine']['portfolio']) <= TOL_MXN,
          f'portfolio engine {tot_e:,.2f} == pin {PIN["engine"]["portfolio"]:,.2f}')
    gap = tot_e - tot_p
    print(f'  [INFO] cross-model gap {gap:,.2f} MXN/yr ({gap/tot_p*100:.2f}%) — '
          'punta-day basis: calendar punta_weekdays vs book billing-period dias_punta')

    print('A3 — bridge: gap attribution residual (engine wd/charge/exced reproduce compute exactly)')
    worst = 0.0
    diffs = []
    for k, site in js['sites'].items():
        for i, br in enumerate(site['bridge']):
            r = site['on']['monthly'][i]
            d = abs(br['carga_solar'] - r['carga_solar'])
            worst = max(worst, d)
            if d > TOL_KWH:
                diffs.append(f"{k} m{r['month']}: bridge {br['carga_solar']:.3f} != compute {r['carga_solar']:.3f}")
    for d in diffs:
        print('    ' + d)
    check(worst <= TOL_KWH, f'zero unexplained residual, worst = {worst:.3e} kWh (tol {TOL_KWH})')

    for k in ('ixt', 'aca', 'can'):
        on = js['sites'][k]['on']
        tf = on['tir_financiador']
        print(f"  [INFO] {k}: engine TIR financiador {tf*100:.2f}% (ppa default; prototype k solved "
              f"portfolio-level at TIR 14.0%, prod target 19% — decision open, issue #5)")

    print()
    if FAILS:
        print(f'PARITY FAIL — {len(FAILS)} failing check(s):')
        for m in FAILS:
            print('  - ' + m)
        return 1
    print('PARITY OK — A1 exact, A2 flag inert, A3 pins hold with gap fully attributed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
