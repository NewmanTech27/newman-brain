# GEPP Solución Energética Deck (v4–v7) + /solucion-deck Skill

**Summary**: Iterated the GEPP PV+BESS client deck through many versions (4% escalators, TIR-14 investor economics, copy/visual polish, investor-facing variant) and froze the workflow into the reusable `/solucion-deck` skill.
**Tags**: #newman #gepp #deck #solucion-deck #skill #ppa #bess #investor
**Created**: 2026-07-13
**Source**: newman-vps sessions 1c58c9c9, cf517344, c28688af, 1a93f954, 451b4d4f, user mario

---

## Content
- Client **GEPP** (4 sites, one = Proplasa with 3 sub-sites), Drive folder `1INDng8_TDPSgC0m69PnjkDHZ5f3BzCOQ`. Deck built in AFC/kfc-report style; the 3-in-1 site expands to show sub-projects.
- Set **PPA and CFE escalators to 4%** (later runs re-solved to keep **combined investor TIR at exactly 14.0%**); PV degradation 1.0%/0.4%.
- Deck evolved v1→v7. Each version PATCHes the **same Drive file id** in place; earlier versions kept as separate files. Verified via headless-Chrome screenshots + a DOM-stub render gate (renders with zero NaN/undefined leaks).
- **Design/copy doctrine captured** (now standard skill copy, not per-client): positive framing (no negative words — "diseñamos sobre su diseño", "reserva operativa"); impersonal third person ("se analizó"); "sistema fotovoltaico" not "sistema solar"; **Inversión Estimada Newman** (CAPEX) shown prominently; contact = sales@newman.re (Jesús López name removed); mountain graphic blends across the portada→page-2 boundary.
- **Despacho de un día típico** chart fully redesigned: monochrome **violet** PV area (never amber/yellow — "tacky"), monotone interpolation, labeled BESS lane (CARGA BASE / DESCARGA capsules), sun animation removed after design-agent review.
- New institutional **"Quiénes somos" manifiesto** (Newman Power Alliance copy) + closing line changed to "What we do today becomes tomorrow's past, let's light it up."
- **Investor-facing deck** built for banks/financial sponsors: IRR, VPN (cashflow only), CAPEX, tariff, term, client DD, with editable fields to vary project conditions.
- **v6/v7** (session 451b4d4f): re-ran all applicable Excels to combined investor IRR 14% (4% escalators), updated investors deck; v7 added a "Cobertura solar y ruta de crecimiento" print page — gen-vs-consumo per site (Op1 Ixtlahuacán 36.6%, Acapulco 34.0%, Cancún 34.7%, Proplasa 6.9%, portfolio 15.0%; 95–98% self-consumed), engine-backed **+0.92 MW** available today (+$1.69M/yr for ~$10.5M, 14.9% incremental IRR), and a solar-charged BESS rung labeled preliminary.
- **/solucion-deck skill** committed to `NewmanTech27/newman-brain` at `skills/solucion-deck/` (SKILL.md + `template_gepp_v2.html` + extractor), commit `9f15996`/`53535a6`. Invoked skill is the local `~/.claude/skills/solucion-deck/`; repo copy is versioned mirror — keep in sync.
- Handoff mechanics learned: working files live in session scratchpad (wiped on end) — permanent copies moved to `~/CFE Brain/work/gepp-deck/` (`gepp_v4.html`, build scripts, 4% model JSON, quality-gate test, README). Auto-memory + `HANDOFF.md` + `claude --continue`/`--resume` are the three resume paths.
- Gotchas noted: two Google accounts, a 6-decimal rounding bug, Proplasa $202M vs $198M discrepancy, a NaN `pct` fix.

## Related Notes
- [[2026-07-14-gepp-solar-charge-bess-dispatch]]
- [[2026-07-12-afc-kfc-pizzahut-proposal]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[newman-brain-repo]]
