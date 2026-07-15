#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sweep_cs_ext.py — EXTENDED superficie/kWp sweep: range grows per site until the client-
savings curve genuinely peaks and declines, hard stop 20,000 kWp DC (~20 MW autoconsumo
CNE-simplified ceiling).  Same methodology as sweep_cs.py: SELF-BASIS, PPA multiplier k
RE-SOLVED at every point (union-7, combined investor TIR 14.0%), BESS fixed.
Coarse 200-kWp grid, refined at 50 kWp around the peak.

Writes sweep_cs_ext.json (schema = sweep_superficie + opt_at_regulatory_cap flag).
SUPERSEDES motor_cs.json's sweep_superficie (which is range-capped at 3x rev3).
Does NOT touch motor_cs.json.
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import sweep_cs as SW

HERE = os.path.dirname(os.path.abspath(__file__))
KWP_CAP = 20000.0   # ~20 MW: autoconsumo interconectado CNE-simplified permit ceiling


# ---- supplementary: STANDALONE per-site deal (k solved on the site alone, TIR 14%) ----
# The union-7 re-solve (primary, deal-consistent) lets a heavily-oversized site be cross-
# subsidized by the other sites' PPA (k rises for everyone).  For the per-site question
# "máximo ahorro posible en ESTE sitio" the standalone solve is the defensible bound.
def solve_k_standalone(sk, kwp):
    fixed, slope = SW._site_cf_parts(sk, kwp)
    lo, hi = 0.3, 6.0
    for _ in range(120):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SW.SK.irr(cf) < SW.TARGET: lo = mid
        else: hi = mid
        if hi - lo < 1e-12: break
    return (lo + hi) / 2


def client_point_standalone(sk, kwp):
    k = solve_k_standalone(sk, kwp)
    c = D.books()[sk]['op1']
    r = SW.SK.motor_annual(sk, 'op1', kwp)
    price = c['31'] * k
    C48 = (r['M72_new'] + r['ahorro_bess_bruto']) - r['K72_self'] * price \
          - r['ahorro_bess_bruto'] * SW.S['B17']
    return dict(kwp=round(kwp, 1), m2=round(kwp * D.M2_PER_KWP, 0),
                k_solved=round(k, 6), price=round(price, 4),
                ahorro_cliente_anio1_mxn=round(C48, 0))


def sweep_site_ext(sk):
    c = D.books()[sk]['op1']
    kwp_rev3 = c['26']
    kwp_design = SW.design_kwp(sk)
    # coarse grid: 0.6x rev3 .. 20,000 kWp, step 200
    kwps = []
    kwp = round(kwp_rev3 * 0.6 / 10) * 10
    while kwp <= KWP_CAP + 1e-6:
        kwps.append(float(kwp)); kwp += 200.0
    if kwps[-1] < KWP_CAP: kwps.append(KWP_CAP)
    if not any(abs(x - kwp_design) < 1 for x in kwps):
        kwps.append(kwp_design); kwps.sort()
    pts = {x: SW.client_point(sk, x) for x in kwps}
    coarse = [pts[x] for x in sorted(pts)]

    def refine(metric):
        """50-kWp refinement around the coarse argmax of `metric`."""
        best = max(coarse, key=lambda p: p[metric])
        i = coarse.index(best)
        lo = coarse[max(0, i - 1)]['kwp']; hi = coarse[min(len(coarse) - 1, i + 1)]['kwp']
        x = lo
        while x <= hi + 1e-6:
            if x not in pts and x <= KWP_CAP:
                pts[x] = SW.client_point(sk, x)
            x += 50.0
        return max(pts.values(), key=lambda p: p[metric])

    opt = refine('ahorro_cliente_anio1_mxn')
    optv = refine('van_20a_mxn')
    at_reg_cap = opt['kwp'] >= KWP_CAP - 1e-6

    # standalone-deal optimum (coarse 200 + refine 50)
    spts = {x: client_point_standalone(sk, x) for x in kwps}
    sbest = max(spts.values(), key=lambda p: p['ahorro_cliente_anio1_mxn'])
    x = max(kwps[0], sbest['kwp'] - 200.0)
    while x <= min(KWP_CAP, sbest['kwp'] + 200.0) + 1e-6:
        if x not in spts:
            spts[x] = client_point_standalone(sk, x)
        x += 50.0
    sopt = max(spts.values(), key=lambda p: p['ahorro_cliente_anio1_mxn'])
    sdesign = spts[min(spts, key=lambda x: abs(x - kwp_design))]
    design = pts[min(pts, key=lambda x: abs(x - kwp_design))]
    m2_disp = D.M2_DISP.get(sk)
    # output curve: coarse downsampled to ~30 pts + peak-neighborhood points, sorted
    keep = set()
    stride = max(1, len(coarse) // 28)
    keep |= {coarse[i]['kwp'] for i in range(0, len(coarse), stride)}
    keep |= {coarse[-1]['kwp'], design['kwp'], opt['kwp'], optv['kwp']}
    keep |= {p['kwp'] for p in pts.values() if abs(p['kwp'] - opt['kwp']) <= 400}
    curve = [pts[x] for x in sorted(k for k in pts if pts[k]['kwp'] in keep or k in keep)]
    return dict(site=sk,
                basis='self (PPA on self-consumed; k re-solved per point, union-7, TIR 14%)',
                kwp_rev3=kwp_rev3, kwp_design=kwp_design, kwp_cap_regulatorio=KWP_CAP,
                kwp_opt=opt['kwp'], kwp_opt_van=optv['kwp'],
                opt_at_regulatory_cap=at_reg_cap,
                m2_opt=opt['m2'], m2_disponibles=m2_disp,
                m2_faltantes=(max(0.0, opt['m2'] - m2_disp) if m2_disp else None),
                design_point=design, opt_point=opt, opt_point_van=optv,
                delta_ahorro_anio1_opt_vs_design=round(opt['ahorro_cliente_anio1_mxn'] - design['ahorro_cliente_anio1_mxn'], 0),
                delta_van_opt_vs_design=round(optv['van_20a_mxn'] - design['van_20a_mxn'], 0),
                standalone=dict(     # supplementary: k solved on the site ALONE (no cross-subsidy)
                    kwp_opt=sopt['kwp'], m2_opt=sopt['m2'],
                    m2_faltantes=(max(0.0, sopt['m2'] - m2_disp) if m2_disp else None),
                    opt_at_regulatory_cap=(sopt['kwp'] >= KWP_CAP - 1e-6),
                    opt_point=sopt, design_point=sdesign,
                    delta_ahorro_anio1_opt_vs_design=round(sopt['ahorro_cliente_anio1_mxn'] - sdesign['ahorro_cliente_anio1_mxn'], 0)),
                curve=curve)


if __name__ == '__main__':
    out = dict(meta=dict(
        note='EXTENDED sweep — SUPERSEDES motor_cs.json sites.<k>.sweep_superficie (that one '
             'is range-capped at 3x rev3 and flags opt_at_range_cap). Range extends until the '
             'client-savings curve peaks, hard stop 20,000 kWp DC (~20 MW autoconsumo CNE '
             'permiso simplificado). Methodology identical: self-basis, k re-solved per point '
             '(union-7, combined investor TIR 14.0%), BESS fixed; 200-kWp coarse grid, 50-kWp '
             'refinement near the peak. opt_at_regulatory_cap=true means still rising at 20 MW. '
             'CAVEAT (union artifact): under the union-7 re-solve an oversized site is cross-'
             'subsidized by the other sites PPA (k rises for the whole portfolio), so its own '
             'client curve can keep rising to the cap (aca, pro). Each site therefore also carries '
             'a "standalone" block — k solved on the site ALONE at TIR 14% — the defensible bound '
             'for the deck section "m2 para el maximo ahorro posible".',
        kwp_cap=KWP_CAP, generated_by='sweep_cs_ext.py'), sites={})
    for sk in D.SITE_KEYS:
        s = sweep_site_ext(sk)
        out['sites'][sk] = s
        st = s['standalone']
        print(f"{sk}: opt={s['kwp_opt']:.0f} kWp (VAN opt {s['kwp_opt_van']:.0f}, reg_cap={s['opt_at_regulatory_cap']})  "
              f"m2_opt={s['m2_opt']:.0f} disp={s['m2_disponibles']} falt={s['m2_faltantes']}  "
              f"Δahorro={s['delta_ahorro_anio1_opt_vs_design']:,.0f}  Δvan={s['delta_van_opt_vs_design']:,.0f}  "
              f"pts={len(s['curve'])}")
        print(f"     standalone: opt={st['kwp_opt']:.0f} kWp (reg_cap={st['opt_at_regulatory_cap']})  m2={st['m2_opt']:.0f}  "
              f"falt={st['m2_faltantes']}  Δahorro={st['delta_ahorro_anio1_opt_vs_design']:,.0f}  k@opt={st['opt_point']['k_solved']:.4f}")
    path = os.path.join(HERE, 'sweep_cs_ext.json')
    json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
    print('wrote', path, f'({os.path.getsize(path)/1024:.0f} KB)')
