# Mario's savings engine wired toward client.calculo: pg_cron offers per RPU across dev/staging/prod

**Summary**: Audited Mario's downstream CFE-bill→savings work on droplet-jesus, refined a prompt to run his engine (newman-brain/cfe-brain) as a pg_cron job writing per-RPU offers into a proposed `client.calculo` schema, then worked autonomously in loops through dev with GitHub issues on newman-rebuild — including a Norte/Centro/Sur tariff-card parser fix and prod migration promotion.

**Tags**: #newman #rebuild #cfe #supabase #pg_cron #engine #savings
**Created**: 2026-07-15
**Source**: mini session 5c1b2c34-ca8d-4f15-adf8-6e2bf7ae327f.jsonl, user jesus

---

## Content
- Confirmed the three Supabase environments (dev/staging/prod) for newman-rebuild.
- Context: user **mario** on droplet-jesus has been building the downstream processes of CFE bill extraction to calculate savings using **newman-brain or cfe-brain**; session ssh'd in and reviewed his work history and quality.
- Prompt engineering ask: assume the roles of data analyst / electricity-market expert / CFE expert / data engineer; take Mario's engine and create a **pg_cron** that stores its output in a Supabase table; evaluate whether a new schema **client.calculo** is needed to hold one offer per RPU; produce and show an implementation plan — then run it.
- Ran under repeated `/loop` autonomy directives: "work autonomously through every interaction into dev, promote when ready, create GitHub issues on newman-rebuild" and later "assess the issues, generate more, and work autonomously to fix them".
- Data-sufficiency check: assessed whether the XMLs already in `raw_cfe` on dev were enough to drive the calculation; produced a todo plan and filed corresponding GitHub issues.
- Parser gotcha discovered mid-loop: the VDM tariff page renders **3 labeled rate cards (Norte/Centro/Sur)** with distinct Fijo/B/I/P/Distribución but shared Capacidad — the parser had to attribute values per card heading; patched.
- Backfill v2 status validated during a loop iteration; **prod migrations applied**, then env ops run staging-first.

## Related Notes
- [[newman-rebuild-project]]
- [[cfe-brain-vault]]
- [[newman-brain-repo]]
- [[2026-07-12-market-data-migration-plan]]
