# newman-data-api: FastAPI over the warehouse, live on the mini

**Summary**: Built and shipped a FastAPI service exposing the Newman warehouse, running as a Docker container on the mac mini behind a Cloudflare tunnel at api.kameloso.com.
**Tags**: #newman #warehouse #cfe
**Created**: 2026-06-27
**Source**: macbook session 37875c10-0d01-489e-a6ac-9b33dba6a20c.jsonl, user jesus

---

## Content
- Applied API best practices (professional-api-generator role): frameworks/requirements review, then published + deployed.
- Repo: https://github.com/lopezpalacios/newman-data-api (public).
- Live API on the mini via Cloudflare tunnel `mac-mini-ai`:
  - Health: https://api.kameloso.com/health → `{"status":"ok","db":true}`
  - Docs: /docs (Swagger), /redoc; Data: `/v1/tariffs/by-cp/77710` → 106 rows, all 12 codes.
- Deploy shape: docker `newman-api` (`--restart unless-stopped`) on 127.0.0.1:8000; tunnel ingress adds `api.kameloso.com → localhost:8000` **before** the 404 rule so `mentat.kameloso.com` stays untouched (verified 200).
- Secrets: Supabase-pooler DSN only in mini `.env`, never committed.
- Tests 9/9 (5 unit + 4 live); survives reboot (launchd tunnel + container restart policy).
- Loose ends: no auth on FastAPI (public reference data; roadmap = per-consumer API keys via Cloudflare API Shield + edge cache); data source = Supabase pooler (PML = June sample), option to switch `.env` to mini Postgres.

## Related Notes
- [[2026-06-26-cfe-warehouse-schema-supabase]]
