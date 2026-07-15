# #62: Extraction end-to-end integration test + browser-layer Finding port + merge #50

- State: OPEN
- Created: 2026-07-11T07:52:19Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/62

## Body

Committee major (8 cites): no test drives a real redacted CFE PDF through extract.identify → extract_bills → reconcile → preflight; no live-CFE CI smoke guarding DOM/selector drift; the 6 runtime-reliability Finding specs (fresh session/RPU, detached-frame delete, WAF pacer) are Python-SPEC'd but not all migrated to Puppeteer/CDP; and the #50 subprocess/timeout isolation is unmerged (daemon-hang cleanup). Required: the e2e integration test, a live-CFE smoke, finish the browser-layer port, land #50. (#49/#50)
