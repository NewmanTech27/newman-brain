# Decommission log — 2026-07-15

Executed per keep/kill decision against `service-inventory-2026-07-15.md`. No machine was rebooted.

| Service | Action taken | How to restore | Blockers / notes |
|---|---|---|---|
| excalidraw.newman.re (vps) | **KEEP** (scope change mid-task) — nothing touched | n/a — nginx vhost, tunnel ingress, /opt/excalidraw all intact; verified live (302→SSO) | none |
| dev-tuesday.newman.re DNS | KILLED — A record deleted via CF API (token = Vault `secret/synaptiq/backend:CLOUDFLARE_NEWMAN_TOKEN`) | Re-create A record → 67.207.89.80, proxied | Droplet 67.207.89.80 still running & unreachable by SSH — **destroy manually in DO console** |
| staging-tuesday.newman.re DNS | KILLED — A record deleted via CF API | Re-create A record → 67.207.89.80 | same droplet flag as above |
| mini docker: n8n | KILLED — workflows/credentials export attempted first (instance was EMPTY: 0 workflows, 0 credentials — see `docs/decommissioned/n8n-workflows-2026-07-15.json`); `docker stop && rm` | Volume **n8n_n8n_data** preserved (`/var/lib/docker/volumes/n8n_n8n_data/_data`); `docker run -p 127.0.0.1:5678:5678 -v n8n_n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n` | none |
| mini docker: open-webui | KILLED — `launchctl bootout/disable gui/501/com.open-webui.serve`; plist → `com.open-webui.serve.plist.disabled`; container stopped (was `--rm`, auto-removed) | Volume **open-webui** preserved; plist is nix-darwin generated (`/nix/store/...-open-webui-start`) — rename back or darwin-rebuild | nix-darwin rebuild will regenerate the LaunchAgent — remove the module from the nix config to make this permanent |
| mini docker: searxng | KILLED — stop + rm | Volumes preserved: anonymous `dce9db42…` (/etc/searxng) and `31813c0…` (/var/cache/searxng); `docker run searxng/searxng:latest` | none |
| mini docker: paperclip | KILLED — `docker compose -f ~/paperclip-deploy/compose.mini.yml down` (network removed, container gone) | Data is a bind mount at `~/paperclip-deploy/data/paperclip` (untouched); `docker compose -f ~/paperclip-deploy/compose.mini.yml up -d` | none |
| mini docker: newman-api + api.kameloso.com | KILLED — stop + rm; cloudflared ingress rules for `api.kameloso.com → :8000` (newman-api) and dead `→ :8790` removed; tunnel restarted | Config backup `~/.cloudflared/config.yml.bak-20260715`; image `newman-data-api` still local | **Deviation kept deliberately:** `api.kameloso.com` hostname NOT fully removed — path rule `/newman/pipeline/.* → :8791` retained because it fronts the KEEP job `com.newman.pipeline-endpoint` (verified 200 post-change). Root of api.kameloso.com now 404s. |
| mini launchd: com.newman.tarifa-cuotas | KILLED — bootout + disable; plist → `.plist.disabled` | `mv` plist back + `launchctl enable gui/501/... && bootstrap` | none |
| mini launchd: com.newman.twilio-reconcile | KILLED — bootout + disable; plist → `.plist.disabled` | same as above | none |
| vps: nordvpnd | KILLED — `systemctl disable --now nordvpnd nordvpnd.socket`; `nordvpnd-killswitch` is static → **masked**; all inactive | `systemctl unmask nordvpnd-killswitch; systemctl enable --now nordvpnd.socket nordvpnd` | none |

## Verification (2026-07-15)
- `docker ps -a` on mini: empty. `launchctl list`: tarifa-cuotas / twilio-reconcile / open-webui gone.
- https://api.kameloso.com/ → 404 (tunnel catch-all); /newman/pipeline/health → 200 (kept endpoint).
- dev-tuesday / staging-tuesday: DNS deleted (curl now fails to resolve).
- https://excalidraw.newman.re → 302 to SSO (KEEP intact).
- nordvpnd/socket disabled+inactive, killswitch masked. No reboots performed.

## Outstanding
1. Destroy droplet 67.207.89.80 (dev/staging tuesday) manually in the DigitalOcean console — no SSH access.
2. Optional: remove open-webui + n8n/searxng docker bits from the mini's nix-darwin config so a darwin-rebuild doesn't resurrect the open-webui LaunchAgent.


- 2026-07-15: droplet 584049096 newman-crm-nonprod (67.207.89.80) destroyed via DO API; verified not_found. Note: Vault also holds CRM_NONPROD_SSH_KEY (now moot).

## Addendum (later 2026-07-15)
- Droplet 584049096 `newman-crm-nonprod` (67.207.89.80): destroyed via DO API (token from Vault). Verified 404.
- `newman-review.service` (vps): disabled + stopped; `/opt/newman-review/newman-review.env` (plaintext Twilio token + pooler password) shredded — Twilio token lives in Supabase secrets. review.newman.re now 301 → tuesday.newman.re/review (feature migrated into Tuesday CRM).
- Supabase bwud security fixes (migration `security_advisor_fixes`): RLS enabled on client.ocr_retry/collector_heartbeat/processed_media; crm.todo_subtask always-true policy → crm.is_newman(); 4 cfe.* views → security_invoker.
