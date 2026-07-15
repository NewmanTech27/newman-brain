# #37: Interactive web offer + live calculator powered by the design-engine (salesman-adjustable)

- State: OPEN
- Created: 2026-07-10T16:42:33Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/37

## Body

## Feature: interactive web offer + live calculator powered by the design-engine (salesman-adjustable)

### Context
We built a static, Newman v3–branded **PDF offer** (ES) for Alimentos y Franquicias de Chiapas — 4-site portfolio PPA, driven by real numbers from the **design-engine / dimension agent** (harvested recibos → `build_load` / `derive_tariff` / `roof_cap` / `sizing.optimize`) and a PPA finance layer. Sections: resumen, análisis de consumo histórico (30 meses reales), costo real $/kWh, alcance por sitio, cómo funciona el PPA, BOM, retorno a 20 años, metodología, próximos pasos, + anexo por sitio.

It's currently a one-off Python generator → HTML → PDF. **The next step is to make it a living web asset with a live calculator the salesman can tune.**

### What we want
1. **Static/served web offer** — the same branded template (Space Grotesk/Inter, canvas `#F6F4F9`, accent `#621558`, gradient bar, KPI cards, tables, per-site annex, the 30-month consumption chart) rendered as a **responsive web page** per client/portfolio (not just a PDF). Reuse the `proposal-builder` render tokens.
2. **Dynamic calculator** — recompute savings / PV / PPA cash-flow **live** as inputs change, calling the **dimension agent** as the compute backend (the `cfe-ppa-bess` edge function is already a numbers-only HTTP engine — use it, or the Python `sizing.optimize`). No hard-coded numbers; every figure traces to the engine + the client's bills.
3. **Salesman-adjustable variables** (live, with instant re-render of every dependent figure and chart):
   - **PPA tariff** ($/kWh), **term** (años), **escalación** PPA / CFE
   - **kWp override** per site (roof-capped ↔ consumption-optimal ↔ manual) — with the OSM-footprint caveat surfaced
   - **Export model**: medición neta (retail) ↔ net-billing (wholesale)
   - **BESS toggle** (off for GDMTO; optional peak-shaving for GDMTH)
   - **EPC $/Wp, FX, WACC, horizonte** (model assumptions, behind an "avanzado" panel)
   - **Commercial model**: PPA (cliente $0) ↔ compra directa (CAPEX/NPV/IRR) ↔ comparativa
   - **Régimen**: exento (<0.7 MW) auto-detect, with the Autoconsumo step shown when a larger kWp is dialed in
4. **Output**: shareable link + one-click **export to the branded PDF** (current pipeline) with whatever the salesman dialed in. Optional WhatsApp/email send (see the Twilio sandbox → registered-sender note below).

### Why this matters
Sales can tailor an offer in front of the client (adjust tariff/term/size), see the 20-year cash-flow and régimen implications update instantly, and export/send a branded doc — instead of re-running a generator per scenario.

### Notes / dependencies
- **Engine as API**: `newman-brain` `cfe-ppa-bess` edge fn (modes `compute` / `size-bess`) is the natural calc backend. The design-engine's GDMTO path (synthesized flat-priced split → PV-only) needs to be wired in — the golden engine currently GUARDs against period-collapsed (GDMTO) input. See newman-rebuild#19 for the GDMTO sizing approach + the harvest→dimensioning data-plumbing gaps (bill vs invoice/bulk_bill, missing service address, `get_bill_series` returning no address/demanda).
- **Roof footprint**: OSM Overpass is flaky and geocode-dependent (one Chiapas site geocoded to a 149 m² building → 19 kWp); the UI must expose "sujeto a medición en sitio" and let the salesman override the cap.
- **Send**: current WhatsApp send is via the Twilio **sandbox** (open-session only); a registered WhatsApp sender + approved media template is needed for production.
- Reference implementation (static generator, branding, PPA model, historical-analysis section) exists as a Python one-off — port its structure into the served template.

