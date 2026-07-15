# DigitalOcean droplet setup, users, secret vaulting, clean-room kickoff

**Summary**: Stood up the newman DigitalOcean droplet (146.190.211.205): ssh aliases, jesus/mario users, Claude installed on-box, DO/OpenRouter/GitHub tokens rotated into the Supabase vault, and kicked off clean-rooming newman-backend + newman-pipeline.
**Tags**: #newman #devops #droplet #secrets #cleanroom
**Created**: 2026-07-07
**Source**: macbook session af33d0c2-1e3d-4814-8d23-a2ff7e7ec603.jsonl (~/.ssh project dir), user jesus

---

## Content
- New DO droplet at 146.190.211.205; ssh via existing ed25519 key; ssh config aliases `droplet` and `droplet-jesus`.
- Migration goal: move the agent-orchestration layer (Supabase, Monday, 2captcha, etc. integrations) onto the droplet.
- Security hygiene: a DO token was pasted in-chat (`dop_v1_c571...`), deleted and rotated twice; final rotated token + OPENROUTER_API_KEY + GitHub token stored in the Supabase vault (STORED: DIGITALOCEAN_TOKEN / OPENROUTER_API_KEY).
- Users: `mario@` created (root-capable, pending his pubkey) and `jesus` (powerful but non-sudo) because `claude --dangerously-skip-permissions` refuses to run as root; Claude Max sub authenticated under user jesus; OpenRouter kept only as fallback when Claude is down.
- GitHub authenticated for both root and jesus on the droplet.
- tmux OSC 52 clipboard configured (tmux 3.4, `set-clipboard on`); gotcha: Terminal.app doesn't support OSC 52 writes — iTerm2 needs "Applications in terminal may access clipboard"; Supabase MCP OAuth on the droplet needs `ssh -t -L 8976:localhost:8976 droplet-jesus` port-forward.
- Started `/clean-room` of newman-backend and https://github.com/NewmanTech27/newman-pipeline.

## Related Notes
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
- [[2026-07-09-agent-org-ceo-cto]]
