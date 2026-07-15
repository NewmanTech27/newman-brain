# Security/privacy review of Mi Espacio CFE history-pull workflow (6/10)

**Summary**: A security-reviewer persona scored the agents Mi Espacio 1-2yr consumption-history workflow 6/10, mainly for credential and PII-at-rest gaps.
**Tags**: #newman #cfe #scraper #security #privacy #eval
**Created**: 2026-07-03
**Source**: macbook session 6635bf95-5e61-4029-a712-38b6439a2d94.jsonl, user jesus

---

## Content
- Workflow reviewed: Playwright+Chromium vs Imperva WAF at app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx; check receipt count BEFORE adding (abort if >=10, permaban risk); add receipt with RPU+No.Servicio+total_mxn; verify count incremented; download 1-2yr via Consulta tu recibo -> Otras facturas.
- Issue 1: no credential storage/rotation plan, no lockout guard after failed logins.
- Issue 2: RPU/No.Servicio in plaintext file paths, no encryption at rest or retention/purge policy (regulated PII under LFPDPPP).
- Issue 3: TOCTOU race — parallel runs could blow past the 10-receipt limit between count-check and add.
- Fixes proposed: secrets manager for creds, encrypted volume + retention window for data/raw/cfe_bills, serialize account access.

## Related Notes
- [[newman-agents-review-committee]]
