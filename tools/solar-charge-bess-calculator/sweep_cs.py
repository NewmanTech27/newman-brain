#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sweep_cs.py — per-site Op1 superficie/kWp sweep under the PRIMARY SELF-BASIS (rev3
continuity: PPA billed on self-consumed energy), with the carga-solar dispatch active
and BESS fixed.

DEAL-SOLVED DOCTRINE: at EACH kWp point the PPA multiplier k is RE-SOLVED so the combined
investor TIR stays 14.0000%.  (A fixed PPA under self-basis makes client savings plateau
instead of peak — ill-posed.)  The k re-solve at each point is over the 7-SITE UNION
(both books) with all other sites at their rev4 design size; the rev4 design point itself
is evaluated under the same union methodology so deltas are apples-to-apples.

Produces per site: kwp_opt, m2_opt, m2_disponibles, m2_faltantes, delta ahorro cliente
año1 / VAN vs the rev4 design point, and a ~25-pt curve
{kwp, m2, k_solved, price, ahorro_cliente_anio1_mxn, van_20a_mxn, exceso_remanente_kwh}.
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import solve_k_cs as SK

HERE = os.path.dirname(os.path.abspath(__file__))
S = SK.S
TARGET = 0.14
ALL7 = ['ixt', 'aca', 'can', 'pro', 'pr1', 'pr2', 'tap']


def design_kwp(sk):
    return D.NEW_KWP_OP1.get(sk, D.books()[sk]['op1']['26'])


def _site_cf_parts(sk, kwp):
    """(fixed, slope) 21-yr vectors: investor cf = fixed + k*slope  (affine in k).
    Self-basis anchors (C42 = K72_self)."""
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=1.0, basis='self')
    B9, B10, B11, B12 = S['B9'], S['B10'], S['B11'], S['B12']
    B18, B19 = int(S['B18']), int(S['B19'])
    B22, B23 = S['B22'], S['B23']
    fixed = [-A['capex_pv'] - A['capex_bess']]
    slope = [0.0]
    for y in range(1, 21):
        esc = (1 + B9) ** (y - 1); escp = (1 + B10) ** (y - 1)
        dpv = (1 - B11) ** (y - 1); dbe = (1 - B12) ** (y - 1)
        G = A['C44'] * esc * dbe
        Mfix = (-B22 * A['C26'] * esc) if y <= B18 else 0.0
        Msl = (A['C42'] * A['price0'] * escp * dpv) if y <= B18 else 0.0
        N = (G * A['C32'] - B23 * A['C29'] * esc) if y <= B19 else 0.0
        fixed.append(Mfix + N)
        slope.append(Msl)
    return fixed, slope


def solve_k_union(sk_override, kwp_override):
    """Re-solve k so the 7-site-union combined investor IRR = 14%, with sk_override at
    kwp_override and every other site at its rev4 design size."""
    fixed = [0.0] * 21; slope = [0.0] * 21
    for sk in ALL7:
        kwp = kwp_override if sk == sk_override else design_kwp(sk)
        f, sl = _site_cf_parts(sk, kwp)
        for y in range(21):
            fixed[y] += f[y]; slope[y] += sl[y]
    lo, hi = 0.3, 3.0
    for _ in range(120):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SK.irr(cf) < TARGET: lo = mid
        else: hi = mid
        if hi - lo < 1e-12: break
    return (lo + hi) / 2


def client_point(sk, kwp):
    """Client economics at kwp with the PPA re-solved (union-7, TIR 14%)."""
    k = solve_k_union(sk, kwp)
    c = D.books()[sk]['op1']
    r = SK.motor_annual(sk, 'op1', kwp)
    price = c['31'] * k
    C45 = r['M72_new'] + r['ahorro_bess_bruto']
    C46 = r['K72_self'] * price                  # PPA on SELF (rev3 basis)
    C47 = r['ahorro_bess_bruto'] * S['B17']
    C48 = C45 - C46 - C47
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=k, basis='self')
    van = SK.recompute(A)['C55']
    rem = r['exceso'] - r['carga_solar']
    return dict(kwp=round(kwp, 1), m2=round(kwp * D.M2_PER_KWP, 0),
                k_solved=round(k, 6), price=round(price, 4),
                ahorro_cliente_anio1_mxn=round(C48, 0), van_20a_mxn=round(van, 0),
                exceso_remanente_kwh=round(rem, 0))


def sweep_site(sitekey):
    c = D.books()[sitekey]['op1']
    kwp_rev3 = c['26']
    kwp_design = design_kwp(sitekey)
    # ~25 points spanning 0.6x .. 3.0x rev3 kWp
    step = max(10.0, round(kwp_rev3 * 2.4 / 24 / 10) * 10)
    kwps = []
    kwp = round(kwp_rev3 * 0.6 / 10) * 10
    while kwp <= kwp_rev3 * 3.0 + 1e-6:
        kwps.append(float(kwp)); kwp += step
    if not any(abs(x - kwp_design) < 1 for x in kwps):
        kwps.append(kwp_design); kwps.sort()
    curve = [client_point(sitekey, x) for x in kwps]
    design = next(p for p in curve if abs(p['kwp'] - kwp_design) < 1)
    opt = max(curve, key=lambda p: p['ahorro_cliente_anio1_mxn'])
    optv = max(curve, key=lambda p: p['van_20a_mxn'])
    m2_disp = D.M2_DISP.get(sitekey)
    return dict(site=sitekey,
                basis='self (PPA on self-consumed; k re-solved per point, union-7, TIR 14%)',
                kwp_rev3=kwp_rev3, kwp_design=kwp_design,
                kwp_opt=opt['kwp'], kwp_opt_van=optv['kwp'],
                opt_at_range_cap=(opt is curve[-1]),   # True: still rising at 3x rev3 (no excess yet; surface binds first)
                m2_opt=opt['m2'], m2_disponibles=m2_disp,
                m2_faltantes=(max(0.0, opt['m2'] - m2_disp) if m2_disp else None),
                design_point=design, opt_point=opt, opt_point_van=optv,
                delta_ahorro_anio1_opt_vs_design=round(opt['ahorro_cliente_anio1_mxn'] - design['ahorro_cliente_anio1_mxn'], 0),
                delta_van_opt_vs_design=round(optv['van_20a_mxn'] - design['van_20a_mxn'], 0),
                curve=curve)


def all_sweeps():
    return {sk: sweep_site(sk) for sk in D.SITE_KEYS}


if __name__ == '__main__':
    for sk in ALL7:
        s = sweep_site(sk)
        print(f"\n=== {sk} ===  rev3={s['kwp_rev3']:.0f} design={s['kwp_design']:.0f}  "
              f"kwp_opt={s['kwp_opt']:.0f} (VAN opt {s['kwp_opt_van']:.0f})  "
              f"m2_opt={s['m2_opt']:.0f} disp={s['m2_disponibles']} falt={s['m2_faltantes']}")
        print(f"  Δahorro opt-vs-design = {s['delta_ahorro_anio1_opt_vs_design']:,.0f}   "
              f"Δvan = {s['delta_van_opt_vs_design']:,.0f}")
        cv = s['curve']
        for p in cv[::max(1, len(cv)//8)]:
            print(f"    kWp {p['kwp']:7.0f}  k={p['k_solved']:.4f}  ahorro {p['ahorro_cliente_anio1_mxn']:>13,.0f}  "
                  f"van {p['van_20a_mxn']:>14,.0f}  rem {p['exceso_remanente_kwh']:>10,.0f}")
