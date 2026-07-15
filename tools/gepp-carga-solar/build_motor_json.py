#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble motor_cs.json — the complete per-site/option/month rev4 motor plus typical-day
profiles and the superficie sweep.  PRIMARY numbers = rev3 SELF-BASIS (PPA on self-consumed);
gen-basis retained under *_gen / basis_gen labels.  Deterministic."""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import solve_k_cs as SK
import sweep_cs as SW

HERE = os.path.dirname(os.path.abspath(__file__))
K = json.load(open(os.path.join(HERE, 'solve_k_cs.json')))


def round_rec(o, nd=2):
    if isinstance(o, float): return round(o, nd)
    if isinstance(o, dict): return {k: round_rec(v, nd) for k, v in o.items()}
    if isinstance(o, list): return [round_rec(v, nd) for v in o]
    return o


def site_block(sk):
    B = D.books()
    block = {}
    for op in ['op1', 'op2']:
        kwp = D.NEW_KWP_OP1.get(sk, B[sk][op]['26']) if op == 'op1' else B[sk][op]['26']
        r = D.motor_site(sk, op, kwp, solar_charge=True)
        a = r['annual']
        c = B[sk][op]
        price0 = c['31']; kmult = K[op]['k_selfbasis']
        months = []
        for m in r['months']:
            months.append(dict(
                month=m['month'], gen_kwh=round(m['gen_kwh'], 1),
                exceso_kwh=round(m['exceso_kwh'], 1),
                carga_solar_kwh=round(m['carga_solar_kwh'], 1),
                carga_base_kwh=round(m['carga_base_kwh'], 1),
                remanente_kwh=round(m['remanente_kwh'], 1),
                exc_periodo_kwh=round_rec(m['exc_per'], 1),
                # PRIMARY self-basis split (D+E+F = pct_ac < 1, rev3-style; book J/K formulas unchanged)
                D=round(m['D'], 6), E=round(m['E'], 6), F=round(m['F'], 6),
                O_new_mxn=round(m['O_new_mxn'], 2), O_rev3_mxn=round(m['O_rev3_mxn'], 2),
                N_kwh=round(m['N_kwh'], 1),
                P_new_mxn=round(m['P_new_mxn'], 2), Q_mxn=round(m['Q_mxn'], 2),
                R_new_mxn=round(m['R_new_mxn'], 2),
                J_new_mxn=round(m['J_new_mxn'], 2), M_new_mxn=round(m['M_new_mxn'], 2),
                K_new_kwh=round(m['K_new_kwh'], 1),           # self-consumed (PPA basis, rev3-style)
                carga_solar_bonus_mxn=round(m['carga_solar_bonus_mxn'], 2),
                # gen-basis fields (labeled; post-approval engine input, NOT for the rev4 book)
                D_gen=round(m['D_gen'], 6), E_gen=round(m['E_gen'], 6), F_gen=round(m['F_gen'], 6),
                K_gen_kwh=round(m['K_gen_kwh'], 1),
                ajuste_excedente_gen_mxn=round(m['ajuste_excedente_gen_mxn'], 2),
                ajuste_residual_mxn=round(m['ajuste_residual_mxn'], 2)))
        annual = dict(
            kwp_rev3=a['kwp_rev3'], kwp_rev4=a['kwp'],
            gen_kwh=round(a['gen'], 0),
            exceso_kwh=round(a['exceso'], 0), carga_solar_kwh=round(a['carga_solar'], 0),
            carga_base_kwh=round(a['carga_base'], 0),
            pct_carga_solar=round(a['carga_solar'] / (a['carga_solar'] + a['carga_base']), 4) if (a['carga_solar'] + a['carga_base']) else 0.0,
            N_kwh=round(a['N'], 0),
            O_new_mxn=round(a['O_new'], 0), O_rev3_mxn=round(a['O_rev3'], 0),
            R72_new_mxn=round(a['R72_new'], 0), R72_rev3_mxn=round(a['R_rev3'], 0),
            ahorro_bess_bruto_mxn=round(a['ahorro_bess_bruto'], 0),
            ahorro_bess_bruto_rev3_mxn=round(a['ahorro_bess_bruto_rev3'], 0),
            solar_charge_bonus_mxn=round(a['bonus'], 0),
            K72_new_kwh=round(a['K72_self'], 0),              # PRIMARY: self-consumed
            M72_new_mxn=round(a['M72_new'], 0), M72_rev3_mxn=round(a['M72_rev3'], 0),
            ahorro_pv_nuevo_mxn=round(a['M72_new'], 0),
            price_ppa_rev3=round(price0, 4), k_mult=round(kmult, 6),
            price_ppa_rev4=round(price0 * kmult, 4),
            basis_gen=dict(                                    # labeled gen-basis annuals
                K72_gen_kwh=round(a['K72_gen'], 0),
                ajuste_excedente_gen_mxn=round(a['ajuste'], 0),
                ajuste_residual_mxn=round(a['ajuste_residual'], 0),
                k_mult_gen=round(K[op]['basis_gen']['k'], 6),
                price_ppa_gen=round(price0 * K[op]['basis_gen']['k'], 4)))
        block[op] = dict(months=months, annual=annual)
    block['typical_day'] = dict(
        invierno=D.typical_day(sk, 'inv'),
        verano=D.typical_day(sk, 'ver'))
    block['sweep_superficie'] = SW.sweep_site(sk)
    return block


def main():
    out = dict(
        meta=dict(
            model='GEPP BESS Carga Solar (rev4)', generated_by='dispatch_cs.py',
            giro='Industrial 24/7 (all 7 sites; imported/*/inputs.json)',
            division='SIN windows (Ixt DIST-Jal, Aca Centro Sur, Can Peninsular, Pro V.Mex Norte)',
            RTE=D.RTE, merma_meses=D.MERMA, texc_op1_mxn_kwh=0.0,
            c_oport_op1='texc≈0 (autoconsumo excedente a CFE ~mayorista)',
            c_oport_op2='t_int (net-metering period credit forgone; Op2 has ~0 excess anyway)',
            accounting_primary='SELF-BASIS (rev3 continuity, verified vs rev3 book: D+E+F=pct_ac<1, '
                       'K72=self<C72, C46=K72*C31): D/E/F = self-consumed period split at the new '
                       'kWp, J credits only self at retail, K bills PPA on self — the book J/K '
                       'formulas need NO ajuste column; excess remanente is worth texc≈0 and absent '
                       'from J. Solar-charge benefit lives ONLY in O_new = carga_base*t_base + '
                       'carga_solar*c_oport; R72_new = R72_rev3 + Σcarga_solar*(t_base-c_oport). '
                       'Anchored so unchanged sites/options reproduce rev3 exactly.',
            accounting_basis_gen='RETAINED, labeled (*_gen / basis_gen): Option B — PPA on TOTAL '
                       'generation (K72=gen, D+E+F=1, J=J_base-ajuste); matches golden engine '
                       'calc_core.py L231 (ppa_pay=gen*ppa). Input for post-approval engine '
                       'formalization, NOT used in the rev4 book.',
            sweep_note='sweep_superficie RE-SOLVES the PPA multiplier k at each kWp point '
                       '(union of the 7 sites, other sites at rev4 design) so combined investor '
                       'TIR stays 14.0% — deal-solved doctrine. Self-basis.',
            new_kwp_op1=D.NEW_KWP_OP1,
            k=dict(op1=K['op1'], op2=K['op2']),
            m2_per_kwp=D.M2_PER_KWP),
        sites={})
    for sk in D.SITE_KEYS:
        out['sites'][sk] = site_block(sk)
    path = os.path.join(HERE, 'motor_cs.json')
    json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
    sz = os.path.getsize(path)
    print(f'wrote {path}  ({sz/1024:.0f} KB)')
    for sk in D.SITE_KEYS:
        a = out['sites'][sk]['op1']['annual']
        sw = out['sites'][sk]['sweep_superficie']
        print(f"  {sk}: kWp {a['kwp_rev3']:.0f}->{a['kwp_rev4']:.0f}  exceso {a['exceso_kwh']:,.0f}  "
              f"%solar {a['pct_carga_solar']*100:.0f}  bonus ${a['solar_charge_bonus_mxn']:,.0f}  "
              f"ΔM72 ${a['M72_new_mxn']-a['M72_rev3_mxn']:,.0f}  PPA {a['price_ppa_rev3']}->{a['price_ppa_rev4']}  "
              f"| sweep opt {sw['kwp_opt']:.0f} kWp (at_cap={sw['opt_at_range_cap']})")


if __name__ == '__main__':
    main()
