# Locate newman.re registrar + configure Google Workspace DNS

**Summary**: Found newman.re's registrar via WHOIS (101domain) and laid out the exact TXT/MX/SPF/DKIM/DMARC records to wire up Google Workspace.
**Tags**: #newman
**Created**: 2026-06-23
**Source**: macbook session ac970995-8682-45d9-a1d8-c0913c6f0eb9.jsonl, user jesus

---

## Content
- Registrar: **101domain GRS Ltd** (registrar@101domain.com), registered 2024-07-05; `.re` = Réunion TLD, AFNIC-managed. Manage DNS at 101domain.com.
- Workspace setup: verify domain via TXT (`google-site-verification=...`, host `@`); email routing via MX `@` priority 1 → `smtp.google.com` (new single-record style).
- Recommended: SPF TXT `v=spf1 include:_sp.google.com ~all`; DKIM generated in Admin console (Apps → Gmail → Authenticate email); DMARC TXT `_dmarc` → `v=DMARC1; p=none; ...`.
- Account recovery: 101domain "Forgot password" with jesus@lopezpalacios.com, or find purchase receipt in Gmail.
- (Off-topic aside in session: OTC aspirin dosing question — not weight-based for adults, 4000 mg/day ceiling.)

## Related Notes
- [[2026-07-05-newman-academy-pages-deploy-check]]
