# #156: Harvest executor loses partials on timeout → pipeline can never complete a deep account

- State: CLOSED
- Created: 2026-07-15T01:57:20Z  Closed: 2026-07-15T06:43:10Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/156

## Body

## Problem
`harvest_one` emits its result (with the drained recibos) **only at the very end**. The endpoint runs it via `subprocess.run(timeout=HARVEST_TIMEOUT_S)` and **kills the child on TimeoutExpired**, parsing only the last stdout line. So a harvest that exceeds the timeout produces **no result → zero recibos stored**, even though it downloaded many XML to disk.

On a WAF-rate-throttled account a deep account drains at ~0.5 XML/min (#128), so a 30-invoice account needs ~60 min — well past the 25-min `HARVEST_TIMEOUT_S`. Result: the pipeline harvests it, times out, kills it, stores nothing, the reaper requeues it (#129), and it **re-harvests from scratch forever** — never storing. This is exactly why `780020900569` was stuck at **1 invoice** in prod while its true history is **30** (backfilled manually this session via a no-timeout direct run + PR #155's per-batch deadline).

## Fix options
1. **Incremental store (preferred):** have the drain store each batch's recibos as it completes (or emit progress lines the endpoint stores), so a killed/timed-out harvest keeps what it got. Combined with raw_cfe dedup (sha256+(rpu,period)), the reaper-requeued next tick resumes and the account completes over N ticks.
2. **Deep-account timeout:** scale `HARVEST_TIMEOUT_S` by `grid_rows` (like `drain_budget_s`) so a deep drain gets its full ~60-90 min in one tick. Simpler but ties up the single-flight executor for an hour.

Depends on / relates to: #155 (per-batch deadline), #128 (WAF rate), #129 (reaper requeue). Until fixed, deep accounts must be backfilled out-of-band (direct `harvest_one`, no endpoint timeout).

## Comment by NewmanTech27 (2026-07-15T05:46:03Z)

Implemented in PR #155 (commit 1179145): `CfeDriver.on_recibos` callback fires per drain batch; `harvest_one` stores each recibo to `raw_cfe.mi_espacio` as it lands (NR-creds-gated, best-effort). **Validated live on dev**: raw_cfe filled 7→8→10 during the drain while harvest_one was still running → a kill now keeps the partial, and reaper-requeue + sha256/(rpu,period) dedup resumes to completion. Option 1 (incremental store) chosen over raising the timeout.

## Comment by NewmanTech27 (2026-07-15T06:17:04Z)

Fully implemented + validated in PR #155 (commits 1179145 incremental store, 2754c71 resume-skip). Incremental store persists a killed tick's partial; resume-skip (`scan_grid_rows` per-row periods + `CfeDriver.skip_periods` + new `rpc_stored_periods`) makes each reaper-requeued tick drain only unstored months. Validated on dev: fully-stored account → `skip_stored=10 todo=0`, downloaded 0. Migration applied to all 3 envs. The pipeline can now complete deep accounts over ticks without out-of-band runs.

## Comment by NewmanTech27 (2026-07-15T06:33:57Z)

**End-to-end multi-tick resume validated on dev** (the real production behavior, not just the pieces): tick1 harvested then KILLED mid-drain at 7 stored → incremental store preserved the 7; safe_cleanup removed the stranded service (as the endpoint does on timeout). Tick2 re-ran → `skip_stored=7 todo=3` → drained only the 3 remaining months → dev raw_cfe reached **10, harvested, confirmed_removed**. So a deep account that times out completes over reaper-requeued ticks — no lost work, no infinite loop. All three fixes (#128 batch deadline, #156 incremental store + resume-skip) proven end-to-end. PR #155.
