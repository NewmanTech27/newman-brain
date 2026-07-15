# CFE Extraction CI/CD Fix, Unit Tests, and the Postback Pseudo-API Probe

**Summary**: Fixed the buggy CI/CD, pushed for unit tests over the whole CFE extraction path, and prepared a __doPostBack pseudo-API probe for Consulta/MiEspacio — blocked at the end on SSH auth to the Mac mini.
**Tags**: #newman #cfe #ci-cd #testing #mac-mini
**Created**: 2026-07-07
**Source**: newman-vps session dd519561-3f09-4353-9008-e3efc6d275f0.jsonl, user jesus

---

## Content
- Task 1: "fix the buggy ci cd" on the CFE extraction repo.
- Task 2: unit tests for the whole CFE extraction part.
- Task 3: probe an .aspx "pseudo-API" — replay `__doPostBack` as raw HTTP POSTs (cookies + __VIEWSTATE) against app.cfe.mx Consulta and MiEspacio, skipping browser clicks. Test RPU: 784220900267.
- Probe script written on the VPS but must run from the Mac mini (Mexican VPN/NordVPN IP).
- Blocker: mini reachable over Tailscale (ping OK) but port 22 is macOS sshd rejecting all keys — Tailscale SSH not enabled on the mini and the VPS has no authorized private key. Dedicated keypair generated on VPS, awaiting Jesus to authorize it.
- Gotcha: `tailscale ssh` does not accept `-o` OpenSSH flags.

## Related Notes
- [[cfe-tariff-backend-feed]]
- [[newman-invoice-collector]]
