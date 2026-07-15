# #122: Benchmark CFE_DRAIN_PARALLEL: is the XML throttle per-session or per-IP?

- State: OPEN
- Created: 2026-07-13T00:20:37Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/122

## Body

PR #120 adds an opt-in `CFE_DRAIN_PARALLEL=N` path that fans the drain across N concurrent fresh browser sessions (each its own cookie jar / 4-download quota). Sequential incognito-per-batch is proven (8→81) but slow (~one captcha login per 4 rows; ~13 min for 92 rows).

Parallel would cut deep accounts to a few minutes **iff** the throttle is per-session. If CFE throttles per-IP, concurrent sessions share one quota and it clips. Untested live.

Task: run `CFE_DRAIN_PARALLEL=4` on a deep RPU, measure wall-clock + captured/expected, and confirm no per-IP clipping / WAF escalation. If per-IP, keep default 1 and document.
