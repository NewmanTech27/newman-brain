# Newman Landing Page CI/CD to dev.newman.re

**Summary**: Wired the Newman landing page repo into a Cloudflare-tunnel + GitHub Actions deploy on newman-vps at dev.newman.re, with Supabase as backend.
**Tags**: #newman #landing #ci-cd #cloudflare #nginx
**Created**: 2026-07-08
**Source**: newman-vps session 6b14c9ff-e4c6-44c6-87a4-376541a1817f.jsonl, user jesus

---

## Content
- Ask: deploy the existing Newman landing GitHub repo with proper CI/CD, Cloudflare-fronted, webapp-ready with Supabase backend; repo moved from newman-architecture into the organization repo.
- Pattern: GitHub Actions rsync as `deploy` user → `/opt/newman-landing/releases` + `current` symlink; nginx on 127.0.0.1:8092; cloudflared tunnel ingress `dev.newman.re → http://localhost:8092`; `cloudflared tunnel route dns` for the CNAME.
- Deploy key: `newman-landing-deploy@github-actions` ed25519 appended to /home/deploy/.ssh/authorized_keys.
- Lesson explicitly stated: a Cloudflare API token controls Cloudflare only — it cannot do the VPS-side steps (nginx site, tunnel config, webroot, key authorization); those Jesus ran manually from a pasted block, then the workflow was triggered.

## Related Notes
- [[2026-07-08-excalidraw-sso-crm-prod]]
