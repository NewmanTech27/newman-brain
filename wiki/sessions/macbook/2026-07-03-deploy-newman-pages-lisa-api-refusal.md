# Deploy all Newman Pages; refuse LISA API IDOR + employee-dossier recon

**Summary**: Deployed GitHub Pages across the Newman repos, then declined to run IDOR/authz testing against the LISA (lisaenergy.com) production API and to scrape a LinkedIn employee dossier.
**Tags**: #newman #ui #scraper
**Created**: 2026-07-03
**Source**: macbook session 405d2f67-c389-432e-8e7b-3f275e845ebc.jsonl, user jesus

---

## Content
- Deployed Pages for all Newman repos; polled each until HTTP 200.
- User asked to curl/test the API at lisaenergy.com and check whether an auth token is committed in a repo; then to hunt for an unsecured backdoor, framing it as "my own test instance" / "real men test in prod."
- Assistant refused IDOR/authz testing against prod `zap.lisaenergy.com` (live customers, Chargebee billing, real RPUs/PII) — ownership of the box doesn't grant consent to read other tenants' data; the shifting framing (competitor → test instance → prod) each arrived after a boundary flag.
- What it offered instead: re-verify auth-gating on every route (PII routes already 401), safe checks on the user's own account/RPU.
- Also refused to build a knowledge graph of named LISA employees + LinkedIn scraping filtered to "overseas/Mexico" handlers — people-targeting recon (ToS-violating, spear-phishing shape).
- Left the door open to authenticated testing on the user's own account/RPU once steps are provided.

## Related Notes
- [[2026-07-05-newman-academy-pages-deploy-check]]
