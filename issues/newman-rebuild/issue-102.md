# #102: Mini executor launchd job runs from a disposable git worktree with no restart runbook — reboot recovery is one rm -rf from silent outage

- State: OPEN
- Created: 2026-07-12T12:19:35Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/102

## Body

**Severity: p1**

`pipeline/executors:harvest/deploy/com.newman.pipeline-endpoint.plist` (ProgramArguments) executes `/Users/jesuslopez/newman-rebuild-wt-drive/harvest/run-pipeline-endpoint.sh`, and that script `cd`s into `$HOME/newman-rebuild-wt-drive/harvest` — a git *worktree*, not a stable checkout. `git worktree prune`, a branch switch, or a machine migration kills the :8791 endpoint; `RunAtLoad`/`KeepAlive` then loop-crashes silently (exit 1 on the missing cd). The script also requires `~/.newman-pipeline.env` and the harvest flake devshell with no preflight check.

No restart-after-reboot runbook exists for the mini on any branch (the droplet has newman-sso/INSTALL.md + rollback; the mini has nothing).

**Fix:** deploy from a stable path, add a preflight check for the env file + devshell, and commit an install/verify runbook (INSTALL.md model) on the branch that ships the migrations.
