# #141: Executor deploy drift: mini ran a 51-commits-behind CI branch

- State: CLOSED
- Created: 2026-07-14T12:51:00Z  Closed: 2026-07-14T14:41:41Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/141

## Body

Found during the 780020900569 debug: the mini's live executor worktree
(~/newman-rebuild-wt-drive, launchd com.newman.pipeline-endpoint) was parked on
ci/supabase-branch-pipeline, 51 commits behind origin/main — missing #120 (deep-drain
session cycle), #123 (invoice-only grid filter), #129 (re-login before eliminar). That is
the likely root cause of the 1/97 drain + eliminar selector failure + leak.

Fixed operationally 2026-07-14: worktree moved to origin/main (branch `drive`), endpoint
restarted, healthy. Needed structurally: auto-deploy — on merge to main, the mini pulls
and kickstarts the endpoint (mirror of the newman-architecture dual auto-deploy), plus a
version line in /pipeline/health so drift is visible from Supabase.

## Comment by NewmanTech27 (2026-07-14T14:41:40Z)

Shipped (PR #152, prod ffcefad) + installed on the mini: launchd com.newman.pipeline-deploy polls origin/main every 180s, fast-forwards ~/newman-rebuild-wt-drive and kickstarts the endpoint on change, deferring if a harvest_one/consulta_one drive is live. /pipeline/health now exposes the running rev for drift checks.
