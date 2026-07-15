# newman-rebuild codebase graphed with Graphify — full drive→DB write chain traced

**Summary**: Installed Graphify-Labs/graphify on the newman-rebuild repo, built a persistent code graph with rationale nodes, and used it to trace the harvest pipeline end-to-end from scheduler poll to the single `HarvestDB._rpc()` DB choke point.

**Tags**: #newman #rebuild #tooling #graphify #harvest
**Created**: 2026-07-12
**Source**: mini session fd8e6a50-007d-4633-a35d-a8bf279b7081.jsonl, user jesus

---

## Content
- Ask: use https://github.com/Graphify-Labs/graphify to graph the newman-rebuild codebase; short approve-driven session ("yes", "yes", "done").
- Graph output persists at `~/newman-rebuild/graphify-out/`; query with `graphify query "..."` from repo root; after code changes run `graphify update .` (re-extracts changed files only, no LLM cost). Saved to memory.
- Traced the harvest chain via the graph: (1) scheduler poll `main()` → `run_once()` (drive_loop.py:91) claims dispatched RPUs via `rpc_claim_dispatched` (limit 5); (2) `CfeDriver` does browser work and returns a plain-data `DriveResult`; (3) `_apply_drive_to_job()` (drive_loop.py:43) translates it into harvest_job DB events + calls `process_recibo()` (harvest_service.py:42) per recibo → `parse_recibo()` → `reconcile()` → `split_populated()` (recibo_parser.py).
- All writes funnel through one choke point, `HarvestDB._rpc()` (db.py:28), with four callers: `.begin()` → `rpc_harvest_begin` (add service: acquire lock + open job), `.event()` → `rpc_harvest_event` (typed business_error enum or None), `.end()` → `rpc_harvest_end` (remove service / release), plus the parser hand-off.
- Rationale nodes on graph edges capture the why (e.g. "Translate a DriveResult into harvest_job DB events + parser hand-off").

## Related Notes
- [[newman-rebuild-project]]
- [[2026-07-12-rebuild-repo-audit-readme-issues]]
