// -*- deterministic PV/BESS/Hibrido engine -*-
// Faithful port of CFE Brain tools/calc_core.py + load_curves.py + cfe_savings/defaults.py.
// Single source of truth for the PPA+BESS solution logic behind the GEPP projects
// (GEPP - Propuesta PV+BESS 4 Sitios rev3 - BESS verano 2h).
//
// Golden doctrine (see CFE Brain/CLAUDE.md):
//   < 700 kWp : generador exento / medicion neta — PV credited up to monthly kWh intermedio
//   >= 700 kWp: autoconsumo — only pct_autoconsumo credited; excedentes at texc (default 0)
//   BESS      : SAE-CC — discharge only punta weekdays, capped at the bill's punta kWh
//   capacidad on kW_punta, distribucion on max(B,I,P), umbral = kWh/(days*24*FC), FC=0.57
//
// Plain ESM JS (no TS types) so it runs unchanged under Node (tests) and Deno (edge).

// ============================================================================
// defaults.py — regulatory constants + schedules
// ============================================================================
export const FC_GDMTH = 0.57;
export const IVA = 0.16;
export const DG_CEILING_KW = 700.0;

function _sin_punta_hours(month) { return (month >= 4 && month <= 10) ? 2 : 4; }
function _bcs_punta_hours(month) { return (month >= 4 && month <= 10) ? 10 : 0; }
function _bc_punta_hours(month) { return (month >= 5 && month <= 10) ? 4 : 0; }

export function punta_hours(division, month) {
  const d = (division || "SIN").toUpperCase();
  if (d === "BCS") return _bcs_punta_hours(month);
  if (d === "BC") return _bc_punta_hours(month);
  return _sin_punta_hours(month);
}

// Python date.weekday(): Mon=0..Sun=6.  JS getUTCDay(): Sun=0..Sat=6.
function pyWeekday(y, m, d) { return (new Date(Date.UTC(y, m - 1, d)).getUTCDay() + 6) % 7; }
function daysInMonth(y, m) { return new Date(Date.UTC(y, m, 0)).getUTCDate(); }

// nth Monday of (year, month): mirrors defaults._nth_monday
function _nthMonday(year, month, n) {
  const wd1 = pyWeekday(year, month, 1);
  const off = (7 - wd1) % 7;
  return 1 + off + 7 * (n - 1); // day-of-month
}

// Statutory holidays treated as domingo by the tariff schedule (defaults.festivos).
// Returned as a Set of "m-d" keys.
export function festivos(year) {
  const s = new Set();
  const add = (m, d) => s.add(m + "-" + d);
  add(1, 1);
  add(2, _nthMonday(year, 2, 1));
  add(3, _nthMonday(year, 3, 3));
  add(5, 1);
  add(9, 16);
  add(11, _nthMonday(year, 11, 3));
  add(12, 25);
  return s;
}

// Days of the month that carry a punta window (Mon-Fri minus festivos).
export function punta_weekdays(year, month) {
  const f = festivos(year);
  let n = 0;
  const dm = daysInMonth(year, month);
  for (let d = 1; d <= dm; d++) {
    if (pyWeekday(year, month, d) < 5 && !f.has(month + "-" + d)) n++;
  }
  return n;
}

// ============================================================================
// load_curves.py — industry curves, CFE windows, autoconsumo overlap
// ============================================================================
function _blk(segs) {
  const v = new Array(24).fill(0.0);
  for (const [a, b, x] of segs) for (let h = a; h < b; h++) v[h] = x;
  return v;
}

export const CURVES = {
  "Hotel/Turismo": {
    MF: _blk([[0, 6, .55], [6, 7, .60], [7, 11, .75], [11, 17, .80], [17, 18, .90], [18, 23, 1.0], [23, 24, .70]]),
    SA: _blk([[0, 6, .58], [6, 7, .62], [7, 11, .78], [11, 17, .82], [17, 18, .92], [18, 23, 1.0], [23, 24, .72]]),
    DO: _blk([[0, 6, .58], [6, 7, .62], [7, 11, .78], [11, 17, .80], [17, 18, .90], [18, 23, 1.0], [23, 24, .70]]),
  },
  "Industrial 24/7": {
    MF: _blk([[0, 7, .90], [7, 19, 1.0], [19, 24, .95]]),
    SA: _blk([[0, 7, .85], [7, 19, .95], [19, 24, .90]]),
    DO: _blk([[0, 24, .85]]),
  },
  "Industrial 1 turno": {
    MF: _blk([[0, 6, .20], [6, 7, .60], [7, 17, 1.0], [17, 18, .50], [18, 24, .25]]),
    SA: _blk([[0, 7, .20], [7, 14, .70], [14, 24, .20]]),
    DO: _blk([[0, 24, .20]]),
  },
  "Comercial/Retail": {
    MF: _blk([[0, 8, .30], [8, 9, .60], [9, 12, .85], [12, 19, 1.0], [19, 21, .90], [21, 23, .50], [23, 24, .30]]),
    SA: _blk([[0, 8, .30], [8, 9, .65], [9, 12, .90], [12, 19, 1.0], [19, 21, .95], [21, 23, .50], [23, 24, .30]]),
    DO: _blk([[0, 8, .30], [8, 9, .60], [9, 12, .85], [12, 19, .95], [19, 21, .85], [21, 23, .45], [23, 24, .30]]),
  },
  "Oficinas": {
    MF: _blk([[0, 7, .20], [7, 8, .50], [8, 10, .90], [10, 16, 1.0], [16, 18, .85], [18, 20, .40], [20, 24, .20]]),
    SA: _blk([[0, 8, .20], [8, 14, .35], [14, 24, .20]]),
    DO: _blk([[0, 24, .20]]),
  },
  "Otro": { MF: _blk([[0, 24, 1.0]]), SA: _blk([[0, 24, 1.0]]), DO: _blk([[0, 24, 1.0]]) },
};

function _lab(base, inter, punta) {
  const v = new Array(24).fill("I");
  for (const [a, b] of (base || [])) for (let h = a; h < b; h++) v[h] = "B";
  for (const [a, b] of (inter || [])) for (let h = a; h < b; h++) v[h] = "I";
  for (const [a, b] of (punta || [])) for (let h = a; h < b; h++) v[h] = "P";
  return v;
}

const WINDOWS = {
  "SIN|verano": { MF: _lab([[0, 6]], [], [[20, 22]]), SA: _lab([[0, 7]], [], []), DO: _lab([[0, 19]], [], []) },
  "SIN|invierno": { MF: _lab([[0, 6]], [], [[18, 22]]), SA: _lab([[0, 8]], [], [[19, 21]]), DO: _lab([[0, 18]], [], []) },
  "BC|verano": { MF: _lab([], [], [[14, 18]]), SA: _lab([], [], []), DO: _lab([], [], []) },
  "BC|invierno": { MF: _lab([[0, 17], [22, 24]], [], []), SA: _lab([[0, 18], [21, 24]], [], []), DO: _lab([[0, 24]], [], []) },
  "BCS|verano": { MF: _lab([], [], [[12, 22]]), SA: _lab([], [], [[19, 22]]), DO: _lab([], [], []) },
  "BCS|invierno": { MF: _lab([[0, 18], [22, 24]], [], []), SA: _lab([[0, 18], [21, 24]], [], []), DO: _lab([[0, 19], [21, 24]], [], []) },
};

function season(division, month) {
  const d = (division || "SIN").toUpperCase();
  if (d === "BC") return (month >= 5 && month <= 10) ? "verano" : "invierno";
  return (month >= 4 && month <= 10) ? "verano" : "invierno";
}

function day_counts(year, month) {
  const f = festivos(year);
  const out = { MF: 0, SA: 0, DO: 0 };
  const dm = daysInMonth(year, month);
  for (let d = 1; d <= dm; d++) {
    const wd = pyWeekday(year, month, d);
    if (f.has(month + "-" + d)) out.DO++;
    else if (wd < 5) out.MF++;
    else if (wd === 5) out.SA++;
    else out.DO++;
  }
  return out;
}

export function model_split(giro, division, year, month) {
  const curve = CURVES[giro];
  const dKey = (division || "SIN").toUpperCase();
  const winKey = (dKey === "BC" || dKey === "BCS" ? dKey : "SIN") + "|" + season(division, month);
  const win = WINDOWS[winKey];
  const cnt = day_counts(year, month);
  const tot = { B: 0.0, I: 0.0, P: 0.0 };
  for (const dt of ["MF", "SA", "DO"]) {
    for (let h = 0; h < 24; h++) tot[win[dt][h]] += curve[dt][h] * cnt[dt];
  }
  const s = tot.B + tot.I + tot.P;
  if (!s) return tot;
  return { B: tot.B / s, I: tot.I / s, P: tot.P / s };
}

export function fit_bills(bills, division) {
  const out = [];
  for (const giro of Object.keys(CURVES)) {
    const errs = [];
    for (const b of bills) {
      const kb = b.kwh_base || 0, ki = b.kwh_inter || 0, kp = b.kwh_punta || 0;
      const tot = kb + ki + kp;
      if (!tot) continue;
      const act = { B: kb / tot, I: ki / tot, P: kp / tot };
      const mod = model_split(giro, division, b.year, b.month);
      const e = (Math.abs(mod.B - act.B) + Math.abs(mod.I - act.I) + Math.abs(mod.P - act.P)) / 3;
      errs.push(e);
    }
    out.push({ giro, mae: errs.length ? errs.reduce((a, c) => a + c, 0) / errs.length : null });
  }
  out.sort((a, b) => (a.mae === null) - (b.mae === null) || (a.mae - b.mae));
  return { ranking: out, best: out.length && out[0].mae !== null ? out[0].giro : null };
}

const PV_BELL = Array.from({ length: 24 }, (_, h) => Math.max(0.0, Math.sin(Math.PI * (h - 7) / 12)));
const _PV_SUM = PV_BELL.reduce((a, c) => a + c, 0);

export function autoconsumo_pct(giro, year, month, kwh_month, gen_month) {
  if (gen_month <= 0 || kwh_month <= 0) return 1.0;
  const curve = CURVES[giro];
  const cnt = day_counts(year, month);
  const days = cnt.MF + cnt.SA + cnt.DO;
  let load_units = 0.0;
  for (const dt of ["MF", "SA", "DO"]) for (let h = 0; h < 24; h++) load_units += curve[dt][h] * cnt[dt];
  const ls = kwh_month / load_units;
  const gs = gen_month / (days * _PV_SUM);
  let selfc = 0.0;
  for (const dt of ["MF", "SA", "DO"]) for (let h = 0; h < 24; h++) selfc += Math.min(curve[dt][h] * ls, PV_BELL[h] * gs) * cnt[dt];
  return Math.min(1.0, selfc / gen_month);
}

// ============================================================================
// calc_core.py — inputs, validation, compute, regimen, finance
// ============================================================================
export const GIRO_PCT_AC = {
  "Hotel/Turismo": 0.80, "Industrial 24/7": 0.90, "Industrial 1 turno": 0.65,
  "Comercial/Retail": 0.75, "Oficinas": 0.60, "Otro": 0.75,
};

export const DEFAULT_INPUTS = {
  cliente: "", rpu: "", municipio: "", division: "SIN", giro: "Otro",
  demanda_contratada: 0.0, fp_correction: false, fc: 0.57,
  kwp: 0.0, yield_monthly: {}, pv_degr: 0.005, epc_usd_wp: 0.75, fx: 17.55,
  om_pv: null, ppa: 1.5, ppa_yrs: 15, esc_ppa: 0.05,
  bess_kwh: 0.0, bess_kw: 0.0, dod: 0.96, rte: 0.96, bess_degr: 0.0125,
  epc_bess: 280.0, om_bess: null, comision: 0.5, falla_meses: 3, bess_yrs: 15,
  pct_autoconsumo: null, curva: null, texc: 0.0,
  wacc: 0.12, esc_cfe: 0.05, fianza: 0.139, horizon: 20, escenario: "Hibrido",
  // rev4 GEPP solar-charge dispatch (dispatch_cs.sim_month port). OFF by
  // default: with solar_charge=false the compute() output is bit-for-bit
  // identical to the pre-flag engine (golden gate).
  solar_charge: false,
  // rev4 per-period PV credit (gap 5, dispatch_cs.sim_month self_per port).
  // OFF by default: with pv_credit_periods=false the compute() output is
  // bit-for-bit identical to the monthly-netting aprov=min(usable,ki) path.
  pv_credit_periods: false,
};

// ============================================================================
// rev4 solar-charge dispatch — dispatch_cs.py sim_month port (flag-gated)
// ============================================================================
// Split the fixed monthly BESS charge energy (carga = desc/rte) into
// carga_solar (charged from same-day PV EXCESS, hourly sim, power-capped) and
// carga_base (grid top-up in base hours). Mirrors dispatch_cs.sim_month:
//   - hourly frame: load curve (giro) scaled to kwh_total; PV bell scaled to gen
//   - exceso = Σ max(0, pv_h - load_h) over all days (hourly excess)
//   - representative punta day = weekday (MF); avail = Σ min(exc_MF_h, bess_kw)
//   - cs_day = min(charge_energy/dias_punta, avail); carga_solar = min(cs_day *
//     dias_punta, exceso, exced_month) — the extra exced_month cap enforces the
//     three-bucket no-double-count against the engine's MONTHLY-NETTING
//     accounting: under medición neta every excess kWh inside the netting
//     credit (aprov) is already valued at bnd_i, so only the engine's own
//     rejected excess (exced = gen - aprov, worth texc≈0) may charge the BESS
//     at opportunity cost texc.
// Buckets (no double count): self/netting credit (aprov @ bnd_i) + BESS charge
// (carga_solar @ texc) + exported remainder (exced_export @ texc); the three
// partition gen exactly: aprov + carga_solar + exced_export = gen.
export function solar_charge_split(curvaKey, year, month, kwh_total, gen_month,
                                   bess_kw, charge_energy, dias_punta, exced_month) {
  if (!dias_punta || charge_energy <= 0 || gen_month <= 0 || kwh_total <= 0)
    return { carga_solar: 0.0, exceso: 0.0 };
  const curve = CURVES[curvaKey] || CURVES["Otro"];
  const cnt = day_counts(year, month);
  const days = cnt.MF + cnt.SA + cnt.DO;
  let load_units = 0.0;
  for (const dt of ["MF", "SA", "DO"]) for (let h = 0; h < 24; h++) load_units += curve[dt][h] * cnt[dt];
  const ls = load_units ? kwh_total / load_units : 0.0;
  const gs = days ? gen_month / (days * _PV_SUM) : 0.0;
  let exceso = 0.0;
  for (const dt of ["MF", "SA", "DO"])
    for (let h = 0; h < 24; h++)
      exceso += Math.max(0.0, PV_BELL[h] * gs - curve[dt][h] * ls) * cnt[dt];
  let avail_solar_day = 0.0;
  for (let h = 0; h < 24; h++)
    avail_solar_day += Math.min(Math.max(0.0, PV_BELL[h] * gs - curve.MF[h] * ls), bess_kw);
  const C_day = charge_energy / dias_punta;
  const cs_day = Math.min(C_day, avail_solar_day);
  const carga_solar = Math.max(0.0, Math.min(cs_day * dias_punta, exceso, exced_month, charge_energy));
  return { carga_solar, exceso };
}

// ============================================================================
// rev4 per-period PV credit — dispatch_cs.py sim_month self_per/exc_per port
// (gap 5, flag-gated)
// ============================================================================
// Hourly overlap of the scaled load curve vs the scaled solar bell, labeled by
// the CFE tariff window (B/I/P) of each hour. Mirrors dispatch_cs.sim_month's
// per-period accumulation exactly:
//   self_per[p] = Σ min(load_h, pv_h)   over all days whose window labels hour h as p
//   exc_per[p]  = Σ max(0, pv_h-load_h) idem
// self_per.B+I+P is the hourly-derived self-consumption (== autoconsumo_pct's
// selfc); exc_per.B+I+P is the same `exceso` solar_charge_split computes.
export function pv_period_split(curvaKey, division, year, month, kwh_total, gen_month) {
  const curve = CURVES[curvaKey] || CURVES["Otro"];
  const dKey = (division || "SIN").toUpperCase();
  const win = WINDOWS[(dKey === "BC" || dKey === "BCS" ? dKey : "SIN") + "|" + season(division, month)];
  const cnt = day_counts(year, month);
  const days = cnt.MF + cnt.SA + cnt.DO;
  let load_units = 0.0;
  for (const dt of ["MF", "SA", "DO"]) for (let h = 0; h < 24; h++) load_units += curve[dt][h] * cnt[dt];
  const ls = load_units ? kwh_total / load_units : 0.0;
  const gs = days ? gen_month / (days * _PV_SUM) : 0.0;
  const self_per = { B: 0.0, I: 0.0, P: 0.0 }, exc_per = { B: 0.0, I: 0.0, P: 0.0 };
  for (const dt of ["MF", "SA", "DO"]) {
    for (let h = 0; h < 24; h++) {
      const load = curve[dt][h] * ls, pv = PV_BELL[h] * gs;
      const p = win[dt][h];
      self_per[p] += Math.min(load, pv) * cnt[dt];
      exc_per[p] += Math.max(0.0, pv - load) * cnt[dt];
    }
  }
  return { self_per, exc_per };
}

export function merge_inputs(over) {
  over = over || {};
  const p = { ...DEFAULT_INPUTS };
  for (const [k, v] of Object.entries(over)) if (v !== null && v !== undefined) p[k] = v;
  p.pct_mode = (over.pct_autoconsumo !== null && over.pct_autoconsumo !== undefined) ? "manual" : "curva";
  if (!(p.curva in CURVES)) p.curva = (p.giro in CURVES) ? p.giro : "Otro";
  if (p.pct_autoconsumo === null || p.pct_autoconsumo === undefined)
    p.pct_autoconsumo = GIRO_PCT_AC[p.giro] ?? 0.75;
  const ym = {};
  for (const [k, v] of Object.entries(p.yield_monthly || {})) ym[parseInt(k, 10)] = parseFloat(v);
  p.yield_monthly = ym;
  if (p.om_pv === null || p.om_pv === undefined) p.om_pv = p.kwp * 310.0;
  if (p.om_bess === null || p.om_bess === undefined) p.om_bess = p.bess_kwh * 180.0;
  p.capex_pv = p.kwp * 1000 * p.epc_usd_wp * p.fx;
  p.capex_bess = p.bess_kwh * p.epc_bess * p.fx;
  p.deliv = p.bess_kwh * p.dod * Math.sqrt(p.rte);
  p.falla = (12 - p.falla_meses) / 12;
  return p;
}

export function validate_bill(b) {
  const keys = ["suministro", "distribucion", "transmision", "cenace", "gen_base",
    "gen_inter", "gen_punta", "capacidad", "scnmem"];
  const mem = keys.reduce((a, k) => a + (b[k] || 0.0), 0.0);
  const bonif = b.bonif_fp || 0.0;
  const calc = (mem + bonif) * 1.16;
  const rec = b.facturacion_recibo;
  const diff = rec ? (calc / rec - 1) : null;
  return { mem, bonif, calc_total: calc, recibo: rec, diff, ok: (diff !== null && Math.abs(diff) < 0.005) };
}

export function compute(inputs, bills) {
  const p = merge_inputs(inputs);
  const autoc = p.kwp >= 700.0;
  const rows = [], val_rows = [];
  for (const b of bills) {
    const y = b.year, m = b.month;
    const v = validate_bill(b);
    val_rows.push({ year: y, month: m, ...v });
    const days = b.days || 30;
    const kb = b.kwh_base || 0.0, ki = b.kwh_inter || 0.0, kp = b.kwh_punta || 0.0;
    const kwh_tot = kb + ki + kp;
    const kwp_ = b.kw_punta || 0.0;
    const mem = v.mem, bonif = v.bonif;
    const umbral = days ? kwh_tot / (days * 24 * p.fc) : 0.0;
    const basis_cap = kwp_ === 0 ? umbral : Math.min(kwp_, umbral);
    const r_cap = basis_cap ? (b.capacidad || 0.0) / basis_cap : 0.0;
    const flat = kwh_tot ? ((b.transmision || 0.0) + (b.cenace || 0.0) + (b.scnmem || 0.0)) / kwh_tot : 0.0;
    const bnd_i = ki ? ((b.gen_inter || 0.0) / ki + flat) : 0.0;
    const bnd_b = kb ? ((b.gen_base || 0.0) / kb + flat) : bnd_i;
    const bnd_p = kp ? ((b.gen_punta || 0.0) / kp + flat) : 0.0;
    const ph = punta_hours(p.division, m);
    const wd = punta_weekdays(y, m);
    const gen = p.kwp * (p.yield_monthly[m] || 0.0);
    let pct_m;
    if (!autoc) pct_m = 1.0;
    else if (p.pct_mode === "manual") pct_m = p.pct_autoconsumo;
    else pct_m = autoconsumo_pct(p.curva, y, m, kwh_tot, gen);
    const usable = gen * pct_m;
    // rev4 per-period PV credit (gap 5, flag-gated; OFF => bit-for-bit legacy
    // path): hourly self-consumption split B/I/P credited at each period's
    // bundled rate, replacing monthly netting aprov=min(usable,ki) @ bnd_i.
    // The hourly frame supersedes pct_autoconsumo (manual or curva): the
    // credited fraction IS self_tot/gen, dispatch_cs self-basis.
    let aprov = Math.min(usable, ki), aprov_per = null;
    if (p.pv_credit_periods) {
      aprov_per = pv_period_split(p.curva, p.division, y, m, kwh_tot, gen).self_per;
      aprov = aprov_per.B + aprov_per.I + aprov_per.P;
    }
    const exced = gen - aprov;
    const ah_pv = aprov_per
      ? aprov_per.B * bnd_b + aprov_per.I * bnd_i + aprov_per.P * bnd_p + exced * p.texc
      : aprov * bnd_i + exced * p.texc;
    const umb_post = days ? (kwh_tot - aprov) / (days * 24 * p.fc) : 0.0;
    const f_pre = basis_cap;
    const f_prebess = kwp_ === 0 ? umb_post : Math.min(kwp_, umb_post);
    const dem_pv = (f_pre - f_prebess) * r_cap;
    const share = mem ? -bonif / mem : 0.0;
    const claw = (s) => bonif < 0 ? -s * share : 0.0;
    const pv_only = ah_pv + dem_pv + claw(ah_pv + dem_pv);
    const shave = ph ? Math.min(p.bess_kw, p.deliv / ph) : 0.0;
    const resid = Math.max(0.0, kwp_ - shave);
    const f_post_h = Math.min(resid, umb_post);
    const dem_bess_h = (f_prebess - f_post_h) * r_cap;
    const desc = ph ? Math.min(p.deliv * wd, kp) : 0.0;
    const carga = p.rte ? desc / p.rte : 0.0;
    const arb_grid = desc * bnd_p - carga * bnd_b; // rev3: BESS charges 100% from grid base
    // rev4 solar-charge dispatch (flag-gated; OFF => bit-for-bit legacy path)
    let arb = arb_grid, ah_pv_h = ah_pv, carga_solar = 0.0, carga_base = carga, exced_export = exced;
    if (p.solar_charge) {
      const c_oport = p.texc; // opportunity cost of BESS-absorbed excess ≈ excess tariff (~0)
      ({ carga_solar } = solar_charge_split(p.curva, y, m, kwh_tot, gen, p.bess_kw, carga, wd, exced));
      carga_base = carga - carga_solar;
      exced_export = exced - carga_solar; // BESS-absorbed excess is NOT exported
      // three buckets, no double count: aprov@bnd_i + carga_solar@c_oport + exced_export@texc
      ah_pv_h = aprov_per
        ? aprov_per.B * bnd_b + aprov_per.I * bnd_i + aprov_per.P * bnd_p + exced_export * p.texc
        : aprov * bnd_i + exced_export * p.texc;
      arb = desc * bnd_p - (carga_base * bnd_b + carga_solar * c_oport);
    }
    const s_hib = ah_pv_h + dem_pv + dem_bess_h + arb;
    const hib = s_hib + claw(s_hib);
    const f_post_b = Math.min(resid, umbral);
    const dem_bess_o = (f_pre - f_post_b) * r_cap;
    const s_bo = dem_bess_o + arb_grid; // BESS-only has no PV to solar-charge from
    const bess_only = s_bo + claw(s_bo);
    const antes = mem + bonif;
    rows.push({
      year: y, month: m, days, kwh_total: kwh_tot, kwh_punta: kp,
      gen, gen_aprov: aprov, exced, desc,
      ah_pv: ah_pv_h, dem_pv, dem_bess_h, arb,
      pv_only, bess_only, hibrido: hib, pct_ac: aprov_per ? (gen ? aprov / gen : 1.0) : pct_m,
      antes, despues_hib: antes - hib,
      pct_hib: antes ? hib / antes : 0.0,
      fp_cargo: b.cargo_fp_penalty || 0.0,
      ...(p.solar_charge ? { carga_solar, carga_base, exced_export, arb_grid } : {}),
      ...(p.pv_credit_periods ? { aprov_base: aprov_per.B, aprov_inter: aprov_per.I, aprov_punta: aprov_per.P } : {}),
    });
  }
  const n_meses = rows.length;
  const ann = (n_meses > 0 && n_meses < 12) ? 12.0 / n_meses : 1.0;
  const T = (k) => rows.reduce((a, r) => a + r[k], 0.0) * ann;
  const annual = {
    antes: T("antes"), gen: T("gen"), exced: T("exced"),
    pv_only: T("pv_only"), bess_only: T("bess_only"), hibrido: T("hibrido"),
    ah_pv: T("ah_pv"), dem_pv: T("dem_pv"), dem_bess_h: T("dem_bess_h"),
    arb: T("arb"), fp_cargo: T("fp_cargo"),
  };
  if (p.solar_charge) {
    // BESS-absorbed excess is excluded from the exported-excess figure (and
    // therefore from the 5% excedente reject rule downstream).
    annual.carga_solar = T("carga_solar");
    annual.carga_base = T("carga_base");
    annual.exced_export = T("exced_export");
    annual.arb_grid = T("arb_grid");
    annual.solar_charge_bonus = annual.arb - annual.arb_grid; // = Σ carga_solar·(bnd_b − texc) ≥ 0
  }
  if (p.pv_credit_periods) {
    annual.aprov_base = T("aprov_base");
    annual.aprov_inter = T("aprov_inter");
    annual.aprov_punta = T("aprov_punta");
  }
  annual.meses = n_meses;
  annual.factor_anual = ann;
  annual.anualizado = ann !== 1.0;
  annual.fp_lever = p.fp_correction ? annual.fp_cargo : 0.0;
  const genSum = rows.reduce((a, r) => a + r.gen, 0.0);
  annual.pct_ac_avg = genSum ? rows.reduce((a, r) => a + r.pct_ac * r.gen, 0.0) / genSum : 1.0;
  const bess_part_h = annual.dem_bess_h + annual.arb;
  annual.neto_disp = {
    pv: annual.pv_only,
    bess: annual.bess_only - annual.bess_only * (1 - p.falla),
    hibrido: annual.hibrido - bess_part_h * (1 - p.falla),
  };
  const regimen = _regimen(p, bills, rows, annual);
  const finance = {};
  for (const esc of ["PV", "BESS", "Hibrido"]) finance[esc] = _finance(p, annual, esc);
  return { inputs: p, monthly: rows, validacion: val_rows, annual, regimen, finance };
}

function _regimen(p, bills, rows, annual) {
  const autoc = p.kwp >= 700.0;
  let reg;
  if (!autoc) reg = "GENERADOR EXENTO — Medición Neta (sin permiso; Art. 30 LSE; RES/142/2017)";
  else if (p.kwp <= 20000) reg = "AUTOCONSUMO interconectado 0.7–20 MW — permiso SIMPLIFICADO CNE (Núm. 2.2 DACG)";
  else reg = "AUTOCONSUMO >20 MW — permiso ORDINARIO CNE (Núm. 2.3 DACG)";
  const alerts = [];
  if (bills.some((b) => !validate_bill(b).ok))
    alerts.push(["error", "Hay recibos que no cuadran (>0.5%) — corregir transcripción/parseo antes de usar resultados"]);
  const kwmax = bills.reduce((mx, b) => Math.max(mx, b.kw_base || 0, b.kw_inter || 0, b.kw_punta || 0), 0);
  if (kwmax < 110)
    alerts.push(["warn", `Demanda máx ${kwmax.toFixed(0)} kW — cerca del gate de 100 kW; revisar si la tarifa correcta es GDMTO`]);
  if (p.bess_kw > (p.demanda_contratada || Infinity))
    alerts.push(["error", `BESS ${p.bess_kw.toFixed(0)} kW > demanda contratada ${p.demanda_contratada.toFixed(0)} kW — viola condición SAE-CC`]);
  const exced_eff = p.solar_charge ? annual.exced_export : annual.exced; // BESS-absorbed excess doesn't count
  if (exced_eff > 1.0)
    alerts.push(["warn", `${Math.round(exced_eff).toLocaleString()} kWh/año de excedentes valuados a $${p.texc.toFixed(2)} — bajo medición neta los créditos expiran a PML en 12 meses; ajustar kWp al consumo`]);
  if (annual.fp_cargo > 0)
    alerts.push(["opp", `Cargos FP por $${Math.round(annual.fp_cargo).toLocaleString()}/año — la corrección FP suele ser el ROI más alto y es ortogonal a PV/BESS`]);
  if (p.division !== "SIN")
    alerts.push(["warn", `División ${p.division}: modelo calibrado SIN; PV genera parcialmente en punta (no acreditado = conservador); tarifas no-SIN = gap abierto del wiki`]);
  if (autoc) {
    const src = p.pct_mode === "manual" ? "manual" : `derivado de curva '${p.curva}' × campana solar`;
    alerts.push(["info", `Autoconsumo activo: ${(annual.pct_ac_avg * 100).toFixed(0)}% del PV acreditado (${src}); excedentes solo a CFE a $${p.texc.toFixed(2)}/kWh; permiso CNE + registro anual 1T + uso mínimo 30%`]);
    if (p.pct_mode === "curva") {
      const fit = fit_bills(bills, p.division);
      const row = fit.ranking.find((r) => r.giro === p.curva);
      if (row && row.mae !== null && row.mae > 0.08)
        alerts.push(["warn", `La curva '${p.curva}' NO ajusta bien a los recibos (MAE ${(row.mae * 100).toFixed(1)}%) — el % autoconsumo derivado es poco confiable; mejor ajuste: '${fit.best}'. Considerar override manual o datos 15-min`]);
    }
    if (p.bess_kwh > 0)
      alerts.push(["info", "Respaldo de intermitencia OBLIGATORIO — cubierto por el BESS del proyecto (Núm. 4.5 DACG)"]);
    else
      alerts.push(["error", "PV ≥0.7 MW intermitente REQUIERE SAE o respaldo CFE contratado — el proyecto no trae BESS"]);
  }
  if (bills.length < 12)
    alerts.push(["warn", `Solo ${bills.length} meses de recibos — riesgo de estacionalidad; ideal 12`]);
  return { autoconsumo: autoc, regimen: reg, alerts };
}

function _finance(p, annual, esc) {
  const has_pv = (esc === "PV" || esc === "Hibrido") && p.kwp > 0;
  const has_bess = (esc === "BESS" || esc === "Hibrido") && p.bess_kwh > 0;
  const base_pv = has_pv ? (annual.ah_pv + annual.dem_pv) : 0.0;
  let base_bess, bruto0;
  if (esc === "Hibrido") { base_bess = annual.dem_bess_h + annual.arb; bruto0 = annual.hibrido; }
  else if (esc === "BESS") { base_bess = annual.bess_only; bruto0 = annual.bess_only; }
  else { base_bess = 0.0; bruto0 = annual.pv_only; }
  const base_claw = esc !== "BESS" ? (bruto0 - base_pv - base_bess) : 0.0;
  const capex = (has_pv ? p.capex_pv : 0.0) + (has_bess ? p.capex_bess : 0.0);
  const gen = has_pv ? annual.gen : 0.0;
  const fl_new = [-capex], fl_proj = [-capex];
  for (let yy = 1; yy <= p.horizon; yy++) {
    const e = Math.pow(1 + p.esc_cfe, yy);
    const dpv = Math.pow(1 - p.pv_degr, yy);
    const dbe = Math.pow(1 - p.bess_degr, yy);
    const sav_pv = base_pv * e * dpv;
    const sav_bess = base_bess * e * dbe * p.falla;
    const clw = base_claw * e * (dpv + dbe) / 2;
    const bruto = sav_pv + sav_bess + clw;
    const ppa_pay = (has_pv && yy <= p.ppa_yrs) ? gen * dpv * p.ppa * Math.pow(1 + p.esc_ppa, yy - 1) : 0.0;
    const com = (has_bess && yy <= p.bess_yrs) ? sav_bess * p.comision : 0.0;
    const ompv = (has_pv && yy <= p.ppa_yrs) ? p.om_pv * Math.pow(1 + p.esc_cfe, yy - 1) : 0.0;
    const ombe = (has_bess && yy <= p.bess_yrs) ? p.om_bess * Math.pow(1 + p.esc_cfe, yy - 1) : 0.0;
    const fz = ppa_pay * p.fianza;
    fl_new.push(ppa_pay + com - ompv - ombe - fz);
    fl_proj.push(bruto - ompv - ombe);
  }
  const irr = (flows, lo = -0.95, hi = 4.0) => {
    const f = (r) => flows.reduce((a, x, i) => a + x / Math.pow(1 + r, i), 0.0);
    if (!flows.length || f(lo) * f(hi) > 0) return null;
    for (let i = 0; i < 200; i++) {
      const mid = (lo + hi) / 2;
      if (f(lo) * f(mid) <= 0) hi = mid; else lo = mid;
    }
    return (lo + hi) / 2;
  };
  const npv = (fl) => fl.reduce((a, x, i) => a + x / Math.pow(1 + p.wacc, i), 0.0);
  const pay = (fl) => { let c = 0.0; for (let i = 0; i < fl.length; i++) { c += fl[i]; if (c >= 0) return i; } return null; };
  return {
    capex, bruto_anio0: bruto0,
    tir_proyecto: irr(fl_proj), tir_financiador: irr(fl_new),
    vpn_proyecto: npv(fl_proj), vpn_financiador: npv(fl_new),
    payback_proyecto: pay(fl_proj), payback_financiador: pay(fl_new),
  };
}

// ============================================================================
// BESS verano-2h sizing rule (rev3) — sizing.py propose_bess + gepp_bess_scenarios.tam_B
// ============================================================================
// E_util = hours * avg(kw_punta over summer months); nominal = E_util/(DoD*sqrt(RTE)),
// rounded to nearest 100 kWh; power = nominal/2 (0.5C).  Default summer = May..Sep.
export function size_bess_verano(bills, opts = {}) {
  const hours = opts.hours ?? 2.0;
  const dod = opts.dod ?? 0.96, rte = opts.rte ?? 0.96;
  const util = dod * Math.sqrt(rte);
  const lo = opts.summer_lo ?? 5, hi = opts.summer_hi ?? 9;
  let summer = bills.filter((b) => b.month >= lo && b.month <= hi);
  if (!summer.length) summer = bills;
  const avg_punta = summer.reduce((a, b) => a + (b.kw_punta || 0), 0) / summer.length;
  const e_util = hours * avg_punta;
  const nominal = Math.round(e_util / util / 100) * 100;
  const power = Math.round(nominal / 2);
  return { bess_kw: power, bess_kwh: nominal, avg_summer_punta_kw: avg_punta,
    basis: `${hours}h × prom. demanda punta verano (m${lo}-${hi}) ${avg_punta.toFixed(0)} kW, 0.5C, DoD ${dod} √RTE` };
}

// ============================================================================
// Sizing sweep (gaps 2/4) — optimizeSizing (newman-rebuild engine/sizing.mjs)
// widened with a bess_hours axis {1,2,4} (sweep_cs.py / probe_bess_scale.py
// doctrine) + superficie sweep output (sizing_params.sweep, kwp_opt_unconstrained)
// ============================================================================
// Search loop only — every candidate is priced through compute(); the flags in
// `inputs` (solar_charge, pv_credit_periods) apply to every point. Objective =
// financier IRR ("irr", default) or financier NPV ("npv"), tie-break financier
// NPV (IRR is scale-invariant across PV-only sizes under a flat yield).
//   opts.kwp_grid          : candidate kWp values (required; max = roof cap)
//   opts.bess_hours        : sizing-basis durations, default [1,2,4] (gap 2)
//   opts.bess_grid         : explicit [{bess_kwh,bess_hours}] — skips seeding
//   opts.reject_exced_kwh  : reject candidates whose annual exported excess
//                            exceeds this (exced_export when solar_charge —
//                            BESS-absorbed excess doesn't count)
//   opts.kwp_max           : unconstrained-sweep ceiling, default 3× roof cap
//   opts.m2_per_kwp        : superficie density, default 4.0 (Supuestos!B24)
// Candidate power tracks the sizing duration: bess_kw = bess_kwh/bess_hours
// (hours=2 reproduces the engine's 0.5C convention in size_bess_verano).
export function optimize_sizing(inputs, bills, opts = {}) {
  const objective = opts.objective ?? "irr";
  const key = objective === "npv" ? "vpn_financiador" : "tir_financiador";
  const kwpGrid = opts.kwp_grid;
  if (!Array.isArray(kwpGrid) || !kwpGrid.length)
    throw new Error("optimize_sizing: opts.kwp_grid required (candidate kWp from roof cap)");
  const dod = inputs.dod ?? 0.96, rte = inputs.rte ?? 0.96;
  const hoursGrid = opts.bess_hours ?? [1, 2, 4];
  let bessGrid = opts.bess_grid;
  if (!Array.isArray(bessGrid) || !bessGrid.length) {
    // gap 2: widened grid — per-duration verano seed ± steps + coarse scale
    // points (probe_bess_scale SCALES 1.5/2/3), rounded to 100 kWh
    bessGrid = [{ bess_kwh: 0, bess_hours: 0 }];
    const seen = new Set(["0|0"]);
    for (const h of hoursGrid) {
      const seed = size_bess_verano(bills, { hours: h, dod, rte }).bess_kwh;
      const kwhs = [seed - 400, seed - 200, seed, seed + 200, seed + 400,
        Math.round(seed * 1.5 / 100) * 100, seed * 2, seed * 3];
      for (const kwh of kwhs) {
        if (kwh <= 0 || seen.has(kwh + "|" + h)) continue;
        seen.add(kwh + "|" + h);
        bessGrid.push({ bess_kwh: kwh, bess_hours: h });
      }
    }
  }
  const score = (kwp, g) => {
    const bess_kw = g.bess_kwh > 0 ? Math.round(g.bess_kwh / (g.bess_hours || 2)) : 0;
    const res = compute({ ...inputs, kwp, bess_kw, bess_kwh: g.bess_kwh }, bills);
    const fin = res.finance.Hibrido;
    return {
      kwp, bess_kw, bess_kwh: g.bess_kwh, bess_hours: g.bess_hours,
      tir_financiador: fin.tir_financiador, vpn_financiador: fin.vpn_financiador,
      vpn_proyecto: fin.vpn_proyecto, capex: fin.capex,
      hibrido: res.annual.hibrido,
      exced: inputs.solar_charge ? res.annual.exced_export : res.annual.exced,
    };
  };
  const admit = (s) => {
    if (opts.reject_exced_kwh != null && s.exced > opts.reject_exced_kwh) return false;
    if (s[key] == null) return false; // no IRR => non-financeable
    return true;
  };
  const byObjective = (a, b) => (b[key] - a[key]) || (b.vpn_financiador - a.vpn_financiador);
  const sweep = [];
  for (const kwp of kwpGrid) for (const g of bessGrid) {
    const s = score(kwp, g);
    if (admit(s)) sweep.push(s);
  }
  if (!sweep.length)
    throw new Error("optimize_sizing: no financeable candidate survived the grid/filters");
  sweep.sort(byObjective);
  const best = sweep[0];
  // gap 4: when the roof cap binds, keep sweeping past it on the same grid
  // step to find kwp_opt_unconstrained ("faltan N m2" for sales)
  const cap = Math.max(...kwpGrid);
  const m2_per_kwp = opts.m2_per_kwp ?? 4.0;
  let kwp_opt_unconstrained = best.kwp, unconstrained = null;
  if (best.kwp === cap) {
    const sorted = [...kwpGrid].sort((a, b) => a - b);
    const step = sorted.length > 1 ? sorted[sorted.length - 1] - sorted[sorted.length - 2]
      : Math.max(100.0, Math.round(cap * 0.2 / 100) * 100);
    const kwp_max = opts.kwp_max ?? cap * 3;
    let cand = best;
    for (let kwp = cap + step; kwp <= kwp_max + 1e-9; kwp += step) {
      const pts = bessGrid.map((g) => score(kwp, g)).filter(admit);
      if (!pts.length) break; // exced reject killed the whole column — stop
      pts.sort(byObjective);
      if (byObjective(pts[0], cand) < 0) { cand = pts[0]; unconstrained = pts[0]; }
    }
    kwp_opt_unconstrained = cand.kwp;
  }
  const m2_faltantes = Math.max(0.0, (kwp_opt_unconstrained - cap) * m2_per_kwp);
  return {
    best, ranking: sweep, objective, key,
    sizing_params: {
      sweep, kwp_grid: kwpGrid, bess_grid: bessGrid,
      kwp_cap: cap, kwp_opt_unconstrained, unconstrained_point: unconstrained,
      m2_per_kwp, m2_faltantes, bess_hours: hoursGrid,
    },
  };
}
