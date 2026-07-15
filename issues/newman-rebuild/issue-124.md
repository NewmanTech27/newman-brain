# #124: Pipeline: full-history batch run (process all pipeline.twilio rows end-to-end)

- State: OPEN
- Created: 2026-07-13T05:15:00Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/124

## Body

Validate/operate the pipeline over the **whole twilio backlog** rather than one seeded row: every `pipeline.twilio` row flows extract → consulta → harvest (incognito drain) → `raw_cfe`, with the per-RPU dedup guards (#92/#114) preventing redundant live-CFE drives.

Notes:
- Live-CFE heavy: N distinct RPUs = N consulta + N harvests (~7-13 min each). Must respect WAF pacing (#119) and the F3 cool-down; likely serialize consulta/harvest (parallelism=1) across RPUs.
- Run in develop first (mini repointed), verify `raw_cfe.invoices` fills per RPU, then promote.
- Depends on the grid-level invoice filter (above) to keep each RPU's drive fast.
