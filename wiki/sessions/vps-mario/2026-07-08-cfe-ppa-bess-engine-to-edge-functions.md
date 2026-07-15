# CFE-PPA-BESS Engine → Supabase Edge Functions + newman-brain Repo

**Summary**: Ported the CFE Brain PPA+BESS savings engine into a Supabase edge function, documented its tariff logic in the newman-brain repo, and ran real Yazaki meters through it end-to-end.
**Tags**: #newman #cfe-brain #supabase #edge-functions #bess #ppa #yazaki
**Created**: 2026-07-08
**Source**: newman-vps sessions a56f35a2, 330d707a, 626ff942, b3b62a68, 488814f8, user mario

---

## Content
- Origin of the **newman-brain** GitHub repo: user wanted the cfe-ppa-bess logic from a Supabase edge function extracted into a repo with a step-by-step markdown (`docs/CFE-PPA-BESS-LOGIC.md`). GEPP data used only as proof-of-concept; logic must be replicable for every project.
- Repo hosted on **GitHub** (NewmanTech27 / `gh` device auth), after the user first asked for "DigitalOcean repo" — corrected: DO is not a git host (Spaces = object store, App Platform pulls from GitHub, Droplet = only real git-push path). GitHub chosen.
- **Tariff mechanics baked into engine.js**: umbral (threshold) = `kWh / (days × 24 × FC)`, load factor **FC = 0.57** (note: 0.55 used elsewhere for GDMTO). `IVA = 0.16`.
- **Capacidad** charge basis = `min(kw_punta, umbral)` (falls back to `umbral` when no kw_punta) — engine.js:259. The doc's §1 one-liner ("billed on kW_punta") was imprecise; §6 step 3 is correct. Fixed §1 to match and reordered so umbral is defined before capacidad. Engine never recomputes baseline capacidad — takes actual peso amount off the receipt, derives r_cap = capacidad / basis.
- **Distribución** billed on `max(kW_base, kW_inter, kW_punta)`.
- Engine deployed to Supabase **main branch**; ran 3 Yazaki meters live through deployed `cfe-ppa-bess`.
- **Yazaki portfolio result** (verano-2h BESS): media `646010612877` $25.70M base → 1,550kW/3,100kWh, $6.55M/yr (25.5%), checksum 0.50% reliable; grande `624070800237` $38.09M → 2,500/5,000, $10.87M/yr (28.5%), 1.22%; chico `626140901179` $1.14M → 100/200, $0.38M (33.1%), checksum 15.77% UNRELIABLE. Portfolio $64.9M / 4,150kW / 8,300kWh / $17.8M / 27.4%.
- Built-in reconstruction checksum: Σ real importes × 1.16 vs real facturación — flags trustworthiness per meter.
- **Key data gotcha**: Supabase stores only total kWh + kw_max + per-period *costs* for Yazaki; kWh-by-period and demand-by-period registers are NULL. B/I/P split and kw_punta are modeled (Industrial 24/7 load curve, kw_punta≈kw_max), so BESS shave is optimistic — prefeasibility, not bankable. Query filtering Yazaki bills on `kwh_punta IS NOT NULL` returned empty.
- Repo commit `716ac62` pushed 67 files; git identity set to `Newman <newman.jjzo@gmail.com>`.

## Related Notes
- [[newman-brain-repo]]
- [[cfe-brain-vault]]
- [[2026-07-08-supabase-mcp-and-auth-setup]]
- [[2026-07-11-gdmto-vs-gdmth-bess-value]]
