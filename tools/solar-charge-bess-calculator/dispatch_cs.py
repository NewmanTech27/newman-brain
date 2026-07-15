#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dispatch_cs.py — Hourly solar-charge dispatch simulator + monthly aggregation for the
GEPP "BESS Carga Solar" model (rev4).  See DESIGN.md (authoritative) and REPORT_MOTOR.md.

WHAT IT DOES
  For every site sheet (7) x option (Op1/Op2) x month (12) it produces the quantities the
  rev4 book surgery + deck need, under the new dispatch rule: the BESS is charged FIRST
  with same-day solar EXCESS (pv>load, sun hours, power-capped C28), and only the shortfall
  is charged from the grid in base hours 0-5.  Discharge (flat-top punta shave) is unchanged.

ACCOUNTING — PRIMARY = rev3 SELF-BASIS (client-facing continuity; verified vs rev3 book:
Ixtlahuacán D60+E60+F60=0.9973<1, K72=7,952,537 < C72=8,114,834, C46=K72*C31 — rev3 bills PPA
on SELF-CONSUMED energy):
  * ANCHORED to rev3.  Every rev4 quantity = rev3 value + a model-derived INCREMENT that is
    exactly 0 when kWp is unchanged and solar charging is disabled.  => old-mode replica of
    R72, K72, M72 and C52 is EXACT (gate 1).
  * BESS:  O_new = carga_base*t_base + carga_solar*c_oport  (c_oport = texc ~= 0 for Op1).
    R72_new = R72_rev3 + Σ carga_solar_m * (t_base - c_oport).   (the solar-charge bonus)
  * PV (PRIMARY, self-basis): D/E/F = SELF-CONSUMED period split at the new kWp
    (D+E+F = pct_ac < 1, rev3-style), so the book's unchanged J formula credits only
    self-consumption at retail and K (=G+H+I) bills the PPA on self only.  NO ajuste column
    needed: excess remanente is worth texc~=0 and simply absent from J; the solar-charge
    benefit lives ONLY in O_new.  Anchoring per period:
    self_new_per = gen_rev3*DEF_rev3_per + (sim_self_new_per - sim_self_rev3_per).
  * GEN-BASIS (Option B: PPA on TOTAL generation, D+E+F=1, J=J_base-ajuste; matches golden
    calc_core.py L231 ppa_pay=gen*ppa) RETAINED under *_gen / basis_gen labels as input for
    the post-approval engine formalization.  NOT used in the rev4 book.
  * Energy identity preserved exactly: carga_solar + carga_base = N/RTE.
  * No double count (self-basis): every excess kWh is either charged to BESS (valued in O via
    c_oport) or remanente at texc~=0 (absent from J).  Self-consumption appears only in J.

Deterministic.  Reads the rev3 book extract (books_data.json) + tools/load_curves.py.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/mario/CFE Brain/tools')
from load_curves import CURVES, WINDOWS, PV_BELL, day_counts, season

BOOKS_DATA = os.environ.get('BOOKS_DATA',
    '/tmp/claude-1001/-home-mario/40ff713a-98bb-4e13-ad1c-565b3a81cc4b/scratchpad/books_data.json')

GIRO = 'Industrial 24/7'         # all 7 GEPP sites (imported/*/inputs.json giro)
DIV  = 'SIN'                      # Ixt DIST(Jal), Aca Centro Sur, Can Peninsular, Pro V.Mex — all SIN windows
RTE  = 0.96
MERMA = 2
PV_SUM = sum(PV_BELL)

# rev4 PV sizes — Op1 only (surface-capped design). Source: DESIGN.md §3 / wiki upsize analysis.
NEW_KWP_OP1 = {'ixt': 5170.0, 'aca': 1748.0, 'can': 1270.0}
# m2 available from Supuestos SITIOS table (4-Sitios book); pr1/pr2/tap have no row -> null.
M2_DISP = {'ixt': 25308.0, 'aca': 7019.0, 'can': 6828.0, 'pro': 15396.0,
           'pr1': None, 'pr2': None, 'tap': None}
M2_PER_KWP = 4.0                 # Supuestos!B24 density

SITE_KEYS = ['ixt', 'aca', 'can', 'pro', 'pr1', 'pr2', 'tap']

_BOOKS = None
def books():
    global _BOOKS
    if _BOOKS is None:
        _BOOKS = json.load(open(BOOKS_DATA))
    return _BOOKS


def month_year(mnum):
    """book column order is may-25..abr-26."""
    return (2025 if mnum >= 5 else 2026, mnum)


def _hourly_frame(mnum, kwh_total, gen_month):
    year, mn = month_year(mnum)
    cnt = day_counts(year, mn)
    days = sum(cnt.values())
    curve = CURVES[GIRO]
    win = WINDOWS[('SIN', season(DIV, mn))]
    load_units = sum(curve[dt][h] * cnt[dt] for dt in cnt for h in range(24))
    ls = kwh_total / load_units if load_units else 0.0
    gs = gen_month / (days * PV_SUM) if days else 0.0
    return curve, win, cnt, ls, gs


def sim_month(mnum, kwh_total, gen_month, C28, N_m, dias_punta, solar_charge=True):
    """Hourly overlap of scaled load curve vs scaled solar bell.
    Returns per-period self & excess (all days) and the day-agnostic monthly
    carga_solar / carga_base split of the fixed BESS charge N/RTE."""
    curve, win, cnt, ls, gs = _hourly_frame(mnum, kwh_total, gen_month)
    exc_per  = {'B': 0.0, 'I': 0.0, 'P': 0.0}
    self_per = {'B': 0.0, 'I': 0.0, 'P': 0.0}
    for dt in cnt:
        for h in range(24):
            load = curve[dt][h] * ls
            pv   = PV_BELL[h] * gs
            s = min(load, pv)
            e = max(0.0, pv - load)
            p = win[dt][h]
            self_per[p] += s * cnt[dt]
            exc_per[p]  += e * cnt[dt]
    exceso = sum(exc_per.values())

    charge_energy = N_m / RTE                       # fixed daily-x-days BESS charge energy (unchanged)
    if solar_charge and dias_punta:
        # representative punta day = weekday (MF); charge solar-first over sun hours, cap C28/h
        exc_MF = [max(0.0, PV_BELL[h] * gs - curve['MF'][h] * ls) for h in range(24)]
        C_day = N_m / RTE / dias_punta
        avail_solar_day = sum(min(exc_MF[h], C28) for h in range(24))
        cs_day = min(C_day, avail_solar_day)
        carga_solar = min(cs_day * dias_punta, exceso)   # V <= U (can't charge more than month excess)
    else:
        carga_solar = 0.0
    carga_base = charge_energy - carga_solar             # V + W = N/RTE  (exact)
    return dict(exc_per=exc_per, self_per=self_per, exceso=exceso, self_tot=sum(self_per.values()),
                carga_solar=carga_solar, carga_base=carga_base, charge_energy=charge_energy)


def N_month(s, c, i):
    C30, C28 = c['30'], c['28']
    return min(C30 * s['dias_punta'][i], C28 * s['hrs_punta'][i] * s['dias_punta'][i], s['kwh_punta'][i])


def motor_site(sitekey, op, kwp, solar_charge=True):
    """Full monthly rev4 motor for one site/option at a given kWp (anchored to rev3).
    Returns dict with per-month arrays and annual roll-ups."""
    B = books(); s = B[sitekey]; c = s[op]
    C30, C28, Qdiv = c['30'], c['28'], c['Q_div']
    kwp_rev3 = c['26']
    Mdiv = c['M_div']
    texc = 0.0 if op == 'op1' else None   # Op1 autoconsumo excedente ~ $0; Op2 has no excess (small PV)
    mo = []
    ann = dict(exceso=0.0, carga_solar=0.0, carga_base=0.0, N=0.0, O_new=0.0, O_rev3=0.0,
               P_new=0.0, Q=0.0, R_new=0.0, R_rev3=0.0, gen=0.0, self=0.0, self_rev3=0.0,
               J_new=0.0, J_rev3=0.0, distrib=0.0, distrib_rev3=0.0, ajuste=0.0, bonus=0.0)
    for i in range(12):
        mnum = s['months'][i]
        tb, ti, tp = s['t_base'][i], s['t_int'][i], s['t_punta'][i]
        c_oport = 0.0 if op == 'op1' else ti      # Op2 net-metering: charging forgoes ~t_int credit
        texc_i = 0.0 if op == 'op1' else ti
        kwh_tot = s['kwh_base'][i] + s['kwh_inter'][i] + s['kwh_punta'][i]
        yld = s['yield'][i]
        gen = kwp * yld
        gen_rev3 = kwp_rev3 * yld
        N = N_month(s, c, i)
        dias = s['dias_punta'][i]
        sim  = sim_month(mnum, kwh_tot, gen,      C28, N, dias, solar_charge=solar_charge)
        sim0 = sim_month(mnum, kwh_tot, gen_rev3, C28, N, dias, solar_charge=False)  # rev3 basis (no solar chg)

        # ---- PV side PRIMARY (self-basis, anchored per period) ----
        # rev3 self kWh per period = gen_rev3 * DEF_rev3; increment = sim self delta per period
        self_new = {}
        rev3_DEF = {'B': c['D'][i], 'I': c['E'][i], 'P': c['F'][i]}
        for p in 'BIP':
            self_new[p] = gen_rev3 * rev3_DEF[p] + (sim['self_per'][p] - sim0['self_per'][p])
        trate = {'B': tb, 'I': ti, 'P': tp}
        J_rev3 = gen_rev3 * (c['D'][i]*tb + c['E'][i]*ti + c['F'][i]*tp)
        J_new = sum(self_new[p] * trate[p] for p in 'BIP')        # = J_rev3 + dJ exactly
        distrib_rev3 = c['L'][i] * kwp_rev3 / Mdiv
        distrib = c['L'][i] * kwp / Mdiv
        M_new = J_new + distrib
        # D/E/F self-basis (fractions of TOTAL gen; D+E+F = pct_ac < 1, rev3-style)
        D1 = self_new['B'] / gen if gen else 0.0
        E1 = self_new['I'] / gen if gen else 0.0
        F1 = self_new['P'] / gen if gen else 0.0
        # K (energy PPA) PRIMARY = SELF-CONSUMED (rev3 basis: K72=self, C46=K72*C31)
        K_self = sum(self_new.values())
        K_new = K_self

        # ---- excess bookkeeping ----
        exceso = sim['exceso']; carga_solar = sim['carga_solar']
        remanente = max(0.0, exceso - carga_solar)
        # GEN-BASIS (labeled, retained for post-approval engine formalization)
        gen_per = {p: sim['self_per'][p] + sim['exc_per'][p] for p in 'BIP'}   # = pv per period
        Dg = gen_per['B'] / gen if gen else 0.0
        Eg = gen_per['I'] / gen if gen else 0.0
        Fg = gen_per['P'] / gen if gen else 0.0
        J_base = gen * (Dg * tb + Eg * ti + Fg * tp)              # all gen at retail
        # ajuste (gen-basis only): all excess at (t_per - texc); Op1 texc=0.
        ajuste = sum(sim['exc_per'][p] * (trate[p] - texc_i) for p in 'BIP')
        ajuste_residual = J_base - J_new    # diagnostic: gap vs rev3-anchored J (sim-vs-calc_core autoconsumo)

        # ---- BESS side (anchored): O_new + solar-charge bonus ----
        carga_base = sim['carga_base']
        O_rev3 = (N / RTE) * tb
        O_new = carga_base * tb + carga_solar * c_oport
        bonus = O_rev3 - O_new                       # = carga_solar*(t_base - c_oport)
        P_new = N * tp - O_new
        Q = c['Q_coefs'][i] * min(1.0, C30 / Qdiv)
        R_new = P_new + Q
        R_rev3 = (N * tp - O_rev3) + Q

        mo.append(dict(month=mnum, gen_kwh=gen, exceso_kwh=exceso, carga_solar_kwh=carga_solar,
                       carga_base_kwh=carga_base, remanente_kwh=remanente,
                       exc_per={p: sim['exc_per'][p] for p in 'BIP'},
                       D=D1, E=E1, F=F1,                      # PRIMARY self-basis split (sum<1)
                       D_gen=Dg, E_gen=Eg, F_gen=Fg,          # gen-basis split (sum=1, labeled)
                       ajuste_excedente_gen_mxn=ajuste, ajuste_residual_mxn=ajuste_residual,
                       O_new_mxn=O_new, O_rev3_mxn=O_rev3,
                       N_kwh=N, P_new_mxn=P_new, Q_mxn=Q, R_new_mxn=R_new,
                       J_new_mxn=J_new, M_new_mxn=M_new,
                       K_new_kwh=K_new, K_gen_kwh=gen,
                       carga_solar_bonus_mxn=bonus))
        ann['exceso']+=exceso; ann['carga_solar']+=carga_solar; ann['carga_base']+=carga_base
        ann['N']+=N; ann['O_new']+=O_new; ann['O_rev3']+=O_rev3; ann['P_new']+=P_new
        ann['Q']+=Q; ann['R_new']+=R_new; ann['R_rev3']+=R_rev3; ann['gen']+=gen
        ann['self']+=sim['self_tot']; ann['self_rev3']+=sim0['self_tot']
        ann['J_new']+=J_new; ann['J_rev3']+=J_rev3; ann['distrib']+=distrib
        ann['distrib_rev3']+=distrib_rev3; ann['ajuste']+=ajuste; ann['bonus']+=bonus
        ann.setdefault('ajuste_residual',0.0); ann['ajuste_residual']+=ajuste_residual
    ann['M72_new'] = ann['J_new'] + ann['distrib']
    ann['M72_rev3'] = ann['J_rev3'] + ann['distrib_rev3']
    ann['K72_new'] = sum(m['K_new_kwh'] for m in mo)     # PRIMARY: self-basis
    ann['K72_self'] = ann['K72_new']
    ann['K72_gen'] = ann['gen']                          # gen-basis (labeled)
    ann['R72_new'] = ann['R_new']
    ann['ahorro_bess_bruto'] = ann['R72_new'] * (12 - MERMA) / 12
    ann['ahorro_bess_bruto_rev3'] = ann['R_rev3'] * (12 - MERMA) / 12
    ann['kwp'] = kwp; ann['kwp_rev3'] = kwp_rev3
    return dict(months=mo, annual=ann)


# ---------------- typical-day 24h profiles (deck) ----------------
def typical_day(sitekey, season_key):
    """Rebuild the design-day profile with solar-first charge placement.
    carga = rev3 static curve (IDENTICAL); pv scaled by kWp_new/kWp_old; chg recomputed
    (solar-first over hours pv>carga, cap C28; base top-up flat in 0-5; total = C30/RTE);
    dis = flat-top punta shave (min(C30, punta energy after pv), cap C28); neta=carga-pv-chg-dis."""
    import json as _j
    deck = _j.load(open('/home/mario/CFE Brain/work/gepp-deck/gepp_data_tir14.json'))
    prof = deck['sites'][sitekey][season_key]['prof']
    B = books(); c = B[sitekey]['op1']
    C28, C30 = c['28'], c['30']
    kwp_old = c['26']
    kwp_new = NEW_KWP_OP1.get(sitekey, kwp_old)
    scale = kwp_new / kwp_old
    carga = [row['carga'] for row in prof]
    pv    = [row['pv'] * scale for row in prof]
    per   = [row['per'] for row in prof]
    # discharge: punta hours, flat-top
    punta_idx = [h for h in range(24) if per[h] == 'Punta']
    after_pv = [max(0.0, carga[h] - pv[h]) for h in range(24)]
    disp_energy = min(C30, sum(after_pv[h] for h in punta_idx))
    nph = len(punta_idx)
    # flat-top level so that shaved energy above level = disp_energy
    if nph:
        peaks = sorted((after_pv[h] for h in punta_idx), reverse=True)
        # solve level: sum(max(0, p-level)) = disp_energy, cap each shave by C28
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
    # charge: total energy = C30/RTE. solar-first where pv>carga (sun hours), cap C28
    charge_total = C30 / RTE
    chg = [0.0] * 24
    exc = [max(0.0, pv[h] - carga[h]) for h in range(24)]
    remaining = charge_total
    for h in range(24):
        if exc[h] > 0 and remaining > 0:
            take = min(exc[h], C28, remaining)
            chg[h] = -take
            remaining -= take
    # base top-up flat over hours 0-5
    if remaining > 1e-6:
        base_hrs = [h for h in range(6)]
        per_h = remaining / len(base_hrs)
        for h in base_hrs:
            add = min(C28 - (-chg[h]), per_h)
            chg[h] += -add
    out = []
    for h in range(24):
        neta = carga[h] - pv[h] - chg[h] - dis[h]
        out.append(dict(h=h, per=per[h], carga=round(carga[h], 2), pv=round(pv[h], 2),
                        chg=round(chg[h], 2), dis=round(dis[h], 2), neta=round(neta, 2)))
    return out


if __name__ == '__main__':
    # gate 1: old-mode replica (old kWp, solar OFF) reproduces rev3 R72 & C52-inputs exactly
    print("GATE 1 — old-mode replica (old kWp, solar disabled) vs rev3 cached R72/K72/M72 (self-basis):")
    B = books()
    worst = 0.0
    for k in SITE_KEYS:
        for op in ['op1', 'op2']:
            r = motor_site(k, op, B[k][op]['26'], solar_charge=False)
            a = r['annual']
            ca = B[k][op]['cache']
            dR = abs(a['R_new'] - ca['R72']) / ca['R72'] * 100
            dK = abs(a['K72_self'] - ca['K72']) / ca['K72'] * 100
            dM = abs(a['M72_new'] - ca['M72']) / ca['M72'] * 100
            worst = max(worst, dR, dK, dM)
            print(f"  {k:4s} {op}: R72 d={dR:.5f}%  K72 d={dK:.5f}%  M72 d={dM:.5f}%")
    print(f"  WORST deviation = {worst:.5f}%  ({'PASS' if worst < 0.1 else 'FAIL'})")
