#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_peak.py — Q1 marginal decomposition around the Autoconsumo-Max (NR) optimum.

For each portfolio site (ixt, aca, can, pro) sweeps kWp on a fine grid spanning the NR
optimum and, at each kWp step, splits the MARGINAL annual generation kWh into three
mutually-exclusive buckets:
  (a) direct self-consumption  d(self)       — daytime coincident min(load,pv)
  (b) solar charge to BESS     d(carga_solar)— bounded by fixed charge_energy = N/RTE
  (c) excedente remanente      d(remanente)  — worth texc ~= 0 (Op1)
identity: dGen = d(self) + d(carga_solar) + d(remanente)  (exact, since Gen = self+exceso
and exceso = carga_solar + remanente).

Also reports the client value marginal (d_ahorro / d_kWp) with the standalone k re-solved
per point (the deal-consistent basis that defines kWp_NR), the addressable-energy ceiling
(asymptotic daytime-coincident load + punta N), and the saturation of each bucket at opt.

READ-ONLY on machinery.  Reuses dispatch_cs + sweep_cs (standalone k solve).
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import sweep_cs as SW
import solve_k_cs as SK
from load_curves import CURVES, PV_BELL, day_counts, season

HERE = os.path.dirname(os.path.abspath(__file__))
SITES = ['ixt', 'aca', 'can', 'pro']
KWP_CAP = 20000.0
sw_ext = json.load(open(os.path.join(HERE, 'sweep_cs_ext.json')))
KWP_NR = {sk: float(sw_ext['sites'][sk]['standalone']['kwp_opt']) for sk in SITES}


def daytime_load_ceiling(sk):
    """Asymptotic self-consumption ceiling = annual load during sun hours (PV_BELL>0),
    the limit of Sum min(load,pv) as kWp->inf."""
    B = D.books(); s = B[sk]
    sun_h = [h for h in range(24) if PV_BELL[h] > 0]
    tot = 0.0
    for i in range(12):
        mnum = s['months'][i]
        kwh_tot = s['kwh_base'][i] + s['kwh_inter'][i] + s['kwh_punta'][i]
        year, mn = D.month_year(mnum)
        cnt = day_counts(year, mn)
        curve = CURVES[D.GIRO]
        load_units = sum(curve[dt][h] * cnt[dt] for dt in cnt for h in range(24))
        ls = kwh_tot / load_units if load_units else 0.0
        tot += sum(curve[dt][h] * ls * cnt[dt] for dt in cnt for h in sun_h)
    return tot


def punta_ceiling(sk):
    """Max punta energy the BESS could ever displace = Sum min(kwh_punta, C28*hrs*dias)
    (power-capped, energy unconstrained) vs current N_annual."""
    B = D.books(); s = B[sk]; c = s['op1']; C28 = c['28']
    N_now = 0.0; N_max = 0.0; punta_tot = 0.0
    for i in range(12):
        dias = s['dias_punta'][i]; hrs = s['hrs_punta'][i]; kp = s['kwh_punta'][i]
        N_now += min(c['30'] * dias, C28 * hrs * dias, kp)
        N_max += min(C28 * hrs * dias, kp)
        punta_tot += kp
    return N_now, N_max, punta_tot


def point(sk, kwp):
    r = D.motor_site(sk, 'op1', kwp, solar_charge=True)['annual']
    SK._MOTOR_CACHE.clear()
    k = SW.solve_k_union(sk, kwp)  # deal-consistent; matches sweep_cs_ext primary curve
    kstd = _solve_k_standalone(sk, kwp)
    c = D.books()[sk]['op1']
    r2 = SK.motor_annual(sk, 'op1', kwp)
    charge_energy = r['N'] / D.RTE
    # standalone client year-1 (the basis that defines kWp_NR)
    price_std = c['31'] * kstd
    ah_std = (r2['M72_new'] + r2['ahorro_bess_bruto']) - r2['K72_self'] * price_std \
        - r2['ahorro_bess_bruto'] * SK.S['B17']
    return dict(kwp=kwp, gen=r['gen'], self=r['self'], exceso=r['exceso'],
                carga_solar=r['carga_solar'], carga_base=r['carga_base'],
                N=r['N'], charge_energy=charge_energy,
                remanente=r['exceso'] - r['carga_solar'],
                bonus=r['bonus'], k_std=kstd, price_std=price_std,
                ahorro_std=ah_std,
                sat_bess=r['carga_solar'] / charge_energy if charge_energy else 0.0)


def _solve_k_standalone(sk, kwp):
    fixed, slope = SW._site_cf_parts(sk, kwp)
    lo, hi = 0.3, 6.0
    for _ in range(120):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SK.irr(cf) < 0.14: lo = mid
        else: hi = mid
        if hi - lo < 1e-12: break
    return (lo + hi) / 2


def sweep(sk):
    c = D.books()[sk]['op1']; rev3 = c['26']
    opt = KWP_NR[sk]
    lo = round(rev3 * 0.6 / 50) * 50
    hi = min(KWP_CAP, opt * 1.6)
    step = max(50.0, round((hi - lo) / 40 / 50) * 50)
    kwps = []
    x = lo
    while x <= hi + 1e-6:
        kwps.append(float(x)); x += step
    for extra in (rev3, D.NEW_KWP_OP1.get(sk, rev3), opt, KWP_CAP if opt >= KWP_CAP else opt):
        if extra <= hi + 1e-6 and not any(abs(extra - k) < 1 for k in kwps):
            kwps.append(float(extra))
    kwps = sorted(set(kwps))
    pts = [point(sk, x) for x in kwps]
    # marginal decomposition between consecutive points
    curve = []
    for i, p in enumerate(pts):
        row = dict(kwp=round(p['kwp'], 0),
                   ahorro_cliente_anio1=round(p['ahorro_std'], 0),
                   k_std=round(p['k_std'], 5), price=round(p['price_std'], 4),
                   gen=round(p['gen'], 0), self=round(p['self'], 0),
                   carga_solar=round(p['carga_solar'], 0),
                   remanente=round(p['remanente'], 0),
                   sat_bess_pct=round(p['sat_bess'] * 100, 1))
        if i > 0:
            q = pts[i - 1]
            dG = p['gen'] - q['gen']
            dself = p['self'] - q['self']
            dcs = p['carga_solar'] - q['carga_solar']
            drem = p['remanente'] - q['remanente']
            dah = p['ahorro_std'] - q['ahorro_std']
            dk = p['kwp'] - q['kwp']
            row['marg'] = dict(
                dGen_kwh=round(dG, 0),
                a_self_frac=round(dself / dG, 3) if dG else None,
                b_solarchg_frac=round(dcs / dG, 3) if dG else None,
                c_remanente_frac=round(drem / dG, 3) if dG else None,
                d_ahorro_per_kwp=round(dah / dk, 0) if dk else None)
        curve.append(row)
    dl = daytime_load_ceiling(sk)
    N_now, N_max, punta_tot = punta_ceiling(sk)
    optrow = min(pts, key=lambda p: abs(p['kwp'] - opt))
    return dict(site=sk, kwp_nr=opt, kwp_rev4=D.NEW_KWP_OP1.get(sk, c['26']),
                ceiling=dict(daytime_load_kwh=round(dl, 0),
                             punta_N_kwh=round(N_now, 0),
                             punta_N_max_kwh=round(N_max, 0),
                             punta_total_kwh=round(punta_tot, 0),
                             addressable_total_kwh=round(dl + N_now, 0)),
                saturacion_at_opt=dict(
                    kwp=round(optrow['kwp'], 0),
                    self_kwh=round(optrow['self'], 0),
                    self_vs_daytime_ceiling_pct=round(optrow['self'] / dl * 100, 1),
                    carga_solar_kwh=round(optrow['carga_solar'], 0),
                    charge_energy_kwh=round(optrow['charge_energy'], 0),
                    sat_bess_pct=round(optrow['sat_bess'] * 100, 1),
                    remanente_kwh=round(optrow['remanente'], 0),
                    gen_kwh=round(optrow['gen'], 0)),
                curve=curve)


if __name__ == '__main__':
    out = {'sites': {}, 'meta': dict(
        note='Q1 marginal decomposition; standalone k re-solved per point (TIR 14%); '
             'buckets a/b/c partition marginal generation exactly.', kwp_nr=KWP_NR)}
    for sk in SITES:
        s = sweep(sk)
        out['sites'][sk] = s
        c = s['ceiling']; sa = s['saturacion_at_opt']
        print(f"\n=== {sk}  kWp_NR={s['kwp_nr']:.0f} ===")
        print(f"  ceiling: daytime_load={c['daytime_load_kwh']:,.0f}  N(punta)={c['punta_N_kwh']:,.0f}  "
              f"N_max={c['punta_N_max_kwh']:,.0f}  addressable={c['addressable_total_kwh']:,.0f}")
        print(f"  at opt: self={sa['self_kwh']:,.0f} ({sa['self_vs_daytime_ceiling_pct']:.0f}% of daytime ceiling)  "
              f"carga_solar={sa['carga_solar_kwh']:,.0f} (BESS sat {sa['sat_bess_pct']:.0f}%)  rem={sa['remanente_kwh']:,.0f}")
        # print marginal near opt
        near = [r for r in s['curve'] if 'marg' in r and abs(r['kwp'] - s['kwp_nr']) <= 4 * 200]
        for r in near[-6:]:
            m = r['marg']
            print(f"    kWp {r['kwp']:6.0f}  ahorro {r['ahorro_cliente_anio1']:>13,.0f}  "
                  f"marg[a{m['a_self_frac']} b{m['b_solarchg_frac']} c{m['c_remanente_frac']}]  "
                  f"d_ah/kWp {m['d_ahorro_per_kwp']:>8}  satBESS {r['sat_bess_pct']:.0f}%")
    json.dump(out, open(os.path.join(HERE, 'probe_peak.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nwrote probe_peak.json')
