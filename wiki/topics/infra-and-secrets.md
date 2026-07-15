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
