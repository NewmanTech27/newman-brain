#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_nr.py — mandatory verification gates for the NR scenario. Reports PASS/FAIL."""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import solve_k_cs as SK
import sweep_cs as SW

HERE = os.path.dirname(os.path.abspath(__file__))
ALL7 = ['ixt', 'aca', 'can', 'pro', 'pr1', 'pr2', 'tap']
mnr = json.load(open(os.path.join(HERE, 'motor_nr.json')))
gnr = json.load(open(os.path.join(HERE, 'gepp_data_nr.json')))
mc = json.load(open(os.path.join(HERE, 'motor_cs.json')))
results = []


def gate(name, ok, detail=''):
    results.append((name, ok, detail))
    print(('PASS' if ok else 'FAIL') + f'  {name}  {detail}')


# ---- Gate A: energy identities per site/month (full precision from motor) ----
worst_id = 0.0; worst_exc = 0.0; nchk = 0
for sk in ALL7:
    kwp = mnr['sites'][sk]['op1']['annual']['kwp_nr']
    r = D.motor_site(sk, 'op1', kwp, solar_charge=True)
    for m in r['months']:
        NR = m['N_kwh'] / D.RTE
        lhs = m['carga_solar_kwh'] + m['carga_base_kwh']
        worst_id = max(worst_id, abs(lhs - NR) / NR if NR else 0)
        if m['carga_solar_kwh'] > m['exceso_kwh'] + 1e-6:
            worst_exc = max(worst_exc, m['carga_solar_kwh'] - m['exceso_kwh'])
        nchk += 1
gate('A energy identity carga_solar+carga_base=N/RTE (%d months, full precision)' % nchk,
     worst_id < 1e-9, 'worst rel dev=%.2e' % worst_id)
gate('A carga_solar<=exceso disponible', worst_exc < 1e-3, 'worst overshoot=%.4f kWh' % worst_exc)

# ---- Gate B: continuity — motor at rev4 kWp reproduces motor_cs.json <0.1% ----
worst_c = 0.0
for sk in ALL7:
    kwp_r4 = D.NEW_KWP_OP1.get(sk, D.books()[sk]['op1']['26'])
    a = D.motor_site(sk, 'op1', kwp_r4, solar_charge=True)['annual']
    ref = mc['sites'][sk]['op1']['annual']
    for fld, rf in [('R72_new', 'R72_new_mxn'), ('gen', 'gen_kwh'),
                    ('carga_solar', 'carga_solar_kwh'), ('M72_new', 'M72_new_mxn'),
                    ('K72_self', 'K72_new_kwh')]:
        rv = ref[rf]
        if rv:
            worst_c = max(worst_c, abs(a[fld] - rv) / abs(rv) * 100)
gate('B continuity motor@rev4 == motor_cs.json', worst_c < 0.1, 'worst dev=%.4f%%' % worst_c)

# ---- Gate C: TIR check — combined investor TIR at k_NR on SITES4 (rev4 methodology) ----
SITES4 = ['ixt', 'aca', 'can', 'pro']
SITESP = ['pr1', 'pr2', 'tap']
k_nr = mnr['meta']['k_nr']
KWP_NR = {sk: mnr['sites'][sk]['op1']['annual']['kwp_nr'] for sk in ALL7}


def comb_irr(sites, k):
    fixed = [0.0] * 21; slope = [0.0] * 21
    for sk in sites:
        f, sl = SW._site_cf_parts(sk, KWP_NR[sk])
        for y in range(21):
            fixed[y] += f[y]; slope[y] += sl[y]
    return SK.irr([fixed[y] + k * slope[y] for y in range(21)])


tir = comb_irr(SITES4, k_nr)
gate('C combined investor TIR @ k_NR on SITES4 = 14.000% +/-0.01pp', abs(tir - 0.14) < 1e-4,
     'TIR=%.5f%% (k_NR=%.6f)' % (tir * 100, k_nr))
tirP = comb_irr(SITESP, k_nr)
gate('C2 SITESP combined IRR @ k_NR matches meta report',
     abs(tirP - mnr['meta']['sitesp_combined_irr_at_knr']) < 1e-4,
     'SITESP IRR=%.4f%% (reported, not solved)' % (tirP * 100))

# ---- Gate C3: rev4 continuity — 4-row Op1 portfolio year-1 client net = $39.13M ----
ref_39 = 39127948.0   # deck suma of neto: ixt 9.94M + aca 4.24M + can 2.58M + pro 22.37M
gp = gnr['portfolio']
dev39 = abs(gp['ahorro_cliente_anio1_rev4_mxn'] - ref_39) / ref_39 * 100
gate('C3 rev4 4-row portfolio baseline = $39.13M (deck suma)', dev39 < 0.1,
     'rev4 baseline=%.0f dev=%.4f%%' % (gp['ahorro_cliente_anio1_rev4_mxn'], dev39))

# ---- Gate C4: portfolio sums = SITES4 only (no Proplasa double count) ----
s4sum = sum(gnr['sites'][sk]['ahorro_cliente_anio1_nr'] for sk in SITES4)
gate('C4 portfolio NR sum == SITES4 only (no double count)',
     abs(s4sum - gp['ahorro_cliente_anio1_nr_mxn']) < 1.0,
     'sum(SITES4)=%.0f portfolio=%.0f' % (s4sum, gp['ahorro_cliente_anio1_nr_mxn']))

# ---- Gate D: sanity — NR client savings >= rev4 per site ----
exceptions = [sk for sk in ALL7 if gnr['sites'][sk]['delta_ahorro_anio1'] < 0]
gate('D NR client savings >= rev4 per site', not exceptions,
     'exceptions=%s' % (exceptions or 'none'))

# ---- Gate E: viability — client net benefit year1 > 0 every site ----
neg = [sk for sk in ALL7 if not gnr['viability'][sk]['ok']]
gate('E viability year1 net benefit > 0 all sites', not neg, 'negatives=%s' % (neg or 'none'))

# ---- Gate F: NR kWp >= rev4 design every site (removing constraint can't shrink) ----
shrink = [sk for sk in ALL7 if KWP_NR[sk] < mnr['sites'][sk]['op1']['annual']['kwp_rev4'] - 1]
gate('F NR kWp >= rev4 design every site', not shrink, 'shrink=%s' % (shrink or 'none'))

# ---- Gate G: Op2 unchanged (copied verbatim from motor_cs) ----
op2_ok = all(mnr['sites'][sk]['op2'] == mc['sites'][sk]['op2'] for sk in ALL7)
gate('G Op2 unchanged vs motor_cs.json', op2_ok, '')

# ---- Gate H: typical-day dispatch closes (neta ~ carga-pv-chg-dis, chg total=C30/RTE) ----
worst_chg = 0.0
for sk in ALL7:
    c = D.books()[sk]['op1']; target = c['30'] / D.RTE
    for season in ['invierno', 'verano']:
        prof = mnr['sites'][sk]['typical_day'][season]
        chg_tot = -sum(p['chg'] for p in prof)
        worst_chg = max(worst_chg, abs(chg_tot - target) / target)
gate('H typical-day charge total == C30/RTE', worst_chg < 1e-3, 'worst rel dev=%.2e' % worst_chg)

print('\n' + ('ALL GATES PASS' if all(r[1] for r in results) else 'SOME GATES FAILED'))
