# AFC (KFC–Pizza Hut) Solución Energética — Excel + HTML Deck

**Summary**: Turned the Alimentos y Franquicias de Chiapas CFE bills into an editable live-motor Excel book and a Newman-branded client-facing HTML deck; this became the reference workflow for all later single/multi-bill proposals.
**Tags**: #newman #afc #kfc #cfe-brain #proposal #excel #deck #bess
**Created**: 2026-07-12
**Source**: newman-vps sessions 5af5f1a0, 733c6e97, c9ae432c, 2d151ec9, d023e58b, 9618c48d, user mario

---

## Content
- Client: **AFC (KFC–Pizza Hut)**, 4 sites, Drive folder `1DYE6ULADTzZNbp-LXejc_AzAKSR8mSYJ`. One bill per RPU, mixed GDMTO/GDMTH.
- Built the **v2 editable live-motor Excel book** `AFC (KFC-Pizza Hut) - Solucion Energetica v2.xlsx` (Drive id `1siKkk5cTD3sE3hkPvd6JBBLbx-4PZsyD`). §3 monthly motor as live Excel formulas (not pasted values): GDMTO PV credit + umbral pre/post-PV + capacidad at umbral; GDMTH per-band tariffs, BESS shave `MIN(P, E útil/hrs punta)`, base↔punta arbitrage, FP claw-back.
- Standardized four permanent defaults into `make_project_book.py`: (1) **Ahorro % después del PPA** column (client cashflow ÷ current CFE spend); (2) **PV degradation split** año 1 = 1.0%, año 2+ = 0.4%, editable; (3) 11 live charts per book; (4) HelioScope satellite roof crop embedded in each site sheet.
- **Investor IRR default set to 19%**; **BESS gate**: auto-drop battery when it doesn't make financial sense (KFC Tuxtla Centro GDMTH case — no battery was better; gate verified to fire).
- HTML deck `AFC (KFC-Pizza Hut) - Solucion Energetica.html` (self-contained, Newman Power Alliance design system: `--accent:#621558` magenta, `--canvas:#F6F4F9`, scroll-deck). Reference style = `newmantech27.github.io/kfc-report/`. 10 sections incl. `techos` (satellite roofs) + `comparativo` (comprar vs cero-inversión).
- PV-only final (user: "Tuxtla better off with no storage"). Portfolio: $2,355,276 gasto / **$617,636 ahorro/yr (26.22%)**, CAPEX $2,058,727; TIR proy per site 32–34%. (Earlier hybrid version showed $739,707/31.4%.)
- **Drive gotcha resolved**: HTML updated in-place by file id (`1n3uhAD9…`), md5-verified, no duplicate; satellite images swapped for the PNGs embedded inside the v2 xlsx.
- Engine golden test **18/18**, book reconciliation **5/5**. Two Google accounts in play: gcloud mario@newman.re (needs interactive re-auth on expiry) vs MCP Drive newman.jjzo (can't reach the client folder).

## Related Notes
- [[2026-07-13-gepp-solucion-deck]]
- [[2026-07-12-fibrahotel-proposals]]
- [[cfe-brain-vault]]
- [[2026-07-09-helioscope-roof-sizing-pipeline]]
