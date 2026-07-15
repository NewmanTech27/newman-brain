# #86: Deep-account harvest: WAF mass-rejects fetchDrain + eliminar selector timeout

- State: OPEN
- Created: 2026-07-12T00:30:18Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/86

## Body

## Symptom
A deep account (98 grid rows) failed harvest:
- `fetchDrain` returned **1 file, 127 rejected** (t+0s/1200s) — the Imperva WAF challenged nearly every POST in the drain.
- The page was left in a challenge state, so the subsequent `eliminar` step timed out: `bridge op click failed: Waiting for selector #ctl00_MainContent_btnEliminarServicio failed: 20000ms exceeded` → `RuntimeError` → status `failed`.
- Post-cleanup `safe_cleanup` still removed the service (`verdict=confirmed_removed`) — **no strand** (charter #7 satisfied).

## Context
The #85 `fetchDrain` fix works well on shallow-to-deep accounts (verified 10–28 months across 9 accounts, incl. a 96-row account that returned 70 files cleanly). This 98-row account hit a WAF wall instead — likely accumulated WAF heat from many consecutive harvests in a short window, since `fetchDrain`'s exponential backoff is module-level and escalates across a deep drain.

## Transient vs code
Treating as transient (WAF cool-down) and requeuing with a delay. If it recurs on retry, the fix is a gentler deep-drain: lower `CHUNK` (3→1) and/or a longer inter-chunk gap for very deep grids, plus making the harvest tolerate an eliminar-timeout when the drain already flagged heavy WAF rejection (fall back to safe_cleanup, which already confirms removal, instead of marking `failed`).

## Follow-up idea
When `rejected >> files` on a drain, the harvest should not attempt a same-session eliminar into a WAF challenge — hand off to the fresh-session safe_cleanup directly (it already works here).

## Comment by NewmanTech27 (2026-07-12T01:07:17Z)

## Root cause (deeper than WAF) + code fix

The WAF cool-down fixed the DRAIN (attempt 2 got 103 files / 7 rejected vs 1/127), but the account still failed — because of a **Python finally-block data-loss trap** in `cfe_driver.harvest_rpu`:

- The drain succeeds and the method hits `return res` (res carries the 103 deduped recibos).
- The `finally:` block then calls `self._eliminar(...)`. On this deep account the confirm button `#ctl00_MainContent_btnEliminarServicio` never renders within 20s (WAF-slow post-drain), so the bridge raises a `RuntimeError`. `_eliminar` only catches `DetachedFrameError`, so the `RuntimeError` propagates out of the `finally`.
- In Python, **an exception raised in `finally` replaces the try's return value** — so `return res` (with 103 recibos) is silently discarded and the harvest is marked `failed`. 30+ months of drained history lost every attempt.

The endpoint's fresh-session `safe_cleanup` was still removing the service (`confirmed_removed`) — so no strand — but the data was thrown away.

## Fix
Wrapped the `finally`-block `_eliminar` call in try/except: a raising eliminar now sets `removal_verdict=VERIFY_FAILED` (triggering the existing clean-tab recheck + the endpoint's safe_cleanup for actual removal) instead of destroying the successful `DriveResult`. The drained recibos survive and are stored as `partial`.

Net: deep accounts whose eliminar confirm-button is WAF-slow now keep their full history (stored partial) and still get removed. Requeued id for a clean re-run.
