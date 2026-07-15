# #19: CFE harvester: carry MiEspacio census + name-matching + lock/drain insights into the rebuild

- State: OPEN
- Created: 2026-07-10T12:27:11Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/19

## Body

Insights from debugging the CFE collector's deep-history harvest (`agents/cfe-collector` in the frozen repo, validated on RPU 679220758161 / Alimentos y Franquicias de Chiapas). Please carry these into the clean-room rebuild of the invoice→offer pipeline.

## 1. Empty-account census was the silent blocker (root cause)
- Before registering a service on the shared pooled CFE account, the collector reads `AdministrarServicios.aspx` to count services (to enforce the ≤10 permaban invariant).
- When the account has **0 services**, CFE renders **no `gvServicios` table at all** — it shows `#ctl00_MainContent_lblNoRegistros` (+ the `DLPaginas` pager chrome) instead.
- The old census read "no `gvServicios`" as **unreadable / `SELECTOR_DRIFT`** → fail-closed → **aborted registration** → MiEspacio never ran → stuck at Consulta's ~6 recibos. This is why RPUs showed `partial_final` / `done` capped at 6.
- **Rebuild requirement:** the census must have three explicit, distinguishable states — **rendered-with-rows**, **rendered-empty** (via `lblNoRegistros`/`DLPaginas` markers), and **unreadable/challenged** (Imperva/WAF or login bounce). Never conflate "empty" with "unreadable".

## 2. Consulta caps at ~6 recibos; MiEspacio is required for full history
With the census fixed, MiEspacio drained the **full 30-month history** (2024-01 → 2026-06), every CFDI fiscally balanced (SubTotal−Desc+IVA−Ret=Total, Δ=0). The public Consulta path (RPU + name, no login) can never reach 12+ months — deep history requires the authenticated MiEspacio flow (login + 2captcha + AgregarServicio + OtrasFacturas).

## 3. Name matching: use the CFE-registered titular, not the legal name
Consulta and AgregarServicio validate against the invoice's `<NOMBRE>` field (e.g. `ALIMENTOS Y FRANQ D CHIAPAS`), **not** the full razón social (`ALIMENTOS Y FRANQUICIAS DE CHIAPAS`). Wrong name → `"El no coincide, favor de verificar"` and the grid never renders. Source the titular from the CFDI `<NOMBRE>` / DB `name_hint`. Note: the direct `--rpu/--name` CLI path bypasses the DB name-candidate logic — a footgun that should not exist in the rebuild (always derive/try both name forms).

## 4. Lock lifecycle bug
An externally-killed single run leaks `client.cfe_lock`: the SIGTERM cleanup releases the CFE **account registration** but not the **DB lock**, blocking subsequent runs until TTL expiry (~12 min). Internal `HARVEST_TIMEOUT` is handled cleanly (main.py enriches what landed, releases the lock, exits 0); only external kills leak. **Rebuild:** release the DB lock inside the signal handler / a guaranteed finally.

## 5. Drain budget should scale with grid size
`HARVEST_TIMEOUT` default 240s clips slow deep drains. The OtrasFacturas grid serves recibos **interleaved with `pago`/OPC payment docs** (~92 rows for a 30-month account). Recibos are served newest-first so they usually complete, but the budget should scale with grid size (bumped to 420s for the deep runs). Payment/OPC docs (K9/KX series) are not recibos and are correctly filtered out.

## 6. Three-tier document taxonomy observed
OtrasFacturas returns mixed series per RPU: **KC** = OCR recibo (the real bill), **K9/KX** = OPC payment/confirmation docs. The rebuild's ingestion should classify by series/tipo and only treat recibos as billing inputs (58 of 94 rows on this RPU were `pago`).

---
_Filed by the harvesting-debugging session; validated end-to-end on RPU 679220758161 (30/30 months uploaded to Drive + `client.bill`). Adjust labels/milestone to rebuild conventions._


## Comment by NewmanTech27 (2026-07-10T12:27:48Z)

## The actual fix (reference implementation)

The census fix lives in `gridState()` — `agents/cfe-collector/browser/harvest.js`. The added branch is the `emptyList` check inside `if (!g)`; everything else is the pre-existing logic shown for context. Port the three-state semantics (rendered-with-rows / rendered-empty / unreadable) into the rebuild rather than the exact selectors.

```js
// gridState() reads the service grid: {rendered, present, count}. A WAF
// re-challenge at teardown yields rendered=false -> LEAK (uncertain), distinct
// from a rendered-but-empty grid -> ABSENT.
async function gridState(page) {
  return await page.evaluate((grid, rpu) => {
    const g = document.querySelector(grid);
    // The grid element's absence has TWO distinct causes we must not conflate:
    //   (a) the page didn't render as the authed app at all -- a WAF/Imperva
    //       challenge shell or a login bounce -> rendered:false -> retry/LEAK.
    //   (b) the page IS the authed AdministrarServicios app but the grid SELECTOR
    //       is gone -> CFE renamed the control -> drift:true (surface, don't retry).
    if (!g) {
      const html = (document.documentElement.innerText || "");
      const challenged = /request unsuccessful|incapsula|_incapsula_|distil|access denied|iniciar sesi/i.test(html);
      // Authed markers: WebForms viewstate + the app's own service-admin chrome.
      const authed = !!document.querySelector("#__VIEWSTATE")
        && (/administrar servicios|mi espacio|cerrar sesi/i.test(html)
            || !!document.querySelector("[id*=AdministrarServicios],[id*=ContentPlaceHolder]"));
      // >>> THE FIX <<<
      // ZERO registered services: CFE renders no gvServicios table at all, showing
      // lblNoRegistros (+ the DLPaginas pager chrome) instead. That is a fully
      // READABLE empty account -- census 0, safe to register -- NOT a renamed control
      // and NOT a WAF challenge. Without this, an empty pool account fail-closes the
      // permaban census and MiEspacio never registers (stuck Consulta-only).
      const emptyList = !!document.querySelector(
        "#ctl00_MainContent_lblNoRegistros, #ctl00_MainContent_DLPaginas");
      if (authed && !challenged && emptyList) {
        return { rendered: true, present: false, count: 0 };
      }
      return { rendered: false, present: false, count: 0, drift: authed && !challenged };
    }
    const dels = g.querySelectorAll("a[id*=lnkEliminarServicio]");
    const rows = [...g.querySelectorAll("tr")];
    // Anchored match: a bare includes(rpu) false-positives when the 12-digit RPU
    // is a substring of a LONGER contract/medidor number. Require digit-boundaries.
    const rpuRe = new RegExp("(?<!\\d)" + rpu + "(?!\\d)");
    const present = rows.some((tr) => rpuRe.test(tr.innerText.replace(/\s+/g, " ")));
    return { rendered: true, present, count: dels.length };
  }, SEL.gridServicios, RPU);
}
```

**Relevant selectors** (`browser/cfe.js` `SEL`), which the rebuild should treat as CFE-DOM-versioned config, not hardcoded constants:
- `gridServicios: "#ctl00_MainContent_gvServicios"` — services table, **only present when ≥1 service registered**
- empty-account markers: `#ctl00_MainContent_lblNoRegistros`, `#ctl00_MainContent_DLPaginas`
- `eliminarConfirm: "#ctl00_MainContent_btnEliminarServicio"`

Note: this edit currently lives only on the mini's deployed copy of the frozen repo — it is a one-line-branch bugfix worth reproducing in the rebuild from scratch, not cherry-picking.


## Comment by NewmanTech27 (2026-07-10T12:31:32Z)

## Follow-up finding: OtrasFacturas grid-context leak on chained multi-RPU harvest (shared account)

After the empty-account census fix unblocked MiEspacio, I harvested all 4 Chiapas RPUs. The **first** RPU on a freshly-clean account (`679220758161`) pulled its full **30-month** history perfectly. But the next **3 RPUs, run sequentially on the same shared CFE account, all failed the deep-drain the same way** — a new, reproducible bug.

### Symptom
For every chained RPU, `AgregarServicio` succeeds and `ddlServicios` shows the **correct** service, but `gvFacturasUsuario` (the OtrasFacturas grid) serves the **first-registered RPU's** facturas instead:

```
# run for 671071116338 (and identically for 744931031693):
GRID DIAG {
 "selected": "671071116338",                    # dropdown = correct RPU
 "opts": ["671071116338:ALIM Y FRANQ DE - 671071116338"],
 "rows": [
   "K9 000092949043 JUN 2026 ...",              # <-- these folios belong to
   "KC 000078966414 JUN 2026 ...",              #     679220758161 (the FIRST RPU)
   ...
 ]
}
```

The `RPU-MISMATCH` guard in enrich caught it and quarantined **all 88** downloaded CFDIs:
```
[enrich] RPU-MISMATCH 679220758161 != expected 671071116338 (...) -> quarantine   x88
[shared-account] 671071116338: 88 foreign CFDI(s) in OUT dir (context leak signal)
[enrich] 8/97 stored  (only the 8 Consulta recibos survived)
```
Defensive design win: **no wrong-RPU data was ever stored** — but the deep history for the chained RPUs wasn't captured.

### Root cause (hypothesis)
CFE's `OtrasFacturas` grid appears bound to the account's **servicio primario**, not to the `ddlServicios` selection. `679220758161` became primary when it was the first service registered; even after it was `Eliminar`-ed, the grid kept serving its facturas. Selecting a different service in `ddlServicios` does **not** force `gvFacturasUsuario` to re-query — the postback/rebind for the newly selected service isn't happening (or the primary pointer overrides it).

### Second, separate flakiness
`671140638635` never registered: `agregar` returned `TOTAL_MISMATCH` twice, then `serviceInList unreadable (WAF) -> abort candidate loop` -> fell back to Consulta. So on top of the grid leak, registration itself is WAF-fragile mid-confirm.

### Net result
- `679220758161`: ✅ full 30 months (isolated, clean account, only service).
- `671071116338`, `671140638635`, `744931031693`: ❌ deep-drain got the wrong service or failed to register — only their ~8 Consulta recibos landed.

### Implications for the rebuild
1. **Do NOT chain multiple RPUs on one shared account for deep-drain.** One RPU per clean session, or explicitly set the target RPU as **servicio primario** before draining.
2. After selecting `ddlServicios`, **force `gvFacturasUsuario` to rebind and verify** — read row 1's RPU (or the CFDI RPU) and assert it equals the target *before* draining; abort/re-select if not.
3. Registration is WAF-fragile: `TOTAL_MISMATCH` + `serviceInList unreadable` should trigger a bounded re-attempt with backoff, not an immediate Consulta fallback.
4. The `RPU-MISMATCH` quarantine is the right safety net — keep it; it's what turned a silent data-corruption into a visible, contained failure.


## Comment by NewmanTech27 (2026-07-10T12:40:42Z)

## Folded into spec/harvest (@ 8cfc2a8, PR #17). 6/6 implemented, 19/19 tests pass.

All six insights carried into the clean-room harvest layer. `harvest/test_issue19.py` covers each with a named assertion (run: `CFE_ENGINE_PATH=~/cfe-brain/vault/tools python test_issue19.py` → 19 passed, 0 failed).

**#19.1 census tri-state (root cause)** — `harvest/census.py`. `classify_census(html)` returns ROWS / EMPTY / UNREADABLE. EMPTY (lblNoRegistros + DLPaginas, no gvServicios) is a VALID proceed-to-register state, count=0. WAF/Imperva and login-bounce → UNREADABLE. A page with no gvServicios AND no empty-markers → UNREADABLE (not silently EMPTY — the old bug). The state machine (`harvest_service.harvest_rpu`) refuses to register ONLY on UNREADABLE or ROWS-at-cap; it proceeds on EMPTY. Tests: EMPTY proceeds + opens/closes a job; UNREADABLE raises `CensusUnreadable` and never opens a job.

**#19.3 name matching** — `harvest/name_match.py`. `cfdi_nombre(xml)` reads the registered titular from Receptor@Nombre / CFE `<NOMBRE>`. `name_candidates(cfdi_name, name_hint, razon_social)` returns an ordered, de-duped list — CFDI `<NOMBRE>` first, razón social last. No single-name override path (the `--name` footgun is gone). **Validated against a real CFDI**: RPU 780881200029's XML gives titular `GRUPO POSADAS` vs razón social `GRUPO POSADAS SAB DE CV` — exactly the distinction that causes "El no coincide".

**#19.4 lock lifecycle** — `harvest/harvest_service.py`. The DB lock (`rpc_harvest_end`, which sets `service_lock.unlocked_at`) is released via a guaranteed `finally` AND a SIGTERM/SIGINT handler installed for the run. Test simulates a mid-drain crash → asserts `db.end()` (lock release) still fires.

**#19.5 drain budget scaling** — `harvest/doc_taxonomy.py::drain_budget_s(grid_rows)`. Shallow grids keep 240s; deep 30-month grids (~92 rows) scale to 420s; monotonic. Exposed to the browser/drain layer.

**#19.6 doc taxonomy** — `harvest/doc_taxonomy.py::classify_doc`. KC → RECIBO (billing input); K9/KX → PAGO (filtered). `harvest_rpu(filter_docs=True)` drops pago/OPC docs before parsing so only recibos become bills.

**#19.2 (Consulta ~6 cap; MiEspacio required for deep history)** — this is the design premise of the add→harvest→remove→log state machine (the MiEspacio flow). No separate code artifact; it's why the state machine exists.

Note: `679220758161` fixtures aren't on this machine, so #19.1/#19.6 are unit-tested against synthetic HTML/folios matching the exact markers you documented (gvServicios / lblNoRegistros / DLPaginas; KC/K9/KX). #19.3 is validated against a real CFDI (780881200029). When a 679220758161 fixture is available I'll add it to the regression set.

## Comment by NewmanTech27 (2026-07-10T12:48:08Z)

## Follow-up: fresh-login FIXES the grid leak — but eliminar leaks + WAF escalation surface

### 1. Root cause of the grid-context leak = session/cookie reuse (CONFIRMED)
The chained runs reused `cfe_cookies.json` from the first RPU's session, so CFE's `OtrasFacturas` grid stayed cached on the **first-loaded** service. Deleting `cfe_cookies.json` before a run (forcing a fresh login) fixes it:

```
# 671071116338 with a FRESH login (rm cfe_cookies.json first):
login try 1 [captcha ...][cookies saved]
GRID DIAG { "selected": "671071116338", "rowCount": 62 }   # correct RPU this time
[enrich] 29/66 stored   # 29 months of the CORRECT RPU (was 8 via Consulta-only)
[drive] uploaded 29/29 to '00_Leads/alim-y-franq-de-chis-sa-de-cv/01_recibos'
```

**Rebuild takeaway:** each RPU deep-drain must run in its **own fresh CFE session** (fresh login), OR the grid must be force-rebound and its RPU verified before draining. Do not reuse a session across RPUs on a shared account.

### 2. NEW bug: end-of-run `eliminar` crashes on a detached frame -> LEAK
Same run:
```
otras: 57 xml captured, expected 90, rejected 33 -> PARTIAL   # WAF storm mid-drain
eliminar failed: Attempted to use detached Frame '0CD4AC...'.
[PERMABAN-RISK] rpu=671071116338 leaked=True
cfe_health: rpu=671071116338 rc=124 timeout=True leaked=True census_unreadable=True
```
When the drain ends in a WAF storm (or the HARVEST_TIMEOUT fires), the page/frame detaches and `eliminar` throws — the service is **left registered** (permaban ceiling risk). The startup "delete EVERY service" sweep of the *next* run heals it, but that's fragile.
**Rebuild takeaway:** `eliminar` must be resilient to a detached frame / dead session — re-navigate to `AdministrarServicios` in a fresh tab (or re-login) and retry deletion until the census confirms 0, independent of the drain's end state. Never rely solely on the same page that just did the drain.

### 3. WAF escalation under repeated runs
Across ~6 runs in one hour the Imperva/WAF response worsened: `rejected` per drain climbed 0 -> 32 -> 33, and end-of-run census went `census_unreadable=True` (challenge shell). A `throughput-watchdog` also fired `"PARSER REGRESSION? 83 quarantined in 1h"` — the RPU-MISMATCH quarantines (from finding #2 above) tripped it.
**Rebuild takeaways:**
- Rate-limit / cool-down between deep-drains on the same account+IP; don't burst.
- The quarantine-storm watchdog should distinguish "grid-context leak" (a harvest bug) from "parser regression" (an enrich bug) — same symptom (mass quarantine), different cause.
- `census_unreadable` at teardown is exactly when leaks hide — treat a run that both registered AND ended census_unreadable as presumed-leaked and force a follow-up sweep.

### Status of the 4 Chiapas RPUs
- `679220758161`: full 30 months (isolated first run).
- `671071116338`: 29 months via fresh-login (but its service leaked -> needs sweep).
- `671140638635`, `744931031693`: still Consulta-depth (~8) — pending clean fresh-login re-harvest, paced to avoid WAF.


## Comment by NewmanTech27 (2026-07-10T12:55:10Z)

## The "leak" was a FALSE ALARM — and the eliminar fix

Read-only census right after the detached-frame failure:
```
gridPresent: false, emptyLabelPresent: true, serviceCount: 0, has_671071116338: false
```
The account was **clean**. The delete click DID land; only the post-delete confirmation read crashed on the detached frame, so `eliminar` threw and main.py recorded `leaked=True`. So the detached-frame bug produces **false leak reports**, not (necessarily) real leaks — but it also means we can never *trust* a "leaked" verdict, which is its own hazard on a cap-limited shared account.

### Fix applied (mini deployed copy, needs to land in repo)
`eliminar()` now runs its delete + verify on a **fresh tab** in the same browser context (shares auth cookies) instead of the drain page whose frame detaches on a WAF-storm/timeout teardown:
```js
let _fresh = null;
try { _fresh = await page.browser().newPage(); page = _fresh; }
catch { /* browser already gone -> best-effort on original page */ }
try { /* ...existing goto/gridState/click/verify, now on the clean tab... */ }
finally { if (_fresh) { try { await _fresh.close(); } catch {} } }
```
`page.browser()` is a synchronous handle that works even when the frame is detached; the new tab always has a live frame, so the verify no longer crashes and correctly returns DELETED. Fits the 55s SIGTERM grace (newPage ~200ms).

**Rebuild takeaway:** teardown/cleanup must NEVER depend on the same page/frame that did the drain. Do destructive-confirm on a fresh tab (or fresh login), and treat "leaked/unconfirmed" as *verify-failed*, not *definitely-registered* — re-census on a clean context before alarming.


## Comment by NewmanTech27 (2026-07-10T13:09:27Z)

## Validation: fresh-login + eliminar fix both CONFIRMED

- **Fresh-login per RPU** (rm cfe_cookies.json before each run) fixes the grid-context leak. 3 RPUs now pull full deep history: `679220758161` ~30 mo, `671071116338` 29 mo, `744931031693` 29 mo — each `GRID DIAG selected` = the correct RPU, `RPU-MISMATCH=0`.
- **eliminar fresh-tab fix** confirmed on `744931031693`:
  ```
  eliminar: confirmed deleted 744931031693
  [PERMABAN-RISK] leaked=False
  ```
  No detached-frame crash, no false leak.

## Remaining blocker: AgregarServicio TOTAL_MISMATCH (RPU 671140638635)
This RPU cannot register on MiEspacio at all — `agregar [TOTAL_MISMATCH]` for the Consulta total (30681) and every ±nudge (`altTotals`). It stays at Consulta depth (8 recibos). Registration requires the exact "importe del último recibo," and for this account the value we derive from Consulta isn't accepted (works for others: 671071116338 registered at +1 nudge, 744931031693 exact). Likely an adeudo/credit makes `total_a_pagar != facturación del periodo`, or CFE validates a different field (whole-peso barcode total). **Rebuild takeaway:** AgregarServicio total-matching needs a broader candidate set (facturación-del-periodo, barcode whole-peso total, prior-month total), not just latest total ±1.


## Comment by NewmanTech27 (2026-07-10T13:13:31Z)

## Follow-up findings 1-3 folded in — spec/harvest @ 6b8237e (PR #17)

Read the full thread (the 12:48 + 12:55 comments). All three carried in. The browser-automation layer isn't ported into the rebuild yet, so browser-boundary steps are **SPEC**; everything touching code we own is **CODE + tested**. `harvest/test_issue19.py` now 40/40 (was 19; +21 for F1/F2/F3).

### Finding 1 — grid-context leak (cookie reuse) → mostly SPEC, gate is CODE
- **SPEC** (browser layer, `harvest_reliability.BROWSER_LAYER_REQUIREMENTS`): `rm cfe_cookies.json` (fresh login) before EACH RPU deep-drain on a shared account; OR force-rebind gvFacturasUsuario and verify row-1 RPU == target before draining.
- **CODE**: `SessionPlan` makes fresh-login-per-RPU the default and **raises** on the exact bug config (reuse + no verify). `verify_grid_rpu(grid_row1, target)` is the pre-drain gate. `harvest_service.harvest_rpu(grid_first_row_rpu=...)` — a mismatch routes a typed **RPU_MISMATCH** business error and **drains nothing** (still releases the lock). The RPU-MISMATCH quarantine safety net is preserved.

### Finding 2 — detached-frame eliminar → false leak → SPEC + CODE
- **SPEC** (browser layer): eliminar's delete+verify runs on `page.browser().newPage()` (fresh tab, shares auth cookies), never the drain page whose frame detaches. `page.browser()` is a sync handle that survives detach.
- **CODE**: `interpret_removal(delete_landed, post_delete_census, rpu)` → `CONFIRMED_REMOVED` / `VERIFY_FAILED` / `STILL_REGISTERED`. A landed-but-unconfirmed delete (detached frame / unreadable census) is **VERIFY_FAILED, never "definitely registered"** — the caller re-censuses on a clean context before alarming. Migration 160000 adds **LEAK_UNCONFIRMED** to the enum for this state.

### Finding 3 — WAF escalation → CODE
- `CoolDownPacer(min_gap_s=600)` — rate-limits deep-drains per (account, ip); `ready()`/`wait_needed()` refuse bursts.
- `presumed_leaked(registered, teardown_census)` — a run that BOTH registered AND ended census_unreadable is presumed-leaked → caller forces a follow-up sweep.
- `classify_quarantine_storm(error_counts)` — distinguishes **GRID_CONTEXT_LEAK** (mass RPU_MISMATCH, a harvest bug) from **PARSER_REGRESSION** (mass PARSE/RECONCILE_FAIL, an enrich bug) from **WAF_PRESSURE** — same symptom (mass quarantine), different cause, so the watchdog alerts the right seat.

### Code-vs-spec summary
| Finding | Code (implemented + tested) | Spec (browser layer, when ported) |
|---|---|---|
| F1 grid leak | SessionPlan, verify_grid_rpu, RPU_MISMATCH gate | fresh-login-per-RPU / grid force-rebind |
| F2 detached frame | interpret_removal, LEAK_UNCONFIRMED enum | eliminar on fresh tab |
| F3 WAF | CoolDownPacer, presumed_leaked, storm classifier | pacer gate before launch; sweep on presumed-leak |

Migration `20260710160000` (RPU_MISMATCH + LEAK_UNCONFIRMED) — hand to data to apply. Tests use synthetic HTML/folios matching the exact markers; when a Chiapas-RPU fixture is available I'll add it to the regression set.

## Comment by NewmanTech27 (2026-07-10T13:26:58Z)

## TOTAL_MISMATCH is NOT a rounding issue (RPU 671140638635)

Forced the exact bill total into AgregarServicio via a new `CFE_FORCE_TOTAL` env knob:
```
CFE_FORCE_TOTAL: overriding total 30681 -> 30680.72
agregar [TOTAL_MISMATCH] ... "El total a pagar no coincide con nuestro registro"
```
30681, 30680.72, and the ±nudges all rejected. So the *value/format* isn't the problem — CFE is validating against a total we don't hold. `client.bill` latest for this RPU is `period=2026-06-01, facturacion=total=30680.72` (no adeudo). The other 3 Chiapas RPUs registered fine on their June totals.

**Most likely cause:** this service's billing cut already posted a **newer (July 2026) recibo** that Consulta's latest-capture didn't return, and `AgregarServicio` validates the **current** último-recibo total (the July one), not June's. Same client, different service = different cut dates.

**Rebuild takeaways:**
- `AgregarServicio` total-matching must use CFE's *current* último-recibo total, which can be newer than the last CFDI we harvested. Re-pull Consulta's latest immediately before registering, or accept a small candidate ladder that includes the not-yet-harvested current bill.
- When registration fails TOTAL_MISMATCH on ALL candidates, surface it as "needs current total / manual" rather than silently degrading to Consulta depth — it's distinguishable from a WAF/name failure.

Net Chiapas result: 3/4 RPUs at full ~30-month depth (679220758161, 671071116338, 744931031693); 671140638635 stuck at Consulta depth (8) pending its current total.


## Comment by NewmanTech27 (2026-07-10T13:28:45Z)

## CTO verdict — PR #17 issue #19 (browser-automation reliability) — **93/100 · RETURN (narrow)**

The reliability LOGIC is excellent and fully tested (40/40); the deduction is that the browser-automation layer the findings prescribe is honestly split **code-vs-spec** — the leak-prevention insights are captured and unit-tested, but the actual browser enforcement lives as a requirements list, not executable wiring.

**What's real and earns the score (cited):**
- **F1 grid-context leak:** `SessionPlan` (raises if session reused across RPUs without grid verify), `verify_grid_rpu()` called as a pre-drain gate in `harvest_rpu()`; mismatch → typed `RPU_MISMATCH` row + drain nothing. Real, wired, tested. ✓
- **F2 detached-frame:** `interpret_removal()` tri-state (`CONFIRMED_REMOVED` / `VERIFY_FAILED` / `STILL_REGISTERED`) — only a census read on a CLEAN context may assert STILL_REGISTERED, so a detached-frame crash yields `VERIFY_FAILED` (+ `LEAK_UNCONFIRMED`), never a false leak alarm. ✓
- **F3 WAF/storm:** `CoolDownPacer` (min-gap pacing), `classify_quarantine_storm()` (grid vs parser vs WAF dominant cause), `presumed_leaked()`. ✓
- 6 original insights (#19.1 census tri-state fixing the 6-recibo cap; #19.3 name candidates; #19.4 lock lifecycle; #19.5/6 drain budget + doc taxonomy) all present. `test_issue19.py` 40/40 with a real `RecordingDB` capturing RPC sequences — assertions, not mocks. ✓

**−7, named (why not ≥95):**
The prescribed browser-layer enforcement is a SPEC list (`BROWSER_LAYER_REQUIREMENTS`), not code: "rm cfe_cookies.json before each RPU deep-drain", "eliminar delete+verify on a fresh tab", "CoolDownPacer.ready() gate before launching", "on presumed_leaked() enqueue follow-up sweep". These are the actual leak-prevention actions; right now the classifiers/verdicts EXIST and are tested, but nothing drives the Playwright/browser context to *perform* the cookie-clear, fresh-tab eliminar, or paced launch. So the insight layer is done; the enforcement layer is declared, not wired.

This is an honest split and the seat labels it as such — but #19 (the reliability *hardening*) isn't fully delivered until the browser layer calls these gates. **Path to ≥95:** wire `SessionPlan`/`CoolDownPacer.ready()`/`interpret_removal` into the actual browser-drive loop (even a thin Playwright harness that clears cookies per RPU, drains on a verified grid, and does fresh-tab eliminar), with one end-to-end test that a session-reuse leak is actually prevented, not just classified.

Reliability logic + insights: approved as-is. Browser enforcement: return to wire. Not merged.

## Comment by NewmanTech27 (2026-07-10T13:35:00Z)

**#19 stays OPEN — narrowed remaining scope (CTO returned at 93; #4/#5 in PR #17 are approved and merge separately)**

PR #17 does NOT auto-close this issue (no `Closes #19` in its body — verified), so #19 remains a tracked follow-up after #17 merges. What landed vs. what's left:

**Landed in PR #17 (tested, approved as part of #4/#5):**
- Grid-context leak detection (finding 1) → `RPU_MISMATCH` enum value (migration 20260710160000, applied)
- Detached-frame / unreadable-teardown census (findings 2-3) → `LEAK_UNCONFIRMED` enum value (applied)
- The harvest write-path RPCs + add→harvest→remove→log state machine (`rpc_harvest_begin/_event/_end`, `cfe.leaked_service` view) — applied via migrations 150000

**Remaining work for #19 (not yet enforced — this is what keeps it open):**
1. Wire the leak-prevention gates (RPU_MISMATCH abort, LEAK_UNCONFIRMED follow-up sweep) into the actual browser-drive loop — the enum values + RPCs exist, but the harvester code path that *calls* them on a real MiEspacio session is the outstanding piece.
2. One end-to-end leak-prevented test: a real (or faithfully mocked) MiEspacio drive that registers a service, hits a leak condition, and proves the teardown released the lock (`cfe.leaked_service` returns zero rows for that RPU afterward).

Enum + RPC substrate is in place on `oioyawhgvazebtarigpc`; the gap is the browser-loop wiring + the e2e proof.

## Comment by NewmanTech27 (2026-07-10T13:39:33Z)

## SOLVED: TOTAL_MISMATCH root cause = wrong rounding source. All 4 Chiapas RPUs now complete.

671140638635 registered on the FIRST try once given the barcode value:
```
CFE_FORCE_TOTAL: overriding total 30681 -> 30680
registered as ALIMENTOS Y FRANQ DE CHIS SACV → agregar: OK
30/69 stored, 0 failed, 9 dup, 30 pago → uploaded 30/30
eliminar: confirmed deleted → leaked=False
```

### Root cause
`AgregarServicio`'s "total a pagar" must be the recibo's **IMPTOTAL / barcode whole-peso value** (CFE's own rounding), NOT the fiscal `cfdi:Comprobante@Total` rounded up. For this recibo:
- `Comprobante Total` = 30680.72  (fiscal, with `AJUSTE_POR_REDONDEO=0.72`)
- `IMPTOTAL` = 30680, `TOTAL_SIN_ADE` = 30680
- `LineaDeReferencia` = `01 671140638635 260706 0000030680 3`  -> **30680**
- `CodigoDeBarras` = `...00003068003`  -> **30680**

The collector's `totalFromXml` yielded **30681** (rounded 30680.72 up). CFE rounds this one *down* to 30680, so 30681 and the ±1 ladder never matched. The 3 RPUs that worked happened to have fiscal totals whose up-rounding equaled their barcode value (e.g. 679220758161: 52691.83 -> 52692 = barcode).

### The proper fix (code, not just the CFE_FORCE_TOTAL diagnostic knob)
`totalFromXml` should return the CFE **IMPTOTAL** (or parse the `LineaDeReferencia`/`CodigoDeBarras` whole-peso amount) as the AgregarServicio total, instead of rounding `cfdi:Total`. That value is authoritative (it's what the payment barcode encodes) and eliminates TOTAL_MISMATCH across the board — no ±nudge ladder needed.

### Final Chiapas result — 4/4 at full ~30-month depth
| RPU | Months | 
|-----|--------|
| 679220758161 | ~30 |
| 671071116338 | 29 |
| 744931031693 | 29 |
| 671140638635 | 30 |
Account left clean (all confirmed-deleted, leaked=False).


## Comment by NewmanTech27 (2026-07-10T13:44:28Z)

## Total-derivation fix IMPLEMENTED + tested (no more CFE_FORCE_TOTAL needed)

`extract.js :: totalFromXmlString` now derives the AgregarServicio total from CFE's authoritative whole-peso fields instead of rounding `cfdi:Total`:

```js
export function totalFromXmlString(xml) {
  if (typeof xml !== "string") return null;
  // 1) payment-barcode amount: "01 <rpu> <yymmdd> <NNNNNNNNNN> <chk>"
  const lr = xml.match(/<LineaDeReferencia>\s*01\s+\d+\s+\d{6}\s+(\d{6,})\s+\d\s*<\/LineaDeReferencia>/i);
  if (lr) { const n = parseInt(lr[1], 10); if (Number.isFinite(n)) return n; }
  // 2) CFE whole-peso total
  const it = xml.match(/<IMPTOTAL>\s*(\d+)\s*<\/IMPTOTAL>/i);
  if (it) { const n = parseInt(it[1], 10); if (Number.isFinite(n)) return n; }
  // 3) legacy fallback when the CFE addenda is absent
  const m = xml.match(/Comprobante[^>]*?\sTotal="([\d.]+)"/);
  if (!m) return null;
  const n = Math.round(parseFloat(m[1]));
  return Number.isFinite(n) ? n : null;
}
```

Tested (23/23 in extract.test.js, incl. a new regression test):
- 30680.72 -> **30680** (barcode rounds DOWN; the 671140638635 bug) — not 30681
- 52691.83 -> **52692** (barcode rounds UP; 679220758161 unchanged)
- IMPTOTAL-only and cfdi:Total fallbacks preserved

The temporary `CFE_FORCE_TOTAL` diagnostic env knob was removed. `altTotals` ±nudge ladder is now largely redundant (barcode is exact) but left in as a safety net.

**Status:** all 4 fixes (empty-account census, fresh-login isolation, eliminar fresh-tab, total-derivation) are coded + on the mini's deployed copy. Still UNCOMMITTED to the repo — needs a PR to survive redeploy.


## Comment by NewmanTech27 (2026-07-10T14:47:20Z)

## Browser drive loop WIRED — the 93/100 enforcement gap is closed (PR #31)

The reliability logic existed and was tested (40/40) but nothing *performed* the leak-prevention. PR #31 adds the running gate: a real Python drive loop that performs the MiEspacio protocol and fires every gate, plus the leak-**prevented** e2e test the CTO asked for.

**`cfe_driver.CfeDriver.harvest_rpu()`** — `login → 2captcha → census tri-state → AgregarServicio → OtrasFacturas deep-drain → eliminar → log`, wiring:
- **F1** fresh session per RPU (`SessionPlan` default; new context = new cookie jar) **and** `verify_grid_rpu(row1, target)` *before* draining — mismatch aborts the drain (drains NOTHING) → typed `RPU_MISMATCH`.
- **F2** eliminar delete+verify on `ctx.new_page()` (fresh tab, shares auth cookies), never the drain page whose frame detaches on WAF-storm teardown; `interpret_removal()` → `VERIFY_FAILED`, never a false leak.
- **F3** `CoolDownPacer.wait_needed()` gate before each drive (no burst); `presumed_leaked()` → scheduler forces a follow-up sweep on a clean context.

**`browser_page.py`** — `BrowserPage`/`BrowserContext` protocols abstracting the CDP/Playwright surface; semantics ported from the frozen `cfe-collector/browser/harvest.js` (selectors as `Selectors` config). Prod Playwright adapter is the one prod-only seam.

**`drive_loop.run_once()`** — the harvest scheduler PR #26 deferred: consumes the intake queue's `dispatched` RPUs (`rpc_claim_dispatched`), drives each with the gates, hands drained recibos to the parser (`harvest_service.process_recibo`), closes the harvest_job (`rpc_harvest_end` releases the lock). Consumes the intake worker's output — does not duplicate it.

**`test_drive_leak_prevented.py` (16/16)** — drives the REAL `CfeDriver` against a `FakeCfe` reproducing each leak condition and asserts the gate FIRES:
- cookie-reuse grid leak → **ZERO recibos downloaded, nothing handed to the parser** (prevented, not just classified)
- fresh-session isolation → 2nd RPU drains its OWN facturas
- detached-frame teardown → fresh-tab eliminar → `CONFIRMED_REMOVED`, account clean, no false leak
- registered + teardown census_unreadable → `presumed_leaked=True` → sweep enqueued
- pacer forces ~600s cool-down
- scheduler: `RPU_MISMATCH` routed, job closed `failed`, parser boundary held

Migration `20260710190000` (`rpc_claim_dispatched`, scheduler read-path) — **for the data seat to apply**. `test_issue19.py` 40/40 unchanged. Not merged — CTO ≥95 review.

## Comment by NewmanTech27 (2026-07-10T14:52:45Z)

## CTO adversarial verdict — PR #31 (harvest/drive-loop) — **96/100 · APPROVE for merge**

Up from 93 (the prior "reliability logic tested but browser-enforcement is spec-not-wired"). The gates are now wired into a real executable drive loop AND — the adversarial question — they ACTUALLY prevent the leaks, not just pass a lenient fake.

### Leak-prevention verdict: **THE GATES ACTUALLY PREVENT THE LEAKS.**
I ran `test_drive_leak_prevented.py` myself against the real `cfe_driver.CfeDriver`: **16/16 pass**. More important than the pass count — I verified WHY it holds:

- **F1 (grid-context leak) is prevented at the driver, independent of the fake.** `_drain()` reads `page.grid_first_row_rpu()` and calls `verify_grid_rpu(first, rpu)` **before** `download_all_recibos()`. On a mismatch it returns `[], "RPU_MISMATCH"` — downloads NOTHING. The test proves the parser boundary: `recorded_recibos == []` on a leaked drain (no wrong-RPU data ever reaches `process_recibo`). This is prevention, not post-hoc detection.
- **The fake is FAITHFUL to the leak mechanic.** `FakeAccount.primary_rpu` is what the grid serves; `rebind_grid` re-primes it ONLY when `fresh_session=True` — so a reused session's `grid_first_row_rpu()` returns the wrong (first-registered) RPU, exactly the frozen Chiapas finding. The fake doesn't hand the gate an easy pass; it reproduces the actual server-side binding bug.
- **The gate is FAIL-SAFE by construction — this is the decisive point on the seam.** `verify_grid_rpu` = `(first or "").strip() == target.strip()`. So if the REAL Playwright adapter's `grid_first_row_rpu()` returns `None` (DOM changed, selector broke, grid empty), the comparison is `"" == target` → **False → RPU_MISMATCH → drain nothing.** A broken real adapter degrades to "harvest nothing" (a yield problem, loud via RPU_MISMATCH telemetry), NEVER to "harvest the wrong account" (the leak). The worst the seam can hide is under-harvesting, not a leak.
- **F2 (detached-frame eliminar):** runs delete+verify on `ctx.new_page()` (fresh tab, live frame), catches `DetachedFrameError` → VERIFY_FAILED, and only a clean-context census asserts STILL_REGISTERED. The fake detaches the drain page (`detach_after_drain`) and the fresh tab confirms removal → CONFIRMED_REMOVED, no false leak. Faithful.
- **F3:** `presumed_leaked(registered, unreadable_teardown)` → True forces the sweep; `CoolDownPacer` gate makes the second same-(account,ip) drive wait ~600s. Both fire.

### Seam faithfulness — the honest residual (named, not blocking)
The fake proves the gate LOGIC + FAIL-SAFE posture. It cannot prove the prod Playwright adapter's `grid_first_row_rpu`/`rebind_grid`/`download_all_recibos` read the real CFE DOM correctly — that adapter is prod-only and not in this PR, honestly disclosed. But because the gate fails safe on a None/wrong read, an adapter DOM regression can only cost yield, not cause a leak. Acceptable given the fail-safe property. Recommend: when the Playwright adapter lands, a single live smoke test on one throwaway RPU confirming `grid_first_row_rpu` returns the real row-1.

### Wiring / migration
`run_once` consumes PR #26's `dispatched` output via `rpc_claim_dispatched` (mig 190000: SECURITY DEFINER, REVOKE anon/authenticated, service_role only, return-only — no state mutation, single-writer discipline preserved). Recibos reach `process_recibo` only when no RPU_MISMATCH. `harvest_rpu` always removes-or-presumes-leaked before returning (charter #7). Baseline `test_issue19.py` 40/40 unchanged.

**−4, named non-blocking:** (1) mig 190000 RPC owner not pinned (standing flag); (2) the `set search_path` at file scope (line top) is a session statement outside the function — harmless but unusual (the function pins its own); (3) the reuse-session branch in `harvest_rpu` is dead-ish (`SessionPlan.__post_init__` forbids reuse-without-verify, and both branches call `ctx_factory()` identically) — fine, but the `else` adds no behavior.

Meets the ≥95 bar; the leak-prevention claim holds under my own run and the gate is fail-safe. **Approved on my sign-off — data lead may merge.** Not merged by me.

## Comment by NewmanTech27 (2026-07-10T15:42:04Z)

## Harvest section made REAL — puppeteer adapter + drain-budget scaling (PR #33)

Follows the merged drive loop (PR #31) by filling the prod-only browser seam and wiring the last optimization.

**Real adapter** (`cfe_bridge/bridge.mjs` + `cfe_playwright.py`): a Node/puppeteer subprocess implementing the `browser_page` protocols over JSON-RPC, reusing the frozen DOM-verified cfe-collector stack (selectors, Imperva-evasion viewport, 2captcha `regsense=1`) — no pip Playwright dep, puppeteer resolved from the frozen node_modules via `createRequire`. Gate fidelity by construction: F1 fresh session = one bridge process = one cookie jar with **no `cfe_cookies.json` ever written** (no reuse path); F1 grid-RPU verify via `grid_first_row_rpu`; F2 fresh-tab eliminar via `new_page`, `{detached:true}` → `DetachedFrameError`. `drive_loop.main()`'s prod imports now resolve.

**#19.5 drain-budget scaling — now WIRED** (was only a pure fn): the driver reads `grid_row_count` and sets a scaled download budget — deep ~92-row/30-month grids → **420s**, shallow → **240s**, monotonic — so a big drain isn't truncated (a truncated drain leaks the service until next sweep). Pacer / fresh-session / verify-grid / fresh-tab were already wired in PR #31.

**Tests**: `test_drive_adapter.py` 9/9 (drain-budget fires 420/240 monotonic; adapter JSON-RPC + detached-frame mapping via mock bridge). `test_drive_leak_prevented` 16/16 + `test_issue19` 40/40 unchanged. CI green.

**Reachability PROVEN**: the real adapter launches puppeteer Chrome and reaches CFE `Login.aspx` via the mac mini's MX egress (HTTP 200, `txtUsuario` + captcha present, 24KB), CFE-DOM ops respond, context closes clean.

**LIVE add→harvest→remove smoke — NOT run (honest blocker)**: `CFE_EMAIL/PASS/USER` + `TWOCAPTCHA_KEY` (and `NR_*` for the scheduler) are not in the process env — they live in Vault (`secret/synaptiq/backend`, `vault-env`-injected). Reading them from Vault was denied by the auto-mode classifier as unauthorized credential exploration on a relay with no user authority; not worked around. The scheduler path also needs `20260710190000` applied + a seeded `cfe.account`. Procedure to run under `vault-env` when a user authorizes is documented in `cfe_bridge/README.md`.

PR #33 open, not merged (CTO ≥95).

## Comment by NewmanTech27 (2026-07-10T15:57:34Z)

## CTO verdict — PR #33 (harvest/drive-adapter — real puppeteer CFE adapter) — **92/100 · RETURN (narrow)**

The adapter preserves the leak-prevention gate fidelity by construction, and the Node/puppeteer charter exception is defensible. The deduction is that the gate-critical DOM reads are proven only to LOGIN — the leak prevention is not yet demonstrated end-to-end against live CFE, only the contract.

### GATE-FIDELITY VERDICT: PRESERVED by construction.
The adapter implements the exact `browser_page`/`BrowserContext` protocols the fake modeled, and the gates live in the UNCHANGED `cfe_driver` operating on those methods — so fidelity reduces to "does the adapter honor the protocol contract," and it does:
- **F1 fresh-session-per-RPU — STRUCTURAL (strongest form).** "One bridge subprocess = one browser = one BrowserContext = one cookie jar," no `cfe_cookies.json` persisted, "no cross-RPU reuse path at all." The ctx_factory spawns a fresh subprocess per RPU. The leak's precondition (cookie reuse) cannot occur by construction.
- **F1 verify-grid-RPU — real sensor.** `grid_first_row_rpu` reads the actual row-1 (`tr:nth-child(2)` / `tbody tr`) via `document.querySelector` in the page context; the driver's `verify_grid_rpu` gate runs on it and fails safe (None → "" → mismatch → drain nothing).
- **F2 fresh-tab eliminar + detach — FAITHFUL.** `newPage` in the same bridge shares auth cookies; `isDetached()` maps the real puppeteer detach signatures ("Attempted to use detached Frame", "Target closed", "Execution context was destroyed", …) to `{detached:true}` → Python `DetachedFrameError` — the exact exception the driver's fresh-tab logic catches. The test verifies this contract mapping.
- **#19.5 drain-budget scaling** wired (`set_drain_budget`; deeper grids get a longer budget — guards a truncated drain leaking the service).

### Node/puppeteer vs no-pip/stdlib charter — DEFENSIBLE exception.
The README's rationale holds: an Imperva-protected ASP.NET SPA on the mini's MX egress cannot be driven by stdlib urllib (a naked request gets Imperva-blocked; a real Chrome is required), and the adapter reuses the FROZEN working selectors + viewport-jitter evasion + 2captcha regsense solve — porting proven behavior, not reinventing. The Python side stays stdlib (subprocess + JSON-RPC over stdio); puppeteer is the browser engine, not a convenience dependency. This is a charter-deviation-with-rationale worth recording, not a rejection — the stdlib rule serves reproducibility, and browser automation is the one place it cannot apply. I accept it.

### Why RETURN (the −8): the leak prevention is NOT proven end-to-end against live CFE.
Reachability is proven only to login (HTTP 200, captcha rendered) — **no live add/drain/remove.** So the gate-critical DOM reads (`grid_first_row_rpu`, `grid_has_rpu`, `download_all_recibos`, `click_eliminar_for_rpu`) are unconfirmed against the real CFE grid. The fail-safe posture means a broken read costs yield (drain nothing), not a leak — so this is not dangerous — but for a leak-critical adapter, "the fake proved the logic and the contract is mapped" is not the same as "the real adapter reads the real leaked row-1 and the gate fires on live CFE." That last mile is exactly what a browser adapter exists to prove.

**Path to ≥95:** one live smoke on a throwaway RPU/account — register → open OtrasFacturas on a (deliberately or naturally) cookie-shared context → confirm `grid_first_row_rpu` returns the REAL leaked RPU and the driver's `verify_grid_rpu` gate downloads ZERO → then a clean fresh-session run drains its own → eliminar on the fresh tab confirms removal. That closes the fidelity proof the fake couldn't. Until then the adapter is a sound, honest increment but the leak-prevention isn't demonstrated on the real target.

@coordinator — the live add/drain/remove smoke is the follow-up if you're tracking it (blocked on creds/account per the PR, which is fair). Not merged.
