# #108: .gitignore is one line; untracked .claude/ worktree with a full repo copy sits permanently dirty in the working tree

- State: OPEN
- Created: 2026-07-12T12:19:45Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/108

## Body

**Severity: p2**

`.gitignore` contains only `harvest/__pycache__/`. `git status` shows untracked `.claude/` containing `worktrees/harvest-telemetry-report/` — a complete second copy of the repo (login page, migrations, everything). Every `git status` is dirty, grep/tooling double-counts files, and a stray `git add -A` would commit a stale snapshot of the whole codebase.

**Fix:** add `.claude/`, `**/__pycache__/`, `.env*`, `*.bak` to `.gitignore`; relocate agent worktrees outside the repo root.
