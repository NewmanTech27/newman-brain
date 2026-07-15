# HashiCorp Vault Setup + Secrets Hardening on newman-vps

**Summary**: Stood up HashiCorp Vault on newman-vps with auto-unseal, rotated leaked tokens (Supabase service_role, DigitalOcean), and published the newman-architecture mermaid/agent-transfer docs.
**Tags**: #newman #vault #secrets #newman-architecture #devops
**Created**: 2026-07-07
**Source**: newman-vps session e0ab9b25-db7a-4aa3-984a-7bff95fc41df.jsonl, user jesus

---

## Content
- Started as "check the backend" via Supabase MCP; pivoted to "create proper security vault" — considered 1Password CLI, chose self-hosted HashiCorp Vault instead.
- Configured auto-unseal: unseal key stored at `/etc/vault.d/unseal.key` (mode 400 root:root, 44-char base64); vault env sourced from `~/.config/vault.env`.
- Rotated Vault root token and Supabase service_role key (patched to version 2), then rotated DIGITALOCEAN_TOKEN (version 4) after prior plaintext exposure.
- Created a new repo docs push: mermaid diagram explaining how all Newman tools are linked ("professional data engineer / software architect" rewrite after first draft judged ugly).
- Wrote `docs/agent-transfer-prompt.md` in NewmanTech27/newman-architecture — the clean-room prompt for the Mac mini's Claude Code to transfer agents from newman-pipeline/newman-agents, including vault-env + service_role contract, RPC list, dev-on-mini/deploy-on-VPS boundary.
- Gist creation failed: fine-grained PAT lacked the separate "Gists" account permission — committed to repo instead (better: versioned next to diagrams).
- Gotcha: token had admin/repo rw but gists need Account permissions → Gists → Read/write on fine-grained PATs.

## Related Notes
- [[2026-07-08-mario-access-and-vps-onboarding]]
- [[newman-secrets-topology]]
