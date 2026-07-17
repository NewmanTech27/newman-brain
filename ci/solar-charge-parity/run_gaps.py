#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solar-charge gaps 2/4/5 harness (issue #2) — sibling of run_parity.py.

Same fixture (books_data.json, op1, rev4 kWp), same doctrine: exact unit parity
against the dispatch_cs.py prototype where the physics is shared, engine-own
pins where the objective legitimately differs, every divergence attributed.

  B1 GAP 5 UNIT PARITY (hard): engine.pv_period_split() == dispatch_cs
     sim_month() self_per/exc_per per period (B/I/P), 7 sites x 12 months,
     tol 1e-6 kWh.  Proves the per-period hourly-frame port is exact.
  B2 GAP 5 END-TO-END (hard): compute(pv_credit_periods:true) credits exactly
     sum(self_per[p] * t_per) + exced*texc (rates == book rates on this
     fixture), aprov == self_tot, exced == gen - self_tot; and
     compute(pv_credit_periods:false) stays bit-for-bit == baseline_off.json
     (flag inert when OFF — same golden as A2).
  B3 GAP 2 (hard): (a) solar_charge_split parity vs sim_month at BESS scales
     x{1,1.5,2,3} on book dias_punta args, tol 1e-6 kWh — the sweep prices the
     identical dispatch at every size; (b) optimize_sizing grid integrity —
     the {1,2,4}h verano seeds are all in the grid, power tracks duration
     (bess_kw = kwh/hours), ranking sorted by (objective, vpn tie-break),
     sizing_params.sweep == ranking; (c) engine-own pins for the best pick.
  B4 GAP 4 (hard): superficie sweep output — when the kwp cap binds,
     kwp_opt_unconstrained > cap and m2_faltantes = (opt-cap)*m2_per_kwp;
     otherwise opt == best.kwp and m2_faltantes == 0.  Engine-own pins.
  B5 BOTH FLAGS (hard): solar_charge + pv_credit_periods — the three-bucket
     partition aprov + carga_solar + exced_export == gen holds to 1e-6 kWh
     every month; engine-own bonus pins under both flags.

ATTRIBUTION (why B3c/B4 pin engine numbers instead of diffing prototype
optima): sweep_cs.py / probe_bess_scale.py optimize CLIENT ahorro with the PPA
k RE-SOLVED per point at combined investor TIR 14.0% (gap 3 — deal-solved PPA
— already shipped separately at TIR 19% via pipeline.config ppa_target_irr,
excluded from #2).  optimize_sizing prices candidates at the FIXED input PPA
and ranks by financier IRR/NPV, and its dispatch rides the engine's calendar
punta_weekdays basis (the prototype uses billing-period dias_punta — the open
#5/#1 decision, kept as-is).  Optima are therefore not comparable by design;
the shared per-point physics IS compared, exactly (B1/B3a).

Usage: python3 ci/solar-charge-parity/run_gaps.py
Stdlib only.  JS side runs under node.
"""
import json, math, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_parity as RP

TOL_KWH = 1e-6
TOL_MXN = 0.01          # B2 money identity: float product/summation-order noise only
SCALES = [1.0, 1.5, 2.0, 3.0]
HOURS = [1, 2, 4]

# Engine-own pins (A3-style) — current state 2026-07-17, see ATTRIBUTION above.
# Every free-run best picks BESS=0: at the fixture's default PPA the PV-only
# financier IRR dominates every BESS candidate even at 1h — the same economics
# that motivated gap 1 (current_offer picks BESS=0).  The {1,2,4}h grid is
# offered regardless (B3b proves it).
PIN_SIZING = {   # sizing_free (flags off): best {kwp, bess_kwh, bess_hours, tir_financiador}
    'ixt': {'kwp': 5170.0, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.165720},
    'aca': {'kwp': 1748.0, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.176429},
    'can': {'kwp': 1270.0, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.128525},
    'pro': {'kwp': 3848.9, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.149939},
    'pr1': {'kwp': 545.0, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.149939},
    'pr2': {'kwp': 1530.0, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.149939},
    'tap': {'kwp': 1255.7, 'bess_kwh': 0.0, 'bess_hours': 0, 'tir': 0.149939},
}
PIN_UNCONSTRAINED = {   # sizing_reject (rev4 flags + 5%-of-gen exced_export reject): kwp_opt_unconstrained
    'ixt': 4136.0, 'aca': 1398.0, 'can': 1016.0, 'pro': 10778.0,
    'pr1': 545.0, 'pr2': 1530.0, 'tap': 3261.3,
}
PIN_BONUS_BOTH = {      # both_on annual.solar_charge_bonus (solar_charge + per-period credit)
    'ixt': 559892.02, 'aca': 121613.36, 'can': 150385.35,
    'pro': 0.0, 'pr1': 0.0, 'pr2': 0.0, 'tap': 0.0,
}

FAILS = []
def check(ok, msg):
    print(('  [PASS] ' if ok else '  [FAIL] ') + msg)
    if not ok:
        FAILS.append(msg)
    return ok


def jsround(x):
    return math.floor(x / 100.0 + 0.5) * 100  # JS Math.round(x/100)*100


def seed_kwh(bills, hours, dod=0.96, rte=0.96):
    """size_bess_verano port: verano seed for one duration."""
    summer = [b for b in bills if 5 <= b['month'] <= 9] or bills
    avg = sum(b['kw_punta'] for b in summer) / len(summer)
    return jsround(hours * avg / (dod * math.sqrt(rte)))


def build_gaps_fixture(D, base):
    """Extend run_parity.build_fixture with scaled-unit args + sizing opts."""
    B = D.books()
    for k, site in base.items():
        s, c = B[k], B[k]['op1']
        kwp = site['inputs']['kwp']
        scaled = []
        for f in SCALES:
            for i in range(12):
                m = s['months'][i]
                N_f = min(c['30'] * f * s['dias_punta'][i],
                          c['28'] * f * s['hrs_punta'][i] * s['dias_punta'][i],
                          s['kwh_punta'][i])
                scaled.append(dict(
                    scale=f, year=D.month_year(m)[0], month=m,
                    kwh_total=s['kwh_base'][i] + s['kwh_inter'][i] + s['kwh_punta'][i],
                    gen=kwp * s['yield'][i], bess_kw=c['28'] * f,
                    charge_energy=N_f / D.RTE, dias_punta_book=s['dias_punta'][i]))
        site['scaled_args'] = scaled
        grid = [round(0.6 * kwp), round(0.8 * kwp), kwp]
        gen_annual = kwp * sum(s['yield'])
        site['sizing_free_opts'] = dict(kwp_grid=grid, kwp_max=2 * kwp)
        site['sizing_reject_opts'] = dict(kwp_grid=grid, kwp_max=3 * kwp,
                                          reject_exced_kwh=0.05 * gen_annual)
    return base


def main():
    D = RP.load_prototype()
    fixture = dict(sites=build_gaps_fixture(D, RP.build_fixture(D)))
    B = D.books()

    with tempfile.TemporaryDirectory() as td:
        fxp, outp = os.path.join(td, 'fx.json'), os.path.join(td, 'out.json')
        with open(fxp, 'w') as f:
            json.dump(fixture, f)
        subprocess.run(['node', os.path.join(HERE, 'run_gaps_engine.mjs'), fxp, outp],
                       check=True)
        with open(outp) as f:
            js = json.load(f)

    with open(RP.BASELINE) as f:
        base_off = json.load(f)

    print('B1 — gap 5 unit parity: pv_period_split vs sim_month self_per/exc_per')
    worst = 0.0
    for k in D.SITE_KEYS:
        s, c = B[k], B[k]['op1']
        for i, a in enumerate(fixture['sites'][k]['sim_args']):
            sim = D.sim_month(a['month'], a['kwh_total'], a['gen'], c['28'],
                              D.N_month(s, c, i), s['dias_punta'][i], solar_charge=False)
            u = js['sites'][k]['period_unit'][i]
            for p in 'BIP':
                worst = max(worst, abs(u['self_per'][p] - sim['self_per'][p]),
                            abs(u['exc_per'][p] - sim['exc_per'][p]))
    check(worst <= TOL_KWH, f'7 sites x 12 months x B/I/P, worst |diff| = {worst:.3e} kWh (tol {TOL_KWH})')

    print('B2 — gap 5 end to end: compute(pv_credit_periods:true) credit identity + flag inert')
    worst_k, worst_m = 0.0, 0.0
    for k in D.SITE_KEYS:
        s, c = B[k], B[k]['op1']
        for i, r in enumerate(js['sites'][k]['pcp_on']['monthly']):
            a = fixture['sites'][k]['sim_args'][i]
            sim = D.sim_month(a['month'], a['kwh_total'], a['gen'], c['28'],
                              D.N_month(s, c, i), s['dias_punta'][i], solar_charge=False)
            trate = {'B': s['t_base'][i], 'I': s['t_int'][i], 'P': s['t_punta'][i]}
            ah_ref = sum(sim['self_per'][p] * trate[p] for p in 'BIP')  # texc = 0
            worst_m = max(worst_m, abs(r['ah_pv'] - ah_ref))
            worst_k = max(worst_k, abs(r['gen_aprov'] - sim['self_tot']),
                          abs(r['exced'] - (r['gen'] - sim['self_tot'])))
    check(worst_k <= TOL_KWH, f'aprov == self_tot, exced == gen - self_tot, worst = {worst_k:.3e} kWh')
    check(worst_m <= TOL_MXN, f'ah_pv == sum(self_per*t_per) + exced*texc, worst = {worst_m:.3e} MXN (tol {TOL_MXN})')
    for k in D.SITE_KEYS:
        check(js['sites'][k]['pcp_off'] == base_off[k],
              f'{k}: pv_credit_periods:false bit-identical to pre-flag baseline')

    print('B5 — both flags: three-bucket partition aprov + carga_solar + exced_export == gen')
    worst = 0.0
    for k in D.SITE_KEYS:
        for r in js['sites'][k]['both_on']['monthly']:
            worst = max(worst, abs(r['gen_aprov'] + r['carga_solar'] + r['exced_export'] - r['gen']))
    check(worst <= TOL_KWH, f'7 sites x 12 months, worst |residual| = {worst:.3e} kWh')
    for k in D.SITE_KEYS:
        bo = js['sites'][k]['both_on']['annual']['solar_charge_bonus']
        check(abs(bo - PIN_BONUS_BOTH[k]) <= 2.0,
              f"{k}: both-flags bonus {bo:,.2f} == pin {PIN_BONUS_BOTH[k]:,.2f}")

    print('B3a — gap 2 unit parity: solar_charge_split vs sim_month at BESS scales x' +
          '/'.join(str(f) for f in SCALES))
    worst = 0.0
    for k in D.SITE_KEYS:
        s, c = B[k], B[k]['op1']
        for j, a in enumerate(fixture['sites'][k]['scaled_args']):
            f = a['scale']
            i = j % 12
            N_f = a['charge_energy'] * D.RTE
            sim = D.sim_month(a['month'], a['kwh_total'], a['gen'], c['28'] * f,
                              N_f, s['dias_punta'][i], solar_charge=True)
            u = js['sites'][k]['scaled_unit'][j]
            worst = max(worst, abs(u['carga_solar'] - sim['carga_solar']),
                        abs(u['exceso'] - sim['exceso']))
    check(worst <= TOL_KWH, f'7 sites x 12 months x 4 scales, worst |diff| = {worst:.3e} kWh (tol {TOL_KWH})')

    print('B3b — gap 2 sweep integrity: {1,2,4}h seeds, power=kwh/hours, ranking order')
    for k in D.SITE_KEYS:
        sz = js['sites'][k]['sizing_free']
        cands = sz['ranking']
        bills = fixture['sites'][k]['bills']
        grid = sz['sizing_params']['bess_grid']
        missing, filtered = [], []
        for h in HOURS:
            kwh = seed_kwh(bills, h)
            if kwh <= 0:
                continue
            if not any(g['bess_kwh'] == kwh and g['bess_hours'] == h for g in grid):
                missing.append(f'{h}h seed {kwh} kWh')
            elif not any(c['bess_kwh'] == kwh and c['bess_hours'] == h for c in cands):
                filtered.append(f'{h}h seed {kwh} kWh')  # in grid, non-financeable at this size
        check(not missing, f"{k}: verano seeds for {HOURS} h all in the candidate grid" +
              ('' if not missing else f' — MISSING {missing}'))
        if filtered:
            print(f"    [INFO] {k}: in grid but IRR-filtered from ranking (non-financeable): {filtered}")
        bad_kw = [c for c in cands if c['bess_kwh'] > 0 and
                  c['bess_kw'] != math.floor(c['bess_kwh'] / c['bess_hours'] + 0.5)]
        check(not bad_kw, f'{k}: bess_kw == round(bess_kwh / bess_hours) on all candidates')
        key = sz['key']
        resorted = sorted(cands, key=lambda c: (-c[key], -c['vpn_financiador']))
        check([(c['kwp'], c['bess_kwh'], c['bess_hours']) for c in cands] ==
              [(c['kwp'], c['bess_kwh'], c['bess_hours']) for c in resorted],
              f'{k}: ranking sorted by ({key} desc, vpn_financiador tie-break)')
        check(sz['best'] == cands[0], f'{k}: best == ranking[0]')
        check(sz['sizing_params']['sweep'] == cands, f'{k}: sizing_params.sweep == ranking (gap 4 output)')

    print('B3c — gap 2 pins (engine-own; objective = financier IRR at fixed PPA — see ATTRIBUTION)')
    for k in D.SITE_KEYS:
        b = js['sites'][k]['sizing_free']['best']
        pin = PIN_SIZING[k]
        ok = (abs(b['kwp'] - pin['kwp']) <= 0.5 and b['bess_kwh'] == pin['bess_kwh'] and
              b['bess_hours'] == pin['bess_hours'] and
              abs(b['tir_financiador'] - pin['tir']) <= 1e-4)
        check(ok, f"{k}: best kwp={b['kwp']:.0f} bess={b['bess_kwh']:.0f} kWh @{b['bess_hours']}h "
                  f"TIR {b['tir_financiador']*100:.2f}% == pin ({pin['kwp']:.0f}, {pin['bess_kwh']:.0f}, "
                  f"{pin['bess_hours']}h, {pin['tir']*100:.2f}%)")

    print('B4 — gap 4 superficie output: kwp_opt_unconstrained + m2_faltantes semantics')
    n_bind = 0
    for k in D.SITE_KEYS:
        sz = js['sites'][k]['sizing_reject']
        sp = sz['sizing_params']
        cap, opt, falt = sp['kwp_cap'], sp['kwp_opt_unconstrained'], sp['m2_faltantes']
        if sz['best']['kwp'] == cap:
            n_bind += 1
            ok = opt >= cap and abs(falt - max(0.0, (opt - cap) * sp['m2_per_kwp'])) <= 1e-6
            tag = f'cap binds, opt {opt:.0f} kWp, faltan {falt:.0f} m2'
        else:
            ok = opt == sz['best']['kwp'] and falt == 0.0
            tag = f'interior optimum {opt:.0f} kWp, m2_faltantes 0'
        check(ok, f'{k}: {tag}')
        check(abs(opt - PIN_UNCONSTRAINED[k]) <= 0.5,
              f"{k}: kwp_opt_unconstrained {opt:.0f} == pin {PIN_UNCONSTRAINED[k]:.0f}")
    check(n_bind >= 1, f'roof cap binds on {n_bind}/7 sites — gap 4 extension path exercised')

    print()
    if FAILS:
        print(f'GAPS FAIL — {len(FAILS)} failing check(s):')
        for m in FAILS:
            print('  - ' + m)
        return 1
    print('GAPS OK — B1/B3a exact ports, B2/B5 identities hold, flag inert, sweep + superficie pins hold')
    return 0


if __name__ == '__main__':
    sys.exit(main())
