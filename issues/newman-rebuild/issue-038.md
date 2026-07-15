# #38: Beat Imperva/WAF on the live MiEspacio harvest (census UNREADABLE blocks the drain)

- State: CLOSED
- Created: 2026-07-10T17:07:24Z  Closed: 2026-07-10T22:11:28Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/38

## Body

## Problem
First live end-to-end harvest (2026-07-10, RPU 999999999999, account 2, via the mini's MX egress) hit an **Imperva/WAF challenge at the census** → `census_state=unreadable`, `business_error=CENSUS_UNREADABLE`, **zero recibos drained**. The #19 gates fail-safed correctly (registered=False, leaked=False, account CLEAN — no permaban), but no drain succeeds.

## Deliverable
The live MiEspacio harvest reaches a **readable census** and completes a real `add → harvest (recibos>0) → remove → verify-account-clean` on a test RPU, past Imperva.

## Approaches to iterate
- Session warming (visit CFE entry pages before the census read).
- Tune the frozen Imperva-evasion in the puppeteer bridge (viewport jitter, headers, user-agent, human-timing) — it's in newman-architecture/agents/cfe-collector/browser.
- The Imperva challenge is SEPARATE from the login 2captcha — it may need its own handling/avoidance.
- Egress: the single NordVPN MX exit may be flagged — evaluate a rotating / residential MX egress.
- Pacing/cool-down (#19.5 CoolDownPacer) — WAF escalation is real; do NOT burst live attempts.

## Constraints
- Honor MiEspacio protocol every attempt: remove-after, account left holding nothing (permaban risk). BOUNDED live attempts, paced.
- Creds are local (~/.newman-collector.env) + on edge secrets; run on the mini (MX egress).

## Link
Unblocks PR #33's final proof (CTO 92 RETURN needs the leak-gate proven on a live READABLE grid — currently WAF blocks before the grid renders).

## Artifact (required to close)
- [ ] A readable census + a real drain (recibos>0) on a test RPU, account clean after
- [ ] Documented what beat Imperva (evasion/egress change)

## Hazards
- [ ] No client PII / creds in repo/logs; account never left holding a service


## Comment by NewmanTech27 (2026-07-10T17:14:18Z)

## We beat this today — here's what worked (Chiapas live harvest, 2026-07-10)

On the same day/stack as this issue, I ran **real end-to-end live harvests** on 4 RPUs (Alimentos y Franquicias de Chiapas: `679220758161`, `671071116338`, `744931031693`, `671140638635`) via the mini's MX egress and got, per RPU: **readable census → add → drain (recibos>0, ~30 meses c/u) → eliminar → account CLEAN (leaked=False)**. So the deliverable here is reproducible. What made the census READABLE past Imperva:

### 1. Fresh login per attempt (the key)
Reusing `cfe_cookies.json` across RPUs/attempts is what correlated with `census_state=unreadable` at teardown and WAF escalation. **Deleting `cfe_cookies.json` before each run** (forcing a fresh 2captcha login → fresh Imperva token/session) made `AdministrarServicios` render the real authed app (not the Imperva shell), so the census read cleanly every time. Causal chain: fresh login → fresh Imperva clearance → grid/`lblNoRegistros` renders → readable census → proceed.
> Concretely: `rm cfe_cookies.json; CFE_HEADFUL=1 python main.py --rpu <x> --name "<exact NOMBRE>"`. First site did a fresh login (`login try 1 [captcha ...][cookies saved]`) → census readable → drained 88 XMLs → `eliminar: confirmed deleted, leaked=False`.

### 2. Do NOT burst — one RPU per fresh session, paced
Chaining RPUs on one warm session escalated the WAF hard: `rejected` per drain climbed 0 → 32 → 33, end-of-run census went `census_unreadable`, and a `throughput-watchdog` even fired `"PARSER REGRESSION? 83 quarantined in 1h"`. **Isolated fresh-login runs, paced, succeeded; bursts did not.** This is the #19.5 CoolDownPacer — it's necessary, not optional.

### 3. Egress that cleared Imperva
Our MX exit was **NordVPN Querétaro, org PacketHub (AS136787)** — Imperva cleared on a fresh session from it. So a single MX exit *can* work; the dominant variable in our runs was **session freshness**, not the exit. Rotating/residential egress is a fallback if a specific exit gets flagged, but try fresh-login first.

### 4. Make sure the #19 empty-account census fix is in
Separate from Imperva: an **empty pooled account** renders `#ctl00_MainContent_lblNoRegistros` and **no `gvServicios` table**. Without the fix, `gridState()` misreads that as drift/unreadable and fail-closes → a *false* `CENSUS_UNREADABLE` with **no WAF involved at all**. The fix (recognize `lblNoRegistros`/`DLPaginas` → `rendered:true, count:0`) is in PR #6 / documented in #19. Confirm it's deployed, or a clean account will look like a WAF block even after you beat Imperva.

### 5. eliminar/teardown census on a fresh tab
The **end-of-run** census (in `eliminar`) failed with `Attempted to use detached Frame` after a WAF-storm drain → a FALSE `leaked`/`census_unreadable`. The #19 fresh-tab eliminar fix (run delete+verify on `page.browser().newPage()`, not the drain page) fixes that teardown-census read too. Also in PR #6.

## Suggested fix order for #38
1. **Force fresh login before the census** (don't reuse cookies across attempts/RPUs) — biggest lever.
2. **Pace** (CoolDownPacer): one RPU per fresh session, cool-down between; never burst.
3. Ensure the **empty-account census** fix + **fresh-tab eliminar** fix (PR #6 / #19) are deployed — else you'll see false CENSUS_UNREADABLE that isn't Imperva.
4. Only if 1–2 still get challenged from a given exit: **rotate egress** (residential MX pool).

## What we did NOT need
- No new Imperva-evasion tuning in the puppeteer bridge, no header/UA changes — the frozen evasion + a **fresh session + paced single-RPU runs** cleared the census on every Chiapas attempt. Session freshness > evasion tuning, in our data.


## Comment by NewmanTech27 (2026-07-10T17:21:46Z)

## Diagnosis + offline fix (PR #39) — earlier CENSUS_UNREADABLE was mostly a LOGIC bug, not just Imperva

**Two causes, dominant one a bug:**

1. **census ran BEFORE login** (root cause, dominant). `AdministrarServicios` is behind auth → an unauthenticated census always bounces to `Login.aspx` → UNREADABLE ("login bounce") → aborts before login. A false-positive by construction. **Reproduced offline**: `driver._census` unauth → `state=unreadable reason="login bounce"`. **Fixed**: login FIRST, then census.

2. **minimal bridge tripped Imperva** (secondary). PR #33's bridge did a cold goto straight to the census URL. **Fixed**: bridge now uses the frozen `launch()` verbatim (full fingerprint evasion) + challenge-aware `gotoThroughWaf` + session warming (Consulta→Login before auth, earning `incap_*` cookies).

**Audit — the three #19 fixes ARE all present in the rebuild path (so NOT the cause):**
- F1 fresh-login: bridge writes NO `cfe_cookies.json` (frozen `launch()` returns a bare page; cookie-load only in `authedPage()`, which we don't call) → not a stale cookie.
- #19.1 empty-account census: `census.py` classifies lblNoRegistros/DLPaginas as EMPTY (proceed) → not an empty-account false-positive.
- F2 fresh-tab eliminar: `driver._eliminar` uses `ctx.new_page()`. ✓

**Offline evidence (read-only, MX egress):** minimal bridge → Imperva challenge shell (reproduced the failure); warmed bridge → warm Consulta+Login ready=true, census goto ready=true, NO challenge-shell markers, `_census` → "login bounce" (readable), not "WAF/Imperva". **Imperva passed.** Tests 40/40 + 16/16 + 9/9. CI green.

**LIVE add→harvest→remove re-run of 008970211013 — BLOCKED pending USER authorization.** I attempted a bounded Phase-A (fresh login + census only, read-only). The auto-mode classifier denied it: a live authenticated login into external production CFE with a real client's credentials, on a coordinator relay with no user approval, requires the actual user's consent. I did not work around it; the frozen deployment was left untouched. Register inputs are staged (total 281439 barcode/IMPTOTAL, titular ETG RESORTS SA DE CV). A user must authorize the live login to complete the artifact and clear PR #33's live-smoke.

**Recommended next lever:** user authorizes the bounded live run (fresh cookies, remove-after + re-census). If Imperva STILL challenges post-warming from the single NordVPN MX exit, the next lever is rotating/residential MX egress (the single datacenter exit IP may be flagged) — but the offline evidence suggests the evasion+warming + login-order fix is sufficient.

## Comment by NewmanTech27 (2026-07-10T22:11:28Z)

Resolved in main via #47 squash (e80c98f).
