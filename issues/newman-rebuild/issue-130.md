# #130: Spike: 2captcha Browser API (cloud browser) vs mac-mini Chrome for CFE harvest WAF stability

- State: OPEN
- Created: 2026-07-13T21:18:16Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/130

## Body

## Why
Dev harvest is blocked by CFE's Imperva WAF on back-to-back drives from the mac-mini's single residential IP (#119). The reaper now requeues WAF_BLOCK forever (PR #129) so no data is lost, but the *root cause* — one IP hammering CFE — remains. 2captcha's **Browser API** offers a cloud Chrome over CDP with per-profile residential proxies (country=MX) + built-in anti-bot/CAPTCHA handling. Multiple profiles = multiple residential IPs = distribute load, avoid the rate trip.

## Done (PR #129)
- `bridge.mjs` feature flag `CFE_CDP_URL`: when set, `puppeteer.connect()` to the cloud browser instead of local `frozen.launch()`. Unset = local path, unchanged.

## Open / needs decision
- [ ] **CDP URL**: create a 2captcha Browser account (2Captcha Proxy, country=Mexico) → copy the profile CDP URL → set as `CFE_CDP_URL` edge/env secret (never commit).
- [ ] **A/B on ONE dev RPU**: local path vs CDP path — does the cloud browser actually beat CFE's Imperva? (We LOSE the frozen launch()-time fingerprint patches on a remote browser; unproven that 2captcha's generic stealth beats CFE specifically.)
- [ ] **CFE login stability** through rotating residential proxy: CFE's own account-security may challenge/lock on new-geo logins (account is CEO-gated/shared — risky).
- [ ] **30-min session cap** vs deep harvests approaching ~25 min — tight; measure.
- [ ] **Session lifecycle**: close browser per RPU to free the profile (profile_locked = one connection per profile). Traffic-billed (budget OK).
- [ ] Decision: roll forward (swap default), keep as fallback, or drop.

## Risk summary
Reversible spike behind a flag. Real uncertainty is whether cloud-browser stealth beats CFE Imperva *without* our frozen evasion, and whether CFE login survives IP rotation. Test small before any rollout.

Refs #119, PR #129.

## Comment by NewmanTech27 (2026-07-13T21:44:16Z)

## ✅ Proxy validated end-to-end (consulta) — beats CFE Imperva

Went with 2captcha **residential proxy** (not the Browser API cloud browser) → keeps the local frozen Chrome + full Imperva evasion, just swaps egress to a residential MX IP.

**Wiring (PR #129):** `CFE_PROXY` + `CFE_PROXY_USER/PASS`. Injected by patching `launch()` on the **ESM** puppeteer default export frozen imports (bridge's CJS `_require` is a different object — that was the initial miss). Basic-auth via `page.authenticate()` per page. Secrets stored on dev/staging/prod edge secrets.

**Proof — `consulta_one` through the proxy, real RPU:**
- `ok: true`, `error_class: none`
- egress: MX residential (UNINET/Telmex, Starlink MX — rotates per session)
- razón social matched, **9 recibos drained** (202511→202606), full CFDI XML w/ SAT cert
- `fetch_s: 92s` (full browser flow through proxy)

Frozen evasion + residential MX IP passes Imperva cleanly. Next: validate the **harvest/login** path (MiEspacio) through the proxy — same bridge, adds CFE login + captcha.

## Comment by NewmanTech27 (2026-07-13T23:39:35Z)

## ✅ SOLVED — Browser API used the right way: no-login consulta + CDP XML capture

Exhaustive controlled testing established the boundary:
- **Login-harvest via Browser API / residential proxy: impossible.** CFE MiEspacio login is IP-gated server-side — accepts the mini's direct IP, silently rejects 2captcha residential IPs (proven: mini-direct logs in first try; proxy+cloud fail ~30×, captcha clean, no error). Not codeable-around.
- **No-login Consulta via Browser API: works cleanly.**

### The shipped solution (PR #129)
2captcha **Browser API cloud browser** → no-login **Consulta** → **CDP Fetch XML-capture** → `raw_cfe.consulta`.
- `buildCdpUrl()` assembles the cloud-browser ws:// endpoint from parts (`CFE_2CAP_LOGIN/PASS/PROXY/COUNTRY`), fresh profile-id per connect, residential proxy embedded.
- The bridge runs locally on the mini even when driving the remote browser, so `_enableXmlCapture()` grabs CFDI bytes over CDP (header-filtered `Fetch.getResponseBody`) and writes them to the **local** DL_DIR → the existing consulta→sha256→store path is unchanged (remote-download problem eliminated).
- CDP mode returns only the UUID-deduped `cdp_*.xml` (fetchDrain also arms browser downloads that 2captcha delivers back — filtered out).

### Proven end-to-end (ETG)
`consulta_one` in CDP mode → **8 distinct monthly CFDIs** (202511→202606), correct sha256/periods, razón matched, adeudo $281,439. Cloud browser clears Imperva in ~5.5s; no login needed.

### Deploy
Creds on dev/staging/prod edge secrets (`CFE_2CAP_*`). Set them in the mini's consulta env to route consulta through the cloud browser. Full-history login-harvest stays mini-direct (28 months proven). See memory `project_cfe_login_ip_gated`.
