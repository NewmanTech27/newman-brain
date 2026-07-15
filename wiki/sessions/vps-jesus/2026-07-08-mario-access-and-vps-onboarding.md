# VPS Onboarding: tmux Layout, Supabase MCP Auth, Mario SSH Access

**Summary**: Set up per-user tmux sessions (jesus-01/mario-01) and Supabase MCP on newman-vps, and installed Mario's SSH public key so he can log in from Windows.
**Tags**: #newman #vps #ssh #tmux #supabase-mcp #onboarding
**Created**: 2026-07-07 / 2026-07-08
**Source**: newman-vps sessions 97244cc2-22de-41ee-99e1-69c42d7c2fc4.jsonl (user jesus) and /root 12d40858-bcb4-4c9d-b22d-5d28ec7e752e.jsonl (root); consolidated

---

## Content
- tmux configured for all users: 4-window sessions named `jesus-01`, `mario-01` for persistent recall.
- Supabase MCP added project-scoped: `claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=bwudgrwfwjdbvqhgbwty&..."` — gotcha: project-scope servers from .mcp.json sit in "Pending approval" and don't appear in /mcp until approved (session started before the file existed, so it never prompted).
- Installed `supabase` + `supabase-postgres-best-practices` agent skills into `~/.agents/skills/`.
- Root session (in Spanish): verified mario user exists on the droplet, produced a Windows ssh-keygen guide, and installed Mario's `ssh-ed25519 ... mario-newman` key into `/home/mario/.ssh/authorized_keys` (700/600 perms).
- Droplet facts: IP 146.190.211.205, SSH port 22, password auth disabled (key-only).

## Related Notes
- [[newman-agent-org]]
