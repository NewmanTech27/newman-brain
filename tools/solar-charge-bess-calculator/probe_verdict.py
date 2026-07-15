#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_verdict.py — Q4: BESS vs NO-BESS at NR sizing under SOLAR-CHARGE accounting.

At kWp_NR per site, compares two deal-consistent configs (standalone k re-solved for each
so both hit investor TIR 14%):
  CON BESS  = the NR config (PV + book BESS, solar-charge dispatch): investor = PV PPA +
              BESS participacion; client = (M72 + ahorro_bess_bruto) - K72*price - bess*B17.
  SIN BESS  = same kWp, no BESS: investor = PV PPA only; client = M72 - K72*price_pv.
              (Regulatory caveat: PV >=0.7 MW intermitente sin BESS requiere respaldo CFE
               contratado — costo NO modelado; see autoconsumo/DACG 4.5.)

Under solar-charge the BESS cycle is nearly free (bono = carga_solar*t_base), so its
arbitrage improves vs the prior grid-charge probe (which found no-BESS won client NPV at
3/6 sites).  We re-run the comparison here.  READ-ONLY.
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import solve_k_cs as SK
import sweep_cs as SW

HERE = os.path.dirname(os.path.abspath(__file__))
S = SK.S
SITES = ['ixt', 'aca', 'can', 'pro']
sw_ext = json.load(open(os.path.join(HERE, 'sweep_cs_ext.json')))
KWP_NR = {sk: float(sw_ext['sites'][sk]['standalone']['kwp_opt']) for sk in SITES}


def pv_only_parts(sk, kwp):
    """(fixed, slope) investor cf for PV-only (no BESS)."""
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=1.0, basis='self')
    B9, B10, B11 = S['B9'], S['B10'], S['B11']
    B18, B22 = int(S['B18']), S['B22']
    fixed = [-A['capex_pv']]; slope = [0.0]
    for y in range(1, 21):
        esc = (1 + B9) ** (y - 1); escp = (1 + B10) ** (y - 1); dpv = (1 - B11) ** (y - 1)
        Mfix = (-B22 * A['C26'] * esc) if y <= B18 else 0.0
        Msl = (A['C42'] * A['price0'] * escp * dpv) if y <= B18 else 0.0
        fixed.append(Mfix); slope.append(Msl)
    return fixed, slope


def solve_k(parts_fn, sk, kwp, lo=0.3, hi=8.0):
    fixed, slope = parts_fn(sk, kwp)
    for _ in range(140):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SK.irr(cf) < 0.14: lo = mid
        else: hi = mid
        if hi - lo < 1e-12: break
    return (lo + hi) / 2


def van_pv_only(sk, kwp, price):
    """Client 20-yr VAN, PV-only: Jcol = F - H."""
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=1.0, basis='self')
    B9, B11, B18 = S['B9'], S['B11'], int(S['B18'])
    B10 = S['B10']; C42, C43 = A['C42'], A['C43']
    Jcol = []
    for y in range(1, 21):
        esc = (1 + B9) ** (y - 1); escp = (1 + B10) ** (y - 1); dpv = (1 - B11) ** (y - 1)
        F = C43 * esc * dpv
        H = (C42 * price * escp * dpv) if y <= B18 else 0.0
        Jcol.append(F - H)
    return SK.npv_excel(S['B21'], Jcol), min(Jcol)


def evaluate(sk):
    kwp = KWP_NR[sk]
    c = D.books()[sk]['op1']
    r = SK.motor_annual(sk, 'op1', kwp)
    # --- CON BESS (standalone k, PV+BESS) ---
    k_con = SW._site_cf_parts and solve_k(SW._site_cf_parts, sk, kwp)
    price_con = c['31'] * k_con
    a1_con = (r['M72_new'] + r['ahorro_bess_bruto']) - r['K72_self'] * price_con \
        - r['ahorro_bess_bruto'] * S['B17']
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=k_con, basis='self')
    van_con = SK.recompute(A)['C55']
    # --- SIN BESS (standalone k, PV only) ---
    k_pv = solve_k(pv_only_parts, sk, kwp)
    price_pv = c['31'] * k_pv
    a1_sin = r['M72_new'] - r['K72_self'] * price_pv
    van_sin, minj_sin = van_pv_only(sk, kwp, price_pv)
    verdict = 'CON BESS' if van_con >= van_sin else 'SIN BESS'
    verdict_a1 = 'CON BESS' if a1_con >= a1_sin else 'SIN BESS'
    return dict(site=sk, kwp_nr=round(kwp),
                k_con=round(k_con, 5), price_con=round(price_con, 4),
                k_pv=round(k_pv, 5), price_pv=round(price_pv, 4),
                con_bess_ahorro_a1=round(a1_con), sin_bess_ahorro_a1=round(a1_sin),
                con_bess_van=round(van_con), sin_bess_van=round(van_sin),
                delta_van_con_minus_sin=round(van_con - van_sin),
                delta_a1_con_minus_sin=round(a1_con - a1_sin),
                bono_solar_charge=round(r['bonus']),
                ahorro_bess_bruto=round(r['ahorro_bess_bruto']),
                veredicto_van=verdict, veredicto_ahorro_a1=verdict_a1)


if __name__ == '__main__':
    out = {'sites': {}, 'meta': dict(
        note='Q4 BESS vs no-BESS at kWp_NR, solar-charge accounting, standalone k re-solved '
             'per config (both investor TIR 14%). SIN BESS ignores the mandatory CFE-backup '
             'contract cost (not modeled) for PV>=0.7MW intermitente.',
        kwp_nr={k: round(v) for k, v in KWP_NR.items()})}
    port = dict(con_a1=0.0, sin_a1=0.0, con_van=0.0, sin_van=0.0)
    for sk in SITES:
        e = evaluate(sk)
        out['sites'][sk] = e
        port['con_a1'] += e['con_bess_ahorro_a1']; port['sin_a1'] += e['sin_bess_ahorro_a1']
        port['con_van'] += e['con_bess_van']; port['sin_van'] += e['sin_bess_van']
        print(f"\n=== {sk}  kWp_NR={e['kwp_nr']:.0f} ===")
        print(f"  CON BESS: PPA {e['price_con']:.4f}  ahorro_a1 {e['con_bess_ahorro_a1']:>13,.0f}  VAN {e['con_bess_van']:>15,.0f}  (bono ${e['bono_solar_charge']:,.0f})")
        print(f"  SIN BESS: PPA {e['price_pv']:.4f}  ahorro_a1 {e['sin_bess_ahorro_a1']:>13,.0f}  VAN {e['sin_bess_van']:>15,.0f}")
        print(f"  ΔVAN(con-sin) {e['delta_van_con_minus_sin']:>+15,.0f}  Δa1 {e['delta_a1_con_minus_sin']:>+13,.0f}  -> VAN:{e['veredicto_van']}  a1:{e['veredicto_ahorro_a1']}")
    out['portfolio'] = dict(
        con_bess_ahorro_a1=round(port['con_a1']), sin_bess_ahorro_a1=round(port['sin_a1']),
        con_bess_van=round(port['con_van']), sin_bess_van=round(port['sin_van']),
        delta_van=round(port['con_van'] - port['sin_van']),
        veredicto_van=('CON BESS' if port['con_van'] >= port['sin_van'] else 'SIN BESS'))
    print(f"\nPORTFOLIO(4-row) VAN con {port['con_van']:,.0f} vs sin {port['sin_van']:,.0f}  -> {out['portfolio']['veredicto_van']}")
    json.dump(out, open(os.path.join(HERE, 'probe_verdict.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nwrote probe_verdict.json')
