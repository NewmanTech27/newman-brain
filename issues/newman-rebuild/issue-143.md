# #143: Harvest executor observability: worker logs are HTTP access lines only

- State: OPEN
- Created: 2026-07-14T12:51:03Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/143

## Body

~/Library/Logs/newman-pipeline-endpoint.log contains only
`[pipeline_endpoint] http "POST /newman/pipeline/harvest HTTP/1.1" 200 -` lines. Per-op
detail (login/agregar/grid/drain/eliminar, WAF events, bridge ops) is not written anywhere
on the mini; the only forensic record is pipeline.* last_error truncated to one message.
Debugging 780020900569 required archaeology in the OLD newman-architecture collector log.

Fix: per-run structured log (one file per harvest_job_id or JSONL with rpu/op/duration),
phase timings actually populated (login_s/agregar_s/drain_s/eliminar_s are NULL in
pipeline.timing today), and last_error carrying the failing op + selector.
