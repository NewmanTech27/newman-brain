# #40: Port the Consulta-first phase: derive total a pagar + nombre from Consulta BEFORE MiEspacio (the real harvest unblock)

- State: CLOSED
- Created: 2026-07-10T18:44:02Z  Closed: 2026-07-10T22:11:31Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/40

## Body

## The gap
The rebuild's `cfe_driver.harvest_rpu` takes `total` and `name_candidates` as **injected parameters** and only *warms* past Consulta (a cookie visit). The frozen `agents/cfe-collector/browser/harvest.js` does the opposite — its documented flow is:

```
1) Consulta (RPU + nombre, NO login) -> capture ~6-8 recent recibos -> derive "total a pagar" from the NEWEST recibo XML
2) MiEspacio login -> AgregarServicio(RPU, nombre, total)   <- total + nombre come from step 1
3) deep-drain history -> eliminar
```

Two things the rebuild gets wrong as a result:
- **total a pagar must come from the Consulta XML** (`totalFromXml(latest)`), NOT the barcode. Live AgregarServicio validates against CFE's *current* total a pagar; an injected barcode figure (e.g. we had 439628 vs 281439 disagreeing) is why registration was never going to stick.
- **nombre must come from the Consulta recibo `<NOMBRE>`**, not OCR — authoritative account name, kills the name-match guessing.

This — not login timing — is why live MiEspacio harvest never registered (repro'd extensively on RPU 999999999999). Consulta-first also properly establishes the Imperva session (a real transaction, not a drive-by warm), which likely fixes the login-bounce too.

## Deliverable
A Consulta phase in the rebuild, mirroring frozen `harvest.js::consultaLatestTotal` (lines ~131-233) + selectors from `browser/cfe.js` (`consultaSubmit/consultaRPU/consultaNombre/consultaLada/consultaTel/consultaCorreo/consultaGridXML`):
- [ ] Bridge primitive(s): goto Consulta -> fill RPU + nombre + dummy contact (dummy contact is fine, not validated) -> submit -> wait grid -> download the recibo window (XML+PDF) -> return captured paths.
- [ ] Driver step `consulta_latest(rpu, nombre_candidates)` -> parse newest recibo XML -> return `(total_a_pagar, nombre_from_xml, latest_recibo_paths)`. Fail distinctly (not silent) if no recibos captured or total unparseable — never submit a wrong total.
- [ ] `harvest_rpu` runs Consulta FIRST, then feeds the *derived* total + nombre into AgregarServicio (keep injected values only as an optional cross-check / fallback).
- [ ] The Consulta recibo window IS the 'most recent invoice' deliverable — surface it (it's the fast, no-login path; MiEspacio is the historical-depth path).

## Verify
- Offline: unit-test the XML total/nombre parse against a captured Consulta recibo.
- Live (CEO runs): Consulta on 999999999999 returns a total + nombre; that total then makes AgregarServicio register; deep-drain; eliminar; account clean.

## Reference
Frozen working code: `~/newman-architecture/agents/cfe-collector/browser/harvest.js` (consultaLatestTotal, agregar) + `browser/cfe.js` (selectors, gotoThroughWaf, login). Do NOT modify the frozen stack — port into the rebuild bridge/driver. PR on the #38/#39 branch or a new branch off it; do not merge.

## Hazards
- [ ] No client PII/creds in repo/logs; account never left holding a service (eliminar always).


## Comment by NewmanTech27 (2026-07-10T18:55:48Z)

## Consulta-first phase ported (PR #41) — derived total 281439, not the injected barcode

Root cause confirmed: the rebuild took total+nombre as INJECTED params; the injected barcode total never matches CFE's current `total a pagar` (only Consulta returns it). Ported the frozen `consultaLatestTotal` + `extract.js` parse into the rebuild bridge+driver. **Frozen stack untouched.**

**Landed:**
- `consulta.py` — `total_from_xml_string` (LineaDeReferencia > IMPTOTAL > rounded cfdi:Total), `nombre_from_xml_string`, `receptor_from_xml_string` (anchored, never the CFE Emisor), `period_from_xml_string`, and `derive_from_recibos` (newest-by-period; **FAILS LOUD** on no recibos / no period / no total — never a guessed total).
- Bridge `consulta` op: gotoThroughWaf → fill RPU+nombre+DUMMY contact → submit → wait grid → click newest XML → frozen `fetchDrain` window → paths. Typed failures CONSULTA_WAF/SELECTOR_DRIFT/CONSULTA_NO_GRID/CONSULTA_NO_RECIBOS.
- Driver: `consulta_latest` (name ladder: raw + canonicalized) + `harvest_rpu` runs **Consulta FIRST**, feeds DERIVED total+nombre into AgregarServicio (injected → fallback/cross-check). Consulta failure → CONSULTA_FAILED, never registers off a guessed total. `DriveResult.consulta_recibos` surfaces the fast no-login 'most recent invoices' window.

**Tests (offline, stdlib):** test_consulta.py 16/16 + test_consulta_drive.py 9/9 (harvest_rpu feeds the DERIVED **281439** into agregar, NOT the injected 439628; all fail-loud paths). Existing 40/40 + 16/16 + 9/9 unchanged. **Parse cross-checked offline against the REAL 008970211013 window: period 202606 → total 281439, nombre 'ETG RESORTS SA DE CV', receptor 'ETG RESORTS'** (recibo NOT committed — carries client RFC/domicilio). CI green.

**Live path (CEO runs — creds + client account):** the exact invocation for the full Consulta→derive→MiEspacio→drain→eliminar on 008970211013 is in the PR #41 description. Expected: Consulta derives 281439 + nombre → registers → deep-drain → eliminar (account clean, leaked=False). I did NOT run the live authenticated flow.

PR #41 (onto the #38/#39 WAF branch per this issue), not merged (CTO ≥95).

## Comment by NewmanTech27 (2026-07-10T19:19:32Z)

## Login blocker fixed (PR #42, stacked on #41) — login is now a single bridge op

The last isolated blocker (MiEspacio login bounced even on a Consulta-warmed context) is fixed. Root cause was purely the rebuild's Python `_login` (low-level primitive orchestration + approximated timing + NO retry); frozen `cfe.js login()` authenticates 4/4 with the same creds.

Ported `tryLogin` + the `login()` ×6 retry loop VERBATIM into `bridge.mjs` as a single `login` op (like the `consulta` op), preserving the two things the frozen gets right that the rebuild didn't:
1. **Auth decided off `location.href`** (read via `page.evaluate` INSIDE the op), NOT the bridge `url()` primitive — `url()` lags CFE's post-login redirect chain and returned a false `inside=true` that bounced at the census.
2. **×6 retry breaking on `inside`** (frozen's own try-1 bounces, try-2 auths); each attempt wrapped so a transient image/nav error retries.

Browser + 2captcha share one Node process (frozen parity); no `cfe_cookies.json` persisted (F1 kept). Driver `_login` now prefers the native `page.login` op; step-orchestration kept only as the fake/thin-adapter fallback.

Tests: `test_login_op.py` 8/8 (native login used + `inside=False` surfaced + fallback + retry-inside-op contract); adapter wiring verified over a JSON-RPC mock bridge. All prior suites unchanged → **98/98**. CI green. Frozen stack untouched.

**Live path unchanged from #41** — `harvest_rpu` drives the full Consulta→login→add(281439)→drain→eliminar; the exact invocation is in PR #42's description. CEO/user runs the authenticated flow; I did not.

PR stack: #33 (adapter) ← #39 (WAF evasion) ← #41 (Consulta-first) ← #42 (login op). None merged (CTO ≥95).

## Comment by NewmanTech27 (2026-07-10T22:11:30Z)

Resolved in main via #47 squash (e80c98f).
