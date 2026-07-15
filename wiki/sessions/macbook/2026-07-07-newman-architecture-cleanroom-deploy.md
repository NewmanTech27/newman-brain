# Clean-room transfer of Newman agents into newman-architecture + droplet deploy

**Summary**: Seven implementer agents clean-roomed the whole mac-mini pipeline (cfe-collector, market-loaders, design-engine, ...) into the newman-architecture repo with tests/CI, then deployed to the droplet with Vault-injected secrets, systemd units, and a Cloudflare tunnel webhook.
**Tags**: #newman #agents #cleanroom #cfe #devops #vault #ci
**Created**: 2026-07-07
**Source**: macbook session 6f417ebf-02cb-4ef8-9066-fa7783a70797.jsonl, user jesus

---

## Content
- Boundaries: mac mini (tailnet 100.102.142.7) = dev only; runtime = newman-vps (100.74.96.63) under `vault-env`; Vault bound to 127.0.0.1:8200 on the VPS, never reachable from dev; strict env-var contract, `.env.example` only, no secrets in repo.
- Clean-room implementations at `/Users/jesuslopez/newman-architecture/agents/`:
  - `cfe-collector` — Stage 3 "Adquirir histórico": Consulta-based lane detection; BÁSICO harvests → `upsert_bill` (logs warehouse rejections); CALIFICADO → `store_bulk_bill`; `eliminar_servicio` cleanup; 11 tests, ruff clean.
  - `market-loaders` — full CFE tariff pipeline (monthly DOF-primary / CENACE-fallback URLs back to Dec 2018) + PML + nodos loaders.
  - `design-engine` — pure deterministic max-NPV `(kWp, BESS_kW, BESS_kWh)` sweep: `E_pv = kWp·Y(m)·PR` (PR=0.80), PV≈0 at punta so BESS is sole punta lever, PV-surplus charges BESS before grid, exempt regime kWp_DC ≤ 839.41, inverter ≤ demanda contratada.
- Supabase password reset and stored in HashiCorp Vault (`secret/synaptiq/backend`, versions 5–6); Google OAuth JSON vaulted then shredded from disk.
- GitHub Actions CI/CD added: tests on push + auto-deploy to the droplet (deploy.sh builds venv + npm); systemd units installed — design-engine + market-loaders timers enabled, Google-dependent agents installed-but-disabled pending GOOGLE_SERVICE_ACCOUNT_JSON.
- Cloudflare tunnel webhook set up (cloudflared cert issued for the zone).
- CFE portal findings re-confirmed: no REST API (legacy ASP.NET WebForms) but postbacks are replayable as raw HTTP POSTs (cookies + __VIEWSTATE + __EVENTTARGET) — flagged as next optimization; Consulta requires the EXACT name (blank → "campos obligatorios", wrong → "no coincide"), so RPU-only intake can't drive the portal — OCR reads the exact name off the bill (HOTELES YORI got 30 recibos this way).

## Related Notes
- [[2026-07-07-droplet-setup-secrets]]
- [[2026-07-04-cfe-invoice-harvest-supabase]]
- [[2026-07-08-supabase-pipeline-pgcron]]
