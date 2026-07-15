#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_bess_scale.py — Q2: is the PV peak an artifact of the FIXED BESS?

Step 1 (cheap check): decompose what binds N each month at kWp_NR — if N is bound by
kwh_punta (load), a bigger BESS adds nothing to discharge.  We already know capacidad Q
is saturated (min(1,C30/Qdiv)=1 at all sites), so more BESS energy adds ZERO capacidad.

Step 2 (co-opt): scale BESS power+energy x1.5/x2/x3 (C28,C29,C30 and BESS CAPEX all scale
linearly; CAPEX basis = C29*B7*1000*B4 = $/kWh from Supuestos, matches the books exactly),
re-sweep kWp coarsely with the standalone k RE-SOLVED at each point INCLUDING the scaled
BESS CAPEX + O&M, and report whether the client-savings optimum kWp / ahorro moves up.

Mutates the in-memory books dict for a site (restored after), clearing SK._MOTOR_CACHE.
READ-ONLY on files.
"""
import json, os, sys, copy
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import sweep_cs as SW
import solve_k_cs as SK

HERE = os.path.dirname(os.path.abspath(__file__))
SITES = ['ixt', 'aca', 'can', 'pro']
KWP_CAP = 20000.0
sw_ext = json.load(open(os.path.join(HERE, 'sweep_cs_ext.json')))
KWP_NR = {sk: float(sw_ext['sites'][sk]['standalone']['kwp_opt']) for sk in SITES}
SCALES = [1.0, 1.5, 2.0, 3.0]


def N_binding(sk):
    B = D.books(); s = B[sk]; c = s['op1']; C28 = c['28']
    rows = []
    for i in range(12):
        dias = s['dias_punta'][i]; hrs = s['hrs_punta'][i]; kp = s['kwh_punta'][i]
        terms = {'energy(C30·d)': c['30'] * dias, 'power(C28·h·d)': C28 * hrs * dias, 'punta(kWh)': kp}
        b = min(terms, key=terms.get)
        rows.append(b)
    from collections import Counter
    return Counter(rows)


def scaled_book(sk, f):
    """Return a deep copy of one site's op1 with BESS power+energy+CAPEX scaled by f."""
    c = D.books()[sk]['op1']
    orig = {k: c[k] for k in ('28', '29', '30', '36')}
    c['28'] = orig['28'] * f
    c['29'] = orig['29'] * f
    c['30'] = orig['30'] * f
    c['36'] = orig['36'] * f            # capex_bess = C29*B7*1000*B4 -> scales linearly
    SK._MOTOR_CACHE.clear()
    return orig


def restore_book(sk, orig):
    c = D.books()[sk]['op1']
    for k, v in orig.items():
        c[k] = v
    SK._MOTOR_CACHE.clear()


def solve_k_standalone(sk, kwp):
    fixed, slope = SW._site_cf_parts(sk, kwp)
    lo, hi = 0.3, 6.0
    for _ in range(120):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SK.irr(cf) < 0.14: lo = mid
        else: hi = mid
        if hi - lo < 1e-12: break
    return (lo + hi) / 2


def client_pt(sk, kwp):
    k = solve_k_standalone(sk, kwp)
    c = D.books()[sk]['op1']
    r = SK.motor_annual(sk, 'op1', kwp)
    price = c['31'] * k
    ah = (r['M72_new'] + r['ahorro_bess_bruto']) - r['K72_self'] * price \
        - r['ahorro_bess_bruto'] * SK.S['B17']
    return dict(kwp=kwp, ahorro=ah, k=k, N=r['N'], carga_solar=r['carga_solar'],
                bono=r['bonus'], bess_bruto=r['ahorro_bess_bruto'])


def sweep_opt(sk):
    """Coarse standalone kWp sweep -> optimum (200 grid, 50 refine)."""
    c = D.books()[sk]['op1']; rev3 = c['26']
    kwps = []
    x = round(rev3 * 0.6 / 100) * 100
    while x <= KWP_CAP + 1e-6:
        kwps.append(float(x)); x += 200.0
    if kwps[-1] < KWP_CAP: kwps.append(KWP_CAP)
    pts = {x: client_pt(sk, x) for x in kwps}
    best = max(pts.values(), key=lambda p: p['ahorro'])
    x = max(kwps[0], best['kwp'] - 200)
    while x <= min(KWP_CAP, best['kwp'] + 200) + 1e-6:
        if x not in pts: pts[x] = client_pt(sk, x)
        x += 50.0
    best = max(pts.values(), key=lambda p: p['ahorro'])
    return best


if __name__ == '__main__':
    out = {'sites': {}, 'meta': dict(
        scales=SCALES,
        capex_basis='BESS CAPEX = C29(kWh)*B7(0.28)*1000*FX(17.55) = $4914/kWh; scales linearly '
                    'with BESS energy. O&M BESS = B23(180)*C29 also scales. Capacidad Q=min(1,C30/Qdiv) '
                    'already =1 at all sites -> more BESS energy adds ZERO capacidad savings.',
        note='Step2: standalone k re-solved per kWp with scaled BESS CAPEX+O&M included.')}
    for sk in SITES:
        binds = N_binding(sk)
        print(f"\n=== {sk}  kWp_NR={KWP_NR[sk]:.0f} ===")
        print(f"  N binding@kWp_NR (months): {dict(binds)}")
        base = client_pt(sk, KWP_NR[sk])
        rows = []
        for f in SCALES:
            orig = scaled_book(sk, f)
            best = sweep_opt(sk)
            rows.append(dict(scale=f, kwp_opt=round(best['kwp'], 0), ahorro_opt=round(best['ahorro'], 0),
                             N_annual=round(best['N'], 0), carga_solar=round(best['carga_solar'], 0),
                             bono=round(best['bono'], 0),
                             capex_bess=round(D.books()[sk]['op1']['36'], 0)))
            restore_book(sk, orig)
        base_ah = rows[0]['ahorro_opt']; base_kwp = rows[0]['kwp_opt']
        out['sites'][sk] = dict(kwp_nr=KWP_NR[sk], N_binding_months=dict(binds), scale_rows=rows)
        for r in rows:
            dah = r['ahorro_opt'] - base_ah
            print(f"  x{r['scale']:.1f}: kWp_opt={r['kwp_opt']:>6.0f} (Δ{r['kwp_opt']-base_kwp:+.0f})  "
                  f"ahorro_opt={r['ahorro_opt']:>13,.0f} (Δ{dah:+,.0f})  N={r['N_annual']:>10,.0f}  "
                  f"capex_bess={r['capex_bess']:>13,.0f}")
    json.dump(out, open(os.path.join(HERE, 'probe_bess_scale.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nwrote probe_bess_scale.json')
