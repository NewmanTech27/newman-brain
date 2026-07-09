---
title: tuesday.newman.re is the Tuesday CRM on its own droplet
service: tuesday-inputs
kind: descriptive
sources: ["newman-architecture/apps/crm-web/.env.example:7", "newman-architecture/deploy/systemd/newman-crm-web.service", "newman-architecture/deploy/crm-web/README.md", "newman-architecture/.github/workflows/deploy-crm.yml"]
verified_at: 2026-07-09
verified_against: a81c43c
confidence: verified
---

# tuesday.newman.re is the Tuesday CRM on its own droplet

`tuesday.newman.re` is the **Newman "Tuesday" CRM** — `apps/crm-web`, a Next.js 15 PWA, the self-hosted monday.com replacement ("Tuesday" = the day after Monday).

The name appears on newman-vps **only** in the source tree and a stale `.next/` build artifact, which misleads: the running service is **not on newman-vps**. It runs on a dedicated DigitalOcean droplet `newman-crm` (nyc1), `next start` bound to `127.0.0.1:3000` (`newman-crm-web.service`), exposed by its **own** Cloudflare Tunnel → `localhost:3000`. That is why `/etc/cloudflared/config.yml` on newman-vps has no `tuesday` entry. CD is automated: push to `dev` touching `apps/crm-web/**` triggers `deploy-crm.yml` → SSH → `redeploy-crm.sh`.

Live check: `curl https://tuesday.newman.re/` → HTTP 307 (auth-gate redirect to `/login`). The service is alive, not a corpse.

Do not assume "tuesday" == the CRM only because of build artifacts on this box — this page is the resolved evidence. See the input surface in [[whatsapp-intake-silent-drop]] and the spec `docs/specs/tuesday-inputs.md`.
