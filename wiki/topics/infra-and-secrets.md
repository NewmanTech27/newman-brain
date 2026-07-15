# Infrastructure & Secrets

**Summary**: The physical/logical topology — mac mini, DigitalOcean droplet (newman-vps), Supabase projects, Cloudflare tunnels, GitHub accounts — plus the secrets doctrine (HashiCorp Vault authoritative) and the recurring devops gotchas.
**Tags**: #newman #devops #infra #secrets #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Hosts
- **mac mini** (tailnet 100.102.142.7): the runtime that clears the CFE WAF (Mexican residential IP), runs the harvest one-shot drains, Ollama local models, FastAPI docker + Cloudflare tunnel `mac-mini-ai` (api.kameloso.com), and the launchd auto-deploy poller. Node runs under nix-darwin.
- **DigitalOcean droplet / newman-vps** (146.190.211.205 / tailnet 100.74.96.63): agent-orchestration + web apps (review.newman.re, tuesday.newman.re). Users `jesus` (non-sudo — `claude --dangerously-skip-permissions` refuses root) and `mario` (root-capable). ssh aliases `droplet`, `droplet-jesus`. **Do not run the CEO agent here** (a reset loses remote access) and **never reboot the box**.
- Ollama: qwen3.6 (Q4) beats qwen3.5 on Newman tasks (GDMTO/PPA reasoning, 25.5 tok/s) but MUST be called via `/api/chat` — `/api/generate` skips the chat template.

### Supabase projects
- **bwudgrwfwjdbvqhgbwty** = legacy warehouse / newman-architecture (cfe/cenace/cre/app/bess_raw schemas).
- **oioyawhgvazebtarigpc** (us-east-2) = newman-rebuild prod (dev/staging/prod envs).
- Publishable/anon keys are fine to embed in client HTML (role=anon); service_role only server-side.

### Secrets doctrine
- **HashiCorp Vault is authoritative** (`secret/synaptiq/backend` on the droplet, loopback + self-signed TLS — needs `bash -ic` in an interactive shell to reach). The Supabase Vault copy is drifted. A DO token once leaked in-chat (and in a plaintext `name` column) — rotated to Vault v8, plaintext row deleted.
- Gotcha: an AppRole/token may be read-only — the first Vault password write can fail silently; always verify write capability first.
- The permission guard blocks agent-side credential retrieval from the droplet vault; some steps end with a one-liner left for Jesus to run at his own keyboard.

### Vault hardening & VPS ops (Jul 07–09)
- HashiCorp Vault on newman-vps got **auto-unseal** (key at `/etc/vault.d/unseal.key`, 400 root:root; env from `~/.config/vault.env`); root token, Supabase service_role, and the leaked DO token all rotated ([[2026-07-07-vault-secrets-hardening]]). Later some secrets migrated Vault → Supabase secrets via the CLI ([[2026-07-08-curvas-consumption-curves]]).
- Boot-race lesson: `vault-fetch.service` ran before Vault was ready and failed all 5 agent services every boot — disabled; broken NordVPN snap mount removed ([[2026-07-09-vps-reboot-cleanup]]).
- Known leak: `sudo -n vault-env env` prints NEWMAN_API_DSN unredacted ([[2026-07-10-newman-rebuild-seat-org]]).
- Users on the droplet: mario's ssh-ed25519 key installed (key-only auth); per-user tmux sessions jesus-01/mario-01 ([[2026-07-08-mario-access-and-vps-onboarding]]).

### SSO & web apps
- **login.newman.re** = Supabase-Auth SSO gate (Google-only, `.newman.re` cookie) fronting all *.newman.re subdomains; RBAC admins = mario/jonathan/jesus. CRITICAL: it lives box-only at `/opt/newman-sso` (captured later to newman-rebuild) and validates the **email suffix instead of the Google `hd` claim** ([[2026-07-08-excalidraw-sso-crm-prod]], [[2026-07-10-newman-rebuild-seat-org]]).
- Deploy pattern for newman.re apps: GitHub Actions rsync as `deploy` user → releases + `current` symlink, nginx on localhost, cloudflared tunnel ingress + `tunnel route dns` (dev.newman.re, curvas.newman.re, excalidraw.newman.re) ([[2026-07-08-newman-landing-deploy]]).
- **Prod cannot be rebuilt from git** (DEL-4): bwudgrwfwjdbvqhgbwty knew only 5/75 git migrations; freeze REVOKEs are ledger-invisible — dump live schema + ACLs before ever dropping it ([[2026-07-09-supabase-devops-gate0]]).

### Auth gotchas (Mario's VPS sessions)
- Supabase CLI can't do the browser login non-TTY — use `supabase login --token sbp_...`; project-scoped MCP servers need in-session approval and only rebind on `/mcp` reconnect. Client-data Supabase project = `ugjqqezqtnjkzxkcqujz` ([[2026-07-08-supabase-mcp-and-auth-setup]]).
- gcloud as mario@newman.re crashes (`EOFError`) under the `!` runner; token expires ~hourly; use `--enable-gdrive-access`. Two Google identities: gcloud mario@newman.re (Drive write to client folders) vs MCP Drive newman.jjzo@gmail.com (read-only, can't reach client folders).
- `.claude/settings.json` pins Fable 5 per project and reasserts on restart over `/model` switches.

### DevOps gotchas
- GitHub: **NewmanTech27** = tech@newman.re (11+ private repos, primary for client work); **lopezpalacios** = personal Pages. Switch with `gh auth switch -u NewmanTech27`; push with `gh auth git-credential` helper.
- Cloudflare adopted for DNS automation (remote MCP `mcp.cloudflare.com/mcp`) over Hostinger. Tunnel ingress rule for api.kameloso.com must sit BEFORE the 404 catch-all.
- tmux OSC 52 clipboard: Terminal.app can't write it (use iTerm2); Supabase MCP OAuth on the droplet needs `ssh -t -L 8976:localhost:8976`.
- Backups: pull the droplet backup off-box ("a backup that only lives on the box it protects isn't a backup"); `git bundle verify` must run inside a repo.

## Related Notes
- [[2026-07-07-droplet-setup-secrets]]
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
- [[2026-07-09-agent-org-ceo-cto]]
- [[2026-07-10-newman-ceo-session-branch-consolidation]]
- [[2026-07-12-rebuild-repo-audit-readme-issues]]
- [[2026-06-24-qwen36-mini-bakeoff]]
- [[2026-06-27-newman-data-api-fastapi-mini]]
- [[2026-06-23-newman-re-registrar-workspace-dns]]
- [[2026-07-03-newman-repos-committee-audit]]
- [[2026-07-07-vault-secrets-hardening]]
- [[2026-07-08-mario-access-and-vps-onboarding]]
- [[2026-07-08-newman-landing-deploy]]
- [[2026-07-08-excalidraw-sso-crm-prod]]
- [[2026-07-08-curvas-consumption-curves]]
- [[2026-07-09-vps-reboot-cleanup]]
- [[2026-07-09-supabase-devops-gate0]]
- [[2026-07-08-supabase-mcp-and-auth-setup]]
