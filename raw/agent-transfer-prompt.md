# Task: clean-room transfer of the Newman agents into the `newman-architecture` repo

## Environment & boundaries (read first)
- You are Claude Code on the **Mac mini** (tailnet 100.102.142.7) — a DEVELOPMENT
  workstation. You write code, update docs, and open a PR. You do NOT deploy or run
  the agents against live infrastructure here.
- The RUNTIME/DEPLOY target is a different host: **newman-vps** (100.74.96.63).
  Agents run THERE under `vault-env`, which exists only on the VPS.
- **Vault is not reachable from this machine.** It is bound to 127.0.0.1:8200 on
  newman-vps and intentionally NOT exposed over Tailscale. Do not attempt to connect
  to it, and do not assume `vault-env`, `/etc/vault.d/*`, or the `vault` CLI exist
  locally. If any code or test tries to reach Vault from here, that's a bug.
- Code STRICTLY against the env-var contract below. Secrets arrive as environment
  variables at runtime (injected by `vault-env` on the VPS). Locally, support a
  `.env` for development but commit only a `.env.example` with variable NAMES and no
  values. Never put real secrets anywhere in the repo.
- Deliverables are code + docs + a PR against `newman-architecture`. Running the
  pipeline end-to-end against real Vault/Supabase happens later, on the VPS, as a
  separate step — not part of this task.

## Goal
Bring the pipeline agents into the `newman-architecture` repo so it becomes the
deployable source of truth (not just docs). Use `newman-pipeline` (and
`newman-agents`) as the behavioural REFERENCE and re-implement in a **clean-room**
way — adapt, don't blindly copy. When behaviour or structure changes, the
architecture docs in this repo MUST be updated in the same PR.

## Repos & roles
- REFERENCE (read-only, source of behaviour): `newman-pipeline`, `newman-agents`
- TARGET (where code + docs live): `newman-architecture` (this repo)
- Transfer: [WHICH AGENTS — e.g. "the WhatsApp webhook worker, the CFE solver,
  and the design/proposal engine" — and TARGET LAYOUT, e.g. "/agents/<name>/"].

## Clean-room rules (strict)
1. Treat `newman-pipeline` as a spec: read it, understand intent, then re-implement
   cleanly in the target. Preserve behaviour; do not carry over dead code, cruft,
   commented-out blocks, or environment-specific hardcoding.
2. NEVER copy secrets, tokens, keys, connection strings, or hardcoded IDs. Every
   secret is read from the environment. If you find a hardcoded secret in the
   reference, replace it with an env var and note it in the PR description.
3. Keep each agent self-contained and documented (its own README: purpose, inputs,
   outputs, env vars consumed, the RPCs it calls, how to run it under `vault-env`).

## Integration contract (the target platform — MUST match exactly)

### Secrets — HashiCorp Vault via `vault-env`
- In PRODUCTION (on newman-vps) every process is LAUNCHED as `vault-env <command>`
  (e.g. `vault-env node worker.js`). `vault-env` AppRole-logs-in and injects all
  fields of KV-v2 path `secret/synaptiq/backend` as env vars. On the Mac mini there
  is no `vault-env`; run locally with a dev `.env` (names from `.env.example`,
  values you supply) — never real prod secrets. Do NOT read Vault directly, do NOT
  write a prod .env file, do NOT bake secrets into images.
- Available env vars (names are exact): CFE_USER, CFE_PASS, CFE_EMAIL,
  TWOCAPTCHA_KEY, CLOUDFLARE_NEWMAN_TOKEN, DOMAIN101_API_KEY, DIGITALOCEAN_TOKEN,
  GITHUB_TOKEN, OPENROUTER_API_KEY, unsplash_access_key, unsplash_application_id,
  unsplash_secret_key, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, DRIVE_ID,
  RAW_BILLS_FOLDER_ID, STOCK, PORT, NEWMAN_API_DSN, WA_SUPABASE_URL,
  WA_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY.

### Supabase — service_role only
- Authenticate to Supabase with SUPABASE_SERVICE_ROLE_KEY (NOT the anon key).
  All application RPCs were locked to `service_role`; any anon-key call now returns
  403. Remove every anon-key code path used for data access.
- Direct table access to `client.*` is not granted; go through these RPCs only:
  - Ingest:   note_whatsapp_intake(p_rpu text, p_file text, p_folder text) -> bigint
              claim_intake_events(p_limit int)
              mark_intake_done(p_id bigint, p_status text, p_detail text)
              request_design(p_rpu text)
  - Bills:    upsert_bill(p jsonb) -> bool  (NOTE: returns false unless the payload
              has reconciled=true — reconciliation is the entry gate)
              store_bulk_bill(p jsonb)
  - Design:   insert_design(p jsonb) -> bigint
  - Reads:    get_bills(p_rpu), get_bill_series(p_rpu), get_bulk_bills(p_rpu),
              get_consumption(p_rpu), get_invoice_series(p_rpu),
              get_designs_by_client(p_client), get_latest_design(p_rpu),
              get_pml_profile(p_market)

### Known gap to resolve (call it out, don't invent)
- There is NO Google credential in Vault yet (only DRIVE_ID / RAW_BILLS_FOLDER_ID /
  STOCK folder IDs). The Drive-writing agent needs a Google service-account (or
  OAuth) credential. Add a required env var (propose the name, e.g.
  GOOGLE_SERVICE_ACCOUNT_JSON) and document that it must be loaded into
  `secret/synaptiq/backend`. Do not hardcode or commit any Google credential.

## Documentation rules (hard requirement)
- `newman-architecture/README.md` contains Mermaid views (L1 context, L2 containers,
  L3 pipeline, sequences, ER). If your changes alter components, data flow, RPC
  names, env vars, or the deployment shape, UPDATE those diagrams and the prose in
  the SAME change. The diagrams are the contract — keep them true.
- Each transferred agent gets/updates its own README as described above.
- If you rename/replace anything from `newman-pipeline`, record the mapping
  (old -> new) in the PR description.

## Definition of done
1. Agents build and pass their own lint/tests in `newman-architecture`.
2. No secret/credential is committed; all secrets come from env.
3. Every Supabase call uses service_role + the RPC contract above (no anon, no
   direct client.* table access).
4. Root README Mermaid diagrams + per-agent READMEs reflect the real, current code.
5. Ship a `.env.example` (variable names only) and a `Makefile`/npm script that runs
   each agent locally from `.env`, AND documents the prod `vault-env` launch command.
6. A top-level "Deployment / agents" section documents how to run each agent under
   `vault-env` on newman-vps, including the new Google credential requirement.
7. Open a PR (do NOT push to main) summarising what was transferred, what was
   re-implemented clean-room, and the old->new mapping.
