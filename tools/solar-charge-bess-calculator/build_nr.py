#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_nr.py — "Sin Restricción de Superficie" (NR) scenario for GEPP Carga Solar.

Op1 (Autoconsumo) variant where roof surface is NOT a constraint: each site is sized to
its STANDALONE optimum (k solved on the site alone at TIR 14%, self-basis, BESS fixed,
solar-charge dispatch, hard cap 20,000 kWp regulatory) — the defensible per-site bound
(sweep_cs_ext.json `standalone` block).

PORTFOLIO CONVENTION (corrected 2026-07-14): `pro` (3,848.9 kWp rev4) IS the consolidation
of pr1+pr2+tap (681.2+1,912+1,255.7 = 3,848.9) — the same physical Proplasa complex
modeled two ways (consolidated predio vs per-meter).  Summing all 7 double-counts
Proplasa.  Therefore:
  * k_NR is solved on SITES4 = [ixt, aca, can, pro] at NR kWp for combined investor
    TIR = 14.000% — the EXACT delivered rev4 methodology (solve_k_cs.py SITES4 solve).
  * All 7 sites are PRICED at that k; SITESP = [pr1, pr2, tap] combined IRR at k_NR is
    reported (like solve_k_cs.json does), and their site data stays as per-meter tabs,
    marked as alternative modeling, EXCLUDED from portfolio sums (4-row convention).
Op2 (GD Medición Neta) does NOT change (0.7 MW regulatory cap binds, not the roof).

Emits: motor_nr.json, gepp_data_nr.json, NUMBERS_NR.md.  Deterministic. READ-ONLY on
everything outside the working dir.
"""
import json, os, sys
sys.path.insert(0, '/home/mario/CFE Brain/work/gepp-carga-solar')
import dispatch_cs as D
import solve_k_cs as SK
import sweep_cs as SW

HERE = os.path.dirname(os.path.abspath(__file__))
S = SK.S
TARGET = 0.14
ALL7 = ['ixt', 'aca', 'can', 'pro', 'pr1', 'pr2', 'tap']
SITES4 = ['ixt', 'aca', 'can', 'pro']    # portfolio basis (rev4 methodology; pro = Proplasa consolidated)
SITESP = ['pr1', 'pr2', 'tap']           # per-meter alternative modeling of the SAME complex as pro
SITE_NAME = {'ixt': 'Ixtlahuacán', 'aca': 'Acapulco', 'can': 'Cancún', 'pro': 'Proplasa',
             'pr1': 'Preforma 1', 'pr2': 'Preforma 2', 'tap': 'Tapa'}

# rev4 delivered PPA multiplier (self-basis, 4-Sitios book solve, applied to all 7 in rev4)
K_REV4 = json.load(open(os.path.join(HERE, 'solve_k_cs.json')))['op1']['k_selfbasis']

# ---- NR sizing = standalone optimum per site (defensible bound) ----
SWEEP = json.load(open(os.path.join(HERE, 'sweep_cs_ext.json')))
KWP_NR = {sk: float(SWEEP['sites'][sk]['standalone']['kwp_opt']) for sk in ALL7}
KWP_REV4 = {sk: D.NEW_KWP_OP1.get(sk, D.books()[sk]['op1']['26']) for sk in ALL7}
NR_AT_CAP = {sk: bool(SWEEP['sites'][sk]['standalone']['opt_at_regulatory_cap']) for sk in ALL7}


def combined_parts(sites, kwpmap):
    fixed = [0.0] * 21; slope = [0.0] * 21
    for sk in sites:
        f, sl = SW._site_cf_parts(sk, kwpmap[sk])
        for y in range(21):
            fixed[y] += f[y]; slope[y] += sl[y]
    return fixed, slope


def combined_irr(sites, kwpmap, k):
    fixed, slope = combined_parts(sites, kwpmap)
    return SK.irr([fixed[y] + k * slope[y] for y in range(21)])


def solve_k_sites(sites, kwpmap):
    """Re-solve a single self-basis PPA multiplier k over the given site set at the given
    kWp map so the combined investor TIR = 14.000%.  rev4 methodology: sites = SITES4."""
    fixed, slope = combined_parts(sites, kwpmap)
    lo, hi = 0.3, 3.0
    for _ in range(300):
        mid = (lo + hi) / 2
        cf = [fixed[y] + mid * slope[y] for y in range(21)]
        if SK.irr(cf) < TARGET: lo = mid
        else: hi = mid
        if hi - lo < 1e-14: break
    k = (lo + hi) / 2
    cf = [fixed[y] + k * slope[y] for y in range(21)]
    return k, SK.irr(cf)


def client_year1(sk, kwp, price):
    """C48 = client net benefit year 1 (self-basis): (M72 + ahorro_bess_bruto)
    - K72_self*price - ahorro_bess_bruto*B17."""
    r = SK.motor_annual(sk, 'op1', kwp)
    return (r['M72_new'] + r['ahorro_bess_bruto']) - r['K72_self'] * price \
        - r['ahorro_bess_bruto'] * S['B17']


def van20(sk, kwp, price0_mult, kmult):
    """VAN 20a client (book C55)."""
    A = SK.anchors(sk, 'op1', kwp=kwp, price_mult=kmult, basis='self')
    rec = SK.recompute(A)
    return rec['C55'], rec['Jcol']


def capex_nr(sk, kwp):
    capex_pv = kwp * 1000 * S['B5'] * S['B4']
    capex_bess = D.books()[sk]['op1']['36']
    return capex_pv, capex_bess, capex_pv + capex_bess


# --- generalized typical-day dispatch at arbitrary kWp (solar-first charge) ---
_DECK = json.load(open('/home/mario/CFE Brain/work/gepp-deck/gepp_data_tir14.json'))
def typical_day_nr(sk, season_key, kwp_new):
    prof = _DECK['sites'][sk][season_key]['prof']
    c = D.books()[sk]['op1']
    C28, C30 = c['28'], c['30']
    kwp_old = c['26']
    scale = kwp_new / kwp_old
    carga = [row['carga'] for row in prof]
    pv = [row['pv'] * scale for row in prof]
    per = [row['per'] for row in prof]
    punta_idx = [h for h in range(24) if per[h] == 'Punta']
    after_pv = [max(0.0, carga[h] - pv[h]) for h in range(24)]
    disp_energy = min(C30, sum(after_pv[h] for h in punta_idx))
    lvl = 0.0
    if punta_idx:
        peaks = sorted((after_pv[h] for h in punta_idx), reverse=True)
        lo, hi = 0.0, max(peaks)
        for _ in range(80):
            lvl = (lo + hi) / 2
            shaved = sum(min(C28, max(0.0, after_pv[h] - lvl)) for h in punta_idx)
            if shaved > disp_energy: lo = lvl
            else: hi = lvl
        lvl = (lo + hi) / 2
    dis = [0.0] * 24
    for h in punta_idx:
        dis[h] = min(C28, max(0.0, after_pv[h] - lvl))
    charge_total = C30 / D.RTE
    chg = [0.0] * 24
    exc = [max(0.0, pv[h] - carga[h]) for h in range(24)]
    remaining = charge_total
    for h in range(24):
        if exc[h] > 0 and remaining > 0:
            take = min(exc[h], C28, remaining)
            chg[h] = -take; remaining -= take
    if remaining > 1e-6:
        base_hrs = list(range(6)); per_h = remaining / len(base_hrs)
        for h in base_hrs:
            add = min(C28 - (-chg[h]), per_h); chg[h] += -add
    out = []
    for h in range(24):
        neta = carga[h] - pv[h] - chg[h] - dis[h]
        out.append(dict(h=h, per=per[h], carga=round(carga[h], 2), pv=round(pv[h], 2),
                        chg=round(chg[h], 2), dis=round(dis[h], 2), neta=round(neta, 2)))
    return out


def build():
    mc = json.load(open(os.path.join(HERE, 'motor_cs.json')))
    gc = json.load(open(os.path.join(HERE, 'gepp_data_cs.json')))

    # k solved on SITES4 at NR kWp — EXACT rev4 methodology (solve_k_cs.py SITES4 solve)
    k_nr, tir_nr = solve_k_sites(SITES4, KWP_NR)
    # SITESP (per-meter Proplasa tabs) combined IRR at k_NR — reported, not part of the solve
    sitesp_irr_at_knr = combined_irr(SITESP, KWP_NR, k_nr)

    # ---------- viability gate ----------
    viab = {}
    for sk in ALL7:
        price = D.books()[sk]['op1']['31'] * k_nr
        c48 = client_year1(sk, KWP_NR[sk], price)
        _, jcol = van20(sk, KWP_NR[sk], None, k_nr)
        viab[sk] = dict(c48=c48, minJ=min(jcol), ok=(c48 > 0 and min(jcol) > 0))
    all_ok = all(v['ok'] for v in viab.values())
    # pricing basis per site: joint k_nr unless viability fails -> standalone k fallback
    price_basis = {}
    for sk in ALL7:
        if viab[sk]['ok']:
            price_basis[sk] = ('joint', k_nr)
        else:
            kk = SWEEP['sites'][sk]['standalone']['opt_point']['k_solved']
            price_basis[sk] = ('standalone', kk)

    # ---------- per-site records ----------
    sites_nr = {}
    motor_sites = {}
    port = dict(kwp_rev4=0.0, kwp_nr=0.0, gen_rev4=0.0, gen_nr=0.0, consumo=0.0,
                carga_solar_nr=0.0, exceso_remanente_nr=0.0, capex_nr=0.0,
                ahorro_a1_rev4=0.0, ahorro_a1_nr=0.0, van_rev4=0.0, van_nr=0.0)
    for sk in ALL7:
        c = D.books()[sk]['op1']
        price0 = c['31']
        kwp_r4 = KWP_REV4[sk]; kwp_nr = KWP_NR[sk]
        basis, kk = price_basis[sk]
        # NR motor
        r_nr = D.motor_site(sk, 'op1', kwp_nr, solar_charge=True)
        a_nr = r_nr['annual']
        # rev4 motor (baseline)
        r_r4 = D.motor_site(sk, 'op1', kwp_r4, solar_charge=True)
        a_r4 = r_r4['annual']
        price_nr = price0 * kk
        price_r4 = price0 * K_REV4
        ah_nr = client_year1(sk, kwp_nr, price_nr)
        ah_r4 = client_year1(sk, kwp_r4, price_r4)
        van_nr, _ = van20(sk, kwp_nr, None, kk)
        van_r4, _ = van20(sk, kwp_r4, None, K_REV4)
        cpv, cbess, ctot = capex_nr(sk, kwp_nr)
        ct = gc['sites'][sk]['ctotal_tot']
        m2_req = kwp_nr * D.M2_PER_KWP
        m2_disp = D.M2_DISP.get(sk)
        m2_falt = (max(0.0, m2_req - m2_disp) if m2_disp else None)
        carga_solar = a_nr['carga_solar']; carga_base = a_nr['carga_base']
        pct_cs = carga_solar / (carga_solar + carga_base) if (carga_solar + carga_base) else 0.0
        rem = a_nr['exceso'] - a_nr['carga_solar']

        sites_nr[sk] = dict(
            name=SITE_NAME[sk],
            en_suma_portafolio=(sk in SITES4),
            modelado=('consolidado (portafolio)' if sk in SITES4 else
                      'per-meter — modelado alternativo del mismo complejo Proplasa que "pro"; '
                      'EXCLUIDO de la suma de portafolio (evita doble conteo)'),
            kwp_rev4=round(kwp_r4, 1), kwp_nr=round(kwp_nr, 1),
            nr_at_regulatory_cap=NR_AT_CAP[sk],
            m2_requeridos=round(m2_req, 0), m2_disponibles=m2_disp,
            m2_faltantes=(round(m2_falt, 0) if m2_falt is not None else None),
            price_basis=basis, k_aplicado=round(kk, 6),
            ppa_price_rev4=round(price_r4, 4), ppa_price_nr=round(price_nr, 4),
            carga_solar_kwh=round(carga_solar, 0),
            pct_carga_solar_del_bess=round(pct_cs, 4),
            exceso_remanente_kwh=round(rem, 0),
            gen_kwh_rev4=round(a_r4['gen'], 0), gen_kwh_nr=round(a_nr['gen'], 0),
            ahorro_cliente_anio1_rev4=round(ah_r4, 0),
            ahorro_cliente_anio1_nr=round(ah_nr, 0),
            delta_ahorro_anio1=round(ah_nr - ah_r4, 0),
            van_20a_rev4=round(van_r4, 0), van_20a_nr=round(van_nr, 0),
            delta_van=round(van_nr - van_r4, 0),
            cobertura_pct_rev4=round(a_r4['gen'] / ct * 100, 2) if ct else None,
            cobertura_pct_nr=round(a_nr['gen'] / ct * 100, 2) if ct else None,
            capex_pv_nr_mxn=round(cpv, 0), capex_bess_mxn=round(cbess, 0),
            inversion_estimada_newman_nr_mxn=round(ctot, 0),
            solar_charge_bonus_mxn=round(a_nr['bonus'], 0),
            typical_day=dict(invierno=typical_day_nr(sk, 'inv', kwp_nr),
                             verano=typical_day_nr(sk, 'ver', kwp_nr)))
        # motor_nr per-site block (op1 NR sizing; op2 unchanged from motor_cs)
        months = []
        for m in r_nr['months']:
            months.append(dict(
                month=m['month'], gen_kwh=round(m['gen_kwh'], 1),
                exceso_kwh=round(m['exceso_kwh'], 1),
                carga_solar_kwh=round(m['carga_solar_kwh'], 1),
                carga_base_kwh=round(m['carga_base_kwh'], 1),
                remanente_kwh=round(m['remanente_kwh'], 1),
                exc_periodo_kwh={p: round(m['exc_per'][p], 1) for p in 'BIP'},
                D=round(m['D'], 6), E=round(m['E'], 6), F=round(m['F'], 6),
                O_new_mxn=round(m['O_new_mxn'], 2), O_rev3_mxn=round(m['O_rev3_mxn'], 2),
                N_kwh=round(m['N_kwh'], 1), P_new_mxn=round(m['P_new_mxn'], 2),
                Q_mxn=round(m['Q_mxn'], 2), R_new_mxn=round(m['R_new_mxn'], 2),
                J_new_mxn=round(m['J_new_mxn'], 2), M_new_mxn=round(m['M_new_mxn'], 2),
                K_new_kwh=round(m['K_new_kwh'], 1),
                carga_solar_bonus_mxn=round(m['carga_solar_bonus_mxn'], 2)))
        annual_nr = dict(
            kwp_rev4=round(kwp_r4, 1), kwp_nr=round(kwp_nr, 1),
            nr_at_regulatory_cap=NR_AT_CAP[sk],
            gen_kwh=round(a_nr['gen'], 0), exceso_kwh=round(a_nr['exceso'], 0),
            carga_solar_kwh=round(carga_solar, 0), carga_base_kwh=round(carga_base, 0),
            pct_carga_solar=round(pct_cs, 4), N_kwh=round(a_nr['N'], 0),
            O_new_mxn=round(a_nr['O_new'], 0), O_rev3_mxn=round(a_nr['O_rev3'], 0),
            R72_new_mxn=round(a_nr['R72_new'], 0), R72_rev3_mxn=round(a_nr['R_rev3'], 0),
            ahorro_bess_bruto_mxn=round(a_nr['ahorro_bess_bruto'], 0),
            solar_charge_bonus_mxn=round(a_nr['bonus'], 0),
            K72_new_kwh=round(a_nr['K72_self'], 0),
            M72_new_mxn=round(a_nr['M72_new'], 0),
            price_ppa_rev4=round(price_r4, 4), price_ppa_nr=round(price_nr, 4),
            k_mult_nr=round(kk, 6), price_basis=basis,
            ahorro_cliente_anio1_mxn=round(ah_nr, 0), van_20a_client_mxn=round(van_nr, 0))
        motor_sites[sk] = dict(
            op1=dict(months=months, annual=annual_nr),
            op2=mc['sites'][sk]['op2'],   # UNCHANGED (0.7 MW cap binds, not roof)
            typical_day=sites_nr[sk]['typical_day'])

        if sk in SITES4:   # 4-row convention: pr1/pr2/tap are the same complex as pro — no double count
            port['kwp_rev4'] += kwp_r4; port['kwp_nr'] += kwp_nr
            port['gen_rev4'] += a_r4['gen']; port['gen_nr'] += a_nr['gen']
            port['consumo'] += ct if ct else 0
            port['carga_solar_nr'] += carga_solar; port['exceso_remanente_nr'] += rem
            port['capex_nr'] += ctot
            port['ahorro_a1_rev4'] += ah_r4; port['ahorro_a1_nr'] += ah_nr
            port['van_rev4'] += van_r4; port['van_nr'] += van_nr

    port_out = dict(
        convencion='4-row (ixt+aca+can+pro) — pr1/pr2/tap son el mismo complejo Proplasa '
                   'que pro (modelado per-meter) y se EXCLUYEN de la suma (sin doble conteo)',
        sitios_en_suma=SITES4,
        kwp_rev4=round(port['kwp_rev4'], 0), kwp_nr=round(port['kwp_nr'], 0),
        gen_rev4_kwh=round(port['gen_rev4'], 0), gen_nr_kwh=round(port['gen_nr'], 0),
        consumo_kwh=round(port['consumo'], 0),
        cobertura_pct_rev4=round(port['gen_rev4'] / port['consumo'] * 100, 2),
        cobertura_pct_nr=round(port['gen_nr'] / port['consumo'] * 100, 2),
        carga_solar_nr_kwh=round(port['carga_solar_nr'], 0),
        exceso_remanente_nr_kwh=round(port['exceso_remanente_nr'], 0),
        inversion_estimada_newman_nr_mxn=round(port['capex_nr'], 0),
        ahorro_cliente_anio1_rev4_mxn=round(port['ahorro_a1_rev4'], 0),
        ahorro_cliente_anio1_nr_mxn=round(port['ahorro_a1_nr'], 0),
        delta_ahorro_anio1_mxn=round(port['ahorro_a1_nr'] - port['ahorro_a1_rev4'], 0),
        van_20a_rev4_mxn=round(port['van_rev4'], 0), van_20a_nr_mxn=round(port['van_nr'], 0),
        delta_van_mxn=round(port['van_nr'] - port['van_rev4'], 0))

    meta = dict(
        scenario='Sin Restricción de Superficie (NR)', model='GEPP BESS Carga Solar rev4 / Op1',
        generated='2026-07-14', generated_by='build_nr.py',
        sizing='kWp_NR = standalone optimum per site (k solved on the site ALONE at TIR 14%, '
               'self-basis, BESS fixed, solar-charge dispatch, hard cap 20,000 kWp regulatory) '
               'from sweep_cs_ext.json standalone block — the defensible per-site bound.',
        pricing='k_NR solved on SITES4 = [ixt,aca,can,pro] at NR kWp for combined investor TIR = '
                '14.000% (self-basis) — EXACT delivered rev4 methodology (solve_k_cs.py). All 7 '
                'sites priced at that k; SITESP=[pr1,pr2,tap] combined IRR at k_NR reported. '
                'Fallback to per-site standalone k only if the solve pushes a site negative.',
        portfolio_convention='4-row: pro (3,848.9 kWp rev4) IS the consolidation of pr1+pr2+tap '
                '(681.2+1,912+1,255.7=3,848.9) — same physical Proplasa complex modeled two ways. '
                'pr1/pr2/tap stay as per-meter tabs, marked alternative modeling, EXCLUDED from '
                'portfolio sums (no double count).',
        op2_note='Op2 (GD Medición Neta) UNCHANGED from rev4 — the 0.7 MW regulatory GD cap binds, '
                 'not the roof. Op2 blocks copied verbatim from motor_cs.json.',
        k_nr=round(k_nr, 6), tir_nr_sites4=round(tir_nr, 6),
        sitesp_combined_irr_at_knr=round(sitesp_irr_at_knr, 6),
        k_rev4_delivered=round(K_REV4, 6),
        kwp_nr=KWP_NR, kwp_rev4=KWP_REV4, nr_at_regulatory_cap=NR_AT_CAP,
        viability_all_ok=all_ok,
        RTE=D.RTE, merma_meses=D.MERMA, m2_per_kwp=D.M2_PER_KWP,
        caveat='Prefactibilidad — datos mensuales GEPP + curva de giro industrial escalada + '
               'campana solar sintética (no hay medición horaria HM 15-min). kWp por encima del '
               'diseño rev4 y m² requeridos suponen superficie/estructura/punto de interconexión '
               'disponibles — sin visita técnica. pro/pr1/pr2/tap NR son cotas teóricas '
               '(pro topa el techo regulatorio de 20 MW; m² requeridos exceden ampliamente el predio).')

    motor_nr = dict(meta=meta, viability=viab, sites=motor_sites)
    json.dump(motor_nr, open(os.path.join(HERE, 'motor_nr.json'), 'w'),
              ensure_ascii=False, indent=1)

    gepp_nr = dict(meta=meta, portfolio=port_out, k=dict(k_nr=round(k_nr, 6),
                   k_rev4_delivered=round(K_REV4, 6), tir_nr_sites4=round(tir_nr, 6),
                   sitesp_combined_irr_at_knr=round(sitesp_irr_at_knr, 6)),
                   viability={sk: dict(ahorro_cliente_anio1_mxn=round(viab[sk]['c48'], 0),
                                       minJ_20a_mxn=round(viab[sk]['minJ'], 0), ok=viab[sk]['ok'])
                              for sk in ALL7},
                   sites=sites_nr)
    json.dump(gepp_nr, open(os.path.join(HERE, 'gepp_data_nr.json'), 'w'), ensure_ascii=False)

    print('k_NR=%.6f  SITES4 TIR=%.6f%%  SITESP comb IRR @k_NR=%.4f%%  viability_all_ok=%s'
          % (k_nr, tir_nr * 100, sitesp_irr_at_knr * 100, all_ok))
    for sk in ALL7:
        s = sites_nr[sk]
        print('  %-4s%s kWp %6.0f->%6.0f  PPA %.4f->%.4f  ah1 %13.0f->%13.0f  d=%+12.0f  cov %5.1f->%5.1f%%%s' % (
            sk, '*' if sk in SITESP else ' ',
            s['kwp_rev4'], s['kwp_nr'], s['ppa_price_rev4'], s['ppa_price_nr'],
            s['ahorro_cliente_anio1_rev4'], s['ahorro_cliente_anio1_nr'], s['delta_ahorro_anio1'],
            s['cobertura_pct_rev4'], s['cobertura_pct_nr'],
            '  [CAP]' if s['nr_at_regulatory_cap'] else ''))
    print('  (* per-meter Proplasa tab, excluded from portfolio sum)')
    print('PORTFOLIO(4-row) ah1 %.0f->%.0f  delta=%+.0f  VAN %.0f->%.0f  capex_NR=%.0f' % (
        port_out['ahorro_cliente_anio1_rev4_mxn'], port_out['ahorro_cliente_anio1_nr_mxn'],
        port_out['delta_ahorro_anio1_mxn'], port_out['van_20a_rev4_mxn'],
        port_out['van_20a_nr_mxn'], port_out['inversion_estimada_newman_nr_mxn']))
    return motor_nr, gepp_nr


if __name__ == '__main__':
    build()
