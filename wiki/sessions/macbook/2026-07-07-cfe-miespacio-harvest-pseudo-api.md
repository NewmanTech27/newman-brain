# CFE MiEspacio harvest via postback pseudo-API (newman-architecture PR #5)

**Summary**: Built and merged the fetch-drain pseudo-API that replays CFE `__doPostBack` as HTTP POSTs to pull historical CFDI XMLs from both Consulta and MiEspacio.
**Tags**: #newman #cfe #scraper #agents
**Created**: 2026-07-07
**Source**: macbook session bd0d0386-7d7d-45fd-b488-05db6356acdf.jsonl, user jesus

---

## Content
- Goal: get a "hidden API" for CFE by replaying `__doPostBack` with cookies + `__VIEWSTATE`, avoiding browser clicks.
- Two harvest depths unified through one `fetchDrain` in `harvest.js`:
  - **Consulta**: login-free, ~6 months, zero risk. Works with RPU only (tested 784220900267, 527051004386 HOTELES YORI); razon social left blank.
  - **MiEspacio**: 2captcha-solved auth, ~30 months, permaban-guarded. Cycle proven: register → drain 30mo → delete, account left clean.
- 2captcha API integrated with headless browser (Playwright/Selenium) for authentication cookie.
- Test RPUs used as CI env secrets on NewmanTech27; 27 JS tests (wiring guards + MiEspacio postback).
- `ci-miespacio.yml`: manual harvest workflow on self-hosted mini runner, concurrency-guarded.
- pg_cron `006` monthly enqueue applied + active (jobid 4).
- Full pipeline on main: pg_cron enqueues stale RPUs → mini `run_loop` claims → `harvest.js` fetch-drains → `enrich.py` reconciles + loads.
- PR #5 merged (squashed to main). Repo: github.com/NewmanTech27/newman-architecture; lopezpalacios added as collaborator.
- Example bills processed: FIDEICOMISO F/1596 (968221200700), Anáhuac (780020900569), HOTELES YORI (527051004386), ETG RESORTS (008970211013).
- Open follow-up: add single-session concurrency guard to `run_loop` so it can't race two MiEspacio registrations on the one CFE account.

## Related Notes
- [[2026-07-14-newman-rebuild-miespacio-phases]]
- [[2026-06-26-cfe-warehouse-schema-supabase]]
