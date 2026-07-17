#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deck_model.py — build-time deck inputs (issue #3): closes the Stage-4 gaps in
docs/roof-design-calculo-flow.md so the deck MODEL no longer needs hand edits:

  1. PPA price / pago / participación — ported from the pricer stage
     (cfe/vault/tools/ppa_pricer.py for engine offers; solve_k_cs-style book
     k-solve for the GEPP books), PARAMETERIZED by target investor IRR.
  2. Proyección 20 años — deck-schema rows (yr/pleno/autoab/real/apv/abess/
     ppa/part/neto/acum/pct) from annual anchors + Supuestos escalations.
  3. Régimen Op1 vs Op2 — two calc_core runs per RPU (autoconsumo vs
     generador-exento cap), with single-option fallback when only one regime
     is available (kwp < 700).
  4. Despacho 24 h invierno/verano — solar-first typical-day dispatcher
     (bit-for-bit replay of the rev4 motor_cs typical_day); synthetic
     load-curve fallback footnoted "ilustrativo".

OPEN DECISIONS — parameterized, NO hardcoded winner (both variants' GEPP
outputs live in golden baselines.json for the decision-maker):
  * target_irr : 0.14 vs 0.19 — every pricing/projection entry point takes it
    explicitly; there is no default.
  * punta_basis: 'billing' (book dias_punta from the bill/perfil) vs
    'calendar' (punta_weekdays = Mon–Fri minus festivos). Book path supports
    both; the engine path is calendar-only (calc_core hardcodes
    punta_weekdays and engine bills carry no dias_punta) — flagged in output.

Stdlib only. Reuses in-repo engines (never duplicated):
  tools/solar-charge-bess-calculator/dispatch_cs.py  (rev4 book motor)
  cfe/vault/tools/{calc_core,ppa_pricer}.py          (golden engine + pricer)
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CALC = os.path.join(REPO, 'tools', 'solar-charge-bess-calculator')
VAULT_TOOLS = os.path.join(REPO, 'cfe', 'vault', 'tools')
# vault first (canonical load_curves/cfe_savings), calculator second (dispatch_cs)
sys.path.insert(0, CALC)
sys.path.insert(0, VAULT_TOOLS)
os.environ.setdefault('BOOKS_DATA', os.path.join(CALC, 'books_data.json'))

import calc_core            # noqa: E402
import dispatch_cs as D     # noqa: E402
import ppa_pricer           # noqa: E402
from cfe_savings.defaults import punta_weekdays  # noqa: E402
from load_curves import CURVES, PV_BELL, WINDOWS, day_counts, season  # noqa: E402

RTE = D.RTE
SITES4 = ['ixt', 'aca', 'can', 'pro']
SITESP = ['pr1', 'pr2', 'tap']
DG_CEILING_KWP = 700.0          # calc_core gate: kwp >= 700 -> autoconsumo
EXENTO_KWP = 699.9              # largest size calc_core treats as generador exento
PUNTA_BASES = ('billing', 'calendar')
DESPACHO_FOOTNOTE = ('Despacho ilustrativo — curva de giro escalada al recibo '
                     'mensual + campana solar sintética, sin medición 15-minutal '
                     '(prefactibilidad).')

_PV_SUM = sum(PV_BELL)


# ---------------------------------------------------------------- finance
def irr(cf, lo=-0.9, hi=5.0):
    def npv(r):
        return sum(c / (1 + r) ** i for i, c in enumerate(cf))
    flo = npv(lo)
    for _ in range(400):
        mid = (lo + hi) / 2
        fm = npv(mid)
        if abs(fm) < 1e-9 or hi - lo < 1e-14:
            return mid
        if flo * fm < 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2


def npv_excel(rate, cfs):
    return sum(c / (1 + rate) ** (i + 1) for i, c in enumerate(cfs))


def supuestos():
    """Named view of the rev3 book Supuestos (B4..B26)."""
    S = D.books()['supuestos']
    return dict(
        fx=S['B4'], usd_wp=S['B5'], esc_cfe=S['B9'], esc_ppa=S['B10'],
        degr_pv=S['B11'], degr_bess=S['B12'], participacion=S['B17'],
        ppa_yrs=int(S['B18']), bess_yrs=int(S['B19']), horizon=int(S['B20']),
        wacc=S['B21'], om_pv_kwp=S['B22'], om_bess_kwh=S['B23'],
        m2_per_kwp=S['B24'], year0=int(S['B25']), autoabasto_until=int(S['B26']))


# ---------------------------------------------------------------- 20-yr projection
def proj_rows(a, sup):
    """Deck-schema 20-yr projection (rev3 book formula, rows 94-139).

    anchors a: real (gasto actual año1), autoab (beneficio autoabasto año1),
    ahorro_pv, ahorro_bess, ppa_kwh (PPA billing base), price ($/kWh año1),
    kwp, bess_kwh, participacion, capex_pv, capex_bess.
    Returns dict(rows=[Año 0 + 20], tir_pv, tir_bess, van_cliente)."""
    rows = [dict(yr='Año 0', pleno=0, autoab=0, real=0, apv=0, abess=0,
                 ppa=0, part=0, neto=0, acum=0, pct=0)]
    Mcol = [-a['capex_pv']]
    Ncol = [-a['capex_bess']]
    Jcol = []
    acum = 0.0
    pleno1 = a['real'] + a['autoab']
    for y in range(1, 21):
        esc = (1 + sup['esc_cfe']) ** (y - 1)
        escp = (1 + sup['esc_ppa']) ** (y - 1)
        dpv = (1 - sup['degr_pv']) ** (y - 1)
        dbe = (1 - sup['degr_bess']) ** (y - 1)
        yr = sup['year0'] + (y - 1)
        pleno = pleno1 * esc
        autoab = a['autoab'] * esc if yr <= sup['autoabasto_until'] else 0.0
        real = pleno - autoab
        apv = a['ahorro_pv'] * esc * dpv
        abess = a['ahorro_bess'] * esc * dbe
        ppa = a['ppa_kwh'] * a['price'] * escp * dpv if y <= sup['ppa_yrs'] else 0.0
        part = abess * a['participacion'] if y <= sup['bess_yrs'] else 0.0
        neto = apv + abess - ppa - part
        acum += neto
        rows.append(dict(yr=yr, pleno=pleno, autoab=autoab, real=real, apv=apv,
                         abess=abess, ppa=ppa, part=part, neto=neto, acum=acum,
                         pct=neto / real if real else 0))
        Mcol.append(ppa - sup['om_pv_kwp'] * a['kwp'] * esc if y <= sup['ppa_yrs'] else 0.0)
        Ncol.append(part - sup['om_bess_kwh'] * a['bess_kwh'] * esc if y <= sup['bess_yrs'] else 0.0)
        Jcol.append(neto)
    return dict(rows=rows, Mcol=Mcol, Ncol=Ncol,
                tir_pv=irr(Mcol), tir_bess=irr(Ncol),
                van_cliente=npv_excel(sup['wacc'], Jcol))


# ---------------------------------------------------------------- book path (GEPP)
def _books_for(punta_basis):
    """Book extract under the requested punta-day basis. 'billing' = as
    delivered (dias_punta from the perfil workbook); 'calendar' = replace
    dias_punta with punta_weekdays(year, month)."""
    if punta_basis == 'billing':
        return D.books()
    if punta_basis != 'calendar':
        raise ValueError('punta_basis must be one of %s' % (PUNTA_BASES,))
    B = copy.deepcopy(D.books())
    for sk in SITES4 + SITESP:
        s = B[sk]
        s['dias_punta'] = [float(punta_weekdays(*D.month_year(m)))
                           for m in s['months']]
    return B


class _punta_books:
    """Temporarily point dispatch_cs at the basis-adjusted book extract."""
    def __init__(self, punta_basis):
        self.books = _books_for(punta_basis)

    def __enter__(self):
        self._saved = D._BOOKS
        D._BOOKS = self.books
        return self.books

    def __exit__(self, *exc):
        D._BOOKS = self._saved


_MOTOR_CACHE = {}


def book_anchors(sitekey, op, k, punta_basis='billing', kwp=None):
    """Projection anchors for one GEPP site/option at PPA multiplier k
    (self-basis PRIMARY: PPA billed on self-consumed K72, rev3 continuity).
    Motor runs are k-independent -> cached per (site, op, kwp, basis)."""
    sup = supuestos()
    with _punta_books(punta_basis) as B:
        c = B[sitekey][op]
        if kwp is None:
            kwp = D.NEW_KWP_OP1.get(sitekey, c['26']) if op == 'op1' else c['26']
        key = (sitekey, op, round(kwp, 3), punta_basis)
        if key not in _MOTOR_CACHE:
            _MOTOR_CACHE[key] = D.motor_site(sitekey, op, kwp)['annual']
        r = _MOTOR_CACHE[key]
    return dict(real=c['N19'], autoab=c['38'], ahorro_pv=r['M72_new'],
                ahorro_bess=r['ahorro_bess_bruto'], ppa_kwh=r['K72_self'],
                price=c['31'] * k, kwp=kwp, bess_kwh=c['29'],
                participacion=sup['participacion'],
                capex_pv=kwp * 1000 * sup['usd_wp'] * sup['fx'],
                capex_bess=c['36'])


def solve_k_book(op, target_irr, punta_basis='billing', sites=SITES4):
    """PPA multiplier k so the COMBINED investor IRR (PV PPA + BESS
    participación over `sites`) hits target_irr. solve_k_cs.py methodology,
    with target IRR and punta basis as parameters (open decisions)."""
    sup = supuestos()

    def combined(k):
        cf = [0.0] * 21
        for sk in sites:
            r = proj_rows(book_anchors(sk, op, k, punta_basis), sup)
            for y in range(21):
                cf[y] += r['Mcol'][y] + r['Ncol'][y]
        return cf

    lo, hi = 0.3, 3.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if irr(combined(mid)) < target_irr:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-13:
            break
    k = (lo + hi) / 2
    return dict(k=k, irr=irr(combined(k)), target_irr=target_irr,
                punta_basis=punta_basis, sites=sites)


# ---------------------------------------------------------------- engine path (any RPU)
def dual_run(inputs, bills, op2_kwp=None):
    """Régimen Op1 vs Op2: two calc_core runs per RPU.
    Op1 = the offer as-is; Op2 = generador-exento run at op2_kwp (default
    EXENTO_KWP, strictly <700 per the engine gate; the book AC-side
    convention 839.45 kWp DC is NOT the engine's — pass op2_kwp to override).
    Single-option fallback: offer already <700 kWp -> one regime available."""
    kwp = float(inputs.get('kwp') or 0.0)
    r1 = calc_core.compute(inputs, bills)
    if kwp < DG_CEILING_KWP:
        return dict(single=True, op1=r1, op2=None,
                    nota='kwp %.1f < %.0f: solo régimen generador exento — '
                         'deck de opción única' % (kwp, DG_CEILING_KWP))
    k2 = float(op2_kwp) if op2_kwp is not None else min(kwp, EXENTO_KWP)
    r2 = calc_core.compute(dict(inputs, kwp=k2), bills)
    return dict(single=False, op1=r1, op2=r2, nota=None)


def ppa_terms(inputs, bills, target_irr, escenario='Hibrido'):
    """Client-facing PPA terms from the pricer stage (ppa_pricer.price),
    parameterized by target investor IRR. Engine deal = PPA on TOTAL
    generation + participación sobre ahorro BESS, O&M/fianza inside."""
    pr = ppa_pricer.price(inputs, bills, target_irr=target_irr,
                          solve='ppa', escenario=escenario, sensitivity=False)
    out = dict(target_irr=target_irr, escenario=escenario,
               precio_ppa=pr['ppa_rate'], participacion=pr['comision'],
               ppa_yrs=pr['ppa_yrs'], esc_ppa=pr['esc_ppa'],
               feasible=pr['feasible'])
    if pr['feasible']:
        out.update(pago_anio1=pr['flows'][0]['ppa_pay'],
                   participacion_anio1=pr['flows'][0]['comision'],
                   cliente_anio1=pr['cliente']['beneficio_anio1'],
                   pct_ahorro_retenido_a1=pr['cliente']['pct_ahorro_retenido_a1'],
                   tir_financiador=pr['tir_financiador'],
                   tarifa_cfe_blend=pr['cliente']['tarifa_cfe_blend'])
    return out


def proj_from_deal(res, ppa, comision, esc='Hibrido'):
    """Deck-schema 20-yr rows for an engine offer, internally consistent with
    ppa_pricer.deal_flows (same escalation/degradation exponents as the
    engine's _finance — NOT the book's (y-1) exponents)."""
    p, annual = res['inputs'], res['annual']
    has_pv = esc in ('PV', 'Hibrido') and p['kwp'] > 0
    has_bess = esc in ('BESS', 'Hibrido') and p['bess_kwh'] > 0
    base_pv = (annual['ah_pv'] + annual['dem_pv']) if has_pv else 0.0
    base_bess = annual['dem_bess_h'] + annual['arb'] if esc == 'Hibrido' else \
        (annual['bess_only'] if esc == 'BESS' else 0.0)
    bruto0 = annual['hibrido'] if esc == 'Hibrido' else \
        (annual['bess_only'] if esc == 'BESS' else annual['pv_only'])
    base_claw = bruto0 - base_pv - base_bess if esc != 'BESS' else 0.0
    gen = annual['gen'] if has_pv else 0.0
    import datetime
    year0 = max(b['year'] for b in res['validacion']) + 1 if res['validacion'] else \
        datetime.date.today().year
    rows = [dict(yr='Año 0', pleno=0, autoab=0, real=0, apv=0, abess=0,
                 ppa=0, part=0, neto=0, acum=0, pct=0)]
    acum = 0.0
    for yy in range(1, p['horizon'] + 1):
        e = (1 + p['esc_cfe']) ** yy
        dpv = (1 - p['pv_degr']) ** yy
        dbe = (1 - p['bess_degr']) ** yy
        real = annual['antes'] * e
        apv = base_pv * e * dpv + base_claw * e * (dpv + dbe) / 2
        abess = base_bess * e * dbe * p['falla']
        pago = (gen * dpv * ppa * (1 + p['esc_ppa']) ** (yy - 1)
                if has_pv and yy <= p['ppa_yrs'] else 0.0)
        part = abess * comision if has_bess and yy <= p['bess_yrs'] else 0.0
        neto = apv + abess - pago - part
        acum += neto
        rows.append(dict(yr=year0 + (yy - 1), pleno=real, autoab=0.0, real=real,
                         apv=apv, abess=abess, ppa=pago, part=part, neto=neto,
                         acum=acum, pct=neto / real if real else 0))
    return rows


# ---------------------------------------------------------------- despacho 24 h
def dispatch_day(carga, pv, per, bess_kw, util_kwh, rte=RTE, punta_cap=None):
    """Solar-first typical-day dispatch (rev4 motor_cs typical_day replay):
    discharge = flat-top punta shave of min(util_kwh, punta-after-PV[, punta_cap]),
    charge = solar-first over hours pv>carga (cap bess_kw), base top-up 0-5;
    total charge = util_kwh/rte. Returns 24 deck-prof rows."""
    punta_idx = [h for h in range(24) if per[h] == 'Punta']
    after_pv = [max(0.0, carga[h] - pv[h]) for h in range(24)]
    disp = min(util_kwh, sum(after_pv[h] for h in punta_idx))
    if punta_cap is not None:
        disp = min(disp, punta_cap)
    dis = [0.0] * 24
    if punta_idx:
        lo, hi = 0.0, max(after_pv[h] for h in punta_idx)
        for _ in range(80):
            lvl = (lo + hi) / 2
            shaved = sum(min(bess_kw, max(0.0, after_pv[h] - lvl)) for h in punta_idx)
            if shaved > disp:
                lo = lvl
            else:
                hi = lvl
        lvl = (lo + hi) / 2
        for h in punta_idx:
            dis[h] = min(bess_kw, max(0.0, after_pv[h] - lvl))
    chg = [0.0] * 24
    rem = util_kwh / rte if rte else 0.0
    for h in range(24):
        exc = pv[h] - carga[h]
        if exc > 0 and rem > 0:
            take = min(exc, bess_kw, rem)
            chg[h] = -take
            rem -= take
    if rem > 1e-6:
        per_h = rem / 6
        for h in range(6):
            add = min(bess_kw - (-chg[h]), per_h)
            chg[h] += -add
    return [dict(h=h, per=per[h], carga=round(carga[h], 2), pv=round(pv[h], 2),
                 chg=round(chg[h], 2), dis=round(dis[h], 2),
                 neta=round(carga[h] - pv[h] - chg[h] - dis[h], 2))
            for h in range(24)]


def _design_bill(bills, division, season_key):
    cands = [b for b in bills if season(division, b['month']) == season_key]
    if not cands:
        cands = bills
    return max(cands, key=lambda b: (b.get('kw_punta') or 0.0,
                                     b.get('kwh_punta') or 0.0))


def synthetic_profiles(inputs, bills, kwp, bess_kw, bess_kwh,
                       punta_basis='calendar', dod=0.96, rte=RTE,
                       yield_monthly=None):
    """Despacho 24 h invierno/verano when no measured/static profile exists.
    Carga = giro curve (MF) scaled to the design bill; PV = solar bell scaled
    to the month's generation. punta_basis sets the per-day punta-energy cap:
    'billing' needs a dias_punta field on the bill (book/perfil sourced),
    'calendar' uses punta_weekdays. Footnoted 'ilustrativo' (issue #3)."""
    giro = inputs.get('giro') or 'Otro'
    curva = giro if giro in CURVES else 'Otro'
    division = inputs.get('division') or 'SIN'
    util = bess_kwh * dod * (rte ** 0.5)
    ym = yield_monthly or {}
    out = dict(synthetic=True, footnote=DESPACHO_FOOTNOTE,
               punta_basis=punta_basis)
    for skey, dkey in (('invierno', 'inv'), ('verano', 'ver')):
        b = _design_bill(bills, division, skey)
        y, m = b['year'], b['month']
        cnt = day_counts(y, m)
        curve = CURVES[curva]
        win = WINDOWS[((division.upper() if division.upper() in ('BC', 'BCS')
                        else 'SIN'), season(division, m))]
        kwh_tot = (b.get('kwh_base') or 0) + (b.get('kwh_inter') or 0) + \
                  (b.get('kwh_punta') or 0)
        load_units = sum(curve[dt][h] * cnt[dt] for dt in cnt for h in range(24))
        ls = kwh_tot / load_units if load_units else 0.0
        gen = kwp * float(ym.get(m) or ym.get(str(m)) or 0.0)
        days = sum(cnt.values())
        gs = gen / (days * _PV_SUM) if days else 0.0
        if punta_basis == 'billing':
            dias = b.get('dias_punta')
            if not dias:
                raise ValueError("punta_basis='billing' pero el recibo %s-%02d "
                                 "no trae dias_punta" % (y, m))
        else:
            dias = punta_weekdays(y, m)
        punta_cap = (b.get('kwh_punta') or 0.0) / dias if dias else None
        carga = [curve['MF'][h] * ls for h in range(24)]
        pv = [PV_BELL[h] * gs for h in range(24)]
        per = [{'B': 'Base', 'I': 'Intermedio', 'P': 'Punta'}[win['MF'][h]]
               for h in range(24)]
        prof = dispatch_day(carga, pv, per, bess_kw, util, rte, punta_cap)
        out[dkey] = dict(prof=prof, lect=DESPACHO_FOOTNOTE,
                         design_month='%04d-%02d' % (y, m))
    return out


# ---------------------------------------------------------------- baseline 12-mo
def baseline_12mo(bills):
    """Deck baseline block straight from the bills (Σ recibos doctrine)."""
    bs = sorted(bills, key=lambda b: (b['year'], b['month']))
    lab = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep',
           'oct', 'nov', 'dic']

    def col(f):
        return [round(b.get(f) or 0.0, 2) for b in bs]

    gasto = [round(b.get('facturacion_recibo') or
                   calc_core.validate_bill(b)['calc_total'], 2) for b in bs]
    out = dict(months=['%s-%02d' % (lab[b['month'] - 1], b['year'] % 100) for b in bs],
               cbase=col('kwh_base'), cint=col('kwh_inter'),
               cpunta=col('kwh_punta'),
               ctotal=[round((b.get('kwh_base') or 0) + (b.get('kwh_inter') or 0) +
                             (b.get('kwh_punta') or 0), 2) for b in bs],
               dpunta=col('kw_punta'), dmax=col('kw_max'), gasto=gasto)
    for key in ('cbase', 'cint', 'cpunta', 'ctotal', 'dpunta', 'dmax', 'gasto'):
        out[key + '_tot'] = round(sum(out[key]), 2)
    return out
