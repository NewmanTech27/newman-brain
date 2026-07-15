# GEPP Solar-Charge BESS Dispatch Engine (rev4)

**Summary**: Built an hourly dispatch model where the BESS charges first from midday PV surplus (then grid-base) to cover punta, quantified the real solar-charge bonus, and shipped rev4 books + a v8 deck — all orchestrated in Fable with Opus/Sonnet sub-agents.
**Tags**: #newman #gepp #bess #dispatch #solar-charge #deck #orchestration #fable #opus
**Created**: 2026-07-14
**Source**: newman-vps sessions 40ff713a, 879e2404, 7b3a7791, 99d6e58a, dcbfee4a, user mario

---

## Content
- Task: integrate a **solar-charged battery** into the GEPP calculator — charge BESS from PV excess first, base second, discharge to cover punta demand. Reference = existing GEPP calculators; deliverables named `... Solucion Energetica Solar-Charge BESS ...` to the GEPP Drive folder.
- Explicit orchestration pattern requested repeatedly: **orchestrate in Fable, delegate execution to Opus/Sonnet** by whichever is most token-efficient per task.
- **Motor**: `dispatch_cs.py` (hourly solar-charge dispatch simulator) + `motor_cs.json` (7 site services, both options, typical days, per-site superficie sweeps). PPA re-solved to keep combined investor TIR at exactly 14.0% (Op1 ×1.00953, Op2 ×1.00003).
- **rev4 result**: BESS charges from midday solar surplus, tops up from grid in base hours; discharge unchanged. New Op1 sizing: Ixtlahuacán 5,170 kWp, Acapulco 1,748, Cancún 1,270; portfolio coverage 15.0%→**16.25%**. Solar-charge bonus = **+$954,437/yr portfolio** (Ixt $644k, Aca $143k, Can $167k). Reality check: only 18–31% of the charge is solar-coverable at design kWp — the earlier $3.08M/yr analytical ceiling assumed 100% solar charging.
- Book surgery done by Opus agent via zip surgery on rev3 books: new charge-source columns V/W, O rewritten as live formula `W·t_base`, reworked typical-day despacho rows, LibreOffice-recalculated values twins for deck extraction. Gates: full-book formula diff, recalc verification, combined TIR 14.00%, energy identities, ArrayFormula preservation.
- Deck agent added split BESS charge lane to the despacho chart (CARGA SOLAR midday / CARGA BASE top-up / punta DESCARGA) and per-site "¿Y con más superficie?" selector from the sweep (m²-for-max-savings + extra $ if available). Verification: node syntax, DOM-stub renders, Playwright screenshots, print-page check.
- All rev4 gates passed: rev3 replica <0.1%, 1,176 energy-identity checks, book recalc vs Python <0.5%, 90 deck renders no leaks.
- Deliverables to Drive folder `1INDng8…`: `... - 4 Sitios.xlsx` (`1bebuh6a…`), `... - Proplasa.xlsx` (`1ycaxDxs…`), deck v8 HTML (`1wk66oHR…`).
- **Gotcha**: sub-agents repeatedly hit the account session usage limit mid-run ("resets 8:50pm/1:50am UTC"); completed audits replay from cache on resume. `.claude/settings.json` pins Fable 5 per project (wins over a default model change on restart). One stale-fallback wakeup loop had to be manually ended.
- Also an "autoconsumo max / no roof restriction + solar-excess charging" scenario requested (879e2404, dcbfee4a) — see how much more can be saved if BESS charges from solar excess with no roof cap.

## Related Notes
- [[2026-07-13-gepp-solucion-deck]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[2026-07-12-fable-opus-handoff-tooling]]
