# #136: Bridge op=consulta goes silent past deadline on mini (:8791)

- State: OPEN
- Created: 2026-07-14T12:34:37Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/136

## Body

11 consulta re-runs died with `BridgeTimeout: bridge op=consulta silent past deadline`
(harvest/cfe_playwright.py:82). The bridge stops emitting heartbeats mid-consulta.
Investigate on the mini: pipeline endpoint logs, whether the puppeteer bridge tab hangs on
the WAF interstitial, and whether the deadline needs to distinguish 'working but slow' from
'dead'. Separate from the status-regression issue — this is the underlying hang.
