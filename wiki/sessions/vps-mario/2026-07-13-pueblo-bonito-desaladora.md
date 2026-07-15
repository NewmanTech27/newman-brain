# Pueblo Bonito / El Chileno Desaladora — 6-Year PPA Proposal

**Summary**: Built a Los Cabos (BCS) desalination-plant PPA proposal — deck, editable book, and a 6-year/18%-IRR financing model — and surfaced a structural CFE Brain limitation: the motor is SIN-calibrated and understates BCS savings.
**Tags**: #newman #pueblo-bonito #el-chileno #desaladora #bcs #ppa #los-cabos #cfe-brain
**Created**: 2026-07-13
**Source**: newman-vps sessions 3e1bf33b, b5f41dec, fd118e52, eff58bcc, 58e195ef, a316b0cf, 4e43baf7, 21173790, 05263ec3, user mario

---

## Content
- Client: **Pueblo Bonito** desaladora at Playa **El Chileno**, Los Cabos. Consumes ~30 MWh/day, ~$50 MDP/yr (client-stated) vs $38.9M modeled. Members exit operation in ≤6 years → offer a **6-year PPA** then cede the asset to members (owners won't invest).
- Deck built in GEPP v5 `/solucion-deck` style with selectable variants (carport / no-carport, medición neta / autoconsumo), HelioScope images. Delivered `Pueblo Bonito - Desaladora - Solucion Energetica.html` + sister resort deck `Pueblo Bonito Solucion Energetica V2`. Drive folder `1jCDYQsenNHa5AwwjaNdkKl7JU0wv2-8w`.
- Editable book `Pueblo Bonito - Solucion Energetica.xlsx` (`1LrAAHEUkntzjbEmfqSrizwf-I6MOsKWn`), 14 sheets incl. a **Propuestas** sheet mapping sites/sizings to each variant (1/3.9/4.4 MW; Montecristo II 564 vs 839 kWp), default 4.4 MW, PPA 2.19 MXN/kWh × 15 años, EPC 1.2 USD/Wp @ FX 17.2. Pipeline 5/5 book, 18/18 golden.
- Orchestration: Fable orchestrator, Opus/Sonnet sub-agents for book surgery and deck build.
- **6-year financing model** (fd118e52, eff58bcc): tariff solved so sponsor NPV at 18% = zero over 6 years. **Tarifa = (CAPEX + VP O&M años 1–6) ÷ VP kWh entregados 1–6**, discounted 18%. Includes full CAPEX (EPC 1.00 USD/Wp × FX 17.2 = $41.3M for scenario B), sponsor-paid O&M (310 MXN/kWp-año +5%/yr), 1%/0.4% degradation, revenue only on self-consumed kWh, **zero terminal value** (client takes O&M from year 7). Escenario B tarifa ≈ **$2.81/kWh**.
- User pushback on price being low → correct: 18% is **pre-tax**. With 30% ISR: at $2.81 post-tax IRR = 14.1% (w/ accelerated depreciation) or 8.2% (straight-line); tarifa for 18% post-tax = $3.14 / $3.74. CFE blended ≈ $3.07/kWh. Headroom: sponsor pre-tax TIR 18.0% @ $2.81 → 23.4% @ $3.20.
- **Open commercial decision**: EPC price chip — at 6-yr term only **0.65 USD/Wp is viable** (PPA $1.04/kWh, 66% descuento); at 1.00 USD/Wp the year-1 saving is already negative. Team must set this before the client sees a number.
- **Critical CFE Brain gotcha (must fix in committed code, dev branch only)**: motor is SIN-calibrated — credits PV only against *intermedio* kWh. Pueblo Bonito is **BCS** where winter has no punta and daytime load bills as *Base*, so the motor drops real savings up to **−53%** and flips small sites falsely negative. Also GDMTH capacidad formula DIV/0s when kw_punta=0 in BCS winter. Both patched **only in this client's output workbook**, NOT in `calc_core`/live motor — any future Los Cabos/La Paz run silently repeats the error. Fix = BCS period-calendar awareness in PV-credit basis (credit vs daytime Base+Int) + `basis_cap=umbral` fallback.
- The 1,470 kW portfolio figure was a false "templated" line — corrected. Reasoning trail saved to `~/CFE Brain/work/pueblo-bonito-desaladora/RAZONAMIENTO.md`; model at `model_v2.py`.
- Audit workflow (4e43baf7/21173790, dup "continue" runs) found: Escenario C inflated ~15× ($2.63B hardcoded prior-book constant); stale V1 numbers in deck static markup ($30.2M buyout, $1.04/kWh, 15-yr — JS overwrites on load but view-source/no-JS shows them); "Cesión o compra" tile leftover (V2 is cesión sin costo); doc text "15 años/14% TIR" where model solves 6 años/18%. Core math confirmed sound (both scenarios exactly 18.00% IRR, baseline $33.58M pre-IVA, blended $3.07/kWh).

## Related Notes
- [[2026-07-13-gepp-solucion-deck]]
- [[2026-07-12-fibrahotel-proposals]]
- [[cfe-brain-vault]]
- [[kamu-iwg-offices-project]]
