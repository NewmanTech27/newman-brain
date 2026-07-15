# #50: Harvest endpoint crashes as a background daemon → service left REGISTERED (leak)

- State: CLOSED
- Created: 2026-07-11T00:27:19Z  Closed: 2026-07-11T16:09:40Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/50

## Body

The mini /harvest endpoint runs the drive loop in a background thread. Proven live: it claimed an RPU, opened the job, dispatched, and registered the service — then the puppeteer BRIDGE crashed mid-drive (no bridge.mjs proc survived), the Python harvest thread hung, the job stuck 'running', and the service was LEFT REGISTERED on the shared account with the lock held. The SAME harvest runs fine FOREGROUND/headful (manual runs drain clean). So it's a daemon-context failure (headless/no-display browser, or resource limits in the http.server process).

Fixes:
- Guarantee teardown on ANY drive failure: the CfeDriver finally must eliminar, and the endpoint thread must ALWAYS call rpc_harvest_end (state=failed) + ensure the service is removed, even when the bridge dies. A crash must never strand a service.
- Per-harvest WATCHDOG/timeout in the endpoint: if a drive exceeds N minutes, force eliminar + harvest_end + kill the bridge.
- Run the endpoint under launchd (persistence + restart) with the right browser env (CFE_HEADFUL / a display, or a headless config the frozen stack tolerates). Diagnose why the bridge dies in the daemon.
- Add a startup reaper: on boot, close any 'running' job with no live thread + release its lock + verify-clean the account.

Repro incident handled: account cleaned (service removed), job set failed, lock released. Severity HIGH (charter #7 — a stranded service is an incident).

## Comment by NewmanTech27 (2026-07-11T02:00:53Z)

## Live validation — robustness PROVEN; harvest-completion is the remaining gap

Ran the hardened endpoint against ETG 4× live. Findings:

**Robustness works perfectly (3×):** a hung/slow harvest → hard timeout → safe_cleanup removes the stranded service (confirmed_removed) → rpc_harvest_end(failed) → lock released. Verified 0 open locks + account empty after every failure. The charter-#7 leak risk is closed.

**Root causes found + fixed:**
- Headless was the original crash; **headful requires the mini's GUI/Aqua session** (nohup lacks it → browser hangs; run under launchd LaunchAgent or a GUI-session context → browser launches, children=2).
- The deep drain pulls the **full ~30-month history** and legitimately takes longer than the old 600s.

**Still open — the harvest doesn't COMPLETE via the endpoint:** the MiEspacio drain itself SUCCEEDS through the endpoint (ctx_2 = 13 XML, same as a manual run), but harvest_rpu times out **after** draining — before/at eliminar — so it returns recibos=0 + HARVEST_TIMEOUT even though it drained. Two candidates, need ONE clean instrumented run to distinguish:
  1. HARVEST_TIMEOUT_S=1800 may not have taken on the process (cut at ~600s just as the drain finished, before eliminar).
  2. The endpoint path is genuinely slower than manual (~8min): likely extra login ×6 retries and/or headful-in-nested-subprocess overhead pushing the full flow past budget.

**Next:** (a) log the resolved HARVEST_TIMEOUT_S + per-phase timestamps (consulta done / login done / drain done / eliminar done) in harvest_one so we SEE where the time goes; (b) confirm the env applies; (c) set the timeout to cover the full flow incl. eliminar (~1200-1800s) once (a) shows the real duration. The drain works end-to-end; this is the last mile.

Also surfaced: dispatched-but-failed uploads don't auto-retry (stuck 'dispatched'); rpc_claim_harvest should re-claim a dispatched upload whose job failed (currently needs a manual reset to ocr_done).

## Comment by NewmanTech27 (2026-07-11T07:39:02Z)

## Root cause FOUND (instrumented run) — _drain hangs

Phase timings from a standalone instrumented ETG harvest (headful, GUI session):
```
consulta_latest  74s
_login           20s
_census           1s
_agregar          8s   → registered by +110s
_drain          START at +110s → NEVER RETURNED (still hung at +33min)
```
The whole front is <2 min. **_drain downloads the recibos (13 XMLs landed on disk) and then hangs — it never returns.** So it's NOT a too-short timeout; the deep-drain genuinely stalls (a stuck download-settle / waitForNavigation after the recibos are pulled). This is why every endpoint attempt logged HARVEST_TIMEOUT with recibos=0: harvest_rpu never returns, so the parent's per-recibo events never fire.

The endpoint's subprocess-timeout + safe_cleanup correctly fail-safes this (no leak via the endpoint). But the standalone run had no belt → ETG was left registered (cleaned: confirmed_removed).

**The real fix is INSIDE the drain, not the timeout:** _drain (harvest_service / the browser drain loop) needs a bounded download-settle timeout + a stuck-drain watchdog so it RETURNS the recibos it captured instead of hanging. Note manual runs sometimes complete the drain — it's intermittent (likely WAF-throttled downloads that stall the settle loop). Fix: cap the post-download settle/wait; if no new download for N sec, finalize and return; hard-cap the whole drain. Then the harvest actually SUCCEEDS end-to-end (the 13 recibos were already pulled).

## Comment by NewmanTech27 (2026-07-11T16:09:39Z)

## Fixed — bridge read deadline + safe_cleanup belt

Root cause confirmed: `_Bridge.call()` read the bridge response with a blocking `readline()`; a wedged bridge (live but unresponsive — one run sat 3.5h in `_drain`) blocked it forever, so `harvest_rpu`'s `finally` (which always runs eliminar) never executed → service stranded. A finally can't rescue a hung read.

**Fix (two layers):**
1. Per-call read deadline via `select()` on the bridge stdout (`BRIDGE_CALL_TIMEOUT_S`, default 120s; the drain op gets budget+90s). A silent bridge now raises `BridgeTimeout`; `_drain` catches it → typed `DRAIN_TIMEOUT` → `harvest_rpu` returns cleanly → the finally runs eliminar. In-process, no strand.
2. `safe_cleanup` belt in the pipeline harvest executor: any harvest that isn't a clean confirmed-removed success (or a killed child) triggers a fresh-session eliminar subprocess.

**Verified live:** harvested 8 months → `raw_cfe.mi_espacio`; in-drive eliminar came back VERIFY_FAILED (→ state=partial); safe_cleanup confirmed_removed → **no strand**. Wedged-fake unit test → `BridgeTimeout` in 2.0s; 55 existing drive/census tests still pass.

Commits on `pipeline/executors` (60f0c5a bridge fix, 4d2a58b harvest_one+safe_cleanup). Closing.
