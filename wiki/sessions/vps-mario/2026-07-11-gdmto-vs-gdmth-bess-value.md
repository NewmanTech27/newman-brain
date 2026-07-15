# BESS Value: GDMTO vs GDMTH (No-Punta Analysis)

**Summary**: Modeled whether a BESS helps a GDMTO site (no periodo punta) vs GDMTH, concluding a battery is barely worth it under GDMTO and quantifying why for the shared-savings investment decision.
**Tags**: #newman #cfe-brain #bess #gdmto #gdmth #tariff #analysis
**Created**: 2026-07-11
**Source**: newman-vps session ec8a9bd4, user mario

---

## Content
- Question: how does a BESS help a GDMTO site with no periodo punta, and is a shared-savings investment worth it for GDMTO vs GDMTH?
- **Answer: barely at all for GDMTO.** GDMTO switches off both BESS value levers:
  1. **No energy arbitrage** — GDMTO bills energy at one flat 24/7 rate; charge-at-night/discharge-evening just moves money minus round-trip losses (energy term slightly negative).
  2. **Capacidad can't be shaved** — no Dmax_punta; CFE bills capacidad at the umbral `Q/(d × 0.55 × 24)`, a pure function of kWh. Grid-charging *increases* Q (losses) → nudges it up.
  3. Only lever left = **distribución** (`min(Dmax_mensual, umbral)`, ~$95/kW-mes, ~4:1 smaller than capacidad); pays only if load factor > 0.55 so Dmax (not umbral) binds.
- Note the **load factor difference**: GDMTO umbral uses **FC = 0.55** here (vs 0.57 for the GDMTH capacidad basis in the engine).
- No real GDMTO bill in `raw/bills/` yet — built a synthetic GDMTO twin (95 kW site just under the 100 kW gate, 25 kW/60 kWh BESS, engine DoD/RTE/availability conventions) and ran GDMTH sites (Posadas Cancún, Tototlán) through the golden `tools/cfe_savings` engine.
- Model filed into the CFE Brain (indexed + logged) in the standard analysis-page format.

## Related Notes
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[cfe-brain-vault]]
- [[2026-07-12-afc-kfc-pizzahut-proposal]]
