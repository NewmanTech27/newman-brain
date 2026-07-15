# #147: 2captcha Browser API can't speed the drain as-is: download-path + WAF-vs-throttle mismatch

- State: OPEN
- Created: 2026-07-14T13:26:36Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/147

## Body

Investigated whether raising CFE_DRAIN_BATCH and/or the 2captcha Browser API
(CFE_CDP_URL, bridge.mjs:200) speeds the MiEspacio harvest. Two separate limiters
are in play and the browser API only addresses the wrong one:

1. XML download throttle (the "4 per session" the drain re-logins around). CFE
   mints ~4-5 XML then returns "No es posible obtener el archivo Xml en este
   momento". cfe_driver.py:391 treats it as PER-COOKIE-SESSION (fresh context
   resets it -> the per-4 re-login); bridge.mjs:588 treats it as a RATE
   (BURST/COOLDOWN). The two files encode different theories -- unresolved, and it
   decides whether a bigger batch is even possible.

2. Imperva WAF on the mini's single residential IP. This is what CFE_CDP_URL was
   added for (residential MX proxy + stealth). Empirically (2 probe runs against
   the already-registered RPU 780020900569, batch=99, consulta skipped) BOTH died
   at #ctl00_MainContent_txtRpu (the AgregarServicio RPU input) after login --
   i.e. the bottleneck to even REACH the drain is the WAF at agregar, not the
   download rate. The drain never ran, so the per-session cap is still unmeasured
   live.

Blocker for the browser-API path: _armDownloads does
Page.setDownloadBehavior({downloadPath: DL_DIR}) where DL_DIR is a LOCAL mini path
(bridge.mjs:230). Over a remote cloud browser the XML lands on the CLOUD box's
disk; the drain fs.readdirSync(DL_DIR) sees nothing. So CFE_CDP_URL as wired today
can log in + pass the WAF but cannot retrieve files -- it needs a fetch/CDP-stream
download rewrite before it can drive a real harvest.

Recommendation: (a) resolve theory (1) with a clean single-session measurement on
a WAF-clear window or via the browser API once the download path is fixed;
(b) implement CDP-stream downloads so the browser API can carry the drain;
(c) only then decide whether batch>4 + proxy rotation beats the current
per-4-relogin.

## Comment by NewmanTech27 (2026-07-14T13:50:59Z)

## Update after research + live probing

**The XML string dump already exists.** raw_cfe.mi_espacio.xml_content holds the full CFDI XML for all 294 rows (2.5–7 KB each, `<?xml … <cfdi:Comprobante`). The file download is only the *acquisition* method — the string already lands in Postgres. So "store the XML as a string dump" is done; the open work is the remote-download acquisition + WAF-reach.

**WAF-reach root cause found + fixed (PR #148, live in prod).** Both probe runs died at `#ctl00_MainContent_txtRpu` because `_agregar` did a plain `goto(Default.aspx)` then typed immediately, racing the Imperva interstitial. Now routed through the challenge-aware goto with the RPU field as ready-selector (mirrors `_login`/`_census`).

**Remote-download-as-string design (researched, ranked winner).** For a remote cloud browser (2captcha Browser API over `puppeteer.connect`), capture the download body via CDP **Fetch at the Response stage** — the only method that works filesystem-free and identically local vs remote:

```js
const client = await p.target().createCDPSession();
await client.send("Fetch.enable", { patterns: [{ urlPattern: "*OtrasFacturas*", requestStage: "Response" }] });
client.on("Fetch.requestPaused", async (e) => {
  const hdrs = (e.responseHeaders||[]).reduce((m,h)=>(m[h.name.toLowerCase()]=h.value,m),{});
  // CFE serves the XML as the response to the __doPostBack to OtrasFacturas.aspx,
  // NOT a distinct Descarga URL — so match by Content-Disposition/Content-Type here,
  // and Fetch.continueRequest anything that isn't the attachment.
  if (!/attachment/i.test(hdrs["content-disposition"]||"") && !/xml/i.test(hdrs["content-type"]||"")) {
    return client.send("Fetch.continueRequest", { requestId: e.requestId });
  }
  const { body, base64Encoded } = await client.send("Fetch.getResponseBody", { requestId: e.requestId });
  const xml = Buffer.from(body, base64Encoded ? "base64" : "utf8").toString("utf8");
  await client.send("Fetch.fulfillRequest", { requestId: e.requestId, responseCode: 200, body: "" }); // swallow the disk download
  // → hand `xml` back over the bridge; write to DL_DIR ourselves so the Python
  //   parser contract is unchanged (works for remote browsers too).
});
```

Pitfalls: always decode with the base64 flag; `Network.getResponseBody` races the download sink (evicted body → "No resource with given identifier"), and puppeteer `page.on('response').buffer()` is unreliable for `attachment` — Fetch is the robust one. Match by **response headers, not URL** (the postback response URL is just OtrasFacturas.aspx). Needs one live capture to confirm the exact Content-Disposition/Type before shipping.

**WAF best practices (Imperva/Incapsula):** sticky residential/mobile IP for the whole session (rotation invalidates the `incap_ses`/`reese84` chain), full Chrome not headless-shell (JA3/JA4), and loop-wait on the challenge (poll `reese84`+`incap_ses` cookies + a real element, reload on interstitial) before touching form inputs. The 2captcha Browser API (residential proxy + stealth full Chrome behind a CDP endpoint) is a recommended pattern and *also* enables the Fetch-capture above — but as wired, `_armDownloads` uses a local `downloadPath`, so the browser-API path can't retrieve files until the Fetch-capture lands. Sources: scrapfly.io/blog bypass-imperva-incapsula, zenrows.com incapsula-bypass, 2captcha.com/h/imperva-bypass.
