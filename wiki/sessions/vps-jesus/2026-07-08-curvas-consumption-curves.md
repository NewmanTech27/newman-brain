# Consumption-Curve Modeling + curvas.newman.re Info Site

**Summary**: Designed client load-curve tables (% of contracted kW by area/industry) in the client schema, launched curvas.newman.re (Spanish, Newman UI) on a new droplet, and migrated tokens from Vault to Supabase secrets.
**Tags**: #newman #load-curves #curvas #supabase #secrets
**Created**: 2026-07-08
**Source**: newman-vps session b1b2f1b0-38c2-4ce2-b15a-e449013566bb.jsonl, user jesus

---

## Content
- Concept: map electricity consumption curves per client by area + industry type, expressed as percentages of maximum contracted kW; no 15-min data available, so implemented the policy/typical-profile option on the client schema.
- Built `curvas.newman.re` — informational page in Spanish explaining consumption curves graphically, Newman UI/UX (Tuesday style), hosted on a basic new DO droplet.
- Cloudflare: added Twilio TXT verification record `twilio-domain-verification=15912f...` via API token.
- Secrets consolidation: installed + authenticated Supabase CLI on the VPS, migrated secrets from HashiCorp Vault into Supabase (single DO token kept, provision token dropped).
- Follow-up prompt drafted for the extraction agent: add an industry-sector field during OCR — when a sales rep sends an invoice, confirm the RPU then offer multiple-choice sector options.
- Side thread: iTerm2-over-ssh garbled TUI (old text interleaved into new) diagnosed as SSH/tmux size-desync repaint issue — fix: resize window (SIGWINCH), Ctrl+L, `reset` + `claude --continue`; tmux is the main amplifier.

## Related Notes
- [[newman-secrets-topology]]
- [[2026-07-08-tuesday-crm-committee-loop]]
