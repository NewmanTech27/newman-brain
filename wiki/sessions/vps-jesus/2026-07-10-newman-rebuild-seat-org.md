# newman-rebuild Seat Org: Issue-Driven Seats (data, cto, engine, harvest, crm)

**Summary**: A new GitHub-issue-driven seat org started the clean-room newman-rebuild — migration-0 orchestration schema with SQL-enforced governance, a merge-blocking golden CI reconciling engine.js to the Python anchor, the recibo split parser, the engine wrap decision, and the newman-sso capture.
**Tags**: #newman #newman-rebuild #agent-org #golden-ci #orchestration #sso
**Created**: 2026-07-10
**Source**: newman-vps sessions (consolidated, all "seat_boot.md" runs, user jesus): 94ca575d (data), 3da7c124 (cto), 274c37fb (engine), 6dc5698d (harvest), a849f8fb (crm)

---

## Content
- Pattern: each seat boots from ~/seat_boot.md, takes CEO direction from the latest comment on its GitHub issue(s), posts artifact links back ("Done = artifact link"), and re-reads issues before going idle.
- data (#1): linked newman-rebuild to fresh Supabase project `oioyawhgvazebtarigpc` via `sudo -n vault-env supabase link`; shipped migration-0 — `orchestration.task`/`task_event` with SQL-enforced rules (INT-1 artifact requirement, ≥95 merge bar, CTO-only/non-self verification), RLS ENABLE+FORCE, schema-level default-deny; branch `data/migration-0-orchestration`, unmerged pending CTO. Flags: broken supabase-go binary in the CLI shim (box-local), and `sudo -n vault-env env` prints NEWMAN_API_DSN unredacted.
- cto (#9): built the merge-blocking golden CI that reconciles the DEPLOYED engine.js to the Python peso anchor (vendored engine.js pinned by sha256, JS reconciliation harness → 18/18 peso-exact) plus the negative test: mutate FC 0.57→0.55 (the umbral divisor) and prove CI goes red.
- engine (#7): wrap decision filed (cfe-brain@abef3a3): vendor engine.js pinned to a commit SHA with CI-enforced checksum rather than live cross-project edge-fn calls (latency, GATE-0 decommission coupling, CI determinism); reconciliation target is the fixed golden system 194.48 kWp / 2940 kWh, not the NPV sweep; dependency chain: #9 gates merges, recibo horaria capture gates meaningful output, P1 schema (#2/#3) gates landing.
- harvest (#5, linchpin for #7): built the recibo-PDF base/intermedio/punta split parser first; then #4 (OCR accuracy measurement) with a local uncommitted ground-truth fixture, OpenRouter key never printed.
- crm (#11): captured the box-only ~/newman-sso (16 files: validator, login page, nginx confs, systemd unit, cloudflared config, scripts) into NewmanTech27/newman-rebuild branch `capture/newman-sso-scaffold` commit b62e550; env secrets redacted to name+length (anon key deliberately left — it's public); `hd`-claim bug left untouched per direction; PAT lacked pull-requests scope so branch pushed without PR; shared-clone hazard dodged via isolated worktree ~/wt-crm-newman-sso.

## Related Notes
- [[2026-07-10-flock-overnight-golden-proof]]
- [[newman-rebuild-project]]
- [[newman-orchestration-schema]]
