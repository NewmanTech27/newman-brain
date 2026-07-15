# #104: Harvest runtime depends on two unpinned external checkouts and an unlocked flake — environment not reproducible from this repo

- State: OPEN
- Created: 2026-07-12T12:19:38Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/104

## Body

**Severity: p1**

Three unpinned dependencies, none vendored or locked:
- `harvest/cfe_playwright.py:49-51` — default `CFE_BRIDGE_CWD = ~/newman-architecture/agents/cfe-collector/browser`: puppeteer + Chrome resolved from the *frozen* old repo's `node_modules`, no lockfile hash or commit pin recorded here.
- `harvest/golden_engine.py:25` — default engine path `~/cfe-brain/vault/tools` via sys.path hack.
- `pipeline/executors:harvest/flake.nix:7` — `inputs.nixpkgs.url = "nixpkgs"` (registry-indirect) with no `flake.lock` committed on any branch.

A Nix GC, a repo move, or a fresh machine leaves harvest unable to start — the same venv-fragility failure mode already seen on this mini.

**Fix:** commit `flake.lock`; record the newman-architecture commit + a `package-lock.json` hash for the bridge deps; pin `CFE_ENGINE_PATH` to a specific cfe-brain commit.
