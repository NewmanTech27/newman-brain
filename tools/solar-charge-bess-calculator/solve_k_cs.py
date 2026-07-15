#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
solve_k_cs.py — Re-solve the PPA-price multiplier k (one per option) so the COMBINED
investor IRR (PV PPA + BESS participacion, aggregated over the 4-Sitios book) = 14.000%
under the NEW "Carga Solar" motor.  Methodology identical to gepp-deck/solve_tir14.py:
recompute the full 20-yr projection from input cells (distrust stale cache), Excel IRR by
bisection.  Only difference: for the 3 upsized sites (ixt/aca/can Op1) the motor anchors
C42(=K72 energy PPA), C43(=M72 ahorro PV), C44(=ahorro BESS bruto) and C26(kWp)+CAPEX_PV
come from dispatch_cs.motor_site (rev4); everything else is rev3.

Writes solve_k_cs.json.  READ-ONLY on the workbooks.
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = 0.14
B = D.books()
S = B['supuestos']           # B4..B26
MERMA = D.MERMA

# site-key -> 4-Sitios sheet membership
SITES4 = ['ixt', 'aca', 'can', 'pro']
SITESP = ['pr1', 'pr2', 'tap']


def irr(cf, lo=-0.9, hi=5.0):
    def npv(r): return sum(c / (1 + r) ** i for i, c in enumerate(cf))
    flo = npv(lo)
    for _ in range(400):
        mid = (lo + hi) / 2; fm = npv(mid)
        if abs(fm) < 1e-9 or hi - lo < 1e-14: return mid
        if flo * fm < 0: hi = mid
        else: lo, flo = mid, fm
    return (lo + hi) / 2


def npv_excel(rate, cfs):
    return sum(c / (1 + rate) ** (i + 1) for i, c in enumerate(cfs))


_MOTOR_CACHE = {}
def motor_annual(sitekey, op, kwp, solar=True):
    key = (sitekey, op, round(kwp, 3), solar)
    if key not in _MOTOR_CACHE:
        _MOTOR_CACHE[key] = D.motor_site(sitekey, op, kwp, solar_charge=solar)['annual']
    return _MOTOR_CACHE[key]


def anchors(sitekey, op, kwp=None, price_mult=1.0, basis='self'):
    """Recompute anchor set for one site/option at kWp (default rev4 design).
    basis='self' (PRIMARY, rev3 continuity: PPA billed on self-consumed K72) or
    basis='gen' (Option B, labeled: PPA on total generation)."""
    c = B[sitekey][op]
    if kwp is None:
        kwp = D.NEW_KWP_OP1.get(sitekey, c['26']) if op == 'op1' else c['26']
    r = motor_annual(sitekey, op, kwp)
    capex_pv = kwp * 1000 * S['B5'] * S['B4']       # C33*B4 = kWp*1000*USD/Wp*FX
    C42 = r['K72_self'] if basis == 'self' else r['K72_gen']
    return dict(
        C38=c['38'], C39_base=c['39'] - c['38'],     # C39 = N19 + C38 -> N19 part = C39-C38
        C42=C42, C43=r['M72_new'], C44=r['ahorro_bess_bruto'],
        C26=kwp, C29=c['29'], C32=S['B17'], N19=c['N19'],
        price0=c['31'], price=c['31'] * price_mult,
        capex_pv=capex_pv, capex_bess=c['36'], C51_kwp=kwp)


def recompute(A):
    """20-yr projection from anchors A (mirrors gepp site formulas / solve_tir14.recompute)."""
    B9, B10, B11, B12 = S['B9'], S['B10'], S['B11'], S['B12']
    B18, B19 = int(S['B18']), int(S['B19'])
    B22, B23, B25, B26 = S['B22'], S['B23'], int(S['B25']), int(S['B26'])
    B21w = S['B21']
    C38, C39base = A['C38'], A['C39_base']
    C42, C43, C44, C26, C29, C32, price = A['C42'], A['C43'], A['C44'], A['C26'], A['C29'], A['C32'], A['price']
    Mcol = [-A['capex_pv']]; Ncol = [-A['capex_bess']]; Jcol = []
    for y in range(1, 21):
        esc = (1 + B9) ** (y - 1); escp = (1 + B10) ** (y - 1)
        dpv = (1 - B11) ** (y - 1); dbe = (1 - B12) ** (y - 1)
        yr = B25 + (y - 1)
        C39 = (C39base + C38) * esc
        Dd = (C38 * esc) if yr <= B26 else 0.0
        E = C39 - Dd
        F = C43 * esc * dpv
        G = C44 * esc * dbe
        H = (C42 * price * escp * dpv) if y <= B18 else 0.0
        I = (G * C32) if y <= B19 else 0.0
        J = F + G - H - I
        M = (H - B22 * C26 * esc) if y <= B18 else 0.0
        N = (I - B23 * C29 * esc) if y <= B19 else 0.0
        Mcol.append(M); Ncol.append(N); Jcol.append(J)
    return dict(Mcol=Mcol, Ncol=Ncol, Jcol=Jcol, C51=irr(Mcol), C52=irr(Ncol),
                C55=npv_excel(B21w, Jcol))


def combined_cf(sites, op, price_mult, basis='self'):
    cf = [0.0] * 21
    for sk in sites:
        A = anchors(sk, op, price_mult=price_mult, basis=basis)
        R = recompute(A)
        for y in range(21):
            cf[y] += R['Mcol'][y] + R['Ncol'][y]
    return cf


def solve_k(sites, op, basis='self'):
    lo, hi = 0.3, 3.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if irr(combined_cf(sites, op, mid, basis)) < TARGET: lo = mid
        else: hi = mid
        if hi - lo < 1e-13: break
    return (lo + hi) / 2


if __name__ == '__main__':
    out = {}
    for basis, tag in [('self', 'SELF-BASIS (PRIMARY — rev3 continuity, PPA on self-consumed)'),
                       ('gen', 'GEN-BASIS (labeled, Option B — post-approval engine input)')]:
        print('=' * 74)
        print(f'4-SITIOS BOOK — re-solve k for combined investor TIR = 14.00% — {tag}')
        print('=' * 74)
        for op in ['op1', 'op2']:
            oldk_irr = irr(combined_cf(SITES4, op, 1.0, basis))   # rev3 price under new motor
            k = solve_k(SITES4, op, basis)
            newk_irr = irr(combined_cf(SITES4, op, k, basis))
            combP = irr(combined_cf(SITESP, op, k, basis))
            rec = dict(k=k, irr_oldk=oldk_irr, irr_newk=newk_irr, proplasa_combined_irr=combP)
            if basis == 'self':
                out.setdefault(op, {})
                out[op].update(k_selfbasis=k, irr_oldk_selfbasis=oldk_irr,
                               irr_newk_selfbasis=newk_irr, proplasa_combined_irr_selfbasis=combP)
            else:
                out[op]['basis_gen'] = rec
            print(f"\n{op.upper()}: OLD k(=1.0) -> {oldk_irr:.4%}   |   solved k = {k:.6f} -> {newk_irr:.4%}   |   Proplasa comb @k = {combP:.4%}")
            if basis == 'self':
                for sk in SITES4 + SITESP:
                    A = anchors(sk, op, price_mult=k, basis=basis)
                    R = recompute(A)
                    minJ = min(R['Jcol'])
                    neg = [y + 1 for y, j in enumerate(R['Jcol']) if j < 0]
                    flag = f'  !!NEG client yrs {neg}' if neg else ''
                    print(f"    {sk:4s} price {A['price0']:.4f} -> {A['price']:.4f} | TIR PV {R['C51']:.3%} | "
                          f"TIR BESS {R['C52']:.3%} | minJ {minJ:,.0f}{flag}")
    out['meta'] = dict(
        primary='self-basis (k_selfbasis): rev3 continuity — PPA billed on SELF-CONSUMED K72, '
                'like the rev3 book (K72<C72, C46=K72*C31). basis_gen retained (Option B, '
                'PPA on total generation) for post-approval engine formalization.',
        target_irr=TARGET, portfolio='4-Sitios book combined (ixt,aca,can,pro)')
    json.dump(out, open(os.path.join(HERE, 'solve_k_cs.json'), 'w'), indent=2)
    print('\nwrote solve_k_cs.json')
