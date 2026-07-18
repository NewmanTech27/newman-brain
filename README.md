> **⚠️ FROZEN — 2026-07-19.** This repo is vendored into
> [`NewmanTech27/newman-rebuild`](https://github.com/NewmanTech27/newman-rebuild)
> (PR [#240](https://github.com/NewmanTech27/newman-rebuild/pull/240), issue #239):
> the physics engine now lives at `engine/core/` and the knowledge base at `brain/`
> (see `brain/IMPORT-MANIFEST.md` there for what moved and what was skipped).
> **Do not commit here — newman-rebuild is the single source of truth.**
> This repo remains as a read-only historical reference.

---

# newman-brain

The CFE Brain logic, as code. This repo is the home for the deterministic engines behind the
CFE Brain projects — starting with the **CFE PPA + BESS** solution engine.

## Contents

| Path | What |
|------|------|
| [`docs/CFE-PPA-BESS-LOGIC.md`](docs/CFE-PPA-BESS-LOGIC.md) | **Step‑by‑step logic** of the PPA+BESS engine — read this first. |
| `supabase/functions/cfe-ppa-bess/index.ts` | Edge Function HTTP handler (Deno) — routes the 3 modes. |
| `supabase/functions/cfe-ppa-bess/engine.js` | The deterministic engine (calc_core port). |
| `supabase/functions/cfe-ppa-bess/gepp_data.js` | GEPP 4‑sites rev3 seed dataset. |

## The engine

`cfe-ppa-bess` is a Supabase Edge Function that turns a stack of monthly CFE **GDMTH** bills into
PV / BESS / Hybrid savings, a regulatory régime, and a project financial model. It is a faithful,
numbers‑only port of the CFE Brain Python engine (`calc_core.py` + `load_curves.py` +
`cfe_savings/defaults.py`), verified bit‑for‑bit against the Python golden reference (4,536 fields,
0 diff).

It is **general‑purpose**: the same logic applies to *any* CFE GDMTH client. The seeded **GEPP**
4‑sites dataset is only a worked **proof of concept** — every new project follows the same recipe
(parse bills → optionally size‑bess / fit giro → compute → read régimen/alerts/finance). See
[§11 of the logic doc](docs/CFE-PPA-BESS-LOGIC.md#11-applying-the-engine-to-a-new-project-the-replicable-recipe)
for the step‑by‑step.

### Modes

- **`compute`** `{ inputs, bills[] }` → monthly + annual + régimen + finance (PV/BESS/Hibrido)
- **`size-bess`** `{ bills[], hours?, dod?, rte? }` → verano‑2h BESS size (kW, kWh)
- **`gepp`** `{ pv_kwp?, fp_correction? }` → the seeded GEPP 4‑sites rev3 design (per‑service,
  Proplasa rollup, portfolio totals)

`GET /` returns machine‑readable usage.

### Doctrine (one line)

> BESS 0.5C / 2h (energía = 2h × demanda punta verano); dispatch punta weekdays;
> medición neta < 0.7 MWp / autoconsumo ≥ 0.7 MWp.

See [`docs/CFE-PPA-BESS-LOGIC.md`](docs/CFE-PPA-BESS-LOGIC.md) for the full walkthrough.

## Deploy

```bash
supabase functions deploy cfe-ppa-bess
```

---

*Source of truth mirrored from Supabase project `bwudgrwfwjdbvqhgbwty`, function version 6.*
