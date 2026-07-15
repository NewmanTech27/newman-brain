# Service inventory — 2026-07-15

Snapshot taken during the Tuesday CRM reset. Purpose: user marks keep / kill per service.
Hosts surveyed: newman-vps (100.74.96.63 / DO), newman-crm droplet (167.172.142.136 — **no SSH access from any host I control; inventoried from repo docs + DNS**), dev/staging droplet (67.207.89.80 — **no SSH access**), Mac mini (100.102.142.7), MacBook Air, Cloudflare DNS (zone newman.re), Supabase.

## Public endpoints (Cloudflare zone newman.re)

| URL | Backing | Host | What it is | Env | Status 2026-07-15 |
|---|---|---|---|---|---|
| newman.re / www.newman.re | CF Pages `newman-site.pages.dev` | Cloudflare Pages | Company landing site | prod | live |
| tuesday.newman.re | tunnel 693801f5… → localhost:3000 | newman-crm droplet (167.172.142.136) | Tuesday CRM web (Next.js, `apps/crm-web`, branch `dev`) | prod | live (307→/login) |
| login.newman.re | tunnel b7cefd82… → nginx :8091 → /opt/newman-sso/login | newman-vps | Central SSO login page + `newman-sso.service` validator (nginx auth_request → Supabase Auth) | prod | live (200) |
| dev-tuesday.newman.re | A 67.207.89.80 (Caddy) | unknown droplet 67.207.89.80 | Tuesday CRM dev instance | dev | live (307→/login) |
| staging-tuesday.newman.re | A 67.207.89.80 (Caddy) | unknown droplet 67.207.89.80 | Tuesday CRM staging instance | staging | live (307→/login) |
| curvas.newman.re | A 67.205.146.19 | droplet 67.205.146.19 | "curvas" app (repo `deploy/curvas`) | prod? | live (200) |
| excalidraw.newman.re | tunnel b7cefd82… → :8091 | newman-vps | Excalidraw whiteboard (SSO-gated, 302) | prod | live |
| review.newman.re | tunnel b7cefd82… → :8091 | newman-vps | newman-review app (`newman-review.service`) | prod | live (302) |
| wa.newman.re | tunnel b7cefd82… → :8080 | newman-vps | WhatsApp/Twilio webhook gateway (`newman-agent@gateway-webhook`) | prod | 404 on `/` (webhook only) |
| api.kameloso.com | cloudflared on mini | Mac mini | Newman Data API (FastAPI docker `newman-api`) | prod | 404 on `/` (API) |

## newman-vps (100.74.96.63) — systemd services

| Service | What it does | Note |
|---|---|---|
| newman-sso.service | SSO validator for *.newman.re (auth_request) | keep with login.newman.re |
| newman-agent@email-intake / @gateway-webhook / @huddle-sync / @intake-worker | CFE bill-intake agent fleet (WhatsApp/email → OCR → Supabase) | pipeline |
| newman-review.service | review.newman.re app | |
| newman-webhook-notify.service | webhook notifier | |
| vault.service | HashiCorp Vault (authoritative secrets) | keep |
| cloudflared.service | tunnel b7cefd82 (login/excalidraw/review/wa) | keep with above |
| nginx (vhosts: login, excalidraw, review on 127.0.0.1:8091) | multiplexer behind tunnel | |
| nordvpnd, tailscaled, fail2ban, droplet-agent | infra | |
| tmux agent org (7 agents) | not running at snapshot time (`tmux ls` empty) | |

## newman-crm droplet (167.172.142.136, DO nyc1, s-1vcpu-2gb) — from deploy/crm-web/README.md

| Service | What it does |
|---|---|
| newman-crm-web.service | Next.js `apps/crm-web` on 127.0.0.1:3000, code /opt/newman-architecture tracking `dev` |
| cloudflared.service | dedicated tunnel `newman-crm` → tuesday.newman.re |
| redeploy-crm.sh (deploy user) | pull dev → build → restart; driven by GH Actions `deploy-crm.yml` |
| ufw | SSH-only (SSH key = GH secret CRM_DROPLET_SSH_KEY; no local access) |

## Droplet 67.207.89.80 (dev/staging tuesday) — no SSH access

Serves dev-tuesday + staging-tuesday behind Caddy. Deployment path unknown (no GH workflow in newman-architecture references it; likely managed by the agent org). Flag: needs an owner/access documented.

## Droplet 67.205.146.19 — curvas.newman.re (repo has `deploy/curvas`). No SSH tried.

## Mac mini (100.102.142.7)

| Service | What it does |
|---|---|
| docker: newman-api | Newman Data API → api.kameloso.com |
| docker: n8n (127.0.0.1:5678) | automation jobs |
| docker: open-webui (:3000), searxng (:8888), paperclip (:3100) | local AI stack (Duncan) |
| launchd: actions.runner.NewmanTech27-newman-architecture.mini | GitHub Actions self-hosted runner |
| launchd: com.newman.pipeline-deploy / pipeline-endpoint | newman-rebuild executor deploy + endpoint |
| launchd: com.newman.collector | CFE invoice collector |
| launchd: com.newman.tarifa-cuotas, com.newman.twilio-reconcile | tariff refresh, Twilio reconcile |
| postgres :5433 (tariffs), pg `bess` | local warehouses |

## MacBook Air (this machine)

launchd: energy.newman.intake-worker, energy.newman.email-intake, com.newman.collector (duplicates of intake/collector — likely dev copies).

## Supabase projects

| Project | Purpose | Env |
|---|---|---|
| bwudgrwfwjdbvqhgbwty | newman-architecture: pipeline schemas (client/app/cenace/cfe/…) + **crm.\* (Tuesday)** + edge functions (whatsapp-intake, huddle-sync) + pg_cron | prod |
| └ branch dev → crmrhsvsowjdnjmjbley | Tuesday/pipeline dev DB (persistent, data copy) | dev |
| └ branch staging → ytknnpxeyikttzyboysz | Tuesday/pipeline staging DB (persistent, data copy) | staging |
| oioyawhgvazebtarigpc | newman-rebuild prod (crm schema there = bill pipeline, NOT Tuesday) | prod |

## GitHub Actions deploy targets (NewmanTech27/newman-architecture)

- deploy-crm.yml: push to `dev` (paths apps/crm-web, deploy/crm-web) → SSH newman-crm droplet.
- deploy.yml: CI-green on `main` → SSH newman-vps.
- deploy-mini.yml: → mac mini self-hosted runner.
- ci.yml / ci-integration.yml / ci-miespacio.yml / db-tests.yml: CI only.
